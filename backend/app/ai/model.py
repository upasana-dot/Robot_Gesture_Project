import json
import os

from transformers import pipeline

MODEL_NAME = os.getenv(
    "RAST_MODEL",
    "google/flan-t5-small",
)

_generator = None


def get_generator():
    global _generator

    if _generator is None:
        _generator = pipeline(
            "text2text-generation",
            model=MODEL_NAME,
            device=-1,
        )

    return _generator


def generate_text(instruction: str) -> str:
    prompt = f"""
Convert this robot instruction into JSON only.

Allowed actions: approach, grasp, lift, move_to, release.

Objects: red_cube, blue_cube, green_cube.
Targets: table, blue_zone, red_zone, green_zone.

Return this format:
{{"actions":[{{"action":"approach","object_name":"red_cube",
"target":null}}]}}

Instruction: {instruction}

JSON:
"""

    result = get_generator()(
        prompt,
        max_new_tokens=180,
        do_sample=False,
    )

    return result[0]["generated_text"]