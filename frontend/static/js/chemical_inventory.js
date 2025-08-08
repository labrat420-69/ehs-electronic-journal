/**
 * Chemical Inventory Management JavaScript
 * EHS Electronic Journal
 */

let chemicalInventoryData = [];
let currentUser = null;

function initializeChemicalInventory() {
    console.log('Initializing Chemical Inventory...');
    
    // Get current user info from template
    currentUser = window.currentUser || null;
    
    // Initialize event listeners
    initializeSearchAndFilters();
    initializeModals();
    initializeQuantityUpdate();
    initializeDeleteFunctionality();
    
    // Load initial data
    loadChemicalInventory();
    
    console.log('Chemical Inventory initialized successfully');
}

function initializeSearchAndFilters() {
    const searchInput = document.getElementById('search-input');
    const clearSearch = document.getElementById('clear-search');
    const hazardFilter = document.getElementById('hazard-filter');
    const statusFilter = document.getElementById('status-filter');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterChemicals, 300));
    }
    
    if (clearSearch) {
        clearSearch.addEventListener('click', () => {
            searchInput.value = '';
            filterChemicals();
        });
    }
    
    if (hazardFilter) {
        hazardFilter.addEventListener('change', filterChemicals);
    }
    
    if (statusFilter) {
        statusFilter.addEventListener('change', filterChemicals);
    }
}

function initializeModals() {
    // Quantity update modal
    const quantityModal = document.getElementById('quantity-update-modal');
    const quantityModalClose = quantityModal?.querySelector('.modal-close');
    const quantityModalCancel = document.getElementById('modal-cancel');
    
    if (quantityModalClose) {
        quantityModalClose.addEventListener('click', () => hideModal('quantity-update-modal'));
    }
    
    if (quantityModalCancel) {
        quantityModalCancel.addEventListener('click', () => hideModal('quantity-update-modal'));
    }
    
    // Delete modal
    const deleteModal = document.getElementById('delete-modal');
    const deleteModalClose = deleteModal?.querySelector('.modal-close');
    const deleteCancel = document.getElementById('delete-cancel');
    
    if (deleteModalClose) {
        deleteModalClose.addEventListener('click', () => hideModal('delete-modal'));
    }
    
    if (deleteCancel) {
        deleteCancel.addEventListener('click', () => hideModal('delete-modal'));
    }
    
    // Click outside to close
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.classList.remove('show');
        }
    });
}

function initializeQuantityUpdate() {
    // Quantity update buttons
    document.addEventListener('click', (e) => {
        if (e.target.closest('.quantity-update-btn')) {
            e.preventDefault();
            const btn = e.target.closest('.quantity-update-btn');
            openQuantityUpdateModal(btn);
        }
    });
    
    // Quantity update form
    const quantityChange = document.getElementById('quantity-change');
    const currentVolumeSpan = document.getElementById('modal-current-volume');
    const previewDiv = document.getElementById('new-quantity-preview');
    const previewSpan = document.getElementById('preview-quantity');
    
    if (quantityChange) {
        quantityChange.addEventListener('input', () => {
            const currentVolume = parseFloat(currentVolumeSpan?.textContent?.replace(/[^\d.]/g, '') || 0);
            const change = parseFloat(quantityChange.value || 0);
            const newVolume = currentVolume + change;
            
            if (quantityChange.value && !isNaN(change)) {
                previewSpan.textContent = newVolume.toFixed(3);
                previewDiv.style.display = 'block';
                
                // Color coding
                if (newVolume < 0) {
                    previewDiv.className = 'alert alert-danger';
                    previewSpan.parentNode.innerHTML = `<strong>Warning: </strong>Insufficient quantity! New: <span style="color: #ea4335">${newVolume.toFixed(3)}</span>`;
                } else if (newVolume === 0) {
                    previewDiv.className = 'alert alert-warning';
                    previewSpan.parentNode.innerHTML = `<strong>New Quantity: </strong><span style="color: #fbbc04">${newVolume.toFixed(3)}</span> (Empty)`;
                } else {
                    previewDiv.className = 'alert alert-info';
                    previewSpan.parentNode.innerHTML = `<strong>New Quantity: </strong><span>${newVolume.toFixed(3)}</span>`;
                }
            } else {
                previewDiv.style.display = 'none';
            }
        });
    }
    
    // Submit quantity update
    const submitBtn = document.getElementById('modal-submit');
    if (submitBtn) {
        submitBtn.addEventListener('click', submitQuantityUpdate);
    }
}

function initializeDeleteFunctionality() {
    document.addEventListener('click', (e) => {
        if (e.target.closest('.delete-btn')) {
            e.preventDefault();
            const btn = e.target.closest('.delete-btn');
            openDeleteModal(btn);
        }
    });
    
    const deleteConfirm = document.getElementById('delete-confirm');
    if (deleteConfirm) {
        deleteConfirm.addEventListener('click', confirmDelete);
    }
}

function openQuantityUpdateModal(btn) {
    const chemicalId = btn.dataset.chemicalId;
    const chemicalName = btn.dataset.chemicalName;
    const currentQuantity = parseFloat(btn.dataset.currentQuantity || 0);
    const unit = btn.dataset.unit || '';
    
    document.getElementById('modal-chemical-name').textContent = chemicalName;
    document.getElementById('modal-current-quantity').textContent = `${currentQuantity.toFixed(3)} ${unit}`;
    document.getElementById('modal-unit').textContent = unit;
    
    // Store data for submission
    const modal = document.getElementById('quantity-update-modal');
    modal.dataset.chemicalId = chemicalId;
    modal.dataset.currentQuantity = currentQuantity;
    
    // Reset form
    document.getElementById('quantity-update-form').reset();
    document.getElementById('new-quantity-preview').style.display = 'none';
    
    showModal('quantity-update-modal');
}

function openDeleteModal(btn) {
    const chemicalId = btn.dataset.chemicalId;
    const chemicalName = btn.dataset.chemicalName;
    
    document.getElementById('delete-chemical-name').textContent = chemicalName;
    
    const modal = document.getElementById('delete-modal');
    modal.dataset.chemicalId = chemicalId;
    
    showModal('delete-modal');
}

async function submitQuantityUpdate() {
    const modal = document.getElementById('quantity-update-modal');
    const chemicalId = modal.dataset.chemicalId;
    const quantityChange = parseFloat(document.getElementById('quantity-change').value);
    const reason = document.getElementById('change-reason').value;
    const notes = document.getElementById('change-notes').value;
    
    if (!quantityChange || quantityChange === 0) {
        showAlert('Please enter a valid quantity change', 'danger');
        return;
    }
    
    if (!reason) {
        showAlert('Please select a reason for the change', 'danger');
        return;
    }
    
    const submitBtn = document.getElementById('modal-submit');
    submitBtn.classList.add('loading');
    submitBtn.disabled = true;
    
    try {
        const response = await fetch(`/chemical_inventory/api/${chemicalId}/quantity`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getAuthToken()}`
            },
            body: JSON.stringify({
                quantity_change: quantityChange,
                reason: reason,
                notes: notes || null
            })
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showAlert(result.message, 'success');
            hideModal('quantity-update-modal');
            loadChemicalInventory(); // Reload data
        } else {
            showAlert(result.detail || 'Failed to update quantity', 'danger');
        }
    } catch (error) {
        console.error('Error updating quantity:', error);
        showAlert('Network error. Please try again.', 'danger');
    } finally {
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
    }
}

async function confirmDelete() {
    const modal = document.getElementById('delete-modal');
    const chemicalId = modal.dataset.chemicalId;
    
    const deleteBtn = document.getElementById('delete-confirm');
    deleteBtn.classList.add('loading');
    deleteBtn.disabled = true;
    
    try {
        const response = await fetch(`/chemical_inventory/api/${chemicalId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showAlert(result.message, 'success');
            hideModal('delete-modal');
            loadChemicalInventory(); // Reload data
        } else {
            showAlert(result.detail || 'Failed to deactivate chemical', 'danger');
        }
    } catch (error) {
        console.error('Error deleting chemical:', error);
        showAlert('Network error. Please try again.', 'danger');
    } finally {
        deleteBtn.classList.remove('loading');
        deleteBtn.disabled = false;
    }
}

async function loadChemicalInventory() {
    try {
        const statusFilter = document.getElementById('status-filter');
        const activeOnly = !statusFilter || statusFilter.value !== 'all';
        
        const response = await fetch(`/chemical_inventory/api/?active_only=${activeOnly}`, {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });
        
        if (response.ok) {
            chemicalInventoryData = await response.json();
            updateChemicalTable();
        } else {
            console.error('Failed to load chemical inventory');
        }
    } catch (error) {
        console.error('Error loading chemical inventory:', error);
    }
}

function filterChemicals() {
    const searchTerm = document.getElementById('search-input')?.value.toLowerCase() || '';
    const hazardFilter = document.getElementById('hazard-filter')?.value || '';
    const statusFilter = document.getElementById('status-filter')?.value || 'active';
    
    let filteredData = chemicalInventoryData.filter(chemical => {
        // Search filter
        const matchesSearch = !searchTerm || 
            chemical.chemical_name.toLowerCase().includes(searchTerm) ||
            (chemical.cas_number && chemical.cas_number.toLowerCase().includes(searchTerm)) ||
            (chemical.manufacturer && chemical.manufacturer.toLowerCase().includes(searchTerm));
        
        // Hazard filter
        const matchesHazard = !hazardFilter || chemical.hazard_class === hazardFilter;
        
        // Status filter
        let matchesStatus = true;
        if (statusFilter === 'active') {
            matchesStatus = chemical.is_active;
        } else if (statusFilter === 'inactive') {
            matchesStatus = !chemical.is_active;
        }
        
        return matchesSearch && matchesHazard && matchesStatus;
    });
    
    updateChemicalTable(filteredData);
}

function updateChemicalTable(data = chemicalInventoryData) {
    const tbody = document.getElementById('chemicals-tbody');
    if (!tbody) return;
    
    if (data.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center">
                    <div class="empty-state">
                        <i class="fas fa-flask"></i>
                        <h3>No chemicals found</h3>
                        <p>Try adjusting your search or filters.</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = data.map(chemical => createChemicalRow(chemical)).join('');
    
    // Update expiration warnings
    updateExpirationWarnings();
}

function createChemicalRow(chemical) {
    const today = new Date();
    const expirationDate = chemical.expiration_date ? new Date(chemical.expiration_date) : null;
    const daysToExpiry = expirationDate ? Math.floor((expirationDate - today) / (1000 * 60 * 60 * 24)) : null;
    
    let expirationHtml = 'N/A';
    if (expirationDate) {
        const dateStr = expirationDate.toLocaleDateString();
        let badge = '';
        
        if (daysToExpiry < 0) {
            badge = '<span class="badge badge-danger">Expired</span>';
        } else if (daysToExpiry < 30) {
            badge = '<span class="badge badge-warning">Expires Soon</span>';
        }
        
        expirationHtml = `<span class="expiry-date">${dateStr}</span>${badge}`;
    }
    
    const quantityBadge = getQuantityBadge(chemical.current_quantity);
    const hazardBadge = chemical.is_hazardous ? '<span class="badge badge-warning" title="Hazardous Chemical"><i class="fas fa-exclamation-triangle"></i></span>' : '';
    const hazardClassBadge = chemical.hazard_class ? `<span class="badge badge-secondary">${chemical.hazard_class}</span>` : '';
    
    const canEdit = currentUser && ['admin', 'manager', 'lab_tech'].includes(currentUser.role);
    const canDelete = currentUser && ['admin', 'manager'].includes(currentUser.role);
    
    return `
        <tr data-chemical-id="${chemical.id}" class="${!chemical.is_active ? 'inactive' : ''}">
            <td>
                <div class="chemical-info">
                    <strong>${chemical.chemical_name}</strong>
                    ${hazardBadge}
                    ${hazardClassBadge}
                </div>
            </td>
            <td>${chemical.cas_number || 'N/A'}</td>
            <td>${chemical.manufacturer || 'N/A'}</td>
            <td>${chemical.lot_number || 'N/A'}</td>
            <td>
                <div class="quantity-info">
                    <span class="quantity-value">${chemical.current_quantity.toFixed(3)} ${chemical.unit}</span>
                    ${quantityBadge}
                </div>
            </td>
            <td>${chemical.storage_location || 'N/A'}</td>
            <td>${expirationHtml}</td>
            <td>
                <span class="badge ${chemical.is_active ? 'badge-success' : 'badge-secondary'}">
                    ${chemical.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>
                <div class="action-buttons">
                    <a href="/chemical_inventory/${chemical.id}" class="btn btn-sm btn-outline" title="View Details">
                        <i class="fas fa-eye"></i>
                    </a>
                    ${canEdit ? `
                        <a href="/chemical_inventory/edit/${chemical.id}" class="btn btn-sm btn-secondary" title="Edit">
                            <i class="fas fa-edit"></i>
                        </a>
                        <button class="btn btn-sm btn-primary quantity-update-btn" 
                                data-chemical-id="${chemical.id}" 
                                data-chemical-name="${chemical.chemical_name}"
                                data-current-quantity="${chemical.current_quantity}"
                                data-unit="${chemical.unit}"
                                title="Update Quantity">
                            <i class="fas fa-balance-scale"></i>
                        </button>
                    ` : ''}
                    ${canDelete ? `
                        <button class="btn btn-sm btn-danger delete-btn" 
                                data-chemical-id="${chemical.id}" 
                                data-chemical-name="${chemical.chemical_name}"
                                title="Deactivate">
                            <i class="fas fa-trash"></i>
                        </button>
                    ` : ''}
                </div>
            </td>
        </tr>
    `;
}

function getQuantityBadge(quantity) {
    if (quantity <= 0) {
        return '<span class="badge badge-danger">Empty</span>';
    } else if (quantity < 10) {
        return '<span class="badge badge-warning">Low</span>';
    }
    return '';
}

function updateExpirationWarnings() {
    const expiryDates = document.querySelectorAll('.expiry-date');
    const today = new Date();
    
    expiryDates.forEach(elem => {
        const expiryDate = new Date(elem.dataset.expiry);
        const daysUntil = Math.floor((expiryDate - today) / (1000 * 60 * 60 * 24));
        
        if (daysUntil < 0) {
            elem.style.color = '#ea4335';
            elem.style.fontWeight = 'bold';
        } else if (daysUntil < 30) {
            elem.style.color = '#fbbc04';
            elem.style.fontWeight = 'bold';
        }
    });
}

// Utility functions
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
        modal.style.display = 'flex';
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.style.display = 'none';
        }, 200);
    }
}

function showAlert(message, type = 'info') {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <strong>${type === 'success' ? 'Success!' : type === 'danger' ? 'Error!' : 'Info!'}</strong> ${message}
        <button class="alert-close" style="float: right; background: none; border: none; font-size: 18px; cursor: pointer;">&times;</button>
    `;
    
    // Add to page
    const container = document.querySelector('.page-content') || document.body;
    container.insertBefore(alert, container.firstChild);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
    
    // Add close functionality
    alert.querySelector('.alert-close').addEventListener('click', () => {
        alert.remove();
    });
    
    // Scroll to top to show alert
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function getAuthToken() {
    // This would normally get the JWT token from localStorage or cookies
    // For now, return empty string as auth is handled by the server
    return localStorage.getItem('authToken') || '';
}

function debounce(func, wait) {
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

// Export for use in other modules
window.chemicalInventory = {
    initialize: initializeChemicalInventory,
    loadData: loadChemicalInventory,
    filterData: filterChemicals
};