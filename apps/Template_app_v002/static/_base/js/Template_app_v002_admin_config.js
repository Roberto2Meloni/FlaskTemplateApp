// Config Management JavaScript
console.log("Config Management JS geladen");

// Speichere Original-Werte beim Laden
let originalValues = {};

/**
 * Wird aufgerufen wenn die Config-Seite geladen wird.
 */
function initializeConfigPage() {
  const form = document.getElementById("configForm");

  if (!form) {
    console.warn("Config Form nicht gefunden - überspringe Initialisierung");
    return;
  }

  saveOriginalValues(form);
  console.log("Config Page initialisiert");
}

/**
 * Speichert alle Original-Werte des Forms
 */
function saveOriginalValues(form) {
  const formData = new FormData(form);

  originalValues = {};

  for (let [key, value] of formData.entries()) {
    originalValues[key] = value;
  }

  const checkboxes = form.querySelectorAll('input[type="checkbox"]');
  checkboxes.forEach((cb) => {
    originalValues[cb.name] = cb.checked;
  });

  console.log(
    "Original-Werte gespeichert:",
    Object.keys(originalValues).length,
    "Felder",
  );
}

/**
 * Reset: Alle Felder auf Original-Werte zurücksetzen
 * Aufruf via: onclick="resetConfig()"
 */
function resetConfig() {
  if (!confirm("Alle Änderungen verwerfen und zurücksetzen?")) {
    return;
  }

  const form = document.getElementById("configForm");
  if (!form) return;

  for (let [key, value] of Object.entries(originalValues)) {
    const field = form.elements[key];
    if (field) {
      if (field.type === "checkbox") {
        field.checked = value;
      } else {
        field.value = value;
      }
    }
  }

  showToast("Formular wurde zurückgesetzt", "info");
}

/**
 * Task hinzufügen (optional)
 * Aufruf via: onclick="addTask()"
 */
function addTask() {
  const taskNameInput = document.getElementById("new_task_name");
  const taskIntervalInput = document.getElementById("new_task_interval");

  if (!taskNameInput || !taskIntervalInput) {
    console.error("Task Input-Felder nicht gefunden");
    return;
  }

  const taskName = taskNameInput.value.trim();
  const taskInterval = taskIntervalInput.value;

  if (!taskName || !taskInterval) {
    showToast("Bitte Task-Name und Intervall eingeben.", "error");
    return;
  }

  const input = document.createElement("input");
  input.type = "hidden";
  input.name = `tasks_intervall[${taskName}]`;
  input.value = taskInterval;
  document.getElementById("configForm").appendChild(input);

  showToast(
    `Task "${taskName}" mit Intervall ${taskInterval} Min. wird beim Speichern hinzugefügt.`,
    "success",
  );

  taskNameInput.value = "";
  taskIntervalInput.value = "";
}

/**
 * Config speichern via API Call
 * Aufruf via: onclick="saveConfig()"
 */
async function saveConfig() {
  const form = document.getElementById("configForm");
  const saveBtn = document.getElementById("saveBtn");

  if (!form || !saveBtn) {
    console.error("Form oder Save-Button nicht gefunden");
    return;
  }

  const formData = new FormData(form);

  saveBtn.disabled = true;
  const originalHTML = saveBtn.innerHTML;
  saveBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Speichere...';

  try {
    const response = await fetch(form.action, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (data.success) {
      showToast(
        data.message || "Konfiguration erfolgreich gespeichert!",
        "success",
      );
      saveOriginalValues(form);
    } else {
      showToast(data.message || "Fehler beim Speichern!", "error");
    }
  } catch (error) {
    console.error("Fehler beim Speichern:", error);
    showToast("Verbindungsfehler: " + error.message, "error");
  } finally {
    saveBtn.disabled = false;
    saveBtn.innerHTML = originalHTML;
  }
}

/**
 * Zeigt eine Toast-Benachrichtigung
 */
function showToast(message, type = "info") {
  const toast = document.getElementById("toast-notification");

  if (!toast) {
    console.warn("Toast-Element nicht gefunden");
    alert(message);
    return;
  }

  const icons = {
    success:
      '<i class="bi bi-check-circle-fill" style="color: #28a745; font-size: 20px;"></i>',
    error:
      '<i class="bi bi-x-circle-fill" style="color: #dc3545; font-size: 20px;"></i>',
    info: '<i class="bi bi-info-circle-fill" style="color: #3498db; font-size: 20px;"></i>',
  };

  toast.innerHTML = `
    ${icons[type]}
    <span>${message}</span>
  `;

  toast.className = `toast-notification ${type} show`;

  setTimeout(() => {
    toast.classList.remove("show");
  }, 3000);
}

// ========================================
// CONFIG FUNCTIONS
// ========================================

function initConfigForm() {
  const form = document.getElementById("configForm");
  if (!form) return;

  const resetBtn = document.getElementById("resetBtn");
  const saveBtn = document.getElementById("saveBtn");

  // Store original values
  const originalValues = {};
  form.querySelectorAll("input:not([readonly])").forEach((input) => {
    originalValues[input.id] =
      input.type === "checkbox" ? input.checked : input.value;
  });

  // Reset
  if (resetBtn) {
    resetBtn.addEventListener("click", function () {
      Object.keys(originalValues).forEach((id) => {
        const input = document.getElementById(id);
        if (input) {
          if (input.type === "checkbox") {
            input.checked = originalValues[id];
          } else {
            input.value = originalValues[id];
          }
        }
      });
      showToast("Änderungen zurückgesetzt", "success");
    });
  }

  // Submit
  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    saveBtn.disabled = true;
    saveBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Speichert...';

    try {
      const formData = new FormData(form);
      const response = await fetch(form.action, {
        method: "POST",
        body: formData,
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });

      const result = await response.json();

      if (result.success) {
        showToast("Konfiguration erfolgreich gespeichert!", "success");

        // Update original values
        form.querySelectorAll("input:not([readonly])").forEach((input) => {
          originalValues[input.id] =
            input.type === "checkbox" ? input.checked : input.value;
        });
      } else {
        showToast(
          "Fehler: " + (result.message || "Unbekannter Fehler"),
          "error",
        );
      }
    } catch (error) {
      showToast("Fehler beim Speichern: " + error.message, "error");
    } finally {
      saveBtn.disabled = false;
      saveBtn.innerHTML = '<i class="bi bi-save"></i> Speichern';
    }
  });
}

// Initialisierung beim ersten Laden
document.addEventListener("DOMContentLoaded", initializeConfigPage);

console.log("Config Management JS bereit");
