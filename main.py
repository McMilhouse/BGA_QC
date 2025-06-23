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
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Erreur chargement stats principales: {e}")
        return None

@st.cache_data(ttl=600)
def charger_feuille(gid):
    url = f"https://docs.google.com/spreadsheets/d/1JEf5uE3lAwqiRCgVQTuQ3CCoqYtshTSaIUp3S49BG5w/export?format=csv&gid={gid}"
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.lower()
        # Ligne suivante supprimée pour ne pas afficher les colonnes chargées
        # st.write(f"Colonnes chargées pour gid={gid} :", df.columns.tolist())
        return df
    except Exception as e:
        st.error(f"Erreur chargement feuille gid={gid}: {e}")
        return pd.DataFrame()

def chercher_places_suisse(df, pseudo):
    places = ["1er", "2e", "3e"]
    resultats = {1: [], 2: [], 3: []}
    pseudo = pseudo.lower()
    for idx, col in enumerate(places, 1):
        if col in df.columns:
            mask = df[col].apply(lambda x: pseudo in [p.strip().lower() for p in str(x).split('/')])
            jeux = df.loc[mask, "jeu"].tolist()
            resultats[idx].extend(jeux)
    return resultats

def chercher_resultats_double(df, pseudo):
    colonnes = {"gagnant(e)": "Gagnant", "finaliste(s)": "Finaliste", "semi-finaliste(s)": "Demi-finaliste"}
    resultats = {v: [] for v in colonnes.values()}
    pseudo = pseudo.lower()
    for col, nom_resultat in colonnes.items():
        if col in df.columns:
            mask = df[col].apply(lambda x: pseudo in [p.strip().lower() for p in str(x).split('/')])
            jeux = df.loc[mask, "jeu"].tolist()
            resultats[nom_resultat].extend(jeux)
    return resultats

st.title(PROGRAM_NAME)

pseudo = st.text_input("Entre ton pseudo").strip().lower()

if pseudo:
    df_stats = charger_stats_principales()
    if df_stats is None:
        st.error("Impossible de charger les statistiques principales.")
        st.stop()

    joueur = df_stats[df_stats["joueurs"].str.lower() == pseudo]
    if joueur.empty:
        st.warning("Pseudo non trouvé.")
        st.stop()

    st.subheader("Résumé général")
    st.write(f"Points total : {int(joueur.iloc[0]['total de points'])}")
    st.write(f"Position globale : {int(joueur.iloc[0]['rang'])} / {df_stats['joueurs'].nunique()}")
    st.write(f"Tournois joués : {int(joueur.iloc[0]['nb de participations'])}")

    df_suisse = charger_feuille(gid=0)
    df_elim = charger_feuille(gid=344099596)

    st.subheader("Mode Suisse")
    if not df_suisse.empty:
        resultats_suisse = chercher_places_suisse(df_suisse, pseudo)
        for place in [1, 2, 3]:
            jeux = resultats_suisse[place]
            if jeux:
                emojis = {1:"🥇", 2:"🥈", 3:"🥉"}
                st.write(f"{emojis[place]} Position {place} à : {', '.join(jeux)}")
        if not any(resultats_suisse.values()):
            st.info("Pas de résultats trouvés en mode suisse.")
    else:
        st.info("Données mode suisse vides.")

    st.subheader("Double élimination")
    if not df_elim.empty:
        resultats_elim = chercher_resultats_double(df_elim, pseudo)
        for nom, jeux in resultats_elim.items():
            if jeux:
                emojis = {"Gagnant":"🏆", "Finaliste":"🎯", "Demi-finaliste":"🏅"}
                st.write(f"{emojis[nom]} {nom} à : {', '.join(jeux)}")
        if not any(resultats_elim.values()):
            st.info("Pas de résultats trouvés en double élimination.")
    else:
        st.info("Données double élimination vides.")

else:
    st.info("Entre un pseudo pour voir les résultats.")
