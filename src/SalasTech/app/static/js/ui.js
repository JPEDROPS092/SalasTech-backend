/**
 * IFAM Sistema de Gerenciamento - UI Utilities
 * Loading indicators, toast notifications, and other UI enhancements
 */

// UI Utilities
const UIUtils = {
    // Loading overlay
    loadingOverlay: {
        /**
         * Show loading overlay
         * @param {string} message - Optional message to display
         */
        show: function(message) {
            // Create overlay if it doesn't exist
            let overlay = document.getElementById('loading-overlay');
            if (!overlay) {
                overlay = document.createElement('div');
                overlay.id = 'loading-overlay';
                overlay.className = 'loading-overlay';
                
                const spinner = document.createElement('div');
                spinner.className = 'loading-spinner';
                overlay.appendChild(spinner);
                
                if (message) {
                    const messageEl = document.createElement('div');
                    messageEl.className = 'loading-message mt-3';
                    messageEl.textContent = message;
                    overlay.appendChild(messageEl);
                }
                
                document.body.appendChild(overlay);
            } else if (message) {
                // Update message if overlay exists
                let messageEl = overlay.querySelector('.loading-message');
                if (!messageEl) {
                    messageEl = document.createElement('div');
                    messageEl.className = 'loading-message mt-3';
                    overlay.appendChild(messageEl);
                }
                messageEl.textContent = message;
            }
            
            // Show overlay
            setTimeout(() => {
                overlay.classList.add('active');
            }, 10); // Small delay for transition
        },
        
        /**
         * Hide loading overlay
         */
        hide: function() {
            const overlay = document.getElementById('loading-overlay');
            if (overlay) {
                overlay.classList.remove('active');
                
                // Remove after transition
                setTimeout(() => {
                    if (overlay.parentNode) {
                        overlay.parentNode.removeChild(overlay);
                    }
                }, 300);
            }
        }
    },
    
    // Toast notifications
    toast: {
        /**
         * Show toast notification
         * @param {string} message - Message to display
         * @param {string} type - Type of toast (success, error, warning, info)
         * @param {number} duration - Duration in milliseconds
         */
        show: function(message, type = 'info', duration = 5000) {
            // Create container if it doesn't exist
            let container = document.querySelector('.toast-container');
            if (!container) {
                container = document.createElement('div');
                container.className = 'toast-container';
                document.body.appendChild(container);
            }
            
            // Create toast
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.setAttribute('role', 'alert');
            
            // Set toast color based on type
            let bgColor, icon;
            switch (type) {
                case 'success':
                    bgColor = 'var(--success)';
                    icon = 'bi-check-circle-fill';
                    break;
                case 'error':
                    bgColor = 'var(--danger)';
                    icon = 'bi-exclamation-triangle-fill';
                    break;
                case 'warning':
                    bgColor = 'var(--warning)';
                    icon = 'bi-exclamation-circle-fill';
                    break;
                default:
                    bgColor = 'var(--info)';
                    icon = 'bi-info-circle-fill';
            }
            
            // Create toast content
            toast.innerHTML = `
                <div class="toast-header" style="background-color: ${bgColor}; color: white;">
                    <i class="bi ${icon} me-2"></i>
                    <strong class="me-auto">${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
                    <button type="button" class="btn-close btn-close-white" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            `;
            
            // Add toast to container
            container.appendChild(toast);
            
            // Add close button functionality
            const closeButton = toast.querySelector('.btn-close');
            closeButton.addEventListener('click', function() {
                UIUtils.toast.hide(toast);
            });
            
            // Auto-hide after duration
            if (duration > 0) {
                setTimeout(() => {
                    UIUtils.toast.hide(toast);
                }, duration);
            }
            
            return toast;
        },
        
        /**
         * Hide toast notification
         * @param {HTMLElement} toast - Toast element to hide
         */
        hide: function(toast) {
            toast.classList.add('hiding');
            
            // Remove after transition
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
                
                // Remove container if empty
                const container = document.querySelector('.toast-container');
                if (container && container.children.length === 0) {
                    container.parentNode.removeChild(container);
                }
            }, 300);
        }
    },
    
    // Form button loading state
    formButton: {
        /**
         * Set button to loading state
         * @param {string} buttonId - ID of the button
         * @param {string} loadingText - Text to display while loading
         */
        setLoading: function(buttonId, loadingText = 'Processando...') {
            const button = document.getElementById(buttonId);
            if (!button) return;
            
            // Save original text
            if (!button.hasAttribute('data-original-text')) {
                button.setAttribute('data-original-text', button.innerHTML);
            }
            
            // Set loading state
            button.setAttribute('disabled', 'disabled');
            button.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> ${loadingText}`;
        },
        
        /**
         * Reset button from loading state
         * @param {string} buttonId - ID of the button
         */
        resetLoading: function(buttonId) {
            const button = document.getElementById(buttonId);
            if (!button) return;
            
            // Restore original text
            if (button.hasAttribute('data-original-text')) {
                button.innerHTML = button.getAttribute('data-original-text');
                button.removeAttribute('data-original-text');
            }
            
            // Remove disabled attribute
            button.removeAttribute('disabled');
        }
    },
    
    // Sidebar toggle for mobile
    sidebar: {
        /**
         * Initialize sidebar toggle
         */
        init: function() {
            const toggleButton = document.querySelector('.navbar-toggler-sidebar');
            if (!toggleButton) return;
            
            const sidebar = document.querySelector('.sidebar');
            if (!sidebar) return;
            
            // Add click event
            toggleButton.addEventListener('click', function() {
                sidebar.classList.toggle('show');
            });
            
            // Close sidebar when clicking outside
            document.addEventListener('click', function(event) {
                if (!sidebar.contains(event.target) && !toggleButton.contains(event.target) && sidebar.classList.contains('show')) {
                    sidebar.classList.remove('show');
                }
            });
        }
    },
    
    // Responsive tables
    tables: {
        /**
         * Initialize responsive tables
         */
        init: function() {
            const tables = document.querySelectorAll('table:not(.table-responsive)');
            tables.forEach(table => {
                // Skip tables that are already wrapped
                if (table.parentNode.classList.contains('table-responsive')) return;
                
                // Wrap table in responsive div
                const wrapper = document.createElement('div');
                wrapper.className = 'table-responsive';
                table.parentNode.insertBefore(wrapper, table);
                wrapper.appendChild(table);
            });
        }
    },
    
    // Initialize all UI components
    init: function() {
        UIUtils.sidebar.init();
        UIUtils.tables.init();
        
        // Add loading overlay for AJAX requests
        if (window.jQuery) {
            $(document).ajaxStart(function() {
                UIUtils.loadingOverlay.show();
            }).ajaxStop(function() {
                UIUtils.loadingOverlay.hide();
            });
        }
    }
};

// Initialize UI utilities on DOM load
document.addEventListener('DOMContentLoaded', function() {
    UIUtils.init();
});

// Export UI utilities for use in other scripts
window.IFAM = window.IFAM || {};
window.IFAM.ui = UIUtils;
