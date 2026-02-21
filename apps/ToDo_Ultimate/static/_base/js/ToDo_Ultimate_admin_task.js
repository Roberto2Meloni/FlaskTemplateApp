// Task Management JavaScript
console.log("Task Management JS geladen");

/**
 * Führt einen Task manuell aus
 */
async function runTask(taskId) {
  console.log(`Führe Task ${taskId} aus...`);

  try {
    const url = window.AppURLs.TaskAPI.run(taskId);

    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();

    if (data.success) {
      showToast(data.message || `Task ${taskId} wurde gestartet`, "success");
    } else {
      showToast(data.message || "Fehler beim Ausführen des Tasks", "error");
    }
  } catch (error) {
    console.error("Fehler beim Ausführen des Tasks:", error);
    showToast("Fehler beim Ausführen des Tasks", "error");
  }
}

/**
 * Pausiert einen Task
 */
async function pauseTask(taskId) {
  console.log(`Pausiere Task ${taskId}...`);

  try {
    const url = window.AppURLs.TaskAPI.pause(taskId);

    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();

    if (data.success) {
      showToast(data.message || `Task ${taskId} wurde pausiert`, "info");

      // UI aktualisieren
      const row = document.querySelector(`tr[data-task-id="${taskId}"]`);
      if (row) {
        const statusCell = row.querySelector(".task-status");
        const actionsCell = row.querySelector(".task-actions");

        statusCell.innerHTML = `
                    <span class="status-badge status-paused">
                        <i class="bi bi-pause-circle-fill"></i> Pausiert
                    </span>
                `;

        actionsCell.innerHTML = `
                    <button class="btn-action btn-run" onclick="runTask('${taskId}')" title="Jetzt ausführen">
                        <i class="bi bi-play-fill"></i>
                    </button>
                    <button class="btn-action btn-resume" onclick="resumeTask('${taskId}')" title="Fortsetzen">
                        <i class="bi bi-play-circle-fill"></i>
                    </button>
                `;
      }
    } else {
      showToast(data.message || "Fehler beim Pausieren des Tasks", "error");
    }
  } catch (error) {
    console.error("Fehler beim Pausieren des Tasks:", error);
    showToast("Fehler beim Pausieren des Tasks", "error");
  }
}

/**
 * Setzt einen pausierten Task fort
 */
async function resumeTask(taskId) {
  console.log(`Setze Task ${taskId} fort...`);

  try {
    const url = window.AppURLs.TaskAPI.resume(taskId);

    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();

    if (data.success) {
      showToast(data.message || `Task ${taskId} wurde fortgesetzt`, "success");

      // UI aktualisieren
      const row = document.querySelector(`tr[data-task-id="${taskId}"]`);
      if (row) {
        const statusCell = row.querySelector(".task-status");
        const actionsCell = row.querySelector(".task-actions");

        statusCell.innerHTML = `
                    <span class="status-badge status-active">
                        <i class="bi bi-check-circle-fill"></i> Aktiv
                    </span>
                `;

        actionsCell.innerHTML = `
                    <button class="btn-action btn-run" onclick="runTask('${taskId}')" title="Jetzt ausführen">
                        <i class="bi bi-play-fill"></i>
                    </button>
                    <button class="btn-action btn-pause" onclick="pauseTask('${taskId}')" title="Pausieren">
                        <i class="bi bi-pause-fill"></i>
                    </button>
                `;
      }
    } else {
      showToast(data.message || "Fehler beim Fortsetzen des Tasks", "error");
    }
  } catch (error) {
    console.error("Fehler beim Fortsetzen des Tasks:", error);
    showToast("Fehler beim Fortsetzen des Tasks", "error");
  }
}

function initTaskManagement() {
  const taskTable = document.querySelector(".task-table");
  if (!taskTable) return;

  // Auto-refresh (30 Sekunden)
  setInterval(async () => {
    try {
      const response = await fetch(`${API_BASE}/api_get_tasks`);
      const data = await response.json();

      if (data.success) {
        data.tasks.forEach((task) => {
          const row = document.querySelector(`tr[data-task-id="${task.id}"]`);
          if (row) {
            const nextRunCell = row.querySelector(".task-next-run");
            if (nextRunCell) nextRunCell.textContent = task.next_run;
          }
        });
      }
    } catch (error) {
      console.error("Auto-refresh error:", error);
    }
  }, 30000);
}

console.log("Task Management JS initialisiert");
