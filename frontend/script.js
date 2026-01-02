// ============ State Management ============
let currentUser = null;
let sessionId = null;
let chatHistory = [];
let currentForm = 'signup';
let currentStep = 1;
let isAuthWall = false;

// ============ Initialization ============
document.addEventListener('DOMContentLoaded', async () => {
    await checkAuthStatus();
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
    // Update chat page
    const userMenu = document.getElementById('user-menu');
    const authButtons = document.getElementById('auth-buttons');
    const userNameDisplay = document.getElementById('user-name-display');

    if (userMenu && authButtons && currentUser) {
        userMenu.classList.remove('hidden');
        authButtons.classList.add('hidden');
        userNameDisplay.textContent = `Hello, ${currentUser.name}`;
    }

    // Hide response limit banner for logged in users
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

// ============ Page Navigation ============
function startChat() {
    document.getElementById('landing-page').classList.add('hidden');
    document.getElementById('chat-page').classList.remove('hidden');
}

// ============ Auth Modal ============
function openAuthModal(form = 'signup', authWall = false) {
    currentForm = form;
    isAuthWall = authWall;
    currentStep = 1;

    const modal = document.getElementById('auth-modal');
    const progressIndicator = document.getElementById('progress-indicator');
    const authPrompt = document.getElementById('auth-prompt-message');

    // Show/hide progress indicator based on form type
    if (form === 'signin') {
        progressIndicator.classList.add('hidden');
    } else {
        progressIndicator.classList.remove('hidden');
        updateProgressIndicator();
    }

    // Show auth prompt message if this is an auth wall
    if (authWall) {
        authPrompt.classList.remove('hidden');
    } else {
        authPrompt.classList.add('hidden');
    }

    // Reset form and show correct slide
    clearErrors();
    resetFormFields();
    updateFormSlide();

    modal.classList.remove('hidden');

    // Focus first input
    setTimeout(() => {
        const firstInput = document.querySelector('.form-slide:not([style*="display: none"]) .form-input');
        if (firstInput) firstInput.focus();
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

function updateFormSlide() {
    const slides = document.getElementById('form-slides');
    const allSlides = document.querySelectorAll('.form-slide');

    // Calculate slide index
    let slideIndex = 0;

    if (currentForm === 'signup') {
        slideIndex = currentStep - 1; // 0, 1, or 2
    } else {
        slideIndex = 3; // signin is the 4th slide (index 3)
    }

    // Transform to show correct slide
    slides.style.transform = `translateX(-${slideIndex * 100}%)`;
}

function updateProgressIndicator() {
    const steps = document.querySelectorAll('.progress-step');
    const lines = document.querySelectorAll('.progress-line');

    steps.forEach((step, index) => {
        const stepNum = index + 1;
        step.classList.remove('active', 'completed');

        if (stepNum < currentStep) {
            step.classList.add('completed');
        } else if (stepNum === currentStep) {
            step.classList.add('active');
        }
    });

    lines.forEach((line, index) => {
        if (index < currentStep - 1) {
            line.classList.add('active');
        } else {
            line.classList.remove('active');
        }
    });
}

// ============ Form Navigation ============
function nextStep() {
    if (!validateCurrentStep()) return;

    currentStep++;
    updateFormSlide();
    updateProgressIndicator();

    // Focus first input of new slide
    setTimeout(() => {
        const inputs = document.querySelectorAll(`[data-form="signup"][data-step="${currentStep}"] .form-input`);
        if (inputs.length > 0) inputs[0].focus();
    }, 400);
}

function prevStep() {
    if (currentStep > 1) {
        currentStep--;
        updateFormSlide();
        updateProgressIndicator();
    }
}

function switchToSignIn(event) {
    event.preventDefault();
    currentForm = 'signin';
    currentStep = 1;
    clearErrors();
    resetFormFields();

    const progressIndicator = document.getElementById('progress-indicator');
    progressIndicator.classList.add('hidden');

    updateFormSlide();
}

function switchToSignUp(event) {
    event.preventDefault();
    currentForm = 'signup';
    currentStep = 1;
    clearErrors();
    resetFormFields();

    const progressIndicator = document.getElementById('progress-indicator');
    progressIndicator.classList.remove('hidden');
    updateProgressIndicator();

    updateFormSlide();
}

// ============ Validation ============
function validateCurrentStep() {
    clearErrors();
    let isValid = true;

    if (currentForm === 'signup') {
        switch (currentStep) {
            case 1:
                const name = document.getElementById('signup-name').value.trim();
                if (!name || name.length < 2) {
                    showError('signup-name', 'Please enter your name (at least 2 characters)');
                    isValid = false;
                }
                break;
            case 2:
                const email = document.getElementById('signup-email').value.trim();
                const password = document.getElementById('signup-password').value;

                if (!email || !isValidEmail(email)) {
                    showError('signup-email', 'Please enter a valid email address');
                    isValid = false;
                }
                if (!password || password.length < 6) {
                    showError('signup-password', 'Password must be at least 6 characters');
                    isValid = false;
                }
                break;
            case 3:
                const confirmPassword = document.getElementById('signup-confirm-password').value;
                const originalPassword = document.getElementById('signup-password').value;
                const terms = document.getElementById('signup-terms').checked;

                if (confirmPassword !== originalPassword) {
                    showError('signup-confirm-password', 'Passwords do not match');
                    isValid = false;
                }
                if (!terms) {
                    showError('signup-terms', 'You must agree to the Terms of Service');
                    isValid = false;
                }
                break;
        }
    }

    return isValid;
}

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

function resetFormFields() {
    document.querySelectorAll('.form-input').forEach(input => {
        input.value = '';
    });
    document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
        checkbox.checked = false;
    });
}

// ============ Form Submission ============
async function submitSignUp() {
    if (!validateCurrentStep()) return;

    const name = document.getElementById('signup-name').value.trim();
    const email = document.getElementById('signup-email').value.trim();
    const password = document.getElementById('signup-password').value;

    showLoading(true);

    try {
        const response = await fetch('/auth/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ name, email, password })
        });

        const data = await response.json();

        if (data.success) {
            currentUser = data.user;
            updateUIForLoggedInUser();
            closeAuthModal();

            // Re-enable input if it was disabled due to auth wall
            const inputArea = document.getElementById('input-area');
            const inputWrapper = inputArea.querySelector('.input-wrapper');
            if (inputWrapper) {
                inputWrapper.classList.remove('disabled');
            }
        } else {
            // Show error on appropriate field
            if (data.message.toLowerCase().includes('email')) {
                currentStep = 2;
                updateFormSlide();
                updateProgressIndicator();
                setTimeout(() => showError('signup-email', data.message), 400);
            } else {
                showError('signup-name', data.message);
            }
        }
    } catch (error) {
        console.error('Signup error:', error);
        showError('signup-name', 'An error occurred. Please try again.');
    } finally {
        showLoading(false);
    }
}

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

            // Re-enable input if it was disabled due to auth wall
            const inputArea = document.getElementById('input-area');
            const inputWrapper = inputArea.querySelector('.input-wrapper');
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

        // Show response limit banner again
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

    // Remove welcome message if it exists
    const welcomeMsg = document.querySelector(".welcome-message");
    if (welcomeMsg) {
        welcomeMsg.remove();
    }

    const message = input.value.trim();
    if (!message) return;

    // Show user message
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
                history: chatHistory
            })
        });

        const data = await response.json();

        // Check if auth is required
        if (data.auth_required) {
            // Disable input and show auth modal
            disableChat();
            openAuthModal('signup', true);
            return;
        }

        // Update remaining free messages banner
        if (data.remaining_free !== null && data.remaining_free !== undefined && !currentUser) {
            updateResponseLimitBanner(data.remaining_free);
        }

        // Update history with this turn
        chatHistory.push({ role: "user", content: message });
        chatHistory.push({ role: "assistant", content: data.reply });

        // IMPORTANT: markdown is parsed here
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

    // Helper to generate the content
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
