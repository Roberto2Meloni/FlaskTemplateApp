console.log("MyGambler.js loaded");

// Globale Variablen
const start_credit = 100;
let credit = start_credit;
let winnings = 0;
let bet = 5;
const symbols = ["💎", "⭐", "🍒", "🍋", "7️⃣"];

function checkCreditToBet(amount = bet) {
  if (credit >= amount) {
    console.log("Credit reicht");
    return true;
  } else {
    console.log("Credit reicht nicht");
    alert("Credit reicht nicht");
    return false;
  }
}

function increaseBet() {
  let bet_step = 5;
  let new_bet = bet + bet_step;

  if (checkCreditToBet(new_bet)) {
    // Neuen Bet übergeben
    bet = new_bet;
    updateDisplay();
    console.log("Bet erhöht auf " + bet);
  } else {
    alert("Credit reicht nicht");
  }
}

function reduceBet() {
  console.log("Bet verringert auf " + bet);
  new_bet = bet - 5;
  if (new_bet > 0) {
    bet = new_bet;
    updateDisplay();
  } else {
    alert("Bet ist zu niedrig");
  }
}

function spin() {
  console.log("Spin");
}

function payOut() {
  console.log("Auszahlen");
  alert("Du hast " + winnings + " gewonnen!");
}

function updateDisplay() {
  document.querySelector("#credits .state_value").textContent = credit;
  document.querySelector("#winn .state_value").textContent = winnings;
  document.querySelector("#bet .state_value").textContent = bet;
}

// Global verfügbar machen für AJAX-Initialisierung
window.initSlotMachine = function () {
  console.log("Slot Machine initialisiert");
  updateDisplay();
  console.log("Zufallssymbol:", getRandomSymbol());
};

// Zufälliges Symbol generieren
function getRandomSymbol() {
  const randomIndex = Math.floor(Math.random() * symbols.length);
  return symbols[randomIndex];
}

function spin() {
  console.log("Spin");
  // 1. Prüfen ob genug Credits
  if (!checkCreditToBet()) {
    alert("Credit reicht nicht");
    return;
  }

  // 2. Credits abziehen
  credit -= bet;
  updateDisplay();
  console.log("Spin gestartet - Credits abgezogen: " + bet);

  // 3. Neue Symbole generieren
  const result1 = getRandomSymbol();
  const result2 = getRandomSymbol();
  const result3 = getRandomSymbol();

  // 4. Animation starten
  const reels = document.querySelectorAll(".reel");
  reels.forEach((reel) => reel.classList.add("spinning"));

  // 5. Nach 2 Sekunden: Symbole setzen und Animation stoppen
  setTimeout(() => {
    // Symbole in die mittlere Position (index 1) setzen
    document.querySelectorAll("#reel1 .reel_symbol")[1].textContent = result1;
    document.querySelectorAll("#reel2 .reel_symbol")[1].textContent = result2;
    document.querySelectorAll("#reel3 .reel_symbol")[1].textContent = result3;

    // Animation stoppen
    reels.forEach((reel) => reel.classList.remove("spinning"));

    console.log("Ergebnis:", result1, result2, result3);

    // 6. Gewinn prüfen (kommt im nächsten Schritt)
    checkWin(result1, result2, result3);
  }, 2000);
}
