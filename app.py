import base64
import io
import json
import os
import random
from datetime import datetime

import gradio as gr
import requests
from PIL import Image, ImageDraw, ImageFont

MODAL_EXCAVATE_URL = os.getenv("MODAL_EXCAVATE_URL", "").strip()
MAX_IMAGE_SIDE = 1200

PERIODS = [
    ("Early Cable Age", "2016-2019"),
    ("Pandemic Desk Layer", "2020-2022"),
    ("Late Notification Period", "2023-present"),
]


def resize_for_modal(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    image.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE))
    return image


def image_to_data_url(image: Image.Image) -> str:
    buffer = io.BytesIO()
    resize_for_modal(image).save(buffer, format="JPEG", quality=88)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


def fallback_artifacts():
    return [
        {"id": 1, "label": "unclassified clutter cluster", "x": 0.32, "y": 0.42, "period": "Pandemic Desk Layer"},
        {"id": 2, "label": "possible charging-cable shrine", "x": 0.62, "y": 0.55, "period": "Late Notification Period"},
        {"id": 3, "label": "paperwork sediment", "x": 0.48, "y": 0.72, "period": "Early Cable Age"},
    ]


def fallback_report(artifacts, tone):
    lines = [
        "# Preliminary Domestic Excavation Report",
        f"**Excavation date:** {datetime.utcnow().strftime('%Y-%m-%d UTC')}  ",
        f"**Tone:** {tone}  ",
        "",
        "## Abstract",
        "The site exhibits clear evidence of active human productivity interrupted by repeated micro-rituals of postponement.",
        "",
        "## Numbered finds",
    ]
    for artifact in artifacts:
        lines.append(
            f"- **Clue #{artifact['id']}: {artifact['label'].title()}** — Assigned to the "
            f"**{artifact['period']}** using highly suspicious desk-stratigraphy methods."
        )
    lines += [
        "",
        "## Curator verdict",
        "The room should be preserved exactly as found until peer reviewers, roommates, or parents demand otherwise.",
    ]
    return "\n".join(lines)


def call_modal(image: Image.Image, tone: str):
    if not MODAL_EXCAVATE_URL:
        return None
    payload = {"image": image_to_data_url(image), "tone": tone}
    response = requests.post(MODAL_EXCAVATE_URL, json=payload, timeout=180)
    response.raise_for_status()
    return response.json()


def normalize_artifacts(artifacts):
    normalized = []
    for index, artifact in enumerate(artifacts[:8], start=1):
        normalized.append(
            {
                "id": index,
                "label": str(artifact.get("label") or f"artifact {index}"),
                "x": min(0.95, max(0.05, float(artifact.get("x", random.uniform(0.2, 0.8))))),
                "y": min(0.95, max(0.05, float(artifact.get("y", random.uniform(0.2, 0.8))))),
                "period": str(artifact.get("period") or random.choice(PERIODS)[0]),
            }
        )
    return normalized or fallback_artifacts()


def annotate_image(image: Image.Image, artifacts):
    annotated = image.convert("RGB").copy()
    draw = ImageDraw.Draw(annotated, "RGBA")
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", max(20, annotated.width // 32))
    except OSError:
        font = ImageFont.load_default()

    for artifact in artifacts:
        x = int(artifact["x"] * annotated.width)
        y = int(artifact["y"] * annotated.height)
        radius = max(16, annotated.width // 45)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(255, 211, 76, 235), outline=(65, 39, 12, 255), width=3)
        text = str(artifact["id"])
        box = draw.textbbox((0, 0), text, font=font)
        draw.text((x - (box[2] - box[0]) / 2, y - (box[3] - box[1]) / 2 - 2), text, fill=(35, 20, 5), font=font)
    return annotated


def site_map(artifacts):
    rows = ["| Find | Artifact | Grid | Period |", "|---:|---|---|---|"]
    for artifact in artifacts:
        grid = f"{chr(65 + min(4, int(artifact['x'] * 5)))}-{1 + min(4, int(artifact['y'] * 5))}"
        rows.append(f"| {artifact['id']} | {artifact['label']} | {grid} | {artifact['period']} |")
    return "\n".join(rows)


def timeline_html(artifacts):
    cards = []
    for period, dates in PERIODS:
        finds = [f"#{a['id']} {a['label']}" for a in artifacts if a["period"] == period]
        cards.append(f"<div class='era'><b>{period}</b><span>{dates}</span><p>{', '.join(finds) or 'no confirmed deposits'}</p></div>")
    return "<div class='timeline'>" + "".join(cards) + "</div>"


def excavate(image, tone):
    if image is None:
        raise gr.Error("Upload a room or workspace photo before excavating.")

    try:
        result = call_modal(image, tone)
        source = "Modal · Qwen2.5-VL-7B-Instruct"
        artifacts = normalize_artifacts(result.get("artifacts", []))
        report = result.get("report") or fallback_report(artifacts, tone)
    except Exception as exc:
        source = f"Local fallback · Modal unavailable ({exc})"
        artifacts = fallback_artifacts()
        report = fallback_report(artifacts, tone)

    annotated = annotate_image(image, artifacts)
    status = f"**Generation path:** {source}  \n**Total model budget:** 7B vision-language model, under the 32B cap."
    return annotated, site_map(artifacts), status + "\n\n" + report, timeline_html(artifacts), json.dumps(artifacts, indent=2)


CSS = """
#title{text-align:center}.timeline{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}.era{border:1px solid #dec78c;border-radius:14px;padding:14px;background:#fff8e7}.era span{display:block;color:#7a4b12;margin:.25rem 0}.era p{min-height:3rem}
"""

with gr.Blocks(title="Photo Archaeology Simulator", theme=gr.themes.Soft(), css=CSS) as demo:
    gr.Markdown(
        """
# Photo Archaeology Simulator 🏺
Turn your messy room into an academic archaeological dig site report.
""",
        elem_id="title",
    )
    with gr.Row():
        with gr.Column():
            image = gr.Image(type="pil", label="Chaotic site photo")
            tone = gr.Radio(["Very academic", "Maximum nonsense", "Museum placard", "Grant proposal"], value="Very academic", label="Report style")
            button = gr.Button("Excavate", variant="primary")
        annotated = gr.Image(type="pil", label="Annotated site map")
    site = gr.Markdown(label="Numbered locations")
    report = gr.Markdown(label="Scholarly report")
    timeline = gr.HTML(label="Timeline")
    raw = gr.Code(label="Artifact JSON", language="json", visible=False)
    button.click(excavate, [image, tone], [annotated, site, report, timeline, raw])

if __name__ == "__main__":
    demo.launch()
