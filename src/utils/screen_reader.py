import os
import json
import pytesseract
from PIL import Image, ImageDraw
import pyautogui

# Configure le chemin de Tesseract pour Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# À ajuster selon la position de la fenêtre Dofus
HOTEL_DES_VENTES_REGION = (100, 100, 800, 600)  # (left, top, width, height)


def capture_screen(region=HOTEL_DES_VENTES_REGION, show_box=False):
    screenshot = pyautogui.screenshot(region=region)
    if show_box:
        # Dessine un cadre rouge sur la région ciblée sur une capture globale
        full_screen = pyautogui.screenshot()
        draw = ImageDraw.Draw(full_screen)
        left, top, width, height = region
        right = left + width
        bottom = top + height
        draw.rectangle([left, top, right, bottom], outline="red", width=4)
        full_screen.show()
    return screenshot


def extract_text(image):
    return pytesseract.image_to_string(image, lang='fra')


def detect_hdv(text):
    # Recherche "Hôtel de vente" (sans 's')
    return "hôtel de vente" in text.lower()


def detect_categorie_bois(text):
    return "bois" in text.lower()


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
