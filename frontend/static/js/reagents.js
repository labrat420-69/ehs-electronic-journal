/**
 * Reagents Management JavaScript
 * EHS Electronic Journal
 */

let reagentsData = [];
let currentReagentType = 'mm';
let currentUser = null;

function initializeReagents(reagentType = 'mm') {
    console.log(`Initializing ${reagentType.toUpperCase()} Reagents...`);
    
    currentReagentType = reagentType.toLowerCase();
    currentUser = window.currentUser || null;
    
    // Initialize event listeners
    initializeSearchAndFilters();
    initializeModals();
    initializeVolumeUpdate();
    initializeDeleteFunctionality();
    
    // Load initial data
    loadReagents();
    
    console.log(`${reagentType.toUpperCase()} Reagents initialized successfully`);
}

function initializeSearchAndFilters() {
    const searchInput = document.getElementById('search-input');
    const clearSearch = document.getElementById('clear-search');
    const statusFilter = document.getElementById('status-filter');
    const dateFilter = document.getElementById('date-filter');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterReagents, 300));
    }
    
    if (clearSearch) {
        clearSearch.addEventListener('click', () => {
            searchInput.value = '';
            filterReagents();
        });
    }
    
    if (statusFilter) {
        statusFilter.addEventListener('change', filterReagents);
    }
    
    if (dateFilter) {
        dateFilter.addEventListener('change', filterReagents);
    }
}

function initializeModals() {
    // Volume update modal
    const volumeModal = document.getElementById('volume-update-modal');
    const volumeModalClose = volumeModal?.querySelector('.modal-close');
    const volumeModalCancel = document.getElementById('modal-cancel');
    
    if (volumeModalClose) {
        volumeModalClose.addEventListener('click', () => hideModal('volume-update-modal'));
    }
    
    if (volumeModalCancel) {
        volumeModalCancel.addEventListener('click', () => hideModal('volume-update-modal'));
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

function initializeVolumeUpdate() {
    // Volume update buttons
    document.addEventListener('click', (e) => {
        if (e.target.closest('.volume-update-btn')) {
            e.preventDefault();
            const btn = e.target.closest('.volume-update-btn');
            openVolumeUpdateModal(btn);
        }
    });
    
    // Volume update form
    const volumeChange = document.getElementById('volume-change');
    const currentVolumeSpan = document.getElementById('modal-current-volume');
    const previewDiv = document.getElementById('new-volume-preview');
    const previewSpan = document.getElementById('preview-volume');
    
    if (volumeChange) {
        volumeChange.addEventListener('input', () => {
            const currentVolume = parseFloat(currentVolumeSpan?.textContent?.replace(/[^\d.]/g, '') || 0);
            const change = parseFloat(volumeChange.value || 0);
            const newVolume = currentVolume + change;
            
            if (volumeChange.value && !isNaN(change)) {
                previewSpan.textContent = newVolume.toFixed(1);
                previewDiv.style.display = 'block';
                
                // Color coding
                if (newVolume < 0) {
                    previewDiv.className = 'alert alert-danger';
                    previewSpan.parentNode.innerHTML = `<strong>Warning: </strong>Insufficient volume! New: <span style="color: #ea4335">${newVolume.toFixed(1)}</span> mL`;
                } else if (newVolume === 0) {
                    previewDiv.className = 'alert alert-warning';
                    previewSpan.parentNode.innerHTML = `<strong>New Volume: </strong><span style="color: #fbbc04">${newVolume.toFixed(1)}</span> mL (Empty)`;
                } else if (newVolume < 50) {
                    previewDiv.className = 'alert alert-warning';
                    previewSpan.parentNode.innerHTML = `<strong>New Volume: </strong><span style="color: #fbbc04">${newVolume.toFixed(1)}</span> mL (Low)`;
                } else {
                    previewDiv.className = 'alert alert-info';
                    previewSpan.parentNode.innerHTML = `<strong>New Volume: </strong><span>${newVolume.toFixed(1)}</span> mL`;
                }
            } else {
                previewDiv.style.display = 'none';
            }
        });
    }
    
    // Submit volume update
    const submitBtn = document.getElementById('modal-submit');
    if (submitBtn) {
        submitBtn.addEventListener('click', submitVolumeUpdate);
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

function openVolumeUpdateModal(btn) {
    const reagentId = btn.dataset.reagentId;
    const reagentName = btn.dataset.reagentName;
    const currentVolume = parseFloat(btn.dataset.currentVolume || 0);
    const reagentType = btn.dataset.reagentType || currentReagentType;
    
    document.getElementById('modal-reagent-name').textContent = reagentName;
    document.getElementById('modal-current-volume').textContent = `${currentVolume.toFixed(1)} mL`;
    
    // Store data for submission
    const modal = document.getElementById('volume-update-modal');
    modal.dataset.reagentId = reagentId;
    modal.dataset.reagentType = reagentType;
    modal.dataset.currentVolume = currentVolume;
    
    // Reset form
    document.getElementById('volume-update-form').reset();
    document.getElementById('new-volume-preview').style.display = 'none';
    
    showModal('volume-update-modal');
}

function openDeleteModal(btn) {
    const reagentId = btn.dataset.reagentId;
    const reagentName = btn.dataset.reagentName;
    const reagentType = btn.dataset.reagentType || currentReagentType;
    
    document.getElementById('delete-reagent-name').textContent = reagentName;
    
    const modal = document.getElementById('delete-modal');
    modal.dataset.reagentId = reagentId;
    modal.dataset.reagentType = reagentType;
    
    showModal('delete-modal');
}

async function submitVolumeUpdate() {
    const modal = document.getElementById('volume-update-modal');
    const reagentId = modal.dataset.reagentId;
    const reagentType = modal.dataset.reagentType;
    const volumeChange = parseFloat(document.getElementById('volume-change').value);
    const reason = document.getElementById('change-reason').value;
    const notes = document.getElementById('change-notes').value;
    
    if (!volumeChange || volumeChange === 0) {
        showAlert('Please enter a valid volume change', 'danger');
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
        const response = await fetch(`/reagents/${reagentType}/api/${reagentId}/volume`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getAuthToken()}`
            },
            body: JSON.stringify({
                volume_change: volumeChange,
                reason: reason,
                notes: notes || null
            })
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showAlert(result.message, 'success');
            hideModal('volume-update-modal');
            loadReagents(); // Reload data
        } else {
            showAlert(result.detail || 'Failed to update volume', 'danger');
        }
    } catch (error) {
        console.error('Error updating volume:', error);
        showAlert('Network error. Please try again.', 'danger');
    } finally {
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
    }
}

async function confirmDelete() {
    const modal = document.getElementById('delete-modal');
    const reagentId = modal.dataset.reagentId;
    const reagentType = modal.dataset.reagentType;
    
    const deleteBtn = document.getElementById('delete-confirm');
    deleteBtn.classList.add('loading');
    deleteBtn.disabled = true;
    
    try {
        const response = await fetch(`/reagents/${reagentType}/api/${reagentId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showAlert(result.message, 'success');
            hideModal('delete-modal');
            loadReagents(); // Reload data
        } else {
            showAlert(result.detail || 'Failed to deactivate reagent', 'danger');
        }
    } catch (error) {
        console.error('Error deleting reagent:', error);
        showAlert('Network error. Please try again.', 'danger');
    } finally {
        deleteBtn.classList.remove('loading');
        deleteBtn.disabled = false;
    }
}

async function loadReagents() {
    try {
        const statusFilter = document.getElementById('status-filter');
        const activeOnly = !statusFilter || statusFilter.value !== 'all';
        
        const response = await fetch(`/reagents/${currentReagentType}/api/?active_only=${activeOnly}`, {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });
        
        if (response.ok) {
            reagentsData = await response.json();
            updateReagentsTable();
        } else if (response.status === 401) {
            showAlert('Please log in to access reagents data', 'warning');
        } else {
            console.error('Failed to load reagents data');
            showAlert('Failed to load reagents data', 'danger');
        }
    } catch (error) {
        console.error('Error loading reagents:', error);
        showAlert('Network error loading reagents', 'danger');
    }
}

function filterReagents() {
    const searchTerm = document.getElementById('search-input')?.value.toLowerCase() || '';
    const statusFilter = document.getElementById('status-filter')?.value || 'active';
    const dateFilter = document.getElementById('date-filter')?.value || '';
    
    let filteredData = reagentsData.filter(reagent => {
        // Search filter
        const matchesSearch = !searchTerm || 
            reagent.reagent_name.toLowerCase().includes(searchTerm) ||
            reagent.batch_number.toLowerCase().includes(searchTerm);
        
        // Status filter
        let matchesStatus = true;
        if (statusFilter === 'active') {
            matchesStatus = reagent.is_active;
        } else if (statusFilter === 'inactive') {
            matchesStatus = !reagent.is_active;
        }
        
        // Date filter
        let matchesDate = true;
        if (dateFilter && reagent.preparation_date) {
            const prepDate = new Date(reagent.preparation_date);
            const today = new Date();
            
            switch (dateFilter) {
                case 'today':
                    matchesDate = prepDate.toDateString() === today.toDateString();
                    break;
                case 'week':
                    const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
                    matchesDate = prepDate >= weekAgo;
                    break;
                case 'month':
                    matchesDate = prepDate.getMonth() === today.getMonth() && 
                                prepDate.getFullYear() === today.getFullYear();
                    break;
                case 'quarter':
                    const currentQuarter = Math.floor(today.getMonth() / 3);
                    const prepQuarter = Math.floor(prepDate.getMonth() / 3);
                    matchesDate = prepQuarter === currentQuarter && 
                                prepDate.getFullYear() === today.getFullYear();
                    break;
            }
        }
        
        return matchesSearch && matchesStatus && matchesDate;
    });
    
    updateReagentsTable(filteredData);
}

function updateReagentsTable(data = reagentsData) {
    const tbody = document.getElementById('reagents-tbody');
    if (!tbody) return;
    
    if (data.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="12" class="text-center">
                    <div class="empty-state">
                        <i class="fas fa-vial"></i>
                        <h3>No ${currentReagentType.toUpperCase()} reagents found</h3>
                        <p>Try adjusting your search or filters.</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = data.map(reagent => createReagentRow(reagent)).join('');
    
    // Update expiration warnings
    updateExpirationWarnings();
}

function createReagentRow(reagent) {
    const today = new Date();
    const expirationDate = reagent.expiration_date ? new Date(reagent.expiration_date) : null;
    const preparationDate = reagent.preparation_date ? new Date(reagent.preparation_date) : null;
    const daysToExpiry = expirationDate ? Math.floor((expirationDate - today) / (1000 * 60 * 60 * 24)) : null;
    
    let expirationHtml = 'N/A';
    if (expirationDate) {
        const dateStr = expirationDate.toLocaleDateString();
        let badge = '';
        
        if (daysToExpiry < 0) {
            badge = '<span class="badge badge-danger">Expired</span>';
        } else if (daysToExpiry < 7) {
            badge = '<span class="badge badge-warning">Expires Soon</span>';
        }
        
        expirationHtml = `<span class="expiry-date">${dateStr}</span>${badge}`;
    }
    
    const volumeBadge = getVolumeBadge(reagent.total_volume || 0);
    const canEdit = currentUser && ['admin', 'manager', 'lab_tech'].includes(currentUser.role);
    const canDelete = currentUser && ['admin', 'manager'].includes(currentUser.role);
    
    // Type-specific columns
    let typeSpecificColumns = '';
    if (currentReagentType === 'mm') {
        typeSpecificColumns = `
            <td>${reagent.ph_value ? reagent.ph_value.toFixed(2) : 'N/A'}</td>
            <td>${reagent.conductivity ? reagent.conductivity.toFixed(1) + ' μS/cm' : 'N/A'}</td>
        `;
    } else if (currentReagentType === 'pb') {
        typeSpecificColumns = `
            <td>${reagent.lead_concentration ? reagent.lead_concentration.toFixed(3) + ' mg/L' : 'N/A'}</td>
        `;
    } else if (currentReagentType === 'tclp') {
        const phDisplay = reagent.ph_target && reagent.final_ph 
            ? `${reagent.ph_target.toFixed(2)} / ${reagent.final_ph.toFixed(2)}`
            : reagent.ph_target 
            ? `${reagent.ph_target.toFixed(2)} / -`
            : 'N/A';
        
        typeSpecificColumns = `
            <td>${reagent.reagent_type || 'N/A'}</td>
            <td>${phDisplay}</td>
            <td>
                ${reagent.verification_passed 
                    ? '<span class="badge badge-success">✓ Verified</span>'
                    : '<span class="badge badge-secondary">Pending</span>'
                }
            </td>
        `;
    }
    
    return `
        <tr data-reagent-id="${reagent.id}" class="${!reagent.is_active ? 'inactive' : ''}">
            <td>
                <div class="reagent-info">
                    <strong>${reagent.reagent_name}</strong>
                    ${reagent.concentration ? `<small class="text-muted">${reagent.concentration}</small>` : ''}
                </div>
            </td>
            <td><code>${reagent.batch_number}</code></td>
            <td>${preparationDate ? preparationDate.toLocaleDateString() : 'N/A'}</td>
            <td>${expirationHtml}</td>
            <td>
                <div class="volume-info">
                    <span class="volume-value">${(reagent.total_volume || 0).toFixed(1)} mL</span>
                    ${volumeBadge}
                </div>
            </td>
            ${typeSpecificColumns}
            <td>${reagent.preparer_name || 'N/A'}</td>
            <td>
                <span class="badge ${reagent.is_active ? 'badge-success' : 'badge-secondary'}">
                    ${reagent.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>
                <div class="action-buttons">
                    <a href="/reagents/${currentReagentType}/${reagent.id}" class="btn btn-sm btn-outline" title="View Details">
                        <i class="fas fa-eye"></i>
                    </a>
                    ${canEdit ? `
                        <a href="/reagents/${currentReagentType}/edit/${reagent.id}" class="btn btn-sm btn-secondary" title="Edit">
                            <i class="fas fa-edit"></i>
                        </a>
                        <button class="btn btn-sm btn-primary volume-update-btn" 
                                data-reagent-id="${reagent.id}" 
                                data-reagent-name="${reagent.reagent_name}"
                                data-current-volume="${reagent.total_volume || 0}"
                                data-reagent-type="${currentReagentType}"
                                title="Update Volume">
                            <i class="fas fa-flask"></i>
                        </button>
                    ` : ''}
                    ${canDelete ? `
                        <button class="btn btn-sm btn-danger delete-btn" 
                                data-reagent-id="${reagent.id}" 
                                data-reagent-name="${reagent.reagent_name}"
                                data-reagent-type="${currentReagentType}"
                                title="Deactivate">
                            <i class="fas fa-trash"></i>
                        </button>
                    ` : ''}
                </div>
            </td>
        </tr>
    `;
}

function getVolumeBadge(volume) {
    if (volume <= 0) {
        return '<span class="badge badge-danger">Empty</span>';
    } else if (volume < 50) {
        return '<span class="badge badge-warning">Low</span>';
    }
    return '';
}

function updateExpirationWarnings() {
    const expiryDates = document.querySelectorAll('.expiry-date');
    const today = new Date();
    
    expiryDates.forEach(elem => {
        const expiryDate = new Date(elem.dataset.expiry || elem.textContent);
        const daysUntil = Math.floor((expiryDate - today) / (1000 * 60 * 60 * 24));
        
        if (daysUntil < 0) {
            elem.style.color = '#ea4335';
            elem.style.fontWeight = 'bold';
        } else if (daysUntil < 7) {
            elem.style.color = '#fbbc04';
            elem.style.fontWeight = 'bold';
        }
    });
}

// Utility functions (shared with chemical_inventory.js)
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
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());
    
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
    // For now, return empty string as auth is handled by the server session
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
window.reagents = {
    initialize: initializeReagents,
    loadData: loadReagents,
    filterData: filterReagents
};