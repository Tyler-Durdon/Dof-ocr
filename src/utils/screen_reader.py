import os
import json
import pytesseract
from PIL import Image, ImageDraw
import pyautogui
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

# Configure le chemin de Tesseract pour Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# À ajuster selon la position de la fenêtre Dofus
# Pour capturer tout l'écran, on met la région à None
# (left, top, width, height) ou None pour tout l'écran
HOTEL_DES_VENTES_REGION = None
# HOTEL_DES_VENTES_REGION = (100, 100, 800, 600)  # (left, top, width, height)

# Charge le modèle TrOCR pour texte imprimé (printed)
processor = TrOCRProcessor.from_pretrained(
    "microsoft/trocr-base-printed", use_fast=True)
model = VisionEncoderDecoderModel.from_pretrained(
    "microsoft/trocr-base-printed")


def capture_screen(region=HOTEL_DES_VENTES_REGION, show_box=False):
    screenshot = pyautogui.screenshot(region=region)
    if show_box and region is not None:
        # Dessine un cadre rouge sur la région ciblée sur une capture globale
        full_screen = pyautogui.screenshot()
        draw = ImageDraw.Draw(full_screen)
        left, top, width, height = region
        right = left + width
        bottom = top + height
        draw.rectangle([left, top, right, bottom], outline="red", width=4)
        full_screen.show()
    elif show_box and region is None:
        # Affiche juste la capture plein écran
        screenshot.show()
    return screenshot


def extract_text(image):
    # Convertit l'image PIL en RGB
    if image.mode != "RGB":
        image = image.convert("RGB")
    # Prépare l'image pour TrOCR
    pixel_values = processor(images=image, return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values)
    text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return text


def detect_hdv(text):
    # Recherche "Hôtel de vente" (sans 's')
    return "hôtel de vente" in text.lower()


def detect_categorie_bois(text):
    """
    Détecte si la catégorie 'Bois' est cochée.
    On cherche une case cochée juste avant 'bois' dans le texte OCR.
    Exemples de cases cochées : '☑', '✔', '[x]', 'X', etc.
    """
    lines = text.lower().split('\n')
    for line in lines:
        if "bois" in line:
            # Cherche un symbole de coche avant 'bois'
            idx = line.find("bois")
            prefix = line[:idx].strip()
            # Liste de symboles ou mots qui indiquent une coche
            checked_symbols = ["☑", "✔", "[x]", "x", "✓"]
            if any(sym in prefix for sym in checked_symbols):
                return True
            # Optionnel : si la ligne commence par 'bois' et est isolée, on peut aussi considérer cochée
            if prefix.endswith(":") or prefix == "":
                continue
    return False


def extract_resources(text):
    lines = text.split('\n')
    resources = []
    for line in lines:
        if line.strip() and any(char.isdigit() for char in line):
            parts = line.split()
            if len(parts) >= 3:
                name = " ".join(parts[:-2])
                level = parts[-2]
                price = parts[-1]
                resources.append({
                    "nom": name,
                    "niveau": level,
                    "prix_moyen": price
                })
    return resources


def save_resources(resources, path="json/bois_resources.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(resources, f, ensure_ascii=False, indent=2)


def show_target_region():
    # Affiche le cadre rouge sur la région ciblée
    capture_screen(HOTEL_DES_VENTES_REGION, show_box=True)
