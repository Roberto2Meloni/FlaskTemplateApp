(function () {
  "use strict";

  // ── Ursprungswerte merken (für Reset) ──────────────────────
  const ORIGINAL = {};
  document.querySelectorAll(".color-swatch").forEach((sw) => {
    ORIGINAL[sw.name] = sw.value;
  });

  // ── Standard-Werte (hardcoded — entsprechen _get_defaults()) ──
  const DEFAULTS = {
    sidebar_bg: "#1e1e1e",
    sidebar_text_inactive: "#ffffff",
    sidebar_hover_bg: "#ffffff",
    sidebar_text_hover: "#333333",
    sidebar_active_bg: "#3498db",
    sidebar_text_active: "#ffffff",
    sidebar_admin_bg: "#fcfcfc",
    sidebar_admin_text: "#333333",
    sidebar_admin_hover_bg: "#f0f0f0",
    sidebar_admin_hover_text: "#111111",
    sidebar_admin_active_bg: "#3498db",
    sidebar_admin_active_text: "#ffffff",
  };

  // ── Hex-Validierung ────────────────────────────────────────
  function isValidHex(v) {
    return /^#[0-9A-Fa-f]{6}$/.test(v);
  }

  // ── Vorschau aktualisieren ─────────────────────────────────
  function applyPreview(values) {
    // Haupt-Sidebar
    const sidebar = document.getElementById("previewSidebar");
    const prevActive = document.getElementById("prev-active");
    const prevInactive = document.getElementById("prev-inactive");
    const prevHover = document.getElementById("prev-hover");

    if (sidebar) {
      sidebar.style.background = values.sidebar_bg;
      const hdr = sidebar.querySelector(".preview-header");
      if (hdr) {
        hdr.style.background = values.sidebar_bg;
        hdr.style.color = values.sidebar_text_inactive;
      }
    }
    if (prevActive) {
      prevActive.style.background = values.sidebar_active_bg;
      prevActive.style.color = values.sidebar_text_active;
    }
    if (prevInactive) {
      prevInactive.style.background = values.sidebar_bg;
      prevInactive.style.color = values.sidebar_text_inactive;
    }
    if (prevHover) {
      prevHover.style.background = values.sidebar_hover_bg;
      prevHover.style.color = values.sidebar_text_hover;
    }

    // Admin-Sidebar
    const adminBar = document.getElementById("previewAdminSidebar");
    const adminHdr = document.getElementById("prev-admin-header");
    const adminActive = document.getElementById("prev-admin-active");
    const adminInactive = document.getElementById("prev-admin-inactive");
    const adminHover = document.getElementById("prev-admin-hover");

    if (adminBar) {
      adminBar.style.background = values.sidebar_admin_bg;
    }
    if (adminHdr) {
      adminHdr.style.background = values.sidebar_admin_bg;
      adminHdr.style.color = values.sidebar_admin_text;
    }
    if (adminActive) {
      adminActive.style.background = values.sidebar_admin_active_bg;
      adminActive.style.color = values.sidebar_admin_active_text;
    }
    if (adminInactive) {
      adminInactive.style.background = values.sidebar_admin_bg;
      adminInactive.style.color = values.sidebar_admin_text;
    }
    if (adminHover) {
      adminHover.style.background = values.sidebar_admin_hover_bg;
      adminHover.style.color = values.sidebar_admin_hover_text;
    }
  }

  // ── Aktuelle Werte aus dem Formular lesen ──────────────────
  function readFormValues() {
    const vals = {};
    document.querySelectorAll(".color-swatch").forEach((sw) => {
      vals[sw.name] = sw.value;
    });
    return vals;
  }

  // ── Color-Swatch ↔ Hex-Textfeld sync ──────────────────────
  document.querySelectorAll(".color-swatch").forEach((swatch) => {
    const hexInput = document.getElementById(swatch.id + "_hex");

    swatch.addEventListener("input", () => {
      if (hexInput) hexInput.value = swatch.value;
      applyPreview(readFormValues());
    });

    if (hexInput) {
      hexInput.addEventListener("input", () => {
        const val = hexInput.value.trim();
        if (isValidHex(val)) {
          hexInput.classList.remove("invalid");
          swatch.value = val;
          applyPreview(readFormValues());
        } else {
          hexInput.classList.add("invalid");
        }
      });

      hexInput.addEventListener("blur", () => {
        let val = hexInput.value.trim();
        if (val && !val.startsWith("#")) val = "#" + val;
        if (isValidHex(val)) {
          hexInput.value = val;
          hexInput.classList.remove("invalid");
          swatch.value = val;
          applyPreview(readFormValues());
        }
      });
    }
  });

  // ── Initiale Vorschau rendern ──────────────────────────────
  applyPreview(readFormValues());

  // ── Speichern ──────────────────────────────────────────────
  window.saveStyle = async function () {
    const btn = document.querySelector("#styleForm .btn-primary");

    let valid = true;
    document.querySelectorAll(".color-hex").forEach((inp) => {
      if (!isValidHex(inp.value.trim())) {
        inp.classList.add("invalid");
        valid = false;
      }
    });
    if (!valid) {
      AppAdmin.showToast(
        "Bitte alle Felder mit gültigen Hex-Farben (#rrggbb) ausfüllen.",
        "error",
      );
      return;
    }

    btn.disabled = true;
    btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Speichern…';

    try {
      const payload = readFormValues();
      const res = await fetch(API_SAVE_STYLE, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({ styling: payload }),
      });

      const data = await res.json();
      if (data.success) {
        AppAdmin.showToast(
          "Farben gespeichert — Sidebar wird live aktualisiert.",
          "success",
        );
        applyCSSVars(payload);
      } else {
        AppAdmin.showToast("Fehler: " + (data.error || "Unbekannt"), "error");
      }
    } catch (e) {
      AppAdmin.showToast("Netzwerkfehler: " + e.message, "error");
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<i class="bi bi-save"></i> Speichern';
    }
  };

  // ── Zurücksetzen ───────────────────────────────────────────
  window.resetStyle = function () {
    document.querySelectorAll(".color-swatch").forEach((sw) => {
      if (ORIGINAL[sw.name]) {
        sw.value = ORIGINAL[sw.name];
        const hex = document.getElementById(sw.id + "_hex");
        if (hex) {
          hex.value = ORIGINAL[sw.name];
          hex.classList.remove("invalid");
        }
      }
    });
    applyPreview(ORIGINAL);
    applyCSSVars(ORIGINAL);
    AppAdmin.showToast(
      "Farben zurückgesetzt — noch nicht gespeichert.",
      "info",
    );
  };

  // ── Auf Standard zurücksetzen ─────────────────────────────
  window.resetToDefaults = function () {
    document.querySelectorAll(".color-swatch").forEach((sw) => {
      const defaultVal = DEFAULTS[sw.name];
      if (defaultVal) {
        sw.value = defaultVal;
        const hex = document.getElementById(sw.id + "_hex");
        if (hex) {
          hex.value = defaultVal;
          hex.classList.remove("invalid");
        }
      }
    });
    applyPreview(DEFAULTS);
    applyCSSVars(DEFAULTS);
    AppAdmin.showToast(
      "Standard-Farben wiederhergestellt — noch nicht gespeichert.",
      "info",
    );
  };

  // ── CSS-Variablen live ins Dokument schreiben ──────────────
  function applyCSSVars(v) {
    const r = document.documentElement.style;
    // Haupt-Sidebar
    r.setProperty("--color-sidbar-background", v.sidebar_bg);
    r.setProperty("--color-sidbar-background-hover", v.sidebar_hover_bg);
    r.setProperty("--color-active-background", v.sidebar_active_bg);
    r.setProperty("--color-text-light", v.sidebar_text_active);
    r.setProperty("--color-text-dark", v.sidebar_text_hover);
    r.setProperty("--color-text-inactive", v.sidebar_text_inactive);
    // Admin-Sidebar
    r.setProperty("--color-sidbar-admin-background", v.sidebar_admin_bg);
    r.setProperty("--color-admin-text", v.sidebar_admin_text);
    r.setProperty("--color-admin-hover-bg", v.sidebar_admin_hover_bg);
    r.setProperty("--color-admin-hover-text", v.sidebar_admin_hover_text);
    r.setProperty("--color-admin-active-bg", v.sidebar_admin_active_bg);
    r.setProperty("--color-admin-active-text", v.sidebar_admin_active_text);
  }
})();
