---
title: Photo Archaeology Simulator
emoji: 🏺
colorFrom: amber
colorTo: stone
sdk: gradio
sdk_version: 5.34.0
app_file: app.py
pinned: false
tags:
  - build-small-hackathon
  - gradio
  - thousand-token-wood
  - modal
  - computer-vision
---

# Photo Archaeology Simulator

**Turn your messy room into an academic archaeological dig site report.**

Upload a chaotic room, desk, or workspace photo. The app detects visible objects, overlays numbered excavation markers, builds a mock site map, and generates a faux-scholarly report about the domestic civilization that produced the mess.

## What it generates

- An annotated image with numbered artifact locations.
- A mock archaeological site map with grid coordinates.
- Fictional artifact descriptions and pseudo-academic carbon dating.
- A timeline of discovered domestic eras.

## Model plan

- **Object detection:** `yolov8n.pt` via Ultralytics. This compact detector is well below the 32B cap.
- **Optional Modal text endpoint:** `Qwen/Qwen3-4B-Instruct-2507`, also below the 32B cap.
- **Fallback:** If `MODAL_EXCAVATE_URL` is not configured, the Space still runs using local humorous report templates so the demo remains available without paid Hugging Face inference.

## Why it fits Build Small

- It is whimsical, tinkerable, and easy to understand from one upload-and-click interaction.
- The AI turns ordinary clutter into spatial evidence, artifact catalogs, and academic parody.
- The Hugging Face Space hosts the Gradio UI while Modal credits can be used for optional LLM report generation.

## Running locally

```bash
pip install -r requirements.txt
python app.py
```

## Deploying the optional Modal writer

```bash
pip install modal
modal deploy modal_app.py
```

After deployment, set the Hugging Face Space secret `MODAL_EXCAVATE_URL` to the printed `/excavate` endpoint URL.

## Demo and social links

- Demo video: TODO
- Social post: TODO
