console.log("JS für Calculator integriert!");

// Einfacher Taschenrechner JavaScript
// Für Anfänger - einfach und verständlich

// Variables für den Taschenrechner
let defaultValue = "-?-";
let operator = "";
let previousInput = "";
let show_result = false;
let calc_way = "";
let result = "";

// Beim Laden der Seite
document.addEventListener("DOMContentLoaded", function () {
  clearDisplay();
});

// 1. DISPLAY AKTUALISIEREN
function clearDisplay() {
  const display = document.getElementById("display");
  show_result = false;
  calc_way = defaultValue;
  updateDisplay();
}

function updateDisplay() {
  const display = document.getElementById("display");
  if (show_result) {
    display.value = result;
  } else {
    if (!calc_way) {
      calc_way = defaultValue;
    } else {
      display.value = calc_way;
    }
  }
  console.log("Hier die aktuelle rechnung: " + calc_way);
}

function addChar(char) {
  console.log("addChar");
  console.log(char);
  show_result = false;

  // SO FÜGST DU EIN ZEICHEN HINZU:
  if (calc_way === defaultValue) {
    calc_way = "";
  }
  calc_way += char;
  updateDisplay();
}

function inputOperator(operator) {
  console.log("inputOperator");
  console.log(operator);
  show_result = false;
  // SO FÜGST DU EIN ZEICHEN HINZU:
  calc_way += operator;
  updateDisplay();
}

function deleteLastChar() {
  console.log("deleteLastChar");
  show_result = false;
  // SO FÜGST DU EIN ZEICHEN HINZU:
  if (calc_way !== defaultValue) {
    calc_way = calc_way.slice(0, -1);
    if (calc_way === "") {
      calc_way = defaultValue;
    }
  }
  updateDisplay();
}

function calculate() {
  console.log("calculate gestartet, calc_way:", calc_way);

  // 1. PRÜFUNG: Ist überhaupt etwas zu berechnen?
  if (calc_way === "" || calc_way === defaultValue) {
    console.log("Fehler: Nichts zu berechnen");

    // Fehler anzeigen
    calc_way = "FEHLER!";
    updateDisplay();

    // Nach 2 Sekunden zurück zu normal
    setTimeout(function () {
      calc_way = defaultValue; // Jetzt erst nach 2 Sekunden!
      updateDisplay();
    }, 2000);

    return; // ← WICHTIG: Funktion hier beenden!
  }

  // 2. BERECHNUNG: eval() macht die Mathe (nur wenn kein Fehler war)
  try {
    console.log("Berechne:", calc_way);
    foo_calc_way = calc_way;
    console.log("foo_calc_way:", foo_calc_way);
    console.log("Der alte Calc_way:", calc_way);
    foo = eval(foo_calc_way);
    result = foo.toString();
    console.log("Ergebnis:", result);
    show_result = true;
    updateDisplay();
  } catch (error) {
    // 3. FEHLERBEHANDLUNG: Falls etwas schief geht
    console.log("Rechenfehler:", error);
    calc_way = "Rechenfehler";
    updateDisplay();
  }
}

function saveCalculation(url) {
  console.log("saveCalculation");
  console.log("Die URL lautet: ", url);
  console.log("calc_way:", calc_way);

  fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ calc_way: calc_way, result: result }),
  })
    .then((response) => {
      // Zuerst HTTP-Status prüfen
      if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      console.log("Server Antwort:", data);

      // ERFOLG oder FEHLER prüfen
      if (data.error) {
        // FEHLER vom Server
        console.error("Server-Fehler:", data.error);

        // User informieren - Fehler
        alert("❌ Fehler: " + data.error);

        // Optional: Display rot färben für 2 Sekunden
        showError(data.error);
      } else if (data.success) {
        // ERFOLG vom Server
        console.log("Erfolgreich:", data.success);

        // User informieren - Erfolg
        alert("✅ " + data.success);

        // Optional: Display grün färben für 2 Sekunden
        showSuccess(data.success);
      } else {
        // Unbekannte Antwort
        console.warn("Unbekannte Server-Antwort:", data);
        alert("⚠️ Unbekannte Antwort vom Server");
      }
    })
    .catch((error) => {
      // Netzwerk-Fehler oder andere Probleme
      console.error("Fetch-Fehler:", error);
      alert("❌ Verbindungsfehler: " + error.message);
    });
}

// Hilfsfunktionen für visuelles Feedback
function showError(message) {
  const display = document.getElementById("display");
  const originalValue = display.value;
  const originalStyle = display.style.backgroundColor;

  // Rot färben
  display.style.backgroundColor = "red";
  display.style.color = "white";
  display.value = "FEHLER!";

  // Nach 2 Sekunden zurücksetzen
  setTimeout(() => {
    display.style.backgroundColor = originalStyle;
    display.style.color = "";
    display.value = originalValue;
  }, 2000);
}

function showSuccess(message) {
  const display = document.getElementById("display");
  const originalValue = display.value;
  const originalStyle = display.style.backgroundColor;

  // Grün färben
  display.style.backgroundColor = "green";
  display.style.color = "white";
  display.value = "GESPEICHERT!";

  // Nach 2 Sekunden zurücksetzen
  setTimeout(() => {
    display.style.backgroundColor = originalStyle;
    display.style.color = "";
    display.value = originalValue;
  }, 2000);
}

// ANGEPASSTE Funktion - nimmt URL als Parameter
function loadSavedCalculations(url) {
  // ← URL als Parameter
  console.log("Lade gespeicherte Rechnungen...");
  console.log("URL:", url); // ← URL aus Jinja2 Template

  fetch(url, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Geladene Daten:", data);

      if (data.success) {
        displayCalculations(data.calculations, data.count);
      } else {
        alert("Fehler: " + (data.error || "Unbekannter Fehler"));
      }
    })
    .catch((error) => {
      console.error("Fehler beim Laden:", error);
      alert("Verbindungsfehler!");
    });
}

// Rest der Funktionen bleiben gleich...
function displayCalculations(calculations, count) {
  let container = document.getElementById("saved-calculations");
  if (!container) {
    container = createCalculationsContainer();
  }

  container.innerHTML = "";

  if (count === 0) {
    container.innerHTML = "<p>Keine gespeicherten Rechnungen gefunden.</p>";
    return;
  }

  const header = document.createElement("h3");
  header.textContent = `Gespeicherte Rechnungen (${count})`;
  container.appendChild(header);

  const list = document.createElement("ul");
  list.style.listStyle = "none";
  list.style.padding = "0";

  calculations.forEach((calc) => {
    const listItem = document.createElement("li");
    listItem.style.margin = "10px 0";
    listItem.style.padding = "10px";
    listItem.style.backgroundColor = "#f0f0f0";
    listItem.style.borderRadius = "5px";
    listItem.style.cursor = "pointer";

    listItem.innerHTML = `
            <strong>${calc.calc_way}</strong> = ${calc.result}<br>
            <small>Gespeichert: ${calc.created_at}</small>
        `;

    listItem.addEventListener("click", function () {
      loadCalculationToDisplay(calc);
    });

    list.appendChild(listItem);
  });

  container.appendChild(list);

  const closeButton = document.createElement("button");
  closeButton.textContent = "Schließen";
  closeButton.style.marginTop = "10px";
  closeButton.addEventListener("click", function () {
    container.style.display = "none";
  });
  container.appendChild(closeButton);

  container.style.display = "block";
}

// Container für die Anzeige erstellen
function createCalculationsContainer() {
  const container = document.createElement("div");
  container.id = "saved-calculations";
  container.style.position = "fixed";
  container.style.top = "10px";
  container.style.right = "10px";
  container.style.width = "300px";
  container.style.maxHeight = "400px";
  container.style.overflow = "auto";
  container.style.backgroundColor = "white";
  container.style.border = "2px solid #333";
  container.style.borderRadius = "10px";
  container.style.padding = "15px";
  container.style.zIndex = "1000";
  container.style.display = "none";

  document.body.appendChild(container);
  return container;
}

// Rechnung wieder in den Taschenrechner laden
function loadCalculationToDisplay(calc) {
  console.log("Lade Rechnung:", calc);

  // calc_way in den Taschenrechner laden
  calc_way = calc.calc_way;
  updateDisplay();

  // Container schließen
  const container = document.getElementById("saved-calculations");
  if (container) {
    container.style.display = "none";
  }

  alert(`Rechnung "${calc.calc_way}" geladen!`);
}
