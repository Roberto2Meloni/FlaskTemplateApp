/**
 * Discounts.js – Printly Rabatte & Aufschläge
 */

const DiscountModal = {
  openAdd() {
    $("#discountModalLabel").text("Neue Preisanpassung");
    $("#discountForm")[0].reset();
    $("#formDiscountId").val("");
    $("#formDiscountType").val("discount");
    $("#formDiscountIsActive").prop("checked", true);
    $("#discountPreview").hide();
    $("#discountModal").modal("show");
  },

  openEdit(dataset) {
    $("#discountModalLabel").text("Preisanpassung bearbeiten");
    $("#discountForm")[0].reset();
    $("#formDiscountId").val(dataset.id || "");
    $("#formDiscountName").val(dataset.name || "");
    $("#formDiscountType").val(dataset.type || "discount");
    $("#formPercentage").val(dataset.percentage || "");
    $("#formDiscountIsActive").prop("checked", dataset.isActive === "true");
    $("#formDiscountNotes").val(dataset.notes || "");

    DiscountModal._updatePreview();
    $("#discountModal").modal("show");
  },

  toggle(profileId, profileName) {
    const url = APP_URLS.api_discount_profile_toggle.replace(
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
    if (!confirm(`"${profileName}" wirklich löschen?`)) return;
    const url = APP_URLS.api_discount_profile_delete.replace(
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

  submit(event) {
    event.preventDefault();
    const id = $("#formDiscountId").val();
    const isEdit = !!id;

    const payload = {
      name: $("#formDiscountName").val(),
      discount_type: $("#formDiscountType").val(),
      percentage: parseFloat($("#formPercentage").val()),
      is_active: $("#formDiscountIsActive").is(":checked"),
      notes: $("#formDiscountNotes").val() || null,
    };

    const url = isEdit
      ? APP_URLS.api_discount_profile_update.replace("/0", `/${id}`)
      : APP_URLS.api_discount_profiles;
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
          $("#discountModal").modal("hide");
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
    const percentage = parseFloat($("#formPercentage").val());
    const type = $("#formDiscountType").val();

    if (percentage > 0) {
      const factor =
        type === "discount" ? 1 - percentage / 100 : 1 + percentage / 100;
      const result = (100 * factor).toFixed(2);
      const sign = type === "discount" ? "-" : "+";

      $("#previewResult").text(`${result} CHF`);
      $("#previewResult").css(
        "color",
        type === "discount" ? "#2E7D32" : "#B71C1C",
      );
      $("#previewFactor").text(`× ${factor.toFixed(4)}`);
      $("#discountPreview").show();
    } else {
      $("#discountPreview").hide();
    }
  },
};

// Live Preview
$(document).on(
  "input change",
  "#formPercentage, #formDiscountType",
  function () {
    DiscountModal._updatePreview();
  },
);

// ============================================================
// STATS werden direkt aus dem Template gezählt – keine JS-Logik nötig
// ============================================================

console.log("Discounts.js geladen");
