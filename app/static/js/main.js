/**
 * IFAM Sistema de Gerenciamento - Main JavaScript
 * Combines all functionality and initializes components
 */

// Main application object
const IFAM = window.IFAM || {};

// Initialize application
IFAM.init = function() {
    // Initialize UI components
    if (IFAM.ui) {
        IFAM.ui.init();
    }
    
    // Initialize form validation for all forms with data-validate attribute
    const forms = document.querySelectorAll('form[data-validate="true"]');
    forms.forEach(form => {
        if (IFAM.validation && form.id) {
            IFAM.validation.initFormValidation(form.id);
        }
    });
    
    // Initialize AJAX form submission for forms with data-ajax attribute
    const ajaxForms = document.querySelectorAll('form[data-ajax="true"]');
    ajaxForms.forEach(form => {
        IFAM.initAjaxForm(form);
    });
    
    // Initialize datetime pickers
    IFAM.initDateTimePickers();
    
    // Initialize tooltips and popovers if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        // Initialize tooltips
        const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltips.forEach(tooltip => {
            new bootstrap.Tooltip(tooltip);
        });
        
        // Initialize popovers
        const popovers = document.querySelectorAll('[data-bs-toggle="popover"]');
        popovers.forEach(popover => {
            new bootstrap.Popover(popover);
        });
    }
};

// Initialize AJAX form submission
IFAM.initAjaxForm = function(form) {
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        
        // Validate form if validation is available
        if (IFAM.validation && !IFAM.validation.validateForm(form)) {
            return false;
        }
        
        // Get form data
        const formData = new FormData(form);
        
        // Get submit button and set loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn && submitBtn.id && IFAM.ui && IFAM.ui.formButton) {
            IFAM.ui.formButton.setLoading(submitBtn.id);
        } else if (submitBtn) {
            submitBtn.setAttribute('disabled', 'disabled');
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Processando...';
        }
        
        // Show loading overlay
        if (IFAM.ui && IFAM.ui.loadingOverlay) {
            IFAM.ui.loadingOverlay.show();
        }
        
        // Send AJAX request
        fetch(form.action, {
            method: form.method || 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            // Parse response
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return response.json().then(data => {
                    return { status: response.status, data };
                });
            } else {
                return response.text().then(text => {
                    return { status: response.status, text };
                });
            }
        })
        .then(result => {
            // Hide loading overlay
            if (IFAM.ui && IFAM.ui.loadingOverlay) {
                IFAM.ui.loadingOverlay.hide();
            }
            
            // Reset submit button
            if (submitBtn && submitBtn.id && IFAM.ui && IFAM.ui.formButton) {
                IFAM.ui.formButton.resetLoading(submitBtn.id);
            } else if (submitBtn) {
                submitBtn.removeAttribute('disabled');
                submitBtn.innerHTML = 'Enviar';
            }
            
            // Handle response
            if (result.status >= 200 && result.status < 300) {
                // Success
                if (result.data) {
                    // Handle JSON response
                    if (result.data.redirect) {
                        // Redirect to specified URL
                        window.location.href = result.data.redirect;
                    } else if (result.data.message) {
                        // Show success message
                        if (IFAM.ui && IFAM.ui.toast) {
                            IFAM.ui.toast.show(result.data.message, 'success');
                        } else {
                            alert(result.data.message);
                        }
                        
                        // Reset form if specified
                        if (result.data.resetForm) {
                            form.reset();
                        }
                        
                        // Call success callback if specified
                        if (form.hasAttribute('data-success-callback')) {
                            const callbackName = form.getAttribute('data-success-callback');
                            if (typeof window[callbackName] === 'function') {
                                window[callbackName](result.data);
                            }
                        }
                    }
                } else if (result.text) {
                    // Handle HTML response (e.g., partial view)
                    const targetId = form.getAttribute('data-target');
                    if (targetId) {
                        const target = document.getElementById(targetId);
                        if (target) {
                            target.innerHTML = result.text;
                        }
                    } else {
                        // Show success message
                        if (IFAM.ui && IFAM.ui.toast) {
                            IFAM.ui.toast.show('Operação realizada com sucesso', 'success');
                        }
                    }
                }
            } else {
                // Error
                if (result.data && result.data.errors) {
                    // Handle validation errors
                    Object.keys(result.data.errors).forEach(key => {
                        const field = form.querySelector(`[name="${key}"]`);
                        if (field) {
                            field.classList.add('is-invalid');
                            
                            // Find or create feedback element
                            let feedback = field.nextElementSibling;
                            if (!feedback || !feedback.classList.contains('invalid-feedback')) {
                                feedback = document.createElement('div');
                                feedback.className = 'invalid-feedback';
                                field.parentNode.insertBefore(feedback, field.nextSibling);
                            }
                            
                            // Set error message
                            feedback.textContent = result.data.errors[key][0];
                        }
                    });
                } else if (result.data && result.data.message) {
                    // Show error message
                    if (IFAM.ui && IFAM.ui.toast) {
                        IFAM.ui.toast.show(result.data.message, 'error');
                    } else {
                        alert(result.data.message);
                    }
                } else {
                    // Generic error message
                    if (IFAM.ui && IFAM.ui.toast) {
                        IFAM.ui.toast.show('Ocorreu um erro ao processar a solicitação. Por favor, tente novamente.', 'error');
                    } else {
                        alert('Ocorreu um erro ao processar a solicitação. Por favor, tente novamente.');
                    }
                }
            }
        })
        .catch(error => {
            // Hide loading overlay
            if (IFAM.ui && IFAM.ui.loadingOverlay) {
                IFAM.ui.loadingOverlay.hide();
            }
            
            // Reset submit button
            if (submitBtn && submitBtn.id && IFAM.ui && IFAM.ui.formButton) {
                IFAM.ui.formButton.resetLoading(submitBtn.id);
            } else if (submitBtn) {
                submitBtn.removeAttribute('disabled');
                submitBtn.innerHTML = 'Enviar';
            }
            
            // Show error message
            if (IFAM.ui && IFAM.ui.toast) {
                IFAM.ui.toast.show('Ocorreu um erro ao processar a solicitação. Por favor, tente novamente.', 'error');
            } else {
                alert('Ocorreu um erro ao processar a solicitação. Por favor, tente novamente.');
            }
            
            console.error('AJAX request error:', error);
        });
    });
};

// Initialize datetime pickers
IFAM.initDateTimePickers = function() {
    // Initialize date inputs
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        // Set min date to today if not specified
        if (!input.hasAttribute('min') && !input.hasAttribute('data-no-min')) {
            const today = new Date().toISOString().split('T')[0];
            input.setAttribute('min', today);
        }
    });
    
    // Initialize time inputs
    const timeInputs = document.querySelectorAll('input[type="time"]');
    timeInputs.forEach(input => {
        // Set min and max time if not specified
        if (!input.hasAttribute('min') && !input.hasAttribute('data-no-min')) {
            input.setAttribute('min', '08:00');
        }
        
        if (!input.hasAttribute('max') && !input.hasAttribute('data-no-max')) {
            input.setAttribute('max', '22:00');
        }
    });
};

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    IFAM.init();
});

// Export IFAM object
window.IFAM = IFAM;
