console.log("JS für Calculator integriert!");

// Einfacher Taschenrechner JavaScript
// Für Anfänger - einfach und verständlich

// Variables für den Taschenrechner
let defaultValue = "-?-";
let operator = "";
let previousInput = "";
let shouldResetDisplay = false;
let calc_way = "";

// Beim Laden der Seite
document.addEventListener("DOMContentLoaded", function () {
  clearDisplay();
});

// 1. DISPLAY AKTUALISIEREN
function clearDisplay() {
  const display = document.getElementById("display");
  calc_way = defaultValue;
  updateDisplay();
}

function updateDisplay() {
  const display = document.getElementById("display");
  if (!calc_way) {
    calc_way = defaultValue;
  } else {
    display.value = calc_way;
  }
  console.log("Hier die aktuelle rechnung: " + calc_way);
}

function addChar(char) {
  console.log("addChar");
  console.log(char);

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
  // SO FÜGST DU EIN ZEICHEN HINZU:
  calc_way += operator;
  updateDisplay();
}

function deleteLastChar() {
  console.log("deleteLastChar");
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
    let result = eval(calc_way);
    console.log("Ergebnis:", result);
    calc_way = result.toString();
    updateDisplay();
  } catch (error) {
    // 3. FEHLERBEHANDLUNG: Falls etwas schief geht
    console.log("Rechenfehler:", error);
    calc_way = "Rechenfehler";
    updateDisplay();
  }
}
