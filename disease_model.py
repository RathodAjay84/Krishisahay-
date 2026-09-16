# disease_model.py
"""Plant disease detection module.

The demo implementation uses a pretrained torchvision model to produce a
vector of logits and then returns a placeholder label. In a real system you
would load a custom model trained on leaf images, map its outputs to
meaningful disease names, and perhaps highlight affected regions.
"""

import os
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


"""Plant image assessment using a vision-capable Gemini model."""

import os

from dotenv import load_dotenv
from PIL import Image

load_dotenv()


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
    """Assess a plant image with Gemini Vision when configured.

    A generic ImageNet classifier cannot identify plant diseases, so this
    function never invents a disease label when the vision service is absent.
    """
    api_key = os.getenv("GEMINI_API")
    if not api_key:
        return {
            "disease": "Vision AI is not configured",
            "treatment": "Add a GEMINI_API key to enable plant disease analysis. Until then, do not spray based on this result; consult a local agriculture officer.",
            "observations": "The image was received, but a disease diagnosis requires a plant-trained vision model.",
            "confidence": "Not available",
        }

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = """You are a cautious agricultural plant pathologist. Analyze this plant leaf image.
Return exactly three lines:
Diagnosis: <most likely disease or Healthy; say Uncertain if the image is insufficient>
Observations: <visible symptoms, affected area, and confidence level>
Treatment: <safe next steps; do not recommend a chemical unless you mention following the local label>
Do not claim certainty from a low-quality or non-leaf image."""
        response = model.generate_content([prompt, image])
        return _parse_response(response.text)
    except Exception as error:
        return {
            "disease": "Vision analysis failed",
            "treatment": "Check your GEMINI_API key and internet connection, then try again. Do not apply chemicals based on an unverified diagnosis.",
            "observations": str(error),
            "confidence": "Not available",
        }
