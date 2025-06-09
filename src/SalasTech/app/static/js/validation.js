/**
 * IFAM Sistema de Gerenciamento - Form Validation
 * Client-side validation for all forms
 */

// Form validation configuration
const ValidationConfig = {
    // Common validation patterns
    patterns: {
        email: {
            regex: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
            message: 'Por favor, insira um email válido'
        },
        ifamEmail: {
            regex: /^[a-zA-Z0-9._%+-]+@ifam\.edu\.br$/,
            message: 'Por favor, use seu email institucional (@ifam.edu.br)'
        },
        password: {
            regex: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
            message: 'A senha deve ter pelo menos 8 caracteres, incluindo letras maiúsculas, minúsculas, números e caracteres especiais'
        },
        name: {
            regex: /^[A-Za-zÀ-ÖØ-öø-ÿ\s]{2,}$/,
            message: 'Por favor, insira um nome válido (mínimo 2 caracteres)'
        },
        phone: {
            regex: /^\(\d{2}\)\s\d{5}-\d{4}$/,
            message: 'Por favor, insira um telefone no formato (99) 99999-9999'
        },
        date: {
            regex: /^\d{4}-\d{2}-\d{2}$/,
            message: 'Por favor, insira uma data no formato AAAA-MM-DD'
        },
        time: {
            regex: /^\d{2}:\d{2}$/,
            message: 'Por favor, insira um horário no formato HH:MM'
        },
        number: {
            regex: /^\d+$/,
            message: 'Por favor, insira apenas números'
        }
    },

    // Validation messages
    messages: {
        required: 'Este campo é obrigatório',
        minLength: 'Este campo deve ter pelo menos {0} caracteres',
        maxLength: 'Este campo deve ter no máximo {0} caracteres',
        passwordMatch: 'As senhas não coincidem',
        dateRange: 'A data deve estar entre {0} e {1}',
        timeRange: 'O horário deve estar entre {0} e {1}',
        min: 'O valor mínimo é {0}',
        max: 'O valor máximo é {0}'
    }
};

/**
 * Validate a form field
 * @param {HTMLElement} field - The form field to validate
 * @returns {boolean} - Whether the field is valid
 */
function validateField(field) {
    // Skip disabled fields
    if (field.disabled) return true;
    
    // Get field value
    const value = field.value.trim();
    
    // Check if field is required
    const isRequired = field.hasAttribute('required');
    if (isRequired && value === '') {
        showError(field, ValidationConfig.messages.required);
        return false;
    }
    
    // Skip empty optional fields
    if (value === '' && !isRequired) {
        clearError(field);
        return true;
    }
    
    // Check min length
    const minLength = field.getAttribute('minlength');
    if (minLength && value.length < parseInt(minLength)) {
        showError(field, ValidationConfig.messages.minLength.replace('{0}', minLength));
        return false;
    }
    
    // Check max length
    const maxLength = field.getAttribute('maxlength');
    if (maxLength && value.length > parseInt(maxLength)) {
        showError(field, ValidationConfig.messages.maxLength.replace('{0}', maxLength));
        return false;
    }
    
    // Check pattern
    const pattern = field.getAttribute('data-pattern');
    if (pattern && ValidationConfig.patterns[pattern]) {
        const patternConfig = ValidationConfig.patterns[pattern];
        if (!patternConfig.regex.test(value)) {
            showError(field, patternConfig.message);
            return false;
        }
    }
    
    // Check custom regex pattern
    const regexPattern = field.getAttribute('pattern');
    if (regexPattern) {
        const regex = new RegExp(regexPattern);
        if (!regex.test(value)) {
            showError(field, field.getAttribute('title') || 'Por favor, insira um valor válido');
            return false;
        }
    }
    
    // Check min/max for number inputs
    if (field.type === 'number') {
        const min = field.getAttribute('min');
        const max = field.getAttribute('max');
        const numValue = parseFloat(value);
        
        if (min && numValue < parseFloat(min)) {
            showError(field, ValidationConfig.messages.min.replace('{0}', min));
            return false;
        }
        
        if (max && numValue > parseFloat(max)) {
            showError(field, ValidationConfig.messages.max.replace('{0}', max));
            return false;
        }
    }
    
    // Check date range
    if (field.type === 'date') {
        const min = field.getAttribute('min');
        const max = field.getAttribute('max');
        
        if (min && value < min) {
            showError(field, ValidationConfig.messages.dateRange.replace('{0}', formatDate(min)).replace('{1}', formatDate(max)));
            return false;
        }
        
        if (max && value > max) {
            showError(field, ValidationConfig.messages.dateRange.replace('{0}', formatDate(min)).replace('{1}', formatDate(max)));
            return false;
        }
    }
    
    // Check time range
    if (field.type === 'time') {
        const min = field.getAttribute('min');
        const max = field.getAttribute('max');
        
        if (min && value < min) {
            showError(field, ValidationConfig.messages.timeRange.replace('{0}', min).replace('{1}', max));
            return false;
        }
        
        if (max && value > max) {
            showError(field, ValidationConfig.messages.timeRange.replace('{0}', min).replace('{1}', max));
            return false;
        }
    }
    
    // Check password confirmation
    if (field.getAttribute('data-match')) {
        const matchFieldId = field.getAttribute('data-match');
        const matchField = document.getElementById(matchFieldId);
        
        if (matchField && value !== matchField.value) {
            showError(field, ValidationConfig.messages.passwordMatch);
            return false;
        }
    }
    
    // If we got here, the field is valid
    clearError(field);
    return true;
}

/**
 * Show error message for a field
 * @param {HTMLElement} field - The form field
 * @param {string} message - The error message
 */
function showError(field, message) {
    // Add invalid class
    field.classList.add('is-invalid');
    field.classList.remove('is-valid');
    
    // Find or create feedback element
    let feedback = field.nextElementSibling;
    if (!feedback || !feedback.classList.contains('invalid-feedback')) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        field.parentNode.insertBefore(feedback, field.nextSibling);
    }
    
    // Set error message
    feedback.textContent = message;
}

/**
 * Clear error message for a field
 * @param {HTMLElement} field - The form field
 */
function clearError(field) {
    // Remove invalid class
    field.classList.remove('is-invalid');
    field.classList.add('is-valid');
    
    // Remove feedback element
    const feedback = field.nextElementSibling;
    if (feedback && feedback.classList.contains('invalid-feedback')) {
        feedback.textContent = '';
    }
}

/**
 * Format date for display
 * @param {string} dateString - Date string in YYYY-MM-DD format
 * @returns {string} - Formatted date (DD/MM/YYYY)
 */
function formatDate(dateString) {
    if (!dateString) return '';
    
    const parts = dateString.split('-');
    if (parts.length !== 3) return dateString;
    
    return `${parts[2]}/${parts[1]}/${parts[0]}`;
}

/**
 * Validate an entire form
 * @param {HTMLFormElement} form - The form to validate
 * @returns {boolean} - Whether the form is valid
 */
function validateForm(form) {
    // Get all form fields
    const fields = form.querySelectorAll('input, select, textarea');
    
    // Validate each field
    let isValid = true;
    fields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * Initialize form validation for a form
 * @param {string} formId - The ID of the form to initialize
 * @param {Function} onSubmit - Optional callback for form submission
 */
function initFormValidation(formId, onSubmit) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    // Add validation on submit
    form.addEventListener('submit', function(event) {
        // Validate form
        const isValid = validateForm(form);
        
        // If not valid, prevent submission
        if (!isValid) {
            event.preventDefault();
            return false;
        }
        
        // If valid and callback provided, call it
        if (isValid && typeof onSubmit === 'function') {
            onSubmit(event);
        }
    });
    
    // Add validation on input
    const fields = form.querySelectorAll('input, select, textarea');
    fields.forEach(field => {
        field.addEventListener('blur', function() {
            validateField(field);
        });
        
        // For fields that should validate on input
        if (field.getAttribute('data-validate-on-input') === 'true') {
            field.addEventListener('input', function() {
                validateField(field);
            });
        }
    });
}

// Initialize all forms with data-validate attribute
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form[data-validate="true"]');
    forms.forEach(form => {
        initFormValidation(form.id);
    });
});

// Export functions for use in other scripts
window.IFAM = window.IFAM || {};
window.IFAM.validation = {
    validateField,
    validateForm,
    initFormValidation
};
