import streamlit as st
import pandas as pd
import time

PROGRAM_NAME = "Statistiques des tournois BGA"

# --- Fonctions de chargement ---
@st.cache_data(ttl=600)
def charger_stats_principales():
    try:
        df = pd.read_excel("data/BGA.xlsx")
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Erreur chargement stats principales: {e}")
        return None

def chercher_places_suisse(df, pseudo):
    places = ["1er", "2e", "3e", "4e", "5e", "6e", "7e", "8e"]
    resultats = {i: [] for i in range(1, 9)}
    pseudo = pseudo.strip().lower()
    for idx, col in enumerate(places, 1):
        if col in df.columns:
            mask = df[col].apply(lambda x: pseudo in [p.strip().lower() for p in str(x).replace(';','/').replace(',','/').split('/')])
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
    pseudo = pseudo.strip().lower()
    for col, nom_resultat in colonnes.items():
        if col in df.columns:
            def match(x):
                noms = str(x).replace(';','/').replace(',','/').split('/')
                noms = [p.strip().lower() for p in noms]
                return pseudo in noms
            mask = df[col].apply(match)
            jeux = df.loc[mask, "jeu"].tolist()
            resultats[nom_resultat].extend(jeux)
    return resultats

# --- Interface Streamlit ---
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

    # --- Classement général des participations en premier ---
    st.subheader("Classement global des participations")
    colonnes_places = ['1er','2e','3e','4e','5e','6e','7e','8e']
    tous_les_joueurs = pd.Series(
        df_stats[colonnes_places].stack()
        .dropna()
        .apply(lambda x: [p.strip().lower() for p in str(x).replace(';','/').replace(',','/').split('/')])
        .sum()
    )
    joueurs_uniques = tous_les_joueurs.unique()
    total_joueurs = len(joueurs_uniques)
    joueurs_counts = tous_les_joueurs.value_counts()
    if pseudo in joueurs_counts:
        rank = joueurs_counts.rank(ascending=False, method='min')[pseudo]
        st.write(f"Tu es {int(rank)}e sur {total_joueurs} joueurs au classement.")
    else:
        st.info("Pseudo non trouvé dans les participations.")

    # --- Mode Suisse ---
    st.subheader("Mode Suisse")
    resultats_suisse = chercher_places_suisse(df_stats, pseudo)
    emojis_suisse = {1:"🥇", 2:"🥈", 3:"🥉", 4:"4️⃣", 5:"5️⃣", 6:"6️⃣", 7:"7️⃣", 8:"8️⃣"}
    positions_texte_suisse = {1: "1ère position", 2: "2e position", 3: "3e position", 4: "4e position",
                              5: "5e position", 6: "6e position", 7: "7e position", 8: "8e position"}
    for place in range(1, 9):
        jeux = resultats_suisse[place]
        if jeux:
            st.write(f"{emojis_suisse[place]} {positions_texte_suisse[place]} à : {', '.join(jeux)}")
    if not any(resultats_suisse.values()):
        st.info("Pas de résultats trouvés en mode suisse.")

    # --- Double élimination ---
    st.subheader("Double élimination")
    resultats_elim = chercher_resultats_double(df_stats, pseudo)
    emojis_elim = {"Gagnant":"🏆", "Finaliste":"🎯", "Demi-finaliste":"🏅", "Quart-finaliste":"🔶"}
    for nom, jeux in resultats_elim.items():
        if jeux:
            st.write(f"{emojis_elim[nom]} {nom} à : {', '.join(jeux)}")
    if not any(resultats_elim.values()):
        st.info("Pas de résultats trouvés en double élimination.")

else:
    st.info("Entre un pseudo pour voir les résultats.")
