import json
import os
import random
from collections import Counter, defaultdict
from datetime import datetime

import gradio as gr
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO

DETECTOR_MODEL = "yolov8n.pt"
MAX_OBJECTS = 12
MODAL_EXCAVATE_URL = os.getenv("MODAL_EXCAVATE_URL", "").strip()

_detector = None


PERIODS = [
    ("Pleistocene of Productivity", "pre-2016", "fossilized adapters, legacy paper deposits"),
    ("Early USB-C Transition", "2017-2019", "mixed connector ecologies and dongle migration"),
    ("Pandemic Desk Accretion", "2020-2022", "snack bowls, webcam altars, duplicated notebooks"),
    ("Late Notification Age", "2023-present", "charging cables, earbuds, hydration vessels"),
]


def get_detector():
    global _detector
    if _detector is None:
        _detector = YOLO(DETECTOR_MODEL)
    return _detector


def detect_artifacts(image: Image.Image):
    model = get_detector()
    result = model.predict(image, imgsz=960, conf=0.18, verbose=False)[0]
    artifacts = []
    width, height = image.size
    for box in result.boxes[:MAX_OBJECTS]:
        x1, y1, x2, y2 = [float(v) for v in box.xyxy[0].tolist()]
        cls_id = int(box.cls[0])
        label = model.names.get(cls_id, f"object_{cls_id}")
        conf = float(box.conf[0])
        area = ((x2 - x1) * (y2 - y1)) / max(width * height, 1)
        cx = (x1 + x2) / 2 / width
        cy = (y1 + y2) / 2 / height
        artifacts.append(
            {
                "id": len(artifacts) + 1,
                "label": label,
                "confidence": round(conf, 2),
                "box": [x1, y1, x2, y2],
                "center": [round(cx, 3), round(cy, 3)],
                "area": round(area, 4),
                "period": random.choice(PERIODS),
            }
        )
    if not artifacts:
        artifacts.append(
            {
                "id": 1,
                "label": "unclassified clutter horizon",
                "confidence": 0.42,
                "box": [width * 0.2, height * 0.2, width * 0.8, height * 0.8],
                "center": [0.5, 0.5],
                "area": 0.36,
                "period": random.choice(PERIODS),
            }
        )
    return artifacts


def annotate_image(image: Image.Image, artifacts):
    annotated = image.convert("RGB").copy()
    draw = ImageDraw.Draw(annotated, "RGBA")
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", max(18, image.width // 40))
        small = ImageFont.truetype("DejaVuSans.ttf", max(12, image.width // 70))
    except Exception:
        font = small = ImageFont.load_default()

    colors = [(255, 80, 80), (60, 180, 255), (255, 190, 60), (140, 255, 120), (210, 120, 255)]
    for artifact in artifacts:
        x1, y1, x2, y2 = artifact["box"]
        color = colors[(artifact["id"] - 1) % len(colors)]
        draw.rectangle([x1, y1, x2, y2], outline=(*color, 240), width=max(3, image.width // 250))
        r = max(14, image.width // 55)
        cx, cy = x1 + r + 4, y1 + r + 4
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*color, 230), outline=(0, 0, 0, 255), width=2)
        label = str(artifact["id"])
        bbox = draw.textbbox((0, 0), label, font=font)
        draw.text((cx - (bbox[2] - bbox[0]) / 2, cy - (bbox[3] - bbox[1]) / 2 - 1), label, fill=(0, 0, 0), font=font)
        draw.text((x1, max(0, y1 - 18)), artifact["label"], fill=(255, 255, 255), font=small, stroke_width=2, stroke_fill=(0, 0, 0))
    return annotated


def make_site_map(artifacts):
    rows = ["| Find | Artifact | Grid position | Confidence |", "|---:|---|---|---:|"]
    for a in artifacts:
        cx, cy = a["center"]
        grid = f"{chr(65 + min(4, int(cx * 5)))}-{1 + min(4, int(cy * 5))}"
        rows.append(f"| {a['id']} | {a['label']} | {grid} | {a['confidence']:.2f} |")
    return "\n".join(rows)


def fallback_report(artifacts, tone):
    counts = Counter(a["label"] for a in artifacts)
    lead = counts.most_common(1)[0][0]
    lines = [
        "# Preliminary Archaeological Report: Domestic Sector A",
        f"**Excavation date:** {datetime.utcnow().strftime('%Y-%m-%d UTC')}  ",
        f"**Interpretive mode:** {tone}",
        "",
        "## Abstract",
        f"Survey of the submitted room photograph identified {len(artifacts)} loci of material culture. The dominant visible taxon, **{lead}**, suggests a civilization balancing productivity with ceremonial postponement.",
        "",
        "## Artifact catalog",
    ]
    for a in artifacts:
        period, date_range, clue = a["period"]
        cx, cy = a["center"]
        placement = "peripheral" if cx < 0.25 or cx > 0.75 else "central"
        elevation = "upper stratum" if cy < 0.45 else "lower stratum"
        lines.append(
            f"- **Clue #{a['id']}: {a['label'].title()}** — Recovered from the {placement} {elevation}. "
            f"Carbon-ish dating assigns it to the **{period}** ({date_range}), based on {clue}. "
            f"Its placement indicates ritual readiness, abandonment, or a tiny rebellion against storage furniture."
        )
    lines.extend(
        [
            "",
            "## Spatial interpretation",
            "Objects form a loose constellation around probable human activity zones. This pattern is consistent with the well-known 'I'll move it later' deposition model (Smith, 1999; Patel & Cordova, 2018).",
            "",
            "## Conclusion",
            f"The site is stable but culturally active. Recommended next step: preserve the chaos for peer review, unless guests are arriving within 45 minutes.",
        ]
    )
    return "\n".join(lines)


def modal_report(artifacts, tone):
    if not MODAL_EXCAVATE_URL:
        return None
    try:
        payload = {"artifacts": artifacts, "tone": tone}
        response = requests.post(MODAL_EXCAVATE_URL, json=payload, timeout=90)
        response.raise_for_status()
        return response.json().get("report")
    except Exception as exc:
        return f"_Modal report generation failed, using local curator notes instead: {exc}_\n\n" + fallback_report(artifacts, tone)


def timeline_html(artifacts):
    grouped = defaultdict(list)
    for a in artifacts:
        grouped[a["period"][0]].append(a)
    cards = []
    for period, date_range, clue in PERIODS:
        items = grouped.get(period, [])
        artifact_text = ", ".join(f"#{a['id']} {a['label']}" for a in items) or "no visible deposits"
        cards.append(
            f"<div class='era'><b>{period}</b><span>{date_range}</span><p>{artifact_text}</p><small>{clue}</small></div>"
        )
    return "<div class='timeline'>" + "".join(cards) + "</div>"


def excavate(image, tone):
    if image is None:
        raise gr.Error("Upload a room, desk, or workspace photo before excavating.")
    if not isinstance(image, Image.Image):
        image = Image.fromarray(np.array(image))
    artifacts = detect_artifacts(image.convert("RGB"))
    annotated = annotate_image(image, artifacts)
    report = modal_report(artifacts, tone) or fallback_report(artifacts, tone)
    return annotated, make_site_map(artifacts), report, timeline_html(artifacts), json.dumps(artifacts, indent=2)


CSS = """
#title {text-align:center} .timeline{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}.era{border:1px solid #ddd;border-radius:14px;padding:14px;background:linear-gradient(180deg,#fff8e7,#f5efe3)}.era span{display:block;color:#7a4b12;font-size:.9rem;margin:.25rem 0}.era p{min-height:3rem}.era small{color:#665}
"""

with gr.Blocks(title="Photo Archaeology Simulator", theme=gr.themes.Soft(), css=CSS) as demo:
    gr.Markdown(
        """
# Photo Archaeology Simulator 🏺

Turn your messy room into an academic archaeological dig site report. Upload a chaotic room/workspace photo, then let the excavation team number artifacts, draft a site map, and fabricate scholarly domestic stratigraphy.
""",
        elem_id="title",
    )
    with gr.Row():
        with gr.Column(scale=1):
            image = gr.Image(type="pil", label="Chaotic site photo")
            tone = gr.Radio(["Very academic", "Maximum nonsense", "Museum placard", "Grant proposal"], value="Very academic", label="Report style")
            btn = gr.Button("Excavate", variant="primary")
        with gr.Column(scale=1):
            annotated = gr.Image(type="pil", label="Annotated site map")
    with gr.Row():
        site_map = gr.Markdown(label="Numbered locations")
    report = gr.Markdown(label="Scholarly report")
    timeline = gr.HTML(label="Timeline")
    raw = gr.Code(label="Artifact JSON", language="json", visible=False)
    btn.click(excavate, [image, tone], [annotated, site_map, report, timeline, raw])

if __name__ == "__main__":
    demo.launch()
