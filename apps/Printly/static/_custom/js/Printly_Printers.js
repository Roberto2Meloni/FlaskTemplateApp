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
          const action = data.is_archived ? "begraben 🪦" : "wiederbelebt 💚";
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

  // ----------------------------------------------------------
  // OVERHEAD VERKNÜPFUNG
  // ----------------------------------------------------------

  linkOverhead(printerId) {
    const overheadId = $(`#overheadSelect_${printerId}`).val();
    const isDefault = $(`#overheadIsDefault_${printerId}`).is(":checked");

    if (!overheadId) {
      alert("Bitte ein Overhead-Profil wählen.");
      return;
    }

    const url = APP_URLS.api_overhead_link_printer.replace(
      "/0",
      `/${overheadId}`,
    );
    fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify({ printer_id: printerId, is_default: isDefault }),
    })
      .then((r) => r.json())
      .then((data) => {
        if (data.success) window.location.reload();
        else alert("Fehler: " + (data.error || "Unbekannter Fehler"));
      })
      .catch((err) => {
        console.error("[PrinterModal] Fehler:", err);
        alert("Verbindungsfehler – bitte nochmals versuchen.");
      });
  },

  unlinkOverhead(overheadId, printerId, overheadName) {
    if (!confirm(`Verknüpfung mit "${overheadName}" entfernen?`)) return;

    const url = APP_URLS.api_overhead_unlink_printer.replace(
      "/0",
      `/${overheadId}`,
    );
    fetch(url, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify({ printer_id: printerId }),
    })
      .then((r) => r.json())
      .then((data) => {
        if (data.success) window.location.reload();
        else alert("Fehler: " + (data.error || "Unbekannter Fehler"));
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

    console.log("[PrinterModal] Payload:", JSON.stringify(payload)); // ← NEU
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
// STATS
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
  let totalCost = 0;
  let count = 0;

  cards.forEach((card) => {
    const brand = card
      .querySelector(".printer-card__brand")
      ?.textContent.trim();
    if (brand) brands.add(brand);

    const btn = card.querySelector(".btn-edit");
    if (btn && btn.dataset.cost) {
      totalCost += parseFloat(btn.dataset.cost);
      count++;
    }
  });

  if (elBrands) elBrands.textContent = brands.size;
  if (elAvgCost && count > 0)
    elAvgCost.textContent = (totalCost / count).toFixed(2);
}

document.addEventListener("DOMContentLoaded", updatePrinterStats);

// ============================================================
// MASCHINENKOSTEN-RECHNER
// ============================================================
const MachineCalc = {
  open() {
    MachineCalc.calculate();
    $("#machineCalcModal").modal("show");
  },

  loadExample() {
    $("#calcPurchasePrice").val(1099);
    $("#calcLifetime").val(5000);
    $("#calcMaintenance").val(0.5);
    $("#calcRoomCost").val(0.0); // ← Weitere Fixkosten = 0
    $("#calcFailureRisk").val(15);
    MachineCalc.calculate();
  },

  calculate() {
    const purchase = parseFloat($("#calcPurchasePrice").val()) || 0;
    const lifetime = parseFloat($("#calcLifetime").val()) || 0;
    const maintenance = parseFloat($("#calcMaintenance").val()) || 0;
    const roomCost = parseFloat($("#calcRoomCost").val()) || 0;
    const failureRisk = parseFloat($("#calcFailureRisk").val()) || 0;

    if (purchase <= 0 || lifetime <= 0) {
      $(
        "#resultDepreciation, #resultMaintenance, #resultRoom, #resultFailure, #resultTotal",
      ).text("– CHF/h");
      $("#resultDaily, #resultMonthly, #result5h").text("–");
      $("#btnApplyCalc").prop("disabled", true);
      return;
    }

    const depreciation = purchase / lifetime;
    const baseCost = depreciation + maintenance + roomCost;
    const failureSurcharge = baseCost * (failureRisk / 100);
    const total = baseCost + failureSurcharge;

    $("#resultDepreciation").text(`CHF ${depreciation.toFixed(4)}/h`);
    $("#resultMaintenance").text(`CHF ${maintenance.toFixed(2)}/h`);
    $("#resultRoom").text(`CHF ${roomCost.toFixed(2)}/h`);
    $("#resultFailure").text(`CHF ${failureSurcharge.toFixed(4)}/h`);
    $("#resultTotal").text(`CHF ${total.toFixed(2)}/h`);
    $("#resultDaily").text(`CHF ${(total * 24).toFixed(2)}`);
    $("#resultMonthly").text(`CHF ${(total * 720).toFixed(2)}`);
    $("#result5h").text(`CHF ${(total * 5).toFixed(2)}`);

    $("#btnApplyCalc").prop("disabled", false).data("value", total.toFixed(2));
  },

  apply() {
    const value = $("#btnApplyCalc").data("value");
    if (value) {
      $("#formCost").val(value);
      $("#machineCalcModal").modal("hide");
    }
  },
};

console.log("Printers.js geladen");
