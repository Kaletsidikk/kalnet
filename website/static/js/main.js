/**
 * Main JavaScript for Printing Business Platform Website
 */

// Global configuration
const API_BASE_URL = window.location.origin + '/api';

// Utility functions
const Utils = {
    /**
     * Show loading state on button
     */
    setButtonLoading: function(button, loading = true) {
        if (loading) {
            button.classList.add('btn-loading');
            button.disabled = true;
            
            // Add spinner if not exists
            if (!button.querySelector('.spinner-border')) {
                const spinner = document.createElement('div');
                spinner.className = 'spinner-border spinner-border-sm';
                spinner.setAttribute('role', 'status');
                button.appendChild(spinner);
            }
        } else {
            button.classList.remove('btn-loading');
            button.disabled = false;
            
            // Remove spinner
            const spinner = button.querySelector('.spinner-border');
            if (spinner) {
                spinner.remove();
            }
        }
    },

    /**
     * Show alert message
     */
    showAlert: function(message, type = 'success', container = null) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);
        } else {
            document.body.insertAdjacentElement('afterbegin', alertDiv);
        }
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv && alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    },

    /**
     * Validate form field
     */
    validateField: function(field, validationRules) {
        const value = field.value.trim();
        const fieldName = field.getAttribute('name');
        const rules = validationRules[fieldName];
        
        if (!rules) return { valid: true, message: '' };
        
        // Required validation
        if (rules.required && !value) {
            return { valid: false, message: `${fieldName} is required` };
        }
        
        // Min length validation
        if (rules.min_length && value.length < rules.min_length) {
            return { valid: false, message: `${fieldName} must be at least ${rules.min_length} characters` };
        }
        
        // Max length validation
        if (rules.max_length && value.length > rules.max_length) {
            return { valid: false, message: `${fieldName} cannot exceed ${rules.max_length} characters` };
        }
        
        // Pattern validation
        if (rules.pattern && value && !new RegExp(rules.pattern).test(value)) {
            return { valid: false, message: `Please enter a valid ${fieldName}` };
        }
        
        return { valid: true, message: '' };
    },

    /**
     * Set field validation state
     */
    setFieldValidation: function(field, isValid, message = '') {
        const feedbackElement = field.parentNode.querySelector('.invalid-feedback, .valid-feedback');
        
        // Remove existing classes
        field.classList.remove('is-valid', 'is-invalid');
        
        if (isValid) {
            field.classList.add('is-valid');
            if (feedbackElement) {
                feedbackElement.className = 'valid-feedback';
                feedbackElement.textContent = 'Looks good!';
            }
        } else {
            field.classList.add('is-invalid');
            if (feedbackElement) {
                feedbackElement.className = 'invalid-feedback';
                feedbackElement.textContent = message;
            } else {
                // Create feedback element if it doesn't exist
                const newFeedback = document.createElement('div');
                newFeedback.className = 'invalid-feedback';
                newFeedback.textContent = message;
                field.parentNode.appendChild(newFeedback);
            }
        }
    },

    /**
     * Format date for input
     */
    formatDate: function(date) {
        const day = date.getDate().toString().padStart(2, '0');
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const year = date.getFullYear();
        return `${day}/${month}/${year}`;
    },

    /**
     * Debounce function
     */
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// Form validation rules (matching backend)
const VALIDATION_RULES = {
    name: {
        required: true,
        min_length: 2,
        max_length: 50
    },
    company: {
        required: false,
        max_length: 100
    },
    email: {
        required: true,
        pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    },
    phone: {
        required: true,
        min_length: 10,
        max_length: 15
    },
    message: {
        required: true,
        min_length: 10,
        max_length: 1000
    }
};

// Form handlers
const FormHandlers = {
    /**
     * Handle order form submission
     */
    handleOrderForm: function() {
        const form = document.getElementById('orderForm');
        if (!form) return;

        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitBtn = form.querySelector('button[type="submit"]');
            const formData = new FormData(form);
            
            // Convert FormData to object
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });
            
            // Show loading state
            Utils.setButtonLoading(submitBtn, true);
            
            try {
                const response = await fetch(`${API_BASE_URL}/order`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    Utils.showAlert(
                        `<i class="fas fa-check-circle me-2"></i>${result.message} Order ID: #${result.order_id}`,
                        'success',
                        form.parentNode
                    );
                    form.reset();
                } else {
                    Utils.showAlert(
                        `<i class="fas fa-exclamation-triangle me-2"></i>${result.error}`,
                        'danger',
                        form.parentNode
                    );
                }
                
            } catch (error) {
                console.error('Order submission error:', error);
                Utils.showAlert(
                    '<i class="fas fa-times-circle me-2"></i>Network error. Please try again.',
                    'danger',
                    form.parentNode
                );
            } finally {
                Utils.setButtonLoading(submitBtn, false);
            }
        });
    },

    /**
     * Handle schedule form submission
     */
    handleScheduleForm: function() {
        const form = document.getElementById('scheduleForm');
        if (!form) return;

        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitBtn = form.querySelector('button[type="submit"]');
            const formData = new FormData(form);
            
            // Convert FormData to object
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });
            
            // Show loading state
            Utils.setButtonLoading(submitBtn, true);
            
            try {
                const response = await fetch(`${API_BASE_URL}/schedule`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    Utils.showAlert(
                        `<i class="fas fa-calendar-check me-2"></i>${result.message} Schedule ID: #${result.schedule_id}`,
                        'success',
                        form.parentNode
                    );
                    form.reset();
                } else {
                    Utils.showAlert(
                        `<i class="fas fa-exclamation-triangle me-2"></i>${result.error}`,
                        'danger',
                        form.parentNode
                    );
                }
                
            } catch (error) {
                console.error('Schedule submission error:', error);
                Utils.showAlert(
                    '<i class="fas fa-times-circle me-2"></i>Network error. Please try again.',
                    'danger',
                    form.parentNode
                );
            } finally {
                Utils.setButtonLoading(submitBtn, false);
            }
        });
    },

    /**
     * Handle contact form submission
     */
    handleContactForm: function() {
        const form = document.getElementById('contactForm');
        if (!form) return;

        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitBtn = form.querySelector('button[type="submit"]');
            const formData = new FormData(form);
            
            // Convert FormData to object
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });
            
            // Show loading state
            Utils.setButtonLoading(submitBtn, true);
            
            try {
                const response = await fetch(`${API_BASE_URL}/message`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    Utils.showAlert(
                        `<i class="fas fa-paper-plane me-2"></i>${result.message} Message ID: #${result.message_id}`,
                        'success',
                        form.parentNode
                    );
                    form.reset();
                } else {
                    Utils.showAlert(
                        `<i class="fas fa-exclamation-triangle me-2"></i>${result.error}`,
                        'danger',
                        form.parentNode
                    );
                }
                
            } catch (error) {
                console.error('Message submission error:', error);
                Utils.showAlert(
                    '<i class="fas fa-times-circle me-2"></i>Network error. Please try again.',
                    'danger',
                    form.parentNode
                );
            } finally {
                Utils.setButtonLoading(submitBtn, false);
            }
        });
    }
};

// Real-time form validation
const FormValidation = {
    init: function() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, select, textarea');
            
            inputs.forEach(input => {
                // Validate on blur
                input.addEventListener('blur', Utils.debounce(() => {
                    this.validateInput(input);
                }, 300));
                
                // Clear validation on focus
                input.addEventListener('focus', () => {
                    input.classList.remove('is-valid', 'is-invalid');
                    const feedback = input.parentNode.querySelector('.invalid-feedback, .valid-feedback');
                    if (feedback) feedback.textContent = '';
                });
            });
        });
    },
    
    validateInput: function(input) {
        const validation = Utils.validateField(input, VALIDATION_RULES);
        Utils.setFieldValidation(input, validation.valid, validation.message);
        return validation.valid;
    },
    
    validateForm: function(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        
        inputs.forEach(input => {
            if (!this.validateInput(input)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize form handlers
    FormHandlers.handleOrderForm();
    FormHandlers.handleScheduleForm();
    FormHandlers.handleContactForm();
    
    // Initialize form validation
    FormValidation.init();
    
    // Set minimum date for date inputs (tomorrow)
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const minDate = tomorrow.toISOString().split('T')[0];
    
    dateInputs.forEach(input => {
        input.min = minDate;
    });
    
    // Character counter for textareas
    const textareas = document.querySelectorAll('textarea[maxlength]');
    textareas.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        const counter = document.createElement('small');
        counter.className = 'text-muted float-end';
        textarea.parentNode.appendChild(counter);
        
        const updateCounter = () => {
            const remaining = maxLength - textarea.value.length;
            counter.textContent = `${remaining} characters remaining`;
            counter.className = remaining < 100 ? 'text-warning float-end' : 'text-muted float-end';
        };
        
        textarea.addEventListener('input', updateCounter);
        updateCounter();
    });
    
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add animation classes to elements when they come into view
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);
    
    // Observe elements with animation
    const animatedElements = document.querySelectorAll('.card, .feature-card, .service-card');
    animatedElements.forEach(el => observer.observe(el));
});

// Export for use in other scripts
window.PrintingPlatform = {
    Utils,
    FormHandlers,
    FormValidation,
    VALIDATION_RULES
};