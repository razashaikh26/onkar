// Warehouse Management System - JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Add event listeners for form validation
    setupFormValidation();
    
    // Add event listeners for status changes
    setupStatusChanges();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Setup form validation
function setupFormValidation() {
    // Get all forms with the class 'needs-validation'
    var forms = document.querySelectorAll('.needs-validation');
    
    // Loop over them and prevent submission
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

// Setup status change handlers
function setupStatusChanges() {
    // Handle status change in slot edit modal
    var statusSelects = document.querySelectorAll('select[id^="status"]');
    
    statusSelects.forEach(function(select) {
        select.addEventListener('change', function() {
            var id = select.id.replace('status', '');
            var isFullCheckbox = document.getElementById('isFull' + id);
            
            // If status is set to occupied, automatically check the "is_full" checkbox
            if (select.value === 'occupied') {
                isFullCheckbox.checked = true;
            } else if (select.value === 'available') {
                isFullCheckbox.checked = false;
            }
        });
    });
}

// Function to confirm actions
function confirmAction(message) {
    return confirm(message || 'Are you sure you want to perform this action?');
}

// Function to format dates
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Function to show flash messages
function showFlashMessage(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, 5000);
} 