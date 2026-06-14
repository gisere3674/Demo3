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

Upload a chaotic room, desk, or workspace photo. The Space sends the image to a Modal-hosted vision-language model, overlays numbered excavation markers from the returned coordinates, builds a mock site map, and generates a faux-scholarly report about the domestic civilization that produced the mess.

## What it generates

- An annotated image with numbered artifact locations.
- A mock archaeological site map with grid coordinates.
- Fictional artifact descriptions and pseudo-academic carbon dating.
- A timeline of discovered domestic eras.

## Model plan

- **Single AI model:** `Qwen/Qwen2.5-VL-7B-Instruct`, hosted on Modal for both image understanding and report writing.
- **Total model budget:** 7B, comfortably under the requested 32B total cap.
- **Fallback:** If `MODAL_EXCAVATE_URL` is not configured, the Space still runs with deterministic local sample artifacts for demo resilience, but the intended polished path is Modal-powered vision-language generation.

## Why it fits Build Small

- It is whimsical, tinkerable, and easy to understand from one upload-and-click interaction.
- The Modal-hosted vision-language model turns ordinary clutter into spatial evidence, artifact catalogs, and academic parody.
- The Hugging Face Space hosts the Gradio UI while Modal credits power the intended image-understanding and report-generation path.

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
