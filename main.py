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
        return df
    except Exception as e:
        st.error(f"Erreur chargement feuille gid={gid}: {e}")
        return pd.DataFrame()

def chercher_places_suisse(df, pseudo):
    places = ["1er", "2e", "3e", "4e", "5e", "6e", "7e", "8e"]
    resultats = {i: [] for i in range(1, 9)}
    pseudo = pseudo.lower()
    for idx, col in enumerate(places, 1):
        if col in df.columns:
            mask = df[col].apply(lambda x: pseudo in [p.strip().lower() for p in str(x).split('/')])
            jeux = df.loc[mask, "jeu"].tolist()
            resultats[idx].extend(jeux)
    return resultats

def chercher_resultats_double(df, pseudo):
    colonnes = {
        "gagnant(e)": "Gagnant",
        "finaliste(s)": "Finaliste",
        "semi-finaliste(s)": "Demi-finaliste",
        "quart-finaliste(s)": "Quart-finaliste"
    }
    resultats = {v: [] for v in colonnes.values()}
    pseudo = pseudo.lower()
    for col, nom_resultat in colonnes.items():
        if col in df.columns:
            mask = df[col].apply(lambda x: pseudo in [p.strip().lower() for p in str(x).split('/')])
            jeux = df.loc[mask, "jeu"].tolist()
            resultats[nom_resultat].extend(jeux)
    return resultats

st.title(PROGRAM_NAME)

with st.expander("🔧 Admin"):
    if st.button("🔁 Recharger les données (vider le cache)"):
        st.cache_data.clear()
        st.success("Cache vidé. Rechargement...")
        st.experimental_rerun()

pseudo = st.text_input("Entre ton pseudo").strip().lower()

if pseudo:
    df_stats = charger_stats_principales()
    if df_stats is None:
        st.error("Impossible de charger les statistiques principales.")
        st.stop()

    st.subheader("Recherche dans les tournois (Mode Suisse et Élimination)")

    resultats_suisse = chercher_places_suisse(df_stats, pseudo)
    total_participations = sum(len(jeux) for jeux in resultats_suisse.values())

    if total_participations == 0:
        st.warning("Pseudo non trouvé dans les résultats.")
        st.stop()

    st.write(f"Tournois joués : {total_participations}")

    df_suisse = charger_feuille(gid=0)
    df_elim = charger_feuille(gid=344099596)

    st.subheader("Mode Suisse")
    if not df_suisse.empty:
        resultats_suisse = chercher_places_suisse(df_suisse, pseudo)
        emojis_suisse = {
            1:"🥇", 2:"🥈", 3:"🥉",
            4:"4️⃣", 5:"5️⃣", 6:"6️⃣",
            7:"7️⃣", 8:"8️⃣"
        }
        positions_texte_suisse = {
            1: "1ère position",
            2: "2e position",
            3: "3e position",
            4: "4e position",
            5: "5e position",
            6: "6e position",
            7: "7e position",
            8: "8e position"
        }
        for place in range(1, 9):
            jeux = resultats_suisse[place]
            if jeux:
                st.write(f"{emojis_suisse[place]} {positions_texte_suisse[place]} à : {', '.join(jeux)}")
        if not any(resultats_suisse.values()):
            st.info("Pas de résultats trouvés en mode suisse.")
    else:
        st.info("Données mode suisse vides.")

    st.subheader("Double élimination")
    if not df_elim.empty:
        resultats_elim = chercher_resultats_double(df_elim, pseudo)
        emojis_elim = {
            "Gagnant":"🏆",
            "Finaliste":"🎯",
            "Demi-finaliste":"🏅",
            "Quart-finaliste":"🔶"
        }
        for nom, jeux in resultats_elim.items():
            if jeux:
                st.write(f"{emojis_elim[nom]} {nom} à : {', '.join(jeux)}")
        if not any(resultats_elim.values()):
            st.info("Pas de résultats trouvés en double élimination.")
    else:
        st.info("Données double élimination vides.")

else:
    st.info("Entre un pseudo pour voir les résultats.")
