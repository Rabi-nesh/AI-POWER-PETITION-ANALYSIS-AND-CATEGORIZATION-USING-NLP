from flask import Blueprint, request, jsonify
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
import os

analyze_bp = Blueprint("analyze_bp", __name__)

# Load BLIP model once (Option B — scene caption)
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

UPLOAD_FOLDER = os.path.join(os.getcwd(), "backend", "data", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@analyze_bp.route("/api/analyze-image", methods=["POST"])
def analyze_image():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        raw_image = Image.open(file_path).convert("RGB")

        # Generate a natural language caption
        inputs = processor(raw_image, return_tensors="pt")
        out = model.generate(**inputs, max_new_tokens=50)
        caption = processor.decode(out[0], skip_special_tokens=True)

        return jsonify({"description": caption})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
