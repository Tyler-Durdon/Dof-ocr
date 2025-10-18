# main.py

import time
import keyboard
from ai.agent import Agent
from utils.screen_reader import (
    capture_screen,
    extract_text,
    remove_accents,
    detect_hdv_fuzzy,
    detect_categorie_bois,
    extract_resources,
    HOTEL_DES_VENTES_REGION,
    show_target_region,
    get_or_select_region,
    set_region,
    draw_zones
)
from PIL import Image


def split_zones(region):
    left, top, width, height = region
    # Découpage des zones (à ajuster selon l'UI du jeu)
    zone_hdv = (left, top, width, int(height * 0.15))  # Haut
    zone_categories = (left, top + int(height * 0.15),
                       int(width * 0.3), int(height * 0.5))  # Gauche
    zone_bois = (left, top + int(height * 0.35), int(width * 0.3),
                 int(height * 0.1))  # Gauche, sous-catégorie
    zone_ressources = (left + int(width * 0.3), top + int(height * 0.15),
                       int(width * 0.7), int(height * 0.85))  # Droite
    return zone_hdv, zone_categories, zone_bois, zone_ressources


def main():
    agent = Agent()
    agent.start_game()

    region = get_or_select_region()
    print("Appuyez sur SHIFT+R pour redéfinir la zone à analyser.")

    while True:
        if keyboard.is_pressed('shift+r'):
            print("Redéfinition de la zone...")
            region = set_region()
            time.sleep(1)

        # Découpe les zones
        zone_hdv, zone_categories, zone_bois, zone_ressources = split_zones(
            region)

        # OCR sur chaque zone
        img_hdv = capture_screen(zone_hdv)
        img_bois = capture_screen(zone_bois)
        img_ressources = capture_screen(zone_ressources)

        text_hdv = remove_accents(extract_text(img_hdv))
        text_bois = remove_accents(extract_text(img_bois))
        text_ressources = remove_accents(extract_text(img_ressources))

        hdv_detected = detect_hdv_fuzzy(text_hdv)
        bois_checked = detect_categorie_bois(
            text_bois) if hdv_detected else False

        if hdv_detected and bois_checked:
            resources = extract_resources(text_ressources)
            print("\nObjets et prix en kamas :")
            for res in resources:
                print(f"- {res['nom']} : {res['prix_moyen']} kamas")
        time.sleep(1)


if __name__ == "__main__":
    main()
