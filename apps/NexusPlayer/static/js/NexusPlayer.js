// Sidebar Toggle Funktionalität
document.addEventListener("DOMContentLoaded", function () {
  const navigation = document.getElementById("navigation");
  const toggle = document.getElementById("toggle");

  // Initial state (collapsed)
  let isExpanded = false;

  // Toggle function
  function toggleSidebar() {
    isExpanded = !isExpanded;

    if (isExpanded) {
      navigation.classList.add("active");
      navigation.classList.remove("collapsed");
      navigation.classList.add("expanded");
    } else {
      navigation.classList.remove("active");
      navigation.classList.add("collapsed");
      navigation.classList.remove("expanded");
    }

    // Save state to localStorage
    localStorage.setItem("sidebarExpanded", isExpanded);
    console.log("Sidebar toggled:", isExpanded);
  }

  // Event listener für Toggle Button
  if (toggle) {
    toggle.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      toggleSidebar();
    });
  }

  // Load saved state from localStorage
  const savedState = localStorage.getItem("sidebarExpanded");
  if (savedState === "true") {
    isExpanded = true;
    navigation.classList.add("active");
    navigation.classList.add("expanded");
    navigation.classList.remove("collapsed");
  } else {
    navigation.classList.add("collapsed");
    navigation.classList.remove("active");
    navigation.classList.remove("expanded");
  }

  // Optional: Keyboard shortcut (Ctrl + B)
  document.addEventListener("keydown", function (e) {
    if (e.ctrlKey && e.key === "b") {
      e.preventDefault();
      toggleSidebar();
    }
  });

  // Optional: Close sidebar when clicking outside (nur auf mobile)
  document.addEventListener("click", function (e) {
    if (window.innerWidth <= 768 && isExpanded && navigation && toggle) {
      if (!navigation.contains(e.target) && !toggle.contains(e.target)) {
        isExpanded = false;
        navigation.classList.remove("active");
        navigation.classList.add("collapsed");
        navigation.classList.remove("expanded");
        localStorage.setItem("sidebarExpanded", false);
      }
    }
  });

  // Menu Item Click Handler (für aktive States)
  const menuItems = document.querySelectorAll(".navigation .list");

  menuItems.forEach((item) => {
    const link = item.querySelector("a");
    if (link) {
      link.addEventListener("click", function (e) {
        // Nur preventDefault wenn es ein # Link ist
        if (this.getAttribute("href") === "#") {
          e.preventDefault();
        }

        // Remove active class from all items
        menuItems.forEach((otherItem) => {
          otherItem.classList.remove("active");
        });

        // Add active class to clicked item
        item.classList.add("active");

        // Optional: Auto-collapse auf mobile nach selection
        if (window.innerWidth <= 768 && isExpanded) {
          setTimeout(() => {
            toggleSidebar();
          }, 300);
        }
      });
    }
  });

  // Existing CLI functionality
  let connectedElement = document.querySelector(".cli-connected p");
  if (connectedElement) {
    console.log(connectedElement);
    let connectedRow = connectedElement.textContent;
    console.log(connectedRow);
    let systemName = connectedRow.match(/Verbunden mit (.*)/)[1];
    console.log(systemName);
    var commandSystemName = systemName + " # ";
    console.log(commandSystemName);
  }
});

// Rest of existing functions...
function clearConsole() {
  const output = document.getElementById("cli-history");
  if (output) {
    output.innerHTML = "";
  }
}

function handleKeyDown(event, url_receive_command, url_check_output) {
  const inputField = document.getElementById("cli-input-field");
  if (!inputField) return;

  const command = inputField.value;

  if (event.key === "Enter" && command.length > 0) {
    processCommand(command, url_receive_command, url_check_output);
    inputField.value = "";
  } else if (event.key === "Escape") {
    inputField.value = "";
  }
}

async function processCommand(command, url_check_command, url_check_output) {
  try {
    const response = await fetch(url_check_command, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ command: command }),
    });

    if (!response.ok) {
      throw new Error(`HTTP Fehler! Status: ${response.status}`);
    }

    const data = await response.json();
    const commandId = data.command_id;

    addCommandToHistory(command, { output: [] }, commandId);
    checkCommandOutput(commandId, url_check_output);
  } catch (error) {
    console.error("Fehler bei der Verarbeitung des Befehls:", error);
    addCommandToHistory(command, { error: [error.message] });
  }
}

function safeDecodeURIComponent(str) {
  try {
    return decodeURIComponent(escape(str));
  } catch (e) {
    try {
      return decodeURIComponent(str);
    } catch (e2) {
      console.warn("Fehler beim Dekodieren:", e2);
      return str;
    }
  }
}

function updateCommandOutput(commandId, output, error) {
  const historyEntry = document.querySelector(
    `[data-command-id="${commandId}"]`
  );
  if (historyEntry) {
    const outputElement = historyEntry.querySelector(".cli-output-command");
    if (output && output.length > 0) {
      output.forEach((line) => {
        const decodedLine = safeDecodeURIComponent(line);
        outputElement.innerHTML += decodedLine + "<br>";
      });
    }
    if (error && error.length > 0) {
      error.forEach((line) => {
        const decodedLine = safeDecodeURIComponent(line);
        outputElement.innerHTML += `<span style="color: red;">${decodedLine}</span><br>`;
      });
    }
    const cliWrapper = document.querySelector(".cli-console-container");
    if (cliWrapper) {
      cliWrapper.scrollTop = 0;
    }
  }
}

function checkCommandOutput(commandId, url_check_output) {
  console.log("checkCommandOutput");
  console.log(commandId);
  let new_url = url_check_output.replace("/0", `/${commandId}`);
  console.log(new_url);

  const intervalId = setInterval(async () => {
    try {
      const response = await fetch(new_url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();

      updateCommandOutput(commandId, data.output, data.error);

      if (data.complete) {
        clearInterval(intervalId);
      }
    } catch (error) {
      console.error("Fehler beim Abrufen der Befehlsausgabe:", error);
      updateCommandOutput(commandId, [], [`Fehler: ${error.message}`]);
      clearInterval(intervalId);
    }
  }, 500);
}

function addCommandToHistory(command, response, commandId) {
  const history = document.getElementById("cli-history");
  if (!history) return;

  const commandUl = document.createElement("div");
  commandUl.classList.add("cli-history-entry");
  commandUl.dataset.commandId = commandId;

  const commandInput = document.createElement("div");
  const commandOutput = document.createElement("div");

  commandInput.classList.add("cli-input-command");
  commandOutput.classList.add("cli-output-command");

  let connectedElement = document.querySelector(".cli-connected p");
  let systemName = "System";

  if (connectedElement) {
    let connectedRow = connectedElement.textContent;
    systemName = connectedRow.match(/Verbunden mit (.*)/)[1] || "System";
  }

  var commandSystemName = systemName + " # ";
  commandInput.textContent = commandSystemName + command;

  if (response.output) {
    commandOutput.innerHTML = response.output.join("<br>");
  } else if (response.error) {
    commandOutput.innerHTML = `Fehler: ${response.error.join("<br>")}`;
    commandOutput.style.color = "red";
  } else {
    commandOutput.textContent = "Keine Antwort vom Server";
  }

  commandUl.appendChild(commandInput);
  commandUl.appendChild(commandOutput);
  history.prepend(commandUl);

  const cliWrapper = document.querySelector(".cli-console-container");
  if (cliWrapper) {
    cliWrapper.scrollTop = 0;
  }
}

function replaceSpecialChars(str) {
  const specialChars = {
    "Ã¼": "ü",
    "Ã¤": "ä",
    "Ã¶": "ö",
    Ã: "Ü",
    "Ã„": "Ä",
    "Ã–": "Ö",
    ÃŸ: "ß",
    "â‚¬": "€",
  };
  return str.replace(/[ÃüäöÜÄÖßâ‚¬]/g, (match) => specialChars[match] || match);
}
