import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pandas as pd

PROGRAM_NAME = "les statistiques des tournois BGA"

# Fonction qui cherche les infos du joueur et met à jour l'affichage
def chercher_joueur():
    pseudo = entree_pseudo.get().strip()
    if not pseudo:
        messagebox.showwarning("Attention", "Veuillez entrer un pseudo.")
        return

    joueur = df[df["Joueurs"].str.lower() == pseudo.lower()]
    total_joueur = df["Joueurs"].nunique()

    if not joueur.empty:
        participations = int(joueur.iloc[0]["Nb de participations"])
        points = int(joueur.iloc[0]["Total de points"])
        premier = int(joueur.iloc[0]["1ère place"])
        deuxieme = int(joueur.iloc[0]["2e place"])
        troisieme = int(joueur.iloc[0]["3e place"])
        cinq_a_huit = int(joueur.iloc[0]["5e à 8e place"])
        rang = int(joueur.iloc[0]["Rang"])
        victoires = int(joueur.iloc[0]["Victoire"])
        finale = int(joueur.iloc[0]["Finale"])
        semi_finale = int(joueur.iloc[0]["Demi-Finale"])
        quart_de_finale = int(joueur.iloc[0]["Quart de finale"])

        # Lignes conditionnelles
        ligne_premier = (
    f"- Tu as remporté {premier} tournoi," if premier == 1 else
    f"- Tu as remporté {premier} tournois," if premier > 1 else
    "- Tu n'as remporté aucun tournoi,"
)
        ligne_deuxieme = f"- Tu as fini {deuxieme} fois en 2e position," if deuxieme != 0 else "- Jamais en 2e position,"
        ligne_troisieme = f"- Tu as fini {troisieme} fois en 3e position," if troisieme != 0 else "- Jamais en 3e position,"
        ligne_cinq_a_huit = f"- Tu as fini {cinq_a_huit} fois entre la 5e et la 8e position." if cinq_a_huit != 0 else "- Jamais classé entre la 5e et la 8e position."

        ligne_victoires = (
    f"- Tu as remporté {victoires} tournoi," if victoires == 1 else
    f"- Tu as remporté {victoires} tournois," if victoires > 1 else
    "- Aucune victoire en tournoi,"
)
        ligne_finale = (
    f"- Tu as fini {finale} fois comme finaliste," if finale > 1 else
    f"- Tu as fini {finale} fois comme finaliste," if finale == 1 else
    "- Jamais finaliste,"
)

        if semi_finale > 0:
            ligne_semi_finale = f"- Tu as fini {semi_finale} fois en demi-finale,"
        elif finale == 0:
            ligne_semi_finale = "- Jamais atteint la demi-finale,"
        else:
            ligne_semi_finale = ""

        if quart_de_finale > 0:
            ligne_quart = f"- Tu as fini {quart_de_finale} fois en quart de finale."
        elif finale == 0 and semi_finale == 0:
            ligne_quart = "- Jamais atteint le quart de finale."
        else:
            ligne_quart = ""

        texte_resultat = (
            f"Tu as un total de {points} points.\n"
            f"Tu es présentement en {rang}e position sur {total_joueur} participants.\n\n"
            f"{pseudo}, en {participations} tournois au total:\n\n"
            f"En mode suisse:\n"
            f"{ligne_premier}\n"
            f"{ligne_deuxieme}\n"
            f"{ligne_troisieme}\n"
            f"{ligne_cinq_a_huit}\n\n"
            f"En mode double élimination:\n"
            f"{ligne_victoires}\n"
            f"{ligne_finale}\n"
            f"{ligne_semi_finale}\n"
            f"{ligne_quart}"
        )
    else:
        texte_resultat = "Pseudo non trouvé ou mal orthographié !"

    label_resultat.config(text=texte_resultat)


# --- Chargement du fichier CSV ---
try:
    df = pd.read_csv("data/BGA.csv", encoding="utf-8")
except FileNotFoundError:
    print("Fichier data/BGA.csv non trouvé. Vérifie le chemin.")
    exit(1)

# --- Création de la fenêtre principale ---
fenetre = tk.Tk()
fenetre.title(PROGRAM_NAME)
fenetre.geometry("600x700")

# --- Chargement du logo ---
try:
    image = Image.open("Images/BGA Qc.jpg")
    image = image.resize((150, 150))
    photo = ImageTk.PhotoImage(image)
except Exception as e:
    print("Erreur lors du chargement du logo :", e)
    photo = None

# Charger ton icône perso (petite image png)
try:
    icone = Image.open("Images/BGA.png")
    icone = icone.resize((64, 64))
    photo_icone = ImageTk.PhotoImage(icone)
    fenetre.iconphoto(False, photo_icone)
except Exception as e:
    print("Erreur chargement icône fenêtre :", e)

# --- Widgets ---

if photo:
    label_logo = tk.Label(fenetre, image=photo)
    label_logo.image = photo
    label_logo.pack(pady=10)

label_intro = tk.Label(fenetre, text=f"Bienvenue dans {PROGRAM_NAME} !", font=("Calibri", 16))
label_intro.pack(pady=10)

label_pseudo = tk.Label(fenetre, text="Entre ton pseudo :", font=("Calibri", 12))
label_pseudo.pack()

entree_pseudo = tk.Entry(fenetre, font=("Calibri", 12), width=30)
entree_pseudo.pack(pady=5)

bouton_rechercher = tk.Button(fenetre, text="Chercher", font=("Calibri", 12), command=chercher_joueur)
bouton_rechercher.pack(pady=10)

label_resultat = tk.Label(fenetre, text="", font=("Calibri", 12), justify="left", wraplength=580)
label_resultat.pack(pady=20)

# --- Démarrage de la boucle tkinter ---
fenetre.mainloop()
