/**
 * Printers.js – Printly Drucker-Verwaltung
 * Globales PrinterModal Objekt – wird direkt via onclick im HTML aufgerufen
 */

// ============================================================
// STATS
// ============================================================

function updatePrinterStats() {
  const cards = document.querySelectorAll(".printer-card");
  const total = cards.length;

  const elTotal = document.getElementById("statTotal");
  const elBrands = document.getElementById("statBrands");
  const elAvgCost = document.getElementById("statAvgCost");

  if (elTotal) elTotal.textContent = total;

  if (total === 0) {
    if (elBrands) elBrands.textContent = "0";
    if (elAvgCost) elAvgCost.textContent = "0.00";
    return;
  }

  // Einzigartige Marken
  const brands = new Set();
  cards.forEach((card) => {
    const brand = card
      .querySelector(".printer-card__brand")
      ?.textContent.trim();
    if (brand) brands.add(brand);
  });
  if (elBrands) elBrands.textContent = brands.size;

  // Ø CHF/h
  let totalCost = 0;
  let count = 0;
  cards.forEach((card) => {
    const btn = card.querySelector(".btn-edit");
    if (btn && btn.dataset.cost) {
      totalCost += parseFloat(btn.dataset.cost);
      count++;
    }
  });
  if (elAvgCost && count > 0) {
    elAvgCost.textContent = (totalCost / count).toFixed(2);
  }
}

// ============================================================
// PRINTER MODAL – globales Objekt
// ============================================================

const PrinterModal = {
  // ----------------------------------------------------------
  // ÖFFNEN: Neuer Drucker
  // ----------------------------------------------------------
  openAdd() {
    document.getElementById("modalTitle").textContent = "Neuer Drucker";
    document.getElementById("formPrinterId").value = "";
    document.getElementById("printerForm").reset();
    document.getElementById("printerModal").style.display = "flex";
    document.getElementById("formName").focus();
  },

  // ----------------------------------------------------------
  // ÖFFNEN: Drucker bearbeiten
  // dataset kommt direkt von this.dataset des Buttons
  // ----------------------------------------------------------
  openEdit(dataset) {
    document.getElementById("modalTitle").textContent = "Drucker bearbeiten";
    document.getElementById("printerForm").reset();
    document.getElementById("formPrinterId").value = dataset.id || "";
    document.getElementById("formName").value = dataset.name || "";
    document.getElementById("formCost").value = dataset.cost || "";
    document.getElementById("formEnergy").value = dataset.energy || "";
    document.getElementById("formNotes").value = dataset.notes || "";

    // Marke im Select setzen
    const select = document.getElementById("formBrand");
    Array.from(select.options).forEach((opt) => {
      opt.selected =
        opt.value === dataset.brand || opt.textContent === dataset.brand;
    });

    document.getElementById("printerModal").style.display = "flex";
    document.getElementById("formName").focus();
  },

  // ----------------------------------------------------------
  // SCHLIESSEN
  // ----------------------------------------------------------
  close() {
    document.getElementById("printerModal").style.display = "none";
    document.getElementById("printerForm").reset();
  },

  // ----------------------------------------------------------
  // OVERLAY KLICK – nur schliessen wenn Klick auf Overlay selbst
  // ----------------------------------------------------------
  overlayClick(event) {
    if (event.target === event.currentTarget) {
      PrinterModal.close();
    }
  },

  // ----------------------------------------------------------
  // SUBMIT – API Call
  // Wird via onsubmit="PrinterModal.submit(event)" im <form> aufgerufen
  // ----------------------------------------------------------
  submit(event) {
    event.preventDefault();

    const id = document.getElementById("formPrinterId").value;
    const isEdit = !!id;

    const payload = {
      name: document.getElementById("formName").value,
      brand: document.getElementById("formBrand").value,
      machine_cost_per_hour: parseFloat(
        document.getElementById("formCost").value,
      ),
      energy_consumption: document.getElementById("formEnergy").value
        ? parseInt(document.getElementById("formEnergy").value)
        : null,
      notes: document.getElementById("formNotes").value || null,
    };

    const url = isEdit
      ? `${APP_URLS.api_printer_update}${id}`
      : APP_URLS.api_printers;
    const method = isEdit ? "PUT" : "POST";

    console.log(`[PrinterModal] ${method} ${url}`, payload);

    fetch(url, {
      method,
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify(payload),
    })
      .then((r) => r.json())
      .then((data) => {
        if (data.success) {
          PrinterModal.close();
          window.location.reload();
        } else {
          alert("Fehler: " + (data.error || "Unbekannter Fehler"));
        }
      })
      .catch((err) => {
        console.error("[PrinterModal] API Fehler:", err);
        alert("Verbindungsfehler – bitte nochmals versuchen.");
      });
  },
};

// ============================================================
// ESC – einziger globaler Event Listener (kein onclick-Equivalent)
// ============================================================
document.addEventListener("keydown", function (e) {
  if (e.key === "Escape") {
    const modal = document.getElementById("printerModal");
    if (modal && modal.classList.contains("is-open")) {
      PrinterModal.close();
    }
  }
});

// ============================================================
// INIT
// ============================================================
document.addEventListener("DOMContentLoaded", updatePrinterStats);

console.log("Printers.js geladen");
