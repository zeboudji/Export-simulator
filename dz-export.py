import streamlit as st

# Titre de l'application
st.title("Simulateur d'Importation de Véhicules en Algérie")

# Introduction
st.markdown("""
Bienvenue sur le simulateur d'importation de véhicules en Algérie. Ce simulateur vous aidera à estimer les coûts associés à l'importation de votre véhicule, en fonction des réglementations en vigueur.
""")

# Sidebar pour la navigation
st.sidebar.header("Informations sur l'Importateur")

# 1. Statut de l'Importateur
importer_status = st.sidebar.selectbox(
    "Sélectionnez votre statut",
    ("Particulier Résident", "Particulier Non-Résident (Binational)")
)

# 2. Informations sur le Véhicule
st.header("Informations sur le Véhicule")

age = st.number_input("Âge du véhicule (en années)", min_value=0, max_value=30, value=1)
carburant = st.selectbox("Type de carburant", ("Essence", "Diesel"))
cylindree = st.number_input("Cylindrée (en cm³)", min_value=0, max_value=5000, value=1800)
etat = st.selectbox("État de conformité", ("Bon état de marche", "Défaut mineur", "Défaut majeur"))

# 3. Calcul des Taxes et Coûts
st.header("Estimation des Coûts et Taxes")

# Fonction pour vérifier l'éligibilité
def verifier_eligibilite(age, carburant, cylindree, etat, importer_status):
    eligibilite = True
    raisons = []

    # Vérification de l'âge du véhicule
    if importer_status == "Particulier Résident":
        if age > 3:
            eligibilite = False
            raisons.append("Le véhicule doit avoir moins de 3 ans pour les particuliers résidents.")
    elif importer_status == "Particulier Non-Résident (Binational)":
        pass  # Conditions spécifiques à ajouter si nécessaire

    # Vérification du carburant et des normes
    if carburant == "Diesel":
        if cylindree > 2000:
            eligibilite = False
            raisons.append("La cylindrée maximale pour les moteurs diesel est de 2000 cm³.")
    elif carburant == "Essence":
        if cylindree > 1800:
            eligibilite = False
            raisons.append("La cylindrée maximale pour les moteurs à essence est de 1800 cm³.")

    # Vérification de l'état de conformité
    if etat != "Bon état de marche":
        eligibilite = False
        raisons.append("Le véhicule doit être en bon état de marche, sans défaut majeur ou critique.")

    return eligibilite, raisons

# Vérification de l'éligibilité
eligible, raisons = verifier_eligibilite(age, carburant, cylindree, etat, importer_status)

if eligible:
    st.success("Le véhicule est éligible à l'importation.")
else:
    st.error("Le véhicule n'est pas éligible à l'importation pour les raisons suivantes :")
    for raison in raisons:
        st.write(f"- {raison}")

# Calcul des droits de douane
def calcul_droits_douane(carburant, cylindree):
    if carburant == "Essence":
        if cylindree <= 1800:
            taux = 15
        else:
            taux = 25
    elif carburant == "Diesel":
        if cylindree <= 2000:
            taux = 20
        else:
            taux = 30
    return taux

droits_douane_taux = calcul_droits_douane(carburant, cylindree)

# Calcul de la TVA
TVA_TAUX = 19

# Calcul de la TIC
def calcul_TIC(carburant, cylindree):
    if carburant == "Diesel" and 2000 < cylindree <= 3000:
        return 60
    else:
        return 0

TIC_TAUX = calcul_TIC(carburant, cylindree)

# Estimation des frais annexes
frais_annexes = 50000  # Exemple fixe en DZD, à ajuster selon les besoins

# Saisie du prix du véhicule en DZD
prix_vehicule = st.number_input("Prix du véhicule (en DZD)", min_value=0, value=1000000)

# Calcul des droits de douane
droits_douane = (droits_douane_taux / 100) * prix_vehicule

# Calcul de la TVA
TVA = (TVA_TAUX / 100) * (prix_vehicule + droits_douane)

# Calcul de la TIC
TIC = (TIC_TAUX / 100) * prix_vehicule

# Calcul total
total = prix_vehicule + droits_douane + TVA + TIC + frais_annexes

# Affichage des résultats
st.subheader("Résumé des Coûts et Taxes")
st.write(f"Droits de Douane ({droits_douane_taux}%): {droits_douane:,.2f} DZD")
st.write(f"TVA (19%): {TVA:,.2f} DZD")
st.write(f"TIC ({TIC_TAUX}%): {TIC:,.2f} DZD")
st.write(f"Frais Annexes: {frais_annexes:,.2f} DZD")
st.write(f"**Total Estimé: {total:,.2f} DZD**")

# 4. Documents Requis
st.header("Documents Requis pour le Dédouanement")
st.markdown("""
1. **Copie de la pièce d'identité** ou carte de résident.
2. **Certificat de résidence**.
3. **Certificat d'immatriculation** du véhicule à l'étranger.
4. **Facture d'achat** ou contrat de vente.
5. **Document attestant le bon état de marche** du véhicule (datant de moins de trois mois).
6. **Rapport d'expertise de conformité** établi par un expert agréé.
""")

# 5. Restrictions Supplémentaires
st.header("Restrictions Supplémentaires")

st.markdown("""
- **Durée d'Incessibilité** : Le véhicule importé ne peut être cédé avant une période de trois ans suivant son importation.
- **Normes Environnementales** : Les véhicules doivent respecter les normes d'émissions en vigueur en Algérie.
""")

# 6. Téléchargement du Rapport (Optionnel)
st.header("Télécharger le Rapport d'Estimation")

if st.button("Télécharger le Rapport"):
    import pandas as pd
    from io import BytesIO

    # Création du rapport
    rapport = {
        "Droits de Douane (%)": droits_douane_taux,
        "Droits de Douane (DZD)": droits_douane,
        "TVA (%)": TVA_TAUX,
        "TVA (DZD)": TVA,
        "TIC (%)": TIC_TAUX,
        "TIC (DZD)": TIC,
        "Frais Annexes (DZD)": frais_annexes,
        "Total Estimé (DZD)": total
    }

    df = pd.DataFrame([rapport])

    # Convertir en Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Rapport')
    data = output.getvalue()

    st.download_button(
        label="Télécharger le Rapport",
        data=data,
        file_name='rapport_importation.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
