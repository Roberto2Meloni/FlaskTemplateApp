// BasicChat.js - KORRIGIERTE VERSION mit Benutzerinformationen
console.log("Socket IO JS geladen");

// === GLOBALE VARIABLEN ===
let socket = null;
let isConnected = false;
let currentChatRoom = null;

// === SOCKET.IO INTEGRATION ===
function initializeSocketIO() {
  if (typeof io === "undefined") {
    console.error("❌ Socket.IO nicht verfügbar!");
    return;
  }

  console.log("🔌 Initialisiere Socket.IO...");
  try {
    socket = io();
    setupSocketEvents();
  } catch (error) {
    console.error("❌ Socket.IO Fehler:", error);
  }
}

function setupSocketEvents() {
  // === BASIS VERBINDUNGS-EVENTS ===
  socket.on("connect", () => {
    console.log("✅ Socket.IO verbunden!");
    isConnected = true;
  });

  socket.on("disconnect", () => {
    console.log("❌ Socket.IO getrennt");
    isConnected = false;
    currentChatRoom = null;
    currentChatInfo = null; // ✅ NEU: Chat-Info zurücksetzen
  });

  socket.on("connect_error", (error) => {
    console.error("❌ Verbindungsfehler:", error);
  });
}

// === INITIALISIERUNG ===
document.addEventListener("DOMContentLoaded", function () {
  console.log("🏁 DOM bereit - SocketIO geladen");
  initializeSocketIO();
});
