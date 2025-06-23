import streamlit as st
import pandas as pd
import time

PROGRAM_NAME = "Statistiques des tournois BGA"

@st.cache_data(ttl=600)
def charger_stats_principales():
    timestamp = int(time.time())
    url = f"https://raw.githubusercontent.com/Mcmilhouse/BGA_QC/main/data/BGA.csv?nocache={timestamp}"
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Erreur chargement stats principales: {e}")
        return None

@st.cache_data(ttl=600)
def charger_feuille(gid):
    url = f"https://docs.google.com/spreadsheets/d/1JEf5uE3lAwqiRCgVQTuQ3CCoqYtshTSaIUp3S49BG5w/export?format=csv&gid={gid}"
    try:
        df = pd.read_csv(url)
        # Nettoyage colonnes
        df.columns = df.columns.str.strip()
        df.columns = df.columns.str.capitalize()
        # Affichage colonnes pour debug
        st.write(f"Colonnes chargées pour gid={gid} :", df.columns.tolist())
        return df
    except Exception as e:
        st.error(f"Erreur chargement feuille gid={gid}: {e}")
        return pd.DataFrame()

st.title(PROGRAM_NAME)

pseudo = st.text_input("Entre ton pseudo").strip().lower()

if pseudo:
    df_stats = charger_stats_principales()
    if df_stats is None:
        st.error("Impossible de charger les statistiques principales.")
        st.stop()

    joueur = df_stats[df_stats["Joueurs"].str.lower() == pseudo]
    if joueur.empty:
        st.warning("Pseudo non trouvé.")
        st.stop()

    st.subheader("Résumé général")
    st.write(f"Points total : {int(joueur.iloc[0]['Total de points'])}")
    st.write(f"Position globale : {int(joueur.iloc[0]['Rang'])} / {df_stats['Joueurs'].nunique()}")
    st.write(f"Tournois joués : {int(joueur.iloc[0]['Nb de participations'])}")

    # Charger feuilles Google Sheets
    df_suisse = charger_feuille(gid=0)
    df_elim = charger_feuille(gid=344099596)

    # Filtrer par pseudo
    st.write("Colonnes dans df_suisse :", df_suisse.columns.tolist())
    df_suisse_joueur = df_suisse[df_suisse["Joueur"].str.lower() == pseudo]
    df_elim_joueur = df_elim[df_elim["Joueur"].str.lower() == pseudo]

    st.subheader("Mode Suisse")
    if not df_suisse_joueur.empty:
        for place in [1, 2, 3]:
            jeux = df_suisse_joueur[df_suisse_joueur["Position"] == place]["Jeu"].tolist()
            if jeux:
                emojis = {1:"🥇", 2:"🥈", 3:"🥉"}
                st.write(f"{emojis[place]} Position {place} à : {', '.join(jeux)}")
    else:
        st.info("Pas de résultats en mode suisse.")

    st.subheader("Double élimination")
    if not df_elim_joueur.empty:
        for res in ["Gagnant", "Finaliste", "Demi-finaliste"]:
            jeux = df_elim_joueur[df_elim_joueur["Résultat"].str.lower() == res.lower()]["Jeu"].tolist()
            if jeux:
                emojis = {"Gagnant":"🏆", "Finaliste":"🎯", "Demi-finaliste":"🏅"}
                st.write(f"{emojis[res]} {res} à : {', '.join(jeux)}")
    else:
        st.info("Pas de résultats en double élimination.")
else:
    st.info("Entre un pseudo pour voir les résultats.")
