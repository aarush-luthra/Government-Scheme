// ============ State Management ============
let currentUser = null;
let sessionId = null;
let chatHistory = [];
let isAuthWall = false;

// Scheme Finder State
// Scheme Finder State
let schemeFormData = {
    name: '',
    email: '',
    password: '',
    gender: null,
    age: null,
    state: '',
    area: null,
    category: null,
    is_disabled: null,
    is_minority: null,
    is_student: null,
    employment_status: null,
    is_govt_employee: null,
    annual_income: null,
    family_income: null
};

// Language State
let currentLanguage = localStorage.getItem('language') || 'en_XX';



// ============ Initialization ============
document.addEventListener('DOMContentLoaded', async () => {
    await checkAuthStatus();

    initializeLanguage();
    initializeLanguageDropdowns();
    initializeCustomSelects();

    // Check for ?chat=true query param (redirect from login/signup)
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('chat') === 'true') {
        startChat();
        // Clean up URL
        window.history.replaceState({}, document.title, '/');
    }

    // Check for ?verify=true query param (show verification modal after signup)
    if (urlParams.get('verify') === 'true') {
        // Load form data from sessionStorage for comparison
        const storedData = sessionStorage.getItem('signupFormData');
        if (storedData) {
            try {
                const formData = JSON.parse(storedData);
                // Populate schemeFormData for comparison
                schemeFormData.name = formData.name || '';
                schemeFormData.age = formData.age;
                schemeFormData.gender = formData.gender;
                schemeFormData.category = formData.category;
                schemeFormData.annual_income = formData.annual_income;
            } catch (e) {
                console.error('Failed to parse signup form data:', e);
            }
        }
        // Open verification modal
        openVerificationModal();
        // Clean up URL
        window.history.replaceState({}, document.title, '/');
    }
});

async function checkAuthStatus() {
    try {
        const response = await fetch('/auth/me', {
            credentials: 'include'
        });
        const data = await response.json();

        sessionId = data.session_id;

        if (data.is_logged_in) {
            currentUser = {
                name: data.user_name,
                user_id: data.user_id
            };
            updateUIForLoggedInUser();
        } else {
            currentUser = null;
            updateUIForAnonymousUser();
        }
    } catch (error) {
        console.error('Auth check failed:', error);
    }
}

function updateUIForLoggedInUser() {
    if (!currentUser) return;

    const userMenu = document.getElementById('user-menu');
    const authButtons = document.getElementById('auth-buttons');
    const userNameDisplay = document.getElementById('user-name-display');
    const navbarSigninBtn = document.getElementById('navbar-signin-btn');
    const navbarUserMenu = document.getElementById('navbar-user-menu');
    const navbarUserName = document.getElementById('navbar-user-name');
    const heroGuestButtons = document.getElementById('hero-guest-buttons');
    const heroLoggedinButtons = document.getElementById('hero-loggedin-buttons');

    // Chat Header
    if (userMenu) userMenu.classList.remove('hidden');
    if (authButtons) authButtons.classList.add('hidden');
    if (userNameDisplay) {
        const greeting = (window.TRANSLATIONS && window.TRANSLATIONS[currentLanguage] && window.TRANSLATIONS[currentLanguage]['greeting_hello']) || 'Hello';
        userNameDisplay.textContent = `${greeting}, ${currentUser.name}`;
    }

    // Navbar
    if (navbarSigninBtn) navbarSigninBtn.style.display = 'none';
    if (navbarUserMenu) navbarUserMenu.classList.remove('hidden');
    if (navbarUserName) {
        const greeting = (window.TRANSLATIONS && window.TRANSLATIONS[currentLanguage] && window.TRANSLATIONS[currentLanguage]['greeting_hello']) || 'Hello';
        navbarUserName.textContent = `${greeting}, ${currentUser.name}`;
    }

    // Hero
    if (heroGuestButtons) heroGuestButtons.classList.add('hidden');
    if (heroLoggedinButtons) heroLoggedinButtons.classList.remove('hidden');

    const responseLimitBanner = document.getElementById('response-limit-banner');
    if (responseLimitBanner) {
        responseLimitBanner.classList.add('hidden');
    }
}

function updateUIForAnonymousUser() {
    const userMenu = document.getElementById('user-menu');
    const authButtons = document.getElementById('auth-buttons');
    const navbarSigninBtn = document.getElementById('navbar-signin-btn');
    const navbarUserMenu = document.getElementById('navbar-user-menu');
    const navbarUserName = document.getElementById('navbar-user-name');
    const heroGuestButtons = document.getElementById('hero-guest-buttons');
    const heroLoggedinButtons = document.getElementById('hero-loggedin-buttons');

    // Chat Header
    if (userMenu) userMenu.classList.add('hidden');
    if (authButtons) authButtons.classList.remove('hidden');

    // Navbar
    if (navbarSigninBtn) navbarSigninBtn.style.display = '';
    if (navbarUserMenu) navbarUserMenu.classList.add('hidden');
    if (navbarUserName) navbarUserName.textContent = '';

    // Hero
    if (heroGuestButtons) heroGuestButtons.classList.remove('hidden');
    if (heroLoggedinButtons) heroLoggedinButtons.classList.add('hidden');
}



// ============ Language Management ============
// Store original values for translation
let i18nOriginals = {};

function initializeLanguage() {
    // 1. Store original Text Content (Labels, Headers, Options)
    document.querySelectorAll('[data-i18n]').forEach(el => {
        i18nOriginals[el.dataset.i18n] = el.innerText.trim();
    });

    // 2. Store original Placeholders (Inputs) - NEW ADDITION
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        // We add '_pl' suffix to the key to avoid collisions with text keys
        i18nOriginals[el.dataset.i18nPlaceholder + '_pl'] = el.getAttribute('placeholder');
    });

    // Translate if needed (if user saved a preference previously)
    if (currentLanguage !== 'en_XX') {
        translatePage(currentLanguage);
    }

    updateLanguageDisplay(currentLanguage);
    updateAgeDropdown(currentLanguage);
}

function initializeLanguageDropdowns() {
    // Main dropdown items
    const mainItems = document.querySelectorAll('#language-menu .dropdown-item');
    mainItems.forEach(item => {
        item.addEventListener('click', () => selectLanguage(item.dataset.lang, 'main'));
    });

    // Chat dropdown items
    const chatItems = document.querySelectorAll('#chat-language-menu .dropdown-item');
    chatItems.forEach(item => {
        item.addEventListener('click', () => selectLanguage(item.dataset.lang, 'chat'));
    });
}

function toggleLanguageDropdown() {
    const dropdown = document.getElementById('language-dropdown');
    dropdown.classList.toggle('open');

    // Close on outside click
    const closeHandler = (e) => {
        if (!dropdown.contains(e.target)) {
            dropdown.classList.remove('open');
            document.removeEventListener('click', closeHandler);
        }
    };

    setTimeout(() => document.addEventListener('click', closeHandler), 0);
}

function toggleChatLanguageDropdown() {
    const dropdown = document.getElementById('chat-language-dropdown');
    dropdown.classList.toggle('open');

    const closeHandler = (e) => {
        if (!dropdown.contains(e.target)) {
            dropdown.classList.remove('open');
            document.removeEventListener('click', closeHandler);
        }
    };

    setTimeout(() => document.addEventListener('click', closeHandler), 0);
}

async function selectLanguage(langCode, source) {
    const langNames = {
        'hi_IN': 'हिन्दी', 'ta_IN': 'தமிழ்', 'te_IN': 'తెలుగు',
        'bn_IN': 'বাংলা', 'mr_IN': 'मराठी', 'gu_IN': 'ગુજરાતી',
        'kn_IN': 'ಕನ್ನಡ', 'ml_IN': 'മലയാളം', 'pa_IN': 'ਪੰਜਾਬੀ',
        'or_IN': 'ଓଡ଼ିଆ', 'as_IN': 'অসমীয়া', 'ur_IN': 'اردو',
        'ks_IN': 'कॉशुर', 'mai_IN': 'मैथिली'
    };

    // 1. Update State & UI Immediately
    currentLanguage = langCode;
    localStorage.setItem('language', langCode);
    updateLanguageDisplay(langCode);

    if (currentUser) {
        updateUIForLoggedInUser();
    }

    // Close dropdowns
    document.getElementById('language-dropdown')?.classList.remove('open');
    document.getElementById('chat-language-dropdown')?.classList.remove('open');

    // 2. Loading Indicator Logic (Only for Chat Page)
    const isOnChatPage = !document.getElementById('chat-page')?.classList.contains('hidden');
    const overlay = document.getElementById('language-loading-overlay');

    if (isOnChatPage && langCode !== 'en_XX' && overlay) {
        const title = document.getElementById('language-loading-title');
        const status = document.getElementById('language-loading-status');
        const langName = langNames[langCode] || langCode;

        title.textContent = `Switching to ${langName}...`;
        status.textContent = 'Translating conversation...';
        overlay.classList.remove('hidden');

        try {
            await translatePage(langCode);
        } finally {
            // Small delay for smooth UX
            setTimeout(() => overlay.classList.add('hidden'), 500);
        }
    } else {
        // Landing page or English -> Instant
        await translatePage(langCode);
    }
}

async function translatePage(targetLang) {
    // Restore English (original) text
    if (targetLang === 'en_XX') {
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.dataset.i18n;
            if (i18nOriginals[key]) {
                el.innerText = i18nOriginals[key];
            }
        });
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.dataset.i18nPlaceholder + '_pl';
            if (i18nOriginals[key]) {
                el.setAttribute('placeholder', i18nOriginals[key]);
            }
        });
        // Update card language display
        const cardLang = document.getElementById('card-current-lang-display');
        if (cardLang) cardLang.textContent = 'English';
        updateAgeDropdown(targetLang);
        return;
    }

    // Check if pre-translated strings exist for this language
    const preTranslations = window.TRANSLATIONS && window.TRANSLATIONS[targetLang];

    const textElements = Array.from(document.querySelectorAll('[data-i18n]'));
    const placeholderElements = Array.from(document.querySelectorAll('[data-i18n-placeholder]'));

    // Track what needs API translation
    const needsApiTranslation = [];
    const elementsForApi = [];

    // --- CACHING LOGIC START ---
    // Load cache from localStorage
    const cacheKey = `trans_cache_${targetLang}`;
    let localCache = {};
    try {
        const cached = localStorage.getItem(cacheKey);
        if (cached) localCache = JSON.parse(cached);
    } catch (e) {
        console.warn('Failed to load translation cache', e);
    }
    // --- CACHING LOGIC END ---

    // First pass: Apply pre-translated strings OR Cache
    const processElement = (el, type) => {
        let key, originalText;
        if (type === 'text') {
            key = el.dataset.i18n;
            originalText = i18nOriginals[key] || el.innerText.trim();
        } else {
            key = el.dataset.i18nPlaceholder; // Base key
            // Original logic used '_pl' suffix in originals
            originalText = i18nOriginals[key + '_pl'] || el.getAttribute('placeholder');
        }

        // 1. Check Pre-translations (Static)
        if (preTranslations) {
            if (type === 'text' && preTranslations[key] !== undefined) {
                el.innerHTML = preTranslations[key];
                return;
            } else if (type === 'placeholder') {
                if (preTranslations[key + '_pl'] !== undefined) {
                    el.setAttribute('placeholder', preTranslations[key + '_pl']);
                    return;
                } else if (preTranslations[key] !== undefined) {
                    el.setAttribute('placeholder', preTranslations[key]);
                    return;
                }
            }
        }

        // 2. Check Local Cache (Dynamic)
        if (localCache[originalText]) {
            if (type === 'text') {
                el.innerText = localCache[originalText];
            } else {
                el.setAttribute('placeholder', localCache[originalText]);
            }
            return;
        }

        // 3. Queue for API
        needsApiTranslation.push(originalText);
        elementsForApi.push({ el, type, originalText });
    };


    textElements.forEach(el => processElement(el, 'text'));
    placeholderElements.forEach(el => processElement(el, 'placeholder'));

    // Update card language display
    const langNames = {
        'hi_IN': 'हिन्दी', 'ta_IN': 'தமிழ்', 'te_IN': 'తెలుగు',
        'bn_IN': 'বাংলা', 'mr_IN': 'मराठी', 'gu_IN': 'ગુજરાતી',
        'kn_IN': 'ಕನ್ನಡ', 'ml_IN': 'മലയാളം', 'pa_IN': 'ਪੰਜਾਬੀ',
        'or_IN': 'ଓଡ଼ିଆ', 'as_IN': 'অসমীয়া', 'ur_IN': 'اردو'
    };
    const cardLang = document.getElementById('card-current-lang-display');
    if (cardLang) cardLang.textContent = langNames[targetLang] || 'English';


    // If there are strings that need API translation, call the API
    // SKIP API translation on chat page to avoid blocking chat responses
    const isOnChatPage = !document.getElementById('chat-page')?.classList.contains('hidden');
    if (needsApiTranslation.length > 0 && !isOnChatPage) {
        try {
            document.body.style.cursor = 'wait';

            // De-duplicate requests to save bandwidth
            const uniqueTexts = [...new Set(needsApiTranslation)];

            const response = await fetch('http://127.0.0.1:8000/translate/batch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    texts: uniqueTexts,
                    source_lang: 'en_XX',
                    target_lang: targetLang
                })
            });

            const data = await response.json();

            if (data.translations) {
                // Map results back to original text for O(1) lookup
                const translationMap = {};
                uniqueTexts.forEach((text, idx) => {
                    if (data.translations[idx]) {
                        translationMap[text] = data.translations[idx];
                        // Update Cache
                        localCache[text] = data.translations[idx];
                    }
                });

                // Apply translations to UI
                elementsForApi.forEach(item => {
                    const translatedText = translationMap[item.originalText];
                    if (translatedText) {
                        if (item.type === 'text') {
                            item.el.innerText = translatedText;
                        } else {
                            item.el.setAttribute('placeholder', translatedText);
                        }
                    }
                });

                // Save updated cache to localStorage
                try {
                    localStorage.setItem(cacheKey, JSON.stringify(localCache));
                } catch (e) {
                    console.warn('Quota exceeded for localStorage', e);
                    // Optional: Clear old caches if quota exceeded
                }
            }
        } catch (error) {
            console.error('Page translation failed:', error);
        } finally {
            document.body.style.cursor = 'default';
        }
    }

    updateAgeDropdown(targetLang);
}

function updateLanguageDisplay(langCode) {
    const langNames = {
        'en_XX': 'English',
        'hi_IN': 'हिन्दी',
        'or_IN': 'ଓଡ଼ିଆ',
        'as_IN': 'অসমীয়া',
        'bn_IN': 'বাংলা',
        'gu_IN': 'ગુજરાતી',
        'kn_IN': 'ಕನ್ನಡ',
        'ml_IN': 'മലയാളം',
        'mr_IN': 'मराठी',
        'pa_IN': 'ਪੰਜਾਬੀ',
        'ta_IN': 'தமிழ்',
        'te_IN': 'తెలుగు',
        'ur_IN': 'اردو',
        'ks_IN': 'कॉशुर',
        'mai_IN': 'मैथिली'
    };

    const displayName = langNames[langCode] || 'English';

    const mainDisplay = document.getElementById('current-lang');
    const chatDisplay = document.getElementById('chat-current-lang');

    if (mainDisplay) mainDisplay.textContent = displayName;
    if (chatDisplay) chatDisplay.textContent = displayName;

    // Update active state in dropdowns
    document.querySelectorAll('.dropdown-item').forEach(item => {
        item.classList.toggle('active', item.dataset.lang === langCode);
    });
}

// Function to populate Age dropdown with localized numbers
function updateAgeDropdown(langCode) {
    const optionsContainer = document.getElementById('age-select-options');
    const hiddenInput = document.getElementById('sf-age');
    if (!optionsContainer) return;

    // 1. Convert your API code (e.g., 'hi_IN') to Browser Locale (e.g., 'hi-IN')
    let locale = langCode.replace('_', '-');
    if (langCode === 'en_XX') locale = 'en-US'; // Fallback for your custom English code

    // 2. Save the user's currently selected age (so it doesn't reset)
    const currentSelection = hiddenInput ? hiddenInput.value : '';

    // 3. Clear existing options
    optionsContainer.innerHTML = '';

    // 4. Create the Number Formatter for the chosen language
    const numberFormatter = new Intl.NumberFormat(locale);

    // 5. Add placeholder option
    const placeholderOption = document.createElement('div');
    placeholderOption.className = 'custom-select-option';
    placeholderOption.dataset.value = '';
    placeholderOption.textContent = 'Select age';
    optionsContainer.appendChild(placeholderOption);

    // 6. Loop to create options
    for (let i = 0; i <= 100; i++) {
        const option = document.createElement('div');
        option.className = 'custom-select-option';
        option.dataset.value = i;
        option.textContent = numberFormatter.format(i);
        if (currentSelection && parseInt(currentSelection) === i) {
            option.classList.add('selected');
        }
        optionsContainer.appendChild(option);
    }

    // 7. Re-initialize click handlers
    initCustomSelectOptions('age');
}

// ============ Custom Select Dropdowns ============
function initializeCustomSelects() {
    // Initialize Age dropdown
    updateAgeDropdown(currentLanguage);

    // Setup toggle for Age dropdown
    const ageTrigger = document.getElementById('age-select-trigger');
    const ageWrapper = document.getElementById('age-select-wrapper');
    if (ageTrigger && ageWrapper) {
        ageTrigger.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            closeAllCustomSelects(ageWrapper);
            ageWrapper.classList.toggle('open');
        });
    }

    // Setup toggle for State dropdown
    const stateTrigger = document.getElementById('state-select-trigger');
    const stateWrapper = document.getElementById('state-select-wrapper');
    if (stateTrigger && stateWrapper) {
        stateTrigger.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            closeAllCustomSelects(stateWrapper);
            stateWrapper.classList.toggle('open');
        });
    }

    // Initialize option click handlers
    initCustomSelectOptions('age');
    initCustomSelectOptions('state');

    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.custom-select-wrapper')) {
            closeAllCustomSelects();
        }
    });
}

function closeAllCustomSelects(exceptWrapper = null) {
    document.querySelectorAll('.custom-select-wrapper').forEach(wrapper => {
        if (wrapper !== exceptWrapper) {
            wrapper.classList.remove('open');
        }
    });
}

function initCustomSelectOptions(type) {
    const optionsContainer = document.getElementById(`${type}-select-options`);
    const trigger = document.getElementById(`${type}-select-trigger`);
    const hiddenInput = document.getElementById(`sf-${type}`);
    const wrapper = document.getElementById(`${type}-select-wrapper`);

    if (!optionsContainer) return;

    optionsContainer.querySelectorAll('.custom-select-option').forEach(option => {
        option.addEventListener('click', (e) => {
            e.stopPropagation();
            const value = option.dataset.value;
            const text = option.textContent;

            // Update hidden input
            if (hiddenInput) {
                hiddenInput.value = value;
            }

            // Update trigger text
            if (trigger) {
                trigger.querySelector('span').textContent = value ? text : (type === 'age' ? 'Select age' : 'Select State');
            }

            // Update selected state
            optionsContainer.querySelectorAll('.custom-select-option').forEach(opt => {
                opt.classList.remove('selected');
            });
            if (value) {
                option.classList.add('selected');
            }

            // Update schemeFormData
            if (type === 'age') {
                schemeFormData.age = value ? parseInt(value) : null;
            } else if (type === 'state') {
                schemeFormData.state = value;
            }

            // Close dropdown
            if (wrapper) {
                wrapper.classList.remove('open');
            }
        });
    });
}

// ============ Carousel Navigation ============
function scrollCarousel(direction) {
    const carousel = document.getElementById('schemes-carousel');
    if (!carousel) return;

    const scrollAmount = 260; // Card width (220px) + gap (20px) + padding
    carousel.scrollBy({
        left: direction * scrollAmount,
        behavior: 'smooth'
    });
}

// ============ Page Navigation ============
function startChat() {
    document.getElementById('landing-page').classList.add('hidden');
    document.getElementById('chat-page').classList.remove('hidden');

    // Sync UI state
    if (currentUser) {
        updateUIForLoggedInUser();
    } else {
        updateUIForAnonymousUser();
    }
}

function continueAsGuest() {
    // Skip sign-in and go directly to chat as a guest
    startChat();
}

// ============ Scheme Finder Modal ============
async function openSchemeFinderModal(mode = 'signup') {
    const modal = document.getElementById('scheme-finder-modal');

    // 1. Get the Correct Elements
    const title = modal.querySelector('.modal-title');

    // FIX: Changed 'btn-submit-profile' to 'sf-submit-btn'
    const submitBtn = document.getElementById('sf-submit-btn');

    // Debugging: Check if elements exist
    if (!submitBtn) {
        console.error("CRITICAL ERROR: 'sf-submit-btn' not found in DOM");
        return;
    }

    resetSchemeFinderUI();

    if (mode === 'edit') {
        // --- EDIT MODE LOGIC ---

        // Hide Auth Header (The "Create Account" text)
        const createAccountHeader = modal.querySelector('h3[data-i18n="sf_h_account"]');
        if (createAccountHeader) {
            const authContainer = createAccountHeader.closest('.form-section');
            if (authContainer) authContainer.style.display = 'none';
        }

        // Change Title
        if (currentUser && currentUser.name) {
            title.textContent = `Edit Profile: ${currentUser.name}`;
            title.removeAttribute('data-i18n');
        } else {
            title.textContent = "Edit Your Profile";
        }

        // Show OCR section in Edit mode
        const ocrSection = document.getElementById('edit-ocr-section');
        if (ocrSection) ocrSection.classList.remove('hidden');

        // Change Button Text & Action
        // Use innerHTML to preserve any potential spans/icons
        submitBtn.innerHTML = "<span>Edit Profile & Continue Chat</span>";
        submitBtn.removeAttribute('onclick'); // Remove HTML onclick attribute
        submitBtn.onclick = submitEditProfile; // Re-bind to the edit function

        // Fetch Data
        try {
            const response = await fetch('http://127.0.0.1:8000/edit');
            const profile = await response.json();
            if (profile && Object.keys(profile).length > 0) {
                populateSchemeForm(profile);
            }
        } catch (e) {
            console.error("Failed to load profile", e);
        }

    } else {
        // --- SIGNUP MODE LOGIC ---

        // Show Auth Header
        const createAccountHeader = modal.querySelector('h3[data-i18n="sf_h_account"]');
        if (createAccountHeader) {
            const authContainer = createAccountHeader.closest('.form-section');
            if (authContainer) authContainer.style.display = 'block';
        }

        // Reset Title
        title.setAttribute('data-i18n', 'sf_modal_title');
        title.textContent = "Help us find the best schemes for you";

        // Reset Button
        submitBtn.innerHTML = "<span data-i18n='sf_btn_submit'>Submit Profile & Start Chat</span>";
        submitBtn.onclick = submitSchemeForm; // Re-bind to original function

        // Re-apply translation if needed
        if (typeof translatePage === 'function' && currentLanguage) {
            translatePage(currentLanguage);
        }
    }

    modal.classList.remove('hidden');
}

function closeSchemeFinderModal() {
    document.getElementById('scheme-finder-modal').classList.add('hidden');
}

function handleSchemeFinderOverlayClick(event) {
    if (event.target === event.currentTarget) {
        closeSchemeFinderModal();
    }
}

function resetSchemeFormData() {
    schemeFormData = {
        name: '',
        email: '',
        password: '',
        gender: null,
        age: null,
        state: '',
        area: null,
        category: null,
        is_disabled: null,
        is_minority: null,
        is_student: null,
        employment_status: null,
        is_govt_employee: null,
        annual_income: null,
        family_income: null
    };

    // Reset form inputs
    document.querySelectorAll('.scheme-step input').forEach(input => input.value = '');
    document.querySelectorAll('.scheme-step select').forEach(select => select.selectedIndex = 0);
    document.querySelectorAll('.selection-card, .toggle-btn, .category-card').forEach(el => {
        el.classList.remove('selected');
    });
}





// ============ Edit Profile ============

function populateSchemeForm(data) {
    console.log('[POPULATE FORM] Received data:', data);

    // 1. Text Inputs
    if (data.name) document.getElementById('sf-name').value = data.name;
    // We skip email/password in edit mode usually, or you can populate email:
    if (data.email) document.getElementById('sf-email').value = data.email;

    // Age - using custom dropdown
    if (data.age) {
        document.getElementById('sf-age').value = data.age;
        const ageTrigger = document.getElementById('age-select-trigger');
        if (ageTrigger) {
            ageTrigger.querySelector('span').textContent = data.age.toString();
        }
        // Mark the option as selected
        const ageOptions = document.getElementById('age-select-options');
        if (ageOptions) {
            ageOptions.querySelectorAll('.custom-select-option').forEach(opt => {
                opt.classList.toggle('selected', opt.dataset.value === data.age.toString());
            });
        }
    }

    // State - using custom dropdown
    if (data.state) {
        document.getElementById('sf-state').value = data.state;
        const stateOptions = document.getElementById('state-select-options');
        if (stateOptions) {
            const selectedOption = stateOptions.querySelector(`[data-value="${data.state}"]`);
            if (selectedOption) {
                const stateTrigger = document.getElementById('state-select-trigger');
                if (stateTrigger) {
                    stateTrigger.querySelector('span').textContent = selectedOption.textContent;
                }
                stateOptions.querySelectorAll('.custom-select-option').forEach(opt => {
                    opt.classList.toggle('selected', opt.dataset.value === data.state);
                });
            }
        }
    }

    if (data.annual_income) document.getElementById('sf-annual-income').value = data.annual_income;
    if (data.family_income) document.getElementById('sf-family-income').value = data.family_income;

    // 2. Update Global State - IMPORTANT: Populate ALL fields from database
    schemeFormData.name = data.name || schemeFormData.name;
    schemeFormData.email = data.email || schemeFormData.email;
    schemeFormData.gender = data.gender || schemeFormData.gender;
    schemeFormData.age = data.age || schemeFormData.age;
    schemeFormData.state = data.state || schemeFormData.state;
    schemeFormData.area = data.area || schemeFormData.area;
    schemeFormData.category = data.category || schemeFormData.category;
    schemeFormData.is_disabled = data.is_disabled !== undefined ? data.is_disabled : schemeFormData.is_disabled;
    schemeFormData.is_minority = data.is_minority !== undefined ? data.is_minority : schemeFormData.is_minority;
    schemeFormData.is_student = data.is_student !== undefined ? data.is_student : schemeFormData.is_student;
    schemeFormData.employment_status = data.employment_status || schemeFormData.employment_status;
    schemeFormData.is_govt_employee = data.is_govt_employee !== undefined ? data.is_govt_employee : schemeFormData.is_govt_employee;
    schemeFormData.annual_income = data.annual_income || schemeFormData.annual_income;
    schemeFormData.family_income = data.family_income || schemeFormData.family_income;

    // 3. Visually Select Cards (Gender, Category, etc.)
    highlightSelection('gender-selection', data.gender);
    highlightSelection('category-selection', data.category);
    highlightSelection('employment-selection', data.employment_status);

    // 4. Visually Select Toggles (Area, Boolean types)
    highlightToggle('area-selection', data.area);
    highlightToggle('disability-selection', data.is_disabled);
    highlightToggle('minority-selection', data.is_minority);
    highlightToggle('student-selection', data.is_student);
    highlightToggle('govt-employee-selection', data.is_govt_employee);

    console.log('[POPULATE FORM] Form populated successfully');
}
// Helper: Highlights standard selection cards
function highlightSelection(containerId, value) {
    if (!value) return;
    const container = document.getElementById(containerId);
    if (!container) return;

    // Remove existing selection
    container.querySelectorAll('.selection-card, .category-card').forEach(c => c.classList.remove('selected'));

    // Find new target
    const target = container.querySelector(`[data-value="${value}"]`);
    if (target) target.classList.add('selected');
}

// Helper: Highlights toggle buttons (Handles 'yes'/'no' and 'urban'/'rural')
function highlightToggle(containerId, value) {
    if (value === null || value === undefined) return;
    const container = document.getElementById(containerId);
    if (!container) return;

    // Convert boolean to string if needed (for data-value="yes"/"no")
    let stringVal = value;
    if (typeof value === 'boolean') {
        stringVal = value ? 'yes' : 'no';
    } else if (value === 1) {
        stringVal = 'yes';
    } else if (value === 0) {
        stringVal = 'no';
    }

    container.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('selected'));

    const target = container.querySelector(`[data-value="${stringVal}"]`);
    if (target) target.classList.add('selected');
}

function selectOptionByValue(fieldName, value) {
    if (!value) return;
    const cards = document.querySelectorAll(`.selection-card[onclick*="'${fieldName}'"]`);
    cards.forEach(card => {
        // extract value from onclick="selectCard(this, 'start_business')" -> 'start_business'
        // Actually the HTML is onclick="selectGender(this)" data-value="Male"
        // We need to find the card with data-value == value
        if (card.dataset.value === value) {
            if (fieldName === 'gender') selectGender(card);
            else if (fieldName === 'area') selectArea(card);
            else if (fieldName === 'category') selectCategory(card);
            else if (fieldName === 'employment_status') selectEmployment(card);
        }
    });
}

function selectBooleanOption(fieldName, value) {
    // value is 0 or 1 (or true/false). Logic expects 1/0? 
    // HTML: onclick="selectBoolean(this, 'is_disabled', 1)"
    const val = (value === true || value === 1 || value === '1') ? 1 : 0;
    const cards = document.querySelectorAll(`.selection-card[onclick*="'${fieldName}'"]`);
    cards.forEach(card => {
        // Check the 3rd argument of onclick, or simpler: check the text/structure? 
        // The onclick string is: selectBoolean(this, 'is_disabled', 1)
        if (card.getAttribute('onclick').includes(`, ${val})`)) {
            selectBoolean(card, fieldName, val);
        }
    });
}

async function submitEditProfile() {
    if (!validateFullForm()) return;
    collectFullFormData();

    const loading = document.getElementById('scheme-form-loading');
    if (loading) loading.classList.remove('hidden');

    try {
        const response = await fetch('http://127.0.0.1:8000/edit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(schemeFormData)
        });

        const data = await response.json();

        if (data.success) {
            // Update UI with new name if changed?
            if (schemeFormData.name) {
                const currentUserDisplay = document.getElementById('user-name-display');
                if (currentUserDisplay) currentUserDisplay.textContent = `Hello, ${schemeFormData.name}`;
                currentUser.name = schemeFormData.name;
            }
            // Silently close modal - no alert popup
            closeSchemeFinderModal();
        } else {
            alert(data.message || 'Failed to update profile');
        }
    } catch (error) {
        console.error('Profile update error:', error);
        alert('An error occurred. Please try again.');
    } finally {
        if (loading) loading.classList.add('hidden');
    }
}

function resetSchemeFinderUI() {
    // revert changes made by openEditProfileModal for normal "Sign Up" flow
    const modal = document.getElementById('scheme-finder-modal');
    const title = modal.querySelector('.modal-title');
    const submitBtn = document.getElementById('sf-submit-btn');

    // Show Auth Header
    const createAccountHeader = modal.querySelector('h3[data-i18n="sf_h_account"]');
    if (createAccountHeader) {
        const authContainer = createAccountHeader.closest('.form-section');
        if (authContainer) authContainer.style.display = 'block';
    }

    title.textContent = "Help us find the best schemes for you";
    title.setAttribute('data-i18n', 'sf_modal_title');

    // Hide OCR section in signup mode
    const ocrSection = document.getElementById('edit-ocr-section');
    if (ocrSection) ocrSection.classList.add('hidden');

    // Use innerHTML to allow for potential child spans
    submitBtn.innerHTML = "<span data-i18n='sf_btn_submit'>Submit Profile & Start Chat</span>";
    submitBtn.onclick = submitSchemeForm;

    // Clear form
    document.querySelectorAll('#scheme-finder-modal input[type="text"], #scheme-finder-modal input[type="email"], #scheme-finder-modal input[type="password"], #scheme-finder-modal input[type="number"]').forEach(i => i.value = '');
    document.querySelectorAll('.selection-card.selected').forEach(c => c.classList.remove('selected'));
    document.querySelectorAll('.toggle-btn.selected').forEach(c => c.classList.remove('selected'));
    document.querySelectorAll('.category-card.selected').forEach(c => c.classList.remove('selected'));

    // Reset custom dropdowns
    const ageTrigger = document.getElementById('age-select-trigger');
    if (ageTrigger) ageTrigger.querySelector('span').textContent = 'Select age';
    document.getElementById('sf-age').value = '';

    const stateTrigger = document.getElementById('state-select-trigger');
    if (stateTrigger) stateTrigger.querySelector('span').textContent = 'Select State';
    document.getElementById('sf-state').value = '';

    document.querySelectorAll('.custom-select-option.selected').forEach(c => c.classList.remove('selected'));

    schemeFormData = {
        gender: null,
        age: null,
        state: null,
        area: null,
        category: null,
        is_disabled: null,
        is_minority: null,
        is_student: null,
        employment_status: null,
        is_govt_employee: null,
        annual_income: null,
        family_income: null
    };
}

function validateFullForm() {
    const name = document.getElementById('sf-name').value.trim();
    const email = document.getElementById('sf-email').value.trim();
    const password = document.getElementById('sf-password').value;

    // Check if we are in Edit Mode (Password field is hidden)
    const createAccountHeader = document.querySelector('h3[data-i18n="sf_h_account"]');
    const authContainer = createAccountHeader ? createAccountHeader.closest('.form-section') : null;
    const isEditMode = authContainer && authContainer.style.display === 'none';

    // Only validate Auth fields if NOT in edit mode
    if (!isEditMode) {
        if (!name || name.length < 2) {
            alert('Please enter your name (at least 2 characters)');
            return false;
        }
        if (!email || !isValidEmail(email)) {
            alert('Please enter a valid email address');
            return false;
        }
        if (!password || password.length < 6) {
            alert('Password must be at least 6 characters');
            return false;
        }
    }

    console.log('[VALIDATE] schemeFormData:', schemeFormData);

    if (!schemeFormData.gender) {
        alert('Please select your gender');
        return false;
    }
    // ... (Rest of validation remains the same)
    if (!document.getElementById('sf-age').value) { alert('Please select your age'); return false; }
    if (!schemeFormData.area) { alert('Please select your area'); return false; }
    if (!schemeFormData.category) { alert('Please select your category'); return false; }

    // Note: Accept 0, 1, true, false as valid - only reject null/undefined
    if (schemeFormData.is_disabled === null || schemeFormData.is_disabled === undefined) {
        alert('Please indicate disability status');
        return false;
    }
    if (schemeFormData.is_minority === null || schemeFormData.is_minority === undefined) {
        alert('Please indicate minority status');
        return false;
    }
    if (schemeFormData.is_student === null || schemeFormData.is_student === undefined) {
        alert('Please indicate student status');
        return false;
    }
    if (!schemeFormData.employment_status) { alert('Please select employment status'); return false; }
    if (schemeFormData.is_govt_employee === null || schemeFormData.is_govt_employee === undefined) {
        alert('Please indicate govt employee status');
        return false;
    }

    return true;
}

function collectFullFormData() {
    schemeFormData.name = document.getElementById('sf-name').value.trim();
    schemeFormData.email = document.getElementById('sf-email').value.trim();
    schemeFormData.password = document.getElementById('sf-password').value;
    schemeFormData.age = parseInt(document.getElementById('sf-age').value) || null;

    schemeFormData.state = document.getElementById('sf-state').value;

    const annualIncome = document.getElementById('sf-annual-income').value;
    const familyIncome = document.getElementById('sf-family-income').value;
    schemeFormData.annual_income = annualIncome ? parseFloat(annualIncome) : null;
    schemeFormData.family_income = familyIncome ? parseFloat(familyIncome) : null;
}

async function submitSchemeForm() {
    if (!validateFullForm()) return;
    collectFullFormData();

    const loading = document.getElementById('scheme-form-loading');
    loading.classList.remove('hidden');

    try {
        const response = await fetch('http://127.0.0.1:8000/profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(schemeFormData)
        });

        const data = await response.json();

        if (data.success) {
            currentUser = {
                name: schemeFormData.name,
                user_id: data.user_id
            };
            updateUIForLoggedInUser();
            closeSchemeFinderModal();
            startChat();
        } else {
            alert(data.message || 'Failed to save profile');
        }
    } catch (error) {
        console.error('Profile save error:', error);
        alert('An error occurred. Please try again.');
    } finally {
        loading.classList.add('hidden');
    }
}

// ============ Selection Helpers ============
function selectCard(element, type) {
    const container = element.parentElement;
    container.querySelectorAll('.selection-card').forEach(card => {
        card.classList.remove('selected');
    });
    element.classList.add('selected');

    if (type === 'gender') {
        schemeFormData.gender = element.dataset.value;
    } else if (type === 'employment') {
        schemeFormData.employment_status = element.dataset.value;
        // Auto-select student status if "Student" or "College Student" is picked
        if (element.dataset.value === 'student' || element.dataset.value === 'college_student') {
            const studentSelection = document.getElementById('student-selection');
            if (studentSelection) {
                const yesBtn = studentSelection.querySelector('[data-value="yes"]');
                if (yesBtn) selectToggle(yesBtn, 'student');
            }
        }
    }
}

function selectToggle(element, type) {
    const container = element.parentElement;
    container.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    element.classList.add('selected');

    const value = element.dataset.value === 'yes';

    switch (type) {
        case 'area':
            schemeFormData.area = element.dataset.value;
            break;
        case 'disability':
            schemeFormData.is_disabled = value;
            break;
        case 'minority':
            schemeFormData.is_minority = value;
            break;
        case 'student':
            schemeFormData.is_student = value;
            break;
        case 'govt-employee':
            schemeFormData.is_govt_employee = value;
            break;
    }
}

function selectCategory(element) {
    const container = element.parentElement;
    container.querySelectorAll('.category-card').forEach(card => {
        card.classList.remove('selected');
    });
    element.classList.add('selected');
    schemeFormData.category = element.dataset.value;
}

// ============ Auth Modal ============
function openAuthModal(form = 'signin', authWall = false) {
    isAuthWall = authWall;

    const modal = document.getElementById('auth-modal');
    const authPrompt = document.getElementById('auth-prompt-message');

    if (authWall) {
        authPrompt.classList.remove('hidden');
    } else {
        authPrompt.classList.add('hidden');
    }

    clearErrors();
    modal.classList.remove('hidden');

    setTimeout(() => {
        document.getElementById('signin-email')?.focus();
    }, 100);
}

function closeAuthModal() {
    const modal = document.getElementById('auth-modal');
    modal.classList.add('hidden');
    isAuthWall = false;
}

function handleOverlayClick(event) {
    if (event.target === event.currentTarget) {
        if (!isAuthWall) {
            closeAuthModal();
        }
    }
}

function switchToSchemeFinderFromAuth(event) {
    event.preventDefault();
    closeAuthModal();
    openSchemeFinderModal();
}

function switchToSignInFromScheme(event) {
    event.preventDefault();
    closeSchemeFinderModal();
    openAuthModal('signin');
}



function closeSchemeFinderModal() {
    const modal = document.getElementById('scheme-finder-modal');
    modal.classList.add('hidden');
}

function handleSchemeFinderOverlayClick(event) {
    if (event.target === event.currentTarget) {
        closeSchemeFinderModal();
    }
}

// ============ Validation ============
function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function showError(fieldId, message) {
    const input = document.getElementById(fieldId);
    const errorEl = document.getElementById(`error-${fieldId}`);

    if (input && input.classList) {
        input.classList.add('error');
    }
    if (errorEl) {
        errorEl.textContent = message;
    }
}

function clearErrors() {
    document.querySelectorAll('.form-input').forEach(input => {
        input.classList.remove('error');
    });
    document.querySelectorAll('.form-error').forEach(error => {
        error.textContent = '';
    });
}

// ============ Form Submission ============
async function submitSignIn() {
    clearErrors();

    const email = document.getElementById('signin-email').value.trim();
    const password = document.getElementById('signin-password').value;

    let isValid = true;

    if (!email || !isValidEmail(email)) {
        showError('signin-email', 'Please enter a valid email address');
        isValid = false;
    }
    if (!password) {
        showError('signin-password', 'Please enter your password');
        isValid = false;
    }

    if (!isValid) return;

    showLoading(true);

    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (data.success) {
            currentUser = data.user;
            updateUIForLoggedInUser();
            closeAuthModal();

            const inputWrapper = document.querySelector('.input-wrapper');
            if (inputWrapper) {
                inputWrapper.classList.remove('disabled');
            }
            startChat();
        } else {
            showError('signin-password', data.message);
        }
    } catch (error) {
        console.error('Login error:', error);
        showError('signin-password', 'An error occurred. Please try again.');
    } finally {
        showLoading(false);
    }
}

async function handleLogout() {
    try {
        await fetch('/auth/logout', {
            method: 'POST',
            credentials: 'include'
        });

        currentUser = null;
        updateUIForAnonymousUser();

        // Redirect to landing page
        window.location.href = '/';
    } catch (error) {
        console.error('Logout error:', error);
        // Still redirect even if logout request fails
        window.location.href = '/';
    }
}

function showLoading(show) {
    const loading = document.getElementById('form-loading');
    if (show) {
        loading.classList.remove('hidden');
    } else {
        loading.classList.add('hidden');
    }
}

// ============ Chat Functions ============
async function sendMessage() {
    const input = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");

    const welcomeMsg = document.querySelector(".welcome-message");
    if (welcomeMsg) {
        welcomeMsg.remove();
    }

    const message = input.value.trim();
    if (!message) return;

    addMessage("You", message, "user");
    input.value = "";

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: 'include',
            body: JSON.stringify({
                message: message,
                history: chatHistory,
                source_lang: "auto", // Auto-detect input language
                target_lang: currentLanguage, // Force output to selected language
                user_id: currentUser ? currentUser.user_id : null // Pass user_id for authenticated users
            })
        });

        const data = await response.json();

        if (data.auth_required) {
            disableChat();
            openAuthModal('signin', true);
            return;
        }

        if (data.remaining_free !== null && data.remaining_free !== undefined && !currentUser) {
            updateResponseLimitBanner(data.remaining_free);
        }

        chatHistory.push({ role: "user", content: message });
        chatHistory.push({ role: "assistant", content: data.reply });

        addMessage("Assistant", data.reply || "Thinking...", "bot", data.sources);

    } catch (error) {
        console.error("Chat Error:", error);
        let errorMsg = "❌ An error occurred. Please try again.";
        if (error.message.includes("Failed to fetch")) {
            errorMsg = "❌ Unable to connect to server. Please ensure the backend is running.";
        }
        addMessage("Assistant", errorMsg, "bot");
    }
}

function addMessage(sender, text, className, sources = null) {
    if (!text) text = ""; // Safe handling for null/undefined
    const chatBox = document.getElementById("chat-box");

    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${className}`;

    let contentHtml = className === "bot" ? marked.parse(text || "") : text;

    msgDiv.innerHTML = `
        <div class="message-bubble">
            ${contentHtml}
        </div>
        <div class="message-label">${sender}</div>
    `;

    chatBox.appendChild(msgDiv);

    // Add quick action buttons after bot messages
    if (className === "bot" && text.length > 50) {
        // Extract scheme names from the response for contextual buttons
        const schemeNames = extractSchemeNamesFromResponse(text);

        // Detect if this is a greeting response (no schemes mentioned)
        const isGreeting = schemeNames.length === 0 ||
            text.toLowerCase().includes("welcome") ||
            text.toLowerCase().includes("hello") ||
            text.toLowerCase().includes("namaste") ||
            text.includes("स्वागत") ||
            text.includes("नमस्ते");

        // Get translations for current language
        const t = window.TRANSLATIONS && window.TRANSLATIONS[currentLanguage] ? window.TRANSLATIONS[currentLanguage] : {};

        const quickActionsDiv = document.createElement("div");
        quickActionsDiv.className = "quick-actions";

        // Translated labels with fallbacks
        const labelText = t.qa_label || "Quick Actions:";
        const findSchemesText = t.qa_find_schemes || "Find My Schemes";
        const browseCategoriesText = t.qa_browse_categories || "Browse Categories";
        const helpText = t.qa_help || "Help";
        const moreAboutText = t.qa_more_about || "More about";
        const moreSchemesText = t.qa_more_schemes || "More Schemes";
        const howToApplyText = t.qa_how_to_apply || "How to Apply";

        let buttonsHtml = `<div class="quick-actions-label">${labelText}</div><div class="quick-actions-buttons">`;

        if (isGreeting && schemeNames.length === 0) {
            // Greeting buttons - help user get started
            buttonsHtml += `<button class="quick-action-btn" onclick="sendQuickAction('Show me schemes I am eligible for')">${findSchemesText}</button>`;
            buttonsHtml += `<button class="quick-action-btn" onclick="sendQuickAction('What categories of schemes are available?')">${browseCategoriesText}</button>`;
            buttonsHtml += `<button class="quick-action-btn" onclick="sendQuickAction('How does this work?')">${helpText}</button>`;
        } else {
            // Scheme response buttons
            // Add "Tell me more" button for first scheme mentioned
            if (schemeNames.length > 0) {
                const shortName = schemeNames[0].substring(0, 15) + (schemeNames[0].length > 15 ? '...' : '');
                buttonsHtml += `<button class="quick-action-btn" onclick="sendQuickAction('Tell me more about ${schemeNames[0]}')">${moreAboutText} ${shortName}</button>`;
            }

            // Add general quick actions
            buttonsHtml += `<button class="quick-action-btn" onclick="sendQuickAction('Show me more schemes')">${moreSchemesText}</button>`;
            buttonsHtml += `<button class="quick-action-btn" onclick="sendQuickAction('How do I apply for these schemes?')">${howToApplyText}</button>`;
        }

        buttonsHtml += '</div>';
        quickActionsDiv.innerHTML = buttonsHtml;

        chatBox.appendChild(quickActionsDiv);
    }

    chatBox.scrollTop = chatBox.scrollHeight;
}

// Extract scheme names from bot response text
function extractSchemeNamesFromResponse(text) {
    const schemeNames = [];
    // Look for patterns like [Scheme Name] or **[Scheme Name]**
    const patterns = [
        /\[([^\]]+)\]/g,  // [Scheme Name] - simple brackets
        /\*\*\[([^\]]+)\]\*\*/g,  // **[Scheme Name]**
        /\*\*([^*\n]+)\*\*\s*\n/g,  // **Scheme Name** at start of line
    ];

    for (const pattern of patterns) {
        let match;
        while ((match = pattern.exec(text)) !== null) {
            const name = match[1].trim();
            // Filter out common non-scheme text
            if (name.length > 3 && name.length < 100 &&
                !schemeNames.includes(name) &&
                !name.toLowerCase().includes('why you') &&
                !name.toLowerCase().includes('benefit') &&
                !name.toLowerCase().includes('how to')) {
                schemeNames.push(name);
            }
        }
    }

    return schemeNames.slice(0, 3); // Max 3 schemes
}

// Send quick action as a message
function sendQuickAction(message) {
    const input = document.getElementById("user-input");
    if (input) {
        input.value = message;
        sendMessage();
    }
}

function disableChat() {
    const inputWrapper = document.querySelector('.input-wrapper');
    if (inputWrapper) {
        inputWrapper.classList.add('disabled');
    }
}

function updateResponseLimitBanner(remaining) {
    const banner = document.getElementById('response-limit-banner');
    const text = document.getElementById('responses-remaining');

    if (remaining <= 0) {
        banner.classList.add('hidden');
    } else {
        banner.classList.remove('hidden');
        text.textContent = `${remaining} free message${remaining !== 1 ? 's' : ''} remaining`;
    }
}

// ============ Scheme Carousel Functions ============
function schemeCarouselNext() {
    const track = document.getElementById('schemesTrack');
    // Scroll by card width (250px) + gap (24px)
    track.scrollBy({ left: 274, behavior: 'smooth' });
}

function schemeCarouselPrev() {
    const track = document.getElementById('schemesTrack');
    track.scrollBy({ left: -274, behavior: 'smooth' });
}

// ============ Verification Modal (Post Sign-Up OCR) ============
let verificationFile = null;

function openVerificationModal() {
    const modal = document.getElementById('verification-modal');
    resetVerificationModal();
    modal.classList.remove('hidden');
}

function closeVerificationModal() {
    document.getElementById('verification-modal').classList.add('hidden');
    verificationFile = null;
}

// Open verification modal from Edit Profile mode
function openVerificationModalFromEdit() {
    // Collect current form data for comparison
    collectFullFormData();
    // Close edit profile modal first
    closeSchemeFinderModal();
    // Open verification modal
    openVerificationModal();
}

function handleVerificationOverlayClick(event) {
    if (event.target === event.currentTarget) {
        skipVerification();
    }
}

function resetVerificationModal() {
    document.getElementById('verify-scan-section').classList.remove('hidden');
    document.getElementById('verify-file-display').classList.add('hidden');
    document.getElementById('verify-processing').classList.add('hidden');
    document.getElementById('verify-comparison').classList.add('hidden');
    document.getElementById('verify-error').classList.add('hidden');
    document.getElementById('verify-file-input').value = '';
    verificationFile = null;
}

function triggerVerificationFileInput() {
    document.getElementById('verify-file-input').click();
}

function handleVerificationFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
        showVerificationError('File too large. Maximum size is 5MB.');
        return;
    }

    // Validate file type
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'application/pdf'];
    if (!allowedTypes.includes(file.type)) {
        showVerificationError('Invalid file type. Please upload PNG, JPG, or PDF.');
        return;
    }

    verificationFile = file;
    document.getElementById('verify-file-name').textContent = file.name;
    document.getElementById('verify-scan-section').classList.add('hidden');
    document.getElementById('verify-file-display').classList.remove('hidden');
    document.getElementById('verify-error').classList.add('hidden');
}

async function processVerificationDocument() {
    if (!verificationFile) {
        showVerificationError('Please select a file first.');
        return;
    }

    // Show processing
    document.getElementById('verify-file-display').classList.add('hidden');
    document.getElementById('verify-processing').classList.remove('hidden');
    document.getElementById('verify-error').classList.add('hidden');

    try {
        const formData = new FormData();
        formData.append('file', verificationFile);

        const response = await fetch('/api/v1/ocr', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'OCR processing failed');
        }

        const result = await response.json();

        if (result.success) {
            displayComparisonResults(result.extracted_fields);
        } else {
            throw new Error(result.message || 'Failed to extract data');
        }

    } catch (error) {
        console.error('OCR Error:', error);
        showVerificationError(error.message || 'Failed to process document. Please try again.');
        document.getElementById('verify-processing').classList.add('hidden');
        document.getElementById('verify-scan-section').classList.remove('hidden');
    }
}

function displayComparisonResults(scannedData) {
    document.getElementById('verify-processing').classList.add('hidden');
    document.getElementById('verify-comparison').classList.remove('hidden');

    const tbody = document.getElementById('comparison-table-body');
    tbody.innerHTML = '';

    // Fields to compare
    const fields = [
        { key: 'name', label: 'Name', entered: schemeFormData.name },
        { key: 'age', label: 'Age', entered: schemeFormData.age },
        { key: 'gender', label: 'Gender', entered: schemeFormData.gender },
        { key: 'category', label: 'Category', entered: schemeFormData.category },
        { key: 'annual_income', label: 'Annual Income', entered: schemeFormData.annual_income }
    ];

    fields.forEach(field => {
        const enteredValue = field.entered || '-';
        const scannedValue = scannedData[field.key] || '-';

        // Check if values match
        const isMatch = compareValues(field.entered, scannedData[field.key]);

        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="field-name">${field.label}</td>
            <td>${formatValue(enteredValue)}</td>
            <td class="${isMatch ? 'value-match' : (scannedValue === '-' ? 'value-empty' : 'value-mismatch')}">${formatValue(scannedValue)}</td>
        `;
        tbody.appendChild(row);
    });

    // Update action buttons - add "Proceed" button
    const actionsDiv = document.querySelector('.verify-actions');
    actionsDiv.innerHTML = `
        <button class="btn btn-verify-scan btn-full" onclick="proceedAfterVerification()" style="margin-bottom: 8px;">
            Proceed to Chat
        </button>
        <button class="btn btn-outline btn-full" onclick="resetVerificationModal()">
            Scan Another Document
        </button>
    `;
}

function compareValues(entered, scanned) {
    if (!entered || !scanned) return false;
    if (entered === '-' || scanned === '-') return false;

    // Normalize for comparison
    const normalizedEntered = String(entered).toLowerCase().trim();
    const normalizedScanned = String(scanned).toLowerCase().trim();

    return normalizedEntered === normalizedScanned;
}

function formatValue(value) {
    if (value === null || value === undefined || value === '') return '-';
    if (typeof value === 'boolean') return value ? 'Yes' : 'No';
    return String(value);
}

function showVerificationError(message) {
    const errorDiv = document.getElementById('verify-error');
    document.getElementById('verify-error-message').textContent = message;
    errorDiv.classList.remove('hidden');
}

function skipVerification() {
    closeVerificationModal();
    startChat();
}

function proceedAfterVerification() {
    closeVerificationModal();
    startChat();
}

// Modify submitSchemeForm to show verification modal after sign-up
const originalSubmitSchemeForm = submitSchemeForm;
submitSchemeForm = async function () {
    if (!validateFullForm()) return;
    collectFullFormData();

    const loading = document.getElementById('scheme-form-loading');
    loading.classList.remove('hidden');

    try {
        const response = await fetch('http://127.0.0.1:8000/profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(schemeFormData)
        });

        const data = await response.json();

        if (data.success) {
            currentUser = {
                name: schemeFormData.name,
                user_id: data.user_id
            };
            updateUIForLoggedInUser();
            closeSchemeFinderModal();

            // Show verification modal instead of directly starting chat
            openVerificationModal();
        } else {
            alert(data.message || 'Failed to save profile');
        }
    } catch (error) {
        console.error('Profile save error:', error);
        alert('An error occurred. Please try again.');
    } finally {
        loading.classList.add('hidden');
    }
};
