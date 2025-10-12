import os
import json

# Definition der Pfade und Ordner mapping
root_path = os.getcwd()
protected_content_path = os.path.join(
    root_path,
    "app",
    "imported_apps",
    "develop_release",
    "NexusPlayer",
    "protected_content",
)
path_NexusPlayer_app_content_device = os.path.join(
    protected_content_path,
    "NexusPlayer_app_content_device",
)
path_NexusPlayer_app_content_images = os.path.join(
    protected_content_path,
    "NexusPlayer_app_content_images",
)
path_NexusPlayer_app_content_log = os.path.join(
    protected_content_path,
    "NexusPlayer_app_content_log",
)
path_NexusPlayer_app_content_offline = os.path.join(
    protected_content_path,
    "NexusPlayer_app_content_offline",
)
path_NexusPlayer_app_content_playlist = os.path.join(
    protected_content_path,
    "NexusPlayer_app_content_playlist",
)
path_NexusPlayer_app_content_temp = os.path.join(
    protected_content_path,
    "NexusPlayer_app_content_temp",
)
path_NexusPlayer_app_content_template = os.path.join(
    protected_content_path,
    "NexusPlayer_app_content_template",
)
path_NexusPlayer_app_content_webpages = os.path.join(
    protected_content_path,
    "NexusPlayer_app_content_webpages",
)


map_folder = {
    "/Bilder": path_NexusPlayer_app_content_images,
    "/Log": path_NexusPlayer_app_content_log,
    "/Geräte": path_NexusPlayer_app_content_device,
    "/Offline": path_NexusPlayer_app_content_offline,
    "/Playlists": path_NexusPlayer_app_content_playlist,
    "/Temp": path_NexusPlayer_app_content_temp,
    "/Templates": path_NexusPlayer_app_content_template,
    "/Webseiten": path_NexusPlayer_app_content_webpages,
}


def create_all_protected_content_folders():
    """
    Erstellt alle Ordner im protected_content_path
    """
    for folder in map_folder:
        folder_path = map_folder[folder]
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)


def get_directory_structure(path):
    """
    Rekursive Funktion, die die Ordnerstruktur als Dictionary zurückgibt
    """
    structure = {}

    try:
        # Alle Elemente im aktuellen Pfad auflisten
        items = os.listdir(path)

        for item in items:
            item_path = os.path.join(path, item)

            if os.path.isdir(item_path):
                # Wenn es ein Ordner ist, rekursiv die Struktur abrufen
                structure[item] = {
                    "type": "directory",
                    "content": get_directory_structure(item_path),
                }
            else:
                # Wenn es eine Datei ist, nur den Namen und Typ speichern
                structure[item] = {"type": "file", "size": os.path.getsize(item_path)}

    except PermissionError:
        # Falls auf einen Ordner nicht zugegriffen werden kann
        structure["error"] = "Permission denied"
    except Exception as e:
        structure["error"] = str(e)

    return structure


def get_file_hirarchy_full():
    """
    Hauptfunktion, die die Ordnerstruktur des NexusPlayer protected_content als JSON zurückgibt
    """
    root_path = os.getcwd()
    nexus_protected_content = os.path.join(
        root_path,
        "app",
        "imported_apps",
        "develop_release",
        "NexusPlayer",
        "protected_content",
    )

    # print(f"Root Path: {root_path}")
    # print(f"Protected Content Path: {nexus_protected_content}")

    # Überprüfen ob der Pfad existiert
    if not os.path.exists(nexus_protected_content):
        error_result = {"error": f"Path does not exist: {nexus_protected_content}"}
        # print(json.dumps(error_result, indent=2))
        return error_result

    # Hauptordner auflisten
    main_folders = os.listdir(nexus_protected_content)
    # print(f"Main Folders: {main_folders}")

    # Struktur für jeden Hauptordner erstellen
    complete_structure = {}

    for folder in main_folders:
        folder_path = os.path.join(nexus_protected_content, folder)
        if os.path.isdir(folder_path):
            complete_structure[folder] = get_directory_structure(folder_path)

    # JSON ausgeben
    json_output = json.dumps(complete_structure, indent=2, ensure_ascii=False)
    # print("\n=== COMPLETE DIRECTORY STRUCTURE AS JSON ===")
    # print(json_output)
    # print("=== END OF JSON OUTPUT ===\n")

    return complete_structure


# Alternative Funktion für kompaktere Ausgabe (nur Ordnernamen)
def get_file_hirarchy_simple():
    """
    Vereinfachte Version, die nur Ordnernamen ohne Dateien zurückgibt
    """

    def get_directory_names_only(path):
        structure = {}
        try:
            items = os.listdir(path)
            for item in items:
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    structure[item] = get_directory_names_only(item_path)
        except (PermissionError, Exception) as e:
            structure["error"] = str(e)
        return structure

    root_path = os.getcwd()
    nexus_protected_content = os.path.join(
        root_path,
        "app",
        "imported_apps",
        "develop_release",
        "NexusPlayer",
        "protected_content",
    )

    if not os.path.exists(nexus_protected_content):
        error_result = {"error": f"Path does not exist: {nexus_protected_content}"}
        # print(json.dumps(error_result, indent=2))
        return error_result

    main_folders = os.listdir(nexus_protected_content)
    complete_structure = {}

    for folder in main_folders:
        folder_path = os.path.join(nexus_protected_content, folder)
        if os.path.isdir(folder_path):
            complete_structure[folder] = get_directory_names_only(folder_path)

    json_output = json.dumps(complete_structure, indent=2, ensure_ascii=False)
    # print("\n=== DIRECTORY STRUCTURE (FOLDERS ONLY) AS JSON ===")
    # print(json_output)
    # print("=== END OF JSON OUTPUT ===\n")

    return complete_structure


def get_both():
    # print(30 * "-")
    # print("Hier die Folle ansicht")
    # print(10 * "-")
    full_architecture = get_file_hirarchy_full()
    # print("Hier die Simple ansicht")
    # print(10 * "-")
    simpel_architecture = get_file_hirarchy_simple()
    # print(30 * "-")

    return full_architecture, simpel_architecture


create_all_protected_content_folders()
