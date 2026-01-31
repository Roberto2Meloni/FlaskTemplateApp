/**
 * Template_app_v002 - Socket.IO Integration
 * Kombiniert: Globale Socket-Verbindung + App-spezifische Events
 */

(function () {
  "use strict";

  console.log("🔌 Template_app_v002 Socket.IO wird initialisiert");

  // ========================================
  // GLOBALE SOCKET-VERBINDUNG
  // ========================================

  let socket = null;
  let isConnected = false;

  /**
   * Initialisiert globale Socket.IO Verbindung
   */
  function initializeGlobalSocket() {
    if (typeof io === "undefined") {
      console.error("❌ Socket.IO Library nicht verfügbar!");
      return null;
    }

    console.log("🔌 Initialisiere globale Socket.IO Verbindung...");

    try {
      socket = io();

      // Basis Events
      socket.on("connect", () => {
        console.log("✅ Socket.IO verbunden! (SID:", socket.id + ")");
        isConnected = true;

        // Trigger Event für andere Scripts
        document.dispatchEvent(
          new CustomEvent("global-socket-connected", {
            detail: { socket, sid: socket.id },
          }),
        );
      });

      socket.on("disconnect", (reason) => {
        console.log("❌ Socket.IO getrennt:", reason);
        isConnected = false;
      });

      socket.on("connect_error", (error) => {
        console.error("❌ Verbindungsfehler:", error);
      });

      // Mache Socket global verfügbar
      window.socket = socket;
      window.isSocketConnected = () => isConnected;

      return socket;
    } catch (error) {
      console.error("❌ Socket.IO Fehler:", error);
      return null;
    }
  }

  // ========================================
  // APP-SPEZIFISCHE SOCKET INTEGRATION
  // ========================================

  // App-Name aus Meta-Tag oder Attribut
  const APP_NAME =
    document.querySelector('meta[name="app-name"]')?.content ||
    document.querySelector("[data-app-name]")?.dataset.appName ||
    "UnknownApp";

  console.log(`📱 App: ${APP_NAME}`);

  /**
   * Setup app-spezifische Socket Events
   */
  function setupAppSocketEvents(socket) {
    if (!socket) {
      console.warn(`⚠️ ${APP_NAME}: Socket nicht verfügbar`);
      return;
    }

    console.log(`✅ ${APP_NAME}: Registriere Socket-Events`);

    // Dynamische Event-Namen
    const CONNECT_EVENT = `${APP_NAME}_connect`;
    const CONNECTED_EVENT = `${APP_NAME}_connected`;
    const PONG_EVENT = `${APP_NAME}_pong`;
    const DISCONNECT_EVENT = `${APP_NAME}_disconnect`;

    // Registriere bei App
    socket.emit(CONNECT_EVENT, {
      timestamp: new Date().toISOString(),
      page: window.location.pathname,
    });

    // Server-Bestätigung
    socket.on(CONNECTED_EVENT, (data) => {
      console.log(`✅ ${APP_NAME} verbunden:`, data);

      // Custom Event für weitere Initialisierung
      document.dispatchEvent(
        new CustomEvent("app-socket-connected", {
          detail: { appName: APP_NAME, data },
        }),
      );
    });

    // Pong Event
    socket.on(PONG_EVENT, (data) => {
      console.log(`🏓 ${APP_NAME} Pong:`, data);
    });

    // Cleanup Handler
    window.addEventListener("beforeunload", () => {
      if (socket && socket.connected) {
        socket.emit(DISCONNECT_EVENT);
        console.log(`👋 ${APP_NAME}: Socket cleanup`);
      }
    });
  }

  // ========================================
  // HELPER FUNCTIONS
  // ========================================

  /**
   * Warte auf Socket-Verbindung
   */
  function waitForSocketConnection(maxAttempts = 10) {
    return new Promise((resolve, reject) => {
      let attempts = 0;

      function checkConnection() {
        if (socket && socket.connected) {
          resolve(socket);
        } else if (attempts++ < maxAttempts) {
          setTimeout(checkConnection, 500);
        } else {
          reject(new Error("Socket-Verbindung Timeout"));
        }
      }

      checkConnection();
    });
  }

  // ========================================
  // INITIALISIERUNG
  // ========================================

  document.addEventListener("DOMContentLoaded", async function () {
    console.log(`🏁 ${APP_NAME}: Socket Client wird initialisiert`);

    // 1. Initialisiere globalen Socket
    const globalSocket = initializeGlobalSocket();

    if (!globalSocket) {
      console.error("❌ Konnte Socket nicht initialisieren");
      return;
    }

    // 2. Warte auf Verbindung
    try {
      await waitForSocketConnection();
      console.log("✅ Socket verbunden, registriere App-Events");

      // 3. Setup App-spezifische Events
      setupAppSocketEvents(globalSocket);
    } catch (error) {
      console.warn(`⚠️ ${APP_NAME}: ${error.message}`);
    }
  });

  // ========================================
  // GLOBAL EXPORT
  // ========================================

  window.AppSocket = {
    appName: APP_NAME,

    /**
     * Sendet App-spezifisches Event
     */
    emit: (eventName, data) => {
      if (socket && socket.connected) {
        socket.emit(`${APP_NAME}_${eventName}`, data);
        console.log(`📤 ${APP_NAME}_${eventName}:`, data);
      } else {
        console.warn("⚠️ Socket nicht verbunden");
      }
    },

    /**
     * Hört auf App-spezifisches Event
     */
    on: (eventName, callback) => {
      if (socket) {
        socket.on(`${APP_NAME}_${eventName}`, callback);
      }
    },

    /**
     * Sendet Ping
     */
    sendPing: () => {
      if (socket && socket.connected) {
        socket.emit(`${APP_NAME}_ping`);
        console.log("🏓 Ping gesendet");
      } else {
        console.warn("⚠️ Socket nicht verbunden, kann kein Ping senden");
      }
    },

    /**
     * Prüft Verbindungsstatus
     */
    isConnected: () => socket && socket.connected,

    /**
     * Gibt Socket-Instanz zurück
     */
    getSocket: () => socket,
  };

  console.log(`✅ ${APP_NAME} Socket Integration bereit`);
})();
