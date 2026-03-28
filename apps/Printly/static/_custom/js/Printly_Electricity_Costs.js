/**
 * EnergyCosts.js – Printly Stromtarif-Verwaltung
 */

const EnergyModal = {
  openAdd() {
    $("#energyModalLabel").text("Neuer Tarif");
    $("#energyForm")[0].reset();
    $("#formEnergyId").val("");
    $("#formIsActive").prop("checked", true);
    $("#nightRateRow").hide();
    $("#nightRateRowHidden").show();
    $("#energyModal").modal("show");
  },

  openEdit(dataset) {
    $("#energyModalLabel").text("Tarif bearbeiten");
    $("#energyForm")[0].reset();
    $("#formEnergyId").val(dataset.id || "");
    $("#formEnergyName").val(dataset.name || "");
    $("#formProvider").val(dataset.provider || "");
    $("#formCostPerKwh").val(dataset.cost || "");
    $("#formNightRate").val(dataset.nightRate || "");
    $("#formValidFrom").val(dataset.validFrom || "");
    $("#formValidUntil").val(dataset.validUntil || "");
    $("#formEnergyNotes").val(dataset.notes || "");
    $("#formIsActive").prop("checked", dataset.isActive === "true");

    $("#formTariffType option").each(function () {
      $(this).prop("selected", $(this).val() === dataset.tariffType);
    });

    $("#formBaseFee").val(dataset.baseFee || "");
    $("#formBaseFeeSimple").val(dataset.baseFee || "");

    EnergyModal._toggleNightRate(dataset.tariffType);
    $("#energyModal").modal("show");
  },

  toggle(costId, costName) {
    const url = APP_URLS.api_energy_cost_toggle.replace("/0", `/${costId}`);
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
          const status = data.is_active ? "aktiviert ⚡" : "deaktiviert ⏸";
          console.log(`[Energy] '${costName}' wurde ${status}`);
          window.location.reload();
        } else {
          alert("Fehler: " + (data.error || "Unbekannter Fehler"));
        }
      })
      .catch((err) => {
        console.error("[EnergyModal] Fehler:", err);
        alert("Verbindungsfehler – bitte nochmals versuchen.");
      });
  },

  delete(costId, costName) {
    if (!confirm(`Tarif "${costName}" wirklich löschen?`)) return;

    const url = APP_URLS.api_energy_cost_delete.replace("/0", `/${costId}`);
    fetch(url, {
      method: "DELETE",
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then((r) => r.json())
      .then((data) => {
        if (data.success) window.location.reload();
        else alert("Fehler: " + (data.error || "Unbekannter Fehler"));
      })
      .catch((err) => {
        console.error("[EnergyModal] Fehler:", err);
        alert("Verbindungsfehler – bitte nochmals versuchen.");
      });
  },

  submit(event) {
    event.preventDefault();
    const id = $("#formEnergyId").val();
    const isEdit = !!id;
    const isDoppeltarif =
      $("#formTariffType").val() === "Doppeltarif (Tag/Nacht)";

    const baseFee = isDoppeltarif
      ? $("#formBaseFee").val()
      : $("#formBaseFeeSimple").val();

    const payload = {
      name: $("#formEnergyName").val(),
      provider: $("#formProvider").val(),
      cost_per_kwh: parseFloat($("#formCostPerKwh").val()),
      base_fee_monthly: baseFee ? parseFloat(baseFee) : null,
      tariff_type: $("#formTariffType").val() || null,
      valid_from: $("#formValidFrom").val() || null,
      valid_until: $("#formValidUntil").val() || null,
      night_rate:
        isDoppeltarif && $("#formNightRate").val()
          ? parseFloat($("#formNightRate").val())
          : null,
      is_active: $("#formIsActive").is(":checked"),
      notes: $("#formEnergyNotes").val() || null,
    };

    const url = isEdit
      ? APP_URLS.api_energy_cost_update.replace("/0", `/${id}`)
      : APP_URLS.api_energy_costs;
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
          $("#energyModal").modal("hide");
          window.location.reload();
        } else {
          alert("Fehler: " + (data.error || "Unbekannter Fehler"));
        }
      })
      .catch((err) => {
        console.error("[EnergyModal] Fehler:", err);
        alert("Verbindungsfehler – bitte nochmals versuchen.");
      });
  },

  // ----------------------------------------------------------
  // HILFSFUNKTIONEN
  // ----------------------------------------------------------

  _toggleNightRate(tariffType) {
    if (tariffType === "Doppeltarif (Tag/Nacht)") {
      $("#nightRateRow").show();
      $("#nightRateRowHidden").hide();
    } else {
      $("#nightRateRow").hide();
      $("#nightRateRowHidden").show();
    }
  },
};

// Tariftyp-Wechsel → Nachttarif-Feld ein/ausblenden
$(document).on("change", "#formTariffType", function () {
  EnergyModal._toggleNightRate($(this).val());
});

// ============================================================
// STATS
// ============================================================
function updateEnergyStats() {
  const cards = document.querySelectorAll(".energy-card");
  const total = cards.length;
  const elTotal = document.getElementById("statTotal");
  const elActive = document.getElementById("statActive");
  const elAvgKwh = document.getElementById("statAvgKwh");

  if (elTotal) elTotal.textContent = total;

  let activeCount = 0;
  let totalKwh = 0;
  let count = 0;

  cards.forEach((card) => {
    const btn = card.querySelector(".btn-edit");
    if (!btn) return;
    if (btn.dataset.isActive === "true") activeCount++;
    const cost = parseFloat(btn.dataset.cost);
    if (cost > 0) {
      totalKwh += cost;
      count++;
    }
  });

  if (elActive) elActive.textContent = activeCount;
  if (elAvgKwh && count > 0) {
    elAvgKwh.textContent = (totalKwh / count).toFixed(4);
  }
}

document.addEventListener("DOMContentLoaded", updateEnergyStats);

console.log("EnergyCosts.js geladen");
