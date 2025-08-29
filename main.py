import streamlit as st
import pandas as pd

PROGRAM_NAME = "Statistiques des tournois BGA"

# Vérification openpyxl
try:
    import openpyxl
except ImportError:
    st.error("❌ openpyxl n'est pas installé")

# Charger les stats principales
@st.cache_data(ttl=600)
def charger_stats_principales():
    try:
        df = pd.read_excel("data/BGA.xlsx")
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Erreur chargement stats principales: {e}")
        return None

# Cherche les places en mode Suisse
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

# Cherche les résultats en double élimination
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

# Calcul du classement global
def classement_global(df):
    pseudo_counts = {}
    for col in df.columns:
        if col != "jeu":
            for val in df[col].dropna():
                joueurs = [p.strip().lower() for p in str(val).split('/')]
                for j in joueurs:
                    pseudo_counts[j] = pseudo_counts.get(j, 0) + 1
    # Tri par nombre de participations décroissant
    sorted_counts = sorted(pseudo_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_counts

# Streamlit UI
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

    # Mode Suisse
    st.subheader("Mode Suisse")
    resultats_suisse = chercher_places_suisse(df_stats, pseudo)
    emojis_suisse = {1:"🥇", 2:"🥈", 3:"🥉", 4:"4️⃣", 5:"5️⃣", 6:"6️⃣", 7:"7️⃣", 8:"8️⃣"}
    positions_texte_suisse = {1: "1ère position", 2: "2e position", 3: "3e position",
                              4: "4e position", 5: "5e position", 6: "6e position",
                              7: "7e position", 8: "8e position"}
    total_participations = sum(len(j) for j in resultats_suisse.values())
    if total_participations == 0:
        st.warning("Pseudo non trouvé dans les résultats.")
        st.stop()

    for place in range(1, 9):
        jeux = resultats_suisse[place]
        if jeux:
            st.write(f"{emojis_suisse[place]} {positions_texte_suisse[place]} à : {', '.join(jeux)}")

    # Double élimination
    st.subheader("Double élimination")
    resultats_elim = chercher_resultats_double(df_stats, pseudo)
    emojis_elim = {"Gagnant":"🏆", "Finaliste":"🎯", "Demi-finaliste":"🏅", "Quart-finaliste":"🔶"}
    for nom, jeux in resultats_elim.items():
        if jeux:
            st.write(f"{emojis_elim[nom]} {nom} à : {', '.join(jeux)}")

    # Classement global
    st.subheader("Classement global des participations")
    classement = classement_global(df_stats)
    total_joueurs = len(classement)
    rang = next((i+1 for i,(j,_) in enumerate(classement) if j == pseudo), None)
    if rang:
        st.write(f"Tu es {rang}ᵉ sur {total_joueurs} joueurs au classement.")
else:
    st.info("Entre un pseudo pour voir les résultats.")
