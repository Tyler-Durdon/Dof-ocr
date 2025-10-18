import os
import json
import pytesseract
from PIL import Image, ImageDraw
import pyautogui
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import difflib
import tkinter as tk
from tkinter import simpledialog
import unicodedata

# Configure le chemin de Tesseract pour Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# À ajuster selon la position de la fenêtre Dofus
# Pour capturer tout l'écran, on met la région à None
# (left, top, width, height) ou None pour tout l'écran
HOTEL_DES_VENTES_REGION = None
# HOTEL_DES_VENTES_REGION = (100, 100, 800, 600)  # (left, top, width, height)

# Charge TrOCR
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
    # Essaye TrOCR d'abord
    try:
        pixel_values = processor(
            images=image, return_tensors="pt").pixel_values
        generated_ids = model.generate(pixel_values)
        text = processor.batch_decode(
            generated_ids, skip_special_tokens=True)[0]
        if text and len(text.strip()) > 3:
            return text
    except Exception as e:
        print(f"Erreur TrOCR: {e}")
    # Fallback pytesseract en français
    try:
        text = pytesseract.image_to_string(image, lang='fra')
        return text
    except Exception as e:
        print(f"Erreur pytesseract: {e}")
        return ""


def detect_hdv(text):
    # Recherche "Hôtel de vente" (sans 's')
    return "hôtel de vente" in text.lower()


def remove_accents(input_str):
    return ''.join(
        c for c in unicodedata.normalize('NFD', input_str)
        if unicodedata.category(c) != 'Mn'
    )


def detect_hdv_fuzzy(text, threshold=0.7):
    """
    Détecte 'Hotel de vente' même si le texte OCR n'est pas exact, sans accent.
    """
    target = "hotel de vente"
    lines = text.lower().split('\n')
    for line in lines:
        line_no_acc = remove_accents(line.strip())
        ratio = difflib.SequenceMatcher(None, line_no_acc, target).ratio()
        if ratio >= threshold:
            return True
    return False


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


def select_region():
    """
    Affiche une fenêtre transparente permettant à l'utilisateur de sélectionner une région à l'écran.
    Retourne (left, top, width, height)
    """
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.attributes('-alpha', 0.3)
    root.attributes('-topmost', True)
    root.config(cursor="crosshair")
    root.title("Sélectionnez la région à analyser (cadre jaune)")

    canvas = tk.Canvas(root, cursor="crosshair", bg="black")
    canvas.pack(fill=tk.BOTH, expand=True)

    region = {}

    def on_mouse_down(event):
        region['x1'] = event.x
        region['y1'] = event.y
        region['rect'] = canvas.create_rectangle(
            event.x, event.y, event.x, event.y, outline='yellow', width=3)

    def on_mouse_drag(event):
        canvas.coords(region['rect'], region['x1'],
                      region['y1'], event.x, event.y)

    def on_mouse_up(event):
        region['x2'] = event.x
        region['y2'] = event.y
        root.quit()

    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)

    root.mainloop()
    root.destroy()

    x1, y1, x2, y2 = region['x1'], region['y1'], region['x2'], region['y2']
    left = min(x1, x2)
    top = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    return (left, top, width, height)


def get_or_select_region():
    global HOTEL_DES_VENTES_REGION
    if HOTEL_DES_VENTES_REGION is None:
        HOTEL_DES_VENTES_REGION = select_region()
    return HOTEL_DES_VENTES_REGION


def set_region():
    """
    Permet de redéfinir la région à analyser via la sélection utilisateur.
    """
    global HOTEL_DES_VENTES_REGION
    HOTEL_DES_VENTES_REGION = select_region()
    return HOTEL_DES_VENTES_REGION
