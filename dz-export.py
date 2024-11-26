import streamlit as st
import pandas as pd
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
        "price_label": "Prix du véhicule (en DZD)",
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
        "report_filename": "rapport_importation.xlsx"
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
        "price_label": "سعر المركبة (بالدينار الجزائري)",
        "costs_header": "تقدير التكاليف والضرائب",
        "eligibility_success": "المركبة مؤهلة للاستيراد.",
        "eligibility_error": "المركبة غير مؤهلة للاستيراد للأسباب التالية:",
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
        "report_filename": "rapport_importation.xlsx"  # Peut rester en français ou être traduit
    }
}

# Fonction pour obtenir les textes en fonction de la langue sélectionnée
def get_text(lang, key):
    return LANGUAGE[lang][key]

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

# Remplacer l'âge par la sélection de l'année et du mois de fabrication
col_year, col_month = st.columns(2)

with col_year:
    current_year = datetime.now().year
    manufacture_year = st.number_input(
        texts["manufacture_date_label"] + " - " + ("Année" if language == "French" else "السنة"),
        min_value=1900,
        max_value=current_year,
        value=current_year
    )

with col_month:
    current_month = datetime.now().month
    manufacture_month = st.selectbox(
        texts["manufacture_date_label"] + " - " + ("Mois" if language == "French" else "الشهر"),
        list(range(1, 13)),
        format_func=lambda x: f"{x}" if language == "French" else f"{x}"
    )

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

carburant = st.selectbox(texts["fuel_label"], texts["fuel_options"])
cylindree = st.number_input(texts["cylindree_label"], min_value=0, max_value=5000, value=1800)
etat = st.selectbox(texts["etat_label"], texts["etat_options"])

# 4. Prix du Véhicule
prix_vehicule = st.number_input(texts["price_label"], min_value=0, value=1000000, step=10000)

# 5. Calcul des Taxes et Coûts
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
droits_douane = (droits_douane_taux / 100) * prix_vehicule

# Calcul de la TVA
TVA = (TVA_TAUX / 100) * (prix_vehicule + droits_douane)

# Calcul de la TIC
TIC = (TIC_TAUX / 100) * prix_vehicule

# Calcul total
total = prix_vehicule + droits_douane + TVA + TIC + frais_annexes

# Conversion en EUR
droits_douane_eur = droits_douane / conversion_rate
TVA_eur = TVA / conversion_rate
TIC_eur = TIC / conversion_rate
frais_annexes_eur = frais_annexes / conversion_rate
total_eur = total / conversion_rate

# Affichage des résultats
st.subheader(texts["summary_header"])

col1, col2 = st.columns(2)

with col1:
    st.write(f"**Droits de Douane ({droits_douane_taux}%):** {droits_douane:,.2f} DZD")
    st.write(f"**TVA ({TVA_TAUX}%):** {TVA:,.2f} DZD")
    st.write(f"**TIC ({TIC_TAUX}%):** {TIC:,.2f} DZD")
    st.write(f"**Frais Annexes:** {frais_annexes:,.2f} DZD")
    st.write(f"**Total Estimé:** {total:,.2f} DZD")

with col2:
    st.write(f"**Droits de Douane ({droits_douane_taux}%):** {droits_douane_eur:,.2f} EUR")
    st.write(f"**TVA ({TVA_TAUX}%):** {TVA_eur:,.2f} EUR")
    st.write(f"**TIC ({TIC_TAUX}%):** {TIC_eur:,.2f} EUR")
    st.write(f"**Frais Annexes:** {frais_annexes_eur:,.2f} EUR")
    st.write(f"**Total Estimé:** {total_eur:,.2f} EUR")

# 4. Documents Requis
st.header(texts["document_header"])
st.markdown(texts["document_list"])

# 5. Restrictions Supplémentaires
st.header(texts["restrictions_header"])
st.markdown(texts["restrictions_list"])

# 6. Téléchargement du Rapport (Optionnel)
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
        "Total Estimé (DZD)": total,
        "Total Estimé (EUR)": total_eur,
        "Taux de Conversion (DZD/EUR)": conversion_rate
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
