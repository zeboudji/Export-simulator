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
        "vat_label": "Taux de TVA (%)",
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
        "price_type_options": ("HT", "TTC"),
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
        "price_type_ht": "Hors Taxe (HT)",
        "price_type_ttc": "Toutes Taxes Comprises (TTC)",
        "tax_rate": "19%"  # TVA par défaut
    },
    "Arabic": {
        "title": "محاكي استيراد المركبات إلى الجزائر",
        "introduction": "مرحبًا بكم في محاكي استيراد المركبات إلى الجزائر. سيساعدك هذا المحاكي في تقدير التكاليف المرتبطة باستيراد مركبتك، وفقًا للأنظمة السارية.",
        "sidebar_header": "معلومات عن المستورد وتحويل العملات",
        "select_status": "اختر حالتك",
        "status_options": ("مقيم خاص", "مقيم غير مقيم (ثنائي الجنسية)"),
        "conversion_subheader": "سعر الصرف",
        "conversion_label": "سعر الصرف DZD مقابل EUR",
        "vat_subheader": "معدل ضريبة القيمة المضافة",
        "vat_label": "معدل ضريبة القيمة المضافة (%)",
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
        "price_type_label": "نوع السعر",
        "price_type_options": ("HT", "TTC"),
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
        "report_filename": "rapport_importation.pdf",
        "months": [
            "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
            "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
        ],
        "select_make_label": "اختر العلامة التجارية",
        "select_model_label": "اختر الطراز",
        "loading_models": "جارٍ تحميل الطرازات...",
        "resale_price_label": "سعر إعادة البيع المطلوب في الجزائر",
        "resale_price_currency_label": "عملة سعر إعادة البيع",
        "resale_price_currency_options": ("دينار جزائري", "يورو"),
        "benefit_label": "الفائدة المحتملة",
        "price_type_ht": "قبل الضريبة (HT)",
        "price_type_ttc": "شامل الضريبة (TTC)",
        "tax_rate": "19%"  # TVA par défaut
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
            # Remplacement de self.epw par self.w - 2 * self.l_margin
            col_width = (self.w - 2 * self.l_margin) / len(df.columns)  # distribute content evenly
            for col in df.columns:
                self.cell(col_width, 10, col, border=1, align='C')
            self.ln()
            self.set_font('Arial', '', 10)
            for index, row in df.iterrows():
                for item in row:
                    # Convertir les nombres en chaînes avec des séparateurs de milliers
                    if isinstance(item, float) or isinstance(item, int):
                        item_str = f"{item:,.2f}"
                    else:
                        item_str = str(item)
                    self.cell(col_width, 10, item_str, border=1)
                self.ln()
            self.ln(10)

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
    with st.container():
        col_year, col_month = st.columns(2)
        with col_year:
            current_year = datetime.now().year
            manufacture_year = st.number_input(
                f"{texts['manufacture_date_label']} - " + ("Année" if language == "French" else "السنة"),
                min_value=1900,
                max_value=current_year,
                value=current_year,
                step=1
            )
        with col_month:
            months = texts["months"]
            manufacture_month_name = st.selectbox(
                f"{texts['manufacture_date_label']} - " + ("Mois" if language == "French" else "الشهر"),
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
                    price = st.number_input("Prix du véhicule (en DZD)", min_value=0, value=1000000, step=10000, key="price_dzd")
                    price_eur = price / conversion_rate if conversion_rate != 0 else 0
                else:
                    price_eur = st.number_input("Prix du véhicule (en EUR)", min_value=0.0, value=1000.0, step=100.0, key="price_eur")
                    price = price_eur * conversion_rate
            else:
                if price_currency == "دينار جزائري":
                    price = st.number_input("سعر المركبة (بالدينار الجزائري)", min_value=0, value=1000000, step=10000, key="price_dzd_ar")
                    price_eur = price / conversion_rate if conversion_rate != 0 else 0
                else:
                    price_eur = st.number_input("سعر المركبة (باليورو)", min_value=0.0, value=1000.0, step=100.0, key="price_eur_ar")
                    price = price_eur * conversion_rate

        with col_price_type:
            price_type = st.selectbox(
                texts["price_type_label"],
                texts["price_type_options"],
                key="price_type_select"
            )

    # Calcul des prix HT et TTC
    TVA_TAUX = vat_rate  # Utilisation du taux de TVA modifiable

    if language == "French":
        if price_type == "HT":
            price_ttc = price * (1 + TVA_TAUX / 100)
            price_ht = price
            st.markdown(f"**Prix TTC :** {price_ttc:,.2f} DZD / {price_ttc / conversion_rate:,.2f} EUR")
        else:
            price_ttc = price
            price_ht = price / (1 + TVA_TAUX / 100)
            st.markdown(f"**Prix HT :** {price_ht:,.2f} DZD / {price_ht / conversion_rate:,.2f} EUR")
    else:
        if price_type == "HT":
            price_ttc = price * (1 + TVA_TAUX / 100)
            price_ht = price
            st.markdown(f"**السعر شامل الضريبة (TTC) :** {price_ttc:,.2f} دينار جزائري / {price_ttc / conversion_rate:,.2f} يورو")
        else:
            price_ttc = price
            price_ht = price / (1 + TVA_TAUX / 100)
            st.markdown(f"**السعر قبل الضريبة (HT) :** {price_ht:,.2f} دينار جزائري / {price_ht / conversion_rate:,.2f} يورو")

    # Autres Informations sur le Véhicule
    with st.container():
        col_fuel, col_cylindree, col_etat = st.columns(3)
        with col_fuel:
            carburant = st.selectbox(texts["fuel_label"], texts["fuel_options"])
        with col_cylindree:
            cylindree = st.number_input(texts["cylindree_label"], min_value=0, max_value=10000, value=1800, step=100)
        with col_etat:
            etat = st.selectbox(texts["etat_label"], texts["etat_options"])

    # Vérification de l'éligibilité (déplacée ici depuis l'onglet 2)
    st.subheader("Éligibilité du Véhicule")
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

# **Onglet 2 : Coûts & Taxes**
with tabs[1]:
    st.header(texts["costs_header"])

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
    droits_douane = (droits_douane_taux / 100) * price_ttc
    droits_douane_eur = droits_douane / conversion_rate if conversion_rate != 0 else 0

    # Calcul de la TVA sur (Prix TTC + Droits de Douane)
    TVA = (TVA_TAUX / 100) * (price_ttc + droits_douane)
    TVA_eur = TVA / conversion_rate if conversion_rate != 0 else 0

    # Calcul de la TIC
    TIC = (TIC_TAUX / 100) * price_ttc
    TIC_eur = TIC / conversion_rate if conversion_rate != 0 else 0

    # Calcul total
    total_dzd = price_ttc + droits_douane + TVA + TIC + frais_annexes
    total_eur = total_dzd / conversion_rate if conversion_rate != 0 else 0

    # Conversion des frais annexes en EUR
    frais_annexes_eur = frais_annexes / conversion_rate if conversion_rate != 0 else 0

    # Affichage des coûts et taxes
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            if language == "French":
                st.markdown("**En DZD:**")
                st.write(f"**Prix TTC :** {price_ttc:,.2f} DZD")
                st.write(f"**Droits de Douane ({droits_douane_taux}%):** {droits_douane:,.2f} DZD")
                st.write(f"**TVA ({TVA_TAUX}%):** {TVA:,.2f} DZD")
                st.write(f"**TIC ({TIC_TAUX}%):** {TIC:,.2f} DZD")
                st.write(f"**Frais Annexes :** {frais_annexes:,.2f} DZD")
                st.write(f"**Total Estimé :** {total_dzd:,.2f} DZD")
            else:
                st.markdown("**بالدينار الجزائري:**")
                st.write(f"**السعر شامل الضريبة (TTC) :** {price_ttc:,.2f} دينار جزائري")
                st.write(f"**حقوق الجمارك ({droits_douane_taux}%):** {droits_douane:,.2f} دينار جزائري")
                st.write(f"**ضريبة القيمة المضافة ({TVA_TAUX}%):** {TVA:,.2f} دينار جزائري")
                st.write(f"**ضريبة أخرى ({TIC_TAUX}%):** {TIC:,.2f} دينار جزائري")
                st.write(f"**الرسوم الإضافية :** {frais_annexes:,.2f} دينار جزائري")
                st.write(f"**الإجمالي المقدر :** {total_dzd:,.2f} دينار جزائري")

        with col2:
            if language == "French":
                st.markdown("**En EUR:**")
                st.write(f"**Prix TTC :** {price_ttc / conversion_rate:,.2f} EUR")
                st.write(f"**Droits de Douane ({droits_douane_taux}%):** {droits_douane_eur:,.2f} EUR")
                st.write(f"**TVA ({TVA_TAUX}%):** {TVA_eur:,.2f} EUR")
                st.write(f"**TIC ({TIC_TAUX}%):** {TIC_eur:,.2f} EUR")
                st.write(f"**Frais Annexes :** {frais_annexes_eur:,.2f} EUR")
                st.write(f"**Total Estimé :** {total_eur:,.2f} EUR")
            else:
                st.markdown("**باليورو:**")
                st.write(f"**السعر شامل الضريبة (TTC) :** {price_ttc / conversion_rate:,.2f} يورو")
                st.write(f"**حقوق الجمارك ({droits_douane_taux}%):** {droits_douane_eur:,.2f} يورو")
                st.write(f"**ضريبة القيمة المضافة ({TVA_TAUX}%):** {TVA_eur:,.2f} يورو")
                st.write(f"**ضريبة أخرى ({TIC_TAUX}%):** {TIC_eur:,.2f} يورو")
                st.write(f"**الرسوم الإضافية :** {frais_annexes_eur:,.2f} يورو")
                st.write(f"**الإجمالي المقدر :** {total_eur:,.2f} يورو")

# **Onglet 3 : Revente & Bénéfice**
with tabs[2]:
    st.header("Calcul du Bénéfice de Revente" if language == "French" else "حساب الفائدة من إعادة البيع")

    # Aligner les deux champs côte à côte
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
                    resale_price_eur = st.number_input("Prix de revente (en EUR)", min_value=0.0, value=1000.0, step=100.0, key="resale_eur")
                    resale_price_dzd = resale_price_eur * conversion_rate
                else:
                    resale_price_dzd = st.number_input("Prix de revente (en DZD)", min_value=0.0, value=1500000.0, step=10000.0, key="resale_dzd")
                    resale_price_eur = resale_price_dzd / conversion_rate if conversion_rate != 0 else 0
            else:
                if resale_price_currency == "يورو":
                    resale_price_eur = st.number_input("سعر إعادة البيع (باليورو)", min_value=0.0, value=1000.0, step=100.0, key="resale_eur_ar")
                    resale_price_dzd = resale_price_eur * conversion_rate
                else:
                    resale_price_dzd = st.number_input("سعر إعادة البيع (بالدينار الجزائري)", min_value=0.0, value=1500000.0, step=10000.0, key="resale_dzd_ar")
                    resale_price_eur = resale_price_dzd / conversion_rate if conversion_rate != 0 else 0

    # Affichage des prix de revente
    st.markdown(f"**Prix de revente en DZD :** {resale_price_dzd:,.2f} DZD / {resale_price_eur:,.2f} EUR")

    # Calcul du bénéfice
    benefit_dzd = resale_price_dzd - total_dzd
    benefit_eur = benefit_dzd / conversion_rate if conversion_rate != 0 else 0

    if benefit_dzd >= 0:
        st.success(f"{texts['benefit_label']}: {benefit_dzd:,.2f} DZD / {benefit_eur:,.2f} EUR")
    else:
        st.warning(f"{texts['benefit_label']}: {benefit_dzd:,.2f} DZD / {benefit_eur:,.2f} EUR")

# **Onglet 4 : Résumé & Rapport**
with tabs[3]:
    st.subheader(texts["summary_header"])

    # Affichage des données sous forme de tableau
    summary_data = {
        "Description": [
            f"Prix TTC" if language == "French" else "السعر شامل الضريبة (TTC)",
            f"Droits de Douane ({droits_douane_taux}%)",
            f"TVA ({TVA_TAUX}%)",
            f"TIC ({TIC_TAUX}%)",
            "Frais Annexes" if language == "French" else "الرسوم الإضافية",
            f"Total Estimé" if language == "French" else "الإجمالي المقدر",
            f"Prix de Revente",
            f"Bénéfice Potentiel" if language == "French" else "الفائدة المحتملة"
        ],
        "En DZD": [
            f"{price_ttc:,.2f}",
            f"{droits_douane:,.2f}",
            f"{TVA:,.2f}",
            f"{TIC:,.2f}",
            f"{frais_annexes:,.2f}",
            f"{total_dzd:,.2f}",
            f"{resale_price_dzd:,.2f}",
            f"{benefit_dzd:,.2f}"
        ],
        "En EUR": [
            f"{price_ttc / conversion_rate:,.2f}",
            f"{droits_douane_eur:,.2f}",
            f"{TVA_eur:,.2f}",
            f"{TIC_eur:,.2f}",
            f"{frais_annexes_eur:,.2f}",
            f"{total_eur:,.2f}",
            f"{resale_price_eur:,.2f}",
            f"{benefit_eur:,.2f}"
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

    # Téléchargement du Rapport en PDF
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
                    "Description": [
                        f"Prix TTC" if language == "French" else "السعر شامل الضريبة (TTC)",
                        f"Droits de Douane ({droits_douane_taux}%)",
                        f"TVA ({TVA_TAUX}%)",
                        f"TIC ({TIC_TAUX}%)",
                        "Frais Annexes" if language == "French" else "الرسوم الإضافية",
                        f"Total Estimé" if language == "French" else "الإجمالي المقدر"
                    ],
                    "En DZD": [
                        f"{price_ttc:,.2f}",
                        f"{droits_douane:,.2f}",
                        f"{TVA:,.2f}",
                        f"{TIC:,.2f}",
                        f"{frais_annexes:,.2f}",
                        f"{total_dzd:,.2f}"
                    ],
                    "En EUR": [
                        f"{price_ttc / conversion_rate:,.2f}",
                        f"{droits_douane_eur:,.2f}",
                        f"{TVA_eur:,.2f}",
                        f"{TIC_eur:,.2f}",
                        f"{frais_annexes_eur:,.2f}",
                        f"{total_eur:,.2f}"
                    ]
                }
                costs_df = pd.DataFrame(costs_data)
                pdf.add_table(costs_df, "Coûts et Taxes" if language == "French" else "التكاليف والضرائب")

                # Ajouter un chapitre pour le bénéfice de revente
                pdf.chapter_title("Calcul du Bénéfice de Revente" if language == "French" else "حساب الفائدة من إعادة البيع")
                benefit_info = f"""
                **Prix de Revente :** {resale_price_dzd:,.2f} DZD / {resale_price_eur:,.2f} EUR
                **Bénéfice Potentiel :** {benefit_dzd:,.2f} DZD / {benefit_eur:,.2f} EUR
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
