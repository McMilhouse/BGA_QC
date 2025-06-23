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
        st.write(f"Colonnes chargées pour gid={gid} :", df.columns.tolist())
        st.write(df.head())
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

    if "joueurs" not in df_stats.columns:
        st.error("Colonne 'joueurs' manquante dans stats principales.")
        st.stop()

    joueur = df_stats[df_stats["joueurs"].str.lower() == pseudo]
    if joueur.empty:
        st.warning("Pseudo non trouvé.")
        st.stop()

    st.subheader("Résumé général")
    st.write(f"Points total : {int(joueur.iloc[0]['total de points'])}")
    st.write(f"Position globale : {int(joueur.iloc[0]['rang'])} / {df_stats['joueurs'].nunique()}")
    st.write(f"Tournois joués : {int(joueur.iloc[0]['nb de participations'])}")

    # Charger feuilles Google Sheets
    df_suisse = charger_feuille(gid=0)
    df_elim = charger_feuille(gid=344099596)

    # Vérifier présence colonne 'joueur' dans chaque df
    if "joueur" not in df_suisse.columns:
        st.error("Colonne 'joueur' manquante dans mode suisse.")
    else:
        df_suisse_joueur = df_suisse[df_suisse["joueur"].str.lower() == pseudo]
        st.subheader("Mode Suisse")
        if not df_suisse_joueur.empty:
            for place in [1, 2, 3]:
                jeux = df_suisse_joueur[df_suisse_joueur["position"] == place]["jeu"].tolist()
                if jeux:
                    emojis = {1:"🥇", 2:"🥈", 3:"🥉"}
                    st.write(f"{emojis[place]} Position {place} à : {', '.join(jeux)}")
        else:
            st.info("Pas de résultats en mode suisse.")

    if "joueur" not in df_elim.columns:
        st.error("Colonne 'joueur' manquante dans double élimination.")
    else:
        df_elim_joueur = df_elim[df_elim["joueur"].str.lower() == pseudo]
        st.subheader("Double élimination")
        if not df_elim_joueur.empty:
            for res in ["gagnant", "finaliste", "demi-finaliste"]:
                jeux = df_elim_joueur[df_elim_joueur["résultat"].str.lower() == res]["jeu"].tolist()
                if jeux:
                    emojis = {"gagnant":"🏆", "finaliste":"🎯", "demi-finaliste":"🏅"}
                    st.write(f"{emojis[res]} {res.capitalize()} à : {', '.join(jeux)}")
        else:
            st.info("Pas de résultats en double élimination.")
else:
    st.info("Entre un pseudo pour voir les résultats.")
