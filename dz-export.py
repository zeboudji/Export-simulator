import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# Tentative d'importation de FPDF avec gestion des erreurs
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ModuleNotFoundError:
    FPDF_AVAILABLE = False
    st.error("Le module 'fpdf' n'est pas installé. Veuillez l'installer pour pouvoir générer des rapports PDF.")

# Dictionnaire des textes pour les différentes langues
LANGUAGE = {
    "French": {
        "title": "Simulateur d'Importation de Véhicules en Algérie",
        "introduction": "Bienvenue sur le simulateur d'importation de véhicules en Algérie. Ce simulateur vous aidera à estimer les coûts associés à l'importation de votre véhicule, en fonction des réglementations en vigueur.",
        "sidebar_header": "Informations sur l'Importateur et Conversion de Devises",
        "select_status": "Sélectionnez votre statut",
        "status_options": ("Particulier Résident", "Particulier Non-Résident (Binational)"),
        "conversion_subheader": "Taux de Conversion",
        "conversion_label": "Taux de conversion DZD par EUR",
        "vat_subheader": "Taux de TVA",
        "vat_label": "Taux de TVA en Algérie (%)",
        "vehicle_info_header": "Informations sur le Véhicule",
        "manufacture_date_label": "Date de fabrication du véhicule",
        "fuel_label": "Type de carburant",
        "fuel_options": ("Essence", "Diesel"),
        "cylindree_label": "Cylindrée (en cm³)",
        "etat_label": "État de conformité",
        "etat_options": ("Bon état de marche", "Défaut mineur", "Défaut majeur"),
        "price_input_label": "Prix du véhicule",
        "price_currency_label": "Devise du prix",
        "price_currency_options": ("DZD", "EUR"),
        "price_type_label": "Type de prix",
        "price_type_options": ("HT (Hors Taxe)", "TTC (Toutes Taxes Comprises)"),
        "origin_vat_label": "TVA du pays d'origine incluse ?",
        "origin_vat_options": ("Oui", "Non"),
        "costs_header": "Estimation des Coûts et Taxes",
        "eligibility_success": "Le véhicule est éligible à l'importation.",
        "eligibility_error": "Le véhicule n'est pas éligible à l'importation pour les raisons suivantes :",
        "summary_header": "Résumé des Coûts et Taxes",
        "document_header": "Documents Requis pour le Dédouanement",
        "document_list": """
        1. **Copie de la pièce d'identité** ou carte de résident.
        2. **Certificat de résidence**.
        3. **Certificat d'immatriculation** du véhicule à l'étranger.
        4. **Facture d'achat** ou contrat de vente.
        5. **Document attestant le bon état de marche** du véhicule (datant de moins de trois mois).
        6. **Rapport d'expertise de conformité** établi par un expert agréé.
        """,
        "restrictions_header": "Restrictions Supplémentaires",
        "restrictions_list": """
        - **Durée d'Incessibilité** : Le véhicule importé ne peut être cédé avant une période de trois ans suivant son importation.
        - **Normes Environnementales** : Les véhicules doivent respecter les normes d'émissions en vigueur en Algérie.
        """,
        "download_header": "Télécharger le Rapport d'Estimation",
        "download_button": "Télécharger le Rapport",
        "report_filename": "rapport_importation.pdf",
        "months": [
            "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
        ],
        "select_make_label": "Sélectionnez la marque",
        "select_model_label": "Sélectionnez le modèle",
        "loading_models": "Chargement des modèles...",
        "resale_price_label": "Prix de revente souhaité en Algérie",
        "resale_price_currency_label": "Devise du prix de revente",
        "resale_price_currency_options": ("DZD", "EUR"),
        "benefit_label": "Bénéfice potentiel",
        "desired_profit_label": "Bénéfice minimum souhaité",
        "minimum_resale_price_label": "Prix minimum de revente nécessaire",
        "profit_currency_label": "Devise du bénéfice",
        "price_type_ht": "Hors Taxe (HT)",
        "price_type_ttc": "Toutes Taxes Comprises (TTC)",
        "tax_rate": "19%"  # Taux de TVA par défaut
    },
    "Arabic": {
        # Traductions en arabe...
    }
}

# Fonction pour obtenir les textes en fonction de la langue sélectionnée
def get_text(lang, key):
    return LANGUAGE[lang][key]

# Liste préenregistrée des marques et modèles courants
MAKES_MODELS = {
    # Comme précédemment...
}

# Classe pour générer le PDF
if FPDF_AVAILABLE:
    class PDF(FPDF):
        # Comme précédemment...
        pass

# Sélection de la langue
st.sidebar.header("Language / اللغة")
language = st.sidebar.selectbox("Choose your language / اختر لغتك", ("French", "Arabic"))

# Appliquer la langue sélectionnée
texts = LANGUAGE[language]

# Configuration de la mise en page pour l'arabe (RTL) si nécessaire
if language == "Arabic":
    st.markdown("<style>body {direction: rtl;}</style>", unsafe_allow_html=True)

# Titre de l'application
st.title(texts["title"])

# Introduction
st.markdown(texts["introduction"])

# Sidebar pour la navigation et les paramètres
st.sidebar.header(texts["sidebar_header"])

# 1. Statut de l'Importateur
with st.sidebar:
    importer_status = st.selectbox(
        texts["select_status"],
        texts["status_options"]
    )

    # 2. Taux de Conversion
    st.sidebar.subheader(texts["conversion_subheader"])
    conversion_rate = st.sidebar.number_input(
        texts["conversion_label"],
        min_value=1.0,
        value=150.0,
        step=1.0
    )

    # 3. Taux de TVA (Modifiable)
    st.sidebar.subheader(texts["vat_subheader"])
    vat_rate = st.sidebar.number_input(
        texts["vat_label"],
        min_value=0.0,
        max_value=100.0,
        value=19.0,
        step=0.1
    )

# Utilisation des onglets pour organiser le contenu principal
tabs = st.tabs(["📄 Informations Véhicule", "💰 Coûts & Taxes", "📈 Revente & Bénéfice", "📋 Résumé & Rapport"])

# **Onglet 1 : Informations Véhicule**
with tabs[0]:
    st.header(texts["vehicle_info_header"])
    # Comme précédemment...

    # Prix du Véhicule avec sélection de la devise et HT/TTC
    st.subheader(texts["price_input_label"])
    with st.container():
        col_currency, col_price, col_price_type = st.columns([1, 2, 1])
        with col_currency:
            price_currency = st.selectbox(
                texts["price_currency_label"],
                texts["price_currency_options"],
                key="currency_select"
            )
        with col_price:
            if language == "French":
                if price_currency == "DZD":
                    price = st.number_input("Prix du véhicule (en DZD)", min_value=0, value=1000000, step=10000, key="price_dzd")
                    price_eur = price / conversion_rate if conversion_rate != 0 else 0
                else:
                    price_eur = st.number_input("Prix du véhicule (en EUR)", min_value=0.0, value=10000.0, step=100.0, key="price_eur")
                    price = price_eur * conversion_rate
            else:
                # Version arabe...
                pass

        with col_price_type:
            price_type = st.selectbox(
                texts["price_type_label"],
                texts["price_type_options"],
                key="price_type_select"
            )

    # Nouveau : Demander si la TVA du pays d'origine est incluse
    origin_vat_included = st.radio(
        texts["origin_vat_label"],
        texts["origin_vat_options"],
        index=0  # Par défaut sur 'Oui'
    )

    # Ajuster le prix si la TVA du pays d'origine est récupérable
    # En supposant un taux de TVA standard du pays d'origine de 20%
    origin_vat_rate = 20.0  # À ajuster si nécessaire
    if origin_vat_included == "Oui" and price_type == "TTC (Toutes Taxes Comprises)":
        # Prix sans TVA du pays d'origine
        price_ht_origin = price / (1 + origin_vat_rate / 100)
    else:
        price_ht_origin = price

    # Calculer le prix HT et TTC en DZD
    TVA_TAUX = vat_rate  # Utilisation du taux de TVA modifiable

    # Afficher le prix ajusté
    if language == "French":
        st.markdown(f"**Prix HT sans TVA du pays d'origine :** {price_ht_origin:,.2f} DZD / {price_ht_origin / conversion_rate:,.2f} EUR")
    else:
        # Version arabe...
        pass

    # Autres Informations sur le Véhicule
    # Comme précédemment...

    # Vérification de l'éligibilité du véhicule
    # Comme précédemment...

# **Onglet 2 : Coûts & Taxes**
with tabs[1]:
    st.header(texts["costs_header"])

    # Calcul des taxes ajusté pour une application correcte
    # Calcul des droits de douane (sur price_ht_origin)
    droits_douane_taux = calcul_droits_douane(carburant, cylindree, language)
    droits_douane = (droits_douane_taux / 100) * price_ht_origin
    droits_douane_eur = droits_douane / conversion_rate if conversion_rate != 0 else 0

    # Calcul de la TIC (sur price_ht_origin)
    TIC_TAUX = calcul_TIC(carburant, cylindree, language)
    TIC = (TIC_TAUX / 100) * price_ht_origin
    TIC_eur = TIC / conversion_rate if conversion_rate != 0 else 0

    # Somme avant TVA
    montant_avant_TVA = price_ht_origin + droits_douane + TIC + frais_annexes

    # Calcul de la TVA (sur montant_avant_TVA)
    TVA = (TVA_TAUX / 100) * montant_avant_TVA
    TVA_eur = TVA / conversion_rate if conversion_rate != 0 else 0

    # Coût total
    total_dzd = montant_avant_TVA + TVA
    total_eur = total_dzd / conversion_rate if conversion_rate != 0 else 0

    # Affichage des coûts et taxes
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            if language == "French":
                st.markdown("**En DZD:**")
                st.write(f"**Prix HT sans TVA du pays d'origine :** {price_ht_origin:,.2f} DZD")
                st.write(f"**Droits de Douane ({droits_douane_taux}%):** {droits_douane:,.2f} DZD")
                st.write(f"**TIC ({TIC_TAUX}%):** {TIC:,.2f} DZD")
                st.write(f"**Frais Annexes :** {frais_annexes:,.2f} DZD")
                st.write(f"**Montant Avant TVA :** {montant_avant_TVA:,.2f} DZD")
                st.write(f"**TVA Algérienne ({TVA_TAUX}%):** {TVA:,.2f} DZD")
                st.write(f"**Total Estimé :** {total_dzd:,.2f} DZD")
            else:
                # Version arabe...
                pass
        with col2:
            if language == "French":
                st.markdown("**En EUR:**")
                st.write(f"**Prix HT sans TVA du pays d'origine :** {price_ht_origin / conversion_rate:,.2f} EUR")
                st.write(f"**Droits de Douane ({droits_douane_taux}%):** {droits_douane_eur:,.2f} EUR")
                st.write(f"**TIC ({TIC_TAUX}%):** {TIC_eur:,.2f} EUR")
                st.write(f"**Frais Annexes :** {frais_annexes_eur:,.2f} EUR")
                st.write(f"**Montant Avant TVA :** {montant_avant_TVA / conversion_rate:,.2f} EUR")
                st.write(f"**TVA Algérienne ({TVA_TAUX}%):** {TVA_eur:,.2f} EUR")
                st.write(f"**Total Estimé :** {total_eur:,.2f} EUR")
            else:
                # Version arabe...
                pass

# **Onglet 3 : Revente & Bénéfice**
with tabs[2]:
    st.header("Calcul du Bénéfice de Revente" if language == "French" else "حساب الفائدة من إعادة البيع")

    # Aligner les champs côte à côte
    with st.container():
        col_resale_currency, col_resale_price = st.columns(2)
        with col_resale_currency:
            resale_price_currency = st.selectbox(
                texts["resale_price_currency_label"],
                texts["resale_price_currency_options"],
                key="resale_currency_select"
            )
        with col_resale_price:
            if language == "French":
                if resale_price_currency == "EUR":
                    resale_price_eur = st.number_input("Prix de revente (en EUR)", min_value=0.0, value=15000.0, step=100.0, key="resale_eur")
                    resale_price_dzd = resale_price_eur * conversion_rate
                else:
                    resale_price_dzd = st.number_input("Prix de revente (en DZD)", min_value=0.0, value=2000000.0, step=10000.0, key="resale_dzd")
                    resale_price_eur = resale_price_dzd / conversion_rate if conversion_rate != 0 else 0
            else:
                # Version arabe...
                pass

    # Affichage des prix de revente
    st.markdown(f"**Prix de revente en DZD :** {resale_price_dzd:,.2f} DZD / {resale_price_eur:,.2f} EUR")

    # Calcul du bénéfice
    benefit_dzd = resale_price_dzd - total_dzd
    benefit_eur = benefit_dzd / conversion_rate if conversion_rate != 0 else 0

    if benefit_dzd >= 0:
        st.success(f"{texts['benefit_label']}: {benefit_dzd:,.2f} DZD / {benefit_eur:,.2f} EUR")
    else:
        st.warning(f"{texts['benefit_label']}: {benefit_dzd:,.2f} DZD / {benefit_eur:,.2f} EUR")

    # **Nouvelle Fonctionnalité : Bénéfice Minimum Souhaité en DZD ou EUR**
    st.subheader(texts["desired_profit_label"])

    # Permettre à l'utilisateur de choisir la devise du bénéfice souhaité
    with st.container():
        col_profit_currency, col_desired_profit = st.columns(2)
        with col_profit_currency:
            profit_currency = st.selectbox(
                texts["profit_currency_label"],
                ("DZD", "EUR"),
                key="profit_currency_select"
            )
        with col_desired_profit:
            if profit_currency == "DZD":
                desired_profit_dzd = st.number_input(
                    texts["desired_profit_label"] + " (DZD)",
                    min_value=0.0,
                    value=0.0,
                    step=10000.0,
                    key="desired_profit_dzd"
                )
                desired_profit_eur = desired_profit_dzd / conversion_rate if conversion_rate != 0 else 0
            else:
                desired_profit_eur = st.number_input(
                    texts["desired_profit_label"] + " (EUR)",
                    min_value=0.0,
                    value=0.0,
                    step=100.0,
                    key="desired_profit_eur"
                )
                desired_profit_dzd = desired_profit_eur * conversion_rate

    # Calculer le prix minimum de revente nécessaire
    minimum_resale_price_dzd = total_dzd + desired_profit_dzd
    minimum_resale_price_eur = minimum_resale_price_dzd / conversion_rate if conversion_rate != 0 else 0

    # Afficher le prix minimum de revente
    st.markdown(f"**{texts['minimum_resale_price_label']} :** {minimum_resale_price_dzd:,.2f} DZD / {minimum_resale_price_eur:,.2f} EUR")

    # Avertir si le prix de revente est inférieur au minimum requis
    if resale_price_dzd < minimum_resale_price_dzd:
        st.warning("Le prix de revente saisi est inférieur au prix minimum requis pour atteindre le bénéfice souhaité.")

# **Onglet 4 : Résumé & Rapport**
with tabs[3]:
    st.subheader(texts["summary_header"])

    # Mettre à jour le tableau récapitulatif pour refléter les nouveaux calculs
    summary_data = {
        "Description": [
            f"Prix HT sans TVA du pays d'origine",
            f"Droits de Douane ({droits_douane_taux}%)",
            f"TIC ({TIC_TAUX}%)",
            "Frais Annexes",
            f"Montant Avant TVA",
            f"TVA Algérienne ({TVA_TAUX}%)",
            f"Total Estimé",
            f"Prix de Revente",
            f"Bénéfice Potentiel",
            texts["minimum_resale_price_label"]
        ],
        "En DZD": [
            f"{price_ht_origin:,.2f}",
            f"{droits_douane:,.2f}",
            f"{TIC:,.2f}",
            f"{frais_annexes:,.2f}",
            f"{montant_avant_TVA:,.2f}",
            f"{TVA:,.2f}",
            f"{total_dzd:,.2f}",
            f"{resale_price_dzd:,.2f}",
            f"{benefit_dzd:,.2f}",
            f"{minimum_resale_price_dzd:,.2f}"
        ],
        "En EUR": [
            f"{price_ht_origin / conversion_rate:,.2f}",
            f"{droits_douane_eur:,.2f}",
            f"{TIC_eur:,.2f}",
            f"{frais_annexes_eur:,.2f}",
            f"{montant_avant_TVA / conversion_rate:,.2f}",
            f"{TVA_eur:,.2f}",
            f"{total_eur:,.2f}",
            f"{resale_price_eur:,.2f}",
            f"{benefit_eur:,.2f}",
            f"{minimum_resale_price_eur:,.2f}"
        ]
    }

    summary_df = pd.DataFrame(summary_data)

    # Afficher le tableau
    st.table(summary_df)

    # Documents Requis
    st.header(texts["document_header"])
    st.markdown(texts["document_list"])

    # Restrictions Supplémentaires
    st.header(texts["restrictions_header"])
    st.markdown(texts["restrictions_list"])

    # Téléchargement du Rapport d'Estimation
    st.header(texts["download_header"])

    if FPDF_AVAILABLE:
        if st.button(texts["download_button"]):
            try:
                # Création du rapport
                pdf = PDF()
                pdf.add_page()

                # Ajouter un chapitre pour les informations générales
                pdf.chapter_title("Informations Générales" if language == "French" else "المعلومات العامة")
                general_info = f"""
                **Statut de l'Importateur :** {importer_status}

                **Taux de Conversion (DZD/EUR) :** {conversion_rate}

                **Marque :** {selected_make}

                **Modèle :** {selected_model_name}

                **Date de Fabrication :** {manufacture_year} - {manufacture_month_name}

                **Type de Carburant :** {carburant}

                **Cylindrée :** {cylindree} cm³

                **État de Conformité :** {etat}

                **Prix du Véhicule :** {price:,.2f} DZD / {price_eur:,.2f} EUR
                """
                pdf.chapter_body(general_info)

                # Ajouter un chapitre pour les coûts et taxes
                pdf.chapter_title(texts["costs_header"])
                costs_data = {
                    "Description": summary_data["Description"][:7],
                    "En DZD": summary_data["En DZD"][:7],
                    "En EUR": summary_data["En EUR"][:7]
                }
                costs_df = pd.DataFrame(costs_data)
                pdf.add_table(costs_df, "Coûts et Taxes" if language == "French" else "التكاليف والضرائب")

                # Ajouter un chapitre pour le bénéfice de revente
                pdf.chapter_title("Calcul du Bénéfice de Revente" if language == "French" else "حساب الفائدة من إعادة البيع")
                benefit_info = f"""
                **Prix de Revente :** {resale_price_dzd:,.2f} DZD / {resale_price_eur:,.2f} EUR
                **Bénéfice Potentiel :** {benefit_dzd:,.2f} DZD / {benefit_eur:,.2f} EUR
                **{texts['minimum_resale_price_label']} :** {minimum_resale_price_dzd:,.2f} DZD / {minimum_resale_price_eur:,.2f} EUR
                """
                pdf.chapter_body(benefit_info)

                # Générer le PDF en mémoire
                pdf_data = pdf.output(dest='S').encode('latin1')  # Utilisation de 'S' pour obtenir le PDF en mémoire

                # Bouton de téléchargement
                st.download_button(
                    label=texts["download_button"],
                    data=pdf_data,
                    file_name=texts["report_filename"],
                    mime='application/pdf'
                )
            except Exception as e:
                st.error(f"Erreur lors de la génération du PDF : {e}")
    else:
        st.warning("La génération de rapports PDF nécessite l'installation du module 'fpdf'. Veuillez l'installer pour utiliser cette fonctionnalité.")
