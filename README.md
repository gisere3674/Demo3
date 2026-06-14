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
  - best-agent
  - best-demo
  - codex
---

# Build Small Idea Forge

A simple project-idea generator for the Hugging Face × Gradio **Build Small** hackathon.

The goal is to help a solo builder create as many small, shippable hackathon projects as possible. It reads the hackathon constraints into the app prompt and returns practical or whimsical project ideas with a suggested model, basic Gradio UI, MVP plan, demo hook, and README tags.

## Why it fits Build Small

- Uses a default text model under the 32B total-parameter cap: `Qwen/Qwen2.5-14B-Instruct`.
- Ships as a Gradio app.
- Keeps the implementation intentionally basic so it can be copied into a Hugging Face Space directly.
- Includes an offline deterministic fallback so the Space still produces ideas if no token or provider is available.

## How to run on Hugging Face Spaces

1. Create a Gradio Space in the `build-small-hackathon` organization.
2. Upload `app.py`, `requirements.txt`, and this `README.md`.
3. Add a Space secret named `HF_TOKEN` if you want live model generation.
4. Optionally set `MODEL_ID` to another under-32B chat model.

## Demo and social links

- Demo video: TODO
- Social post: TODO

## Tech

- Gradio UI
- `huggingface_hub.InferenceClient`
- Default model: `Qwen/Qwen2.5-14B-Instruct`
- Offline fallback idea generator
