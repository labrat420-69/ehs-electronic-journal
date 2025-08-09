/**
 * EHS Electronic Journal - Enhanced Features
 * Provides Excel export, cross-referencing, and improved UI interactions
 */

class EHSEnhancedFeatures {
    constructor() {
        this.init();
    }

    init() {
        this.setupExportFunctionality();
        this.setupCrossReferences();
        this.setupTableEnhancements();
        this.setupFormValidation();
    }

    /**
     * Set up Excel export functionality
     */
    setupExportFunctionality() {
        const exportBtns = document.querySelectorAll('[id$="-export-btn"], .export-btn');
        exportBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleExport(e.target);
            });
        });
    }

    /**
     * Handle Excel export
     */
    async handleExport(button) {
        try {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Exporting...';

            // Determine export type based on current page
            const currentPath = window.location.pathname;
            let exportType = 'general';
            
            if (currentPath.includes('chemical_inventory')) {
                exportType = 'chemical_inventory';
            } else if (currentPath.includes('reagents')) {
                exportType = 'reagents';
            } else if (currentPath.includes('standards')) {
                exportType = 'standards';
            } else if (currentPath.includes('equipment')) {
                exportType = 'equipment';
            } else if (currentPath.includes('maintenance')) {
                exportType = 'maintenance';
            }

            // Get table data
            const tableData = this.extractTableData();
            
            // Create and download Excel file
            this.downloadAsExcel(tableData, exportType);
            
        } catch (error) {
            console.error('Export failed:', error);
            this.showNotification('Export failed. Please try again.', 'error');
        } finally {
            // Restore button
            setTimeout(() => {
                button.disabled = false;
                button.innerHTML = '<i class="fas fa-download"></i> Export';
            }, 2000);
        }
    }

    /**
     * Extract data from the current table
     */
    extractTableData() {
        const table = document.querySelector('.data-table');
        if (!table) return [];

        const headers = [];
        const headerCells = table.querySelectorAll('thead th');
        headerCells.forEach(th => headers.push(th.textContent.trim()));

        const rows = [];
        const bodyRows = table.querySelectorAll('tbody tr');
        bodyRows.forEach(row => {
            const cells = row.querySelectorAll('td');
            const rowData = [];
            cells.forEach(cell => {
                rowData.push(cell.textContent.trim());
            });
            if (rowData.length > 0) {
                rows.push(rowData);
            }
        });

        return { headers, rows };
    }

    /**
     * Download data as Excel file
     */
    downloadAsExcel(data, type) {
        // Create CSV content (fallback for Excel functionality)
        let csvContent = data.headers.join(',') + '\n';
        data.rows.forEach(row => {
            csvContent += row.map(cell => `"${cell}"`).join(',') + '\n';
        });

        // Create blob and download
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${type}_export_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        this.showNotification('Export completed successfully!', 'success');
    }

    /**
     * Set up cross-referencing links
     */
    setupCrossReferences() {
        // Make chemical names, lot numbers, and EHS IDs clickable
        const tableLinks = document.querySelectorAll('.table-link');
        tableLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.openCrossReference(e.target);
            });
        });

        // Convert existing table cells to links
        this.convertToLinks();
    }

    /**
     * Convert specific table cells to clickable links
     */
    convertToLinks() {
        const tables = document.querySelectorAll('.data-table');
        tables.forEach(table => {
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                
                // Chemical Name (usually first column)
                if (cells[0] && cells[0].textContent.trim()) {
                    this.makeClickable(cells[0], 'chemical_name');
                }

                // Look for Lot Number columns
                const headers = table.querySelectorAll('thead th');
                headers.forEach((header, index) => {
                    const headerText = header.textContent.toLowerCase();
                    if (headerText.includes('lot') && cells[index]) {
                        this.makeClickable(cells[index], 'lot_number');
                    }
                    if (headerText.includes('ehs') && headerText.includes('id') && cells[index]) {
                        this.makeClickable(cells[index], 'ehs_id');
                    }
                });
            });
        });
    }

    /**
     * Make a table cell clickable
     */
    makeClickable(cell, type) {
        const content = cell.textContent.trim();
        if (!content) return;

        const link = document.createElement('a');
        link.href = '#';
        link.className = 'table-link';
        link.textContent = content;
        link.dataset.type = type;
        link.dataset.value = content;

        link.addEventListener('click', (e) => {
            e.preventDefault();
            this.openCrossReference(link);
        });

        cell.innerHTML = '';
        cell.appendChild(link);
    }

    /**
     * Open cross-reference in new tab
     */
    openCrossReference(element) {
        const type = element.dataset.type;
        const value = element.dataset.value;
        
        // Create search URL for cross-referencing
        const searchParams = new URLSearchParams();
        searchParams.set('search', value);
        searchParams.set('type', type);
        
        // Open new tab with search results
        const newTab = window.open(`/search?${searchParams.toString()}`, '_blank');
        
        // Fallback: show notification if search page doesn't exist
        setTimeout(() => {
            if (!newTab || newTab.closed) {
                this.showNotification(`Searching for ${type}: ${value}`, 'info');
            }
        }, 1000);
    }

    /**
     * Set up table enhancements
     */
    setupTableEnhancements() {
        // Add View Details buttons where missing
        this.addViewDetailsButtons();
        
        // Enhance search functionality
        this.enhanceSearch();
    }

    /**
     * Add View Details buttons to tables
     */
    addViewDetailsButtons() {
        const tables = document.querySelectorAll('.data-table');
        tables.forEach(table => {
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const actionCell = row.querySelector('td:last-child');
                if (actionCell && !actionCell.querySelector('.view-details-btn')) {
                    const button = document.createElement('button');
                    button.className = 'view-details-btn';
                    button.innerHTML = '<i class="fas fa-eye"></i> View';
                    button.addEventListener('click', () => {
                        this.showDetails(row);
                    });
                    actionCell.appendChild(button);
                }
            });
        });
    }

    /**
     * Show details modal or page
     */
    showDetails(row) {
        const cells = row.querySelectorAll('td');
        const data = {};
        const headers = document.querySelectorAll('.data-table thead th');
        
        headers.forEach((header, index) => {
            if (cells[index]) {
                data[header.textContent.trim()] = cells[index].textContent.trim();
            }
        });

        // For now, show an alert with details (can be enhanced to modal)
        let details = 'Record Details:\n\n';
        Object.entries(data).forEach(([key, value]) => {
            if (key !== 'Actions') {
                details += `${key}: ${value}\n`;
            }
        });
        
        alert(details);
    }

    /**
     * Enhance search functionality
     */
    enhanceSearch() {
        const searchInputs = document.querySelectorAll('#search-input, .search-input');
        searchInputs.forEach(input => {
            let timeout;
            input.addEventListener('input', (e) => {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    this.performSearch(e.target.value);
                }, 300);
            });
        });
    }

    /**
     * Perform table search
     */
    performSearch(query) {
        const table = document.querySelector('.data-table tbody');
        if (!table) return;

        const rows = table.querySelectorAll('tr');
        const searchTerm = query.toLowerCase();

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(searchTerm) || searchTerm === '') {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    /**
     * Set up form validation
     */
    setupFormValidation() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                }
            });
        });
    }

    /**
     * Validate form fields
     */
    validateForm(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                this.showFieldError(field, 'This field is required');
                isValid = false;
            } else {
                this.clearFieldError(field);
            }
        });

        return isValid;
    }

    /**
     * Show field error
     */
    showFieldError(field, message) {
        field.style.borderColor = 'var(--error-color)';
        
        let errorDiv = field.parentNode.querySelector('.field-error');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'field-error';
            errorDiv.style.color = 'var(--error-color)';
            errorDiv.style.fontSize = '12px';
            errorDiv.style.marginTop = '4px';
            field.parentNode.appendChild(errorDiv);
        }
        errorDiv.textContent = message;
    }

    /**
     * Clear field error
     */
    clearFieldError(field) {
        field.style.borderColor = '';
        const errorDiv = field.parentNode.querySelector('.field-error');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;

        // Set background color based on type
        const colors = {
            success: 'var(--success-color)',
            error: 'var(--error-color)',
            warning: 'var(--warning-color)',
            info: 'var(--info-color)'
        };
        notification.style.background = colors[type] || colors.info;

        notification.textContent = message;
        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Add CSS animations for notifications
const notificationStyle = document.createElement('style');
notificationStyle.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(notificationStyle);

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new EHSEnhancedFeatures();
});