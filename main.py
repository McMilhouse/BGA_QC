import streamlit as st
import pandas as pd
import time
import unicodedata

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

# --- Recherche Mode Suisse ---
def chercher_places_suisse(df, pseudo):
    places = [col for col in df.columns if col.lower().startswith(('1er','2e','3e','4e','5e','6e','7e','8e'))]
    resultats = {i: [] for i in range(1, 9)}
    pseudo_norm = normaliser_texte(pseudo)
    for idx, col in enumerate(places, 1):
        mask = df[col].apply(lambda x: pseudo_norm in [normaliser_texte(p) for p in str(x).split('/')])
        if "jeu" in df.columns:
            resultats[idx].extend(df.loc[mask, "jeu"].tolist())
    return resultats

# --- Recherche Double élimination ---
def chercher_resultats_double(df, pseudo):
    colonnes = {
        "gagnant(e)": "Gagnant",
        "finaliste(s)": "Finaliste",
        "semi-finaliste(s)": "Demi-finaliste",
        "quart-finaliste(s)": "Quart-finaliste"
    }
    resultats = {v: [] for v in colonnes.values()}
    pseudo_norm = normaliser_texte(pseudo)
    for col, nom_resultat in colonnes.items():
        if col in df.columns:
            mask = df[col].apply(lambda x: pseudo_norm in [normaliser_texte(p) for p in str(x).split('/')])
            if "jeu" in df.columns:
                resultats[nom_resultat].extend(df.loc[mask, "jeu"].tolist())
    return resultats

# --- Classement global ---
def classement_global(df):
    colonnes_positions = [col for col in df.columns if col.endswith("e") or col.endswith("er")]
    participations = {}
    for col in colonnes_positions:
        if col in df.columns:
            for joueurs in df[col].dropna():
                for j in str(joueurs).split('/'):
                    j_norm = normaliser_texte(j)
                    if j_norm:
                        participations[j_norm] = participations.get(j_norm, 0) + 1
    df_participations = pd.DataFrame(list(participations.items()), columns=["pseudo", "participations"])
    df_participations = df_participations.sort_values("participations", ascending=False).reset_index(drop=True)
    df_participations["rang"] = df_participations["participations"].rank(method="min", ascending=False).astype(int)
    return df_participations

# --- Interface Streamlit ---
st.title(PROGRAM_NAME)

with st.expander("🔧 Admin"):
    if st.button("🔁 Recharger les données (vider le cache)"):
        st.cache_data.clear()
        st.success("Cache vidé. Rechargement...")
        st.experimental_rerun()

# --- Upload du fichier Excel ---
uploaded_file = st.file_uploader("📥 Téléverse ton fichier BGA (.xlsx)", type=["xlsx"])

if uploaded_file:
    pseudo = st.text_input("Entre ton pseudo").strip()

    if pseudo:
        df_stats = charger_stats_principales_xlsx(uploaded_file)
        if df_stats is None:
            st.error("Impossible de charger les statistiques principales.")
            st.stop()

        st.subheader("Recherche dans les tournois (Mode Suisse et Élimination)")

        # Résultats suisses
        resultats_suisse = chercher_places_suisse(df_stats, pseudo)
        total_participations = sum(len(jeux) for jeux in resultats_suisse.values())
        if total_participations == 0:
            st.warning("Pseudo non trouvé dans les résultats.")
            st.stop()

        st.write(f"Tournois joués : {total_participations}")

        # Classement global
        df_global = classement_global(df_stats)
        ligne_joueur = df_global[df_global["pseudo"] == normaliser_texte(pseudo)]
        if not ligne_joueur.empty:
            ton_rang = int(ligne_joueur.iloc[0]["rang"])
            nb_joueurs = df_global.shape[0]
            st.success(f"🎖️ Tu es **{ton_rang}ᵉ sur {nb_joueurs} joueurs** au classement général des participations")

        # Mode Suisse
        st.subheader("Mode Suisse")
        emojis_suisse = {1:"🥇", 2:"🥈", 3:"🥉", 4:"4️⃣", 5:"5️⃣", 6:"6️⃣", 7:"7️⃣", 8:"8️⃣"}
        positions_texte_suisse = {
            1: "1ère position", 2: "2e position", 3: "3e position", 4: "4e position",
            5: "5e position", 6: "6e position", 7: "7e position", 8: "8e position"
        }
        for place in range(1, 9):
            jeux = resultats_suisse[place]
            if jeux:
                st.write(f"{emojis_suisse[place]} {positions_texte_suisse[place]} à : {', '.join(jeux)}")
        if not any(resultats_suisse.values()):
            st.info("Pas de résultats trouvés en mode suisse.")

        # Double élimination
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
else:
    st.info("Téléverse ton fichier Excel pour commencer.")
