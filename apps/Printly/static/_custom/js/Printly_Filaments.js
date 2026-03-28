/**
 * Filaments.js – Printly Filament-Verwaltung
 */

const FilamentModal = {
  openAdd() {
    $("#filamentModalLabel").text("Neues Filament");
    $("#filamentForm")[0].reset();
    $("#formFilamentId").val("");
    $("#pricePreview").hide();
    $("#formColorFromName").prop("checked", true); // ← NEU
    $("#formColor").prop("readonly", true); // ← NEU
    $("#filamentModal").modal("show");
  },
  openEdit(dataset) {
    $("#filamentModalLabel").text("Filament bearbeiten");
    $("#filamentForm")[0].reset();
    $("#formFilamentId").val(dataset.id || "");
    $("#formFilamentName").val(dataset.name || "");
    $("#formWeight").val(dataset.weight || "");
    $("#formPrice").val(dataset.price || "");
    $("#formFilamentNotes").val(dataset.notes || "");

    // Farbe-Haken: aktiv wenn keine manuelle Farbe gesetzt
    const hasManualColor = !!dataset.color;
    $("#formColorFromName").prop("checked", !hasManualColor);
    $("#formColor").prop("readonly", !hasManualColor);
    $("#formColor").val(dataset.color || "");

    // Typ setzen
    $("#formType option").each(function () {
      $(this).prop("selected", $(this).val() === dataset.type);
    });

    // Hersteller setzen
    $("#formManufacturer option").each(function () {
      $(this).prop("selected", $(this).val() === dataset.manufacturer);
    });

    // Durchmesser setzen
    $("#formDiameter option").each(function () {
      $(this).prop("selected", $(this).val() === dataset.diameter);
    });

    FilamentModal._updatePricePreview();
    $("#filamentModal").modal("show");
  },

  archive(filamentId, filamentName) {
    const url = APP_URLS.api_filament_archive.replace("/0", `/${filamentId}`);

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
          console.log(`[Filaments] '${filamentName}' wurde ${action}`);
          window.location.reload();
        } else {
          alert("Fehler: " + (data.error || "Unbekannter Fehler"));
        }
      })
      .catch((err) => {
        console.error("[FilamentModal] Fehler:", err);
        alert("Verbindungsfehler – bitte nochmals versuchen.");
      });
  },

  submit(event) {
    event.preventDefault();
    const id = $("#formFilamentId").val();
    const isEdit = !!id;

    // Farbe aus Name extrahieren falls Haken gesetzt
    let color = $("#formColor").val() || null;
    if ($("#formColorFromName").is(":checked")) {
      color = FilamentModal._extractColorFromName($("#formFilamentName").val());
    }

    const payload = {
      filament_type: $("#formType").val(),
      name: $("#formFilamentName").val(),
      color: color,
      manufacturer: $("#formManufacturer").val(),
      diameter: parseFloat($("#formDiameter").val()),
      weight: parseInt($("#formWeight").val()),
      price: parseFloat($("#formPrice").val()),
      notes: $("#formFilamentNotes").val() || null,
    };

    const url = isEdit
      ? APP_URLS.api_filament_update.replace("/0", `/${id}`)
      : APP_URLS.api_filaments;
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
          $("#filamentModal").modal("hide");
          window.location.reload();
        } else {
          alert("Fehler: " + (data.error || "Unbekannter Fehler"));
        }
      })
      .catch((err) => {
        console.error("[FilamentModal] Fehler:", err);
        alert("Verbindungsfehler – bitte nochmals versuchen.");
      });
  },

  // ----------------------------------------------------------
  // HILFSFUNKTIONEN
  // ----------------------------------------------------------

  _extractColorFromName(name) {
    // Entfernt den Typ-Prefix (z.B. "PLA ") und gibt den Rest zurück
    const types = [
      "PLA",
      "PETG",
      "TPU",
      "ABS",
      "ASA",
      "WOOD",
      "CARBON",
      "NYLON",
    ];
    let color = name.trim();
    types.forEach((type) => {
      if (color.toUpperCase().startsWith(type)) {
        color = color.substring(type.length).trim();
      }
    });
    return color || null;
  },

  _updatePricePreview() {
    const weight = parseFloat($("#formWeight").val());
    const price = parseFloat($("#formPrice").val());

    if (weight > 0 && price > 0) {
      const perKg = ((price / weight) * 1000).toFixed(2);
      const perGram = (price / weight).toFixed(4);
      $("#previewPerKg").text(perKg);
      $("#previewPerGram").text(perGram);
      $("#pricePreview").show();
    } else {
      $("#pricePreview").hide();
    }
  },
};

// Preis-Preview live aktualisieren
$(document).on("input", "#formWeight, #formPrice", function () {
  FilamentModal._updatePricePreview();
});

// Farbe aus Name übernehmen – live
$(document).on("input", "#formFilamentName", function () {
  if ($("#formColorFromName").is(":checked")) {
    const color = FilamentModal._extractColorFromName($(this).val());
    $("#formColor").val(color || "");
  }
});

$(document).on("change", "#formColorFromName", function () {
  if ($(this).is(":checked")) {
    const color = FilamentModal._extractColorFromName(
      $("#formFilamentName").val(),
    );
    $("#formColor").val(color || "");
    $("#formColor").prop("readonly", true);
  } else {
    $("#formColor").prop("readonly", false);
  }
});

// ============================================================
// STATS
// ============================================================
function updateFilamentStats() {
  const cards = document.querySelectorAll(
    ".filaments-grid:not(.filaments-grid--graveyard) .filament-card",
  );
  const total = cards.length;

  const elTotal = document.getElementById("statTotal");
  const elManufacturers = document.getElementById("statManufacturers");
  const elAvgPrice = document.getElementById("statAvgPrice");

  if (elTotal) elTotal.textContent = total;

  if (total === 0) {
    if (elManufacturers) elManufacturers.textContent = "0";
    if (elAvgPrice) elAvgPrice.textContent = "0.00";
    return;
  }

  const manufacturers = new Set();
  let totalPricePerKg = 0;
  let count = 0;

  cards.forEach((card) => {
    const btn = card.querySelector(".btn-edit");
    if (!btn) return;

    const manufacturer = card
      .querySelector(".filament-card__manufacturer")
      ?.textContent.trim();
    if (manufacturer) manufacturers.add(manufacturer);

    const weight = parseFloat(btn.dataset.weight);
    const price = parseFloat(btn.dataset.price);
    if (weight > 0 && price > 0) {
      totalPricePerKg += (price / weight) * 1000;
      count++;
    }
  });

  if (elManufacturers) elManufacturers.textContent = manufacturers.size;
  if (elAvgPrice && count > 0) {
    elAvgPrice.textContent = (totalPricePerKg / count).toFixed(2);
  }
}

document.addEventListener("DOMContentLoaded", updateFilamentStats);

console.log("Filaments.js geladen");
