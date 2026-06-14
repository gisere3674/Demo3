---
title: Build Small Idea Forge
emoji: 🛠️
colorFrom: green
colorTo: indigo
sdk: gradio
sdk_version: 5.34.0
app_file: app.py
pinned: false
tags:
  - build-small-hackathon
  - gradio
  - backyard-ai
  - thousand-token-wood
---

# Build Small Idea Forge

A simple project-idea generator for the Hugging Face × Gradio **Build Small** hackathon.

The app uses a single 32B-cap-compatible idea model, `Qwen/Qwen3-32B`, to generate concise, buildable project concepts for the selected hackathon track.

## Why it fits Build Small

- Uses `Qwen/Qwen3-32B`, a strong model available through Hugging Face Inference Providers and aligned with the 32B model cap.
- Ships as a small Gradio app.
- Keeps the interface minimal: one project goal input, one track selector, one idea-count slider, and one output panel.
- Avoids extra local heuristics or fallback idea rules so the generated ideas come from the selected LLM.

## How to run on Hugging Face Spaces

1. Create a Gradio Space in the `build-small-hackathon` organization.
2. Upload `app.py`, `requirements.txt`, and this `README.md`.
3. Add a Space secret named `HF_TOKEN`.
4. Run the Space and generate ideas.

## Demo and social links

- Demo video: TODO
- Social post: TODO

## Tech

- Gradio UI
- `huggingface_hub.InferenceClient`
- Default model: `Qwen/Qwen3-32B`
