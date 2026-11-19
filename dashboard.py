import streamlit as st
import pandas as pd

st.set_page_config(page_title="Moteur de recommandation LANALA", layout="wide")
st.title("Moteur de recommandation LANALA")

# --- Chargement des données ---
clients = pd.read_csv("clients_avec_segments.csv", encoding="utf-8-sig")
recommandations = pd.read_csv("recommandations.csv", encoding="utf-8-sig")

# Seules les recommandations "Neutre" ou "Favorable" sont réellement
# affichées comme une opportunité dans la fiche Client 360° — les
# "Défavorable" sont masquées (message "aucune opportunité forte").
# Les indicateurs du dashboard doivent refléter la même règle, sinon
# la page d'accueil et la fiche client racontent deux histoires
# différentes.
opportunites_reelles = recommandations[
    recommandations["categorie_lift"].isin(["Neutre (0.8-1.3)", "Favorable (>1.3)"])
]

# --- Indicateurs clés en haut ---
col1, col2, col3 = st.columns(3)
col1.metric("Nombre de clients", len(clients))
col2.metric("Opportunités identifiées", len(opportunites_reelles),
            help="Clients avec un produit manquant dont le lift est ≥ 0.8 (Neutre ou Favorable)")
col3.metric("Probabilité relative moyenne", f"×{opportunites_reelles['lift_eligible'].mean():.1f}",
            help="Lift moyen des opportunités affichées, par rapport aux autres clients éligibles à ce produit")

clients_avec_tous = len(clients) - len(recommandations)
clients_sans_signal = len(recommandations) - len(opportunites_reelles)

st.caption(
    f"Sur {len(clients)} clients : {clients_avec_tous} possèdent déjà les 3 produits, "
    f"{clients_sans_signal} ont un produit manquant mais sans signal suffisant, "
    f"et {len(opportunites_reelles)} présentent une vraie opportunité commerciale."
)

st.divider()

# --- Répartition des segments ---
st.subheader("Répartition des segments")
repartition = clients["segment"].value_counts()
st.bar_chart(repartition)

# --- Répartition par catégorie de lift ---
st.subheader("Qualité des recommandations (catégorie de lift)")
repartition_lift = recommandations["categorie_lift"].value_counts()
st.bar_chart(repartition_lift)

# --- Produits recommandés (uniquement les vraies opportunités) ---
st.subheader("Produits recommandés (opportunités réelles uniquement)")
produits = opportunites_reelles["produit_recommande"].value_counts()
st.bar_chart(produits)

# --- Produits actuellement détenus par les clients ---
st.subheader("Produits les plus détenus par les clients")
produits_detenus = pd.Series({
    "Compte de Dépôt": (clients["nb_deposit"] > 0).sum(),
    "Compte d'Épargne": (clients["nb_saving"] > 0).sum(),
    "Épargne Liée": (clients["nb_linkedsaving"] > 0).sum(),
}).sort_values(ascending=False)
st.bar_chart(produits_detenus)