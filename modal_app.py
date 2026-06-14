"""Modal vision-language endpoint for Photo Archaeology Simulator.

Deploy with:
    modal deploy modal_app.py

Set the Hugging Face Space secret MODAL_EXCAVATE_URL to the printed /excavate URL.
"""

import json
import re

import modal

MODEL_ID = "Qwen/Qwen2.5-VL-7B-Instruct"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "accelerate",
        "fastapi[standard]",
        "pillow",
        "qwen-vl-utils[decord]",
        "torch",
        "transformers>=4.49.0",
    )
)

app = modal.App("photo-archaeology-simulator")


@app.cls(image=image, gpu="A10G", timeout=300, scaledown_window=300)
class ExcavationModel:
    @modal.enter()
    def load(self):
        from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

        self.processor = AutoProcessor.from_pretrained(MODEL_ID)
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(MODEL_ID, device_map="auto", torch_dtype="auto")

    @modal.method()
    def excavate(self, image_data_url: str, tone: str):
        from qwen_vl_utils import process_vision_info

        prompt = f"""
Analyze this messy room or workspace photo as a playful archaeologist.
Return ONLY valid JSON with this schema:
{{
  "artifacts": [{{"label": "short funny artifact name", "x": 0.0, "y": 0.0, "period": "Early Cable Age|Pandemic Desk Layer|Late Notification Period"}}],
  "report": "markdown faux-academic excavation report under 700 words"
}}
Rules:
- x and y are approximate normalized coordinates from 0 to 1.
- Use 4 to 8 artifacts.
- Tone: {tone}.
- Be funny, kind, specific to visible objects, and pseudo-scholarly.
- Do not include chain-of-thought, markdown fences, or text outside JSON.
""".strip()
        messages = [{"role": "user", "content": [{"type": "image", "image": image_data_url}, {"type": "text", "text": prompt}]}]
        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = self.processor(text=[text], images=image_inputs, videos=video_inputs, padding=True, return_tensors="pt").to(self.model.device)
        output = self.model.generate(**inputs, max_new_tokens=1200, temperature=0.75, top_p=0.9, do_sample=True)
        decoded = self.processor.batch_decode(output[:, inputs.input_ids.shape[1]:], skip_special_tokens=True)[0]
        return parse_json(decoded)


def parse_json(text: str):
    cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    match = re.search(r"\{.*\}", cleaned, flags=re.S)
    if match:
        cleaned = match.group(0)
    return json.loads(cleaned)


@app.function(image=image, timeout=360)
@modal.fastapi_endpoint(method="POST")
def excavate(payload: dict):
    return ExcavationModel().excavate.remote(payload["image"], payload.get("tone", "Very academic"))
