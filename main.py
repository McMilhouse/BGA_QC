import streamlit as st
import pandas as pd

PROGRAM_NAME = "Statistiques des tournois BGA"

@st.cache_data(ttl=600)
def charger_onglet(sheet_name):
    try:
        df = pd.read_excel("data/BGA.xlsx", sheet_name=sheet_name)
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Erreur chargement onglet {sheet_name}: {e}")
        return None

def normaliser_joueurs(cell):
    if pd.isna(cell):
        return []
    noms = str(cell).replace(';','/').replace(',','/').split('/')
    return [p.strip().lower() for p in noms]

def chercher_places_suisse(df, pseudo):
    places = ["1er", "2e", "3e", "4e", "5e", "6e", "7e", "8e"]
    resultats = {i: [] for i in range(1, 9)}
    pseudo_lower = pseudo.lower()
    for idx, col in enumerate(places, 1):
        if col in df.columns:
            mask = df[col].apply(lambda x: pseudo_lower in normaliser_joueurs(x))
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
    pseudo_lower = pseudo.lower()
    for col, nom_resultat in colonnes.items():
        if col in df.columns:
            mask = df[col].apply(lambda x: pseudo_lower in normaliser_joueurs(x))
            jeux = df.loc[mask, "jeu"].tolist()
            resultats[nom_resultat].extend(jeux)
    return resultats

# --- Interface ---
st.title(PROGRAM_NAME)

with st.expander("🔧 Admin"):
    if st.button("🔁 Recharger les données (vider le cache)"):
        st.cache_data.clear()
        st.success("Cache vidé. Rechargement...")
        st.experimental_rerun()

pseudo = st.text_input("Entre ton pseudo").strip().lower()

if pseudo:
    df_suisse = charger_onglet("Suisse")
    df_elim = charger_onglet("Double")
    df_classement = charger_onglet("Classement")

    if df_suisse is None or df_elim is None or df_classement is None:
        st.error("Impossible de charger les données.")
        st.stop()

    # --- Classement global des participations ---
    st.subheader("Classement global des participations")
    tous_joueurs = []
    for cell in df_classement["joueurs"].dropna():
        tous_joueurs.extend(normaliser_joueurs(cell))
    pseudo_lower = pseudo.lower()
    unique_joueurs = list(dict.fromkeys(tous_joueurs))  # ordre + suppression doublons
    total_joueurs = len(unique_joueurs)
    if pseudo_lower in unique_joueurs:
        rank = unique_joueurs.index(pseudo_lower) + 1
        st.write(f"Tu es {rank}e sur {total_joueurs} joueurs au classement.")
    else:
        st.info("Pseudo non trouvé dans le classement global.")

    # --- Mode Suisse ---
    st.subheader("Mode Suisse")
    resultats_suisse = chercher_places_suisse(df_suisse, pseudo)
    emojis_suisse = {1:"🥇", 2:"🥈", 3:"🥉", 4:"4️⃣", 5:"5️⃣", 6:"6️⃣", 7:"7️⃣", 8:"8️⃣"}
    positions_texte_suisse = {1: "1ère position", 2: "2e position", 3: "3e position",
                              4: "4e position", 5: "5e position", 6: "6e position",
                              7: "7e position", 8: "8e position"}
    for place in range(1, 9):
        jeux = resultats_suisse[place]
        if jeux:
            st.write(f"{emojis_suisse[place]} {positions_texte_suisse[place]} à : {', '.join(jeux)}")
    if not any(resultats_suisse.values()):
        st.info("Pas de résultats trouvés en mode suisse.")

    # --- Double élimination ---
    st.subheader("Double élimination")
    resultats_elim = chercher_resultats_double(df_elim, pseudo)
    emojis_elim = {"Gagnant":"🏆", "Finaliste":"🎯", "Demi-finaliste":"🏅", "Quart-finaliste":"🔶"}
    for nom, jeux in resultats_elim.items():
        if jeux:
            st.write(f"{emojis_elim[nom]} {nom} à : {', '.join(jeux)}")
    if not any(resultats_elim.values()):
        st.info("Pas de résultats trouvés en double élimination.")

else:
    st.info("Entre un pseudo pour voir les résultats.")
