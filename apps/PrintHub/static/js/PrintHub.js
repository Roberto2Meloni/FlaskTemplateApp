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

/**
 * PrintHub Drucker JavaScript Functions - Vereinfacht
 * Ergänzungen für PrintHub.js - nur relevante Funktionen
 */

// Erweitere die bestehenden Funktionen in PrintHub.js:

document.addEventListener("DOMContentLoaded", function () {
  // Bestehende Initialisierung...

  // Drucker-spezifische Initialisierung
  initializePrinterFunctions();
});

/**
 * Initialize Printer-specific Functions
 */
function initializePrinterFunctions() {
  // Drucker Delete Modal
  const deletePrinterModalElement =
    document.getElementById("deletePrinterModal");
  if (deletePrinterModalElement) {
    window.deletePrinterModal = new bootstrap.Modal(deletePrinterModalElement);
  }

  // Drucker Form Handler
  initializePrinterForm();

  // Drucker Delete Buttons
  document.addEventListener("click", function (e) {
    const deleteBtn = e.target.closest(
      '[data-action="delete"][data-printer-id]'
    );
    if (!deleteBtn) return;

    e.preventDefault();

    const printerId = deleteBtn.getAttribute("data-printer-id");
    const printerName = deleteBtn.getAttribute("data-printer-name");

    console.log("Delete printer clicked:", printerId, printerName);
    showDeletePrinterModal(printerId, printerName);
  });
}

/**
 * Initialize Printer Form
 */
function initializePrinterForm() {
  const printerForm = document.getElementById("printerForm");
  if (!printerForm) return;

  // Reset Button
  const resetBtn = document.getElementById("resetPrinterFormBtn");
  if (resetBtn) {
    resetBtn.addEventListener("click", function () {
      printerForm.reset();
      // Reset validation classes
      const inputs = printerForm.querySelectorAll(".is-invalid");
      inputs.forEach((input) => input.classList.remove("is-invalid"));
      // Reset cost calculations
      updateDailyCostDisplay();
    });
  }

  // Live Cost Calculation
  const costInput = document.getElementById("machine_cost_per_hour");
  const energyInput = document.getElementById("energy_consumption");

  if (costInput) {
    costInput.addEventListener("input", updateDailyCostDisplay);
  }

  if (energyInput) {
    energyInput.addEventListener("input", updateDailyCostDisplay);
  }

  // Form Validation
  printerForm.addEventListener("submit", validatePrinterForm);

  // Remove validation classes on input
  const inputs = printerForm.querySelectorAll("input, select, textarea");
  inputs.forEach((input) => {
    input.addEventListener("input", function () {
      this.classList.remove("is-invalid");
    });
  });

  // Initial calculations
  updateDailyCostDisplay();
}

/**
 * Show Delete Printer Modal
 */
function showDeletePrinterModal(printerId, printerName) {
  console.log("Showing delete printer modal for:", printerId, printerName);

  if (!window.deletePrinterModal) {
    console.error("Delete printer modal not found");
    return;
  }

  const deleteNameSpan = document.getElementById("deletePrinterName");
  const deleteForm = document.getElementById("deletePrinterForm");

  if (deleteNameSpan) {
    deleteNameSpan.textContent = printerName;
  }

  if (deleteForm) {
    deleteForm.action = `/printhub/printer/delete_printer/${printerId}`;
  }

  window.deletePrinterModal.show();
}

/**
 * Update Daily Cost Display
 */
function updateDailyCostDisplay() {
  const costInput = document.getElementById("machine_cost_per_hour");
  const energyInput = document.getElementById("energy_consumption");

  if (!costInput) return;

  const hourlyCost = parseFloat(costInput.value) || 0;
  const energyWatts = parseFloat(energyInput?.value) || 0;

  // Berechne tägliche Kosten
  const dailyMachineCost = hourlyCost * 24;

  // Berechne Energiekosten (Annahme: 0.25 CHF/kWh)
  const dailyEnergyKwh = (energyWatts / 1000) * 24;
  const dailyEnergyCost = dailyEnergyKwh * 0.25;

  const totalDailyCost = dailyMachineCost + dailyEnergyCost;

  // Update Tooltip
  if (hourlyCost > 0) {
    costInput.title = `Tägliche Kosten: CHF ${totalDailyCost.toFixed(
      2
    )} (24h Betrieb)`;
    costInput.style.borderColor = "var(--prusa-orange)";
  } else {
    costInput.title = "";
    costInput.style.borderColor = "";
  }

  // Update Energie-Tooltip
  if (energyInput && energyWatts > 0) {
    energyInput.title = `Täglich: ${dailyEnergyKwh.toFixed(
      2
    )} kWh = CHF ${dailyEnergyCost.toFixed(2)}`;
    energyInput.style.borderColor = "var(--prusa-orange)";
  } else if (energyInput) {
    energyInput.title = "";
    energyInput.style.borderColor = "";
  }
}

/**
 * Validate Printer Form
 */
function validatePrinterForm(e) {
  const form = e.target;
  const requiredFields = [
    "printer_name",
    "printer_brand",
    "machine_cost_per_hour",
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

  // Validate machine cost is positive
  const costField = document.getElementById("machine_cost_per_hour");
  if (costField) {
    const cost = parseFloat(costField.value);
    if (isNaN(cost) || cost <= 0) {
      costField.classList.add("is-invalid");
      if (!firstInvalidField) firstInvalidField = costField;
      isValid = false;
    } else {
      costField.classList.remove("is-invalid");
    }
  }

  // Validate optional energy consumption
  const energyField = document.getElementById("energy_consumption");
  if (energyField && energyField.value.trim()) {
    const value = parseFloat(energyField.value);
    if (isNaN(value) || value < 0) {
      energyField.classList.add("is-invalid");
      if (!firstInvalidField) firstInvalidField = energyField;
      isValid = false;
    } else {
      energyField.classList.remove("is-invalid");
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

// Global functions
window.deletePrinter = showDeletePrinterModal;

/**
 * Maschinenkosten-Rechner JavaScript
 * Ergänzung für PrintHub.js
 */

// Global Variables for Cost Calculator
let costCalculatorModal;

document.addEventListener("DOMContentLoaded", function () {
  // Initialize Cost Calculator Modal
  const costModalElement = document.getElementById("costCalculatorModal");
  if (costModalElement) {
    costCalculatorModal = new bootstrap.Modal(costModalElement);
  }
});

/**
 * Open Cost Calculator Modal
 */
function openCostCalculator() {
  if (costCalculatorModal) {
    // Load current value if exists
    const currentValue = document.getElementById("machine_cost_per_hour").value;
    if (currentValue && parseFloat(currentValue) > 0) {
      // Try to reverse-engineer the values (optional)
      loadExampleValues();
    }
    costCalculatorModal.show();
  }
}

/**
 * Load Example Values
 */
function loadExampleValues() {
  document.getElementById("calc_purchase_price").value = "1000";
  document.getElementById("calc_lifetime_hours").value = "3000";
  document.getElementById("calc_maintenance_cost").value = "0.50";
  document.getElementById("calc_room_cost").value = "1.00";
  document.getElementById("calc_failure_rate").value = "15";

  calculateMachineCost();
}

/**
 * Calculate Machine Cost
 */
function calculateMachineCost() {
  // Get input values
  const purchasePrice =
    parseFloat(document.getElementById("calc_purchase_price").value) || 0;
  const lifetimeHours =
    parseFloat(document.getElementById("calc_lifetime_hours").value) || 1;
  const maintenanceCost =
    parseFloat(document.getElementById("calc_maintenance_cost").value) || 0;
  const roomCost =
    parseFloat(document.getElementById("calc_room_cost").value) || 0;
  const failureRate =
    parseFloat(document.getElementById("calc_failure_rate").value) || 0;

  // Calculate depreciation
  const depreciation = purchasePrice / lifetimeHours;

  // Calculate base costs
  const baseCost = depreciation + maintenanceCost + roomCost;

  // Calculate failure risk cost (percentage of base cost)
  const failureCost = baseCost * (failureRate / 100);

  // Total cost per hour
  const totalCost = baseCost + failureCost;

  // Update display elements
  document.getElementById(
    "calc_depreciation"
  ).textContent = `CHF ${depreciation.toFixed(2)}/h`;
  document.getElementById(
    "calc_maintenance_display"
  ).textContent = `CHF ${maintenanceCost.toFixed(2)}/h`;
  document.getElementById(
    "calc_room_display"
  ).textContent = `CHF ${roomCost.toFixed(2)}/h`;
  document.getElementById(
    "calc_failure_display"
  ).textContent = `CHF ${failureCost.toFixed(2)}/h`;
  document.getElementById(
    "calc_total_cost"
  ).innerHTML = `<strong>CHF ${totalCost.toFixed(2)}/h</strong>`;

  // Calculate additional costs
  const dailyCost = totalCost * 24;
  const monthlyCost = totalCost * 720; // 30 days * 24 hours
  const printCost = totalCost * 4; // 4 hour print

  document.getElementById(
    "calc_daily_cost"
  ).textContent = `CHF ${dailyCost.toFixed(2)}`;
  document.getElementById(
    "calc_monthly_cost"
  ).textContent = `CHF ${monthlyCost.toFixed(0)}`;
  document.getElementById(
    "calc_print_cost"
  ).textContent = `CHF ${printCost.toFixed(2)}`;

  // Store calculated value for later use
  window.calculatedMachineCost = totalCost;

  // Visual feedback
  if (totalCost > 0) {
    document.getElementById("calc_total_cost").parentElement.style.borderColor =
      "var(--prusa-orange)";
    document.getElementById("calc_total_cost").parentElement.style.boxShadow =
      "0 0 10px rgba(255, 102, 0, 0.3)";
  }
}

/**
 * Apply Calculated Cost to Form
 */
function applyCostToForm() {
  const calculatedCost = window.calculatedMachineCost;

  if (calculatedCost && calculatedCost > 0) {
    const machineField = document.getElementById("machine_cost_per_hour");
    if (machineField) {
      machineField.value = calculatedCost.toFixed(2);

      // Trigger change event to update any live calculations
      machineField.dispatchEvent(new Event("input"));

      // Visual feedback
      machineField.style.borderColor = "var(--prusa-orange)";
      machineField.style.boxShadow = "0 0 10px rgba(255, 102, 0, 0.3)";

      setTimeout(() => {
        machineField.style.borderColor = "";
        machineField.style.boxShadow = "";
      }, 2000);
    }

    // Close modal
    if (costCalculatorModal) {
      costCalculatorModal.hide();
    }

    // Show success message
    showTemporaryMessage("Maschinenkosten erfolgreich übernommen!", "success");
  } else {
    showTemporaryMessage(
      "Bitte füllen Sie die Berechnungsfelder aus!",
      "warning"
    );
  }
}

/**
 * Show Temporary Message
 */
function showTemporaryMessage(message, type = "info") {
  // Remove existing temporary messages
  const existingMessages = document.querySelectorAll(".temp-message");
  existingMessages.forEach((msg) => msg.remove());

  // Create message element
  const messageDiv = document.createElement("div");
  messageDiv.className = `alert alert-${type} temp-message`;
  messageDiv.style.position = "fixed";
  messageDiv.style.top = "20px";
  messageDiv.style.right = "20px";
  messageDiv.style.zIndex = "9999";
  messageDiv.style.minWidth = "300px";
  messageDiv.style.animation = "slideInRight 0.3s ease";
  messageDiv.innerHTML = `
        <i class="bi bi-${
          type === "success"
            ? "check-circle"
            : type === "warning"
            ? "exclamation-triangle"
            : "info-circle"
        }"></i>
        ${message}
    `;

  document.body.appendChild(messageDiv);

  // Remove after 3 seconds
  setTimeout(() => {
    messageDiv.style.animation = "slideOutRight 0.3s ease";
    setTimeout(() => {
      if (messageDiv.parentNode) {
        messageDiv.remove();
      }
    }, 300);
  }, 3000);
}

/**
 * Enhanced Form Validation for Printer Form (erweitert bestehende Funktion)
 */
function validatePrinterFormWithCalculator(e) {
  const form = e.target;
  const requiredFields = [
    "printer_name",
    "printer_brand",
    "machine_cost_per_hour",
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

  // Validate machine cost is positive
  const costField = document.getElementById("machine_cost_per_hour");
  if (costField) {
    const cost = parseFloat(costField.value);
    if (isNaN(cost) || cost <= 0) {
      costField.classList.add("is-invalid");
      if (!firstInvalidField) firstInvalidField = costField;
      isValid = false;

      // Suggest using calculator
      showTemporaryMessage(
        "Verwenden Sie den Rechner-Button für eine genaue Kostenkalkulation!",
        "info"
      );
    } else {
      costField.classList.remove("is-invalid");
    }
  }

  // Validate optional energy consumption
  const energyField = document.getElementById("energy_consumption");
  if (energyField && energyField.value.trim()) {
    const value = parseFloat(energyField.value);
    if (isNaN(value) || value < 0) {
      energyField.classList.add("is-invalid");
      if (!firstInvalidField) firstInvalidField = energyField;
      isValid = false;
    } else {
      energyField.classList.remove("is-invalid");
    }
  }

  if (!isValid) {
    e.preventDefault();

    // Focus first invalid field
    if (firstInvalidField) {
      firstInvalidField.focus();
    }

    showTemporaryMessage(
      "Bitte füllen Sie alle Pflichtfelder korrekt aus!",
      "warning"
    );
  }
}

// Add CSS animations for messages
const messageAnimations = `
@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes slideOutRight {
    from {
        transform: translateX(0);
        opacity: 1;
    }
    to {
        transform: translateX(100%);
        opacity: 0;
    }
}
`;

// Add animations to page
const styleSheet = document.createElement("style");
styleSheet.textContent = messageAnimations;
document.head.appendChild(styleSheet);

// Global functions
window.openCostCalculator = openCostCalculator;
window.calculateMachineCost = calculateMachineCost;
window.loadExampleValues = loadExampleValues;
window.applyCostToForm = applyCostToForm;

// Form zurücksetzen
document
  .getElementById("resetEnergyFormBtn")
  ?.addEventListener("click", function () {
    document.getElementById("energyCostForm").reset();
  });

// Nachttarif automatisch aktivieren bei Doppeltarif
document.getElementById("tariff_type")?.addEventListener("change", function () {
  const nightRateField = document.getElementById("night_rate");
  if (this.value.includes("Tag/Nacht") || this.value.includes("Doppeltarif")) {
    nightRateField.setAttribute("placeholder", "Nachttarif erforderlich");
    nightRateField.parentElement.parentElement.classList.add("required-field");
  } else {
    nightRateField.setAttribute("placeholder", "0.1800");
    nightRateField.parentElement.parentElement.classList.remove(
      "required-field"
    );
  }
});

// Gültigkeitsdaten validation
document.getElementById("valid_from")?.addEventListener("change", function () {
  const validUntil = document.getElementById("valid_until");
  if (this.value) {
    validUntil.min = this.value;
  }
});

// Delete Modal Handling
document.addEventListener("DOMContentLoaded", function () {
  // Delete Button Click Handler
  document.querySelectorAll('[data-action="delete"]').forEach((button) => {
    button.addEventListener("click", function () {
      const energyCostId = this.getAttribute("data-energy-id");
      const energyCostName = this.getAttribute("data-energy-name");

      // Modal-Inhalte setzen
      document.getElementById("deleteEnergyCostName").textContent =
        energyCostName;
      document.getElementById(
        "deleteEnergyCostForm"
      ).action = `/PrintHub/energy_cost/delete_energy_cost/${energyCostId}`;

      // Modal anzeigen
      const deleteModal = new bootstrap.Modal(
        document.getElementById("deleteEnergyCostModal")
      );
      deleteModal.show();
    });
  });

  // Toggle Active/Inactive Handler (falls gewünscht)
  document.querySelectorAll('[data-action="toggle"]').forEach((button) => {
    button.addEventListener("click", function () {
      const energyCostId = this.getAttribute("data-energy-id");

      // AJAX Request um Status zu ändern (optional)
      fetch(`/PrintHub/energy_cost/toggle_energy_cost/${energyCostId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            location.reload(); // Seite neu laden um Änderungen zu zeigen
          } else {
            alert("Fehler beim Ändern des Status");
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          alert("Fehler beim Ändern des Status");
        });
    });
  });
});

// Form zurücksetzen
document
  .getElementById("resetWorkFormBtn")
  ?.addEventListener("click", function () {
    document.getElementById("workHourForm").reset();
  });

// Gültigkeitsdaten validation
document.getElementById("valid_from")?.addEventListener("change", function () {
  const validUntil = document.getElementById("valid_until");
  if (this.value) {
    validUntil.min = this.value;
  }
});

// Delete Modal Handling
document.addEventListener("DOMContentLoaded", function () {
  // Delete Button Click Handler
  document.querySelectorAll('[data-action="delete"]').forEach((button) => {
    button.addEventListener("click", function () {
      const workId = this.getAttribute("data-work-id");
      const workName = this.getAttribute("data-work-name");

      // Modal-Inhalte setzen
      document.getElementById("deleteWorkHourName").textContent = workName;
      document.getElementById(
        "deleteWorkHourForm"
      ).action = `/PrintHub/work_hour/delete_work_hour/${workId}`;

      // Modal anzeigen
      const deleteModal = new bootstrap.Modal(
        document.getElementById("deleteWorkHourModal")
      );
      deleteModal.show();
    });
  });
});

// Form zurücksetzen
document
  .getElementById("resetOverheadFormBtn")
  ?.addEventListener("click", function () {
    document.getElementById("overheadProfileForm").reset();
    updateLiveCalculation();
  });

// Live-Berechnung
function updateLiveCalculation() {
  const rent = parseFloat(document.getElementById("rent_monthly").value) || 0;
  const heating =
    parseFloat(document.getElementById("heating_electricity").value) || 0;
  const insurance = parseFloat(document.getElementById("insurance").value) || 0;
  const internet = parseFloat(document.getElementById("internet").value) || 0;
  const softwareCost =
    parseFloat(document.getElementById("software_cost").value) || 0;
  const softwareBilling = document.getElementById("software_billing").value;
  const otherCosts =
    parseFloat(document.getElementById("other_costs").value) || 0;
  const plannedHours =
    parseInt(document.getElementById("planned_hours_monthly").value) || 1;

  // Software-Kosten pro Monat berechnen
  const softwareMonthly =
    softwareBilling === "yearly" ? softwareCost / 12 : softwareCost;

  // Gesamte Fixkosten
  const totalMonthly =
    rent + heating + insurance + internet + softwareMonthly + otherCosts;

  // Overhead pro Stunde
  const overheadHourly = totalMonthly / plannedHours;

  // Anzeige aktualisieren
  document.getElementById(
    "calc-monthly-total"
  ).textContent = `CHF ${totalMonthly.toFixed(2)}`;
  document.getElementById(
    "calc-overhead-hourly"
  ).textContent = `CHF ${overheadHourly.toFixed(4)}/h`;
}

// Event Listener für Live-Berechnung
document.addEventListener("DOMContentLoaded", function () {
  const calcFields = [
    "rent_monthly",
    "heating_electricity",
    "insurance",
    "internet",
    "software_cost",
    "software_billing",
    "other_costs",
    "planned_hours_monthly",
  ];

  calcFields.forEach((fieldId) => {
    const field = document.getElementById(fieldId);
    if (field) {
      field.addEventListener("input", updateLiveCalculation);
      field.addEventListener("change", updateLiveCalculation);
    }
  });

  // Initial calculation
  updateLiveCalculation();

  // Delete Button Click Handler
  document.querySelectorAll('[data-action="delete"]').forEach((button) => {
    button.addEventListener("click", function () {
      const profileId = this.getAttribute("data-profile-id");
      const profileName = this.getAttribute("data-profile-name");

      // Modal-Inhalte setzen
      document.getElementById("deleteOverheadProfileName").textContent =
        profileName;
      document.getElementById(
        "deleteOverheadProfileForm"
      ).action = `/PrintHub/overhead_profile/delete_overhead_profile/${profileId}`;

      // Modal anzeigen
      const deleteModal = new bootstrap.Modal(
        document.getElementById("deleteOverheadProfileModal")
      );
      deleteModal.show();
    });
  });
});
