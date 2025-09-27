// Admin dashboard JavaScript functionality

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Auto-refresh functionality
let autoRefreshInterval;
let autoRefreshEnabled = false;

function toggleAutoRefresh() {
    const button = document.getElementById('autoRefreshBtn');
    
    if (autoRefreshEnabled) {
        clearInterval(autoRefreshInterval);
        autoRefreshEnabled = false;
        button.innerHTML = '<i class="fas fa-play me-1"></i>Auto Refresh';
        button.classList.remove('btn-success');
        button.classList.add('btn-outline-success');
    } else {
        autoRefreshInterval = setInterval(() => {
            location.reload();
        }, 30000); // Refresh every 30 seconds
        autoRefreshEnabled = true;
        button.innerHTML = '<i class="fas fa-pause me-1"></i>Stop Refresh';
        button.classList.remove('btn-outline-success');
        button.classList.add('btn-success');
    }
}

// Notification system
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv && alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Export functions
function exportOrders() {
    showNotification('Exporting orders...', 'info');
    // Implementation would go here
}

function exportProducts() {
    showNotification('Exporting products...', 'info');
    // Implementation would go here
}

// Quick stats update
function updateQuickStats() {
    fetch('/api/admin/stats')
        .then(response => response.json())
        .then(data => {
            // Update stat cards
            document.getElementById('totalOrders').textContent = data.totalOrders;
            document.getElementById('totalRevenue').textContent = '$' + data.totalRevenue.toFixed(2);
            document.getElementById('totalProducts').textContent = data.totalProducts;
            document.getElementById('totalUsers').textContent = data.totalUsers;
            
            showNotification('Stats updated successfully!', 'success');
        })
        .catch(error => {
            console.error('Error updating stats:', error);
            showNotification('Error updating stats', 'danger');
        });
}

// Bulk operations
function selectAllOrders() {
    const checkboxes = document.querySelectorAll('input[name="order_ids"]');
    const selectAllCheckbox = document.getElementById('selectAllOrders');
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
    });
    
    updateBulkActionsVisibility();
}

function updateBulkActionsVisibility() {
    const checkedBoxes = document.querySelectorAll('input[name="order_ids"]:checked');
    const bulkActions = document.getElementById('bulkActions');
    
    if (checkedBoxes.length > 0) {
        bulkActions.style.display = 'block';
        document.getElementById('selectedCount').textContent = checkedBoxes.length;
    } else {
        bulkActions.style.display = 'none';
    }
}

// Bulk status update
function bulkUpdateStatus() {
    const checkedBoxes = document.querySelectorAll('input[name="order_ids"]:checked');
    const newStatus = document.getElementById('bulkStatus').value;
    
    if (checkedBoxes.length === 0) {
        alert('Please select at least one order');
        return;
    }
    
    if (!newStatus) {
        alert('Please select a status');
        return;
    }
    
    const orderIds = Array.from(checkedBoxes).map(cb => cb.value);
    
    if (confirm(`Update ${orderIds.length} orders to ${newStatus}?`)) {
        fetch('/api/admin/bulk-update-status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                order_ids: orderIds,
                status: newStatus
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(`Updated ${data.updated} orders successfully!`, 'success');
                location.reload();
            } else {
                showNotification('Error updating orders: ' + data.error, 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error updating orders', 'danger');
        });
    }
}

// Search functionality
function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    
    if (searchInput && searchButton) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
        
        searchButton.addEventListener('click', performSearch);
    }
}

function performSearch() {
    const searchTerm = document.getElementById('searchInput').value;
    const currentUrl = new URL(window.location);
    
    if (searchTerm.trim()) {
        currentUrl.searchParams.set('search', searchTerm);
    } else {
        currentUrl.searchParams.delete('search');
    }
    
    window.location.href = currentUrl.toString();
}

// Initialize all functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeSearch();
    
    // Add event listeners for order checkboxes
    const orderCheckboxes = document.querySelectorAll('input[name="order_ids"]');
    orderCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateBulkActionsVisibility);
    });
    
    // Add event listener for select all checkbox
    const selectAllCheckbox = document.getElementById('selectAllOrders');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', selectAllOrders);
    }
});

// Real-time updates using WebSocket (if implemented)
function initWebSocket() {
    if (typeof WebSocket !== 'undefined') {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const ws = new WebSocket(`${protocol}//${window.location.host}/ws/admin`);
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            switch(data.type) {
                case 'new_order':
                    showNotification(`New order received: ${data.order_number}`, 'success');
                    updateQuickStats();
                    break;
                    
                case 'payment_received':
                    showNotification(`Payment received for order ${data.order_number}`, 'success');
                    updateQuickStats();
                    break;
                    
                case 'low_stock':
                    showNotification(`Low stock alert: ${data.product_name}`, 'warning');
                    break;
            }
        };
        
        ws.onerror = function(error) {
            console.error('WebSocket error:', error);
        };
    }
}

// Initialize WebSocket connection if supported
// initWebSocket();
