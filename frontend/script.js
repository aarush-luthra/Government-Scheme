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

// Theme State
let isDarkMode = localStorage.getItem('theme') === 'dark';

// ============ Initialization ============
document.addEventListener('DOMContentLoaded', async () => {
    await checkAuthStatus();
    initializeTheme();
    initializeLanguage();
    initializeLanguageDropdowns();
    initializeCustomSelects();
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
        }
    } catch (error) {
        console.error('Auth check failed:', error);
    }
}

function updateUIForLoggedInUser() {
    const userMenu = document.getElementById('user-menu');
    const authButtons = document.getElementById('auth-buttons');
    const userNameDisplay = document.getElementById('user-name-display');

    if (userMenu && authButtons && currentUser) {
        userMenu.classList.remove('hidden');
        authButtons.classList.add('hidden');
        userNameDisplay.textContent = `Hello, ${currentUser.name}`;
    }

    const responseLimitBanner = document.getElementById('response-limit-banner');
    if (responseLimitBanner) {
        responseLimitBanner.classList.add('hidden');
    }
}

function updateUIForAnonymousUser() {
    const userMenu = document.getElementById('user-menu');
    const authButtons = document.getElementById('auth-buttons');

    if (userMenu && authButtons) {
        userMenu.classList.add('hidden');
        authButtons.classList.remove('hidden');
    }
}

// ============ Theme Management ============
function initializeTheme() {
    if (isDarkMode) {
        document.documentElement.setAttribute('data-theme', 'dark');
    }
}

function toggleDarkMode() {
    isDarkMode = !isDarkMode;

    if (isDarkMode) {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
    } else {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('theme', 'light');
    }
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

function selectLanguage(langCode, source) {
    currentLanguage = langCode;
    localStorage.setItem('language', langCode);

    updateLanguageDisplay(langCode);
    translatePage(langCode);

    // Close dropdowns
    document.getElementById('language-dropdown')?.classList.remove('open');
    document.getElementById('chat-language-dropdown')?.classList.remove('open');
}

async function translatePage(targetLang) {
    if (targetLang === 'en_XX') {
        // Restore Text
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.dataset.i18n;
            if (i18nOriginals[key]) {
                el.innerText = i18nOriginals[key];
            }
        });
        // Restore Placeholders - NEW
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.dataset.i18nPlaceholder + '_pl';
            if (i18nOriginals[key]) {
                el.setAttribute('placeholder', i18nOriginals[key]);
            }
        });
        return;
    }

    // Prepare texts to translate
    const textElements = Array.from(document.querySelectorAll('[data-i18n]'));
    const placeholderElements = Array.from(document.querySelectorAll('[data-i18n-placeholder]'));

    // We combine both lists into one array to send to the backend
    // We prioritize using the 'i18nOriginals' as the source to ensure we always translate from English
    const textsToTranslate = [
        ...textElements.map(el => i18nOriginals[el.dataset.i18n] || el.innerText.trim()),
        ...placeholderElements.map(el => i18nOriginals[el.dataset.i18nPlaceholder + '_pl'] || el.getAttribute('placeholder'))
    ];
    if (textsToTranslate.length === 0) return;

    try {
        // Optional: Show loading cursor
        document.body.style.cursor = 'wait';

        const response = await fetch('/translate/batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                texts: textsToTranslate,
                source_lang: 'en_XX',
                target_lang: targetLang
            })
        });

        const data = await response.json();

        if (data.translations) {
            let tIndex = 0;

            // First, apply translations to Text Elements (Labels, Headers)
            textElements.forEach(el => {
                if (data.translations[tIndex]) {
                    el.innerText = data.translations[tIndex];
                }
                tIndex++;
            });

            // Next, apply translations to Placeholder Elements (Inputs)
            placeholderElements.forEach(el => {
                if (data.translations[tIndex]) {
                    el.setAttribute('placeholder', data.translations[tIndex]);
                }
                tIndex++;
            });
        }
    } catch (error) {
        console.error('Page translation failed:', error);
    } finally {
        document.body.style.cursor = 'default';
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
    for (let i = 18; i <= 100; i++) {
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
// ============ Page Navigation ============
function startChat() {
    document.getElementById('landing-page').classList.add('hidden');
    document.getElementById('chat-page').classList.remove('hidden');
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

        // Change Button Text & Action
        // Use innerHTML to preserve any potential spans/icons
        submitBtn.innerHTML = "<span>Edit Profile & Continue Chat</span>";
        submitBtn.onclick = submitEditProfile; // Re-bind to the edit function

        // Fetch Data
        try {
            const response = await fetch('/edit');
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
        const response = await fetch('/edit', {
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
        const response = await fetch('/profile', {
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

        const responseLimitBanner = document.getElementById('response-limit-banner');
        if (responseLimitBanner) {
            responseLimitBanner.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Logout error:', error);
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
                target_lang: currentLanguage // Force output to selected language
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

        addMessage("Assistant", data.reply, "bot");

    } catch (error) {
        addMessage("Assistant", "❌ Unable to connect to server. Please ensure the backend is running.", "bot");
        console.error(error);
    }
}

function addMessage(sender, text, className) {
    const chatBox = document.getElementById("chat-box");

    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${className}`;

    const contentHtml = className === "bot" ? marked.parse(text) : text;

    msgDiv.innerHTML = `
        <div class="message-bubble">
            ${contentHtml}
        </div>
        <div class="message-label">${sender}</div>
    `;

    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
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
