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
        # Vous pouvez ajouter les traductions en arabe ici si nécessaire.
    }
}

# Fonction pour obtenir les textes en fonction de la langue sélectionnée
def get_text(lang, key):
    return LANGUAGE[lang][key]

# Liste préenregistrée des marques et modèles courants
MAKES_MODELS = {
    "Renault": ["Clio", "Megane", "Captur", "Kadjar"],
    "Peugeot": ["208", "308", "2008", "3008"],
    "Citroën": ["C3", "C4", "C5 Aircross", "Berlingo"],
    "Audi": ["A3", "A4", "Q3", "Q5"],
    "Fiat": ["500", "Panda", "Tipo", "500X"],
    "BMW": ["Serie 3", "Serie 5", "X1", "X3"],
    "Mercedes-Benz": ["C-Class", "E-Class", "GLA", "GLC"],
    "Volkswagen": ["Golf", "Polo", "Tiguan", "Passat"],
    "Toyota": ["Corolla", "Yaris", "RAV4", "C-HR"],
    "Hyundai": ["i20", "i30", "Kona", "Santa Fe"]
}

# Classe pour générer le PDF
if FPDF_AVAILABLE:
    class PDF(FPDF):
        def header(self):
            # Titre
            self.set_font('Arial', 'B', 16)
            self.cell(0, 10, 'Rapport d\'Importation de Véhicule', ln=True, align='C')
            self.ln(10)

        def chapter_title(self, label):
            # Sous-titre
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, label, ln=True)
            self.ln(5)

        def chapter_body(self, body):
            # Corps du texte
            self.set_font('Arial', '', 12)
            for line in body.split('\n'):
                self.multi_cell(0, 10, line)
                self.ln()

        def add_table(self, df, title):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, title, ln=True)
            self.ln(2)
            # Table
            self.set_font('Arial', 'B', 10)
            col_width = (self.w - 2 * self.l_margin) / len(df.columns)
            for col in df.columns:
                self.cell(col_width, 10, col, border=1, align='C')
            self.ln()
            self.set_font('Arial', '', 10)
            for index, row in df.iterrows():
                for item in row:
                    if isinstance(item, float) or isinstance(item, int):
                        item_str = f"{item:,.2f}"
                    else:
                        item_str = str(item)
                    self.cell(col_width, 10, item_str, border=1)
                self.ln()
            self.ln(10)

# Fonction pour formater les montants en DZD avec équivalence en millions
def format_dzd(amount):
    millions = amount / 10_000  # 1 million équivaut à 10 000 DZD
    return f"{amount:,.2f} DZD ({int(millions)} millions)"

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

    # 4. Taux de Change pour le Marché Parallèle (Optionnel)
    st.sidebar.subheader("Taux de Change du Marché Parallèle (Optionnel)")
    use_parallel_rate = st.sidebar.checkbox("Utiliser le taux de change du marché parallèle")
    if use_parallel_rate:
        parallel_rate = st.sidebar.number_input(
            "Entrez le taux de change du marché parallèle DZD par EUR",
            min_value=1.0,
            value=150.0,
            step=1.0,
            help="Utilisez ce taux si vous souhaitez calculer le bénéfice en utilisant le taux de change du marché parallèle."
        )
    else:
        parallel_rate = conversion_rate  # Utiliser le taux officiel par défaut

# Utilisation des onglets pour organiser le contenu principal
tabs = st.tabs(["📄 Informations Véhicule", "💰 Coûts & Taxes", "📈 Revente & Bénéfice", "📋 Résumé & Rapport"])

# **Onglet 1 : Informations Véhicule**
with tabs[0]:
    st.header(texts["vehicle_info_header"])
    with st.container():
        col_year, col_month = st.columns(2)
        with col_year:
            current_year = datetime.now().year
            manufacture_year = st.number_input(
                f"{texts['manufacture_date_label']} - Année",
                min_value=1900,
                max_value=current_year,
                value=current_year,
                step=1
            )
        with col_month:
            months = texts["months"]
            manufacture_month_name = st.selectbox(
                f"{texts['manufacture_date_label']} - Mois",
                months
            )
            manufacture_month = months.index(manufacture_month_name) + 1

    # Calcul de l'âge du véhicule
    def calculate_age(year, month):
        today = datetime.now()
        manufacture_date = datetime(year, month, 1)
        age_in_years = today.year - manufacture_date.year
        age_in_months = today.month - manufacture_date.month
        if age_in_months < 0:
            age_in_years -= 1
            age_in_months += 12
        return age_in_years + age_in_months / 12

    age = calculate_age(manufacture_year, manufacture_month)

    # Sélection de la Marque et du Modèle du Véhicule
    with st.container():
        col_make, col_model = st.columns(2)
        with col_make:
            makes = list(MAKES_MODELS.keys())
            selected_make = st.selectbox(
                texts["select_make_label"],
                makes
            )
        with col_model:
            models = MAKES_MODELS.get(selected_make, [])
            if models:
                selected_model_name = st.selectbox(
                    texts["select_model_label"],
                    models
                )
            else:
                selected_model_name = None
                st.warning("Aucun modèle disponible pour cette marque.")

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
                    price = st.number_input("Prix du véhicule (en DZD)", min_value=0, value=15000000.00, step=10000.00, key="price_dzd")
                    price_eur = price / conversion_rate if conversion_rate != 0 else 0
                    st.markdown("**Note :** 15 000 000 DZD équivaut à 1 000 EUR.")
                else:
                    price_eur = st.number_input("Prix du véhicule (en EUR)", min_value=0.0, value=1000.0, step=10.0, key="price_eur")
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

    # Nouveau : Demander si la TVA du pays d'origine est incluse avec info-bulle
    origin_vat_included = st.radio(
        texts["origin_vat_label"],
        texts["origin_vat_options"],
        index=0,  # Par défaut sur 'Oui'
        help="Si le prix du véhicule inclut la TVA du pays d'origine (par exemple, la France), sélectionnez 'Oui'. Sinon, sélectionnez 'Non'."
    )

    # Ajuster le prix si la TVA du pays d'origine est récupérable
    origin_vat_rate = 20.0  # Taux de TVA du pays d'origine (France)
    if origin_vat_included == "Oui" and price_type == "TTC (Toutes Taxes Comprises)":
        # Prix sans TVA du pays d'origine
        price_ht_origin = price / (1 + origin_vat_rate / 100)
    else:
        price_ht_origin = price

    # Calculer le prix HT et TTC en DZD
    TVA_TAUX = vat_rate  # Utilisation du taux de TVA modifiable

    # Afficher le prix ajusté
    if language == "French":
        st.markdown(f"**Prix HT sans TVA du pays d'origine :** {format_dzd(price_ht_origin)} / {price_ht_origin / conversion_rate:,.2f} EUR")
    else:
        # Version arabe...
        pass

    # Autres Informations sur le Véhicule avec info-bulle pour la TIC
    with st.container():
        col_fuel, col_cylindree, col_etat = st.columns(3)
        with col_fuel:
            carburant = st.selectbox(texts["fuel_label"], texts["fuel_options"])
            st.markdown(
                "<span title='Sélectionnez le type de carburant du véhicule.'>🔍</span>",
                unsafe_allow_html=True
            )
        with col_cylindree:
            cylindree = st.number_input(texts["cylindree_label"], min_value=0, max_value=10000, value=1800, step=100)
            st.markdown(
                "<span title='Entrez la cylindrée du moteur en centimètres cubes (cm³).'>🔍</span>",
                unsafe_allow_html=True
            )
        with col_etat:
            etat = st.selectbox(texts["etat_label"], texts["etat_options"])
            st.markdown(
                "<span title='Sélectionnez l\'état de conformité du véhicule. Un bon état de marche est requis. Défauts mineurs ou majeurs affecteront l\'éligibilité. '>🔍</span>",
                unsafe_allow_html=True
            )

    # Vérification de l'éligibilité du véhicule avec explications
    st.subheader("Éligibilité du Véhicule")
    def verifier_eligibilite(age, carburant, cylindree, etat, importer_status, lang):
        eligibilite = True
        raisons = []

        # Vérification de l'âge du véhicule
        if importer_status == LANGUAGE[lang]["status_options"][0]:  # Particulier Résident
            if age > 3:
                eligibilite = False
                raisons.append("Le véhicule doit avoir moins de 3 ans pour les particuliers résidents.")
        elif importer_status == LANGUAGE[lang]["status_options"][1]:  # Particulier Non-Résident
            raisons.append("Conditions spécifiques à Particulier Non-Résident à implémenter.")

        # Vérification du carburant et des normes
        if carburant == LANGUAGE[lang]["fuel_options"][1]:  # Diesel
            if cylindree > 2000:
                eligibilite = False
                raisons.append("La cylindrée maximale pour les moteurs diesel est de 2000 cm³.")
        elif carburant == LANGUAGE[lang]["fuel_options"][0]:  # Essence
            if cylindree > 1800:
                eligibilite = False
                raisons.append("La cylindrée maximale pour les moteurs à essence est de 1800 cm³.")

        # Vérification de l'état de conformité
        if etat != LANGUAGE[lang]["etat_options"][0]:  # Bon état de marche
            eligibilite = False
            raisons.append("Le véhicule doit être en bon état de marche, sans défaut majeur ou critique.")

        return eligibilite, raisons

    # Vérification de l'éligibilité
    eligible, raisons = verifier_eligibilite(age, carburant, cylindree, etat, importer_status, language)

    if eligible:
        st.success(texts["eligibility_success"])
    else:
        st.error(texts["eligibility_error"])
        for raison in raisons:
            st.write(f"- {raison}")

# **Définitions des fonctions manquantes**

def calcul_droits_douane(carburant, cylindree, lang):
    if carburant == LANGUAGE[lang]["fuel_options"][0]:  # Essence
        if cylindree <= 1800:
            taux = 15
        else:
            taux = 25
    elif carburant == LANGUAGE[lang]["fuel_options"][1]:  # Diesel
        if cylindree <= 2000:
            taux = 20
        else:
            taux = 30
    else:
        taux = 0
    return taux

def calcul_TIC(carburant, cylindree, lang):
    if carburant == LANGUAGE[lang]["fuel_options"][1]:  # Diesel
        if 2000 < cylindree <= 2500:
            return 2
        elif 2500 < cylindree <= 3000:
            return 5
        elif cylindree > 3000:
            return 10
        else:
            return 0
    else:
        return 0

# **Onglet 2 : Coûts & Taxes**
with tabs[1]:
    st.header(texts["costs_header"])

    # Estimation des frais annexes
    frais_annexes = 50000  # Exemple fixe en DZD
    frais_annexes_eur = frais_annexes / conversion_rate if conversion_rate != 0 else 0

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
    TVA_TAUX = vat_rate
    TVA = (TVA_TAUX / 100) * montant_avant_TVA
    TVA_eur = TVA / conversion_rate if conversion_rate != 0 else 0

    # Coût total
    total_dzd = montant_avant_TVA + TVA
    total_eur = total_dzd / conversion_rate if conversion_rate != 0 else 0

    # Présentation des coûts et taxes sous forme de tableau
    costs_data = {
        "Description": [
            f"Prix HT sans TVA du pays d'origine",
            f"Droits de Douane ({droits_douane_taux}%)",
            f"TIC ({TIC_TAUX}%)",
            "Frais Annexes",
            "Montant Avant TVA",
            f"TVA Algérienne ({TVA_TAUX}%)",
            "Total Estimé"
        ],
        "En DZD": [
            format_dzd(price_ht_origin),
            format_dzd(droits_douane),
            format_dzd(TIC),
            format_dzd(frais_annexes),
            format_dzd(montant_avant_TVA),
            format_dzd(TVA),
            format_dzd(total_dzd)
        ],
        "En EUR": [
            f"{price_ht_origin / conversion_rate:,.2f}",
            f"{droits_douane_eur:,.2f}",
            f"{TIC_eur:,.2f}",
            f"{frais_annexes_eur:,.2f}",
            f"{montant_avant_TVA / conversion_rate:,.2f}",
            f"{TVA_eur:,.2f}",
            f"{total_eur:,.2f}"
        ]
    }

    costs_df = pd.DataFrame(costs_data)

    # Affichage du tableau avec info-bulle sur la TVA
    st.markdown("### **Détails des Coûts et Taxes**")
    st.table(costs_df)
    st.markdown(
        "<span title='La TVA est calculée sur le montant avant TVA, incluant le prix HT, les droits de douane, la TIC et les frais annexes.'>ℹ️</span> **Note :** La TVA est calculée sur la somme des éléments précédents.",
        unsafe_allow_html=True
    )

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
                    resale_price_eur = st.number_input("Prix de revente (en EUR)", min_value=0.0, value=1000.0, step=10.0, key="resale_eur")
                    resale_price_dzd = resale_price_eur * conversion_rate
                else:
                    resale_price_dzd = st.number_input("Prix de revente (en DZD)", min_value=0.0, value=15000000.0, step=100000.0, key="resale_dzd")
                    resale_price_eur = resale_price_dzd / conversion_rate if conversion_rate != 0 else 0
            else:
                # Version arabe...
                pass

    # Affichage des prix de revente avec traduction
    st.markdown(f"**Prix de revente en DZD :** {format_dzd(resale_price_dzd)} / {resale_price_eur:,.2f} EUR")
    st.markdown(
        "<span title='En dialecte algérien, 15 000 000 DZD équivaut à 1 000 EUR.'>ℹ️</span> **Note :** 15 000 000 DZD équivaut à 1 000 EUR.",
        unsafe_allow_html=True
    )

    # Calcul du bénéfice
    benefit_dzd = resale_price_dzd - total_dzd
    benefit_eur = benefit_dzd / parallel_rate if parallel_rate != 0 else 0

    if benefit_dzd >= 0:
        st.success(f"{texts['benefit_label']}: {format_dzd(benefit_dzd)} / {benefit_eur:,.2f} EUR")
    else:
        st.warning(f"{texts['benefit_label']}: {format_dzd(benefit_dzd)} / {benefit_eur:,.2f} EUR")

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
                desired_profit_eur = desired_profit_dzd / parallel_rate if parallel_rate != 0 else 0
            else:
                desired_profit_eur = st.number_input(
                    texts["desired_profit_label"] + " (EUR)",
                    min_value=0.0,
                    value=0.0,
                    step=100.0,
                    key="desired_profit_eur"
                )
                desired_profit_dzd = desired_profit_eur * parallel_rate

    # Calculer le prix minimum de revente nécessaire
    minimum_resale_price_dzd = total_dzd + desired_profit_dzd
    minimum_resale_price_eur = minimum_resale_price_dzd / parallel_rate if parallel_rate != 0 else 0

    # Afficher le prix minimum de revente
    st.markdown(f"**{texts['minimum_resale_price_label']} :** {format_dzd(minimum_resale_price_dzd)} / {minimum_resale_price_eur:,.2f} EUR")

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
            "Total Estimé",
            "Prix de Revente",
            "Bénéfice Potentiel",
            texts["minimum_resale_price_label"]
        ],
        "En DZD": [
            format_dzd(price_ht_origin),
            format_dzd(droits_douane),
            format_dzd(TIC),
            format_dzd(frais_annexes),
            format_dzd(montant_avant_TVA),
            format_dzd(TVA),
            format_dzd(total_dzd),
            format_dzd(resale_price_dzd),
            format_dzd(benefit_dzd),
            format_dzd(minimum_resale_price_dzd)
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
                pdf.chapter_title("Informations Générales")
                general_info = f"""
**Statut de l'Importateur :** {importer_status}

**Taux de Conversion (DZD/EUR) :** {conversion_rate}

**Marque :** {selected_make}

**Modèle :** {selected_model_name}

**Date de Fabrication :** {manufacture_year} - {manufacture_month_name}

**Type de Carburant :** {carburant}

**Cylindrée :** {cylindree} cm³

**État de Conformité :** {etat}

**Prix du Véhicule :** {format_dzd(price)} / {price_eur:,.2f} EUR
"""
                pdf.chapter_body(general_info)

                # Ajouter un chapitre pour les coûts et taxes
                pdf.chapter_title(texts["costs_header"])
                costs_data_pdf = {
                    "Description": summary_data["Description"][:7],
                    "En DZD": summary_data["En DZD"][:7],
                    "En EUR": summary_data["En EUR"][:7]
                }
                costs_df_pdf = pd.DataFrame(costs_data_pdf)
                pdf.add_table(costs_df_pdf, "Coûts et Taxes")

                # Ajouter un chapitre pour le bénéfice de revente
                pdf.chapter_title("Calcul du Bénéfice de Revente")
                benefit_info = f"""
**Prix de Revente :** {format_dzd(resale_price_dzd)} / {resale_price_eur:,.2f} EUR

**Bénéfice Potentiel :** {format_dzd(benefit_dzd)} / {benefit_eur:,.2f} EUR

**{texts['minimum_resale_price_label']} :** {format_dzd(minimum_resale_price_dzd)} / {minimum_resale_price_eur:,.2f} EUR
"""
                pdf.chapter_body(benefit_info)

                # Ajouter les documents requis et les restrictions
                pdf.chapter_title(texts["document_header"])
                pdf.chapter_body(texts["document_list"])

                pdf.chapter_title(texts["restrictions_header"])
                pdf.chapter_body(texts["restrictions_list"])

                # Générer le PDF en mémoire
                pdf_data = pdf.output(dest='S').encode('latin1')

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
