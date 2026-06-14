import os

import gradio as gr
from huggingface_hub import InferenceClient

MODEL_ID = os.getenv("MODEL_ID", "Qwen/Qwen3-32B")

HACKATHON_CONTEXT = """
Build Small hackathon constraints:
- Build something small, local, tinkerable, and yours.
- Every model must stay at or under the 32B total-parameter cap.
- Ship a Gradio app as a Hugging Face Space in the Build Small org.
- Record a demo, make one social post, and link both from the Space README.
- Tracks: Backyard AI for practical daily-life problem solvers; Thousand Token Wood for whimsical AI-native fun.
""".strip()

SYSTEM_PROMPT = """
You are a sharp hackathon product ideation assistant.
Generate simple, clever, buildable project ideas for the Hugging Face × Gradio Build Small hackathon.
Do not recommend any model over 32B parameters.
Prefer ideas that can be built in one small Gradio Space with beginner-friendly code.
""".strip()


def build_prompt(goal, track, count):
    return f"""
{HACKATHON_CONTEXT}

Builder goal:
{goal or 'Generate small, clever hackathon projects that are realistic to ship fast.'}

Track focus: {track}
Number of ideas: {count}

For each idea, return:
1. Title
2. One-line pitch
3. Why it fits the selected track
4. Minimal Gradio UI
5. Files needed
6. 2-hour MVP plan
7. Demo video hook

Keep everything practical, concise, and easy to implement.
""".strip()


def generate(goal, track, count):
    token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if not token:
        return "Set an `HF_TOKEN` Space secret to generate ideas with the selected 32B model."

    try:
        client = InferenceClient(model=MODEL_ID, token=token)
        response = client.chat_completion(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_prompt(goal, track, count)},
            ],
            max_tokens=2200,
            temperature=0.85,
        )
        return response.choices[0].message.content
    except Exception as exc:
        return f"Model call failed for `{MODEL_ID}`: {exc}"


with gr.Blocks(title="Build Small Idea Forge", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        f"""
# Build Small Idea Forge 🛠️

Generate simple, clever project ideas for the Hugging Face × Gradio Build Small hackathon.

**Model:** `{MODEL_ID}`  
**Rule:** keep project ideas compatible with the hackathon's 32B model cap.
"""
    )

    goal = gr.Textbox(
        label="What kind of projects do you want?",
        placeholder="Example: useful student tools, funny AI games, document helpers, local community apps",
        lines=3,
    )
    track = gr.Radio(
        ["Backyard AI", "Thousand Token Wood"],
        value="Backyard AI",
        label="Hackathon track",
    )
    count = gr.Slider(1, 8, value=5, step=1, label="Number of ideas")
    btn = gr.Button("Generate project ideas", variant="primary")
    output = gr.Markdown(label="Ideas")

    btn.click(generate, [goal, track, count], output)

if __name__ == "__main__":
    demo.launch()
