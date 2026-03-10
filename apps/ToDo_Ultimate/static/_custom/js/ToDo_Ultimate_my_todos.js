console.log("Template_app_v001_page_01.js loaded");

// =============================================
// FUNKTION: Neuen Todo erstellen
// Wird aufgerufen wenn der Button geklickt wird
// =============================================
function addTodo() {
  // Hole die Liste aus dem HTML
  const todoList = document.getElementById("todo-list");

  // Erstelle ein neues HTML-Element (ein leeres div)
  const newItem = document.createElement("div");
  newItem.className = "todo-item todo-item--new";

  // Fülle das div mit HTML - hier ist das Eingabefeld drin
  newItem.innerHTML = `
    <button class="todo-check" disabled>
      <i class="bi bi-circle"></i>
    </button>
    <div class="todo-body">
      <input
        id="todo-new-input"
        class="todo-input"
        type="text"
        placeholder="Task beschreiben und Enter drücken …"
        autocomplete="off"
      />
    </div>
    <div class="todo-actions" style="opacity:1;">
      <button class="action-btn danger" title="Abbrechen" onclick="cancelNewTodo()">
        <i class="bi bi-x-lg"></i>
      </button>
    </div>
  `;

  // Füge das neue Element ganz oben in die Liste ein
  todoList.prepend(newItem);

  // Hole das Eingabefeld und setze den Fokus darauf
  const input = document.getElementById("todo-new-input");
  input.focus();

  // Reagiere auf Tastendruck im Eingabefeld
  input.addEventListener("keydown", function (event) {
    // Enter gedrückt → speichern
    if (event.key === "Enter") {
      saveTodo();
    }

    // Escape gedrückt → abbrechen
    if (event.key === "Escape") {
      cancelNewTodo();
    }
  });
}

// =============================================
// FUNKTION: Todo speichern
// Liest den Text aus dem Eingabefeld und
// erstellt daraus einen echten Todo-Eintrag
// =============================================
function saveTodo() {
  // Hole das Eingabefeld
  const input = document.getElementById("todo-new-input");

  // Lese den eingetippten Text (trim entfernt Leerzeichen am Anfang/Ende)
  const text = input.value.trim();

  // Wenn das Feld leer ist → nichts speichern
  if (text === "") {
    input.focus();
    return;
  }

  // Hole das Eingabe-Item (das div mit der Klasse todo-item--new)
  const newItem = document.querySelector(".todo-item--new");

  // Ersetze den Inhalt mit einem echten Todo-Eintrag
  newItem.classList.remove("todo-item--new");
  newItem.setAttribute("data-status", "open");
  newItem.innerHTML = `
    <button class="todo-check" title="Als erledigt markieren">
      <i class="bi bi-circle"></i>
    </button>
    <div class="todo-body">
      <span class="todo-text">${text}</span>
      <div class="todo-meta">
        <span class="todo-tag tag-high">Offen</span>
      </div>
    </div>
    <div class="todo-actions">
      <button class="action-btn danger" title="Löschen" onclick="deleteTodo(this)">
        <i class="bi bi-trash3"></i>
      </button>
    </div>
  `;

  // Stats aktualisieren
  updateStats();
}

// =============================================
// FUNKTION: Abbrechen
// Entfernt das Eingabefeld wieder
// =============================================
function cancelNewTodo() {
  const newItem = document.querySelector(".todo-item--new");

  // Nur entfernen wenn es existiert
  if (newItem) {
    newItem.remove();
  }
}

// =============================================
// FUNKTION: Todo löschen
// Bekommt den geklickten Button übergeben
// =============================================
function deleteTodo(button) {
  // Gehe vom Button hoch zum übergeordneten todo-item div
  const todoItem = button.closest(".todo-item");

  // Entferne das ganze Item aus der Liste
  todoItem.remove();

  // Stats aktualisieren
  updateStats();
}

// =============================================
// FUNKTION: Stats aktualisieren
// Zählt die Items und zeigt die Zahlen an
// =============================================
function updateStats() {
  // Zähle alle Items in der Liste
  const alleItems = document.querySelectorAll("#todo-list .todo-item");
  const erledigtItems = document.querySelectorAll(
    '#todo-list .todo-item[data-status="done"]',
  );
  const offenItems = alleItems.length - erledigtItems.length;

  // Schreibe die Zahlen ins HTML
  document.getElementById("stat-total").textContent = alleItems.length;
  document.getElementById("stat-open").textContent = offenItems;
  document.getElementById("stat-done").textContent = erledigtItems.length;
}
