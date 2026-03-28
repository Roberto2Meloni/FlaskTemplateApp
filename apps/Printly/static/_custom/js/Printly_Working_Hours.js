/**
 * WorkHours.js – Printly Arbeitszeiten-Verwaltung
 */

const WorkHoursModal = {
  openAdd() {
    $("#workHoursModalLabel").text("Neuer Stundensatz");
    $("#workHoursForm")[0].reset();
    $("#formWorkHoursId").val("");
    $("#workHoursPreview").hide();
    $("#workHoursModal").modal("show");
  },

  openEdit(dataset) {
    $("#workHoursModalLabel").text("Stundensatz bearbeiten");
    $("#workHoursForm")[0].reset();
    $("#formWorkHoursId").val(dataset.id || "");
    $("#formWorkHoursName").val(dataset.name || "");
    $("#formCostPerHour").val(dataset.cost || "");
    $("#formWorkHoursNotes").val(dataset.notes || "");

    WorkHoursModal._updatePreview();
    $("#workHoursModal").modal("show");
  },

  archive(rateId, rateName) {
    const url = APP_URLS.api_work_hours_archive.replace("/0", `/${rateId}`);
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
          console.log(`[WorkHours] '${rateName}' wurde ${action}`);
          window.location.reload();
        } else {
          alert("Fehler: " + (data.error || "Unbekannter Fehler"));
        }
      })
      .catch((err) => {
        console.error("[WorkHoursModal] Fehler:", err);
        alert("Verbindungsfehler – bitte nochmals versuchen.");
      });
  },

  delete(rateId, rateName) {
    if (!confirm(`Stundensatz "${rateName}" wirklich löschen?`)) return;

    const url = APP_URLS.api_work_hours_delete.replace("/0", `/${rateId}`);
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
        console.error("[WorkHoursModal] Fehler:", err);
        alert("Verbindungsfehler – bitte nochmals versuchen.");
      });
  },

  submit(event) {
    event.preventDefault();
    const id = $("#formWorkHoursId").val();
    const isEdit = !!id;

    const payload = {
      name: $("#formWorkHoursName").val(),
      cost_per_hour: parseFloat($("#formCostPerHour").val()),
      notes: $("#formWorkHoursNotes").val() || null,
    };

    const url = isEdit
      ? APP_URLS.api_work_hours_update.replace("/0", `/${id}`)
      : APP_URLS.api_work_hours;
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
          $("#workHoursModal").modal("hide");
          window.location.reload();
        } else {
          alert("Fehler: " + (data.error || "Unbekannter Fehler"));
        }
      })
      .catch((err) => {
        console.error("[WorkHoursModal] Fehler:", err);
        alert("Verbindungsfehler – bitte nochmals versuchen.");
      });
  },

  _updatePreview() {
    const cost = parseFloat($("#formCostPerHour").val());
    if (cost > 0) {
      $("#previewDaily").text((cost * 8).toFixed(2) + " CHF");
      $("#previewMonthly").text((cost * 160).toFixed(2) + " CHF");
      $("#workHoursPreview").show();
    } else {
      $("#workHoursPreview").hide();
    }
  },
};

// Live Preview
$(document).on("input", "#formCostPerHour", function () {
  WorkHoursModal._updatePreview();
});

// ============================================================
// STATS
// ============================================================
function updateWorkHoursStats() {
  const cards = document.querySelectorAll(
    ".workhours-grid:not(.workhours-grid--graveyard) .workhours-card",
  );
  const total = cards.length;

  const elTotal = document.getElementById("statTotal");
  const elAvg = document.getElementById("statAvgRate");
  const elMax = document.getElementById("statMaxRate");

  if (elTotal) elTotal.textContent = total;

  if (total === 0) {
    if (elAvg) elAvg.textContent = "0.00";
    if (elMax) elMax.textContent = "0.00";
    return;
  }

  let totalCost = 0;
  let maxCost = 0;

  cards.forEach((card) => {
    const btn = card.querySelector(".btn-edit");
    if (!btn) return;
    const cost = parseFloat(btn.dataset.cost);
    if (cost > 0) {
      totalCost += cost;
      if (cost > maxCost) maxCost = cost;
    }
  });

  if (elAvg) elAvg.textContent = (totalCost / total).toFixed(2);
  if (elMax) elMax.textContent = maxCost.toFixed(2);
}

document.addEventListener("DOMContentLoaded", updateWorkHoursStats);

console.log("WorkHours.js geladen");
