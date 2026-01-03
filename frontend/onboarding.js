// Onboarding Form Handler

document.addEventListener('DOMContentLoaded', function() {
    // Check if user already has a profile
    const existingProfile = localStorage.getItem('userProfile');
    if (existingProfile) {
        // User already onboarded, redirect to chatbot
        window.location.href = '/';
        return;
    }

    // Form submission handler
    const form = document.getElementById('onboarding-form');
    form.addEventListener('submit', handleFormSubmit);

    // Skip link handler
    const skipLink = document.getElementById('skip-link');
    skipLink.addEventListener('click', handleSkip);
});

function handleFormSubmit(event) {
    event.preventDefault();

    // Collect form data
    const formData = new FormData(event.target);
    const profile = {
        fullName: formData.get('fullName') || '',
        age: formData.get('age') ? parseInt(formData.get('age')) : null,
        gender: formData.get('gender') || '',
        state: formData.get('state') || '',
        category: formData.get('category') || '',
        income: formData.get('income') ? parseInt(formData.get('income')) : null,
        occupation: formData.get('occupation') || '',
        language: formData.get('language') || 'en',
        createdAt: new Date().toISOString()
    };

    // Validate required field (language)
    if (!profile.language) {
        alert('Please select your preferred language.');
        return;
    }

    // Save to localStorage
    saveProfile(profile);

    // Redirect to chatbot
    window.location.href = '/';
}

function handleSkip(event) {
    event.preventDefault();

    // Create minimal profile with just language
    const languageSelect = document.getElementById('language');
    const profile = {
        fullName: '',
        age: null,
        gender: '',
        state: '',
        category: '',
        income: null,
        occupation: '',
        language: languageSelect.value || 'en',
        createdAt: new Date().toISOString(),
        skipped: true
    };

    // Save to localStorage
    saveProfile(profile);

    // Redirect to chatbot
    window.location.href = '/';
}

function saveProfile(profile) {
    try {
        localStorage.setItem('userProfile', JSON.stringify(profile));
    } catch (error) {
        console.error('Failed to save profile to localStorage:', error);
    }
}

// Utility function to get user profile (can be imported by other scripts)
function getUserProfile() {
    try {
        const profile = localStorage.getItem('userProfile');
        return profile ? JSON.parse(profile) : null;
    } catch (error) {
        console.error('Failed to read profile from localStorage:', error);
        return null;
    }
}
