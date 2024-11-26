import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from datetime import datetime

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
        "report_filename": "rapport_importation.xlsx",
        "months": [
            "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
        ],
        "select_make_label": "Sélectionnez la marque",
        "select_model_label": "Sélectionnez le modèle",
        "loading_models": "Chargement des modèles..."
    },
    "Arabic": {
        "title": "محاكي استيراد المركبات إلى الجزائر",
        "introduction": "مرحبًا بكم في محاكي استيراد المركبات إلى الجزائر. سيساعدك هذا المحاكي في تقدير التكاليف المرتبطة باستيراد مركبتك، وفقًا للأنظمة السارية.",
        "sidebar_header": "معلومات عن المستورد وتحويل العملات",
        "select_status": "اختر حالتك",
        "status_options": ("مقيم خاص", "مقيم غير مقيم (ثنائي الجنسية)"),
        "conversion_subheader": "سعر الصرف",
        "conversion_label": "سعر الصرف DZD مقابل EUR",
        "vehicle_info_header": "معلومات عن المركبة",
        "manufacture_date_label": "تاريخ تصنيع المركبة",
        "fuel_label": "نوع الوقود",
        "fuel_options": ("بنزين", "ديزل"),
        "cylindree_label": "سعة المحرك (بالسم³)",
        "etat_label": "حالة المطابقة",
        "etat_options": ("حالة جيدة للعمل", "عيب طفيف", "عيب كبير"),
        "price_input_label": "سعر المركبة",
        "price_currency_label": "عملة السعر",
        "price_currency_options": ("دينار جزائري", "يورو"),
        "costs_header": "تقدير التكاليف والضرائب",
        "eligibility_success": "المركبة مؤهلة للاستيراد.",
        "eligibility_error": "المركبة غير مؤهلة للاستيراد للأسباب التالية :",
        "summary_header": "ملخص التكاليف والضرائب",
        "document_header": "المستندات المطلوبة للتخليص الجمركي",
        "document_list": """
        1. **نسخة من بطاقة الهوية** أو بطاقة الإقامة.
        2. **شهادة الإقامة**.
        3. **شهادة تسجيل** المركبة في الخارج.
        4. **فاتورة الشراء** أو عقد البيع.
        5. **مستند يثبت حالة جيدة للعمل** للمركبة (لا يزيد عمره عن ثلاثة أشهر).
        6. **تقرير تقييم المطابقة** صادر عن خبير معتمد.
        """,
        "restrictions_header": "قيود إضافية",
        "restrictions_list": """
        - **مدة عدم التنازل** : لا يمكن التنازل عن المركبة المستوردة قبل مرور ثلاث سنوات من تاريخ الاستيراد.
        - **المعايير البيئية** : يجب أن تلتزم المركبات بمعايير الانبعاثات السارية في الجزائر.
        """,
        "download_header": "تحميل تقرير التقدير",
        "download_button": "تحميل التقرير",
        "report_filename": "rapport_importation.xlsx",
        "months": [
            "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
            "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
        ],
        "select_make_label": "اختر العلامة التجارية",
        "select_model_label": "اختر الطراز",
        "loading_models": "جارٍ تحميل الطرازات..."
    }
}

# Fonction pour obtenir les textes en fonction de la langue sélectionnée
def get_text(lang, key):
    return LANGUAGE[lang][key]

# Fonctions pour interagir avec l'API CarQuery
@st.cache_data(show_spinner=False)
def get_makes():
    """Récupère la liste des marques de véhicules depuis CarQuery API."""
    url = "https://www.carqueryapi.com/api/0.3/?cmd=getMakes&callback="
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            makes = data['Makes']
            # Trier les marques par ordre alphabétique
            makes_sorted = sorted(makes, key=lambda x: x['make_display'])
            return makes_sorted
        else:
            st.error("Erreur lors de la récupération des marques.")
            return []
    except Exception as e:
        st.error(f"Une erreur s'est produite : {e}")
        return []

@st.cache_data(show_spinner=False)
def get_models(make_slug):
    """Récupère la liste des modèles pour une marque donnée depuis CarQuery API."""
    url = f"https://www.carqueryapi.com/api/0.3/?cmd=getModels&make={make_slug}&callback="
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            models = data['Models']
            # Trier les modèles par ordre alphabétique
            models_sorted = sorted(models, key=lambda x: x['model_display'])
            return models_sorted
        else:
            st.error("Erreur lors de la récupération des modèles.")
            return []
    except Exception as e:
        st.error(f"Une erreur s'est produite : {e}")
        return []

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
importer_status = st.sidebar.selectbox(
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

# 3. Informations sur le Véhicule
st.header(texts["vehicle_info_header"])

# Sélection de l'année et du mois de fabrication avec noms de mois
col_year, col_month = st.columns(2)

with col_year:
    current_year = datetime.now().year
    manufacture_year = st.number_input(
        texts["manufacture_date_label"] + " - " + ("Année" if language == "French" else "السنة"),
        min_value=1900,
        max_value=current_year,
        value=current_year,
        step=1
    )

with col_month:
    months = texts["months"]
    manufacture_month_name = st.selectbox(
        texts["manufacture_date_label"] + " - " + ("Mois" if language == "French" else "الشهر"),
        months
    )
    # Map the selected month name to month number
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

# 4. Sélection de la Marque et du Modèle du Véhicule
st.subheader(get_text(language, "vehicle_info_header"))

# Récupérer les marques
makes = get_makes()
if not makes:
    st.warning("Aucune marque disponible.")
else:
    make_names = [make['make_display'] for make in makes]
    selected_make_name = st.selectbox(
        get_text(language, "select_make_label"),
        make_names
    )

    # Récupérer le slug de la marque sélectionnée pour obtenir les modèles
    selected_make = next((make for make in makes if make['make_display'] == selected_make_name), None)

    if selected_make:
        make_slug = selected_make['make_slug']
        # Récupérer les modèles basés sur la marque sélectionnée
        with st.spinner(texts["loading_models"]):
            models = get_models(make_slug)
        if models:
            model_names = [model['model_display'] for model in models]
            selected_model_name = st.selectbox(
                get_text(language, "select_model_label"),
                model_names
            )
        else:
            selected_model_name = None
    else:
        selected_model_name = None

# Check if model is selected before proceeding
if selected_make and selected_model_name:
    # 5. Prix du Véhicule avec sélection de la devise
    st.subheader(texts["price_input_label"])

    col_currency, col_price = st.columns([1, 2])

    with col_currency:
        price_currency = st.selectbox(
            texts["price_currency_label"],
            texts["price_currency_options"]
        )

    with col_price:
        if language == "French":
            if price_currency == "DZD":
                prix_vehicule_dzd = st.number_input("Prix du véhicule (en DZD)", min_value=0, value=1000000, step=10000)
                prix_vehicule_eur = prix_vehicule_dzd / conversion_rate
            else:
                prix_vehicule_eur = st.number_input("Prix du véhicule (en EUR)", min_value=0.0, value=1000.0, step=100.0)
                prix_vehicule_dzd = prix_vehicule_eur * conversion_rate
        else:
            if price_currency == "دينار جزائري":
                prix_vehicule_dzd = st.number_input("سعر المركبة (بالدينار الجزائري)", min_value=0, value=1000000, step=10000)
                prix_vehicule_eur = prix_vehicule_dzd / conversion_rate
            else:
                prix_vehicule_eur = st.number_input("سعر المركبة (باليورو)", min_value=0.0, value=1000.0, step=100.0)
                prix_vehicule_dzd = prix_vehicule_eur * conversion_rate

    # 6. Autres Informations sur le Véhicule
    carburant = st.selectbox(texts["fuel_label"], texts["fuel_options"])
    cylindree = st.number_input(texts["cylindree_label"], min_value=0, max_value=5000, value=1800, step=100)
    etat = st.selectbox(texts["etat_label"], texts["etat_options"])

    # 7. Calcul des Taxes et Coûts
    st.header(texts["costs_header"])

    # Fonction pour vérifier l'éligibilité
    def verifier_eligibilite(age, carburant, cylindree, etat, importer_status, lang):
        eligibilite = True
        raisons = []

        # Vérification de l'âge du véhicule
        if importer_status == LANGUAGE[lang]["status_options"][0]:  # Particulier Résident / مقيم خاص
            if age > 3:
                eligibilite = False
                if lang == "French":
                    raisons.append("Le véhicule doit avoir moins de 3 ans pour les particuliers résidents.")
                else:
                    raisons.append("يجب أن يكون عمر المركبة أقل من 3 سنوات للمقيمين الخاصين.")
        elif importer_status == LANGUAGE[lang]["status_options"][1]:  # Particulier Non-Résident / مقيم غير مقيم
            if lang == "French":
                raisons.append("Conditions spécifiques à Particulier Non-Résident à implémenter.")
            else:
                raisons.append("يجب إضافة شروط خاصة بالمقيمين غير المقيمين.")

        # Vérification du carburant et des normes
        if carburant == LANGUAGE[lang]["fuel_options"][1]:  # Diesel / ديزل
            if cylindree > 2000:
                eligibilite = False
                if lang == "French":
                    raisons.append("La cylindrée maximale pour les moteurs diesel est de 2000 cm³.")
                else:
                    raisons.append("السعة القصوى لمحركات الديزل هي 2000 سم³.")
        elif carburant == LANGUAGE[lang]["fuel_options"][0]:  # Essence / بنزين
            if cylindree > 1800:
                eligibilite = False
                if lang == "French":
                    raisons.append("La cylindrée maximale pour les moteurs à essence est de 1800 cm³.")
                else:
                    raisons.append("السعة القصوى لمحركات البنزين هي 1800 سم³.")

        # Vérification de l'état de conformité
        if etat != LANGUAGE[lang]["etat_options"][0]:  # Bon état de marche / حالة جيدة للعمل
            eligibilite = False
            if lang == "French":
                raisons.append("Le véhicule doit être en bon état de marche, sans défaut majeur ou critique.")
            else:
                raisons.append("يجب أن تكون المركبة في حالة جيدة للعمل، بدون عيوب كبيرة أو حرجة.")

        return eligibilite, raisons

    # Vérification de l'éligibilité
    eligible, raisons = verifier_eligibilite(age, carburant, cylindree, etat, importer_status, language)

    if eligible:
        st.success(texts["eligibility_success"])
    else:
        st.error(texts["eligibility_error"])
        for raison in raisons:
            st.write(f"- {raison}")

    # Calcul des droits de douane
    def calcul_droits_douane(carburant, cylindree, lang):
        if carburant == LANGUAGE[lang]["fuel_options"][0]:  # Essence / بنزين
            if cylindree <= 1800:
                taux = 15
            else:
                taux = 25
        elif carburant == LANGUAGE[lang]["fuel_options"][1]:  # Diesel / ديزل
            if cylindree <= 2000:
                taux = 20
            else:
                taux = 30
        else:
            taux = 0
        return taux

    droits_douane_taux = calcul_droits_douane(carburant, cylindree, language)

    # Calcul de la TVA
    TVA_TAUX = 19

    # Calcul de la TIC
    def calcul_TIC(carburant, cylindree, lang):
        if carburant == LANGUAGE[lang]["fuel_options"][1] and 2000 < cylindree <= 3000:  # Diesel / ديزل
            return 60
        else:
            return 0

    TIC_TAUX = calcul_TIC(carburant, cylindree, language)

    # Estimation des frais annexes
    frais_annexes = 50000  # Exemple fixe en DZD, à ajuster selon les besoins

    # Calcul des droits de douane
    droits_douane = (droits_douane_taux / 100) * prix_vehicule_dzd
    droits_douane_eur = droits_douane / conversion_rate

    # Calcul de la TVA
    TVA = (TVA_TAUX / 100) * (prix_vehicule_dzd + droits_douane)
    TVA_eur = TVA / conversion_rate

    # Calcul de la TIC
    TIC = (TIC_TAUX / 100) * prix_vehicule_dzd
    TIC_eur = TIC / conversion_rate

    # Calcul total
    total_dzd = prix_vehicule_dzd + droits_douane + TVA + TIC + frais_annexes
    total_eur = total_dzd / conversion_rate

    # Conversion des frais annexes en EUR
    frais_annexes_eur = frais_annexes / conversion_rate

    # Affichage des résultats
    st.subheader(texts["summary_header"])

    col1, col2 = st.columns(2)

    with col1:
        if language == "French":
            st.markdown("**En DZD:**")
        else:
            st.markdown("**بالدينار الجزائري:**")
        st.write(f"**Droits de Douane ({droits_douane_taux}%):** {droits_douane:,.2f} DZD")
        st.write(f"**TVA ({TVA_TAUX}%):** {TVA:,.2f} DZD")
        st.write(f"**TIC ({TIC_TAUX}%):** {TIC:,.2f} DZD")
        st.write(f"**Frais Annexes:** {frais_annexes:,.2f} DZD")
        st.write(f"**Total Estimé:** {total_dzd:,.2f} DZD")

    with col2:
        if language == "French":
            st.markdown("**En EUR:**")
        else:
            st.markdown("**باليورو:**")
        st.write(f"**Droits de Douane ({droits_douane_taux}%):** {droits_douane_eur:,.2f} EUR")
        st.write(f"**TVA ({TVA_TAUX}%):** {TVA_eur:,.2f} EUR")
        st.write(f"**TIC ({TIC_TAUX}%):** {TIC_eur:,.2f} EUR")
        st.write(f"**Frais Annexes:** {frais_annexes_eur:,.2f} EUR")
        st.write(f"**Total Estimé:** {total_eur:,.2f} EUR")

    # 8. Documents Requis
    st.header(texts["document_header"])
    st.markdown(texts["document_list"])

    # 9. Restrictions Supplémentaires
    st.header(texts["restrictions_header"])
    st.markdown(texts["restrictions_list"])

    # 10. Téléchargement du Rapport (Optionnel)
    st.header(texts["download_header"])

    if st.button(texts["download_button"]):
        # Création du rapport
        rapport = {
            "Droits de Douane (%)": droits_douane_taux,
            "Droits de Douane (DZD)": droits_douane,
            "Droits de Douane (EUR)": droits_douane_eur,
            "TVA (%)": TVA_TAUX,
            "TVA (DZD)": TVA,
            "TVA (EUR)": TVA_eur,
            "TIC (%)": TIC_TAUX,
            "TIC (DZD)": TIC,
            "TIC (EUR)": TIC_eur,
            "Frais Annexes (DZD)": frais_annexes,
            "Frais Annexes (EUR)": frais_annexes_eur,
            "Total Estimé (DZD)": total_dzd,
            "Total Estimé (EUR)": total_eur,
            "Taux de Conversion (DZD/EUR)": conversion_rate,
            "Devise du Prix": price_currency
        }

        df = pd.DataFrame([rapport])

        # Convertir en Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Rapport')
        data = output.getvalue()

        st.download_button(
            label=texts["download_button"],
            data=data,
            file_name=texts["report_filename"],
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
else:
    st.info("Veuillez sélectionner une marque et un modèle de véhicule pour estimer les coûts.")
