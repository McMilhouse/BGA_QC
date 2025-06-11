PROGRAM_NAME = "les statistiques des tournois BGA"

import os
import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    try:
        import time
        timestamp = int(time.time())  # bust GitHub cache

        csv_url = f"https://raw.githubusercontent.com/Mcmilhouse/BGA_QC/main/data/BGA.csv?nocache={timestamp}"
        df = pd.read_csv(csv_url)

        # Nettoie les noms de colonnes (supprime les espaces avant/après)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier depuis GitHub : {e}")
        return None

df = load_data()

st.title(PROGRAM_NAME)

if df is not None:
    pseudo = st.text_input("Entre ton pseudo :").strip()

    if pseudo:
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
                f"- Tu as fini {finale} fois comme finaliste," if finale > 0 else
                "- Jamais finaliste,"
            )
            ligne_semi_finale = f"- Tu as fini {semi_finale} fois en demi-finale," if semi_finale > 0 else "- Jamais atteint la demi-finale,"
            ligne_quart = f"- Tu as fini {quart_de_finale} fois en quart de finale." if quart_de_finale > 0 else "- Jamais atteint le quart de finale."

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
            st.text(texte_resultat)
        else:
            st.warning("Pseudo non trouvé ou mal orthographié !")
else:
    st.error("Impossible de charger les données.")
