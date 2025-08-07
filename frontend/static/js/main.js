/**
 * Main JavaScript file for EHS Electronic Journal
 * Handles common functionality across all pages
 */

// Global application object
window.EHSJournal = {
    // Configuration
    config: {
        apiBaseUrl: '/api',
        timeZone: 'America/New_York', // EST
        dateFormat: 'MM/DD/YYYY h:mm A'
    },
    
    // Utility functions
    utils: {},
    
    // Components
    components: {},
    
    // State management
    state: {
        user: null,
        sidebarCollapsed: localStorage.getItem('sidebarCollapsed') === 'true',
        theme: localStorage.getItem('theme') || 'light'
    }
};

/**
 * Initialize theme switcher
 */
function initializeThemeSwitcher() {
    // Apply saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);
    
    // Theme toggle event listeners
    document.querySelectorAll('[data-theme]').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const theme = this.getAttribute('data-theme');
            applyTheme(theme);
            localStorage.setItem('theme', theme);
            
            // Close modal if it's open
            const modal = document.querySelector('.modal.show');
            if (modal) {
                const backdrop = bootstrap.Modal.getInstance(modal);
                if (backdrop) backdrop.hide();
            }
        });
    });
}

/**
 * Apply theme to the document
 */
function applyTheme(theme) {
    document.body.setAttribute('data-bs-theme', theme);
    EHSJournal.state.theme = theme;
    
    // Update theme toggle buttons
    document.querySelectorAll('[data-theme]').forEach(button => {
        if (button.getAttribute('data-theme') === theme) {
            button.classList.add('btn-primary');
            button.classList.remove('btn-outline-primary');
        } else {
            button.classList.remove('btn-primary');
            button.classList.add('btn-outline-primary');
        }
    });
}

/**
 * Initialize flash messages handling
 */
function initializeFlashMessages() {
    // Handle flash message close buttons
    document.querySelectorAll('.alert-close').forEach(button => {
        button.addEventListener('click', function() {
            const alert = this.closest('.alert');
            if (alert) {
                alert.style.animation = 'slideUp 0.3s ease-out forwards';
                setTimeout(() => alert.remove(), 300);
            }
        });
    });
    
    // Auto-hide success messages after 5 seconds
    document.querySelectorAll('.alert-success').forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.style.animation = 'slideUp 0.3s ease-out forwards';
                setTimeout(() => alert.remove(), 300);
            }
        }, 5000);
    });
}

/**
 * Initialize URL parameter messages
 */
function initializeUrlMessages() {
    const urlParams = new URLSearchParams(window.location.search);
    const messagesContainer = document.getElementById('url-messages');
    
    if (!messagesContainer) return;
    
    // Success messages
    if (urlParams.get('created') === 'true') {
        showMessage('success', 'Record created successfully!');
    }
    if (urlParams.get('updated') === 'true') {
        showMessage('success', 'Record updated successfully!');
    }
    if (urlParams.get('deleted') === 'true') {
        showMessage('success', 'Record deleted successfully!');
    }
    if (urlParams.get('password_changed') === 'true') {
        showMessage('success', 'Password changed successfully!');
    }
    
    // Clear URL parameters after showing messages
    if (urlParams.toString()) {
        const cleanUrl = window.location.pathname;
        window.history.replaceState({}, document.title, cleanUrl);
    }
}

/**
 * Show a message to the user
 */
function showMessage(type, message) {
    const messagesContainer = document.getElementById('url-messages') || 
                             document.querySelector('.flash-messages') ||
                             document.querySelector('.page-content');
    
    if (!messagesContainer) return;
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        <i class="fas fa-${getIconForMessageType(type)}"></i>
        ${message}
        <button class="alert-close">&times;</button>
    `;
    
    // Insert at the beginning of the container
    messagesContainer.insertBefore(alertDiv, messagesContainer.firstChild);
    
    // Add close event listener
    const closeButton = alertDiv.querySelector('.alert-close');
    if (closeButton) {
        closeButton.addEventListener('click', function() {
            alertDiv.style.animation = 'slideUp 0.3s ease-out forwards';
            setTimeout(() => alertDiv.remove(), 300);
        });
    }
    
    // Auto-hide success messages
    if (type === 'success') {
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.style.animation = 'slideUp 0.3s ease-out forwards';
                setTimeout(() => alertDiv.remove(), 300);
            }
        }, 5000);
    }
}

/**
 * Get icon for message type
 */
function getIconForMessageType(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * API helper functions
 */
EHSJournal.utils.api = {
    /**
     * Make an authenticated API request
     */
    async request(url, options = {}) {
        const token = this.getAuthToken();
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` })
            }
        };
        
        const mergedOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };
        
        try {
            const response = await fetch(url, mergedOptions);
            
            if (response.status === 401) {
                // Unauthorized - redirect to login
                window.location.href = '/auth/login';
                return null;
            }
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                throw new Error(errorData?.detail || `HTTP ${response.status}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return response;
        } catch (error) {
            console.error('API request failed:', error);
            showMessage('error', `Request failed: ${error.message}`);
            throw error;
        }
    },
    
    /**
     * Get authentication token from localStorage
     */
    getAuthToken() {
        return localStorage.getItem('token');
    },
    
    /**
     * GET request
     */
    async get(url) {
        return this.request(url, { method: 'GET' });
    },
    
    /**
     * POST request
     */
    async post(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    /**
     * PUT request
     */
    async put(url, data) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    /**
     * DELETE request
     */
    async delete(url) {
        return this.request(url, { method: 'DELETE' });
    }
};

/**
 * Form validation utilities
 */
EHSJournal.utils.validation = {
    /**
     * Validate email format
     */
    isValidEmail(email) {
        const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return pattern.test(email);
    },
    
    /**
     * Validate phone number
     */
    isValidPhone(phone) {
        const digitsOnly = phone.replace(/\D/g, '');
        return digitsOnly.length === 10;
    },
    
    /**
     * Validate required fields
     */
    validateRequired(formData, requiredFields) {
        const errors = [];
        for (const field of requiredFields) {
            if (!formData[field] || formData[field].trim() === '') {
                errors.push(`${field} is required`);
            }
        }
        return errors;
    },
    
    /**
     * Show field validation error
     */
    showFieldError(fieldName, message) {
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (!field) return;
        
        // Remove existing error
        const existingError = field.parentNode.querySelector('.form-error');
        if (existingError) existingError.remove();
        
        // Add error class to field
        field.classList.add('is-invalid');
        
        // Add error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback form-error';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    },
    
    /**
     * Clear field validation error
     */
    clearFieldError(fieldName) {
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (!field) return;
        
        field.classList.remove('is-invalid');
        const errorDiv = field.parentNode.querySelector('.form-error');
        if (errorDiv) errorDiv.remove();
    },
    
    /**
     * Clear all form errors
     */
    clearFormErrors(form) {
        form.querySelectorAll('.form-control.is-invalid').forEach(field => {
            field.classList.remove('is-invalid');
        });
        form.querySelectorAll('.form-error').forEach(error => {
            error.remove();
        });
    }
};

/**
 * Date and time utilities
 */
EHSJournal.utils.datetime = {
    /**
     * Format date to EST display format (MM/DD/YYYY H:MM AM/PM)
     */
    formatDateEST(date) {
        if (!date) return '';
        
        const d = new Date(date);
        return d.toLocaleString('en-US', {
            timeZone: 'America/New_York',
            month: '2-digit',
            day: '2-digit',
            year: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    },
    
    /**
     * Format date to EST date only (MM/DD/YYYY)
     */
    formatDateOnlyEST(date) {
        if (!date) return '';
        
        const d = new Date(date);
        return d.toLocaleDateString('en-US', {
            timeZone: 'America/New_York',
            month: '2-digit',
            day: '2-digit',
            year: 'numeric'
        });
    },
    
    /**
     * Get current EST time
     */
    getCurrentEST() {
        return new Date().toLocaleString('en-US', {
            timeZone: 'America/New_York',
            month: '2-digit',
            day: '2-digit',
            year: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    }
};

/**
 * Table utilities for Tabler tables
 */
EHSJournal.utils.table = {
    /**
     * Make table sortable
     */
    makeSortable(tableId) {
        const table = document.getElementById(tableId);
        if (!table) return;
        
        const headers = table.querySelectorAll('th[data-sortable]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.innerHTML += ' <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-sm" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><polyline points="6,15 12,9 18,15"/></svg>';
            
            header.addEventListener('click', () => {
                this.sortTable(table, header.cellIndex, header.dataset.type || 'string');
            });
        });
    },
    
    /**
     * Sort table by column
     */
    sortTable(table, columnIndex, dataType) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        rows.sort((a, b) => {
            const aValue = a.cells[columnIndex].textContent.trim();
            const bValue = b.cells[columnIndex].textContent.trim();
            
            if (dataType === 'number') {
                return parseFloat(aValue) - parseFloat(bValue);
            } else if (dataType === 'date') {
                return new Date(aValue) - new Date(bValue);
            } else {
                return aValue.localeCompare(bValue);
            }
        });
        
        // Clear and re-append rows
        tbody.innerHTML = '';
        rows.forEach(row => tbody.appendChild(row));
    }
};

// CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideUp {
        from {
            opacity: 1;
            transform: translateY(0);
            max-height: 100px;
        }
        to {
            opacity: 0;
            transform: translateY(-20px);
            max-height: 0;
            padding: 0;
            margin: 0;
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);