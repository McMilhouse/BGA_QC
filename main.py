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
        return df
    except Exception as e:
        st.error(f"Erreur chargement feuille gid={gid}: {e}")
        return pd.DataFrame()

def chercher_places_suisse(df, pseudo):
    places = {"1er": 1, "2e": 2, "3e": 3}
    resultats = {1: [], 2: [], 3: []}
    for col, place in places.items():
        mask = df[col].str.lower() == pseudo
        jeux = df.loc[mask, "jeu"].tolist()
        resultats[place].extend(jeux)
    return resultats

def chercher_resultats_double(df, pseudo):
    colonnes = {"gagnant(e)": "Gagnant", "finaliste(s)": "Finaliste", "semi-finaliste(s)": "Demi-finaliste"}
    resultats = {v: [] for v in colonnes.values()}
    for col, nom_resultat in colonnes.items():
        mask = df[col].str.lower() == pseudo
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

def verifier_presence_pseudo(df, pseudo, colonnes):
    pseudo = pseudo.lower()
    lignes_trouvees = []
    for col in colonnes:
        if col in df.columns:
            # Cherche les lignes où la colonne contient le pseudo (insensible à la casse)
            mask = df[col].astype(str).str.lower().str.contains(pseudo)
            df_filtree = df.loc[mask, ["jeu", col]]
            if not df_filtree.empty:
                for _, row in df_filtree.iterrows():
                    lignes_trouvees.append((col, row["jeu"], row[col]))
    return lignes_trouvees

if pseudo:
    st.subheader("Vérification de la présence du pseudo dans les colonnes clés")

    df_suisse = charger_feuille(gid=0)
    colonnes_suisse = ["1er", "2e", "3e"]

    resultats_suisse = verifier_presence_pseudo(df_suisse, pseudo, colonnes_suisse)
    if resultats_suisse:
        st.write("Pseudo trouvé dans mode Suisse :")
        for col, jeu, val in resultats_suisse:
            st.write(f"- Colonne **{col}**, Jeu : {jeu}, Valeur trouvée : {val}")
    else:
        st.write("Pseudo non trouvé dans mode Suisse dans les colonnes 1er, 2e, 3e.")

    df_elim = charger_feuille(gid=344099596)
    colonnes_elim = ["gagnant(e)", "finaliste(s)", "semi-finaliste(s)"]

    resultats_elim = verifier_presence_pseudo(df_elim, pseudo, colonnes_elim)
    if resultats_elim:
        st.write("Pseudo trouvé dans mode Double élimination :")
        for col, jeu, val in resultats_elim:
            st.write(f"- Colonne **{col}**, Jeu : {jeu}, Valeur trouvée : {val}")
    else:
        st.write("Pseudo non trouvé dans mode Double élimination dans les colonnes gagnant(e), finaliste(s), demi-finaliste(s).")


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
