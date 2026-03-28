/**
 * OverheadProfiles.js – Printly Overhead-Verwaltung
 */

const OverheadModal = {
  openAdd() {
    $("#overheadModalLabel").text("Neues Profil");
    $("#overheadForm")[0].reset();
    $("#formOverheadId").val("");
    $("#formOverheadIsActive").prop("checked", true);
    // Standardwerte setzen
    $(
      "#formRent, #formElectricity, #formInsurance, #formInternet, #formSoftwareCost, #formOtherCosts",
    ).val("0");
    $("#formPlannedHours").val("100");
    $("#formSoftwareBilling").val("monthly");
    $("#overheadTotalPreview").hide();
    $("#overheadPerHourPreview").text("–");
    $("#overheadModal").modal("show");
  },

  openEdit(dataset) {
    $("#overheadModalLabel").text("Profil bearbeiten");
    $("#overheadForm")[0].reset();
    $("#formOverheadId").val(dataset.id || "");
    $("#formOverheadName").val(dataset.name || "");
    $("#formLocation").val(dataset.location || "");
    $("#formRent").val(dataset.rent || "0");
    $("#formElectricity").val(dataset.electricity || "0");
    $("#formInsurance").val(dataset.insurance || "0");
    $("#formInternet").val(dataset.internet || "0");
    $("#formSoftwareCost").val(dataset.softwareCost || "0");
    $("#formSoftwareBilling").val(dataset.softwareBilling || "monthly");
    $("#formOtherCosts").val(dataset.otherCosts || "0");
    $("#formPlannedHours").val(dataset.plannedHours || "100");
    $("#formOverheadIsActive").prop("checked", dataset.isActive === "true");
    $("#formOverheadNotes").val(dataset.notes || "");

    OverheadModal._updatePreview();
    $("#overheadModal").modal("show");
  },

  toggle(profileId, profileName) {
    const url = APP_URLS.api_overhead_profile_toggle.replace(
      "/0",
      `/${profileId}`,
    );
    fetch(url, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
    })
      .then((r) => r.json())
      .then((data) => {
        if (data.success) window.location.reload();
        else alert("Fehler: " + (data.error || "Unbekannter Fehler"));
      });
  },

  delete(profileId, profileName) {
    if (!confirm(`Profil "${profileName}" wirklich löschen?`)) return;
    const url = APP_URLS.api_overhead_profile_delete.replace(
      "/0",
      `/${profileId}`,
    );
    fetch(url, {
      method: "DELETE",
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then((r) => r.json())
      .then((data) => {
        if (data.success) window.location.reload();
        else alert("Fehler: " + (data.error || "Unbekannter Fehler"));
      });
  },

  linkPrinter(profileId) {
    const printerId = $(`#printerSelect_${profileId}`).val();
    const isDefault = $(`#isDefault_${profileId}`).is(":checked");

    if (!printerId) {
      alert("Bitte einen Drucker wählen.");
      return;
    }

    const url = APP_URLS.api_overhead_link_printer.replace(
      "/0",
      `/${profileId}`,
    );
    fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify({
        printer_id: parseInt(printerId),
        is_default: isDefault,
      }),
    })
      .then((r) => r.json())
      .then((data) => {
        if (data.success) window.location.reload();
        else alert("Fehler: " + (data.error || "Unbekannter Fehler"));
      });
  },

  unlinkPrinter(profileId, printerId, printerName) {
    if (!confirm(`Verknüpfung mit "${printerName}" entfernen?`)) return;

    const url = APP_URLS.api_overhead_unlink_printer.replace(
      "/0",
      `/${profileId}`,
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
      });
  },

  submit(event) {
    event.preventDefault();
    const id = $("#formOverheadId").val();
    const isEdit = !!id;

    const softwareCost = parseFloat($("#formSoftwareCost").val()) || 0;
    const softwareBilling = $("#formSoftwareBilling").val();
    const softwareCostMonthly =
      softwareBilling === "yearly" ? softwareCost / 12 : softwareCost;

    const payload = {
      name: $("#formOverheadName").val(),
      location: $("#formLocation").val() || null,
      rent_monthly: parseFloat($("#formRent").val()) || 0,
      electricity_monthly: parseFloat($("#formElectricity").val()) || 0,
      insurance: parseFloat($("#formInsurance").val()) || 0,
      internet: parseFloat($("#formInternet").val()) || 0,
      software_cost: softwareCost,
      software_billing: softwareBilling,
      other_costs: parseFloat($("#formOtherCosts").val()) || 0,
      planned_hours_monthly: parseInt($("#formPlannedHours").val()) || 100,
      is_active: $("#formOverheadIsActive").is(":checked"),
      notes: $("#formOverheadNotes").val() || null,
    };

    const url = isEdit
      ? APP_URLS.api_overhead_profile_update.replace("/0", `/${id}`)
      : APP_URLS.api_overhead_profiles;
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
          $("#overheadModal").modal("hide");
          window.location.reload();
        } else {
          alert("Fehler: " + (data.error || "Unbekannter Fehler"));
        }
      });
  },

  // ----------------------------------------------------------
  // LIVE PREVIEW
  // ----------------------------------------------------------
  _updatePreview() {
    const rent = parseFloat($("#formRent").val()) || 0;
    const insurance = parseFloat($("#formInsurance").val()) || 0;
    const internet = parseFloat($("#formInternet").val()) || 0;
    const softwareCost = parseFloat($("#formSoftwareCost").val()) || 0;
    const softwareBilling = $("#formSoftwareBilling").val();
    const otherCosts = parseFloat($("#formOtherCosts").val()) || 0;
    const plannedHours = parseInt($("#formPlannedHours").val()) || 0;

    const softwareMonthly =
      softwareBilling === "yearly" ? softwareCost / 12 : softwareCost;
    const total = rent + insurance + internet + softwareMonthly + otherCosts;
    const perHour = plannedHours > 0 ? total / plannedHours : 0;

    if (total > 0) {
      $("#previewTotal").text(total.toFixed(2) + " CHF");
      $("#previewPerHour").text(perHour.toFixed(4) + " CHF/h");
      $("#overheadPerHourPreview").text(perHour.toFixed(4) + " CHF/h");
      $("#overheadTotalPreview").show();
    } else {
      $("#overheadTotalPreview").hide();
      $("#overheadPerHourPreview").text("–");
    }
  },
};

// Live Preview bei Eingabe
$(document).on("input change", ".overhead-calc-input", function () {
  OverheadModal._updatePreview();
});

// ============================================================
// STATS
// ============================================================
function updateOverheadStats() {
  const cards = document.querySelectorAll(".overhead-card--active");
  let totalPerHour = 0;
  let count = 0;

  cards.forEach((card) => {
    const btn = card.querySelector(".btn-edit");
    if (!btn) return;
    // overhead_per_hour aus data berechnen wäre komplex – vereinfacht via DOM
    count++;
  });

  // Ø aus allen sichtbaren CHF/h Werten
  const rateEls = document.querySelectorAll(
    ".overhead-card--active .overhead-card__per-hour",
  );
  rateEls.forEach((el) => {
    const val = parseFloat(el.textContent);
    if (!isNaN(val)) totalPerHour += val;
  });

  const elAvg = document.getElementById("statAvgOverhead");
  if (elAvg && rateEls.length > 0) {
    elAvg.textContent = (totalPerHour / rateEls.length).toFixed(4);
  }
}

document.addEventListener("DOMContentLoaded", updateOverheadStats);

console.log("OverheadProfiles.js geladen");
