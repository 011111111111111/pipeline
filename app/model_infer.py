# app/model_infer.py
from transformers import ViTFeatureExtractor, ViTForImageClassification
from PIL import Image # type: ignore
import torch # type: ignore
import os 
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to load from .env file first (for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, continue with environment variables

# Get token from environment (either from .env or system environment)
your_token = os.environ.get("HF_TOKEN")
if not your_token:
    raise ValueError("HF_TOKEN environment variable is not set. Please set it in your .env file or as an environment variable.")

# Ensure token is properly formatted
if not your_token.startswith('hf_'):
    your_token = f'hf_{your_token}'
    logger.info("Added 'hf_' prefix to token")

# Validate token format
if not your_token.startswith('hf_') or len(your_token) < 10:
    raise ValueError("Invalid HF_TOKEN format. Token must start with 'hf_' and be at least 10 characters long.")

model_name = 'google/vit-base-patch16-224'

# Load model and feature extractor
try:
    logger.info("Loading model and feature extractor...")
    feature_extractor = ViTFeatureExtractor.from_pretrained(
        model_name, 
        token=your_token,
        local_files_only=True  # Use cached model
    )
    model = ViTForImageClassification.from_pretrained(
        model_name, 
        token=your_token,
        local_files_only=True  # Use cached model
    )
    model.eval()
    logger.info("Model and feature extractor loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    raise

def predict(image_path):
    try:
        image = Image.open(image_path).convert("RGB")  # ensures image mode consistency
        inputs = feature_extractor(images=image, return_tensors="pt", padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
        predicted_class_idx = logits.argmax(-1).item()
        return model.config.id2label[predicted_class_idx]
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        raise

