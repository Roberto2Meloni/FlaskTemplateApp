/**
 * Quotes.js – Printly Offerten-Verwaltung
 */

// ============================================================
// QUOTE MODAL (Neue Offerte)
// ============================================================
const QuoteModal = {
  openAdd() {
    $("#quoteModalLabel").text("Neue Offerte");
    $("#quoteForm")[0].reset();
    $("#formQuoteId").val("");
    $("#formQuoteMargin").val(30);
    $("#quoteModal").modal("show");
  },
  openEditProfiles(quoteId) {
    if (QuoteModal._editProfilesOpen) return;
    QuoteModal._editProfilesOpen = true;
    setTimeout(() => {
      QuoteModal._editProfilesOpen = false;
    }, 500);

    $("#quoteModalLabel").text("Globale Profile bearbeiten");
    $("#formQuoteId").val(quoteId);

    fetch(`/Printly/api/quotes/${quoteId}`, {
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then((r) => r.json())
      .then((data) => {
        const q = data.quote;
        $("#formQuoteTitle").val(q.title);
        $("#formQuoteMargin").val(q.margin_percentage);
        $("#formQuoteNotes").val(q.notes || "");

        const setSelect = (id, val) => {
          $(`#${id} option`).each(function () {
            $(this).prop("selected", $(this).val() === String(val || ""));
          });
        };
        setSelect("formQuoteCompany", q.company_id);
        setSelect("formQuoteCustomer", q.customer_id);
        setSelect("formQuotePrinter", q.global_printer_id);
        setSelect("formQuoteWorkHours", q.global_work_hours_id);
        setSelect("formQuoteOverhead", q.global_overhead_profile_id);
        setSelect("formQuoteDiscount", q.discount_profile_id);

        $("#quoteModal").modal("show");
      })
      .catch((err) => {
        console.error("Fehler:", err);
      });
  },

  onCompanyChange() {
    const companyId = $("#formQuoteCompany").val();
    // Kontaktpersonen filtern
    $("#formQuoteCustomer option").each(function () {
      const optCompany = $(this).data("company");
      if (
        !companyId ||
        !optCompany ||
        String(optCompany) === String(companyId)
      ) {
        $(this).show();
      } else {
        $(this).hide();
      }
    });
    $("#formQuoteCustomer").val("");
  },

  delete(quoteId, quoteNumber) {
    if (!confirm(`Offerte "${quoteNumber}" wirklich löschen?`)) return;
    const url = APP_URLS.api_quote_delete.replace("/0", `/${quoteId}`);
    fetch(url, {
      method: "DELETE",
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then((r) => r.json())
      .then((data) => {
        console.log("Data:", data);
        const q = data.quote;
        $("#formQuoteTitle").val(q.title);
        $("#formQuoteMargin").val(q.margin_percentage);

        const setSelect = (id, val) => {
          $(`#${id} option`).each(function () {
            $(this).prop("selected", $(this).val() === String(val || ""));
          });
        };
        setSelect("formQuotePrinter", q.global_printer_id);
        setSelect("formQuoteWorkHours", q.global_work_hours_id);
        setSelect("formQuoteOverhead", q.global_overhead_profile_id);
        setSelect("formQuoteDiscount", q.discount_profile_id);

        $("#quoteModal").modal("show"); // ← am Ende!
      });
  },
  submit(event) {
    event.preventDefault();

    const payload = {
      title: $("#formQuoteTitle").val(),
      company_id: $("#formQuoteCompany").val()
        ? parseInt($("#formQuoteCompany").val())
        : null,
      customer_id: $("#formQuoteCustomer").val()
        ? parseInt($("#formQuoteCustomer").val())
        : null,
      global_printer_id: $("#formQuotePrinter").val()
        ? parseInt($("#formQuotePrinter").val())
        : null,
      global_work_hours_id: $("#formQuoteWorkHours").val()
        ? parseInt($("#formQuoteWorkHours").val())
        : null,
      global_overhead_profile_id: $("#formQuoteOverhead").val()
        ? parseInt($("#formQuoteOverhead").val())
        : null,
      discount_profile_id: $("#formQuoteDiscount").val()
        ? parseInt($("#formQuoteDiscount").val())
        : null,
      margin_percentage: parseFloat($("#formQuoteMargin").val()) || 30,
      valid_until: $("#formQuoteValidUntil").val() || null,
      notes: $("#formQuoteNotes").val() || null,
    };

    fetch(APP_URLS.api_quotes, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify(payload),
    })
      .then((r) => r.json())
      .then((data) => {
        // console.log("Response:", data); // ← temporär
        if (data.success) {
          //   console.log("Quote ID:", data.quote.id);
          //   console.log(
          //     "Redirect:",
          //     APP_URLS.quote_detail.replace("/0", `/${data.quote.id}`),
          //   );
          $("#quoteModal").modal("hide");
          window.location.href = APP_URLS.quote_detail.replace(
            "/0",
            `/${data.quote.id}`,
          );
        } else {
          alert("Fehler: " + (data.error || "Unbekannter Fehler"));
        }
      });
  },
};

// ============================================================
// QUOTE DETAIL
// ============================================================
const QuoteDetail = {
  setStatus(quoteId, status) {
    const labels = {
      sent: "Als gesendet markieren?",
      accepted: "Als angenommen markieren?",
      rejected: "Als abgelehnt markieren?",
      invoiced: "Als verrechnet markieren?",
    };
    if (!confirm(labels[status] || "Status ändern?")) return;

    const url = APP_URLS.api_quote_status.replace("/0", `/${quoteId}`);
    fetch(url, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify({ status }),
    })
      .then((r) => r.json())
      .then((data) => {
        if (data.success) window.location.reload();
        else alert("Fehler: " + (data.error || "Unbekannter Fehler"));
      });
  },

  editTitle(el) {
    const current = el.textContent.trim();
    const quoteId = el.closest("[data-quote-id]").dataset.quoteId;

    el.contentEditable = "true";
    el.focus();

    const range = document.createRange();
    range.selectNodeContents(el);
    range.collapse(false);
    window.getSelection().removeAllRanges();
    window.getSelection().addRange(range);

    el.style.outline = "2px solid var(--color-active-background)";
    el.style.borderRadius = "4px";
    el.style.padding = "2px 6px";

    el.onkeydown = function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        el.blur();
      }
      if (e.key === "Escape") {
        el.textContent = current;
        el.blur();
      }
    };

    el.onblur = function () {
      el.contentEditable = "false";
      el.style.outline = "";
      el.style.padding = "";
      const newTitle = el.textContent.trim();
      if (newTitle && newTitle !== current) {
        QuoteDetail.saveTitle(quoteId, newTitle, el, current);
      }
    };
  },

  saveTitle(quoteId, newTitle, el, oldTitle) {
    const url = APP_URLS.api_quote_update.replace("/0", `/${quoteId}`);
    fetch(url, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify({ title: newTitle }),
    })
      .then((r) => r.json())
      .then((data) => {
        if (!data.success) {
          el.textContent = oldTitle;
          alert("Fehler: " + (data.error || "Unbekannt"));
        }
      })
      .catch(() => {
        el.textContent = oldTitle;
      });
  },
};

// ============================================================
// SUBORDER MODAL
// ============================================================
const SuborderModal = {
  openAdd(quoteId) {
    $("#suborderModalLabel").text("Neues Druckbett");
    $("#suborderForm")[0].reset();
    $("#formSubId").val("");
    $("#formSubQuoteId").val(quoteId);
    $("#formSubQty").val(1);
    $("#suborderModal").modal("show");
  },

  openEdit(dataset, quoteId) {
    $("#suborderModalLabel").text("Druckbett bearbeiten");
    $("#suborderForm")[0].reset();
    $("#formSubId").val(dataset.id || "");
    $("#formSubQuoteId").val(quoteId);
    $("#formSubName").val(dataset.name || "");
    $("#formSubQty").val(dataset.qty || 1);
    $("#formSubGrams").val(dataset.grams || "");
    $("#formSubPrintTime").val(formatTimeInput(dataset.printTime));
    $("#formSubWorkTime").val(formatTimeInput(dataset.workTime));
    $("#formSubMargin").val(dataset.margin || "");

    // Selects setzen
    const setSelect = (id, val) => {
      $(`#${id} option`).each(function () {
        $(this).prop("selected", $(this).val() === String(val || ""));
      });
    };
    setSelect("formSubFilament", dataset.filamentId);
    setSelect("formSubPrinter", dataset.printerId);
    setSelect("formSubWorkHours", dataset.workHoursId);
    setSelect("formSubOverhead", dataset.overheadId);

    $("#suborderModal").modal("show");
  },

  delete(quoteId, subId, subName) {
    if (!confirm(`Druckbett "${subName}" wirklich löschen?`)) return;
    const url = APP_URLS.api_suborder_delete
      .replace("quote_id=0", `quote_id=${quoteId}`)
      .replace("sub_id=0", `sub_id=${subId}`);

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

  submit(event) {
    event.preventDefault();
    const subId = $("#formSubId").val();
    const quoteId = $("#formSubQuoteId").val();
    const isEdit = !!subId;
    // console.log("subId:", subId, "quoteId:", quoteId);

    const payload = {
      name: $("#formSubName").val(),
      quantity: parseInt($("#formSubQty").val()) || 1,
      filament_id: $("#formSubFilament").val()
        ? parseInt($("#formSubFilament").val())
        : null,
      filament_usage_grams: parseFloat($("#formSubGrams").val()) || 0,
      print_time_hours: parseTimeInput($("#formSubPrintTime").val()),
      work_time_hours: parseTimeInput($("#formSubWorkTime").val()),
      printer_id: $("#formSubPrinter").val()
        ? parseInt($("#formSubPrinter").val())
        : null,
      work_hours_id: $("#formSubWorkHours").val()
        ? parseInt($("#formSubWorkHours").val())
        : null,
      overhead_profile_id: $("#formSubOverhead").val()
        ? parseInt($("#formSubOverhead").val())
        : null,
      margin_percentage: $("#formSubMargin").val()
        ? parseFloat($("#formSubMargin").val())
        : null,
    };

    let url, method;
    if (isEdit) {
      url = APP_URLS.api_suborder_update
        .replace("/0/suborders/", `/${quoteId}/suborders/`)
        .replace("/suborders/0", `/suborders/${subId}`);
      method = "PUT";
    } else {
      url = APP_URLS.api_suborders.replace("/0/", `/${quoteId}/`);
      method = "POST";
    }

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
          $("#suborderModal").modal("hide");
          window.location.reload();
        } else {
          alert("Fehler: " + (data.error || "Unbekannter Fehler"));
        }
      });
  },
};

// ============================================================
// EXTRA MATERIAL MODAL
// ============================================================
const ExtraModal = {
  openAdd(quoteId) {
    $("#extraModalLabel").text("Zusatzmaterial hinzufügen");
    $("#extraForm")[0].reset();
    $("#formExtraId").val("");
    $("#formExtraQuoteId").val(quoteId);
    $("#formExtraQty").val(1);
    $("#extraModal").modal("show");
  },

  openEdit(dataset, quoteId) {
    $("#extraModalLabel").text("Zusatzmaterial bearbeiten");
    $("#extraForm")[0].reset();
    $("#formExtraId").val(dataset.id || "");
    $("#formExtraQuoteId").val(quoteId);
    $("#formExtraName").val(dataset.name || "");
    $("#formExtraQty").val(dataset.qty || 1);
    $("#formExtraPrice").val(dataset.price || "");
    $("#formExtraNotes").val(dataset.notes || "");
    $("#extraModal").modal("show");
  },

  delete(quoteId, extraId, extraName) {
    if (!confirm(`"${extraName}" wirklich löschen?`)) return;
    const url = APP_URLS.api_extra_delete
      .replace("quote_id=0", `quote_id=${quoteId}`)
      .replace("extra_id=0", `extra_id=${extraId}`);

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

  submit(event) {
    event.preventDefault();
    const extraId = $("#formExtraId").val();
    const quoteId = $("#formExtraQuoteId").val();
    const isEdit = !!extraId;

    const payload = {
      name: $("#formExtraName").val(),
      quantity: parseInt($("#formExtraQty").val()) || 1,
      unit_price: parseFloat($("#formExtraPrice").val()) || 0,
      notes: $("#formExtraNotes").val() || null,
    };

    let url, method;
    if (isEdit) {
      url = APP_URLS.api_extra_update
        .replace("quote_id=0", `quote_id=${quoteId}`)
        .replace("extra_id=0", `extra_id=${extraId}`);
      method = "PUT";
    } else {
      url = APP_URLS.api_extras.replace("quote_id=0", `quote_id=${quoteId}`);
      method = "POST";
    }

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
          $("#extraModal").modal("hide");
          window.location.reload();
        } else {
          alert("Fehler: " + (data.error || "Unbekannter Fehler"));
        }
      });
  },
};

// Hilfsfunktion: "5:16" → 5.2667
function parseTimeInput(value) {
  if (!value) return 0;
  value = value.trim();
  if (value.includes(":")) {
    const parts = value.split(":");
    const hours = parseInt(parts[0]) || 0;
    const minutes = parseInt(parts[1]) || 0;
    return round4(hours + minutes / 60);
  }
  return parseFloat(value) || 0;
}

// Hilfsfunktion: 5.2667 → "5:16"
function formatTimeInput(hours) {
  if (!hours) return "";
  const h = Math.floor(hours);
  const m = Math.round((hours - h) * 60);
  return `${h}:${String(m).padStart(2, "0")}`;
}

function round4(val) {
  return Math.round(val * 10000) / 10000;
}

console.log("Quotes.js geladen");
