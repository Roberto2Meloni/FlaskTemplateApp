// Globale Variable für den aktuellen Pfad
let currentPath = "/";
document.addEventListener("DOMContentLoaded", function () {
  // Hamburger Menu Funktionalität (unverändert)
  const hamburgerMenu = document.getElementById("hamburgerMenu");
  const navigation = document.getElementById("navigation");

  if (hamburgerMenu && navigation) {
    hamburgerMenu.addEventListener("click", function () {
      navigation.classList.toggle("collapsed");

      // Icon ändern
      const icon = hamburgerMenu.querySelector("i");
      if (navigation.classList.contains("collapsed")) {
        icon.className = "bi bi-chevron-right";
      } else {
        icon.className = "bi bi-list";
      }
    });
  }

  // Navigation mit AJAX (erweitert)
  const allMenuItems = document.querySelectorAll(
    ".upper_items .list, .lower_items .list"
  );

  const menuItems = [];
  allMenuItems.forEach(function (item) {
    const linkText = item.querySelector(".list_element").textContent.trim();
    if (linkText !== "Zurück zu Apps") {
      menuItems.push(item);
    }
  });

  menuItems.forEach(function (menuItem) {
    const link = menuItem.querySelector("a");

    if (link) {
      link.addEventListener("click", function (event) {
        event.preventDefault();

        menuItems.forEach(function (item) {
          item.classList.remove("active");
        });

        menuItem.classList.add("active");

        // NEU: Seite laden
        const elementName = menuItem
          .querySelector(".list_element")
          .textContent.trim();

        if (elementName === "Dashboard") {
          loadPage(url_dashboard);
        } else if (elementName === "Datei") {
          loadPage(url_files).then(() => {
            initFileBrowser();
          });
        } else if (elementName === "Playlists") {
          loadPage(url_playlists);
        } else if (elementName === "Geräte") {
          loadPage(url_devices);
        } else if (elementName === "Admin") {
          loadPage(url_admin);
        }
      });
    }
  });
});

// NEU: Dashboard laden
function loadPage(url) {
  return fetch(url)
    .then((response) => response.text())
    .then((html) => {
      document.querySelector(".app-content").innerHTML = html;
      // Warte einen kurzen Moment damit der DOM aktualisiert wird
      return new Promise((resolve) => setTimeout(resolve, 10));
    });
}

function formatFileSize(bytes) {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
}

function createFolderElement(name, content) {
  const folderDiv = document.createElement("div");
  folderDiv.className = "folder";

  const folderName = document.createElement("div");
  folderName.className = "folder-name";

  const icon = document.createElement("span");
  icon.className = "folder-icon";
  icon.textContent = "📁";

  const nameSpan = document.createElement("span");
  nameSpan.textContent = name;

  folderName.appendChild(icon);
  folderName.appendChild(nameSpan);

  folderName.addEventListener("click", function () {
    const folderContent = folderDiv.querySelector(".folder-content");
    if (folderContent) {
      folderContent.classList.toggle("open");
      icon.textContent = folderContent.classList.contains("open") ? "📂" : "📁";
    }

    document
      .querySelectorAll(".folder-name")
      .forEach((el) => el.classList.remove("selected"));
    folderName.classList.add("selected");

    showFolderDetails(name, content);
  });

  folderDiv.appendChild(folderName);

  if (content && Object.keys(content).length > 0) {
    const folderContentDiv = document.createElement("div");
    folderContentDiv.className = "folder-content";

    Object.keys(content).forEach((itemName) => {
      const item = content[itemName];

      if (
        item.type === "directory" ||
        (typeof item === "object" && !item.type)
      ) {
        folderContentDiv.appendChild(
          createFolderElement(itemName, item.content || item)
        );
      } else if (item.type === "file") {
        folderContentDiv.appendChild(createFileElement(itemName, item));
      }
    });

    folderDiv.appendChild(folderContentDiv);
  }

  return folderDiv;
}

function createFileElement(name, fileInfo) {
  const fileDiv = document.createElement("div");
  fileDiv.className = "file-item";

  const icon = document.createElement("span");
  icon.className = "file-icon";

  const ext = name.split(".").pop().toLowerCase();
  switch (ext) {
    case "jpg":
    case "jpeg":
    case "png":
    case "gif":
      icon.textContent = "🖼️";
      break;
    default:
      icon.textContent = "📄";
  }

  const nameSpan = document.createElement("span");
  nameSpan.textContent = name;

  const sizeSpan = document.createElement("span");
  sizeSpan.className = "file-size";
  sizeSpan.textContent = formatFileSize(fileInfo.size || 0);

  fileDiv.appendChild(icon);
  fileDiv.appendChild(nameSpan);
  fileDiv.appendChild(sizeSpan);

  fileDiv.addEventListener("click", function () {
    document
      .querySelectorAll(".folder-name, .file-item")
      .forEach((el) => el.classList.remove("selected"));
    fileDiv.classList.add("selected");

    showFileDetails(name, fileInfo);
  });

  return fileDiv;
}

function showFolderDetails(name, content) {
  const detailsDiv = document.querySelector(".file-details-view");
  let detailsHtml = "";

  if (content && Object.keys(content).length > 0) {
    Object.keys(content).forEach((itemName) => {
      const item = content[itemName];
      // Nur Ordner anzeigen, keine Dateien
      if (item.type !== "file") {
        detailsHtml += `📁 ${itemName}/<br>`;
      }
    });
  } else {
    detailsHtml += "Ordner ist leer.";
  }

  detailsDiv.innerHTML = detailsHtml;
}

function showFileDetails(name, fileInfo) {
  const detailsDiv = document.querySelector(".file-details-view");
  let detailsHtml = `<strong>Datei: ${name}</strong><br><br>`;
  detailsHtml += `Größe: ${formatFileSize(fileInfo.size || 0)}<br>`;
  detailsHtml += `Typ: ${fileInfo.type || "Unbekannt"}`;

  detailsDiv.innerHTML = detailsHtml;
}

function initFileBrowser() {
  console.log("hole die Json's");
  const fileThreeDiv = document.querySelector(".file-three");
  const fileDetailsDiv = document.querySelector(".file-details-view");

  // Name-Mapping für bessere Anzeige
  const folderNameMapping = {
    NexusPlayer_app_content_device: "Geräte",
    NexusPlayer_app_content_images: "Bilder",
    NexusPlayer_app_content_log: "Log",
    NexusPlayer_app_content_offline: "Offline",
    NexusPlayer_app_content_playlist: "Playlist",
    NexusPlayer_app_content_temp: "Temp",
    NexusPlayer_app_content_template: "Templates",
    NexusPlayer_app_content_webpages: "Webseiten",
  };

  // 1. Hole die P-Tags
  const simplePTag = fileThreeDiv?.querySelector("p");
  const fullPTag = fileDetailsDiv?.querySelector("p");
  const adminStatusTag = document.getElementById("admin-status");

  if (!simplePTag || !fullPTag) {
    console.error("JSON P-Tags nicht gefunden!");
    return;
  }

  // 2. Parse die JSON Strings
  let simpleJson, fullJson;
  try {
    simpleJson = JSON.parse(simplePTag.textContent);
    fullJson = JSON.parse(fullPTag.textContent);
    console.log("Simple JSON geparst:", simpleJson);
    console.log("Full JSON geparst:", fullJson);
  } catch (error) {
    console.error("Fehler beim JSON parsen:", error);
    return;
  }

  // 3. Admin-Ordner definieren
  const adminFolders = [
    "NexusPlayer_app_content_device",
    "NexusPlayer_app_content_log",
    "NexusPlayer_app_content_temp",
    "NexusPlayer_app_content_template",
    "NexusPlayer_app_content_offline",
    "NexusPlayer_app_content_playlist",
  ];

  // Nicht Admin-Ordner sind diese
  // NexusPlayer_app_content_images: "Bilder",
  // NexusPlayer_app_content_webpages: "Webseiten",

  // 4. Filtere Admin-Ordner raus (nur für normale User)
  const isAdminManuel = false; // TODO: Echte Admin-Prüfung implementieren
  const isAdmin = adminStatusTag.textContent.trim() === "true";
  console.log("isAdminManuel:", isAdminManuel);
  console.log("Is Admin:", isAdmin);

  // 5. Filtere Admin-Ordner raus, egal ob Admin oder nicht
  let filteredJson = {};
  Object.keys(fullJson).forEach((folderName) => {
    if (!adminFolders.includes(folderName)) {
      filteredJson[folderName] = fullJson[folderName];
    }
  });

  // 6. Erstelle separate Admin-Ordner Liste (für später)
  let adminJson = {};
  Object.keys(fullJson).forEach((folderName) => {
    if (adminFolders.includes(folderName)) {
      adminJson[folderName] = fullJson[folderName];
    }
  });

  console.log("Gefilterte JSON:", filteredJson);

  // 7. Lösche alte Inhalte
  fileThreeDiv.innerHTML = "";
  fileDetailsDiv.innerHTML = "<div>Wählen Sie einen Ordner aus.</div>";

  // 8. Zeige normale Ordner an (mit schönen Namen)
  Object.keys(filteredJson).forEach((folderName) => {
    const displayName = folderNameMapping[folderName] || folderName;
    const folderElement = createSimpleFolder(
      displayName,
      filteredJson[folderName],
      false,
      folderName // Original-Name für interne Verarbeitung
    );
    fileThreeDiv.appendChild(folderElement);
  });

  // 9. Zeige Admin-Ordner an (falls Admin)
  if (isAdmin) {
    const separator = document.createElement("div");
    separator.innerHTML = "<hr><strong>Admin</strong>";
    separator.style.marginTop = "20px";
    fileThreeDiv.appendChild(separator);

    Object.keys(adminJson).forEach((folderName) => {
      const displayName = folderNameMapping[folderName] || folderName;
      const adminFolderElement = createSimpleFolder(
        displayName,
        adminJson[folderName],
        true,
        folderName // Original-Name
      );
      fileThreeDiv.appendChild(adminFolderElement);
    });
  }
}
function createSimpleFolder(
  displayName,
  folderContent,
  isAdminFolder = false,
  originalName = null,
  parentPath = ""
) {
  const folderDiv = document.createElement("div");

  // Haupt-Ordner
  const folderHeader = document.createElement("div");
  folderHeader.style.cursor = "pointer";
  folderHeader.style.padding = "5px";
  folderHeader.style.userSelect = "none";
  folderHeader.title = displayName; // Tooltip für lange Namen

  // Aktueller vollständiger Pfad
  const fullPath = parentPath
    ? `${parentPath}/${displayName}`
    : `/${displayName}`;

  // Hat dieser Ordner Unterelemente?
  const hasSubfolders = folderContent && Object.keys(folderContent).length > 0;

  // Text mit oder ohne Pfeil
  if (hasSubfolders) {
    folderHeader.innerHTML = `▶ 📁 ${displayName}`;
  } else {
    folderHeader.innerHTML = `📁 ${displayName}`;
  }

  // Click auf Ordner
  folderHeader.addEventListener("click", function (e) {
    e.stopPropagation();
    const nameForProcessing = originalName || displayName;
    console.log("Ordner geklickt:", displayName, "Pfad:", fullPath);

    showFolderDetails(displayName, folderContent);
    updateCurrentPath(fullPath);

    // Unterordner auf/zuklappen
    if (hasSubfolders) {
      const subContainer = folderDiv.querySelector(".sub-container");
      if (subContainer.style.display === "none") {
        subContainer.style.display = "block";
        folderHeader.innerHTML = `▼ 📁 ${displayName}`;
      } else {
        subContainer.style.display = "none";
        folderHeader.innerHTML = `▶ 📁 ${displayName}`;
      }
    }
  });

  folderDiv.appendChild(folderHeader);

  // Unterordner-Container
  if (hasSubfolders) {
    const subContainer = document.createElement("div");
    subContainer.className = "sub-container";
    subContainer.style.display = "none";
    subContainer.style.marginLeft = "20px";

    Object.keys(folderContent).forEach((itemName) => {
      const item = folderContent[itemName];

      if (item.type === "file") {
        // ==================== DATEI ====================
        const fileDiv = document.createElement("div");
        fileDiv.style.padding = "3px";
        fileDiv.style.cursor = "pointer";
        fileDiv.style.userSelect = "none";
        fileDiv.title = itemName; // Tooltip für lange Dateinamen
        fileDiv.innerHTML = `&nbsp;&nbsp;├─ 📄 ${itemName}`;

        fileDiv.addEventListener("click", function (e) {
          e.stopPropagation();
          console.log(
            "Datei geklickt:",
            itemName,
            "Pfad:",
            `${fullPath}/${itemName}`
          );
          updateCurrentPath(`${fullPath}/${itemName}`);
          showFileDetails(itemName, item);
        });

        subContainer.appendChild(fileDiv);
      } else {
        // ==================== UNTERORDNER (REKURSIV) ====================
        const subFolderElement = createSimpleFolder(
          itemName,
          item.content || item,
          isAdminFolder,
          null,
          fullPath // Vollständigen Pfad weitergeben
        );
        subContainer.appendChild(subFolderElement);
      }
    });

    folderDiv.appendChild(subContainer);
  }

  return folderDiv;
}

function updateCurrentPath(newPath) {
  currentPath = newPath;
  const currentPathElement = document.getElementById("current-path");
  if (currentPathElement) {
    currentPathElement.textContent = `Aktueller Pfad: ${currentPath}`;
  }

  // NEU: Button-Status aktualisieren
  updateButtonStates();
}

function updateButtonStates() {
  const newFolderButton = document.querySelector(".btn-warning");

  if (newFolderButton) {
    if (currentPath === "/") {
      newFolderButton.disabled = true;
    } else {
      newFolderButton.disabled = false;
    }
  }
}

function showNewFolderModal() {
  document.getElementById("newFolderModal").style.display = "block";
  const newFolderModalPath = document.getElementById("newFolderModalPath");
  const currentPathElement = document.getElementById("current-path");

  if (currentPathElement) {
    newFolderModalPath.innerHTML = `Pfad für neuen Ordner: <strong>${currentPath}</strong>`;
  }
}
function hideNewFolderModal() {
  document.getElementById("newFolderModal").style.display = "none";
}

function createNewFolder() {
  const newFolderName = document.getElementById("newFolderName").value;
  const errorDiv = document.getElementById("folderNameError");
  let errorMessage = "";
  let errorMessageState = false;
  const currentPathOrigin = document.getElementById("current-path").textContent;
  const currentPath = currentPathOrigin.replace("Aktueller Pfad: ", "");

  // Log Meldung
  console.log("Neuer Ordnername:", newFolderName);
  console.log("_", currentPath, "_");

  // Führe eine umfangreichen Check aus.
  // Ordnername leer?
  if (newFolderName === "") {
    errorMessage = "Der Ordnername darf nicht leer sein.";
    errorMessageState = true;
  }

  if (errorMessageState) {
    errorDiv.style.display = "block";
    errorDiv.innerHTML = errorMessage;
    return;
  } else {
    // ÄNDERUNG: Fehlermeldung verstecken vor dem Fetch
    errorDiv.style.display = "none";
    fetchNewFolder(newFolderName, currentPath);
  }

  // ENTFERNT: Das Leeren passiert jetzt nur bei Erfolg in fetchNewFolder
  // document.getElementById("newFolderName").value = "";
}

function fetchNewFolder(newFolderName, currentPath) {
  fetch(url_new_folder, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      new_folder_name: newFolderName,
      current_path: currentPath,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      if (data.success) {
        // Modal schließen
        hideNewFolderModal();
        // Input-Feld leeren
        document.getElementById("newFolderName").value = "";
        // Erfolgsmeldung anzeigen
        showSuccessMessage(data.message);

        // NEU: Verwende die bestehende loadPage() Funktion
        setTimeout(() => {
          loadPage(url_files).then(() => {
            initFileBrowser();
          });
        }, 500);
      } else {
        // Fehlermeldung im Modal anzeigen
        const errorDiv = document.getElementById("folderNameError");
        errorDiv.style.display = "block";
        errorDiv.innerHTML = data.message;
      }
    })
    .catch((error) => {
      console.error("Fehler:", error);
      const errorDiv = document.getElementById("folderNameError");
      errorDiv.style.display = "block";
      errorDiv.innerHTML = "Ein Fehler ist aufgetreten.";
    });
}

function showSuccessMessage(message) {
  // Erfolgsmeldung erstellen oder anzeigen
  let successDiv = document.getElementById("successMessage");

  if (!successDiv) {
    // Erstelle die Erfolgsmeldung einmalig
    successDiv = document.createElement("div");
    successDiv.id = "successMessage";
    successDiv.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background-color: #28a745;
      color: white;
      padding: 15px;
      border-radius: 5px;
      z-index: 2000;
      display: none;
    `;
    document.body.appendChild(successDiv);
  }

  // Meldung setzen und anzeigen
  successDiv.innerHTML = message;
  successDiv.style.display = "block";

  // Nach 3 Sekunden wieder verstecken
  setTimeout(() => {
    successDiv.style.display = "none";
  }, 3000);
}
