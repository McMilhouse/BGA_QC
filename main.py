PROGRAM_NAME = "les statistiques des tournois BGA"

import os
import streamlit as st
import pandas as pd

# --- Chargement des données principales depuis GitHub ---
@st.cache_data
def load_data():
    try:
        import time
        timestamp = int(time.time())  # évite le cache GitHub

        csv_url = f"https://raw.githubusercontent.com/Mcmilhouse/BGA_QC/main/data/BGA.csv?nocache={timestamp}"
        df = pd.read_csv(csv_url)

        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier depuis GitHub : {e}")
        return None

# --- Chargement dynamique des noms de jeux depuis Google Sheets ---
@st.cache_data
def charger_liste_jeux(mode="Suisse"):
    try:
        if mode == "Suisse":
            url_jeux = "https://docs.google.com/spreadsheets/d/1JEf5uE3lAwqiRCgVQTuQ3CCoqYtshTSaIUp3S49BG5w/export?format=csv&gid=0"
        else:
            url_jeux = "https://docs.google.com/spreadsheets/d/1JEf5uE3lAwqiRCgVQTuQ3CCoqYtshTSaIUp3S49BG5w/export?format=csv&gid=344099596"
        
        jeux_df = pd.read_csv(url_jeux)
        liste_jeux = jeux_df.iloc[:, 0].dropna().unique().tolist()
        return liste_jeux
    except Exception as e:
        st.error(f"Erreur de chargement des jeux : {e}")
        return []

# --- Application principale ---
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

            # --- NOUVELLE SECTION : Associer des jeux à ses performances ---
            st.markdown("---")
            st.subheader("Associer des jeux à tes meilleures positions")

            mode_choisi = st.radio("Quel mode veux-tu annoter ?", ["Mode Suisse", "Double élimination"])
            liste_jeux = charger_liste_jeux(mode=mode_choisi)

            if mode_choisi == "Mode Suisse":
                jeu_1er = st.selectbox("Jeu où tu as terminé 1er", options=liste_jeux)
                jeu_2e = st.selectbox("Jeu où tu as terminé 2e", options=liste_jeux)
                jeu_3e = st.selectbox("Jeu où tu as terminé 3e", options=liste_jeux)

                if st.button("Valider", key="valide_suisse"):
                    st.success(f"🥇 1er : {jeu_1er}\n🥈 2e : {jeu_2e}\n🥉 3e : {jeu_3e}")

            elif mode_choisi == "Double élimination":
                jeu_victoire = st.selectbox("Jeu remporté", options=liste_jeux)
                jeu_finale = st.selectbox("Jeu en finale", options=liste_jeux)
                jeu_demi1 = st.selectbox("1er jeu en demi-finale", options=liste_jeux)
                jeu_demi2 = st.selectbox("2e jeu en demi-finale", options=liste_jeux)

                if st.button("Valider", key="valide_double"):
                    st.success(f"🏆 Gagnant : {jeu_victoire}\n🥈 Finaliste : {jeu_finale}\n🏅 Demi-finales : {jeu_demi1}, {jeu_demi2}")

        else:
            st.warning("Pseudo non trouvé ou mal orthographié !")
else:
    st.error("Impossible de charger les données.")

