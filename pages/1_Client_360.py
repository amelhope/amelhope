import streamlit as st
import pandas as pd

st.set_page_config(page_title="Client 360° - LANALA", layout="wide")
st.title("Fiche Client 360°")

clients = pd.read_csv("clients_avec_segments.csv", encoding="utf-8-sig")
recommandations = pd.read_csv("recommandations.csv", encoding="utf-8-sig")

NOMS_PRODUITS = {
    "deposit": "Compte de Dépôt",
    "saving": "Compte d'Épargne",
    "linkedsaving": "Épargne Liée",
}

client_id = st.number_input("Entrer un identifiant client (client_id)", min_value=1, step=1)

if st.button("Rechercher"):
    ligne = clients[clients["client_id"] == client_id]
    if ligne.empty:
        st.error(f"Client {client_id} introuvable.")
    else:
        c = ligne.iloc[0]
        st.divider()
        st.subheader(f"Client #{client_id}")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Segment", c["segment"])
        col2.metric("Âge", int(c["age"]))
        col3.metric("Statut civil", c["civilstatus_"])
        col4.metric("Revenu mensuel", f"{c['revenu_mensuel']:.0f}")

        st.divider()
        st.subheader("Produits actuellement détenus")
        p1, p2, p3 = st.columns(3)
        p1.write(("✅" if c["nb_deposit"] > 0 else "❌") + " Compte de Dépôt")
        p2.write(("✅" if c["nb_saving"] > 0 else "❌") + " Compte d'Épargne")
        p3.write(("✅" if c["nb_linkedsaving"] > 0 else "❌") + " Épargne Liée")

        st.divider()
        st.subheader("💼 Opportunité commerciale")

        reco = recommandations[recommandations["client_id"] == client_id]

        # Cas 1 : le client possède déjà les 3 produits — recommandations.csv
        # ne contient tout simplement pas de ligne pour lui.
        if reco.empty:
            st.info("Ce client possède déjà les 3 produits disponibles — aucune recommandation possible.")
        else:
            r = reco.iloc[0]
            categorie = r["categorie_lift"]
            produit = r["produit_recommande"]
            nom_produit = NOMS_PRODUITS.get(produit, produit)
            lift = r["lift_eligible"]

            # Cas 2 : un produit manquant existe, mais son lift éligible est
            # défavorable — on ne le présente PAS comme une opportunité.
            if categorie == "Defavorable (<0.8)":
                st.info(
                    "Aucune opportunité forte identifiée pour ce client. "
                    "Le produit manquant est moins fréquent chez les clients "
                    "similaires que chez les autres clients qui en sont aussi dépourvus."
                )
            else:
                # Cas 3 : opportunité neutre ou favorable — on l'affiche.
                col_a, col_b = st.columns([2, 1])
                with col_a:
                    st.success(f"**Produit à proposer : {nom_produit}**")
                    st.caption(
                        f"Ce client appartient au segment {c['segment']}. "
                        f"Parmi ses clients les plus similaires, {round(r['score_confiance'] * 100)}% "
                        f"possèdent déjà ce produit — contre {round(r['baseline_eligible'] * 100)}% chez les "
                        f"autres clients qui en sont eux aussi dépourvus."
                    )
                with col_b:
                    st.metric("Probabilité relative", f"×{lift:.1f}", help="Par rapport aux autres clients éligibles à ce produit")

                if categorie == "Favorable (>1.3)":
                    st.caption("🟢 Opportunité forte")
                else:
                    st.caption("🟡 Signal neutre")