/**
 * Customers.js v2 – Printly Kundenverwaltung
 * Firma → Kontakte Struktur
 */

// ============================================================
// FIRMA MODAL
// ============================================================
const CompanyModal = {
  openAdd() {
    $("#companyModalLabel").text("Neue Firma");
    $("#companyForm")[0].reset();
    $("#formCompanyId").val("");
    $("#formCompanyCountry").val("CH");
    $("#companyModal").modal("show");
  },

  openEdit(dataset) {
    $("#companyModalLabel").text("Firma bearbeiten");
    $("#companyForm")[0].reset();
    $("#formCompanyId").val(dataset.id || "");
    $("#formCompanyName").val(dataset.companyName || "");
    $("#formCompanyEmail").val(dataset.email || "");
    $("#formCompanyPhone").val(dataset.phone || "");
    $("#formCompanyWebsite").val(dataset.website || "");
    $("#formCompanyAddress").val(dataset.address || "");
    $("#formCompanyZip").val(dataset.zip || "");
    $("#formCompanyCity").val(dataset.city || "");
    $("#formCompanyCountry").val(dataset.country || "CH");
    $("#formCompanyNotes").val(dataset.notes || "");

    $("#formCompanyDiscount option").each(function () {
      $(this).prop("selected", $(this).val() === dataset.discountId);
    });

    $("#companyModal").modal("show");
  },

  toggle(companyId, companyName) {
    const url = APP_URLS.api_company_toggle.replace("/0", `/${companyId}`);
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

  delete(companyId, companyName) {
    if (
      !confirm(
        `Firma "${companyName}" wirklich löschen?\nAlle Kontaktpersonen werden ebenfalls gelöscht.`,
      )
    )
      return;
    const url = APP_URLS.api_company_delete.replace("/0", `/${companyId}`);
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
    const id = $("#formCompanyId").val();
    const isEdit = !!id;

    const payload = {
      company_name: $("#formCompanyName").val(),
      email: $("#formCompanyEmail").val() || null,
      phone: $("#formCompanyPhone").val() || null,
      website: $("#formCompanyWebsite").val() || null,
      address: $("#formCompanyAddress").val() || null,
      zip_code: $("#formCompanyZip").val() || null,
      city: $("#formCompanyCity").val() || null,
      country: $("#formCompanyCountry").val() || "CH",
      discount_profile_id: $("#formCompanyDiscount").val()
        ? parseInt($("#formCompanyDiscount").val())
        : null,
      notes: $("#formCompanyNotes").val() || null,
    };

    const url = isEdit
      ? APP_URLS.api_company_update.replace("/0", `/${id}`)
      : APP_URLS.api_companies;
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
          $("#companyModal").modal("hide");
          window.location.reload();
        } else {
          alert("Fehler: " + (data.error || "Unbekannter Fehler"));
        }
      });
  },
};

// ============================================================
// KUNDEN / KONTAKT MODAL
// ============================================================
const CustomerModal = {
  // Privatkunde (kein companyId)
  openAdd(companyId = null) {
    $("#customerModalLabel").text(
      companyId ? "Kontaktperson hinzufügen" : "Neuer Privatkunde",
    );
    $("#customerForm")[0].reset();
    $("#formCustomerId").val("");
    $("#formCustomerCompanyId").val(companyId || "");
    $("#formCustomerCountry").val("CH");
    $("#formCustomerIsPrimary").prop("checked", false);

    if (companyId) {
      // Firmenkontakt – Adressfelder ausblenden, Rollenfelder einblenden
      const companyName = $(
        `[data-id="${companyId}"] .customer-card__name`,
      ).text();
      $("#companyBadgeName").text(companyName);
      $("#companyBadge").show();
      $("#contactFields").show();
      $("#addressFields").hide();
    } else {
      $("#companyBadge").hide();
      $("#contactFields").hide();
      $("#addressFields").show();
    }

    $("#customerModal").modal("show");
  },

  openEdit(dataset) {
    const isContact = !!dataset.companyId;
    $("#customerModalLabel").text(
      isContact ? "Kontaktperson bearbeiten" : "Kunde bearbeiten",
    );
    $("#customerForm")[0].reset();
    $("#formCustomerId").val(dataset.id || "");
    $("#formCustomerCompanyId").val(dataset.companyId || "");
    $("#formCustomerFirstName").val(dataset.firstName || "");
    $("#formCustomerLastName").val(dataset.lastName || "");
    $("#formCustomerEmail").val(dataset.email || "");
    $("#formCustomerPhone").val(dataset.phone || "");
    $("#formCustomerRole").val(dataset.role || "");
    $("#formCustomerIsPrimary").prop("checked", dataset.isPrimary === "true");
    $("#formCustomerAddress").val(dataset.address || "");
    $("#formCustomerZip").val(dataset.zip || "");
    $("#formCustomerCity").val(dataset.city || "");
    $("#formCustomerCountry").val(dataset.country || "CH");
    $("#formCustomerNotes").val(dataset.notes || "");

    $("#formCustomerDiscount option").each(function () {
      $(this).prop("selected", $(this).val() === dataset.discountId);
    });

    if (isContact) {
      $("#companyBadge").show();
      $("#contactFields").show();
      $("#addressFields").hide();
    } else {
      $("#companyBadge").hide();
      $("#contactFields").hide();
      $("#addressFields").show();
    }

    $("#customerModal").modal("show");
  },

  toggle(customerId, customerName) {
    const url = APP_URLS.api_customer_toggle.replace("/0", `/${customerId}`);
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

  delete(customerId, customerName) {
    if (!confirm(`"${customerName}" wirklich löschen?`)) return;
    const url = APP_URLS.api_customer_delete.replace("/0", `/${customerId}`);
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
    const id = $("#formCustomerId").val();
    const isEdit = !!id;
    const companyId = $("#formCustomerCompanyId").val();

    const payload = {
      company_id: companyId ? parseInt(companyId) : null,
      first_name: $("#formCustomerFirstName").val(),
      last_name: $("#formCustomerLastName").val(),
      role: $("#formCustomerRole").val() || null,
      is_primary: $("#formCustomerIsPrimary").is(":checked"),
      email: $("#formCustomerEmail").val() || null,
      phone: $("#formCustomerPhone").val() || null,
      address: companyId ? null : $("#formCustomerAddress").val() || null,
      zip_code: companyId ? null : $("#formCustomerZip").val() || null,
      city: companyId ? null : $("#formCustomerCity").val() || null,
      country: companyId ? "CH" : $("#formCustomerCountry").val() || "CH",
      discount_profile_id: $("#formCustomerDiscount").val()
        ? parseInt($("#formCustomerDiscount").val())
        : null,
      notes: $("#formCustomerNotes").val() || null,
    };

    const url = isEdit
      ? APP_URLS.api_customer_update.replace("/0", `/${id}`)
      : APP_URLS.api_customers;
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
          $("#customerModal").modal("hide");
          window.location.reload();
        } else {
          alert("Fehler: " + (data.error || "Unbekannter Fehler"));
        }
      });
  },
};

console.log("Customers.js v2 geladen");
