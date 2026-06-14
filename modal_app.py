"""Modal endpoint for Photo Archaeology Simulator text generation.

Deploy with:
    modal deploy modal_app.py

Then set the Hugging Face Space secret MODAL_EXCAVATE_URL to the printed /excavate URL.
"""

import modal

MODEL_ID = "Qwen/Qwen3-4B-Instruct-2507"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("fastapi[standard]", "torch", "transformers>=4.51.0", "accelerate", "sentencepiece")
)

app = modal.App("photo-archaeology-simulator")


@app.cls(image=image, gpu="A10G", timeout=240, scaledown_window=300)
class ArchaeologyWriter:
    @modal.enter()
    def load(self):
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        self.model = AutoModelForCausalLM.from_pretrained(MODEL_ID, device_map="auto", torch_dtype="auto")

    @modal.method()
    def write(self, artifacts, tone):
        prompt = f"""
You are a comic academic archaeologist studying messy modern rooms.
Write a faux-scholarly excavation report in markdown.
Tone: {tone}
Use numbered Clue entries matching these detected artifacts: {artifacts}
Invent playful carbon-dating methods for digital and household objects.
Keep it funny, kind, and under 700 words. Do not give real cleaning advice except as a joke.
""".strip()
        messages = [
            {"role": "system", "content": "You produce humorous pseudo-academic reports, never serious scientific claims."},
            {"role": "user", "content": prompt},
        ]
        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        output = self.model.generate(**inputs, max_new_tokens=900, temperature=0.85, do_sample=True)
        return self.tokenizer.decode(output[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)


@app.function(image=image, timeout=300)
@modal.fastapi_endpoint(method="POST")
def excavate(payload: dict):
    report = ArchaeologyWriter().write.remote(payload.get("artifacts", []), payload.get("tone", "Very academic"))
    return {"model": MODEL_ID, "report": report}
