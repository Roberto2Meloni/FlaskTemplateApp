// Globale Variable für den aktuellen Pfad
let currentPath = "/";
const folderNameMapping = {
  NexusPlayer_app_content_device: "Geräte",
  NexusPlayer_app_content_content: "Inhalte",
  NexusPlayer_app_content_log: "Log",
  NexusPlayer_app_content_offline: "Offline",
  NexusPlayer_app_content_playlist: "Playlist",
  NexusPlayer_app_content_temp: "Temp",
  NexusPlayer_app_content_template: "Templates",
};

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

  // Wenn es sich um ein Bild handelt
  if (
    fileInfo.type === "file" &&
    ["jpg", "jpeg", "png", "gif", "webp", "svg"].includes(
      name.split(".").pop().toLowerCase()
    )
  ) {
    // Lade Bildvorschau
    fetch(url_show_image, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        current_path: currentPath,
        filename: name,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          let detailsHtml = `
          <strong>Datei: ${name}</strong><br><br>
          <img src="${
            data.image
          }" style="max-width: 100%; max-height: 300px; object-fit: contain;"><br><br>
          Größe: ${formatFileSize(data.size)}<br>
          Typ: Bild<br>
          Zuletzt geändert: ${new Date(
            data.last_modified * 1000
          ).toLocaleString()}
        `;
          detailsDiv.innerHTML = detailsHtml;
        } else {
          throw new Error(data.message);
        }
      })
      .catch((error) => {
        console.error("Fehler bei Bildvorschau:", error);
        detailsDiv.innerHTML = `
        <strong>Datei: ${name}</strong><br><br>
        Größe: ${formatFileSize(fileInfo.size || 0)}<br>
        Typ: ${fileInfo.type || "Unbekannt"}<br>
        <p style="color: red;">Vorschau nicht verfügbar</p>
      `;
      });
  } else {
    // Normale Dateidetails für Nicht-Bild-Dateien
    let detailsHtml = `
      <strong>Datei: ${name}</strong><br><br>
      Größe: ${formatFileSize(fileInfo.size || 0)}<br>
      Typ: ${fileInfo.type || "Unbekannt"}
    `;
    detailsDiv.innerHTML = detailsHtml;
  }
}
function initFileBrowser() {
  console.log("hole die Json's");
  const fileThreeDiv = document.querySelector(".file-three");
  const fileDetailsDiv = document.querySelector(".file-details-view");

  // Debug: Prüfe alle möglichen Selektoren
  console.log("Selektoren überprüfen:");
  console.log("fileThreeDiv:", fileThreeDiv);
  console.log("fileThreeDiv innerHTML:", fileThreeDiv?.innerHTML);
  console.log("fileDetailsDiv:", fileDetailsDiv);

  // Versuche verschiedene Wege, die P-Tags zu finden
  const simplePTagSelectors = [
    ".file-three p[style='display: none']",
    ".file-three p",
    "p[style='display: none']",
  ];

  const fullPTagSelectors = [
    ".file-details p[style='display: none']",
    ".file-details p",
    "p[style='display: none']",
  ];

  let simplePTag = null;
  let fullPTag = null;

  // Durchsuche alle Selektoren
  for (let selector of simplePTagSelectors) {
    simplePTag = fileThreeDiv?.querySelector(selector);
    if (simplePTag) break;
  }

  for (let selector of fullPTagSelectors) {
    fullPTag = fileDetailsDiv?.querySelector(selector);
    if (fullPTag) break;
  }

  console.log("Gefundene simplePTag:", simplePTag);
  console.log("Gefundene fullPTag:", fullPTag);

  const adminStatusTag = document.getElementById("admin-status");

  if (!simplePTag || !fullPTag) {
    console.error("JSON P-Tags nicht gefunden!");
    console.error("fileThreeDiv HTML:", fileThreeDiv?.innerHTML);
    console.error("fileDetailsDiv HTML:", fileDetailsDiv?.innerHTML);
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
  const newFolderButton = document.getElementById("newFolderButton");
  const deleteButton = document.getElementById("deleteButton");
  const addFileButton = document.getElementById("addFileButton");

  if (newFolderButton) {
    if (currentPath === "/") {
      newFolderButton.disabled = true;
      deleteButton.disabled = false;
      addFileButton.disabled = false;
    } else if (
      currentPath === "/Inhalte" ||
      currentPath === "/Geräte" ||
      currentPath === "/Log" ||
      currentPath === "/Offline" ||
      currentPath === "/Playlist" ||
      currentPath === "/Temp" ||
      currentPath === "/Templates"
    ) {
      newFolderButton.disabled = false;
      deleteButton.disabled = true;
      addFileButton.disabled = false;
    } else {
      newFolderButton.disabled = false;
      deleteButton.disabled = false;
      addFileButton.disabled = false;
    }
  }
}

function showDeleteModal() {
  // Aktuellen Pfad und Dateinamen aus dem UI extrahieren
  const currentPathText = currentPath;

  // Extrahiere den Dateinamen aus dem aktuellen Pfad
  const fileName = currentPathText.split("/").pop(); // "6af166a6-89ab-4f7f-a214-c48a45a4a0f.png"

  // Pfad ohne Dateinamen
  const deletePath = currentPathText.replace(`/${fileName}`, "");

  // Modal vorbereiten
  const deleteModal = document.getElementById("deleteModal");
  const deleteFileNameElement = document.getElementById("deleteFileName");
  const deleteError = document.getElementById("deleteError");

  // Fehler verstecken
  deleteError.style.display = "none";

  // Dateinamen im Modal anzeigen
  deleteFileNameElement.textContent = fileName;

  // Für den Löschvorgang
  currentDeletePath = deletePath;
  currentDeleteFileName = fileName;

  // Modal anzeigen
  deleteModal.style.display = "block";
}

function confirmDelete() {
  const deleteError = document.getElementById("deleteError");
  const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");

  // Button deaktivieren während des Löschvorgangs
  confirmDeleteBtn.disabled = true;
  deleteError.style.display = "none";

  fetch(url_delete_image, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      current_path: currentPath,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        // Modal schließen
        hideDeleteModal();

        // Erfolgsbenachrichtigung
        showSuccessMessage(data.message);

        // Seite neu laden
        setTimeout(() => {
          loadPage(url_files).then(() => {
            initFileBrowser();
          });
        }, 500);
      } else {
        // Fehlermeldung anzeigen
        deleteError.textContent = data.message;
        deleteError.style.display = "block";
      }
    })
    .catch((error) => {
      console.error("Fehler beim Löschen:", error);
      deleteError.textContent = "Ein Fehler ist aufgetreten";
      deleteError.style.display = "block";
    })
    .finally(() => {
      // Button wieder aktivieren
      confirmDeleteBtn.disabled = false;
    });
}

function hideDeleteModal() {
  document.getElementById("deleteModal").style.display = "none";
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
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
      transition: opacity 0.3s ease;
    `;
    document.body.appendChild(successDiv);
  }

  // Meldung setzen und anzeigen
  successDiv.innerHTML = message;
  successDiv.style.display = "block";
  successDiv.style.opacity = "1";

  // Nach 3 Sekunden wieder verstecken
  setTimeout(() => {
    successDiv.style.opacity = "0";
    setTimeout(() => {
      successDiv.style.display = "none";
    }, 300);
  }, 3000);
}

function showNewFolderModal() {
  document.getElementById("newFolderModal").style.display = "block";
  const newFolderModalPath = document.getElementById("newFolderModalPath");
  const currentPathElement = document.getElementById("current-path");

  if (currentPathElement) {
    newFolderModalPath.innerHTML = `Pfad für neuen Ordner: <strong>${currentPath}</strong>`;
  }
}

function showAddFileModal() {
  const modal = document.getElementById("addFileModal");
  const pathDisplay = document.getElementById("uploadModalPath");
  const currentPathText = currentPath;

  // Pfad korrigieren, wenn er eine Datei enthält
  const correctedPath = currentPathText.includes(".")
    ? currentPathText.substring(0, currentPathText.lastIndexOf("/"))
    : currentPathText;

  pathDisplay.textContent = `Upload nach: ${correctedPath}`;

  // Reset
  document.getElementById("fileInput").value = "";
  document.getElementById("filePreview").innerHTML = "";
  document.getElementById("uploadError").style.display = "none";
  document.getElementById("uploadFileBtn").disabled = true;
  selectedFile = null;

  modal.style.display = "block";
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
    // Fehlermeldung verstecken vor dem Fetch
    errorDiv.style.display = "none";
    fetchNewFolder(newFolderName, currentPath);
  }
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

        // Seite neu laden
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

function hideNewFolderModal() {
  document.getElementById("newFolderModal").style.display = "none";
}
function hideAddFileModal() {
  document.getElementById("addFileModal").style.display = "none";
}

function handleFileSelect(event) {
  const file = event.target.files[0];
  const errorDiv = document.getElementById("uploadError");
  const uploadBtn = document.getElementById("uploadFileBtn");
  const previewDiv = document.getElementById("filePreview");

  errorDiv.style.display = "none";
  previewDiv.innerHTML = "";

  if (!file) {
    uploadBtn.disabled = true;
    selectedFile = null;
    return;
  }

  // Validierung: Nur Bilder erlauben
  const allowedTypes = [
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/svg+xml",
  ];
  if (!allowedTypes.includes(file.type)) {
    errorDiv.textContent =
      "Nur Bilddateien sind erlaubt (JPG, PNG, GIF, WebP, SVG)";
    errorDiv.style.display = "block";
    uploadBtn.disabled = true;
    selectedFile = null;
    return;
  }

  // Dateigröße prüfen (z.B. max 10MB)
  const maxSize = 10 * 1024 * 1024; // 10MB
  if (file.size > maxSize) {
    errorDiv.textContent = "Datei ist zu groß (max. 10MB)";
    errorDiv.style.display = "block";
    uploadBtn.disabled = true;
    selectedFile = null;
    return;
  }

  selectedFile = file;
  uploadBtn.disabled = false;

  // Vorschau anzeigen
  const reader = new FileReader();
  reader.onload = function (e) {
    previewDiv.innerHTML = `
      <img src="${
        e.target.result
      }" style="max-width: 200px; max-height: 200px; border: 1px solid #ccc;" />
      <p><strong>Dateiname:</strong> ${file.name}</p>
      <p><strong>Größe:</strong> ${(file.size / 1024).toFixed(2)} KB</p>
    `;
  };
  reader.readAsDataURL(file);
}

async function uploadFile(url) {
  if (!selectedFile) {
    alert("Bitte wählen Sie eine Datei aus");
    return;
  }

  const reader = new FileReader();
  reader.onload = async function (event) {
    const base64Image = event.target.result;
    const uploadBtn = document.getElementById("uploadFileBtn");
    const cancelBtn = document.getElementById("cancelUploadBtn");
    const progressDiv = document.getElementById("uploadProgress");
    const errorDiv = document.getElementById("uploadError");

    // Korrektur des aktuellen Pfads
    const currentPathOrigin =
      document.getElementById("current-path").textContent;
    const currentPathRaw = currentPathOrigin.replace("Aktueller Pfad: ", "");
    const currentPath = currentPathRaw.includes(".")
      ? currentPathRaw.substring(0, currentPathRaw.lastIndexOf("/"))
      : currentPathRaw;

    uploadBtn.disabled = true;
    cancelBtn.disabled = true;
    progressDiv.style.display = "block";
    errorDiv.style.display = "none";

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          current_path: currentPath, // Korrigierter Pfad
          image: base64Image,
          filename: selectedFile.name,
        }),
      });

      const data = await response.json();
      if (data.status === "success") {
        showSuccessMessage(data.message);
        hideAddFileModal();

        setTimeout(() => {
          loadPage(url_files).then(() => {
            initFileBrowser();

            // Pfad wiederherstellen, aber ohne Dateinamen
            const pathToRestore = currentPath;
            updateCurrentPath(pathToRestore);
          });
        }, 500);
      } else {
        errorDiv.textContent = data.message || "Fehler beim Hochladen";
        errorDiv.style.display = "block";
      }
    } catch (error) {
      console.error("Upload-Fehler:", error);
      errorDiv.textContent = "Fehler beim Hochladen: " + error.message;
      errorDiv.style.display = "block";
    } finally {
      uploadBtn.disabled = false;
      cancelBtn.disabled = false;
      progressDiv.style.display = "none";
    }
  };

  reader.readAsDataURL(selectedFile);
}

async function loadPage(url, specificPath = null) {
  console.log(`\n→ Lade Seite: ${url}`);

  const contentArea = document.querySelector(".app-content");

  if (!contentArea) {
    window.location.href = url;
    return;
  }

  try {
    const response = await fetch(url, {
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const html = await response.text();
    contentArea.innerHTML = html;

    console.log(`✓ Seite geladen`);

    // Seite neu laden und aktuellen Pfad wiederherstellen
    setTimeout(() => {
      initFileBrowser();

      // Aktuellen Pfad wiederherstellen
      const currentPathElement = document.getElementById("current-path");
      if (currentPathElement) {
        // Verwende den übergebenen Pfad oder den globalen Pfad
        const pathToRestore = specificPath || currentPath || "/";

        const formattedPath = pathToRestore.startsWith("Aktueller Pfad: ")
          ? pathToRestore
          : `Aktueller Pfad: ${pathToRestore}`;

        currentPathElement.textContent = formattedPath;

        // Aktualisiere den globalen Pfad
        currentPath = pathToRestore.replace("Aktueller Pfad: ", "");

        // Ordnerstruktur entsprechend des aktuellen Pfads öffnen
        reopenCurrentPath(pathToRestore);
      }
    }, 300);

    return Promise.resolve();
  } catch (error) {
    console.error("Fehler beim Laden:", error);
    window.location.href = url;
    return Promise.reject(error);
  }
}

function reopenCurrentPath(path) {
  // Teile den Pfad in Segmente
  const pathSegments = path.split("/").filter((segment) => segment !== "");

  // Durchlaufe die Segmente und öffne die entsprechenden Ordner
  let currentFolder = null;
  pathSegments.forEach((segment, index) => {
    // Suche den Ordner mit dem aktuellen Segmentnamen
    const folderHeaders = document.querySelectorAll(
      ".folder-header, .folder-name"
    );
    const matchingFolder = Array.from(folderHeaders).find((header) =>
      header.textContent.trim().includes(segment)
    );

    if (matchingFolder) {
      // Öffne den Ordner
      const subContainer = matchingFolder.nextElementSibling;
      if (subContainer && subContainer.classList.contains("sub-container")) {
        subContainer.style.display = "block";
        matchingFolder.innerHTML = matchingFolder.innerHTML.replace("▶", "▼");
      }
    }
  });
}
