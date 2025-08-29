import streamlit as st
import pandas as pd
import unicodedata
import re

PROGRAM_NAME = "Statistiques des tournois BGA"

# --- Fonctions utilitaires ---
def normaliser_texte(texte):
    """Convertit en minuscules, enlève accents et espaces superflus"""
    if not isinstance(texte, str):
        texte = str(texte)
    texte = texte.strip().lower()
    texte = ''.join(c for c in unicodedata.normalize('NFD', texte) if unicodedata.category(c) != 'Mn')
    return texte

# --- Chargement des données ---
@st.cache_data(ttl=600)
def charger_stats_principales_xlsx(fichier):
    """Charge tous les onglets du fichier Excel et les combine en un DataFrame"""
    try:
        xls = pd.ExcelFile(fichier)
        dfs = [pd.read_excel(xls, sheet_name=nom) for nom in xls.sheet_names]
        df = pd.concat(dfs, ignore_index=True)
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Erreur chargement stats principales: {e}")
        return None

# --- Mode Suisse avec ex aequo ---
def chercher_places_suisse(df, pseudo):
    places_cols = [col for col in df.columns if re.search(r'\b\d+(er|e|ème|ere)?\b', col, re.IGNORECASE)]
    resultats = {}
    pseudo_norm = normaliser_texte(pseudo)
    for idx, col in enumerate(places_cols, 1):
        jeux = []
        for i, cell in df[col].dropna().items():
            joueurs = [normaliser_texte(j) for j in str(cell).split('/')]
            if pseudo_norm in joueurs and "jeu" in df.columns:
                jeux.append(df.at[i, "jeu"])
        resultats[idx] = jeux
    return resultats

# --- Double élimination ---
def chercher_resultats_double(df, pseudo):
    colonnes = {
        "gagnant": "Gagnant",
        "finaliste": "Finaliste",
        "semi": "Demi-finaliste",
        "quart": "Quart-finaliste"
    }
    resultats = {v: [] for v in colonnes.values()}
    pseudo_norm = normaliser_texte(pseudo)
    for col, nom_resultat in colonnes.items():
        cols_match = [c for c in df.columns if col in c.lower()]
        for c in cols_match:
            mask = df[c].apply(lambda x: pseudo_norm in [normaliser_texte(p) for p in str(x).split('/')])
            if "jeu" in df.columns:
                resultats[nom_resultat].extend(df.loc[mask, "jeu"].tolist())
    return resultats

# --- Nombre total de participations ---
def compter_participations(df, pseudo):
    pseudo_norm = normaliser_texte(pseudo)
    total = 0
    for col in df.columns:
        if re.search(r'\b\d+(er|e|ème|ere)?\b', col, re.IGNORECASE):
            for cell in df[col].dropna():
                joueurs = [normaliser_texte(j) for j in str(cell).split('/')]
                if pseudo_norm in joueurs:
                    total += 1
    return total

# --- Classement global basé sur l'onglet final, colonne 'joueurs' ---
def classement_global(df_final):
    df_final = df_final.dropna(subset=["joueurs"])
    pseudos = set()
    for cell in df_final["joueurs"]:
        for j in str(cell).split('/'):
            pseudos.add(normaliser_texte(j))
    df_global = pd.DataFrame(list(pseudos), columns=["pseudo"])
    df_global = df_global.sort_values("pseudo").reset_index(drop=True)
    df_global["rang"] = df_global.index + 1
    return df_global

# --- Interface Streamlit ---
st.title(PROGRAM_NAME)

with st.expander("🔧 Admin"):
    if st.button("🔁 Recharger les données (vider le cache)"):
        st.cache_data.clear()
        st.success("Cache vidé. Rechargement...")
        st.experimental_rerun()

pseudo = st.text_input("Entre ton pseudo").strip()

if pseudo:
    df_stats = charger_stats_principales_xlsx("data/BGA.xlsx")
    if df_stats is None:
        st.error("Impossible de charger les statistiques principales.")
        st.stop()

    st.subheader("Recherche dans les tournois (Mode Suisse et Élimination)")

    # Résultats suisses
    resultats_suisse = chercher_places_suisse(df_stats, pseudo)
    total_participations = compter_participations(df_stats, pseudo)
    if total_participations == 0:
        st.warning("Pseudo non trouvé dans les résultats.")
        st.stop()

    st.write(f"Tournois joués : {total_participations}")

    # Classement global (onglet final)
    df_global = classement_global(df_stats)  # assure-toi que df_stats contient l'onglet final avec 'joueurs'
    ligne_joueur = df_global[df_global["pseudo"] == normaliser_texte(pseudo)]
    if not ligne_joueur.empty:
        ton_rang = int(ligne_joueur.iloc[0]["rang"])
        nb_joueurs = df_global.shape[0]
        st.success(f"Tu es {ton_rang}e sur {nb_joueurs} joueurs au classement")

    # Mode Suisse
    st.subheader("Mode Suisse")
    emojis_suisse = {1:"🥇", 2:"🥈", 3:"🥉", 4:"4️⃣", 5:"5️⃣", 6:"6️⃣", 7:"7️⃣", 8:"8️⃣"}
    positions_texte_suisse = {
        1: "1ère position", 2: "2e position", 3: "3e position", 4: "4e position",
        5: "5e position", 6: "6e position", 7: "7e position", 8: "8e position"
    }
    for place in range(1, 9):
        jeux = resultats_suisse.get(place, [])
        if jeux:
            st.write(f"{emojis_suisse.get(place, '')} {positions_texte_suisse.get(place, str(place)+'e')} à : {', '.join(jeux)}")
    if not any(resultats_suisse.values()):
        st.info("Pas de résultats trouvés en mode suisse.")

    # Double élimination
    st.subheader("Double élimination")
    resultats_elim = chercher_resultats_double(df_stats, pseudo)
    emojis_elim = {"Gagnant":"🏆", "Finaliste":"🎯", "Demi-finaliste":"🏅", "Quart-finaliste":"🔶"}
    for nom, jeux in resultats_elim.items():
        if jeux:
            st.write(f"{emojis_elim.get(nom, '')} {nom} à : {', '.join(jeux)}")
    if not any(resultats_elim.values()):
        st.info("Pas de résultats trouvés en double élimination.")
else:
    st.info("Entre un pseudo pour voir les résultats.")
