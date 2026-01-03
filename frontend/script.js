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
    const select = document.getElementById('sf-age');
    if (!select) return;

    // 1. Convert your API code (e.g., 'hi_IN') to Browser Locale (e.g., 'hi-IN')
    let locale = langCode.replace('_', '-');
    if (langCode === 'en_XX') locale = 'en-US'; // Fallback for your custom English code

    // 2. Save the user's currently selected age (so it doesn't reset)
    const currentSelection = select.value;

    // 3. Clear existing options (EXCEPT the first "Select age" placeholder)
    // We assume the first option is the placeholder
    const placeholderOption = select.options[0];
    select.innerHTML = ''; 
    select.appendChild(placeholderOption);

    // 4. Create the Number Formatter for the chosen language
    const numberFormatter = new Intl.NumberFormat(locale);

    // 5. Loop to create options
    for (let i = 18; i <= 100; i++) {
        const option = document.createElement('option');
        option.value = i; // The value sent to backend stays "18" (Integers)
        option.text = numberFormatter.format(i); // The display text becomes "१८"
        select.appendChild(option);
    }

    // 6. Restore the user's selection
    select.value = currentSelection;
}
// ============ Page Navigation ============
function startChat() {
    document.getElementById('landing-page').classList.add('hidden');
    document.getElementById('chat-page').classList.remove('hidden');
}

// ============ Scheme Finder Modal ============
function openSchemeFinderModal() {
    resetSchemeFormData();
    document.getElementById('scheme-finder-modal').classList.remove('hidden');
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





function validateFullForm() {
    const name = document.getElementById('sf-name').value.trim();
    const email = document.getElementById('sf-email').value.trim();
    const password = document.getElementById('sf-password').value;

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
    if (!schemeFormData.gender) {
        alert('Please select your gender');
        return false;
    }
    if (!document.getElementById('sf-age').value) {
        alert('Please select your age');
        return false;
    }
    if (!schemeFormData.area) {
        alert('Please select your area of residence');
        return false;
    }
    if (!schemeFormData.category) {
        alert('Please select your category');
        return false;
    }
    if (schemeFormData.is_disabled === null) {
        alert('Please indicate if you have a disability');
        return false;
    }
    if (schemeFormData.is_minority === null) {
        alert('Please indicate if you belong to a minority');
        return false;
    }
    if (schemeFormData.is_student === null) {
        alert('Please indicate if you are a student');
        return false;
    }
    if (!schemeFormData.employment_status) {
        alert('Please select your employment status');
        return false;
    }
    if (schemeFormData.is_govt_employee === null) {
        alert('Please indicate if you are a government employee');
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
