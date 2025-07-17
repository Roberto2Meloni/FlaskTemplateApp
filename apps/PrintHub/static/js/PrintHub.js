/**
 * PrintHub JavaScript - Optimierte modulare Version
 * Alle PrintHub Funktionen in einer organisierten Struktur
 */

console.log("PrintHub JS loaded - Optimized Version");

// Global PrintHub Namespace
const PrintHub = {
  // Configuration
  config: {
    energyRate: 0.25, // CHF per kWh
    validationMessages: {
      required: "Bitte füllen Sie alle Pflichtfelder aus!",
      positiveNumber: "Wert muss eine positive Zahl sein!",
      validEmail: "Bitte geben Sie eine gültige E-Mail-Adresse ein!",
    },
  },

  // Global state
  state: {
    modals: {},
    calculatedValues: {},
  },

  // Utility functions
  utils: {
    // Safe DOM element access
    getElement: (id) => document.getElementById(id),

    // Safe value extraction
    getValue: (elementId, defaultValue = 0) => {
      const element = PrintHub.utils.getElement(elementId);
      if (!element) {
        console.warn(`Element '${elementId}' not found`);
        return defaultValue;
      }
      const value = parseFloat(element.value);
      return isNaN(value) ? defaultValue : value;
    },

    // Safe text setting
    setText: (elementId, text) => {
      const element = PrintHub.utils.getElement(elementId);
      if (element) {
        element.textContent = text;
        return true;
      }
      console.warn(`Cannot set text - element '${elementId}' not found`);
      return false;
    },

    // Safe value setting
    setValue: (elementId, value) => {
      const element = PrintHub.utils.getElement(elementId);
      if (element) {
        element.value = value;
        return true;
      }
      console.warn(`Cannot set value - element '${elementId}' not found`);
      return false;
    },

    // Format currency
    formatCurrency: (amount, currency = "CHF") => {
      return `${currency} ${amount.toFixed(2)}`;
    },

    // Add event listener safely
    addEventSafe: (elementId, event, callback) => {
      const element = PrintHub.utils.getElement(elementId);
      if (element) {
        element.addEventListener(event, callback);
        return true;
      }
      console.warn(
        `Cannot add event listener - element '${elementId}' not found`
      );
      return false;
    },

    // Show temporary message
    showMessage: (message, type = "info", duration = 3000) => {
      // Remove existing messages
      document.querySelectorAll(".temp-message").forEach((msg) => msg.remove());

      const messageDiv = document.createElement("div");
      messageDiv.className = `alert alert-${type} temp-message`;
      messageDiv.style.cssText = `
        position: fixed; top: 20px; right: 20px; z-index: 9999;
        min-width: 300px; animation: slideInRight 0.3s ease;
      `;

      const iconMap = {
        success: "check-circle",
        warning: "exclamation-triangle",
        error: "x-circle",
        info: "info-circle",
      };

      messageDiv.innerHTML = `
        <i class="bi bi-${iconMap[type] || "info-circle"}"></i>
        ${message}
      `;

      document.body.appendChild(messageDiv);

      setTimeout(() => {
        messageDiv.style.animation = "slideOutRight 0.3s ease";
        setTimeout(() => messageDiv.remove(), 300);
      }, duration);
    },
  },

  // Form validation
  validation: {
    // Generic field validation
    validateField: (fieldId, rules = {}) => {
      const element = PrintHub.utils.getElement(fieldId);
      if (!element) return false;

      const value = element.value.trim();
      let isValid = true;

      // Required check
      if (rules.required && !value) {
        isValid = false;
      }

      // Number validation
      if (rules.type === "number" && value) {
        const num = parseFloat(value);
        if (isNaN(num)) isValid = false;
        if (rules.min !== undefined && num < rules.min) isValid = false;
        if (rules.max !== undefined && num > rules.max) isValid = false;
      }

      // Email validation
      if (rules.type === "email" && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) isValid = false;
      }

      // Apply visual feedback
      element.classList.toggle("is-invalid", !isValid);
      return isValid;
    },

    // Validate entire form
    validateForm: (formId, fieldRules) => {
      let isValid = true;
      let firstInvalidField = null;

      Object.entries(fieldRules).forEach(([fieldId, rules]) => {
        const fieldValid = PrintHub.validation.validateField(fieldId, rules);
        if (!fieldValid) {
          isValid = false;
          if (!firstInvalidField) {
            firstInvalidField = PrintHub.utils.getElement(fieldId);
          }
        }
      });

      if (!isValid && firstInvalidField) {
        firstInvalidField.focus();
        PrintHub.utils.showMessage(
          PrintHub.config.validationMessages.required,
          "error"
        );
      }

      return isValid;
    },
  },

  // Modal management
  modals: {
    // Initialize modal
    init: (modalId) => {
      const modalElement = PrintHub.utils.getElement(modalId);
      if (modalElement && typeof bootstrap !== "undefined") {
        PrintHub.state.modals[modalId] = new bootstrap.Modal(modalElement);
        return PrintHub.state.modals[modalId];
      }
      console.warn(`Modal '${modalId}' not found or Bootstrap not available`);
      return null;
    },

    // Show modal
    show: (modalId) => {
      if (PrintHub.state.modals[modalId]) {
        PrintHub.state.modals[modalId].show();
      } else {
        console.warn(`Modal '${modalId}' not initialized`);
      }
    },

    // Hide modal
    hide: (modalId) => {
      if (PrintHub.state.modals[modalId]) {
        PrintHub.state.modals[modalId].hide();
      }
    },

    // Generic delete modal
    showDeleteModal: (modalId, itemId, itemName, deleteUrl) => {
      const modal = PrintHub.state.modals[modalId];
      if (!modal) {
        console.error(`Delete modal '${modalId}' not found`);
        return;
      }

      // Set item name in modal
      const nameElement = document.querySelector(
        `#${modalId} [data-item-name]`
      );
      if (nameElement) {
        nameElement.textContent = itemName;
      }

      // Set form action
      const formElement = document.querySelector(`#${modalId} form`);
      if (formElement) {
        formElement.action = deleteUrl;
      }

      modal.show();
    },
  },

  // Filament Management
  filament: {
    init: () => {
      console.log("Initializing filament module");

      // Initialize form
      PrintHub.filament.initForm();

      // Initialize delete handlers
      PrintHub.filament.initDeleteHandlers();
    },

    initForm: () => {
      const formId = "filamentForm";
      const form = PrintHub.utils.getElement(formId);
      if (!form) return;

      // Reset button
      PrintHub.utils.addEventSafe("resetFormBtn", "click", () => {
        form.reset();
        form
          .querySelectorAll(".is-invalid")
          .forEach((input) => input.classList.remove("is-invalid"));
      });

      // Live price calculation
      ["filament_weight", "filament_price"].forEach((fieldId) => {
        PrintHub.utils.addEventSafe(
          fieldId,
          "input",
          PrintHub.filament.updatePricePerKg
        );
      });

      // Form validation
      form.addEventListener("submit", PrintHub.filament.validateForm);

      // Remove validation on input
      form.querySelectorAll("input, select, textarea").forEach((input) => {
        input.addEventListener("input", () =>
          input.classList.remove("is-invalid")
        );
      });
    },

    initDeleteHandlers: () => {
      PrintHub.modals.init("deleteModal");

      document.addEventListener("click", (e) => {
        const deleteBtn = e.target.closest(
          '[data-action="delete"][data-filament-id]'
        );
        if (!deleteBtn) return;

        e.preventDefault();
        const filamentId = deleteBtn.getAttribute("data-filament-id");
        const filamentName = deleteBtn.getAttribute("data-filament-name");
        const deleteUrl = `/PrintHub/filament/delete_filament/${filamentId}`;

        PrintHub.modals.showDeleteModal(
          "deleteModal",
          filamentId,
          filamentName,
          deleteUrl
        );
      });
    },

    updatePricePerKg: () => {
      const weight = PrintHub.utils.getValue("filament_weight");
      const price = PrintHub.utils.getValue("filament_price");

      const weightElement = PrintHub.utils.getElement("filament_weight");
      const priceElement = PrintHub.utils.getElement("filament_price");

      if (weight > 0 && price > 0) {
        const pricePerKg = ((price / weight) * 1000).toFixed(2);

        if (priceElement) {
          priceElement.title = `Preis pro kg: CHF ${pricePerKg}`;
          priceElement.style.borderColor = "var(--prusa-orange)";
        }
        if (weightElement) {
          weightElement.style.borderColor = "var(--prusa-orange)";
        }
      } else {
        if (priceElement) {
          priceElement.title = "";
          priceElement.style.borderColor = "";
        }
        if (weightElement) {
          weightElement.style.borderColor = "";
        }
      }
    },

    validateForm: (e) => {
      const fieldRules = {
        filament_type: { required: true },
        filament_name: { required: true },
        filament_manufacturer: { required: true },
        filament_weight: { required: true, type: "number", min: 0 },
        filament_price: { required: true, type: "number", min: 0 },
      };

      if (!PrintHub.validation.validateForm("filamentForm", fieldRules)) {
        e.preventDefault();
      }
    },
  },

  // Printer Management
  printer: {
    init: () => {
      console.log("Initializing printer module");

      PrintHub.printer.initForm();
      PrintHub.printer.initDeleteHandlers();
      PrintHub.printer.initCostCalculator();
    },

    initForm: () => {
      const formId = "printerForm";
      const form = PrintHub.utils.getElement(formId);
      if (!form) return;

      // Reset button
      PrintHub.utils.addEventSafe("resetPrinterFormBtn", "click", () => {
        form.reset();
        form
          .querySelectorAll(".is-invalid")
          .forEach((input) => input.classList.remove("is-invalid"));
        PrintHub.printer.updateDailyCostDisplay();
      });

      // Live cost calculation
      ["machine_cost_per_hour", "energy_consumption"].forEach((fieldId) => {
        PrintHub.utils.addEventSafe(
          fieldId,
          "input",
          PrintHub.printer.updateDailyCostDisplay
        );
      });

      // Form validation
      form.addEventListener("submit", PrintHub.printer.validateForm);

      // Remove validation on input
      form.querySelectorAll("input, select, textarea").forEach((input) => {
        input.addEventListener("input", () =>
          input.classList.remove("is-invalid")
        );
      });

      // Initial calculation
      PrintHub.printer.updateDailyCostDisplay();
    },

    initDeleteHandlers: () => {
      PrintHub.modals.init("deletePrinterModal");

      document.addEventListener("click", (e) => {
        const deleteBtn = e.target.closest(
          '[data-action="delete"][data-printer-id]'
        );
        if (!deleteBtn) return;

        e.preventDefault();
        const printerId = deleteBtn.getAttribute("data-printer-id");
        const printerName = deleteBtn.getAttribute("data-printer-name");
        const deleteUrl = `/PrintHub/printer/delete_printer/${printerId}`;

        PrintHub.modals.showDeleteModal(
          "deletePrinterModal",
          printerId,
          printerName,
          deleteUrl
        );
      });
    },

    updateDailyCostDisplay: () => {
      const hourlyCost = PrintHub.utils.getValue("machine_cost_per_hour");
      const energyWatts = PrintHub.utils.getValue("energy_consumption");

      const dailyMachineCost = hourlyCost * 24;
      const dailyEnergyKwh = (energyWatts / 1000) * 24;
      const dailyEnergyCost = dailyEnergyKwh * PrintHub.config.energyRate;
      const totalDailyCost = dailyMachineCost + dailyEnergyCost;

      const costElement = PrintHub.utils.getElement("machine_cost_per_hour");
      const energyElement = PrintHub.utils.getElement("energy_consumption");

      if (costElement && hourlyCost > 0) {
        costElement.title = `Tägliche Kosten: ${PrintHub.utils.formatCurrency(
          totalDailyCost
        )} (24h Betrieb)`;
        costElement.style.borderColor = "var(--prusa-orange)";
      }

      if (energyElement && energyWatts > 0) {
        energyElement.title = `Täglich: ${dailyEnergyKwh.toFixed(
          2
        )} kWh = ${PrintHub.utils.formatCurrency(dailyEnergyCost)}`;
        energyElement.style.borderColor = "var(--prusa-orange)";
      }
    },

    validateForm: (e) => {
      const fieldRules = {
        printer_name: { required: true },
        printer_brand: { required: true },
        machine_cost_per_hour: { required: true, type: "number", min: 0 },
        energy_consumption: { type: "number", min: 0 },
      };

      if (!PrintHub.validation.validateForm("printerForm", fieldRules)) {
        e.preventDefault();
      }
    },

    // Cost Calculator
    initCostCalculator: () => {
      PrintHub.modals.init("costCalculatorModal");
    },

    openCostCalculator: () => {
      PrintHub.modals.show("costCalculatorModal");
      PrintHub.printer.loadExampleValues();
    },

    loadExampleValues: () => {
      const exampleValues = {
        calc_purchase_price: "1000",
        calc_lifetime_hours: "3000",
        calc_maintenance_cost: "0.50",
        calc_room_cost: "1.00",
        calc_failure_rate: "15",
      };

      Object.entries(exampleValues).forEach(([id, value]) => {
        PrintHub.utils.setValue(id, value);
      });

      PrintHub.printer.calculateMachineCost();
    },

    calculateMachineCost: () => {
      const purchasePrice = PrintHub.utils.getValue("calc_purchase_price");
      const lifetimeHours = PrintHub.utils.getValue("calc_lifetime_hours", 1);
      const maintenanceCost = PrintHub.utils.getValue("calc_maintenance_cost");
      const roomCost = PrintHub.utils.getValue("calc_room_cost");
      const failureRate = PrintHub.utils.getValue("calc_failure_rate");

      const depreciation = purchasePrice / lifetimeHours;
      const baseCost = depreciation + maintenanceCost + roomCost;
      const failureCost = baseCost * (failureRate / 100);
      const totalCost = baseCost + failureCost;

      // Update displays
      const updates = {
        calc_depreciation: `CHF ${depreciation.toFixed(2)}/h`,
        calc_maintenance_display: `CHF ${maintenanceCost.toFixed(2)}/h`,
        calc_room_display: `CHF ${roomCost.toFixed(2)}/h`,
        calc_failure_display: `CHF ${failureCost.toFixed(2)}/h`,
        calc_total_cost: `<strong>CHF ${totalCost.toFixed(2)}/h</strong>`,
        calc_daily_cost: PrintHub.utils.formatCurrency(totalCost * 24),
        calc_monthly_cost: PrintHub.utils.formatCurrency(totalCost * 720),
        calc_print_cost: PrintHub.utils.formatCurrency(totalCost * 4),
      };

      Object.entries(updates).forEach(([id, text]) => {
        PrintHub.utils.setText(id, text);
      });

      PrintHub.state.calculatedValues.machineCost = totalCost;
    },

    applyCostToForm: () => {
      const calculatedCost = PrintHub.state.calculatedValues.machineCost;

      if (calculatedCost && calculatedCost > 0) {
        PrintHub.utils.setValue(
          "machine_cost_per_hour",
          calculatedCost.toFixed(2)
        );
        PrintHub.printer.updateDailyCostDisplay();
        PrintHub.modals.hide("costCalculatorModal");
        PrintHub.utils.showMessage(
          "Maschinenkosten erfolgreich übernommen!",
          "success"
        );
      } else {
        PrintHub.utils.showMessage(
          "Bitte füllen Sie die Berechnungsfelder aus!",
          "warning"
        );
      }
    },
  },

  // Discount Profiles
  discountProfiles: {
    init: () => {
      console.log("Initializing discount profiles module");

      PrintHub.discountProfiles.initForm();
      PrintHub.discountProfiles.initDeleteHandlers();
    },

    initForm: () => {
      const formId = "discountProfileForm";
      const form = PrintHub.utils.getElement(formId);
      if (!form) return;

      // Reset button
      PrintHub.utils.addEventSafe("resetFormBtn", "click", () => {
        form.reset();
        PrintHub.discountProfiles.updatePreview();
      });

      // Live preview
      ["discount_type", "percentage"].forEach((fieldId) => {
        PrintHub.utils.addEventSafe(
          fieldId,
          "change",
          PrintHub.discountProfiles.updatePreview
        );
        PrintHub.utils.addEventSafe(
          fieldId,
          "input",
          PrintHub.discountProfiles.updatePreview
        );
      });

      // Initial preview
      PrintHub.discountProfiles.updatePreview();
    },

    initDeleteHandlers: () => {
      PrintHub.modals.init("deleteDiscountProfileModal");

      document.addEventListener("click", (e) => {
        const deleteBtn = e.target.closest(
          '[data-action="delete"][data-profile-id]'
        );
        if (!deleteBtn) return;

        e.preventDefault();
        const profileId = deleteBtn.getAttribute("data-profile-id");
        const profileName = deleteBtn.getAttribute("data-profile-name");
        const deleteUrl = `/PrintHub/discount_profile/delete_discount_profile/${profileId}`;

        PrintHub.modals.showDeleteModal(
          "deleteDiscountProfileModal",
          profileId,
          profileName,
          deleteUrl
        );
      });
    },

    updatePreview: () => {
      const typeElement = PrintHub.utils.getElement("discount_type");
      const type = typeElement ? typeElement.value : "";
      const percentage = PrintHub.utils.getValue("percentage");
      const examplePrice = 100.0;

      let adjustmentAmount, finalPrice, typeDisplay, result;

      if (type === "discount") {
        typeDisplay = "Rabatt";
        adjustmentAmount = examplePrice * (percentage / 100);
        finalPrice = examplePrice - adjustmentAmount;
        result = `${percentage.toFixed(1)}% günstiger`;
      } else if (type === "surcharge") {
        typeDisplay = "Aufschlag";
        adjustmentAmount = examplePrice * (percentage / 100);
        finalPrice = examplePrice + adjustmentAmount;
        result = `${percentage.toFixed(1)}% teurer`;
      } else {
        typeDisplay = "-";
        adjustmentAmount = 0;
        finalPrice = examplePrice;
        result = "Typ wählen";
      }

      const updates = {
        "preview-type": typeDisplay,
        "preview-adjustment": PrintHub.utils.formatCurrency(adjustmentAmount),
        "preview-final": PrintHub.utils.formatCurrency(finalPrice),
        "preview-result": result,
      };

      Object.entries(updates).forEach(([id, text]) => {
        PrintHub.utils.setText(id, text);
      });
    },
  },

  // Generic Cost Module (for energy, work hours, overhead)
  costModule: {
    init: (config) => {
      console.log(`Initializing cost module: ${config.name}`);

      if (config.formId) {
        PrintHub.costModule.initForm(config);
      }

      if (config.deleteModalId) {
        PrintHub.costModule.initDeleteHandlers(config);
      }

      if (config.liveCalculation) {
        PrintHub.costModule.initLiveCalculation(config);
      }
    },

    initForm: (config) => {
      const form = PrintHub.utils.getElement(config.formId);
      if (!form) return;

      // Reset button
      if (config.resetButtonId) {
        PrintHub.utils.addEventSafe(config.resetButtonId, "click", () => {
          form.reset();
          if (config.liveCalculation) {
            config.liveCalculation();
          }
        });
      }

      // Date validation
      if (config.dateFields) {
        config.dateFields.forEach(({ from, to }) => {
          PrintHub.utils.addEventSafe(from, "change", () => {
            const fromElement = PrintHub.utils.getElement(from);
            const toElement = PrintHub.utils.getElement(to);
            if (fromElement && toElement && fromElement.value) {
              toElement.min = fromElement.value;
            }
          });
        });
      }
    },

    initDeleteHandlers: (config) => {
      PrintHub.modals.init(config.deleteModalId);

      document.addEventListener("click", (e) => {
        const deleteBtn = e.target.closest(
          `[data-action="delete"][data-${config.dataAttribute}-id]`
        );
        if (!deleteBtn) return;

        e.preventDefault();
        const itemId = deleteBtn.getAttribute(
          `data-${config.dataAttribute}-id`
        );
        const itemName = deleteBtn.getAttribute(
          `data-${config.dataAttribute}-name`
        );
        const deleteUrl = config.deleteUrlTemplate.replace("{id}", itemId);

        PrintHub.modals.showDeleteModal(
          config.deleteModalId,
          itemId,
          itemName,
          deleteUrl
        );
      });
    },

    initLiveCalculation: (config) => {
      if (config.calculationFields) {
        config.calculationFields.forEach((fieldId) => {
          PrintHub.utils.addEventSafe(fieldId, "input", config.liveCalculation);
          PrintHub.utils.addEventSafe(
            fieldId,
            "change",
            config.liveCalculation
          );
        });

        // Initial calculation
        config.liveCalculation();
      }
    },
  },

  // Main initialization
  init: () => {
    console.log("Initializing PrintHub modules");

    // Add CSS animations
    PrintHub.addAnimations();

    // Initialize individual modules
    PrintHub.filament.init();
    PrintHub.printer.init();
    PrintHub.discountProfiles.init();

    // Initialize cost modules
    PrintHub.costModule.init({
      name: "energy",
      formId: "energyCostForm",
      resetButtonId: "resetEnergyFormBtn",
      deleteModalId: "deleteEnergyCostModal",
      dataAttribute: "energy",
      deleteUrlTemplate: "/PrintHub/energy_cost/delete_energy_cost/{id}",
      dateFields: [{ from: "valid_from", to: "valid_until" }],
    });

    PrintHub.costModule.init({
      name: "work",
      formId: "workHourForm",
      resetButtonId: "resetWorkFormBtn",
      deleteModalId: "deleteWorkHourModal",
      dataAttribute: "work",
      deleteUrlTemplate: "/PrintHub/work_hour/delete_work_hour/{id}",
      dateFields: [{ from: "valid_from", to: "valid_until" }],
    });

    PrintHub.costModule.init({
      name: "overhead",
      formId: "overheadProfileForm",
      resetButtonId: "resetOverheadFormBtn",
      deleteModalId: "deleteOverheadProfileModal",
      dataAttribute: "profile",
      deleteUrlTemplate:
        "/PrintHub/overhead_profile/delete_overhead_profile/{id}",
      liveCalculation: PrintHub.overhead.calculate,
      calculationFields: [
        "rent_monthly",
        "heating_electricity",
        "insurance",
        "internet",
        "software_cost",
        "software_billing",
        "other_costs",
        "planned_hours_monthly",
      ],
    });

    console.log("PrintHub initialization complete");
  },

  // Overhead calculations
  overhead: {
    calculate: () => {
      const rent = PrintHub.utils.getValue("rent_monthly");
      const heating = PrintHub.utils.getValue("heating_electricity");
      const insurance = PrintHub.utils.getValue("insurance");
      const internet = PrintHub.utils.getValue("internet");
      const softwareCost = PrintHub.utils.getValue("software_cost");
      const otherCosts = PrintHub.utils.getValue("other_costs");
      const plannedHours = PrintHub.utils.getValue("planned_hours_monthly", 1);

      const softwareBillingElement =
        PrintHub.utils.getElement("software_billing");
      const softwareBilling = softwareBillingElement
        ? softwareBillingElement.value
        : "monthly";
      const softwareMonthly =
        softwareBilling === "yearly" ? softwareCost / 12 : softwareCost;

      const totalMonthly =
        rent + heating + insurance + internet + softwareMonthly + otherCosts;
      const overheadHourly = totalMonthly / plannedHours;

      PrintHub.utils.setText(
        "calc-monthly-total",
        PrintHub.utils.formatCurrency(totalMonthly)
      );
      PrintHub.utils.setText(
        "calc-overhead-hourly",
        `${PrintHub.utils.formatCurrency(overheadHourly)}/h`
      );
    },
  },

  // Add CSS animations
  addAnimations: () => {
    if (document.getElementById("printhub-animations")) return;

    const animations = `
      @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
      }
      @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
      }
    `;

    const styleSheet = document.createElement("style");
    styleSheet.id = "printhub-animations";
    styleSheet.textContent = animations;
    document.head.appendChild(styleSheet);
  },
};

// Global functions for backward compatibility
window.PrintHub = PrintHub;
window.openCostCalculator = () => PrintHub.printer.openCostCalculator();
window.calculateMachineCost = () => PrintHub.printer.calculateMachineCost();
window.loadExampleValues = () => PrintHub.printer.loadExampleValues();
window.applyCostToForm = () => PrintHub.printer.applyCostToForm();
window.updatePreview = () => PrintHub.discountProfiles.updatePreview();

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", PrintHub.init);

console.log("PrintHub JavaScript loaded successfully");
