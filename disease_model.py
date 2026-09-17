# disease_model.py
"""Plant disease detection module.

The demo implementation uses a pretrained torchvision model to produce a
vector of logits and then returns a placeholder label. In a real system you
would load a custom model trained on leaf images, map its outputs to
meaningful disease names, and perhaps highlight affected regions.
"""

import base64
import io
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from PIL import Image

import torch
from torchvision import transforms, models

_MODEL = None
_TRANSFORM = None


def _initialize():
    global _MODEL, _TRANSFORM
    if _MODEL is None:
        # load a lightweight pretrained model; in practice replace with a
        # model trained on plant leaves
        _MODEL = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        _MODEL.eval()
        _TRANSFORM = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]),
        ])


from dotenv import load_dotenv
from PIL import Image

PROJECT_ROOT = Path(__file__).parent
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_FILE)


def _parse_response(text: str) -> dict:
    """Convert the vision response into the fields used by the UI."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    disease = text.strip()
    treatment = "Follow the recommended treatment on the product label and consult a local agriculture officer before spraying."
    observations = ""

    for line in lines:
        lower_line = line.lower()
        if lower_line.startswith("diagnosis:"):
            disease = line.split(":", 1)[1].strip()
        elif lower_line.startswith("treatment:"):
            treatment = line.split(":", 1)[1].strip()
        elif lower_line.startswith("observations:"):
            observations = line.split(":", 1)[1].strip()

    return {
        "disease": disease,
        "treatment": treatment,
        "observations": observations,
        "confidence": "See observations",
    }


def predict_disease(image: Image.Image) -> dict:
    """Assess a plant image with OpenAI vision when configured.

    A generic ImageNet classifier cannot identify plant diseases, so this
    function never invents a disease label when the vision service is absent.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "disease": "Vision AI is not configured",
            "treatment": "Add an OPENAI_API_KEY to enable plant disease analysis. Until then, do not spray based on this result; consult a local agriculture officer.",
            "observations": "The image was received, but a disease diagnosis requires a plant-trained vision model.",
            "confidence": "Not available",
        }

    try:
        image_buffer = io.BytesIO()
        image.convert("RGB").save(image_buffer, format="JPEG", quality=85)
        image_data = base64.b64encode(image_buffer.getvalue()).decode("ascii")
        prompt = """You are a cautious agricultural plant pathologist. Analyze this plant leaf image.
Return exactly three lines:
Diagnosis: <most likely disease or Healthy; say Uncertain if the image is insufficient>
Observations: <visible symptoms, affected area, and confidence level>
Treatment: <safe next steps; do not recommend a chemical unless you mention following the local label>
Do not claim certainty from a low-quality or non-leaf image. If unclear, say exactly:
Image is not clear. Please upload a better image."""
        payload = json.dumps({
            "model": os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            "input": [{"role": "user", "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": f"data:image/jpeg;base64,{image_data}"},
            ]}],
            "temperature": 0.1,
        }).encode("utf-8")
        request = urllib.request.Request(
            "https://api.openai.com/v1/responses",
            data=payload,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
        return _parse_response(result.get("output_text", ""))
    except (OSError, ValueError, urllib.error.URLError) as error:
        return {
            "disease": "Vision analysis failed",
            "treatment": "Check your OPENAI_API_KEY and internet connection, then try again. Do not apply chemicals based on an unverified diagnosis.",
            "observations": str(error),
            "confidence": "Not available",
        }
