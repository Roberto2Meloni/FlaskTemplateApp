console.log("Template_app_v002.js loaded");

// ========================================
// APP-SPEZIFISCHE SOCKET EVENTS
// Nutzt die globale Socket-Verbindung aus base.js/BasicChat.js
// ========================================

/**
 * Registriert Template_app_v002 spezifische Socket-Events
 * Wird aufgerufen sobald Socket verbunden ist
 */
function setupTemplateAppSocketEvents() {
  // Prüfe ob globale Socket-Verbindung existiert
  if (typeof socket === "undefined" || !socket) {
    console.warn("⚠️ Globale Socket-Verbindung nicht verfügbar");
    return;
  }

  console.log("🔌 Registriere Template_app_v002 Socket-Events");

  // Registriere bei der App für Tracking
  socket.emit("Template_app_v002_connect", {
    timestamp: new Date().toISOString(),
    page: window.location.pathname,
  });

  // Bestätigung vom Server
  socket.on("Template_app_v002_connected", (data) => {
    console.log("✅ Template_app_v002 registriert:", data);
  });

  // Pong Event
  socket.on("Template_app_v002_pong", (data) => {
    console.log("🏓 Template_app_v002 Pong:", data);
  });

  // Optional: Weitere app-spezifische Events
  // socket.on('Template_app_v002_custom_event', (data) => {
  //     console.log('📨 Custom Event:', data);
  // });
}

/**
 * Cleanup beim Verlassen der Seite
 */
function cleanupTemplateAppSocket() {
  if (typeof socket !== "undefined" && socket && socket.connected) {
    socket.emit("Template_app_v002_disconnect");
    console.log("👋 Template_app_v002 Socket cleanup");
  }
}

// ========================================
// INITIALISIERUNG
// ========================================

document.addEventListener("DOMContentLoaded", function () {
  console.log("🏁 Template_app_v002.js initialisiert");

  // Warte kurz bis Socket verbunden ist, dann registriere Events
  if (typeof socket !== "undefined" && socket) {
    if (socket.connected) {
      // Socket bereits verbunden
      setupTemplateAppSocketEvents();
    } else {
      // Warte auf Connect
      socket.once("connect", () => {
        setupTemplateAppSocketEvents();
      });
    }
  } else {
    // Fallback: Warte auf globale Socket-Variable
    let retries = 0;
    const checkInterval = setInterval(() => {
      if (typeof socket !== "undefined" && socket) {
        clearInterval(checkInterval);
        if (socket.connected) {
          setupTemplateAppSocketEvents();
        } else {
          socket.once("connect", setupTemplateAppSocketEvents);
        }
      } else if (retries++ > 10) {
        // Nach 5 Sekunden aufgeben
        clearInterval(checkInterval);
        console.warn("⚠️ Konnte globale Socket-Verbindung nicht finden");
      }
    }, 500);
  }
});

// Cleanup
window.addEventListener("beforeunload", cleanupTemplateAppSocket);
