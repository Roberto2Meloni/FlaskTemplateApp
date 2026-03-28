/**
 * Printers.js – Printly Drucker-Verwaltung
 */

const PrinterModal = {
  openAdd() {
    $("#printerModalLabel").text("Neuer Drucker");
    $("#printerForm")[0].reset();
    $("#formPrinterId").val("");
    $("#printerModal").modal("show");
  },

  openEdit(dataset) {
    $("#printerModalLabel").text("Drucker bearbeiten");
    $("#printerForm")[0].reset();
    $("#formPrinterId").val(dataset.id || "");
    $("#formName").val(dataset.name || "");
    $("#formCost").val(dataset.cost || "");
    $("#formEnergy").val(dataset.energy || "");
    $("#formNotes").val(dataset.notes || "");

    const brand = dataset.brand || "";
    $("#formBrand option").each(function () {
      $(this).prop(
        "selected",
        $(this).val() === brand || $(this).text() === brand,
      );
    });

    $("#printerModal").modal("show");
  },

  archive(printerId, printerName) {
    const url = APP_URLS.api_printer_archive.replace("/0", `/${printerId}`);

    fetch(url, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
    })
      .then((r) => r.json())
      .then((data) => {
        if (data.success) {
          const action = data.is_archived ? "begraben ⚰️" : "wiederbelebt 💚";
          console.log(`[Printers] '${printerName}' wurde ${action}`);
          window.location.reload();
        } else {
          alert("Fehler: " + (data.error || "Unbekannter Fehler"));
        }
      })
      .catch((err) => {
        console.error("[PrinterModal] Fehler:", err);
        alert("Verbindungsfehler – bitte nochmals versuchen.");
      });
  },

  submit(event) {
    event.preventDefault();
    const id = $("#formPrinterId").val();
    const isEdit = !!id;

    const payload = {
      name: $("#formName").val(),
      brand: $("#formBrand").val(),
      machine_cost_per_hour: parseFloat($("#formCost").val()),
      energy_consumption: $("#formEnergy").val()
        ? parseInt($("#formEnergy").val())
        : null,
      notes: $("#formNotes").val() || null,
    };

    const url = isEdit
      ? APP_URLS.api_printer_update.replace("/0", `/${id}`)
      : APP_URLS.api_printers;
    const method = isEdit ? "PUT" : "POST";

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
          $("#printerModal").modal("hide");
          window.location.reload();
        } else {
          alert("Fehler: " + (data.error || "Unbekannter Fehler"));
        }
      })
      .catch((err) => {
        console.error("[PrinterModal] Fehler:", err);
        alert("Verbindungsfehler – bitte nochmals versuchen.");
      });
  },
};

// ============================================================
// STATS (nur aktive Drucker)
// ============================================================
function updatePrinterStats() {
  const cards = document.querySelectorAll(
    ".printers-grid:not(.printers-grid--graveyard) .printer-card",
  );
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

  const brands = new Set();
  cards.forEach((card) => {
    const brand = card
      .querySelector(".printer-card__brand")
      ?.textContent.trim();
    if (brand) brands.add(brand);
  });
  if (elBrands) elBrands.textContent = brands.size;

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

document.addEventListener("DOMContentLoaded", updatePrinterStats);

console.log("Printers.js geladen");
