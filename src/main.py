# main.py

import time
from ai.agent import Agent
from utils.screen_reader import (
    capture_screen,
    extract_text,
    detect_hdv,
    detect_categorie_bois,
    extract_resources,
    save_resources,
    HOTEL_DES_VENTES_REGION,
    show_target_region
)


def main():
    agent = Agent()
    agent.start_game()

    show_target_region()  # Affiche le cadre rouge une fois au lancement

    while True:
        img = capture_screen(HOTEL_DES_VENTES_REGION)
        text = extract_text(img)
        if detect_hdv(text):
            if detect_categorie_bois(text):
                resources = extract_resources(text)
                save_resources(resources)
                print("Ressources bois sauvegardées :", resources)
            else:
                print("Catégorie 'Bois' non détectée.")
        else:
            print("Hôtel de vente non détecté.")
        time.sleep(5)


if __name__ == "__main__":
    main()
