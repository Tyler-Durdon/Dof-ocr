# main.py

import time
import keyboard
from ai.agent import Agent
from utils.screen_reader import (
    capture_screen,
    extract_text,
    detect_hdv_fuzzy,
    detect_categorie_bois,
    extract_resources,
    HOTEL_DES_VENTES_REGION,
    show_target_region,
    get_or_select_region,
    set_region
)


def main():
    agent = Agent()
    agent.start_game()

    region = get_or_select_region()  # Sélectionne la région au lancement
    show_target_region()  # Affiche le cadre rouge une fois au lancement

    print("Appuyez sur SHIFT+R pour redéfinir la zone à analyser.")

    while True:
        if keyboard.is_pressed('shift+r'):
            print("Redéfinition de la zone...")
            region = set_region()
            show_target_region()
            time.sleep(1)  # Anti double-déclenchement

        img = capture_screen(region)
        text = extract_text(img)
        hdv_detected = detect_hdv_fuzzy(text)
        bois_checked = detect_categorie_bois(text) if hdv_detected else False

        print(
            f"Hôtel de vente : {'ON' if hdv_detected else 'OFF'} | Catégorie Bois : {'ON' if bois_checked else 'OFF'}")
        time.sleep(1)  # 1 seconde d'intervalle


if __name__ == "__main__":
    main()
