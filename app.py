import os
import random
from datetime import datetime, timezone

import gradio as gr
from huggingface_hub import InferenceClient

MODEL_ID = os.getenv("MODEL_ID", "Qwen/Qwen2.5-14B-Instruct")

HACKATHON_RULES = """
Build Small hackathon constraints:
- Build something small, local, tinkerable, and yours.
- Every model must stay under the 32B total-parameter cap.
- Ship a Gradio app as a Hugging Face Space in the Build Small org.
- Record a demo, make one social post, and link both from the Space README.
- README should include track/badge tags plus a short idea and tech write-up.
- Tracks: Backyard AI for practical daily-life problem solvers; Thousand Token Wood for whimsical AI-native fun.
- Useful prize angles: Tiny Titan (<=4B), Best Agent, Off Brand custom UI, Best Demo, Modal runtime/dev, sponsor models.
""".strip()

PRACTICAL_SEEDS = [
    "receipt-to-routine planner",
    "offline paperwork explainer",
    "tiny study coach",
    "family tech-support translator",
    "meal-from-leftovers planner",
    "bill dispute draft helper",
    "lab-report plain-language guide",
    "local-first meeting action extractor",
]

WHIMSICAL_SEEDS = [
    "goblin product manager",
    "desktop pet with chores",
    "haunted diary co-writer",
    "tiny courtroom for arguments",
    "AI board-game dungeon crier",
    "dream vending machine",
    "fortune-cookie debugger",
    "neighborhood myth generator",
]

MODEL_SUGGESTIONS = [
    "Qwen/Qwen2.5-14B-Instruct (general text, well under 32B)",
    "microsoft/Phi-3.5-mini-instruct (tiny text assistant angle)",
    "openbmb/MiniCPM3-4B (Tiny Titan + MiniCPM angle)",
    "openbmb/MiniCPM-V-4_5 (vision/OCR angle)",
    "nvidia/Nemotron-Nano-9B-v2 (Nemotron sponsor angle)",
]


def offline_idea(goal, track, skill, resources, count):
    seeds = PRACTICAL_SEEDS if track == "Backyard AI" else WHIMSICAL_SEEDS
    rng = random.Random(f"{goal}|{track}|{skill}|{resources}|{count}")
    chosen = rng.sample(seeds, k=min(count, len(seeds)))
    blocks = []
    for i, seed in enumerate(chosen, 1):
        tiny = "<=4B" in resources or "Zero GPU" in resources
        model = MODEL_SUGGESTIONS[2] if tiny else rng.choice(MODEL_SUGGESTIONS)
        blocks.append(f"""
### {i}. {seed.title()}
**One-line pitch:** A small Gradio app that turns `{goal or 'a personal pain point'}` into a shippable {track} demo using simple prompts and clear outputs.

**Basic build:**
1. One text box for the user's situation.
2. One dropdown for tone / constraint.
3. One model call that returns a structured answer.
4. One copy-ready README/demo script panel.

**Why it can win:** Targets the {track} track, stays simple enough to finish fast, and can be polished with a non-default UI for Off Brand / Best Demo.

**Suggested model:** {model}.
**Use credits:** {resources}.
**MVP files:** `app.py`, `requirements.txt`, `README.md`.
**Demo hook:** Show a before/after in under 45 seconds.
""")
    return "\n".join(blocks)


def build_prompt(goal, track, skill, resources, count):
    return f"""
You are a hackathon idea generator for Hugging Face × Gradio Build Small.
Use these rules exactly:\n{HACKATHON_RULES}

User goal: {goal or 'Build many small projects fast'}
Preferred track: {track}
Builder skill level: {skill}
Available resources: {resources}

Generate {count} project ideas. Keep code architecture basic and realistic for Hugging Face Spaces.
For each idea include:
- catchy title
- one-line pitch
- why it fits Build Small
- suggested model under 32B total params
- basic Gradio UI components
- 2-hour MVP plan
- demo video hook
- README tags to use
Prefer pure, clever ideas over complex engineering.
""".strip()


def generate(goal, track, skill, resources, count, use_model):
    if not use_model:
        return offline_idea(goal, track, skill, resources, count)

    token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if not token:
        return "⚠️ No HF_TOKEN found, so here is the deterministic offline generator output.\n\n" + offline_idea(goal, track, skill, resources, count)

    try:
        client = InferenceClient(model=MODEL_ID, token=token)
        messages = [
            {"role": "system", "content": "You create concise, high-leverage hackathon project ideas. Never suggest models over 32B parameters."},
            {"role": "user", "content": build_prompt(goal, track, skill, resources, count)},
        ]
        response = client.chat_completion(messages=messages, max_tokens=1800, temperature=0.8)
        return response.choices[0].message.content
    except Exception as exc:
        return f"⚠️ Model call failed: {exc}\n\nOffline fallback:\n\n" + offline_idea(goal, track, skill, resources, count)


with gr.Blocks(title="Build Small Idea Forge", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
# Build Small Idea Forge 🛠️🌲
Generate many simple, shippable project ideas for the Hugging Face × Gradio Build Small hackathon.

This Space is itself a Build Small project: a basic Gradio app using a default model under the 32B cap (`Qwen/Qwen2.5-14B-Instruct`) with an offline fallback.
""")
    with gr.Row():
        goal = gr.Textbox(label="What do you want to build around?", placeholder="Example: tools for students, silly games, document helpers, local community apps")
        track = gr.Radio(["Backyard AI", "Thousand Token Wood"], value="Backyard AI", label="Track")
    with gr.Row():
        skill = gr.Radio(["Beginner", "Intermediate", "Fast prototype only"], value="Beginner", label="Skill level")
        count = gr.Slider(1, 8, value=4, step=1, label="Number of ideas")
    resources = gr.CheckboxGroup(
        ["Hugging Face credits", "Zero GPU", "Modal credits", "<=4B Tiny Titan attempt", "Codex-built repo"],
        value=["Hugging Face credits", "Zero GPU", "Modal credits", "Codex-built repo"],
        label="Resources / prize angles",
    )
    use_model = gr.Checkbox(value=True, label="Use HF model if token is available")
    btn = gr.Button("Generate project ideas", variant="primary")
    output = gr.Markdown(label="Ideas")
    btn.click(generate, [goal, track, skill, resources, count, use_model], output)
    gr.Markdown(f"_Generated at runtime. Current UTC date in app environment: {datetime.now(timezone.utc).date()}._")

if __name__ == "__main__":
    demo.launch()
