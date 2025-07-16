/**
 * PrintHub JavaScript Functions - Vereinfacht
 * Nur Add und Delete Funktionen
 */

console.log("PrintHub JS loaded - Simple Version");

// Global Variables
let deleteModal;

/**
 * Initialize PrintHub Functions
 */
document.addEventListener("DOMContentLoaded", function () {
  console.log("PrintHub DOM loaded");

  // Initialize Bootstrap Modal
  const deleteModalElement = document.getElementById("deleteModal");
  if (deleteModalElement) {
    deleteModal = new bootstrap.Modal(deleteModalElement);
  }

  // Initialize Event Listeners
  initializeEventListeners();
  initializeFormHandlers();
});

/**
 * Initialize All Event Listeners
 */
function initializeEventListeners() {
  // Reset Form Button
  const resetBtn = document.getElementById("resetFormBtn");
  if (resetBtn) {
    resetBtn.addEventListener("click", function () {
      const form = document.getElementById("filamentForm");
      if (form) {
        form.reset();
        // Reset any validation classes
        const inputs = form.querySelectorAll(".is-invalid");
        inputs.forEach((input) => input.classList.remove("is-invalid"));
      }
    });
  }

  // Delete Buttons
  document.addEventListener("click", function (e) {
    const deleteBtn = e.target.closest('[data-action="delete"]');
    if (!deleteBtn) return;

    e.preventDefault();

    const filamentId = deleteBtn.getAttribute("data-filament-id");
    const filamentName = deleteBtn.getAttribute("data-filament-name");

    console.log("Delete clicked:", filamentId, filamentName);
    showDeleteModal(filamentId, filamentName);
  });
}

/**
 * Initialize Form Handlers
 */
function initializeFormHandlers() {
  const filamentForm = document.getElementById("filamentForm");
  if (!filamentForm) return;

  // Live Price Calculation
  const weightInput = document.getElementById("filament_weight");
  const priceInput = document.getElementById("filament_price");

  if (weightInput && priceInput) {
    weightInput.addEventListener("input", updatePricePerKg);
    priceInput.addEventListener("input", updatePricePerKg);
  }

  // Form Validation
  filamentForm.addEventListener("submit", validateForm);

  // Remove validation classes on input
  const inputs = filamentForm.querySelectorAll("input, select, textarea");
  inputs.forEach((input) => {
    input.addEventListener("input", function () {
      this.classList.remove("is-invalid");
    });
  });
}

/**
 * Show Delete Confirmation Modal
 */
function showDeleteModal(filamentId, filamentName) {
  console.log("Showing delete modal for:", filamentId, filamentName);

  if (!deleteModal) {
    console.error("Delete modal not found");
    return;
  }

  const deleteNameSpan = document.getElementById("deleteFilamentName");
  const deleteForm = document.getElementById("deleteForm");

  if (deleteNameSpan) {
    deleteNameSpan.textContent = filamentName;
  }

  if (deleteForm) {
    deleteForm.action = `/printhub/filament/delete_filament/${filamentId}`;
  }

  deleteModal.show();
}

/**
 * Update Price Per KG Calculation
 */
function updatePricePerKg() {
  const weightInput = document.getElementById("filament_weight");
  const priceInput = document.getElementById("filament_price");

  if (!weightInput || !priceInput) return;

  const weight = parseFloat(weightInput.value) || 0;
  const price = parseFloat(priceInput.value) || 0;

  if (weight > 0 && price > 0) {
    const pricePerKg = ((price / weight) * 1000).toFixed(2);

    // Update tooltip
    priceInput.title = `Preis pro kg: CHF ${pricePerKg}`;

    // Show visual feedback
    priceInput.style.borderColor = "var(--prusa-orange)";
    weightInput.style.borderColor = "var(--prusa-orange)";
  } else {
    priceInput.title = "";
    priceInput.style.borderColor = "";
    weightInput.style.borderColor = "";
  }
}

/**
 * Validate Form
 */
function validateForm(e) {
  const form = e.target;
  const requiredFields = [
    "filament_type",
    "filament_name",
    "filament_manufacturer",
    "filament_weight",
    "filament_price",
  ];
  let isValid = true;
  let firstInvalidField = null;

  // Check required fields
  requiredFields.forEach((fieldName) => {
    const field = document.getElementById(fieldName);
    if (!field || !field.value.trim()) {
      if (field) {
        field.classList.add("is-invalid");
        if (!firstInvalidField) firstInvalidField = field;
      }
      isValid = false;
    } else {
      if (field) field.classList.remove("is-invalid");
    }
  });

  // Validate weight and price are positive numbers
  const weightField = document.getElementById("filament_weight");
  const priceField = document.getElementById("filament_price");

  if (weightField) {
    const weight = parseFloat(weightField.value);
    if (isNaN(weight) || weight <= 0) {
      weightField.classList.add("is-invalid");
      if (!firstInvalidField) firstInvalidField = weightField;
      isValid = false;
    } else {
      weightField.classList.remove("is-invalid");
    }
  }

  if (priceField) {
    const price = parseFloat(priceField.value);
    if (isNaN(price) || price <= 0) {
      priceField.classList.add("is-invalid");
      if (!firstInvalidField) firstInvalidField = priceField;
      isValid = false;
    } else {
      priceField.classList.remove("is-invalid");
    }
  }

  if (!isValid) {
    e.preventDefault();

    // Focus first invalid field
    if (firstInvalidField) {
      firstInvalidField.focus();
    }

    // Show error message
    showFormError("Bitte füllen Sie alle Pflichtfelder korrekt aus!");
  }
}

/**
 * Show Form Error Message
 */
function showFormError(message) {
  // Remove existing error alerts
  const existingAlerts = document.querySelectorAll(".alert-danger.form-error");
  existingAlerts.forEach((alert) => alert.remove());

  // Create new error alert
  const alertDiv = document.createElement("div");
  alertDiv.className =
    "alert alert-danger alert-dismissible fade show form-error";
  alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

  // Insert before form
  const form = document.getElementById("filamentForm");
  if (form) {
    form.parentNode.insertBefore(alertDiv, form);

    // Auto-remove after 5 seconds
    setTimeout(() => {
      if (alertDiv.parentNode) {
        alertDiv.remove();
      }
    }, 5000);
  }
}

/**
 * Global functions for backward compatibility
 */
window.deleteFilament = showDeleteModal;
