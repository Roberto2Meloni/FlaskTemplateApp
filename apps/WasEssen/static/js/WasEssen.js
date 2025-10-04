console.log("WasEssen.js loaded");

// ==========================================
// 1️⃣ FARBEN FÜR DIE SEGMENTE
// ==========================================
const COLORS = [
  "#FF6B6B", // Rot
  "#4ECDC4", // Türkis
  "#45B7D1", // Blau
  "#FFA07A", // Lachs
  "#98D8C8", // Mint
  "#F7DC6F", // Gelb
  "#BB8FCE", // Lila
  "#85C1E2", // Hellblau
  "#F8B739", // Orange
  "#52B788", // Grün
];

// ==========================================
// 2️⃣ GERICHTE VOM BACKEND HOLEN
// ==========================================
// Diese Variable wird vom HTML/Jinja2 gesetzt
const FOODS = window.FOODS_DATA || [];
console.log("📊 Anzahl Gerichte:", FOODS.length);

// ==========================================
// 3️⃣ CANVAS SETUP
// ==========================================
const canvas = document.getElementById("wheelCanvas");
const ctx = canvas.getContext("2d");

// Canvas Größe setzen (höhere Auflösung)
canvas.width = 1200;
canvas.height = 1200;

// ==========================================
// 4️⃣ RAD ZEICHNEN - HAUPTFUNKTION
// ==========================================
function drawWheel() {
  const numSegments = FOODS.length; // Anzahl der Gerichte
  const anglePerSegment = (2 * Math.PI) / numSegments; // Winkel pro Segment
  const centerX = canvas.width / 2; // Mitte X
  const centerY = canvas.height / 2; // Mitte Y
  const radius = canvas.width / 2; // Radius

  console.log("🎨 Zeichne Rad mit", numSegments, "Segmenten");

  // Jedes Segment einzeln zeichnen
  for (let i = 0; i < numSegments; i++) {
    // Start- und End-Winkel für dieses Segment berechnen
    // -Math.PI / 2 bedeutet: Start bei 12 Uhr (oben)
    const startAngle = i * anglePerSegment - Math.PI / 2;
    const endAngle = startAngle + anglePerSegment;

    // Farbe für dieses Segment (wiederholt sich)
    const color = COLORS[i % COLORS.length];

    // Segment zeichnen
    drawSegment(i, startAngle, endAngle, centerX, centerY, radius, color);
  }
}

// ==========================================
// 5️⃣ EIN EINZELNES SEGMENT ZEICHNEN
// ==========================================
function drawSegment(
  index,
  startAngle,
  endAngle,
  centerX,
  centerY,
  radius,
  color
) {
  const food = FOODS[index];

  // SCHRITT 1: Segment-Form zeichnen (wie ein Kuchenstück)
  ctx.beginPath();
  ctx.arc(centerX, centerY, radius, startAngle, endAngle);
  ctx.lineTo(centerX, centerY); // Linie zur Mitte
  ctx.fillStyle = color;
  ctx.fill();

  // SCHRITT 2: Weißer Rand zwischen Segmenten
  ctx.strokeStyle = "#ffffff";
  ctx.lineWidth = 3;
  ctx.stroke();

  // SCHRITT 3: Text im Segment zeichnen
  drawSegmentText(food, startAngle, endAngle, centerX, centerY, radius);
}

// ==========================================
// 6️⃣ TEXT IM SEGMENT ZEICHNEN
// ==========================================
function drawSegmentText(food, startAngle, endAngle, centerX, centerY, radius) {
  // Winkel in der Mitte des Segments
  const angle = (startAngle + endAngle) / 2;

  // Position für Text berechnen (65% vom Rand)
  const textRadius = radius * 0.65;
  const textX = centerX + Math.cos(angle) * textRadius;
  const textY = centerY + Math.sin(angle) * textRadius;

  // Canvas drehen für aufrechten Text
  ctx.save(); // Aktuellen Zustand speichern
  ctx.translate(textX, textY); // Zum Text-Punkt bewegen
  ctx.rotate(angle + Math.PI / 2); // Drehen für aufrechten Text

  // Emoji zeichnen
  ctx.font = "bold 28px Arial";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillStyle = "#ffffff";
  ctx.fillText(food.emoji, 0, -15);

  // Name zeichnen (nur erste 10 Zeichen bei vielen Segmenten)
  const maxLength = FOODS.length > 20 ? 10 : 15;
  let displayName = food.name;
  if (displayName.length > maxLength) {
    displayName = displayName.substring(0, maxLength) + "...";
  }

  ctx.font = "bold 16px Arial";
  ctx.fillText(displayName, 0, 10);

  ctx.restore(); // Zustand wiederherstellen
}

// ==========================================
// 7️⃣ BUTTON FUNKTIONALITÄT MIT ANIMATION
// ==========================================
const spinButton = document.getElementById("spinButton");
const wheel = document.getElementById("wheel");
const resultDiv = document.getElementById("result");
const resultEmoji = document.getElementById("resultEmoji");
const resultName = document.getElementById("resultName");

let isSpinning = false; // Verhindert mehrfaches Drehen

spinButton.addEventListener("click", function () {
  // Wenn bereits am Drehen, ignoriere Klick
  if (isSpinning) return;

  console.log("🎲 Button geklickt! Starte Drehung...");
  isSpinning = true;

  // Button deaktivieren
  spinButton.style.opacity = "0.5";
  spinButton.style.cursor = "not-allowed";

  // Altes Ergebnis verstecken
  resultDiv.style.display = "none";

  // Zufälliges Gericht auswählen
  const randomIndex = Math.floor(Math.random() * FOODS.length);
  const selectedFood = FOODS[randomIndex];

  console.log("🎯 Ziel:", selectedFood.name);

  // Dreh-Animation starten
  spinWheel(randomIndex, selectedFood);
});

// ==========================================
// 8️⃣ DREH-ANIMATION FUNKTION
// ==========================================
function spinWheel(targetIndex, selectedFood) {
  // SCHRITT 1: Berechne Drehung
  const numSegments = FOODS.length;
  const anglePerSegment = 360 / numSegments; // Grad pro Segment

  // SCHRITT 2: Berechne Ziel-Winkel
  // Der Pfeil zeigt nach unten (auf 0°), also müssen wir das Segment dorthin drehen
  const targetAngle = targetIndex * anglePerSegment;

  // SCHRITT 3: Extra Umdrehungen (5 volle Drehungen = 1800°)
  const extraSpins = 5 * 360;

  // SCHRITT 4: Gesamt-Drehung
  // Wir drehen gegen den Uhrzeigersinn, also negativ
  const totalRotation = -(extraSpins + targetAngle);

  console.log("🔄 Drehe um", totalRotation, "Grad");

  // SCHRITT 5: Animation anwenden
  wheel.classList.add("spinning");
  wheel.style.transform = `rotate(${totalRotation}deg)`;

  // SCHRITT 6: Warte bis Animation fertig (4 Sekunden)
  setTimeout(() => {
    // Ergebnis anzeigen
    showResult(selectedFood);

    // Button wieder aktivieren
    isSpinning = false;
    spinButton.style.opacity = "1";
    spinButton.style.cursor = "pointer";

    console.log("✅ Drehung beendet!");
  }, 4000); // 4000ms = 4 Sekunden
}

// ==========================================
// 9️⃣ ERGEBNIS ANZEIGEN
// ==========================================
function showResult(food) {
  resultEmoji.textContent = food.emoji;
  resultName.textContent = food.name;
  resultDiv.style.display = "block";

  console.log("🎉 Gewinner:", food.name);
}

// ==========================================
// 8️⃣ RAD BEIM LADEN ZEICHNEN
// ==========================================
// Warte kurz, damit alle Daten geladen sind
setTimeout(() => {
  if (FOODS.length > 0) {
    drawWheel();
    console.log("✅ Rad erfolgreich gezeichnet!");
  } else {
    console.error("❌ Keine Gerichte gefunden!");
  }
}, 100);

// ==========================================
// 🎓 JAVASCRIPT KONZEPTE ERKLÄRT:
// ==========================================
/*
1. Canvas = Zeichenfläche wie ein leeres Blatt Papier
   - ctx.arc() = Kreisbogen zeichnen
   - ctx.fill() = Ausfüllen mit Farbe
   - ctx.stroke() = Rand zeichnen

2. Math.PI = Pi (3.14159...)
   - 2 * Math.PI = 360° (voller Kreis)
   - Math.PI / 2 = 90° (Viertelkreis)

3. Winkel in JavaScript:
   - 0 = rechts (3 Uhr)
   - Math.PI / 2 = unten (6 Uhr)
   - Math.PI = links (9 Uhr)
   - -Math.PI / 2 = oben (12 Uhr)

4. ctx.save() und ctx.restore():
   - save() = Aktuellen Zustand speichern
   - restore() = Gespeicherten Zustand wiederherstellen
   - Nützlich beim Drehen und Transformieren

5. addEventListener('click', function):
   - Reagiert auf Button-Klick
   - Die Funktion wird ausgeführt wenn geklickt wird

6. CSS Transform und Rotation:
   - transform: rotate(360deg) = Eine volle Drehung
   - rotate(1800deg) = 5 volle Drehungen
   - Negativ (-360deg) = Gegen den Uhrzeigersinn

7. setTimeout(function, milliseconds):
   - Wartet X Millisekunden, dann führt Code aus
   - 4000ms = 4 Sekunden
   - Perfekt um auf Animation zu warten
*/
