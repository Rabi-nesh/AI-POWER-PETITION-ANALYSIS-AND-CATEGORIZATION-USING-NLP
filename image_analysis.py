# backend/analysis/image_analysis.py
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

# Lazy load global model to avoid re-loading each request
_processor = None
_model = None

def _load_blip():
    global _processor, _model
    if _processor is None or _model is None:
        print("🔹 Loading BLIP image captioning model (first time may take a minute)...")
        _processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        _model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        print("✅ BLIP model loaded.")
    return _processor, _model


def generate_caption(image_path: str) -> str:
    """
    Generate a natural-language caption for the image using BLIP.
    """
    try:
        processor, model = _load_blip()
        image = Image.open(image_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")
        out = model.generate(**inputs, max_length=60)
        caption = processor.decode(out[0], skip_special_tokens=True)
        return caption
    except Exception as e:
        return f"Error generating caption: {e}"
