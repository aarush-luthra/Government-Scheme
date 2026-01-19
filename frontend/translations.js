/**
 * Pre-translated static strings for instant language switching
 * Languages: English (base), Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Odia, Assamese, Urdu, Kashmiri, Maithili
 */
const TRANSLATIONS = {
    // English is the base - we keep original values in HTML
    "en_XX": null, // Use originals

    "hi_IN": {
        // App & Navigation
        "app_title": "सरकारी योजना सहायक",

        "logo-text": "सरकारी योजना सहायक",

        "signin": "साइन इन →",

        "logout": "लॉग आउट",

        "edit_profile": "प्रोफ़ाइल संपादित करें",

        "status-online": "ऑनलाइन",


        // Hero Section
        "hero-badge": "सुरक्षित, सरल, निर्बाध",

        "hero-accent": "फास्ट-ट्रैक",

        "hero-title": "सरकारी लाभ<br>प्राप्त करें",

        "cta-btn": "योजनाएं देखें",

        "skip-btn": "अतिथि के रूप में जारी रखें →",


        // Quick Start Card
        "tab_new": "नया उपयोगकर्ता",

        "tab_signin": "साइन इन",

        "quick_lang": "आपकी भाषा",

        "quick_state": "आपका राज्य",

        "quick_all_india": "संपूर्ण भारत",

        "quick_explore": "योजनाएं खोजें",


        // Statistics
        "stat_schemes": "५००+",

        "stat_schemes_label": "उपलब्ध योजनाएं",

        "stat_serving": "AI-संचालित",

        "stat_serving_label": "सहायता",

        "stat_languages": "१५+",

        "stat_languages_label": "समर्थित भाषाएं",


        // Chat Page
        "chat_welcome_title": "सरकारी योजना सहायक में आपका स्वागत है",

        "chat_welcome_desc": "मैं आपकी पसंदीदा भाषा में भारतीय सरकारी योजनाओं की पात्रता, लाभ और आवेदन प्रक्रिया को समझने में मदद कर सकता हूं।",

        "chat_limit_msg": "३ मुफ्त संदेश शेष",

        "chat_input_placeholder": "अपना संदेश टाइप करें...",


        // Auth Modal
        "signin-title": "वापस स्वागत है",

        "signin-subtitle": "चैट जारी रखने के लिए साइन इन करें",

        "signin-email": "ईमेल पता",

        "signin-btn": "साइन इन →",

        "signin-loading": "साइन इन हो रहा है...",

        "auth_lbl_password": "पासवर्ड",

        "auth_pl_password": "अपना पासवर्ड दर्ज करें",

        "auth_msg_no_account": "खाता नहीं है?",

        "auth_link_signup": "साइन अप करें",

        "auth-prompt-message": "चैट जारी रखने के लिए साइन इन या खाता बनाएं",

        "forgot-password": "पासवर्ड भूल गए?",


        // Scheme Finder Modal
        "sf_modal_title": "आपके लिए सर्वोत्तम योजनाएं खोजने में हमारी मदद करें",

        "sf_h_account": "अपना खाता बनाएं",

        "sf_msg_have_account": "पहले से खाता है?",

        "sf_link_signin": "साइन इन करें",

        "sf_lbl_name": "पूरा नाम",

        "sf_pl_name": "अपना नाम दर्ज करें",

        "sf_lbl_email": "ईमेल पता",

        "sf_pl_email": "you@example.com",

        "sf_lbl_pass": "पासवर्ड",

        "sf_pl_pass": "कम से कम 6 अक्षर",

        "sf_h_about": "आपके बारे में",

        "sf_lbl_gender": "लिंग",

        "sf_opt_male": "पुरुष",

        "sf_opt_female": "महिला",

        "sf_opt_trans": "ट्रांसजेंडर",

        "sf_lbl_age": "आयु",

        "sf_opt_sel_age": "आयु चुनें",

        "sf_h_loc": "स्थान",

        "sf_lbl_state": "राज्य",

        "sf_opt_sel_state": "राज्य चुनें",

        "sf_lbl_area": "क्षेत्र प्रकार",

        "sf_opt_urban": "शहरी",

        "sf_opt_rural": "ग्रामीण",

        "sf_h_social": "सामाजिक विवरण",

        "sf_lbl_cat": "श्रेणी",

        "sf_cat_gen": "सामान्य",

        "sf_cat_obc": "ओबीसी",

        "sf_cat_pvtg": "पीवीटीजी",

        "sf_cat_sc": "एससी",

        "sf_cat_st": "एसटी",

        "sf_cat_dnt": "डीएनटी",

        "sf_lbl_pwd": "विकलांग व्यक्ति?",

        "sf_opt_yes": "हां",

        "sf_opt_no": "नहीं",

        "sf_lbl_minor": "अल्पसंख्यक?",

        "sf_h_emp": "रोजगार और शिक्षा",

        "sf_lbl_student": "छात्र?",

        "sf_lbl_status": "रोजगार स्थिति",

        "sf_emp_emp": "नौकरीपेशा",

        "sf_emp_unemp": "बेरोजगार",

        "sf_emp_self": "स्व-रोजगार",

        "sf_lbl_govt": "सरकारी कर्मचारी?",

        "sf_h_income": "आय विवरण",

        "sf_lbl_inc_ann": "वार्षिक आय (₹)",

        "sf_lbl_inc_fam": "पारिवारिक आय (₹)",

        "sf_pl_zero": "0",

        "sf_submit_btn": "प्रोफ़ाइल सबमिट करें और चैट शुरू करें",

        "sf_loading": "आपकी प्रोफ़ाइल सेट हो रही है...",

        "user-name-display": "",
        "features_title": "प्रमुख विशेषताएं",

        "feature_secure_profile": "सुरक्षित प्रोफ़ाइल",

        "feature_secure_desc": "अपने उपयोगकर्ता प्रोफ़ाइल की पहचान सुरक्षित करें, और प्रोफ़ाइल लाभ सुरक्षित करें।",

        "feature_direct_benefit": "प्रत्यक्ष लाभ हस्तांतरण",

        "feature_direct_desc": "प्रत्यक्ष लाभ हस्तांतरण सूचना लाभ।",

        "feature_multilingual": "बहुभाषी",

        "feature_multilingual_desc": "अनुकूलन और लेनदेन उत्तर में सर्वोत्तम बहुभाषी क्षमताएं।",

        "feature_personalized": "व्यक्तिगत",

        "feature_personalized_desc": "अपनी पहचान और प्रोफ़ाइल लाभों को सुरक्षित करें",

        "featured_title": "विशेष योजनाएं",

        "scheme_agriculture": "कृषि एवं ग्रामीण क्षेत्र",

        "scheme_agriculture_count": "८१८ योजनाएं",

        "scheme_banking": "बैंकिंग और वित्त",

        "scheme_banking_count": "३१७ योजनाएं",

        "scheme_business": "व्यापार",

        "scheme_business_count": "७०५ योजनाएं",

        "scheme_education": "शिक्षा",

        "scheme_education_count": "१०७६ योजनाएं",

        "scheme_health": "स्वास्थ्य",

        "scheme_health_count": "२७४ योजनाएं",

        "scheme_housing": "आवास",

        "scheme_housing_count": "१२८ योजनाएं",

        "scheme_public_safety": "सार्वजनिक सुरक्षा",

        "scheme_public_safety_count": "२९ योजनाएं",

        "scheme_science": "विज्ञान और सूचना प्रौद्योगिकी",

        "scheme_science_count": "१०० योजनाएं",

        "scheme_skills": "कौशल",

        "scheme_skills_count": "३६८ योजनाएं",

        "scheme_social_welfare": "सामाजिक कल्याण",

        "scheme_social_welfare_count": "१४५६ योजनाएं",

        "scheme_sports": "खेल",

        "scheme_sports_count": "२४८ योजनाएं",

        "scheme_transport": "परिवहन",

        "scheme_transport_count": "८६ योजनाएं",

        "scheme_travel": "यात्रा",

        "scheme_travel_count": "९१ योजनाएं",

        "scheme_utility": "उपयोगिता",

        "scheme_utility_count": "५८ योजनाएं",

        "scheme_women": "महिला और बच्चा",

        "scheme_women_count": "४५८ योजनाएं",

        "how_title": "यह कैसे काम करता है",

        "step1_title": "अपनी जानकारी दें",

        "step2_title": "व्यक्तिगत योजनाएं प्राप्त करें",

        "step3_title": "योजना के लाभ",

        "hero-signup": "साइन अप करें",

        "hero-continue": "अतिथि बने रहें",

        "stat_ai": "एआई",

        "stat_ai_label": "विद्युत",

        "stat_languages_new": "१२+",

        "stat_languages_interactive": "भाषाएँ, इंटरएक्टिव",


        // New button translations for hi_IN
        "nav_signin": "साइन इन करें",

        "start_chatting": "चैट शुरू करें",

        "greeting_hello": "हैलो .",

        // Verification Modal translations
        "verify_title": "अपने विवरण सत्यापित करें",
        "verify_subtitle": "क्या आप अपनी दर्ज जानकारी को सत्यापित करने के लिए एक दस्तावेज़ स्कैन करना चाहेंगे?",
        "verify_scan_btn": "सत्यापित करने के लिए दस्तावेज़ स्कैन करें",
        "verify_process_btn": "दस्तावेज़ प्रोसेस करें",
        "verify_processing": "दस्तावेज़ स्कैन हो रहा है...",
        "verify_comparison_title": "तुलना परिणाम",
        "verify_field": "फ़ील्ड",
        "verify_entered": "दर्ज किया गया",
        "verify_scanned": "स्कैन किया गया",
        "verify_skip": "सत्यापन छोड़ें",

        // Quick Action Button translations
        "qa_label": "त्वरित कार्रवाई:",
        "qa_find_schemes": "मेरी योजनाएं खोजें",
        "qa_browse_categories": "श्रेणियां देखें",
        "qa_help": "सहायता",
        "qa_more_about": "अधिक जानें",
        "qa_more_schemes": "अधिक योजनाएं",
        "qa_how_to_apply": "आवेदन कैसे करें",

    },

    "ta_IN": {
        "app_title": "அரசு திட்ட உதவியாளர்",

        "logo-text": "அரசு திட்ட உதவியாளர்",

        "signin": "உள்நுழையவும் →",

        "logout": "வெளியேறு",

        "edit_profile": "சுயவிவரத்தை திருத்து",

        "status-online": "ஆன்லைன்",

        "hero-badge": "பாதுகாப்பான, எளிமையான, தடையற்ற",

        "hero-accent": "விரைவு-பாதை",

        "hero-title": "அரசு நலன்கள்\<br>பெறுங்கள்",

        "cta-btn": "திட்டங்களை ஆராயுங்கள்",

        "skip-btn": "விருந்தினராக தொடரவும் →",

        "tab_new": "புதிய பயனர்",

        "tab_signin": "உள்நுழைய",

        "quick_lang": "உங்கள் மொழி",

        "quick_state": "உங்கள் மாநிலம்",

        "quick_all_india": "அனைத்து இந்தியா",

        "quick_explore": "திட்டங்களை ஆராயுங்கள்",

        "stat_schemes": "௫௦௦+",

        "stat_schemes_label": "திட்டங்கள் கிடைக்கும்",

        "stat_serving": "AI-இயக்கப்படும்",

        "stat_serving_label": "உதவி",

        "stat_languages": "௧௫+",

        "stat_languages_label": "ஆதரிக்கப்படும் மொழிகள்",

        "chat_welcome_title": "அரசு திட்ட உதவியாளருக்கு வரவேற்கிறோம்",

        "chat_welcome_desc": "உங்கள் விருப்பமான மொழியில் இந்திய அரசு திட்டங்கள், தகுதி, நன்மைகள் மற்றும் விண்ணப்ப செயல்முறையை புரிந்துகொள்ள நான் உதவ முடியும்.",

        "chat_limit_msg": "௩ இலவச செய்திகள் மீதமுள்ளன",

        "chat_input_placeholder": "உங்கள் செய்தியை தட்டச்சு செய்யவும்...",

        "signin-title": "மீண்டும் வரவேற்கிறோம்",

        "signin-subtitle": "அரட்டையை தொடர உள்நுழையவும்",

        "signin-email": "மின்னஞ்சல் முகவரி",

        "signin-btn": "உள்நுழையவும் →",

        "signin-loading": "உள்நுழைகிறது...",

        "auth_lbl_password": "கடவுச்சொல்",

        "auth_pl_password": "உங்கள் கடவுச்சொல்லை உள்ளிடவும்",

        "auth_msg_no_account": "கணக்கு இல்லையா?",

        "auth_link_signup": "பதிவு செய்யுங்கள்",

        "auth-prompt-message": "தொடர உள்நுழையவும் அல்லது கணக்கை உருவாக்கவும்",

        "forgot-password": "கடவுச்சொல் மறந்துவிட்டதா?",

        "sf_modal_title": "உங்களுக்கு சிறந்த திட்டங்களை கண்டறிய உதவுங்கள்",

        "sf_h_account": "உங்கள் கணக்கை உருவாக்கவும்",

        "sf_msg_have_account": "ஏற்கனவே கணக்கு உள்ளதா?",

        "sf_link_signin": "உள்நுழையவும்",

        "sf_lbl_name": "முழு பெயர்",

        "sf_pl_name": "உங்கள் பெயரை உள்ளிடவும்",

        "sf_lbl_email": "மின்னஞ்சல் முகவரி",

        "sf_pl_email": "you@example.com",

        "sf_lbl_pass": "கடவுச்சொல்",

        "sf_pl_pass": "குறைந்தது 6 எழுத்துக்கள்",

        "sf_h_about": "உங்களைப் பற்றி",

        "sf_lbl_gender": "பாலினம்",

        "sf_opt_male": "ஆண்",

        "sf_opt_female": "பெண்",

        "sf_opt_trans": "திருநங்கை",

        "sf_lbl_age": "வயது",

        "sf_opt_sel_age": "வயதைத் தேர்ந்தெடுக்கவும்",

        "sf_h_loc": "இடம்",

        "sf_lbl_state": "மாநிலம்",

        "sf_opt_sel_state": "மாநிலத்தைத் தேர்ந்தெடுக்கவும்",

        "sf_lbl_area": "பகுதி வகை",

        "sf_opt_urban": "நகர்ப்புற",

        "sf_opt_rural": "கிராமப்புற",

        "sf_h_social": "சமூக விவரங்கள்",

        "sf_lbl_cat": "பிரிவு",

        "sf_cat_gen": "பொது",

        "sf_cat_obc": "ஓபிசி",

        "sf_cat_pvtg": "பிவிடிஜி",

        "sf_cat_sc": "எஸ்சி",

        "sf_cat_st": "எஸ்டி",

        "sf_cat_dnt": "டிஎன்டி",

        "sf_lbl_pwd": "மாற்றுத்திறனாளியா?",

        "sf_opt_yes": "ஆம்",

        "sf_opt_no": "இல்லை",

        "sf_lbl_minor": "சிறுபான்மையினரா?",

        "sf_h_emp": "வேலைவாய்ப்பு மற்றும் கல்வி",

        "sf_lbl_student": "மாணவரா?",

        "sf_lbl_status": "வேலைவாய்ப்பு நிலை",

        "sf_emp_emp": "வேலையில் உள்ளவர்",

        "sf_emp_unemp": "வேலையில்லாதவர்",

        "sf_emp_self": "சுயதொழில்",

        "sf_lbl_govt": "அரசு ஊழியரா?",

        "sf_h_income": "வருமான விவரங்கள்",

        "sf_lbl_inc_ann": "ஆண்டு வருமானம் (₹)",

        "sf_lbl_inc_fam": "குடும்ப வருமானம் (₹)",

        "sf_pl_zero": "0",

        "sf_submit_btn": "சுயவிவரத்தை சமர்ப்பித்து அரட்டையைத் தொடங்கு",

        "sf_loading": "உங்கள் சுயவிவரம் அமைக்கப்படுகிறது...",

        "user-name-display": "",
        "features_title": "முக்கிய அம்சங்கள்",

        "feature_secure_profile": "பாதுகாப்பான சுயவிவரம்",

        "feature_secure_desc": "உங்கள் பயனரின் சுயவிவர அடையாளத்தை பாதுகாக்கவும், சுயவிவர நன்மைகளை பாதுகாக்கவும்.",

        "feature_direct_benefit": "நேரடி நன்மைகள் பரிமாற்றம்",

        "feature_direct_desc": "நேரடி நன்மைகள் பரிமாற்றம் மற்றும் தகவல் நன்மைகள்.",

        "feature_multilingual": "பலமொழிகள்",

        "feature_multilingual_desc": "ஏற்றுக்கொள்ளும் மற்றும் பரிவர்த்தனைகளுக்கு பதிலளிக்க சிறந்த பலமொழி திறன்கள்.",

        "feature_personalized": "தனிப்பட்ட முறையில்",

        "feature_personalized_desc": "உங்கள் அடையாளம் மற்றும் சுயவிவர நன்மைகளை பாதுகாக்கவும்",

        "featured_title": "சிறப்புத் திட்டங்கள்",

        "scheme_agriculture": "வேளாண்மை & கிராமப்புறங்கள்",

        "scheme_agriculture_count": "௮௧௮ திட்டங்கள்",

        "scheme_banking": "வங்கி மற்றும் நிதி",

        "scheme_banking_count": "௩௧௭ திட்டங்கள்",

        "scheme_business": "வணிகம்",

        "scheme_business_count": "௭௦௫ திட்டங்கள்",

        "scheme_education": "கல்வி",

        "scheme_education_count": "௧௦௭௬ திட்டங்கள்",

        "scheme_health": "சுகாதாரம்",

        "scheme_health_count": "௨௭௪ திட்டங்கள்",

        "scheme_housing": "குடியிருப்பு",

        "scheme_housing_count": "௧௨௮ திட்டங்கள்",

        "scheme_public_safety": "பொதுமக்கள் பாதுகாப்பு",

        "scheme_public_safety_count": "௨௯ திட்டங்கள்",

        "scheme_science": "அறிவியல் & தகவல் தொழில்நுட்பம்",

        "scheme_science_count": "௧௦௦ திட்டங்கள்",

        "scheme_skills": "திறன்கள்",

        "scheme_skills_count": "௩௬௮ திட்டங்கள்",

        "scheme_social_welfare": "சமூக நலன்",

        "scheme_social_welfare_count": "௧௪௫௬ திட்டங்கள்",

        "scheme_sports": "விளையாட்டு",

        "scheme_sports_count": "௨௪௮ திட்டங்கள்",

        "scheme_transport": "போக்குவரத்து",

        "scheme_transport_count": "௮௬ திட்டங்கள்",

        "scheme_travel": "பயணம்",

        "scheme_travel_count": "௯௧ திட்டங்கள்",

        "scheme_utility": "பயன்பாடு",

        "scheme_utility_count": "௫௮ திட்டங்கள்",

        "scheme_women": "பெண்கள் & குழந்தை",

        "scheme_women_count": "௪௫௮ திட்டங்கள்",

        "how_title": "அது எவ்வாறு செயல்படுகிறது",

        "step1_title": "உங்கள் தகவலைத் தரவும்",

        "step2_title": "தனிப்பயனாக்கப்பட்ட திட்டங்களைப் பெறுங்கள்",

        "step3_title": "இத்திட்டத்தின் நன்மைகள்",

        "hero-signup": "பதிவு செய்யுங்கள்",

        "hero-continue": "விருந்தினராக தொடருங்கள்",

        "stat_ai": "AI",

        "stat_ai_label": "மின்சாரம்",

        "stat_languages_new": "௧௨+",

        "stat_languages_interactive": "மொழிகள், ஊடாடும்",


        // New button translations for ta_IN
        "nav_signin": "பதிவு செய்யவும்",

        "start_chatting": "உரையாடலைத் தொடங்கவும்",

        "greeting_hello": "வணக்கம் .",

    },

    "te_IN": {
        "app_title": "ప్రభుత్వ పథకం సహాయకుడు",

        "logo-text": "ప్రభుత్వ పథకం సహాయకుడు",

        "signin": "సైన్ ఇన్ →",

        "logout": "లాగ్ అవుట్",

        "edit_profile": "ప్రొఫైల్ సవరించు",

        "status-online": "ఆన్‌లైన్",

        "hero-badge": "సురక్షితమైన, సులభమైన, అతుకులు లేని",

        "hero-accent": "ఫాస్ట్-ట్రాక్",

        "hero-title": "ప్రభుత్వ ప్రయోజనాలు\<br>పొందండి",

        "cta-btn": "పథకాలను అన్వేషించండి",

        "skip-btn": "అతిథిగా కొనసాగించు →",

        "tab_new": "కొత్త వాడుకరి",

        "tab_signin": "సైన్ ఇన్",

        "quick_lang": "మీ భాష",

        "quick_state": "మీ రాష్ట్రం",

        "quick_all_india": "మొత్తం భారతదేశం",

        "quick_explore": "పథకాలను అన్వేషించండి",

        "stat_schemes": "౫౦౦+",

        "stat_schemes_label": "అందుబాటులో ఉన్న పథకాలు",

        "stat_serving": "AI-ఆధారిత",

        "stat_serving_label": "సహాయం",

        "stat_languages": "౧౫+",

        "stat_languages_label": "మద్దతు భాషలు",

        "chat_welcome_title": "ప్రభుత్వ పథకం సహాయకుడికి స్వాగతం",

        "chat_welcome_desc": "మీకు ఇష్టమైన భాషలో భారత ప్రభుత్వ పథకాలు, అర్హత, ప్రయోజనాలు మరియు దరఖాస్తు ప్రక్రియను అర్థం చేసుకోవడంలో నేను సహాయం చేయగలను.",

        "chat_limit_msg": "౩ ఉచిత సందేశాలు మిగిలి ఉన్నాయి",

        "chat_input_placeholder": "మీ సందేశాన్ని టైప్ చేయండి...",

        "signin-title": "తిరిగి స్వాగతం",

        "signin-subtitle": "చాట్ కొనసాగించడానికి సైన్ ఇన్ చేయండి",

        "signin-email": "ఇమెయిల్ చిరునామా",

        "signin-btn": "సైన్ ఇన్ →",

        "signin-loading": "సైన్ ఇన్ అవుతోంది...",

        "auth_lbl_password": "పాస్‌వర్డ్",

        "auth_pl_password": "మీ పాస్‌వర్డ్ నమోదు చేయండి",

        "auth_msg_no_account": "ఖాతా లేదా?",

        "auth_link_signup": "సైన్ అప్ చేయండి",

        "auth-prompt-message": "కొనసాగించడానికి సైన్ ఇన్ చేయండి లేదా ఖాతా సృష్టించండి",

        "forgot-password": "పాస్‌వర్డ్ మర్చిపోయారా?",

        "sf_modal_title": "మీకు ఉత్తమ పథకాలను కనుగొనడంలో మాకు సహాయం చేయండి",

        "sf_h_account": "మీ ఖాతాను సృష్టించండి",

        "sf_msg_have_account": "ఇప్పటికే ఖాతా ఉందా?",

        "sf_link_signin": "సైన్ ఇన్ చేయండి",

        "sf_lbl_name": "పూర్తి పేరు",

        "sf_pl_name": "మీ పేరు నమోదు చేయండి",

        "sf_lbl_email": "ఇమెయిల్ చిరునామా",

        "sf_pl_email": "you@example.com",

        "sf_lbl_pass": "పాస్‌వర్డ్",

        "sf_pl_pass": "కనీసం 6 అక్షరాలు",

        "sf_h_about": "మీ గురించి",

        "sf_lbl_gender": "లింగం",

        "sf_opt_male": "పురుషుడు",

        "sf_opt_female": "స్త్రీ",

        "sf_opt_trans": "ట్రాన్స్‌జెండర్",

        "sf_lbl_age": "వయస్సు",

        "sf_opt_sel_age": "వయస్సు ఎంచుకోండి",

        "sf_h_loc": "స్థానం",

        "sf_lbl_state": "రాష్ట్రం",

        "sf_opt_sel_state": "రాష్ట్రం ఎంచుకోండి",

        "sf_lbl_area": "ప్రాంత రకం",

        "sf_opt_urban": "పట్టణ",

        "sf_opt_rural": "గ్రామీణ",

        "sf_h_social": "సామాజిక వివరాలు",

        "sf_lbl_cat": "వర్గం",

        "sf_cat_gen": "సాధారణ",

        "sf_cat_obc": "ఓబీసీ",

        "sf_cat_pvtg": "పీవీటీజీ",

        "sf_cat_sc": "ఎస్సీ",

        "sf_cat_st": "ఎస్టీ",

        "sf_cat_dnt": "డీఎన్‌టీ",

        "sf_lbl_pwd": "వికలాంగులా?",

        "sf_opt_yes": "అవును",

        "sf_opt_no": "కాదు",

        "sf_lbl_minor": "మైనారిటీయా?",

        "sf_h_emp": "ఉపాధి మరియు విద్య",

        "sf_lbl_student": "విద్యార్థా?",

        "sf_lbl_status": "ఉపాధి స్థితి",

        "sf_emp_emp": "ఉద్యోగం చేస్తున్నారు",

        "sf_emp_unemp": "నిరుద్యోగి",

        "sf_emp_self": "స్వయం ఉపాధి",

        "sf_lbl_govt": "ప్రభుత్వ ఉద్యోగా?",

        "sf_h_income": "ఆదాయ వివరాలు",

        "sf_lbl_inc_ann": "వార్షిక ఆదాయం (₹)",

        "sf_lbl_inc_fam": "కుటుంబ ఆదాయం (₹)",

        "sf_pl_zero": "0",

        "sf_submit_btn": "ప్రొఫైల్ సమర్పించి చాట్ ప్రారంభించు",

        "sf_loading": "మీ ప్రొఫైల్ సెట్ చేయబడుతోంది...",

        "user-name-display": "",
        "features_title": "ముఖ్య లక్షణాలు",

        "feature_secure_profile": "సురక్షిత ప్రొఫైల్",

        "feature_secure_desc": "మీ వినియోగదారు ప్రొఫైల్ గుర్తింపును భద్రపరచండి, మరియు ప్రొఫైల్ ప్రయోజనాలను భద్రపరచండి.",

        "feature_direct_benefit": "ప్రత్యక్ష ప్రయోజన బదిలీ",

        "feature_direct_desc": "ప్రత్యక్ష ప్రయోజన బదిలీ అనధికారిక సమాచార ప్రయోజనం.",

        "feature_multilingual": "బహుభాషా",

        "feature_multilingual_desc": "స్వీకరణ మరియు లావాదేవీల కోసం ఉత్తమమైన బహుభాషా సామర్థ్యాలు.",

        "feature_personalized": "వ్యక్తిగతీకరించబడింది",

        "feature_personalized_desc": "మీ గుర్తింపు మరియు ప్రొఫైల్ ప్రయోజనాలను భద్రపరచండి",

        "featured_title": "ప్రత్యేకమైన పథకాలు",

        "scheme_agriculture": "వ్యవసాయం & గ్రామీణ రంగం",

        "scheme_agriculture_count": "౮౧౮ పథకాలు",

        "scheme_banking": "బ్యాంకింగ్ & ఫైనాన్స్",

        "scheme_banking_count": "౩౧౭ పథకాలు",

        "scheme_business": "వ్యాపారం",

        "scheme_business_count": "౭౦౫ పథకాలు",

        "scheme_education": "విద్య",

        "scheme_education_count": "౧౦౭౬ పథకాలు",

        "scheme_health": "ఆరోగ్యం",

        "scheme_health_count": "౨౭౪ పథకాలు",

        "scheme_housing": "నివాసం",

        "scheme_housing_count": "౧౨౮ పథకాలు",

        "scheme_public_safety": "ప్రజా భద్రత",

        "scheme_public_safety_count": "౨౯ పథకాలు",

        "scheme_science": "సైన్స్ & ఐటి",

        "scheme_science_count": "౧౦౦ పథకాలు",

        "scheme_skills": "నైపుణ్యాలు",

        "scheme_skills_count": "౩౬౮ పథకాలు",

        "scheme_social_welfare": "సామాజిక సంక్షేమం",

        "scheme_social_welfare_count": "౧౪౫౬ పథకాలు",

        "scheme_sports": "క్రీడలు",

        "scheme_sports_count": "౨౪౮ పథకాలు",

        "scheme_transport": "రవాణా",

        "scheme_transport_count": "౮౬ పథకాలు",

        "scheme_travel": "ప్రయాణం",

        "scheme_travel_count": "౯౧ పథకాలు",

        "scheme_utility": "వినియోగం",

        "scheme_utility_count": "౫౮ పథకాలు",

        "scheme_women": "మహిళలు & పిల్లలు",

        "scheme_women_count": "౪౫౮ పథకాలు",

        "how_title": "ఇది ఎలా పనిచేస్తుంది",

        "step1_title": "మీ సమాచారం ఇవ్వండి",

        "step2_title": "వ్యక్తిగతీకరించిన ప్రణాళికలను పొందండి",

        "step3_title": "ఈ పథకం వల్ల లభించే ప్రయోజనాలు",

        "hero-signup": "సైన్ అప్ చేయండి",

        "hero-continue": "అతిథిగా కొనసాగండి",

        "stat_ai": "AI",

        "stat_ai_label": "శక్తితో",

        "stat_languages_new": "౧౨+",

        "stat_languages_interactive": "భాషలు, పరస్పర చర్య",


        // New button translations for te_IN
        "nav_signin": "సైన్ ఇన్ చేయండి",

        "start_chatting": "చాటింగ్ ప్రారంభించండి",

        "greeting_hello": "హలో .",

    },

    "bn_IN": {
        "app_title": "সরকারি প্রকল্প সহায়ক",

        "logo-text": "সরকারি প্রকল্প সহায়ক",

        "signin": "সাইন ইন →",

        "logout": "লগ আউট",

        "edit_profile": "প্রোফাইল সম্পাদনা করুন",

        "status-online": "অনলাইন",

        "hero-badge": "নিরাপদ, সহজ, নির্বিঘ্ন",

        "hero-accent": "দ্রুত-ট্র্যাক",

        "hero-title": "সরকারি সুবিধা\<br>প্রাপ্য",

        "cta-btn": "প্রকল্পগুলি অন্বেষণ করুন",

        "skip-btn": "অতিথি হিসাবে চালিয়ে যান →",

        "tab_new": "নতুন ব্যবহারকারী",

        "tab_signin": "সাইন ইন",

        "quick_lang": "আপনার ভাষা",

        "quick_state": "আপনার রাজ্য",

        "quick_all_india": "সমগ্র ভারত",

        "quick_explore": "প্রকল্প অন্বেষণ",

        "stat_schemes": "৫০০+",

        "stat_schemes_label": "উপলব্ধ প্রকল্প",

        "stat_serving": "AI-চালিত",

        "stat_serving_label": "সহায়তা",

        "stat_languages": "১৫+",

        "stat_languages_label": "সমর্থিত ভাষা",

        "chat_welcome_title": "সরকারি প্রকল্প সহায়কে স্বাগতম",

        "chat_welcome_desc": "আপনার পছন্দের ভাষায় ভারতীয় সরকারি প্রকল্প, যোগ্যতা, সুবিধা এবং আবেদন প্রক্রিয়া বুঝতে আমি আপনাকে সাহায্য করতে পারি।",

        "chat_limit_msg": "৩টি বিনামূল্যে বার্তা অবশিষ্ট",

        "chat_input_placeholder": "আপনার বার্তা টাইপ করুন...",

        "signin-title": "স্বাগতম",

        "signin-subtitle": "চ্যাট চালিয়ে যেতে সাইন ইন করুন",

        "signin-email": "ইমেল ঠিকানা",

        "signin-btn": "সাইন ইন →",

        "signin-loading": "সাইন ইন হচ্ছে...",

        "auth_lbl_password": "পাসওয়ার্ড",

        "auth_pl_password": "আপনার পাসওয়ার্ড লিখুন",

        "auth_msg_no_account": "একাউন্ট নেই?",

        "auth_link_signup": "সাইন আপ করুন",

        "auth-prompt-message": "চালিয়ে যেতে সাইন ইন বা একাউন্ট তৈরি করুন",

        "forgot-password": "পাসওয়ার্ড ভুলে গেছেন?",

        "sf_modal_title": "আপনার জন্য সেরা প্রকল্প খুঁজে পেতে আমাদের সাহায্য করুন",

        "sf_h_account": "আপনার একাউন্ট তৈরি করুন",

        "sf_msg_have_account": "ইতিমধ্যে একাউন্ট আছে?",

        "sf_link_signin": "সাইন ইন করুন",

        "sf_lbl_name": "পুরো নাম",

        "sf_pl_name": "আপনার নাম লিখুন",

        "sf_lbl_email": "ইমেল ঠিকানা",

        "sf_pl_email": "you@example.com",

        "sf_lbl_pass": "পাসওয়ার্ড",

        "sf_pl_pass": "অন্তত ৬ অক্ষর",

        "sf_h_about": "আপনার সম্পর্কে",

        "sf_lbl_gender": "লিঙ্গ",

        "sf_opt_male": "পুরুষ",

        "sf_opt_female": "মহিলা",

        "sf_opt_trans": "ট্রান্সজেন্ডার",

        "sf_lbl_age": "বয়স",

        "sf_opt_sel_age": "বয়স নির্বাচন করুন",

        "sf_h_loc": "অবস্থান",

        "sf_lbl_state": "রাজ্য",

        "sf_opt_sel_state": "রাজ্য নির্বাচন করুন",

        "sf_lbl_area": "এলাকার ধরন",

        "sf_opt_urban": "শহুরে",

        "sf_opt_rural": "গ্রামীণ",

        "sf_h_social": "সামাজিক বিবরণ",

        "sf_lbl_cat": "বিভাগ",

        "sf_cat_gen": "সাধারণ",

        "sf_cat_obc": "ওবিসি",

        "sf_cat_pvtg": "পিভিটিজি",

        "sf_cat_sc": "এসসি",

        "sf_cat_st": "এসটি",

        "sf_cat_dnt": "ডিএনটি",

        "sf_lbl_pwd": "প্রতিবন্ধী?",

        "sf_opt_yes": "হ্যাঁ",

        "sf_opt_no": "না",

        "sf_lbl_minor": "সংখ্যালঘু?",

        "sf_h_emp": "কর্মসংস্থান এবং শিক্ষা",

        "sf_lbl_student": "ছাত্র?",

        "sf_lbl_status": "কর্মসংস্থান স্থিতি",

        "sf_emp_emp": "চাকুরীজীবী",

        "sf_emp_unemp": "বেকার",

        "sf_emp_self": "স্ব-নিযুক্ত",

        "sf_lbl_govt": "সরকারি কর্মচারী?",

        "sf_h_income": "আয়ের বিবরণ",

        "sf_lbl_inc_ann": "বার্ষিক আয় (₹)",

        "sf_lbl_inc_fam": "পারিবারিক আয় (₹)",

        "sf_pl_zero": "0",

        "sf_submit_btn": "প্রোফাইল জমা দিন এবং চ্যাট শুরু করুন",

        "sf_loading": "আপনার প্রোফাইল সেট করা হচ্ছে...",

        "user-name-display": "",
        "features_title": "মূল বৈশিষ্ট্য",

        "feature_secure_profile": "নিরাপদ প্রোফাইল",

        "feature_secure_desc": "আপনার ব্যবহারকারীর প্রোফাইল পরিচয় সুরক্ষিত করুন, এবং প্রোফাইল সুবিধা সুরক্ষিত করুন।",

        "feature_direct_benefit": "সরাসরি সুবিধার স্থানান্তর",

        "feature_direct_desc": "প্রত্যক্ষ সুবিধার স্থানান্তর",

        "feature_multilingual": "বহুভাষী",

        "feature_multilingual_desc": "গ্রহণ এবং লেনদেনের উত্তরের জন্য সর্বোত্তম বহুমুখী ক্ষমতা।",

        "feature_personalized": "ব্যক্তিগতকৃত",

        "feature_personalized_desc": "আপনার পরিচয় এবং প্রোফাইল সুবিধা নিশ্চিত করুন",

        "featured_title": "বৈশিষ্ট্যযুক্ত প্রকল্প",

        "scheme_agriculture": "কৃষি ও গ্রামাঞ্চল",

        "scheme_agriculture_count": "৮১৮ স্কিম",

        "scheme_banking": "ব্যাংকিং ও অর্থনীতি",

        "scheme_banking_count": "৩১৭ স্কিম",

        "scheme_business": "ব্যবসা",

        "scheme_business_count": "৭০৫ স্কিম",

        "scheme_education": "শিক্ষা",

        "scheme_education_count": "১০৭৬ স্কিম",

        "scheme_health": "স্বাস্থ্য",

        "scheme_health_count": "২৭৪ প্রকল্প",

        "scheme_housing": "আবাসন",

        "scheme_housing_count": "১২৮ স্কিম",

        "scheme_public_safety": "জনসাধারণের নিরাপত্তা",

        "scheme_public_safety_count": "২৯ স্কিম",

        "scheme_science": "বিজ্ঞান ও তথ্য প্রযুক্তি",

        "scheme_science_count": "১০০টি স্কিম",

        "scheme_skills": "দক্ষতা",

        "scheme_skills_count": "৩৬৮ স্কিম",

        "scheme_social_welfare": "সামাজিক কল্যাণ",

        "scheme_social_welfare_count": "১৪৫৬ স্কিম",

        "scheme_sports": "খেলাধুলা",

        "scheme_sports_count": "২৪৮ স্কিম",

        "scheme_transport": "পরিবহন",

        "scheme_transport_count": "৮৬ স্কিম",

        "scheme_travel": "ভ্রমণ",

        "scheme_travel_count": "৯১ স্কিম",

        "scheme_utility": "ইউটিলিটি",

        "scheme_utility_count": "৫৮ স্কিম",

        "scheme_women": "নারী ও শিশু",

        "scheme_women_count": "৪৫৮ স্কিম",

        "how_title": "কিভাবে কাজ করে",

        "step1_title": "আপনার তথ্য দিন",

        "step2_title": "ব্যক্তিগতকৃত স্কিমগুলি পান",

        "step3_title": "এই স্কিমের সুবিধা",

        "hero-signup": "নিবন্ধন করুন",

        "hero-continue": "অতিথি হিসেবে থাকুন",

        "stat_ai": "এআই",

        "stat_ai_label": "চালিত",

        "stat_languages_new": "১২+",

        "stat_languages_interactive": "ভাষা, ইন্টারেক্টিভ",


        // New button translations for bn_IN
        "nav_signin": "সাইন ইন করুন",

        "start_chatting": "চ্যাট শুরু করুন",

        "greeting_hello": "হ্যালো .",

    },

    "mr_IN": {
        "app_title": "सरकारी योजना सहाय्यक",

        "logo-text": "सरकारी योजना सहाय्यक",

        "signin": "साइन इन →",

        "logout": "लॉग आउट",

        "edit_profile": "प्रोफाइल संपादित करा",

        "status-online": "ऑनलाइन",

        "hero-badge": "सुरक्षित, सोपे, अखंड",

        "hero-accent": "फास्ट-ट्रॅक",

        "hero-title": "सरकारी लाभ\<br>मिळवा",

        "cta-btn": "योजना शोधा",

        "skip-btn": "अतिथी म्हणून सुरू ठेवा →",

        "tab_new": "नवीन वापरकर्ता",

        "tab_signin": "साइन इन",

        "quick_lang": "तुमची भाषा",

        "quick_state": "तुमचे राज्य",

        "quick_all_india": "संपूर्ण भारत",

        "quick_explore": "योजना शोधा",

        "stat_schemes": "५००+",

        "stat_schemes_label": "उपलब्ध योजना",

        "stat_serving": "AI-चालित",

        "stat_serving_label": "मदत",

        "stat_languages": "१५+",

        "stat_languages_label": "समर्थित भाषा",

        "chat_welcome_title": "सरकारी योजना सहाय्यकामध्ये आपले स्वागत आहे",

        "chat_welcome_desc": "मी तुम्हाला तुमच्या पसंतीच्या भाषेत भारतीय सरकारी योजना, पात्रता, फायदे आणि अर्ज प्रक्रिया समजून घेण्यास मदत करू शकतो.",

        "chat_limit_msg": "३ मोफत संदेश बाकी",

        "chat_input_placeholder": "तुमचा संदेश टाइप करा...",

        "signin-title": "परत स्वागत आहे",

        "signin-subtitle": "चॅट चालू ठेवण्यासाठी साइन इन करा",

        "signin-email": "ईमेल पत्ता",

        "signin-btn": "साइन इन →",

        "signin-loading": "साइन इन होत आहे...",

        "auth_lbl_password": "पासवर्ड",

        "auth_pl_password": "तुमचा पासवर्ड टाका",

        "auth_msg_no_account": "खाते नाही?",

        "auth_link_signup": "साइन अप करा",

        "auth-prompt-message": "चાલુ ठेवण्यासाठी साइन इन किंवा खाते तयार करा",

        "forgot-password": "पासवर्ड विसरलात?",

        "sf_modal_title": "आपल्यासाठी सर्वोत्तम योजना शोधण्यात आम्हाला मदत करा",

        "sf_h_account": "तुमचे खाते तयार करा",

        "sf_msg_have_account": "आधीच खाते आहे?",

        "sf_link_signin": "साइन इन करा",

        "sf_lbl_name": "पूर्ण नाव",

        "sf_pl_name": "तुमचे नाव प्रविष्ट करा",

        "sf_lbl_email": "ईमेल पत्ता",

        "sf_pl_email": "you@example.com",

        "sf_lbl_pass": "पासवर्ड",

        "sf_pl_pass": "किमान 6 अक्षरे",

        "sf_h_about": "तुमच्याबद्दल",

        "sf_lbl_gender": "लिंग",

        "sf_opt_male": "पुरुष",

        "sf_opt_female": "स्त्री",

        "sf_opt_trans": "ट्रान्सजेंडर",

        "sf_lbl_age": "वय",

        "sf_opt_sel_age": "वय निवडा",

        "sf_h_loc": "स्थान",

        "sf_lbl_state": "राज्य",

        "sf_opt_sel_state": "राज्य निवडा",

        "sf_lbl_area": "भाग प्रकार",

        "sf_opt_urban": "शहरी",

        "sf_opt_rural": "ग्रामीण",

        "sf_h_social": "सामाजिक तपशील",

        "sf_lbl_cat": "श्रेणी",

        "sf_cat_gen": "सामान्य",

        "sf_cat_obc": "ओबीसी",

        "sf_cat_pvtg": "पीव्हीटीजी",

        "sf_cat_sc": "एससी",

        "sf_cat_st": "एसटी",

        "sf_cat_dnt": "डीएनटी",

        "sf_lbl_pwd": "अपंग व्यक्ती?",

        "sf_opt_yes": "होय",

        "sf_opt_no": "नाही",

        "sf_lbl_minor": "अल्पसंख्याक?",

        "sf_h_emp": "रोजगार आणि शिक्षण",

        "sf_lbl_student": "विद्यार्थी?",

        "sf_lbl_status": "रोजगार स्थिती",

        "sf_emp_emp": "नोकरी",

        "sf_emp_unemp": "बेरोजगार",

        "sf_emp_self": "स्वयंरोजगार",

        "sf_lbl_govt": "सरकारी कर्मचारी?",

        "sf_h_income": "उत्पन्न तपशील",

        "sf_lbl_inc_ann": "वार्षिक उत्पन्न (₹)",

        "sf_lbl_inc_fam": "कौटुंबिक उत्पन्न (₹)",

        "sf_pl_zero": "0",

        "sf_submit_btn": "प्रोफाइल सबमिट करा आणि चॅट सुरू करा",

        "sf_loading": "आपले प्रोफाइल सेट केले जात आहे...",

        "user-name-display": "",
        "features_title": "मुख्य वैशिष्ट्ये",

        "feature_secure_profile": "सुरक्षित प्रोफाइल",

        "feature_secure_desc": "आपल्या वापरकर्त्याची प्रोफाइल ओळख सुरक्षित करा, आणि प्रोफाइल फायदे सुरक्षित करा.",

        "feature_direct_benefit": "थेट लाभ हस्तांतरण",

        "feature_direct_desc": "थेट लाभ हस्तांतरण",

        "feature_multilingual": "बहुभाषिक",

        "feature_multilingual_desc": "दत्तक आणि व्यवहार प्रतिसादासाठी बहुभाषिक क्षमता.",

        "feature_personalized": "वैयक्तिकृत",

        "feature_personalized_desc": "आपली ओळख आणि प्रोफाइल फायदे सुनिश्चित करा",

        "featured_title": "मुख्य योजना",

        "scheme_agriculture": "कृषी आणि ग्रामीण भाग",

        "scheme_agriculture_count": "८१८ योजना",

        "scheme_banking": "बँकिंग आणि वित्त",

        "scheme_banking_count": "३१७ योजना",

        "scheme_business": "व्यवसाय",

        "scheme_business_count": "७०५ योजना",

        "scheme_education": "शिक्षण",

        "scheme_education_count": "१०७६ योजना",

        "scheme_health": "आरोग्य",

        "scheme_health_count": "२७४ योजना",

        "scheme_housing": "गृहनिर्माण",

        "scheme_housing_count": "१२८ योजना",

        "scheme_public_safety": "सार्वजनिक सुरक्षा",

        "scheme_public_safety_count": "२९ योजना",

        "scheme_science": "विज्ञान आणि माहिती तंत्रज्ञान",

        "scheme_science_count": "१०० योजना",

        "scheme_skills": "कौशल्ये",

        "scheme_skills_count": "३६८ योजना",

        "scheme_social_welfare": "सामाजिक कल्याण",

        "scheme_social_welfare_count": "१४५६ योजना",

        "scheme_sports": "क्रीडा",

        "scheme_sports_count": "२४८ योजना",

        "scheme_transport": "वाहतूक",

        "scheme_transport_count": "८६ योजना",

        "scheme_travel": "प्रवास",

        "scheme_travel_count": "९१ योजना",

        "scheme_utility": "उपयुक्तता",

        "scheme_utility_count": "५८ योजना",

        "scheme_women": "महिला आणि मुले",

        "scheme_women_count": "४५८ योजना",

        "how_title": "ते कसे कार्य करते",

        "step1_title": "आपली माहिती द्या",

        "step2_title": "वैयक्तिकृत योजना मिळवा",

        "step3_title": "योजनेचा लाभ",

        "hero-signup": "नोंदणी करा",

        "hero-continue": "पाहुण्यासारखे रहा",

        "stat_ai": "कृत्रिम बुद्धिमत्ता",

        "stat_ai_label": "उर्जा",

        "stat_languages_new": "१२+",

        "stat_languages_interactive": "भाषा, परस्परसंवादी",


        // New button translations for mr_IN
        "nav_signin": "साइन इन करा",

        "start_chatting": "गप्पा सुरू करा",

        "greeting_hello": "नमस्कार.",

    },

    "gu_IN": {
        "app_title": "સરકારી યોજના સહાયક",

        "logo-text": "સરકારી યોજના સહાયક",

        "signin": "સાઇન ઇન →",

        "logout": "લોગ આઉટ",

        "edit_profile": "પ્રોફાઇલ સંપાદિત કરો",

        "status-online": "ઓનલાઇન",

        "hero-badge": "સુરક્ષિત, સરળ, સીમલેસ",

        "hero-accent": "ફાસ્ટ-ટ્રેક",

        "hero-title": "સરકારી લાભો\<br>મેળવો",

        "cta-btn": "યોજનાઓ શોધો",

        "skip-btn": "મહેમાન તરીકે ચાલુ રાખો →",

        "tab_new": "નવો વપરાશકર્તા",

        "tab_signin": "સાઇન ઇન",

        "quick_lang": "તમારી ભાષા",

        "quick_state": "તમારું રાજ્ય",

        "quick_all_india": "સમગ્ર ભારત",

        "quick_explore": "યોજનાઓનું અન્વેષણ કરો",

        "stat_schemes": "૫૦૦+",

        "stat_schemes_label": "ઉપલબ્ધ યોજનાઓ",

        "stat_serving": "AI-સંચાલિત",

        "stat_serving_label": "સહાય",

        "stat_languages": "૧૫+",

        "stat_languages_label": "સમર્થિત ભાષાઓ",

        "chat_welcome_title": "સરકારી યોજના સહાયકમાં આપનું સ્વાગત છે",

        "chat_welcome_desc": "હું તમને તમારી પસંદગીની ભાષામાં ભારતીય સરકારી યોજનાઓ, યોગ્યતા, લાભો અને અરજી પ્રક્રિયા સમજવામાં મદદ કરી શકું છું.",

        "chat_limit_msg": "૩ મફત સંદેશાઓ બાકી",

        "chat_input_placeholder": "તમારો સંદેશ લખો...",

        "signin-title": "ફરી સ્વાગત છે",

        "signin-subtitle": "ચેટ ચાલુ રાખવા માટે સાઇન ઇન કરો",

        "signin-email": "ઇમેઇલ સરનામું",

        "signin-btn": "સાઇન ઇન →",

        "signin-loading": "સાઇન ઇન થઈ રહ્યું છે...",

        "auth_lbl_password": "પાસવર્ડ",

        "auth_pl_password": "તમારો પાસવર્ડ દાખલ કરો",

        "auth_msg_no_account": "ખાતું નથી?",

        "auth_link_signup": "સાઇન અપ કરો",

        "auth-prompt-message": "ચાલુ રાખવા માટે સાઇન ઇન કરો અથવા ખાતું બનાવો",

        "forgot-password": "પાસવર્ડ ભૂલી ગયા છો?",

        "sf_modal_title": "તમારા માટે શ્રેષ્ઠ યોજનાઓ શોધવામાં અમને મદદ કરો",

        "sf_h_account": "તમારું ખાતું બનાવો",

        "sf_msg_have_account": "પહેલેથી જ ખાતું છે?",

        "sf_link_signin": "સાઇન ઇન કરો",

        "sf_lbl_name": "પૂરું નામ",

        "sf_pl_name": "તમારું નામ દાખલ કરો",

        "sf_lbl_email": "ઇમેઇલ સરનામું",

        "sf_pl_email": "you@example.com",

        "sf_lbl_pass": "પાસવર્ડ",

        "sf_pl_pass": "ઓછામાં ઓછાં 6 અક્ષરો",

        "sf_h_about": "તમારા વિશે",

        "sf_lbl_gender": "લિંગ",

        "sf_opt_male": "પુરુષ",

        "sf_opt_female": "સ્ત્રી",

        "sf_opt_trans": "ટ્રાન્સજેન્ડર",

        "sf_lbl_age": "ઉંમર",

        "sf_opt_sel_age": "ઉંમર પસંદ કરો",

        "sf_h_loc": "સ્થાન",

        "sf_lbl_state": "રાજ્ય",

        "sf_opt_sel_state": "રાજ્ય પસંદ કરો",

        "sf_lbl_area": "વિસ્તારનો પ્રકાર",

        "sf_opt_urban": "શહેરી",

        "sf_opt_rural": "ગ્રામીણ",

        "sf_h_social": "સામાજિક વિગતો",

        "sf_lbl_cat": "શ્રેણી",

        "sf_cat_gen": "સામાન્ય",

        "sf_cat_obc": "ઓબીસી",

        "sf_cat_pvtg": "પીવીટીજી",

        "sf_cat_sc": "એસસી",

        "sf_cat_st": "એસટી",

        "sf_cat_dnt": "ડીએનટી",

        "sf_lbl_pwd": "દિવ્યાંગ વ્યક્તિ?",

        "sf_opt_yes": "હા",

        "sf_opt_no": "ના",

        "sf_lbl_minor": "લઘુમતી?",

        "sf_h_emp": "રોજગાર અને શિક્ષણ",

        "sf_lbl_student": "વિદ્યાર્થી?",

        "sf_lbl_status": "રોજગાર સ્થિતિ",

        "sf_emp_emp": "નોકરિયાત",

        "sf_emp_unemp": "બેરોજગાર",

        "sf_emp_self": "સ્વ-રોજગાર",

        "sf_lbl_govt": "સરકારી કર્મચારી?",

        "sf_h_income": "આવક વિગતો",

        "sf_lbl_inc_ann": "વાર્ષિક આવક (₹)",

        "sf_lbl_inc_fam": "કૌટુંબિક આવક (₹)",

        "sf_pl_zero": "0",

        "sf_submit_btn": "પ્રોફાઇલ સબમિટ કરો અને ચેટ શરૂ કરો",

        "sf_loading": "તમારી પ્રોફાઇલ સેટ થઈ રહી છે...",

        "user-name-display": "",
        "features_title": "મુખ્ય લક્ષણો",

        "feature_secure_profile": "સુરક્ષિત પ્રોફાઇલ",

        "feature_secure_desc": "તમારા વપરાશકર્તાની પ્રોફાઇલ ઓળખ સુરક્ષિત કરો, અને પ્રોફાઇલ લાભો સુરક્ષિત કરો.",

        "feature_direct_benefit": "સીધી લાભ ટ્રાન્સફર",

        "feature_direct_desc": "સીધી લાભ ટ્રાન્સફર બિનસલાહભર્યું માહિતી લાભ.",

        "feature_multilingual": "બહુભાષી",

        "feature_multilingual_desc": "સ્વીકાર અને વ્યવહારોના જવાબમાં શ્રેષ્ઠ માટે બહુભાષી ક્ષમતાઓ.",

        "feature_personalized": "વ્યક્તિગત",

        "feature_personalized_desc": "તમારી ઓળખ અને પ્રોફાઇલ લાભો સુરક્ષિત કરો",

        "featured_title": "વિશેષ યોજનાઓ",

        "scheme_agriculture": "કૃષિ અને ગ્રામીણ",

        "scheme_agriculture_count": "૮૧૮ યોજનાઓ",

        "scheme_banking": "બેંકિંગ અને નાણા",

        "scheme_banking_count": "૩૧૭ યોજનાઓ",

        "scheme_business": "વ્યવસાય",

        "scheme_business_count": "૭૦૫ યોજનાઓ",

        "scheme_education": "શિક્ષણ",

        "scheme_education_count": "૧૦૭૬ યોજનાઓ",

        "scheme_health": "આરોગ્ય",

        "scheme_health_count": "૨૭૪ યોજનાઓ",

        "scheme_housing": "હાઉસિંગ",

        "scheme_housing_count": "૧૨૮ યોજનાઓ",

        "scheme_public_safety": "જાહેર સલામતી",

        "scheme_public_safety_count": "૨૯ યોજનાઓ",

        "scheme_science": "વિજ્ઞાન અને આઇટી",

        "scheme_science_count": "૧૦૦ યોજનાઓ",

        "scheme_skills": "કૌશલ્ય",

        "scheme_skills_count": "૩૬૮ યોજનાઓ",

        "scheme_social_welfare": "સામાજિક કલ્યાણ",

        "scheme_social_welfare_count": "૧૪૫૬ યોજનાઓ",

        "scheme_sports": "રમતગમત",

        "scheme_sports_count": "૨૪૮ યોજનાઓ",

        "scheme_transport": "પરિવહન",

        "scheme_transport_count": "૮૬ યોજનાઓ",

        "scheme_travel": "મુસાફરી",

        "scheme_travel_count": "૯૧ યોજનાઓ",

        "scheme_utility": "ઉપયોગિતા",

        "scheme_utility_count": "૫૮ યોજનાઓ",

        "scheme_women": "મહિલાઓ અને બાળકો",

        "scheme_women_count": "૪૫૮ યોજનાઓ",

        "how_title": "તે કેવી રીતે કાર્ય કરે છે",

        "step1_title": "તમારી માહિતી આપો",

        "step2_title": "વ્યક્તિગત યોજનાઓ મેળવો",

        "step3_title": "યોજનાના લાભો",

        "hero-signup": "નોંધણી કરાવો",

        "hero-continue": "મહેમાન તરીકે ચાલુ રાખો",

        "stat_ai": "એઆઈ",

        "stat_ai_label": "પાવર",

        "stat_languages_new": "૧૨+",

        "stat_languages_interactive": "ભાષાઓ, ઇન્ટરેક્ટિવ",


        // New button translations for gu_IN
        "nav_signin": "સાઇન ઇન કરો",

        "start_chatting": "ચેટિંગ શરૂ કરો",

        "greeting_hello": "હેલો .",

    },

    "kn_IN": {
        "app_title": "ಸರ್ಕಾರಿ ಯೋಜನೆ ಸಹಾಯಕ",

        "logo-text": "ಸರ್ಕಾರಿ ಯೋಜನೆ ಸಹಾಯಕ",

        "signin": "ಸೈನ್ ಇನ್ →",

        "logout": "ಲಾಗ್ ಔಟ್",

        "edit_profile": "ಪ್ರೊಫೈಲ್ ಸಂಪಾದಿಸಿ",

        "status-online": "ಆನ್‌ಲೈನ್",

        "hero-badge": "ಸುರಕ್ಷಿತ, ಸರಳ, ತಡೆರಹಿತ",

        "hero-accent": "ಫಾಸ್ಟ್-ಟ್ರ್ಯಾಕ್",

        "hero-title": "ಸರ್ಕಾರಿ ಪ್ರಯೋಜನಗಳನ್ನು\<br>ಪಡೆಯಿರಿ",

        "cta-btn": "ಯೋಜನೆಗಳನ್ನು ಅನ್ವೇಷಿಸಿ",

        "skip-btn": "ಅತಿಥಿಯಾಗಿ ಮುಂದುವರಿಸಿ →",

        "tab_new": "ಹೊಸ ಬಳಕೆದಾರ",

        "tab_signin": "ಸೈನ್ ಇನ್",

        "quick_lang": "ನಿಮ್ಮ ಭಾಷೆ",

        "quick_state": "ನಿಮ್ಮ ರಾಜ್ಯ",

        "quick_all_india": "ಇಡೀ ಭಾರತ",

        "quick_explore": "ಯೋಜನೆಗಳನ್ನು ಅನ್ವೇಷಿಸಿ",

        "stat_schemes": "೫೦೦+",

        "stat_schemes_label": "ಲಭ್ಯವಿರುವ ಯೋಜನೆಗಳು",

        "stat_serving": "AI-ಚಾಲಿತ",

        "stat_serving_label": "ಸಹಾಯ",

        "stat_languages": "೧೫+",

        "stat_languages_label": "ಬೆಂಬಲಿತ ಭಾಷೆಗಳು",

        "chat_welcome_title": "ಸರ್ಕಾರಿ ಯೋಜನೆ ಸಿಹಾಯಕಕ್ಕೆ ಸ್ವಾಗತ",

        "chat_welcome_desc": "ನಿಮ್ಮ ಆದ್ಯತೆಯ ಭಾಷೆಯಲ್ಲಿ ಭಾರತೀಯ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು, ಅರ್ಹತೆ, ಪ್ರಯೋಜನಗಳು ಮತ್ತು ಅರ್ಜಿ ಪ್ರಕ್ರಿಯೆಯನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲು ನಾನು ನಿಮಗೆ ಸಹಾಯ ಮಾಡಬಲ್ಲೆ.",

        "chat_limit_msg": "೩ ಉಚಿತ ಸಂದೇಶಗಳು ಉಳಿದಿವೆ",

        "chat_input_placeholder": "ನಿಮ್ಮ ಸಂದೇಶವನ್ನು ಟೈಪ್ ಮಾಡಿ...",

        "signin-title": "ಮತ್ತೆ ಸ್ವಾಗತ",

        "signin-subtitle": "ಚಾಟ್ ಮುಂದುವರಿಸಲು ಸೈನ್ ಇನ್ ಮಾಡಿ",

        "signin-email": "ಇಮೇಲ್ ವಿಳಾಸ",

        "signin-btn": "ಸೈನ್ ಇನ್ →",

        "signin-loading": "ಸೈನ್ ಇನ್ ಮಾಡಲಾಗುತ್ತಿದೆ...",

        "auth_lbl_password": "ಪಾಸ್‌ವರ್ಡ್",

        "auth_pl_password": "ನಿಮ್ಮ ಪಾಸ್‌ವರ್ಡ್ ನಮೂದಿಸಿ",

        "auth_msg_no_account": "ಖಾತೆ ಇಲ್ಲವೇ?",

        "auth_link_signup": "ಸೈನ್ ಅಪ್ ಮಾಡಿ",

        "auth-prompt-message": "ಮುಂದುವರಿಸಲು ಸೈನ್ ಇನ್ ಮಾಡಿ ಅಥವಾ ಖಾತೆ ರಚಿಸಿ",

        "forgot-password": "ಪಾಸ್‌ವರ್ಡ್ ಮರೆತಿರಾ?",

        "sf_modal_title": "ನಿಮಗಾಗಿ ಉತ್ತಮ ಯೋಜನೆಗಳನ್ನು ಹುಡುಕಲು ನಮಗೆ ಸಹಾಯ ಮಾಡಿ",

        "sf_h_account": "ನಿಮ್ಮ ಖಾತೆಯನ್ನು ರಚಿಸಿ",

        "sf_msg_have_account": "ಈಗಾಗಲೇ ಖಾತೆ ಇದೆಯೇ?",

        "sf_link_signin": "ಸೈನ್ ಇನ್ ಮಾಡಿ",

        "sf_lbl_name": "ಪೂರ್ಣ ಹೆಸರು",

        "sf_pl_name": "ನಿಮ್ಮ ಹೆಸರನ್ನು ನಮೂದಿಸಿ",

        "sf_lbl_email": "ಇಮೇಲ್ ವಿಳಾಸ",

        "sf_pl_email": "you@example.com",

        "sf_lbl_pass": "ಪಾಸ್‌ವರ್ಡ್",

        "sf_pl_pass": "ಕನಿಷ್ಠ 6 ಅಕ್ಷರಗಳು",

        "sf_h_about": "ನಿಮ್ಮ ಬಗ್ಗೆ",

        "sf_lbl_gender": "ಲಿಂಗ",

        "sf_opt_male": "ಪುರುಷ",

        "sf_opt_female": "ಮಹಿಳೆ",

        "sf_opt_trans": "ತೃತೀಯ ಲಿಂಗಿ",

        "sf_lbl_age": "ವಯಸ್ಸು",

        "sf_opt_sel_age": "ವಯಸ್ಸನ್ನು ಆಯ್ಕೆಮಾಡಿ",

        "sf_h_loc": "ಸ್ಥಳ",

        "sf_lbl_state": "ರಾಜ್ಯ",

        "sf_opt_sel_state": "ರಾಜ್ಯವನ್ನು ಆಯ್ಕೆಮಾಡಿ",

        "sf_lbl_area": "ಪ್ರದೇಶದ ಪ್ರಕಾರ",

        "sf_opt_urban": "ನಗರ",

        "sf_opt_rural": "ಗ್ರಾಮೀಣ",

        "sf_h_social": "ಸಾಮಾಜಿಕ ವಿವರಗಳು",

        "sf_lbl_cat": "ವರ್ಗ",

        "sf_cat_gen": "ಸಾಮಾನ್ಯ",

        "sf_cat_obc": "ಒಬಿಸಿ",

        "sf_cat_pvtg": "ಪಿವಿಟಿಜಿ",

        "sf_cat_sc": "ಎಸ್ಸಿ",

        "sf_cat_st": "ಎಸ್ಟಿ",

        "sf_cat_dnt": "ಡಿಎನ್‌ಟಿ",

        "sf_lbl_pwd": "ವಿಕಲಚೇತನರೇ?",

        "sf_opt_yes": "ಹೌದು",

        "sf_opt_no": "ಇಲ್ಲ",

        "sf_lbl_minor": "ಅಲ್ಪಸಂಖ್ಯಾತರೇ?",

        "sf_h_emp": "ಉದ್ಯೋಗ ಮತ್ತು ಶಿಕ್ಷಣ",

        "sf_lbl_student": "ವಿದ್ಯಾರ್ಥಿಯೇ?",

        "sf_lbl_status": "ಉದ್ಯೋಗ ಸ್ಥಿತಿ",

        "sf_emp_emp": "ಉದ್ಯೋಗಿ",

        "sf_emp_unemp": "ನಿರುದ್ಯೋಗಿ",

        "sf_emp_self": "ಸ್ವಯಂ ಉದ್ಯೋಗಿ",

        "sf_lbl_govt": "ಸರ್ಕಾರಿ ನೌಕರರೇ?",

        "sf_h_income": "ಆದಾಯ ವಿವರಗಳು",

        "sf_lbl_inc_ann": "ವಾರ್ಷಿಕ ಆದಾಯ (₹)",

        "sf_lbl_inc_fam": "ಕುಟುಂಬದ ಆದಾಯ (₹)",

        "sf_pl_zero": "0",

        "sf_submit_btn": "ಪ್ರೊಫೈಲ್ ಸಲ್ಲಿಸಿ ಮತ್ತು ಚಾಟ್ ಪ್ರಾರಂಭಿಸಿ",

        "sf_loading": "ನಿಮ್ಮ ಪ್ರೊಫೈಲ್ ಹೊಂದಿಸಲಾಗುತ್ತಿದೆ...",

        "user-name-display": "",
        "features_title": "ಪ್ರಮುಖ ಲಕ್ಷಣಗಳು",

        "feature_secure_profile": "ಸುರಕ್ಷಿತ ಪ್ರೊಫೈಲ್",

        "feature_secure_desc": "ನಿಮ್ಮ ಬಳಕೆದಾರರ ಪ್ರೊಫೈಲ್ ಗುರುತನ್ನು ಭದ್ರಪಡಿಸಿ, ಮತ್ತು ಪ್ರೊಫೈಲ್ ಪ್ರಯೋಜನಗಳನ್ನು ಭದ್ರಪಡಿಸಿ.",

        "feature_direct_benefit": "ನೇರ ಪ್ರಯೋಜನ ವರ್ಗಾವಣೆ",

        "feature_direct_desc": "ನೇರ ಪ್ರಯೋಜನ ವರ್ಗಾವಣೆ",

        "feature_multilingual": "ಬಹುಭಾಷಾ",

        "feature_multilingual_desc": "ಅಳವಡಿಕೆ ಮತ್ತು ವಹಿವಾಟು ಪ್ರತಿಕ್ರಿಯೆಗಳಲ್ಲಿ ಉತ್ತಮವಾದ ಬಹುಭಾಷಾ ಸಾಮರ್ಥ್ಯಗಳು.",

        "feature_personalized": "ವೈಯಕ್ತಿಕಗೊಳಿಸಿದ",

        "feature_personalized_desc": "ನಿಮ್ಮ ಗುರುತಿನ ಮತ್ತು ಪ್ರೊಫೈಲ್ ಪ್ರಯೋಜನಗಳನ್ನು ಭದ್ರಪಡಿಸಿ",

        "featured_title": "ಒಳಗೊಂಡಿರುವ ಯೋಜನೆಗಳು",

        "scheme_agriculture": "ಕೃಷಿ ಮತ್ತು ಗ್ರಾಮೀಣ",

        "scheme_agriculture_count": "೮೧೮ ಯೋಜನೆಗಳು",

        "scheme_banking": "ಬ್ಯಾಂಕಿಂಗ್ ಮತ್ತು ಹಣಕಾಸು",

        "scheme_banking_count": "೩೧೭ ಯೋಜನೆಗಳು",

        "scheme_business": "ವ್ಯಾಪಾರ",

        "scheme_business_count": "೭೦೫ ಯೋಜನೆಗಳು",

        "scheme_education": "ಶಿಕ್ಷಣ",

        "scheme_education_count": "೧೦೭೬ ಯೋಜನೆಗಳು",

        "scheme_health": "ಆರೋಗ್ಯ",

        "scheme_health_count": "೨೭೪ ಯೋಜನೆಗಳು",

        "scheme_housing": "ವಸತಿ",

        "scheme_housing_count": "೧೨೮ ಯೋಜನೆಗಳು",

        "scheme_public_safety": "ಸಾರ್ವಜನಿಕ ಸುರಕ್ಷತೆ",

        "scheme_public_safety_count": "೨೯ ಯೋಜನೆಗಳು",

        "scheme_science": "ವಿಜ್ಞಾನ ಮತ್ತು ಐಟಿ",

        "scheme_science_count": "೧೦೦ ಯೋಜನೆಗಳು",

        "scheme_skills": "ಕೌಶಲ್ಯ",

        "scheme_skills_count": "೩೬೮ ಯೋಜನೆಗಳು",

        "scheme_social_welfare": "ಸಾಮಾಜಿಕ ಕಲ್ಯಾಣ",

        "scheme_social_welfare_count": "೧೪೫೬ ಯೋಜನೆಗಳು",

        "scheme_sports": "ಕ್ರೀಡೆ",

        "scheme_sports_count": "೨೪೮ ಯೋಜನೆಗಳು",

        "scheme_transport": "ಸಾರಿಗೆ",

        "scheme_transport_count": "೮೬ ಯೋಜನೆಗಳು",

        "scheme_travel": "ಪ್ರಯಾಣ",

        "scheme_travel_count": "೯೧ ಯೋಜನೆಗಳು",

        "scheme_utility": "ಉಪಯುಕ್ತತೆ",

        "scheme_utility_count": "೫೮ ಯೋಜನೆಗಳು",

        "scheme_women": "ಮಹಿಳೆ ಮತ್ತು ಮಗು",

        "scheme_women_count": "೪೫೮ ಯೋಜನೆಗಳು",

        "how_title": "ಅದು ಹೇಗೆ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತದೆ",

        "step1_title": "ನಿಮ್ಮ ಮಾಹಿತಿಯನ್ನು ನೀಡಿ",

        "step2_title": "ವೈಯಕ್ತಿಕಗೊಳಿಸಿದ ಯೋಜನೆಗಳನ್ನು ಪಡೆಯಿರಿ",

        "step3_title": "ಯೋಜನೆಯ ಪ್ರಯೋಜನಗಳು",

        "hero-signup": "ಸೈನ್ ಅಪ್ ಮಾಡಿ",

        "hero-continue": "ಅತಿಥಿಯಾಗಿ ಮುಂದುವರಿಯಿರಿ",

        "stat_ai": "AI",

        "stat_ai_label": "ವಿದ್ಯುತ್ ಚಾಲಿತ",

        "stat_languages_new": "೧೨+",

        "stat_languages_interactive": "ಭಾಷೆಗಳು, ಸಂವಾದಾತ್ಮಕ",


        // New button translations for kn_IN
        "nav_signin": "ಸೈನ್ ಇನ್ ಮಾಡಿ",

        "start_chatting": "ಚಾಟ್ ಪ್ರಾರಂಭಿಸಿ",

        "greeting_hello": "ಹಲೋ .",

    },

    "ml_IN": {
        "app_title": "സർക്കാർ പദ്ധതി സഹായി",

        "logo-text": "സർക്കാർ പദ്ധതി സഹായി",

        "signin": "സൈൻ ഇൻ →",

        "logout": "ലോഗ് ഔട്ട്",

        "edit_profile": "പ്രൊഫൈൽ എഡിറ്റ് ചെയ്യുക",

        "status-online": "ഓൺലൈൻ",

        "hero-badge": "സുരക്ഷിതം, ലളിതം, തടസ്സമില്ലാത്ത",

        "hero-accent": "ഫാസ്റ്റ്-ട്രാക്ക്",

        "hero-title": "സർക്കാർ ആനുകൂല്യങ്ങൾ\<br>നേടുക",

        "cta-btn": "പദ്ധതികൾ കണ്ടെത്തുക",

        "skip-btn": "അതിഥിയായി തുടരുക →",

        "tab_new": "പുതിയ ഉപയോക്താവ്",

        "tab_signin": "സൈൻ ഇൻ",

        "quick_lang": "നിങ്ങളുടെ ഭാഷ",

        "quick_state": "നിങ്ങളുടെ സംസ്ഥാനം",

        "quick_all_india": "മുഴുവൻ ഇന്ത്യ",

        "quick_explore": "പദ്ധതികൾ പര്യവേക്ഷണം ചെയ്യുക",

        "stat_schemes": "൫൦൦+",

        "stat_schemes_label": "ലഭ്യമായ പദ്ധതികൾ",

        "stat_serving": "AI-അധിഷ്ഠിതമായ",

        "stat_serving_label": "സഹായം",

        "stat_languages": "൧൫+",

        "stat_languages_label": "പിന്തുണയ്ക്കുന്ന ഭാഷകൾ",

        "chat_welcome_title": "സർക്കാർ പദ്ധതി സഹായിയിലേക്ക് സ്വാഗതം",

        "chat_welcome_desc": "നിങ്ങളുടെ ഇഷ്ട ഭാഷയിൽ ഇന്ത്യൻ സർക്കാർ പദ്ധതികൾ, യോഗ്യത, ആനുകൂല്യങ്ങൾ, അപേക്ഷാ നടപടിക്രമങ്ങൾ എന്നിവ മനസ്സിലാക്കാൻ എനിക്ക് സഹായിക്കാനാകും.",

        "chat_limit_msg": "൩ സൗജന്യ സന്ദേശങ്ങൾ ബാക്കിയുണ്ട്",

        "chat_input_placeholder": "നിങ്ങളുടെ സന്ദേശം ടൈപ്പ് ചെയ്യുക...",

        "signin-title": "വീണ്ടും സ്വാഗതം",

        "signin-subtitle": "ചാറ്റ് തുടരാൻ സൈൻ ഇൻ ചെയ്യുക",

        "signin-email": "ഇമെയിൽ വിലാസം",

        "signin-btn": "സൈൻ ഇൻ →",

        "signin-loading": "സൈൻ ഇൻ ചെയ്യുന്നു...",

        "auth_lbl_password": "പാസ്‌വേഡ്",

        "auth_pl_password": "നിങ്ങളുടെ പാസ്‌വേഡ് നൽകുക",

        "auth_msg_no_account": "അക്കൗണ്ട് ഇല്ലേ?",

        "auth_link_signup": "സൈൻ അപ്പ് ചെയ്യുക",

        "auth-prompt-message": "തുടരാൻ സൈൻ ഇൻ ചെയ്യുക അല്ലെങ്കിൽ അക്കൗണ്ട് സൃഷ്ടിക്കുക",

        "forgot-password": "പാസ്‌വേഡ് മറന്നോ?",

        "sf_modal_title": "നിങ്ങൾക്ക് അനുയോജ്യമായ പദ്ധതികൾ കണ്ടെത്താൻ ഞങ്ങളെ സഹായിക്കൂ",

        "sf_h_account": "നിങ്ങളുടെ അക്കൗണ്ട് സൃഷ്ടിക്കുക",

        "sf_msg_have_account": "ഇതിനകം അക്കൗണ്ട് ഉണ്ടോ?",

        "sf_link_signin": "സൈൻ ഇൻ ചെയ്യുക",

        "sf_lbl_name": "മുഴുവൻ പേര്",

        "sf_pl_name": "നിങ്ങളുടെ പേര് നൽകുക",

        "sf_lbl_email": "ഇമെയിൽ വിലാസം",

        "sf_pl_email": "you@example.com",

        "sf_lbl_pass": "പാസ്‌വേഡ്",

        "sf_pl_pass": "കുറഞ്ഞത് 6 അക്ഷരങ്ങൾ",

        "sf_h_about": "നിങ്ങളെക്കുറിച്ച്",

        "sf_lbl_gender": "ലിംഗഭേദം",

        "sf_opt_male": "പുരുഷൻ",

        "sf_opt_female": "സ്ത്രീ",

        "sf_opt_trans": "ട്രാൻസ്‌ജെൻഡർ",

        "sf_lbl_age": "വയസ്സ്",

        "sf_opt_sel_age": "വയസ്സ് തിരഞ്ഞെടുക്കുക",

        "sf_h_loc": "സ്ഥലം",

        "sf_lbl_state": "സംസ്ഥാനം",

        "sf_opt_sel_state": "സംസ്ഥാനം തിരഞ്ഞെടുക്കുക",

        "sf_lbl_area": "പ്രദേശ തരം",

        "sf_opt_urban": "നഗരം",

        "sf_opt_rural": "ഗ്രാമം",

        "sf_h_social": "സാമൂഹിക വിവരങ്ങൾ",

        "sf_lbl_cat": "വിഭാഗം",

        "sf_cat_gen": "ജനറൽ",

        "sf_cat_obc": "ഒബിസി",

        "sf_cat_pvtg": "പിവിടിജി",

        "sf_cat_sc": "എസ്‌സി",

        "sf_cat_st": "എസ്‌ടി",

        "sf_cat_dnt": "ഡിഎൻടി",

        "sf_lbl_pwd": "ഭിന്നശേഷിക്കാരനാണോ?",

        "sf_opt_yes": "അതെ",

        "sf_opt_no": "അല്ല",

        "sf_lbl_minor": "ന്യൂനപക്ഷമാണോ?",

        "sf_h_emp": "തൊഴിലും വിദ്യാഭ്യാസവും",

        "sf_lbl_student": "വിദ്യാർത്ഥിയാണോ?",

        "sf_lbl_status": "തൊഴിൽ നില",

        "sf_emp_emp": "ഉദ്യോഗസ്ഥൻ",

        "sf_emp_unemp": "തൊഴിലില്ലാത്തവർ",

        "sf_emp_self": "സ്വയം തൊഴിൽ",

        "sf_lbl_govt": "സർക്കാർ ജീവനക്കാരനാണോ?",

        "sf_h_income": "വരുമാന വിവരങ്ങൾ",

        "sf_lbl_inc_ann": "വാർഷിക വരുമാനം (₹)",

        "sf_lbl_inc_fam": "കുടുംബ വരുമാനം (₹)",

        "sf_pl_zero": "0",

        "sf_submit_btn": "പ്രൊഫൈൽ സമർപ്പിച്ച് ചാറ്റ് ആരംഭിക്കുക",

        "sf_loading": "നിങ്ങളുടെ പ്രൊഫൈൽ സജ്ജീകരിക്കുന്നു...",

        "user-name-display": "",
        "features_title": "പ്രധാന സവിശേഷതകൾ",

        "feature_secure_profile": "സുരക്ഷിത പ്രൊഫൈല്",

        "feature_secure_desc": "നിങ്ങളുടെ ഉപയോക്താവിന്റെ പ്രൊഫൈല് ഐഡന്റിറ്റി ഉറപ്പാക്കുക, ഒപ്പം പ്രൊഫൈല് ആനുകൂല്യങ്ങള് ഉറപ്പാക്കുക.",

        "feature_direct_benefit": "നേരിട്ടുള്ള ആനുകൂല്യ കൈമാറ്റം",

        "feature_direct_desc": "നേരിട്ടുള്ള ആനുകൂല്യം കൈമാറ്റം",

        "feature_multilingual": "ബഹുഭാഷാ",

        "feature_multilingual_desc": "സ്വീകരണത്തിലും ഇടപാടുകളിലും മികച്ച പ്രതികരണത്തിനുള്ള ബഹുഭാഷാ ശേഷി.",

        "feature_personalized": "വ്യക്തിഗതമാക്കിയവ",

        "feature_personalized_desc": "നിങ്ങളുടെ ഐഡന്റിറ്റിയും പ്രൊഫൈലും ഉറപ്പാക്കുക",

        "featured_title": "സവിശേഷ പദ്ധതികൾ",

        "scheme_agriculture": "കാർഷികവും ഗ്രാമീണവും",

        "scheme_agriculture_count": "൮൧൮ പദ്ധതികൾ",

        "scheme_banking": "ബാങ്കിംഗ് , ധനകാര്യ മേഖല",

        "scheme_banking_count": "൩൧൭ പദ്ധതികൾ",

        "scheme_business": "വ്യാപാരം",

        "scheme_business_count": "൭൦൫ പദ്ധതികൾ",

        "scheme_education": "വിദ്യാഭ്യാസം",

        "scheme_education_count": "൧൦൭൬ പദ്ധതികൾ",

        "scheme_health": "ആരോഗ്യം",

        "scheme_health_count": "൨൭൪ പദ്ധതികൾ",

        "scheme_housing": "ഭവനങ്ങൾ",

        "scheme_housing_count": "൧൨൮ പദ്ധതികൾ",

        "scheme_public_safety": "പൊതു സുരക്ഷ",

        "scheme_public_safety_count": "൨൯ പദ്ധതികൾ",

        "scheme_science": "ശാസ്ത്രവും സാങ്കേതികവിദ്യയും",

        "scheme_science_count": "൧൦൦ പദ്ധതികൾ",

        "scheme_skills": "വൈദഗ്ധ്യം",

        "scheme_skills_count": "൩൬൮ പദ്ധതികൾ",

        "scheme_social_welfare": "സാമൂഹിക ക്ഷേമം",

        "scheme_social_welfare_count": "൧൪൫൬ പദ്ധതികൾ",

        "scheme_sports": "സ്പോർട്സ്",

        "scheme_sports_count": "൨൪൮ പദ്ധതികൾ",

        "scheme_transport": "ഗതാഗതം",

        "scheme_transport_count": "൮൬ പദ്ധതികൾ",

        "scheme_travel": "യാത്ര",

        "scheme_travel_count": "൯൧ പദ്ധതികൾ",

        "scheme_utility": "പ്രയോജനം",

        "scheme_utility_count": "൫൮ പദ്ധതികൾ",

        "scheme_women": "സ്ത്രീകളും കുട്ടികളും",

        "scheme_women_count": "൪൫൮ പദ്ധതികൾ",

        "how_title": "അത് എങ്ങനെ പ്രവർത്തിക്കുന്നു",

        "step1_title": "നിങ്ങളുടെ വിവരങ്ങൾ നല് കുക",

        "step2_title": "വ്യക്തിഗത സ്കീമുകൾ നേടുക",

        "step3_title": "പദ്ധതിയുടെ പ്രയോജനം",

        "hero-signup": "സൈൻ അപ്പ് ചെയ്യുക",

        "hero-continue": "അതിഥിയായി തുടരുക",

        "stat_ai": "AI",

        "stat_ai_label": "വൈദ്യുതി",

        "stat_languages_new": "൧൨+",

        "stat_languages_interactive": "ഭാഷകൾ, സംവേദനാത്മക",


        // New button translations for ml_IN
        "nav_signin": "സൈൻ ഇൻ ചെയ്യുക",

        "start_chatting": "ചാറ്റ് തുടങ്ങുക",

        "greeting_hello": "ഹലോ .",

    },

    "pa_IN": {
        "app_title": "ਸਰਕਾਰੀ ਯੋਜਨਾ ਸਹਾਇਕ",

        "logo-text": "ਸਰਕਾਰੀ ਯੋਜਨਾ ਸਹਾਇਕ",

        "signin": "ਸਾਈਨ ਇਨ →",

        "logout": "ਲੌਗ ਆਉਟ",

        "edit_profile": "ਪ੍ਰੋਫਾਈਲ ਸੰਪਾਦਿਤ ਕਰੋ",

        "status-online": "ਔਨਲਾਈਨ",

        "hero-badge": "ਸੁਰੱਖਿਅਤ, ਸਰਲ, ਨਿਰਵਿਘਨ",

        "hero-accent": "ਫਾਸਟ-ਟ੍ਰੈਕ",

        "hero-title": "ਸਰਕਾਰੀ ਲਾਭ\<br>ਪ੍ਰਾਪਤ ਕਰੋ",

        "cta-btn": "ਯੋਜਨਾਵਾਂ ਖੋਜੋ",

        "skip-btn": "ਮਹਿਮਾਨ ਵਜੋਂ ਜਾਰੀ ਰੱਖੋ →",

        "tab_new": "ਨਵਾਂ ਵਰਤੋਂਕਾਰ",

        "tab_signin": "ਸਾਈਨ ਇਨ",

        "quick_lang": "ਤੁਹਾਡੀ ਭਾਸ਼ਾ",

        "quick_state": "ਤੁਹਾਡਾ ਰਾਜ",

        "quick_all_india": "ਪੂਰਾ ਭਾਰਤ",

        "quick_explore": "ਯੋਜਨਾਵਾਂ ਦੀ ਪੜਚੋਲ ਕਰੋ",

        "stat_schemes": "੫੦੦+",

        "stat_schemes_label": "ਉਪਲਬਧ ਯੋਜਨਾਵਾਂ",

        "stat_serving": "AI-ਸੰਚਾਲਿਤ",

        "stat_serving_label": "ਸਹਾਇਤਾ",

        "stat_languages": "੧੫+",

        "stat_languages_label": "ਸਮਰਥਿਤ ਭਾਸ਼ਾਵਾਂ",

        "chat_welcome_title": "ਸਰਕਾਰੀ ਯੋਜਨਾ ਸਹਾਇਕ ਵਿੱਚ ਤੁਹਾਡਾ ਸੁਆਗਤ ਹੈ",

        "chat_welcome_desc": "ਮੈਂ ਤੁਹਾਡੀ ਪਸੰਦੀਦਾ ਭਾਸ਼ਾ ਵਿੱਚ ਭਾਰਤੀ ਸਰਕਾਰੀ ਯੋਜਨਾਵਾਂ, ਯੋਗਤਾ, ਲਾਭ ਅਤੇ ਅਰਜ਼ੀ ਪ੍ਰਕਿਰਿਆ ਨੂੰ ਸਮਝਣ ਵਿੱਚ ਤੁਹਾਡੀ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ।",

        "chat_limit_msg": "੩ ਮੁਫਤ ਸੰਦੇਸ਼ ਬਾਕੀ",

        "chat_input_placeholder": "ਆਪਣਾ ਸੰਦੇਸ਼ ਟਾਈਪ ਕਰੋ...",

        "signin-title": "ਜੀ ਆਇਆਂ ਨੂੰ",

        "signin-subtitle": "ਗੱਲਬਾਤ ਜਾਰੀ ਰੱਖਣ ਲਈ ਸਾਈਨ ਇਨ ਕਰੋ",

        "signin-email": "ਈਮੇਲ ਪਤਾ",

        "signin-btn": "ਸਾਈਨ ਇਨ →",

        "signin-loading": "ਸਾਈਨ ਇਨ ਹੋ ਰਿਹਾ ਹੈ...",

        "auth_lbl_password": "ਪਾਸਵਰਡ",

        "auth_pl_password": "ਆਪਣਾ ਪਾਸਵਰਡ ਦਰਜ ਕਰੋ",

        "auth_msg_no_account": "ਖਾਤਾ ਨਹੀਂ ਹੈ?",

        "auth_link_signup": "ਸਾਈਨ ਅਪ ਕਰੋ",

        "auth-prompt-message": "ਜਾਰੀ ਰੱਖਣ ਲਈ ਸਾਈਨ ਇਨ ਕਰੋ ਜਾਂ ਖਾਤਾ ਬਣਾਓ",

        "forgot-password": "ਪਾਸਵਰਡ ਭੁੱਲ ਗਏ?",

        "sf_modal_title": "ਤੁਹਾਡੇ ਲਈ ਸਭ ਤੋਂ ਵਧੀਆ ਯੋਜਨਾਵਾਂ ਲੱਭਣ ਵਿੱਚ ਸਾਡੀ ਮਦਦ ਕਰੋ",

        "sf_h_account": "ਆਪਣਾ ਖਾਤਾ ਬਣਾਓ",

        "sf_msg_have_account": "ਪਹਿਲਾਂ ਹੀ ਖਾਤਾ ਹੈ?",

        "sf_link_signin": "ਸਾਈਨ ਇਨ ਕਰੋ",

        "sf_lbl_name": "ਪੂਰਾ ਨਾਮ",

        "sf_pl_name": "ਆਪਣਾ ਨਾਮ ਦਰਜ ਕਰੋ",

        "sf_lbl_email": "ਈਮੇਲ ਪਤਾ",

        "sf_pl_email": "you@example.com",

        "sf_lbl_pass": "ਪਾਸਵਰਡ",

        "sf_pl_pass": "ਘੱਟੋ-ਘੱਟ 6 ਅੱਖਰ",

        "sf_h_about": "ਤੁਹਾਡੇ ਬਾਰੇ",

        "sf_lbl_gender": "ਲਿੰਗ",

        "sf_opt_male": "ਮਰਦ",

        "sf_opt_female": "ਔਰਤ",

        "sf_opt_trans": "ਟ੍ਰਾਂਸਜੈਂਡਰ",

        "sf_lbl_age": "ਉਮਰ",

        "sf_opt_sel_age": "ਉਮਰ ਚੁਣੋ",

        "sf_h_loc": "ਸਥਾਨ",

        "sf_lbl_state": "ਰਾਜ",

        "sf_opt_sel_state": "ਰਾਜ ਚੁਣੋ",

        "sf_lbl_area": "ਖੇਤਰ ਦੀ ਕਿਸਮ",

        "sf_opt_urban": "ਸ਼ਹਿਰੀ",

        "sf_opt_rural": "ਪੇਂਡੂ",

        "sf_h_social": "ਸਮਾਜਿਕ ਵੇਰਵੇ",

        "sf_lbl_cat": "ਸ਼੍ਰੇਣੀ",

        "sf_cat_gen": "ਜਨਰਲ",

        "sf_cat_obc": "ਓਬੀਸੀ",

        "sf_cat_pvtg": "ਪੀਵੀਟੀਜੀ",

        "sf_cat_sc": "ਐਸਸੀ",

        "sf_cat_st": "ਐਸਟੀ",

        "sf_cat_dnt": "ਡੀਐਨਟੀ",

        "sf_lbl_pwd": "ਕੀ ਵਿਕਲਾਂਗ ਹੋ?",

        "sf_opt_yes": "ਹਾਂ",

        "sf_opt_no": "ਨਹੀਂ",

        "sf_lbl_minor": "ਕੀ ਘੱਟ ਗਿਣਤੀ ਹੋ?",

        "sf_h_emp": "ਰੁਜ਼ਗਾਰ ਅਤੇ ਸਿੱਖਿਆ",

        "sf_lbl_student": "ਕੀ ਵਿਦਿਆਰਥੀ ਹੋ?",

        "sf_lbl_status": "ਰੁਜ਼ਗਾਰ ਸਥਿਤੀ",

        "sf_emp_emp": "ਨੌਕਰੀਪੇਸ਼ਾ",

        "sf_emp_unemp": "ਬੇਰੁਜ਼ਗਾਰ",

        "sf_emp_self": "ਸਵੈ-ਰੁਜ਼ਗਾਰ",

        "sf_lbl_govt": "ਕੀ ਸਰਕਾਰੀ ਕਰਮਚਾਰੀ ਹੋ?",

        "sf_h_income": "ਆਮਦਨ ਵੇਰਵੇ",

        "sf_lbl_inc_ann": "ਸਾਲਾਨਾ ਆਮਦਨ (₹)",

        "sf_lbl_inc_fam": "ਪਰਿਵਾਰਕ ਆਮਦਨ (₹)",

        "sf_pl_zero": "0",

        "sf_submit_btn": "ਪ੍ਰੋਫਾਈਲ ਜਮ੍ਹਾਂ ਕਰੋ ਅਤੇ ਗੱਲਬਾਤ ਸ਼ੁਰੂ ਕਰੋ",

        "sf_loading": "ਤੁਹਾਡਾ ਪ੍ਰੋਫਾਈਲ ਸੈੱਟ ਕੀਤਾ ਜਾ ਰਿਹਾ ਹੈ...",

        "user-name-display": "",
        "features_title": "ਮੁੱਖ ਵਿਸ਼ੇਸ਼ਤਾਵਾਂ",

        "feature_secure_profile": "ਸੁਰੱਖਿਅਤ ਪ੍ਰੋਫਾਈਲ",

        "feature_secure_desc": "ਆਪਣੇ ਉਪਭੋਗਤਾ ਦੀ ਪ੍ਰੋਫਾਈਲ ਪਛਾਣ ਨੂੰ ਸੁਰੱਖਿਅਤ ਕਰੋ, ਅਤੇ ਪ੍ਰੋਫਾਈਲ ਲਾਭਾਂ ਨੂੰ ਸੁਰੱਖਿਅਤ ਕਰੋ.",

        "feature_direct_benefit": "ਸਿੱਧੇ ਲਾਭ ਟ੍ਰਾਂਸਫਰ",

        "feature_direct_desc": "ਸਿੱਧੇ ਲਾਭ ਦਾ ਤਬਾਦਲਾ",

        "feature_multilingual": "ਬਹੁਭਾਸ਼ਾਈ",

        "feature_multilingual_desc": "ਅਪਣਾਉਣ ਅਤੇ ਲੈਣ-ਦੇਣ ਦੇ ਜਵਾਬ ਵਿੱਚ ਸਭ ਤੋਂ ਵਧੀਆ ਬਹੁਭਾਸ਼ਾਈ ਸਮਰੱਥਾ.",

        "feature_personalized": "ਵਿਅਕਤੀਗਤ",

        "feature_personalized_desc": "ਆਪਣੀ ਪਛਾਣ ਅਤੇ ਪ੍ਰੋਫਾਈਲ ਲਾਭਾਂ ਨੂੰ ਸੁਰੱਖਿਅਤ ਕਰੋ",

        "featured_title": "ਵਿਸ਼ੇਸ਼ ਯੋਜਨਾਵਾਂ",

        "scheme_agriculture": "ਖੇਤੀਬਾੜੀ ਅਤੇ ਦਿਹਾਤੀ",

        "scheme_agriculture_count": "੮੧੮ ਯੋਜਨਾਵਾਂ",

        "scheme_banking": "ਬੈਂਕਿੰਗ ਅਤੇ ਵਿੱਤ",

        "scheme_banking_count": "੩੧੭ ਯੋਜਨਾਵਾਂ",

        "scheme_business": "ਕਾਰੋਬਾਰ",

        "scheme_business_count": "੭੦੫ ਯੋਜਨਾਵਾਂ",

        "scheme_education": "ਸਿੱਖਿਆ",

        "scheme_education_count": "੧੦੭੬ ਯੋਜਨਾਵਾਂ",

        "scheme_health": "ਸਿਹਤ",

        "scheme_health_count": "੨੭੪ ਯੋਜਨਾਵਾਂ",

        "scheme_housing": "ਰਿਹਾਇਸ਼",

        "scheme_housing_count": "੧੨੮ ਯੋਜਨਾਵਾਂ",

        "scheme_public_safety": "ਜਨਤਕ ਸੁਰੱਖਿਆ",

        "scheme_public_safety_count": "੨੯ ਯੋਜਨਾਵਾਂ",

        "scheme_science": "ਵਿਗਿਆਨ ਅਤੇ ਆਈਟੀ",

        "scheme_science_count": "੧੦੦ ਯੋਜਨਾਵਾਂ",

        "scheme_skills": "ਹੁਨਰ",

        "scheme_skills_count": "੩੬੮ ਯੋਜਨਾਵਾਂ",

        "scheme_social_welfare": "ਸਮਾਜਿਕ ਭਲਾਈ",

        "scheme_social_welfare_count": "੧੪੫੬ ਯੋਜਨਾਵਾਂ",

        "scheme_sports": "ਖੇਡਾਂ",

        "scheme_sports_count": "੨੪੮ ਯੋਜਨਾਵਾਂ",

        "scheme_transport": "ਆਵਾਜਾਈ",

        "scheme_transport_count": "੮੬ ਯੋਜਨਾਵਾਂ",

        "scheme_travel": "ਯਾਤਰਾ",

        "scheme_travel_count": "੯੧ ਯੋਜਨਾਵਾਂ",

        "scheme_utility": "ਉਪਯੋਗਤਾ",

        "scheme_utility_count": "੫੮ ਯੋਜਨਾਵਾਂ",

        "scheme_women": "ਔਰਤਾਂ ਅਤੇ ਬੱਚੇ",

        "scheme_women_count": "੪੫੮ ਯੋਜਨਾਵਾਂ",

        "how_title": "ਇਹ ਕਿਵੇਂ ਕੰਮ ਕਰਦਾ ਹੈ",

        "step1_title": "ਆਪਣੀ ਜਾਣਕਾਰੀ ਦਿਓ",

        "step2_title": "ਵਿਅਕਤੀਗਤ ਯੋਜਨਾਵਾਂ ਪ੍ਰਾਪਤ ਕਰੋ",

        "step3_title": "ਯੋਜਨਾ ਦੇ ਲਾਭ",

        "hero-signup": "ਰਜਿਸਟਰ ਕਰੋ",

        "hero-continue": "ਮਹਿਮਾਨ ਬਣੇ ਰਹੋ",

        "stat_ai": "ਏਆਈ",

        "stat_ai_label": "ਪਾਵਰ",

        "stat_languages_new": "੧੨+",

        "stat_languages_interactive": "ਭਾਸ਼ਾਵਾਂ, ਇੰਟਰਐਕਟਿਵ",


        // New button translations for pa_IN
        "nav_signin": "ਸਾਈਨ ਇਨ ਕਰੋ",

        "start_chatting": "ਗੱਲਬਾਤ ਸ਼ੁਰੂ ਕਰੋ",

        "greeting_hello": "ਹੈਲੋ",

    },

    "or_IN": {
        // App & Navigation
        "app_title": "ସରକାରୀ ଯୋଜନା ସହାୟକ",

        "logo-text": "ସରକାରୀ ଯୋଜନା ସହାୟକ",

        "signin": "ସାଇନ୍ ଇନ୍ →",

        "logout": "ଲଗ୍ ଆଉଟ୍",

        "edit_profile": "ପ୍ରୋଫାଇଲ୍ ସଂପାଦନା କରନ୍ତୁ",

        "status-online": "ଅନଲାଇନ୍",


        // Hero Section
        "hero-badge": "ସୁରକ୍ଷିତ, ସରଳ, ନିର୍ବିଘ୍ନ",

        "hero-accent": "ଫାଷ୍ଟ-ଟ୍ରାକ",

        "hero-title": "ସରକାରୀ ସୁବିଧା\<br>ପ୍ରାପ୍ତ କରନ୍ତୁ",

        "cta-btn": "ଯୋଜନା ଖୋଜନ୍ତୁ",

        "skip-btn": "ଅତିଥି ଭାବେ ଜାରି ରଖନ୍ତୁ →",


        // Quick Start Card
        "tab_new": "ନୂଆ ବ୍ୟବହାରକାରୀ",

        "tab_signin": "ସାଇନ୍ ଇନ୍",

        "quick_lang": "ଆପଣଙ୍କ ଭାଷା",

        "quick_state": "ଆପଣଙ୍କ ରାଜ୍ୟ",

        "quick_all_india": "ସମଗ୍ର ଭାରତ",

        "quick_explore": "ଯୋଜନା ଖୋଜନ୍ତୁ",


        // Statistics
        "stat_schemes": "୫୦୦+",

        "stat_schemes_label": "ଉପଲବ୍ଧ ଯୋଜନା",

        "stat_serving": "AI-ଚାଳିତ",

        "stat_serving_label": "ସହାୟତା",

        "stat_languages": "୧୫+",

        "stat_languages_label": "ସମର୍ଥିତ ଭାଷା",


        // Chat Page
        "chat_welcome_title": "ସରକାରୀ ଯୋଜନା ସହାୟକକୁ ସ୍ୱାଗତ",

        "chat_welcome_desc": "ମୁଁ ଆପଣଙ୍କୁ ଆପଣଙ୍କ ପସନ୍ଦର ଭାଷାରେ ଭାରତୀୟ ସରକାରୀ ଯୋଜନା, ଯୋଗ୍ୟତା, ଲାଭ ଏବଂ ଆବେଦନ ପ୍ରକ୍ରିୟା ବୁଝିବାରେ ସାହାଯ୍ୟ କରିପାରିବି।",

        "chat_limit_msg": "୩ଟି ମାଗଣା ସନ୍ଦେଶ ବାକି",

        "chat_input_placeholder": "ଆପଣଙ୍କ ସନ୍ଦେଶ ଟାଇପ୍ କରନ୍ତୁ...",


        // Auth Modal
        "signin-title": "ପୁଣି ସ୍ୱାଗତ",

        "signin-subtitle": "ଚାଟ୍ ଜାରି ରଖିବାକୁ ସାଇନ୍ ଇନ୍ କରନ୍ତୁ",

        "signin-email": "ଇମେଲ୍ ଠିକଣା",

        "signin-btn": "ସାଇନ୍ ଇନ୍ →",

        "signin-loading": "ସାଇନ୍ ଇନ୍ ହେଉଛି...",

        "auth_lbl_password": "ପାସୱାର୍ଡ",

        "auth_pl_password": "ଆପଣଙ୍କ ପାସୱାର୍ଡ ପ୍ରବେଶ କରନ୍ତୁ",

        "auth_msg_no_account": "ଆକାଉଣ୍ଟ ନାହିଁ?",

        "auth_link_signup": "ସାଇନ୍ ଅପ୍ କରନ୍ତୁ",

        "auth-prompt-message": "ଚାଟ୍ ଜାରି ରଖିବାକୁ ସାଇନ୍ ଇନ୍ କରନ୍ତୁ କିମ୍ବା ଆକାଉଣ୍ଟ ତିଆରି କରନ୍ତୁ",

        "forgot-password": "ପାସୱାର୍ଡ ଭୁଲିଗଲେ?",


        // Scheme Finder Modal
        "sf_modal_title": "ଆପଣଙ୍କ ପାଇଁ ସର୍ବୋତ୍ତମ ଯୋଜନା ଖୋଜିବାରେ ଆମକୁ ସାହାଯ୍ୟ କରନ୍ତୁ",

        "sf_h_account": "ଆପଣଙ୍କ ଆକାଉଣ୍ଟ ତିଆରି କରନ୍ତୁ",

        "sf_msg_have_account": "ପୂର୍ବରୁ ଆକାଉଣ୍ଟ ଅଛି?",

        "sf_link_signin": "ସାଇନ୍ ଇନ୍ କରନ୍ତୁ",

        "sf_lbl_name": "ସମ୍ପୂର୍ଣ୍ଣ ନାମ",

        "sf_pl_name": "ଆପଣଙ୍କ ନାମ ପ୍ରବେଶ କରନ୍ତୁ",

        "sf_lbl_email": "ଇମେଲ୍ ଠିକଣା",

        "sf_pl_email": "you@example.com",

        "sf_lbl_pass": "ପାସୱାର୍ଡ",

        "sf_pl_pass": "ନ୍ୟୁନତମ 6 ଅକ୍ଷର",

        "sf_h_about": "ଆପଣଙ୍କ ବିଷୟରେ",

        "sf_lbl_gender": "ଲିଙ୍ଗ",

        "sf_opt_male": "ପୁରୁଷ",

        "sf_opt_female": "ମହିଳା",

        "sf_opt_trans": "ତୃତୀୟ ଲିଙ୍ଗ",

        "sf_lbl_age": "ବୟସ",

        "sf_opt_sel_age": "ବୟସ ଚୟନ କରନ୍ତୁ",

        "sf_h_loc": "ଅବସ୍ଥାନ",

        "sf_lbl_state": "ରାଜ୍ୟ",

        "sf_opt_sel_state": "ରାଜ୍ୟ ଚୟନ କରନ୍ତୁ",

        "sf_lbl_area": "କ୍ଷେତ୍ର ପ୍ରକାର",

        "sf_opt_urban": "ସହରୀ",

        "sf_opt_rural": "ଗ୍ରାମୀଣ",

        "sf_h_social": "ସାମାଜିକ ବିବରଣୀ",

        "sf_lbl_cat": "ଶ୍ରେଣୀ",

        "sf_cat_gen": "ସାଧାରଣ",

        "sf_cat_obc": "ଓବିସି",

        "sf_cat_pvtg": "ପିଭିଟିଜି",

        "sf_cat_sc": "ଏସ୍‌ସି",

        "sf_cat_st": "ଏସ୍‌ଟି",

        "sf_cat_dnt": "ଡିଏନ୍‌ଟି",

        "sf_lbl_pwd": "ଅକ୍ଷମ ବ୍ୟକ୍ତି?",

        "sf_opt_yes": "ହଁ",

        "sf_opt_no": "ନା",

        "sf_lbl_minor": "ସଂଖ୍ୟାଲଘୁ?",

        "sf_h_emp": "ନିଯୁକ୍ତି ଏବଂ ଶିକ୍ଷା",

        "sf_lbl_student": "ଛାତ୍ର?",

        "sf_lbl_status": "ନିଯୁକ୍ତି ସ୍ଥିତି",

        "sf_emp_emp": "ନିଯୁକ୍ତ",

        "sf_emp_unemp": "ବେରୋଜଗାର",

        "sf_emp_self": "ସ୍ୱ-ନିଯୁକ୍ତ",

        "sf_lbl_govt": "ସରକାରୀ କର୍ମଚାରୀ?",

        "sf_h_income": "ଆୟ ବିବରଣୀ",

        "sf_lbl_inc_ann": "ବାର୍ଷିକ ଆୟ (₹)",

        "sf_lbl_inc_fam": "ପାରିବାରିକ ଆୟ (₹)",

        "sf_pl_zero": "0",

        "sf_submit_btn": "ପ୍ରୋଫାଇଲ୍ ଦାଖଲ କରନ୍ତୁ ଏବଂ ଚାଟ୍ ଆରମ୍ଭ କରନ୍ତୁ",

        "sf_loading": "ଆପଣଙ୍କ ପ୍ରୋଫାଇଲ୍ ସେଟ୍ ହେଉଛି...",

        "user-name-display": "",
        "features_title": "ମୂଳ ବୈଶିଷ୍ଟ୍ୟ",

        "feature_secure_profile": "ନିରାପଦ ପ୍ରୋଫାଇଲ",

        "feature_secure_desc": "ଆପଣଙ୍କର ବ୍ୟବହାରକାରୀଙ୍କ ପ୍ରୋଫାଇଲ୍ ପରିଚୟକୁ ସୁରକ୍ଷିତ କରନ୍ତୁ, ଏବଂ ପ୍ରୋଫାଇଲ୍ ଲାଭକୁ ସୁରକ୍ଷିତ କରନ୍ତୁ ।",

        "feature_direct_benefit": "ସିଧାସଳଖ ଲାଭ ହସ୍ତାନ୍ତର",

        "feature_direct_desc": "ସିଧାସଳଖ ଲାଭ ହସ୍ତାନ୍ତର",

        "feature_multilingual": "ବହୁଭାଷୀ",

        "feature_multilingual_desc": "ଗ୍ରହଣ ଏବଂ କାରବାରର ଉତ୍ତମ ଉତ୍ତର ପାଇଁ ବହୁଭାଷୀ କ୍ଷମତା।",

        "feature_personalized": "ବ୍ୟକ୍ତିଗତକୃତ",

        "feature_personalized_desc": "ଆପଣଙ୍କର ପରିଚୟ ଏବଂ ପ୍ରୋଫାଇଲ ସୁବିଧା ନିଶ୍ଚିତ କରନ୍ତୁ",

        "featured_title": "ବିଶେଷ ଯୋଜନା",

        "scheme_agriculture": "କୃଷି ଓ ଗ୍ରାମାଞ୍ଚଳ",

        "scheme_agriculture_count": "୮୧୮ ଯୋଜନା",

        "scheme_banking": "ବ୍ୟାଙ୍କିଙ୍ଗ ଓ ଅର୍ଥ",

        "scheme_banking_count": "୩୧୭ ଯୋଜନା",

        "scheme_business": "ବ୍ୟବସାୟ",

        "scheme_business_count": "୭୦୫ ଯୋଜନା",

        "scheme_education": "ଶିକ୍ଷା",

        "scheme_education_count": "୧୦୭୬ ଯୋଜନା",

        "scheme_health": "ସ୍ୱାସ୍ଥ୍ୟ",

        "scheme_health_count": "୨୭୪ ଯୋଜନା",

        "scheme_housing": "ଆବାସ",

        "scheme_housing_count": "୧୨୮ ଯୋଜନା",

        "scheme_public_safety": "ଜନସାଧାରଣଙ୍କ ସୁରକ୍ଷା",

        "scheme_public_safety_count": "୨୯ ଯୋଜନା",

        "scheme_science": "ବିଜ୍ଞାନ ଓ ଆଇଟି",

        "scheme_science_count": "ଶହେ ଯୋଜନା",

        "scheme_skills": "ଦକ୍ଷତା",

        "scheme_skills_count": "୩୬୮ ଯୋଜନା",

        "scheme_social_welfare": "ସାମାଜିକ କଲ୍ୟାଣ",

        "scheme_social_welfare_count": "୧୪୫୬ ଯୋଜନା",

        "scheme_sports": "କ୍ରୀଡ଼ା",

        "scheme_sports_count": "୨୪୮ ଯୋଜନା",

        "scheme_transport": "ପରିବହନ",

        "scheme_transport_count": "୮୬ ଯୋଜନା",

        "scheme_travel": "ଯାତ୍ରା",

        "scheme_travel_count": "୯୧ ଯୋଜନା",

        "scheme_utility": "ଉପଯୋଗିତା",

        "scheme_utility_count": "୫୮ ଯୋଜନା",

        "scheme_women": "ମହିଳା ଓ ଶିଶୁ",

        "scheme_women_count": "୪୫୮ ଯୋଜନା",

        "how_title": "ଏହା କିପରି କାମ କରେ",

        "step1_title": "ନିଜର ସୂଚନା ଦିଅନ୍ତୁ",

        "step2_title": "ବ୍ୟକ୍ତିଗତ ଯୋଜନାଗୁଡିକ ପ୍ରାପ୍ତ କରନ୍ତୁ",

        "step3_title": "ଯୋଜନାର ଲାଭ",

        "hero-signup": "ପଞ୍ଜୀକରଣ କରନ୍ତୁ",

        "hero-continue": "ଅତିଥି ହୋଇ ରହନ୍ତୁ",

        "stat_ai": "ଏଆଇ",

        "stat_ai_label": "ଚାଳିତ",

        "stat_languages_new": "୧୨+",

        "stat_languages_interactive": "ଭାଷା, ପାରସ୍ପରିକ",


        // New button translations for or_IN
        "nav_signin": "ସାଇନ୍ ଇନ୍ କରନ୍ତୁ",

        "start_chatting": "ଚାଟିଂ ଆରମ୍ଭ କରନ୍ତୁ",

        "greeting_hello": "ନମସ୍କାର ।",

    },

    "as_IN": {
        "app_title": "চৰকাৰী আঁচনি সহায়ক",

        "logo-text": "চৰকাৰী আঁচনি সহায়ক",

        "signin": "চাইন ইন →",

        "logout": "লগ আউট",

        "edit_profile": "প্ৰফাইল সম্পাদনা কৰক",

        "status-online": "অনলাইন",

        "hero-badge": "সুৰক্ষিত, সৰল, নিৰ্বিঘ্ন",

        "hero-accent": "ফাষ্ট-ট্ৰেক",

        "hero-title": "চৰকাৰী সুবিধাৰ বাবে",

        "cta-btn": "আঁচনি অন্বেষণ কৰক",

        "skip-btn": "অতিথি হিচাপে আগবাঢ়ক →",

        "tab_new": "নতুন ব্যৱহাৰকাৰী",

        "tab_signin": "চাইন ইন",

        "quick_lang": "আপোনাৰ ভাষা",

        "quick_state": "আপোনাৰ ৰাজ্য",

        "quick_all_india": "সমগ্ৰ ভাৰত",

        "quick_explore": "আঁচনি অন্বেষণ",

        "stat_schemes": "৫০০+",

        "stat_schemes_label": "উপলব্ধ আঁচনি",

        "stat_serving": "AI-চালিত",

        "stat_serving_label": "সহায়",

        "stat_languages": "১৫+",

        "stat_languages_label": "সমৰ্থিত ভাষা",

        "chat_welcome_title": "চৰকাৰী আঁচনি সহায়কলৈ স্বাগতম",

        "chat_welcome_desc": "মই আপোনাক আপোনাৰ পচন্দৰ ভাষাত ভাৰতীয় চৰকাৰী আঁচনি, যোগ্যতা, লাভালাভ আৰু আবেদন প্ৰক্ৰিয়া বুজাত সহায় কৰিব পাৰো।",

        "chat_limit_msg": "৩টা বিনামূলীয়া বাৰ্তা বাকী",

        "chat_input_placeholder": "আপোনাৰ বাৰ্তা টাইপ কৰক...",

        "signin-title": "পুনৰ স্বাগতম",

        "signin-subtitle": "চেট অব্যাহত ৰাখিবলৈ চাইল ইন কৰক",

        "signin-email": "ই-মেইল ঠিকনা",

        "signin-btn": "চাইন ইন →",

        "signin-loading": "চাইন ইন হৈ আছে...",

        "auth_lbl_password": "পাছৱৰ্ড",

        "auth_pl_password": "আপোনাৰ পাছৱৰ্ড লিখক",

        "auth_msg_no_account": "একাউণ্ট নাই নেকি?",

        "auth_link_signup": "চাইন আপ কৰক",

        "auth-prompt-message": "অব্যাহত ৰাখিবলৈ চাইল ইন বা একাউণ্ট সৃষ্টি কৰক",

        "forgot-password": "পাছৱৰ্ড পাহৰি গৈছে?",

        "sf_modal_title": "আপোনাৰ বাবে শ্ৰেষ্ঠ আঁচনি বিচাৰি উলিওৱাত আমাক সহায় কৰক",

        "sf_h_account": "আপোনাৰ একাউণ্ট সৃষ্টি কৰক",

        "sf_msg_have_account": "ইতিমধ্যে একাউণ্ট আছে?",

        "sf_link_signin": "চাইন ইন কৰক",

        "sf_lbl_name": "সম্পূৰ্ণ নাম",

        "sf_pl_name": "আপোনাৰ নাম লিখক",

        "sf_lbl_email": "ই-মেইল ঠিকনা",

        "sf_pl_email": "you@example.com",

        "sf_lbl_pass": "পাছৱৰ্ড",

        "sf_pl_pass": "কমেও 6টা আখৰ",

        "sf_h_about": "আপোনাৰ বিষয়ে",

        "sf_lbl_gender": "লিংগ",

        "sf_opt_male": "পুৰুষ",

        "sf_opt_female": "মহিলা",

        "sf_opt_trans": "তৃতীয় লিংগ",

        "sf_lbl_age": "বয়স",

        "sf_opt_sel_age": "বয়স নিৰ্বাচন কৰক",

        "sf_h_loc": "স্থান",

        "sf_lbl_state": "ৰাজ্য",

        "sf_opt_sel_state": "ৰাজ্য নিৰ্বাচন কৰক",

        "sf_lbl_area": "এলাকাৰ ধৰণ",

        "sf_opt_urban": "নগৰীয়া",

        "sf_opt_rural": "গ্ৰাম্য",

        "sf_h_social": "সামাজিক বিৱৰণ",

        "sf_lbl_cat": "শ্ৰেণী",

        "sf_cat_gen": "সাধাৰণ",

        "sf_cat_obc": "অ'বিচি",

        "sf_cat_pvtg": "পিভিটিজি",

        "sf_cat_sc": "অনুসূচিত জাতি",

        "sf_cat_st": "অনুসূচিত জনজাতি",

        "sf_cat_dnt": "ডিএনটি",

        "sf_lbl_pwd": "প্রতিবন্ধী নেকি?",

        "sf_opt_yes": "হয়",

        "sf_opt_no": "নহয়",

        "sf_lbl_minor": "সংখ্যালঘু নেকি?",

        "sf_h_emp": "নিযুক্তি আৰু শিক্ষা",

        "sf_lbl_student": "ছাত্ৰ নেকি?",

        "sf_lbl_status": "নিযুক্তিৰ স্থিতি",

        "sf_emp_emp": "চাকৰিয়াল",

        "sf_emp_unemp": "নিবনুৱা",

        "sf_emp_self": "স্ব-নিযোজিত",

        "sf_lbl_govt": "চৰকাৰী কৰ্মচাৰী নেকি?",

        "sf_h_income": "আয়ৰ বিৱৰণ",

        "sf_lbl_inc_ann": "বাৰ্ষিক আয় (₹)",

        "sf_lbl_inc_fam": "পৰিয়ালৰ আয় (₹)",

        "sf_pl_zero": "0",

        "sf_submit_btn": "প্ৰফাইল জমা দিয়ক আৰু চেট আৰম্ভ কৰক",

        "sf_loading": "আপোনাৰ প্ৰফাইল ছেট কৰা হৈছে...",

        "user-name-display": "",
        "features_title": "প্ৰধান বৈশিষ্ট্যসমূহ",

        "feature_secure_profile": "সুৰক্ষিত প্ৰফাইল",

        "feature_secure_desc": "আপোনাৰ ব্যৱহাৰকৰ্তাৰ প্ৰফাইল পৰিচয় সুৰক্ষিত কৰক, আৰু প্ৰফাইল সুবিধা সুৰক্ষিত কৰক।",

        "feature_direct_benefit": "প্ৰত্যক্ষ লাভৰ হস্তান্তৰ",

        "feature_direct_desc": "প্ৰত্যক্ষ উপকাৰিতাৰ পৰিবৰ্তন",

        "feature_multilingual": "বহুভাষী",

        "feature_multilingual_desc": "গ্ৰহণ আৰু লেনদেনৰ উত্তৰণৰ ক্ষেত্ৰত সৰ্বোত্তম বহুভাষিক ক্ষমতা।",

        "feature_personalized": "ব্যক্তিগতকৃত",

        "feature_personalized_desc": "আপোনাৰ পৰিচয় আৰু প্ৰফাইল সুবিধা সুৰক্ষিত কৰক",

        "featured_title": "বিশেষ আঁচনিসমূহ",

        "scheme_agriculture": "কৃষি আৰু গ্ৰাম্য",

        "scheme_agriculture_count": "৮১৮ আঁচনি",

        "scheme_banking": "বেংকিং আৰু বিত্ত",

        "scheme_banking_count": "৩১৭ আঁচনি",

        "scheme_business": "ব্যৱসায়",

        "scheme_business_count": "৭০৫ আঁচনি",

        "scheme_education": "শিক্ষা",

        "scheme_education_count": "১০৭৬ আঁচনি",

        "scheme_health": "স্বাস্থ্য",

        "scheme_health_count": "২৭৪ আঁচনিসমূহ",

        "scheme_housing": "বাসগৃহ",

        "scheme_housing_count": "১২৮ আঁচনি",

        "scheme_public_safety": "ৰাজহুৱা সুৰক্ষা",

        "scheme_public_safety_count": "২৯ আঁচনিসমূহ",

        "scheme_science": "বিজ্ঞান আৰু তথ্য-প্ৰযুক্তি",

        "scheme_science_count": "১০০ আঁচনি",

        "scheme_skills": "দক্ষতা",

        "scheme_skills_count": "৩৬৮ আঁচনি",

        "scheme_social_welfare": "সামাজিক কল্যাণ",

        "scheme_social_welfare_count": "১৪৫৬ আঁচনিসমূহ",

        "scheme_sports": "ক্ৰীড়া",

        "scheme_sports_count": "২৪৮ আঁচনি",

        "scheme_transport": "পৰিবহণ",

        "scheme_transport_count": "৮৬ আঁচনিসমূহ",

        "scheme_travel": "যাত্ৰা",

        "scheme_travel_count": "৯১ আঁচনিসমূহ",

        "scheme_utility": "উপযোগীতা",

        "scheme_utility_count": "৫৮ আঁচনি",

        "scheme_women": "মহিলা আৰু শিশু",

        "scheme_women_count": "৪৫৮ আঁচনি",

        "how_title": "ই কেনেদৰে কাম কৰে",

        "step1_title": "আপোনাৰ তথ্য প্ৰদান কৰক",

        "step2_title": "ব্যক্তিগতকৃত স্কিম লাভ কৰক",

        "step3_title": "আঁচনিৰ উপকাৰিতা",

        "hero-signup": "পঞ্জীয়ন কৰক",

        "hero-continue": "অতিথি হৈ থাকক",

        "stat_ai": "AI",

        "stat_ai_label": "চালিত",

        "stat_languages_new": "১২+",

        "stat_languages_interactive": "ভাষাসমূহ, ইণ্টাৰেক্টিভ",


        // New button translations for as_IN
        "nav_signin": "লগ ইন কৰক",

        "start_chatting": "চ্যাট আৰম্ভ কৰক",

        "greeting_hello": "হ্যালো।",

    },

    "ur_IN": {
        "app_title": "سرکاری اسکیم اسسٹنٹ",

        "logo-text": "سرکاری اسکیم اسسٹنٹ",

        "signin": "سائن ان →",

        "logout": "لاگ آؤٹ",

        "edit_profile": "پروفائل میں ترمیم کریں",

        "status-online": "آن لائن",

        "hero-badge": "محفوظ، آسان، بے رکاوٹ",

        "hero-accent": "فاسٹ ٹریک",

        "hero-title": "سرکاری فوائد\<br>حاصل کریں",

        "cta-btn": "اسکیمیں دیکھیں",

        "skip-btn": "مہمان کے طور پر جاری رکھیں →",

        "tab_new": "نیا صارف",

        "tab_signin": "سائن ان",

        "quick_lang": "آپ کی زبان",

        "quick_state": "اپنی ریاست",

        "quick_all_india": "پورا ہندوستان",

        "quick_explore": "اسکیمیں تلاش کریں",

        "stat_schemes": "٥٠٠+",

        "stat_schemes_label": "دستیاب اسکیمیں",

        "stat_serving": "AI-بیسڈ",

        "stat_serving_label": "مدد",

        "stat_languages": "١٥+",

        "stat_languages_label": "معاون زبانیں",

        "chat_welcome_title": "سرکاری اسکیم اسسٹنٹ میں خوش آمدید",

        "chat_welcome_desc": "میں آپ کی پسندیدہ زبان میں ہندوستانی سرکاری اسکیموں، اہلیت، فوائد اور درخواست کے عمل کو سمجھنے میں آپ کی مدد کر سکتا ہوں۔",

        "chat_limit_msg": "٣ مفت پیغامات باقی ہیں",

        "chat_input_placeholder": "اپنا پیغام ٹائپ کریں...",

        "signin-title": "خوش آمدید",

        "signin-subtitle": "چیٹ جاری رکھنے کے لیے سائن ان کریں",

        "signin-email": "ای میل ایڈریس",

        "signin-btn": "سائن ان →",

        "signin-loading": "سائن ان ہو رہا ہے...",

        "auth_lbl_password": "پاس ورڈ",

        "auth_pl_password": "اپنا پاس ورڈ درج کریں",

        "auth_msg_no_account": "اکاؤنٹ نہیں ہے؟",

        "auth_link_signup": "سائن اپ کریں",

        "auth-prompt-message": "جاری رکھنے کے لیے سائن ان کریں یا اکاؤنٹ بنائیں",

        "forgot-password": "پاس ورڈ بھول گئے؟",

        "sf_modal_title": "اپنے لیے بہترین اسکیمیں تلاش کرنے میں ہماری مدد کریں",

        "sf_h_account": "اپنا اکاؤنٹ بنائیں",

        "sf_msg_have_account": "پہلے سے اکاؤنٹ ہے؟",

        "sf_link_signin": "سائن ان کریں",

        "sf_lbl_name": "پورا نام",

        "sf_pl_name": "اپنا نام درج کریں",

        "sf_lbl_email": "ای میل ایڈریس",

        "sf_pl_email": "you@example.com",

        "sf_lbl_pass": "پاس ورڈ",

        "sf_pl_pass": "کم از کم 6 حروف",

        "sf_h_about": "آپ کے بارے میں",

        "sf_lbl_gender": "صنف",

        "sf_opt_male": "مرد",

        "sf_opt_female": "عورت",

        "sf_opt_trans": "ٹرانس جینڈر",

        "sf_lbl_age": "عمر",

        "sf_opt_sel_age": "عمر منتخب کریں",

        "sf_h_loc": "مقام",

        "sf_lbl_state": "ریاست",

        "sf_opt_sel_state": "ریاست منتخب کریں",

        "sf_lbl_area": "علاقے کی قسم",

        "sf_opt_urban": "شہری",

        "sf_opt_rural": "دیہی",

        "sf_h_social": "سماجی تفصیلات",

        "sf_lbl_cat": "زمرہ",

        "sf_cat_gen": "جنرل",

        "sf_cat_obc": "او بی سی",

        "sf_cat_pvtg": "پی وی ٹی جی",

        "sf_cat_sc": "ایس سی",

        "sf_cat_st": "ایس ٹی",

        "sf_cat_dnt": "ڈی این ٹی",

        "sf_lbl_pwd": "کیا آپ معذور ہیں؟",

        "sf_opt_yes": "ہاں",

        "sf_opt_no": "نہیں",

        "sf_lbl_minor": "کیا آپ اقلیت ہیں؟",

        "sf_h_emp": "روزگار اور تعلیم",

        "sf_lbl_student": "کیا آپ طالب علم ہیں؟",

        "sf_lbl_status": "روزگار کی حیثیت",

        "sf_emp_emp": "ملازم",

        "sf_emp_unemp": "بے روزگار",

        "sf_emp_self": "خود ملازم",

        "sf_lbl_govt": "کیا آپ سرکاری ملازم ہیں؟",

        "sf_h_income": "آمدنی کی تفصیلات",

        "sf_lbl_inc_ann": "سالانہ آمدنی (₹)",

        "sf_lbl_inc_fam": "خاندانی آمدنی (₹)",

        "sf_pl_zero": "0",

        "sf_submit_btn": "پروفائل جمع کریں اور چیٹ شروع کریں",

        "sf_loading": "آپ کا پروفائل ترتیب دیا جا رہا ہے...",

        "user-name-display": "",
        "features_title": "اہم خصوصیات",

        "feature_secure_profile": "محفوظ پروفائل",

        "feature_secure_desc": "اپنے صارف کی پروفائل کی شناخت کو محفوظ کریں، اور پروفائل فوائد کو محفوظ کریں.",

        "feature_direct_benefit": "براہ راست فوائد کی منتقلی",

        "feature_direct_desc": "براہ راست فوائد کی منتقلی",

        "feature_multilingual": "کثیر لسانی",

        "feature_multilingual_desc": "اپنانے اور لین دین کے جواب میں بہترین کے لئے کثیر لسانی صلاحیتیں.",

        "feature_personalized": "ذاتی نوعیت",

        "feature_personalized_desc": "اپنی شناخت اور پروفائل کے فوائد کو یقینی بنائیں",

        "featured_title": "خاص اسکیمیں",

        "scheme_agriculture": "زراعت اور دیہی علاقہ",

        "scheme_agriculture_count": "٨١٨ اسکیمیں",

        "scheme_banking": "بینکنگ & فنانس",

        "scheme_banking_count": "٣١٧ اسکیمیں",

        "scheme_business": "کاروبار",

        "scheme_business_count": "٧٠٥ اسکیمیں",

        "scheme_education": "تعلیم",

        "scheme_education_count": "١٠٧٦ اسکیمیں",

        "scheme_health": "صحت",

        "scheme_health_count": "٢٧٤ اسکیمیں",

        "scheme_housing": "رہائش",

        "scheme_housing_count": "١٢٨ اسکیمیں",

        "scheme_public_safety": "پبلک سیفٹی",

        "scheme_public_safety_count": "٢٩ اسکیمیں",

        "scheme_science": "سائنس اور آئی ٹی",

        "scheme_science_count": "١٠٠ اسکیمیں",

        "scheme_skills": "مہارت",

        "scheme_skills_count": "٣٦٨ اسکیمیں",

        "scheme_social_welfare": "سماجی بہبود",

        "scheme_social_welfare_count": "١٤٥٦ اسکیمیں",

        "scheme_sports": "کھیل",

        "scheme_sports_count": "٢٤٨ اسکیمیں",

        "scheme_transport": "نقل و حمل",

        "scheme_transport_count": "٨٦ اسکیمیں",

        "scheme_travel": "سفر",

        "scheme_travel_count": "٩١ اسکیمیں",

        "scheme_utility": "افادیت",

        "scheme_utility_count": "٥٨ اسکیمیں",

        "scheme_women": "خواتین اور بچے",

        "scheme_women_count": "٤٥٨ اسکیمیں",

        "how_title": "یہ کیسے کام کرتا ہے",

        "step1_title": "اپنی معلومات دیں",

        "step2_title": "اپنی مرضی کے مطابق اسکیمیں حاصل کریں",

        "step3_title": "اسکیم کے فوائد",

        "hero-signup": "سائن اپ کریں",

        "hero-continue": "مہمانوں کی حیثیت سے جاری رکھیں",

        "stat_ai": "اے آئی",

        "stat_ai_label": "طاقت",

        "stat_languages_new": "١٢+",

        "stat_languages_interactive": "زبانیں، انٹرایکٹو",


        // New button translations for ur_IN
        "nav_signin": "سائن ان کریں",

        "start_chatting": "چیٹنگ شروع کریں",

        "greeting_hello": "ہیلو",

    },

    "ks_IN": {
        "app_title": "سرکٲری سکیٖم مدگار",

        "logo-text": "سرکٲری سکیٖم مدگار",

        "signin": "سائن اِن",

        "logout": "لاگ آؤٹ",

        "edit_profile": "پروفائلِ تبدیٖل",

        "status-online": "آنلائن",

        "hero-badge": "محفوظ، آسان، بے رکاوٹ",

        "hero-accent": "فاسٹ ٹریک",

        "hero-title": "سرکٲری فٲیدہ\<br>ہٲصل کٔریو",

        "cta-btn": "سکیٖمہٕ وُچھیو",

        "skip-btn": "مہمان سٕنٛد پٲٹھۍ جٲری تھٲویو →",

        "tab_new": "نۆو صٲرف",

        "tab_signin": "سائن اِن",

        "quick_lang": "تُہنٛز زبان",

        "quick_state": "تُہونٛد رِیاست",

        "quick_all_india": "پورہ ہِندوستان",

        "quick_explore": "سکیٖمہٕ ژھانڈِیو",

        "stat_schemes": "٥٠٠+",

        "stat_schemes_label": "دستیاب سکیٖمہٕ",

        "stat_serving": "AI-مَدَتہٕ سٟتۍ",

        "stat_serving_label": "مَدَت",

        "stat_languages": "١٥+",

        "stat_languages_label": "سپورٹڈ زبانہٕ",

        "chat_welcome_title": "سرکٲری سکیٖم مدگارس منٛز خوش آمدید",

        "chat_welcome_desc": "بہٕ ہیکا توہیہِ تُہنٛزِ پسندیدہ زبانِ منٛز ہندوستٲنۍ سرکٲری سکیٖمہٕ، اہلیت، فٲیدہ تہٕ درخواستُک طریقِ کار سمجناونس منٛز مَدَت کرِتھ۔",

        "chat_limit_msg": "٣ مُفت پیغامات بٲقی",

        "chat_input_placeholder": "پانہٕ پیغام ٹائپ کٔریو...",

        "signin-title": "وَآپس خیرمقدم",

        "signin-subtitle": "چیٹ جٲری تھاونہٕ خٲطرٕ سائن اِن کٔریو",

        "signin-email": "ای میل ایڈریس",

        "signin-btn": "سائن اِن →",

        "signin-loading": "سائن اِن گژھان...",

        "auth_lbl_password": "پاس ورڈ",

        "auth_pl_password": "پانہٕ پاس ورڈ درج کٔریو",

        "auth_msg_no_account": "اکاؤنٹ چھُ نہٕ؟",

        "auth_link_signup": "سائن اَپ کٔریو",

        "auth-prompt-message": "جٲری تھاونہٕ خٲطرٕ سائن اِن کٔریو یا اکاؤنٹ بنایو",

        "forgot-password": "پاس ورڈ مشیتھ؟",

        "sf_modal_title": "تُہنٛد خٲطرٕ بہتٔریٖن سکیٖمہٕ ژھانڈنس منٛز سٲنی مَدَت کٔریو",

        "sf_h_account": "پانہٕ اکاؤنٹ بنایو",

        "sf_msg_have_account": "پہلٚے چھُ اکاؤنٹ؟",

        "sf_link_signin": "سائن اِن کٔریو",

        "sf_lbl_name": "پُورہ ناو",

        "sf_pl_name": "پانہٕ ناو درج کٔریو",

        "sf_lbl_email": "ای میل ایڈریس",

        "sf_pl_email": "you@example.com",

        "sf_lbl_pass": "پاس ورڈ",

        "sf_pl_pass": "کم از کم 6 حروف",

        "sf_h_about": "تُہنٛد مُتعلق",

        "sf_lbl_gender": "جِنس",

        "sf_opt_male": "مرد",

        "sf_opt_female": "زنانہٕ",

        "sf_opt_trans": "ٹرانس جینڈر",

        "sf_lbl_age": "عُمر",

        "sf_opt_sel_age": "عُمر ژاریو",

        "sf_h_loc": "مقام",

        "sf_lbl_state": "رِیاست",

        "sf_opt_sel_state": "رِیاست ژاریو",

        "sf_lbl_area": "علاقہٕ قٕسم",

        "sf_opt_urban": "شہری",

        "sf_opt_rural": "گامُک",

        "sf_h_social": "سمٲجی تफ़صیلات",

        "sf_lbl_cat": "زاتھ",

        "sf_cat_gen": "عام",

        "sf_cat_obc": "او بی سی",

        "sf_cat_pvtg": "پی وی ٹی جی",

        "sf_cat_sc": "ایس سی",

        "sf_cat_st": "ایس ٹی",

        "sf_cat_dnt": "ڈی این ٹی",

        "sf_lbl_pwd": "کیا تُہۍ چھِوا معذور؟",

        "sf_opt_yes": "آ",

        "sf_opt_no": "نہٕ",

        "sf_lbl_minor": "کیا تُہۍ چھِوا اقلیت؟",

        "sf_h_emp": "روزگار تہٕ تٲلیٖم",

        "sf_lbl_student": "کیا تُہۍ چھِوا طالِب عِلم؟",

        "sf_lbl_status": "روزگارُک حالت",

        "sf_emp_emp": "مُلازم",

        "sf_emp_unemp": "بے روزگار",

        "sf_emp_self": "پانہٕ روزگار",

        "sf_lbl_govt": "کیا تُہۍ چھِوا سرکٲری مُلازم؟",

        "sf_h_income": "آمدنی ہِنٛز تफ़صیل",

        "sf_lbl_inc_ann": "سلانہٕ آمدنی (₹)",

        "sf_lbl_inc_fam": "خاندانٕچ آمدنی (₹)",

        "sf_pl_zero": "0",

        "sf_submit_btn": "پروفائل جمع کٔریو تہٕ چیٹ شروع کٔریو",

        "sf_loading": "تُہنٛد پروفائل سیٹ گژھان...",

        "user-name-display": "",
        "features_title": "اہم خصوصیات",

        "feature_secure_profile": "محفوظ پروفائل",

        "feature_secure_desc": "پننہٕ صارفک پروفائل شناخت محفوظ کرُن، تہٕ پروفائل فوائد محفوظ کرُن۔",

        "feature_direct_benefit": "براہ راست فوائد ہنز منتقلی",

        "feature_direct_desc": "براہ راست فوائد منتقلی inconzune معلومات فوائد.",

        "feature_multilingual": "کثیر لسانی",

        "feature_multilingual_desc": "اپوزیشن تہٕ ٹرانزیکشن جوابن منٛز بہترین خٲطرٕہ کثیر لسانی صلاحیتہٕ۔",

        "feature_personalized": "شخصی طور پٲنٹھ",

        "feature_personalized_desc": "پننہٕ شناخت تہٕ پروفائل فوائد محفوظ کرُن",

        "featured_title": "خاص اسکیمہٕ",

        "scheme_agriculture": "زراعت تہٕ دیہی علاقہٕ",

        "scheme_agriculture_count": "٨١٨ اسکیمیں",

        "scheme_banking": "بینکنگ تہٕ فنانس",

        "scheme_banking_count": "٣١٧ اسکیمیں",

        "scheme_business": "کاروبار",

        "scheme_business_count": "٧٠٥ اسکیمیں",

        "scheme_education": "تعلیم",

        "scheme_education_count": "١٠٧٦ اسکیمٕ",

        "scheme_health": "صحت",

        "scheme_health_count": "٢٧٤ اسکیمیں",

        "scheme_housing": "ہاؤسنگ",

        "scheme_housing_count": "١٢٨ اسکیمیں",

        "scheme_public_safety": "پبلک سیفٹی",

        "scheme_public_safety_count": "٢٩ اسکیمٕ",

        "scheme_science": "سائنس تہٕ آئی ٹی",

        "scheme_science_count": "١٠٠ اسکیمٕ",

        "scheme_skills": "صلاحیتہٕ",

        "scheme_skills_count": "٣٦٨ اسکیمٕ",

        "scheme_social_welfare": "سمأجی فلاح",

        "scheme_social_welfare_count": "١٤٥٦ اسکیمیں",

        "scheme_sports": "سپورٹس",

        "scheme_sports_count": "٢٤٨ اسکیمٕ",

        "scheme_transport": "نقل و حمل",

        "scheme_transport_count": "٨٦ اسکیمیں",

        "scheme_travel": "سفرہٕ",

        "scheme_travel_count": "٩١ اسکیمٕ",

        "scheme_utility": "افادیت",

        "scheme_utility_count": "٥٨ اسکیمٕ",

        "scheme_women": "زنانہٕ تہٕ بچہٕ",

        "scheme_women_count": "٤٥٨ اسکیمیں",

        "how_title": "یہٕ چُھ کِتھ پأنٹھ کٲم کران",

        "step1_title": "پننہٕ معلوماتہٕ دِنہٕ",

        "step2_title": "شخصی سکیمہٕ حٲصل کرُن",

        "step3_title": "اسکیمہٕ کہِ فوائد",

        "hero-signup": "سائن اپ کٔرِتھ",

        "hero-continue": "مہمانن ہٕنٛدس طورس پیٚٹھ جٲری",

        "stat_ai": "AI",

        "stat_ai_label": "پاورٕ آمت",

        "stat_languages_new": "١٢+",

        "stat_languages_interactive": "زبٲنۍ، انٹرایکٹو",


        // New button translations for ks_IN
        "nav_signin": "سائن ان کرُن",

        "start_chatting": "چیٹ شروع کٔرِتھ",

        "greeting_hello": "ہائے، ہیلو",

    },

    "mai_IN": {
        "app_title": "सरकारी योजना सहायक",
        "logo-text": "सरकारी योजना सहायक",
        "signin": "साइन इन →",
        "logout": "लॉग आउट",
        "edit_profile": "प्रोफाइल संपादित करू",
        "status-online": "ऑनलाइन",
        "hero-badge": "सुरक्षित, सरल, निर्बाध",
        "hero-accent": "फास्ट-ट्रैक",
        "hero-title": "सरकारी लाभ\\nप्राप्त करू",
        "cta-btn": "योजना देखू",
        "skip-btn": "अतिथि के रूप में जारी रखू →",
        "tab_new": "नवा उपयोगकर्ता",
        "tab_signin": "साइन इन",
        "quick_lang": "अहांक भाषा",
        "quick_state": "अहांक राज्य",
        "quick_all_india": "संपूर्ण भारत",
        "quick_explore": "योजना खोजू",
        "stat_schemes": "500+",
        "stat_schemes_label": "उपलब्ध योजना",
        "stat_serving": "AI-संचालित",
        "stat_serving_label": "सहायता",
        "stat_languages": "15+",
        "stat_languages_label": "समर्थित भाषा",
        "chat_welcome_title": "सरकारी योजना सहायक में अहांक स्वागत अछि",
        "chat_welcome_desc": "हम अहांक पसंदीदा भाषा में भारतीय सरकारी योजना, पात्रता, लाभ और आवेदन प्रक्रिया को बुझय में मदद क सकय छी।",
        "chat_limit_msg": "3टा मुफ्त संदेश शेष",
        "chat_input_placeholder": "अपन संदेश टाइप करू...",
        "signin-title": "फेर स स्वागत अछि",
        "signin-subtitle": "चैट जारी रखबाक लेल साइन इन करू",
        "signin-email": "ईमेल पता",
        "signin-btn": "साइन इन →",
        "signin-loading": "साइन इन भ रहल अछि...",
        "auth_lbl_password": "पासवर्ड",
        "auth_pl_password": "अपन पासवर्ड दर्ज करू",
        "auth_msg_no_account": "खाता नहि अछि?",
        "auth_link_signup": "साइन अप करू",
        "auth-prompt-message": "जारी रखबाक लेल साइन इन वा खाता बनाउ",
        "forgot-password": "पासवर्ड बिसरि गेलहुं?",
        "sf_modal_title": "अहांक लेल सर्वोत्तम योजना खोजय में हमर मदद करू",
        "sf_h_account": "अपन खाता बनाउ",
        "sf_msg_have_account": "पहिने स खाता अछि?",
        "sf_link_signin": "साइन इन करू",
        "sf_lbl_name": "पूरा नाम",
        "sf_pl_name": "अपन नाम दर्ज करू",
        "sf_lbl_email": "ईमेल पता",
        "sf_pl_email": "you@example.com",
        "sf_lbl_pass": "पासवर्ड",
        "sf_pl_pass": "कम स कम 6 अक्षर",
        "sf_h_about": "अहांक विषय में",
        "sf_lbl_gender": "लिंग",
        "sf_opt_male": "पुरुष",
        "sf_opt_female": "महिला",
        "sf_opt_trans": "ट्रांसजेंडर",
        "sf_lbl_age": "आयु",
        "sf_opt_sel_age": "उम्र चुनु",
        "sf_h_loc": "स्थान",
        "sf_lbl_state": "राज्य",
        "sf_opt_sel_state": "राज्य चुनु",
        "sf_lbl_area": "क्षेत्र प्रकार",
        "sf_opt_urban": "शहरी",
        "sf_opt_rural": "ग्रामीण",
        "sf_h_social": "सामाजिक विवरण",
        "sf_lbl_cat": "श्रेणी",
        "sf_cat_gen": "सामान्य",
        "sf_cat_obc": "ओबीसी",
        "sf_cat_pvtg": "पीवीटीजी",
        "sf_cat_sc": "एससी",
        "sf_cat_st": "एसटी",
        "sf_cat_dnt": "डीएनटी",
        "sf_lbl_pwd": "विकलांग?",
        "sf_opt_yes": "हँ",
        "sf_opt_no": "नहि",
        "sf_lbl_minor": "अल्पसंख्यक?",
        "sf_h_emp": "रोजगार आ शिक्षा",
        "sf_lbl_student": "छात्र?",
        "sf_lbl_status": "रोजगार स्थिति",
        "sf_emp_emp": "नौकरीपेशा",
        "sf_emp_unemp": "बेरोजगार",
        "sf_emp_self": "स्वरोजगार",
        "sf_lbl_govt": "सरकारी कर्मचारी?",
        "sf_h_income": "आय विवरण",
        "sf_lbl_inc_ann": "वार्षिक आय (₹)",
        "sf_lbl_inc_fam": "पारिवारिक आय (₹)",
        "sf_pl_zero": "0",
        "sf_submit_btn": "प्रोफाइल सबमिट करू आ चैट शुरू करू",
        "sf_loading": "अहांक प्रोफाइल सेट भ रहल अछि...",
        "user-name-display": "",
        "features_title": "प्रमुख विशेषतासभ",
        "feature_secure_profile": "सुरक्षित प्रोफाइल",
        "feature_secure_desc": "अपन प्रयोक्ताक प्रोफाइल पहिचान केँ सुरक्षित राखू, आ प्रोफाइल लाभकेँ सुरक्षित राखू।",
        "feature_direct_benefit": "प्रत्यक्ष लाभ हस्तांतरण",
        "feature_direct_desc": "प्रत्यक्ष लाभ हस्तांतरण inconzune जानकारी लाभ।",
        "feature_multilingual": "बहुभाषी",
        "feature_multilingual_desc": "स्वीकृति आ लेनदेनक उत्तर देबाक लेल बहुभाषी क्षमता सभसँ नीक।",
        "feature_personalized": "वैयक्तिकृत",
        "feature_personalized_desc": "अपन पहचान आ प्रोफाइलक लाभ सुनिश्चित करू",
        "featured_title": "विशेष योजनासभ",
        "scheme_agriculture": "कृषि आ ग्रामीण क्षेत्र",
        "scheme_agriculture_count": "818 योजनासभ",
        "scheme_banking": "बैंकिङ & फाइनान्स",
        "scheme_banking_count": "317 योजनासभ",
        "scheme_business": "व्यवसाय",
        "scheme_business_count": "705 योजनासभ",
        "scheme_education": "शिक्षा",
        "scheme_education_count": "1076 योजनासभ",
        "scheme_health": "स्वास्थ्य",
        "scheme_health_count": "274 योजनासभ",
        "scheme_housing": "आवास",
        "scheme_housing_count": "128 योजनासभ",
        "scheme_public_safety": "सार्वजनिक सुरक्षा",
        "scheme_public_safety_count": "29 योजनासभ",
        "scheme_science": "विज्ञान आ सूचना प्रौद्योगिकी",
        "scheme_science_count": "१०० योजनासभ",
        "scheme_skills": "कौशल",
        "scheme_skills_count": "368 योजनासभ",
        "scheme_social_welfare": "सामाजिक कल्याण",
        "scheme_social_welfare_count": "1456 योजनासभ",
        "scheme_sports": "खेलकूद",
        "scheme_sports_count": "248 योजनासभ",
        "scheme_transport": "परिवहन",
        "scheme_transport_count": "86 योजनासभ",
        "scheme_travel": "यात्रा",
        "scheme_travel_count": "91 योजनासभ",
        "scheme_utility": "उपयोगिता",
        "scheme_utility_count": "58 योजनासभ",
        "scheme_women": "महिला आ बच्चा",
        "scheme_women_count": "458 योजनासभ",
        "how_title": "ई काज कोना करैत अछि",
        "step1_title": "अपन जानकारी दिअ",
        "step2_title": "व्यक्तिगत योजना प्राप्त करू",
        "step3_title": "योजनाक लाभ",
        "hero-signup": "साइन अप करू",
        "hero-continue": "अतिथि बनल रहू",
        "stat_ai": "एआई",
        "stat_ai_label": "संचालित",
        "stat_languages_new": "12+",
        "stat_languages_interactive": "भाषा, अन्तरक्रियात्मक",

    }
};

// Export for use in script.js
if (typeof window !== 'undefined') {
    window.TRANSLATIONS = TRANSLATIONS;
}
