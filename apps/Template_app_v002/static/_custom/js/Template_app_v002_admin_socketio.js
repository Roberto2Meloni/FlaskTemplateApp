/**
 * Template_app_v002 - Custom SocketIO Events
 *
 * Test-Integration für eigene Socket-Events
 * Nutzt window.socket aus socketio.js
 *
 * Events:
 *   Client → Server:  "hello"
 *   Server → Client:  "world"
 */

console.log("⚡ Custom SocketIO Events geladen");

// ========================================
// HELPER: Custom Log
// ========================================

function addCustomLogEntry(type, message) {
  const log = document.getElementById("customEventLog");
  if (!log) return;

  const time = new Date().toLocaleTimeString("de-DE");
  const entry = document.createElement("div");
  entry.className = `log-entry log-${type}`;
  entry.innerHTML = `<span class="log-time">${time}</span><span class="log-message">${message}</span>`;
  log.appendChild(entry);
  log.scrollTop = log.scrollHeight;
}

window.clearCustomLog = function () {
  const log = document.getElementById("customEventLog");
  if (!log) return;
  log.innerHTML = `
    <div class="log-entry log-info">
      <span class="log-time">--:--:--</span>
      <span class="log-message">Log gelöscht...</span>
    </div>`;
};

function setCustomStatus(connected, text) {
  const badge = document.getElementById("customEventStatus");
  if (!badge) return;
  badge.className = `status-badge ${connected ? "online" : "offline"}`;
  badge.innerHTML = `<span class="status-dot"></span><span class="status-text">${text}</span>`;
}

// ========================================
// HELLO SENDEN
// ========================================

window.sendHelloEvent = function () {
  const sock = window.socket;

  if (!sock || !sock.connected) {
    addCustomLogEntry("error", "❌ Socket nicht verbunden! Zuerst verbinden.");
    setCustomStatus(false, "Nicht verbunden");
    return;
  }

  addCustomLogEntry("info", "📤 Sende: hello");
  sock.emit("hello");
};

// ========================================
// WORLD EMPFANGEN
// ========================================

function registerCustomEvents() {
  const sock = window.socket;
  if (!sock) {
    // Socket noch nicht bereit → warten
    setTimeout(registerCustomEvents, 300);
    return;
  }

  sock.on("world", (data) => {
    const message = data?.message || JSON.stringify(data);
    addCustomLogEntry("success", `📥 Empfangen: world → "${message}"`);
    setCustomStatus(true, "Antwort erhalten");

    const lastResp = document.getElementById("customLastResponse");
    if (lastResp)
      lastResp.textContent = `Letzte Antwort: ${new Date().toLocaleTimeString("de-DE")}`;
  });

  addCustomLogEntry(
    "success",
    "✅ Custom Events registriert (world listener aktiv)",
  );
  console.log("✅ Custom Socket-Events registriert");
}

// ========================================
// INIT
// ========================================

document.addEventListener("DOMContentLoaded", function () {
  // Warte kurz bis socketio.js fertig initialisiert hat
  setTimeout(registerCustomEvents, 500);
});
