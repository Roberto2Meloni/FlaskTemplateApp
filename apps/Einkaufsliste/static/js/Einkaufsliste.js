console.log("Hello World von der Einkauflsite js");

document.addEventListener("DOMContentLoaded", function () {
  // Add loading state to buttons
  const buttons = document.querySelectorAll(".btn-custom");
  buttons.forEach((button) => {
    button.addEventListener("click", function () {
      if (!this.href.includes("delete")) {
        const originalContent = this.innerHTML;
        this.innerHTML = '<span class="loading-spinner"></span> Laden...';
        this.style.pointerEvents = "none";

        // Reset after 2 seconds if still on page
        setTimeout(() => {
          this.innerHTML = originalContent;
          this.style.pointerEvents = "auto";
        }, 2000);
      }
    });
  });

  // Enhanced hover effects for table rows
  const rows = document.querySelectorAll(".clickable-row");
  rows.forEach((row) => {
    row.addEventListener("mouseenter", function () {
      this.style.transform = "translateX(5px)";
    });

    row.addEventListener("mouseleave", function () {
      this.style.transform = "translateX(0)";
    });
  });

  // Initialize all functionality
  initializeEinkaufsliste();
});

/**
 * Initialize all functionality
 */
function initializeEinkaufsliste() {
  setupDeleteButtons();
  setupTouchHandlers();
  setupKeyboardNavigation();
  setupRefreshButton();
  addLoadingStates();
  handleViewportChanges();
}

/**
 * Setup delete buttons with proper event handling
 */
function setupDeleteButtons() {
  // Find all delete buttons (both desktop and mobile)
  const deleteButtons = document.querySelectorAll('[href*="delete_list"]');

  deleteButtons.forEach((button) => {
    // Get the data attributes
    const dateRange = button.getAttribute("data-date-range");
    const groupName = button.getAttribute("data-group-name");
    const deleteUrl = button.href;

    if (dateRange && groupName) {
      // Add event listener
      button.addEventListener("click", async function (e) {
        e.preventDefault();
        e.stopPropagation();

        const confirmed = await showConfirmDialog(dateRange, groupName);
        if (confirmed) {
          // Add loading state
          const icon = this.querySelector("i");
          if (icon) {
            icon.className = "loading-spinner";
          }
          this.style.pointerEvents = "none";
          this.style.opacity = "0.7";

          // Navigate to delete URL
          window.location.href = deleteUrl;
        }
      });
    }
  });
}

/**
 * Show confirmation dialog (works for both mobile and desktop)
 * @param {string} dateRange - Date range of the list
 * @param {string} groupName - Name of the group
 * @returns {Promise<boolean>} - Whether deletion was confirmed
 */
async function showConfirmDialog(dateRange, groupName) {
  const message = `Möchten Sie diese Einkaufsliste wirklich löschen?\n\nListe: ${dateRange}\nGruppe: ${groupName}`;

  // For mobile devices, use custom modal
  if (window.innerWidth <= 768) {
    return await showMobileConfirm(message);
  }

  // For desktop, use native confirm
  return confirm(message);
}

/**
 * Navigate to list (used by onclick handlers in template)
 * @param {string} url - The URL to navigate to
 */
function navigateToList(url) {
  // Add loading state
  const clickedElement = event.target.closest(".clickable-row, .list-card");
  if (clickedElement) {
    addLoadingState(clickedElement);
  }

  // Navigate after short delay for visual feedback
  setTimeout(() => {
    window.location.href = url;
  }, 150);
}

/**
 * Show mobile-friendly confirmation dialog
 * @param {string} message - Confirmation message
 * @returns {Promise<boolean>} - Whether action was confirmed
 */
function showMobileConfirm(message) {
  return new Promise((resolve) => {
    // Create custom modal for better mobile experience
    const modal = document.createElement("div");
    modal.className = "mobile-confirm-modal";
    modal.innerHTML = `
      <div class="mobile-confirm-backdrop"></div>
      <div class="mobile-confirm-dialog">
        <div class="mobile-confirm-header">
          <h4>⚠️ Bestätigung erforderlich</h4>
        </div>
        <div class="mobile-confirm-body">
          <p>${message.replace(/\n/g, "<br>")}</p>
        </div>
        <div class="mobile-confirm-actions">
          <button type="button" class="btn-custom btn-light-custom cancel-btn">
            <i class="bi bi-x-circle"></i>
            <span>Abbrechen</span>
          </button>
          <button type="button" class="btn-custom btn-danger-custom confirm-btn">
            <i class="bi bi-trash3"></i>
            <span>Löschen</span>
          </button>
        </div>
      </div>
    `;

    // Add modal styles if not already present
    addModalStyles();

    document.body.appendChild(modal);
    document.body.style.overflow = "hidden"; // Prevent background scrolling

    const confirmBtn = modal.querySelector(".confirm-btn");
    const cancelBtn = modal.querySelector(".cancel-btn");
    const backdrop = modal.querySelector(".mobile-confirm-backdrop");

    const cleanup = () => {
      document.body.style.overflow = "";
      if (document.body.contains(modal)) {
        document.body.removeChild(modal);
      }
    };

    // Handle confirm
    confirmBtn.addEventListener("click", () => {
      cleanup();
      resolve(true);
    });

    // Handle cancel
    cancelBtn.addEventListener("click", () => {
      cleanup();
      resolve(false);
    });

    // Handle backdrop click
    backdrop.addEventListener("click", () => {
      cleanup();
      resolve(false);
    });

    // Handle escape key
    const handleEscape = (e) => {
      if (e.key === "Escape") {
        cleanup();
        resolve(false);
        document.removeEventListener("keydown", handleEscape);
      }
    };
    document.addEventListener("keydown", handleEscape);

    // Focus on cancel button initially for accessibility
    setTimeout(() => {
      cancelBtn.focus();
    }, 100);
  });
}

/**
 * Add modal styles dynamically
 */
function addModalStyles() {
  if (document.getElementById("mobile-confirm-styles")) return;

  const styles = document.createElement("style");
  styles.id = "mobile-confirm-styles";
  styles.textContent = `
    .mobile-confirm-modal {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: 9999;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1rem;
    }
    
    .mobile-confirm-backdrop {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.6);
      backdrop-filter: blur(5px);
      -webkit-backdrop-filter: blur(5px);
    }
    
    .mobile-confirm-dialog {
      background: white;
      border-radius: 20px;
      box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4);
      position: relative;
      max-width: 450px;
      width: 100%;
      animation: modalSlideIn 0.3s ease-out;
      border: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    @keyframes modalSlideIn {
      from {
        opacity: 0;
        transform: translateY(-30px) scale(0.9);
      }
      to {
        opacity: 1;
        transform: translateY(0) scale(1);
      }
    }
    
    .mobile-confirm-header {
      padding: 1.5rem 1.5rem 1rem;
      border-bottom: 2px solid #e9ecef;
    }
    
    .mobile-confirm-header h4 {
      margin: 0;
      color: #dc3545;
      font-weight: 700;
      font-size: 1.2rem;
      text-align: center;
    }
    
    .mobile-confirm-body {
      padding: 1.5rem;
    }
    
    .mobile-confirm-body p {
      margin: 0;
      color: #495057;
      line-height: 1.6;
      font-size: 1rem;
      text-align: center;
    }
    
    .mobile-confirm-actions {
      padding: 1rem 1.5rem 1.5rem;
      display: flex;
      gap: 1rem;
      justify-content: center;
    }
    
    .btn-danger-custom {
      background: linear-gradient(135deg, #dc3545, #c82333);
      color: white;
      text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    }
    
    .btn-danger-custom:hover {
      background: linear-gradient(135deg, #c82333, #a71e2a);
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(220, 53, 69, 0.3);
    }
    
    @media (max-width: 480px) {
      .mobile-confirm-actions {
        flex-direction: column-reverse;
        gap: 0.75rem;
      }
      
      .mobile-confirm-actions .btn-custom {
        width: 100%;
        justify-content: center;
        padding: 0.875rem 1.5rem;
      }
      
      .mobile-confirm-dialog {
        margin: 1rem;
        max-width: calc(100% - 2rem);
      }
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
      .mobile-confirm-dialog {
        background: #343a40;
        color: #f8f9fa;
        border: 2px solid rgba(255, 255, 255, 0.1);
      }
      
      .mobile-confirm-header {
        border-bottom-color: rgba(255, 255, 255, 0.1);
      }
      
      .mobile-confirm-header h4 {
        color: #ff6b7a;
      }
      
      .mobile-confirm-body p {
        color: #f8f9fa;
      }
    }
  `;

  document.head.appendChild(styles);
}

/**
 * Setup touch handlers for better mobile interaction
 */
function setupTouchHandlers() {
  // Add touch feedback to cards and rows
  const touchElements = document.querySelectorAll(".clickable-row, .list-card");

  touchElements.forEach((element) => {
    element.addEventListener(
      "touchstart",
      function () {
        this.style.transform = "scale(0.98)";
      },
      { passive: true }
    );

    element.addEventListener(
      "touchend",
      function () {
        setTimeout(() => {
          this.style.transform = "";
        }, 150);
      },
      { passive: true }
    );

    element.addEventListener(
      "touchcancel",
      function () {
        this.style.transform = "";
      },
      { passive: true }
    );
  });

  // Prevent double-tap zoom on action buttons
  const actionButtons = document.querySelectorAll(".action-btn");
  actionButtons.forEach((button) => {
    button.addEventListener("touchend", function (e) {
      e.preventDefault();
      // Trigger click after preventing default
      setTimeout(() => {
        this.click();
      }, 0);
    });
  });
}

/**
 * Setup keyboard navigation for accessibility
 */
function setupKeyboardNavigation() {
  const rows = document.querySelectorAll(".clickable-row, .list-card");

  rows.forEach((row, index) => {
    // Make rows focusable
    row.setAttribute("tabindex", "0");

    row.addEventListener("keydown", function (e) {
      switch (e.key) {
        case "Enter":
        case " ":
          e.preventDefault();
          this.click();
          break;
        case "ArrowDown":
          e.preventDefault();
          const nextRow = rows[index + 1];
          if (nextRow) nextRow.focus();
          break;
        case "ArrowUp":
          e.preventDefault();
          const prevRow = rows[index - 1];
          if (prevRow) prevRow.focus();
          break;
      }
    });
  });
}

/**
 * Setup refresh button with loading state
 */
function setupRefreshButton() {
  const refreshBtn = document.querySelector('a[href*="Einkaufsliste_index"]');

  if (refreshBtn) {
    refreshBtn.addEventListener("click", function (e) {
      // Add loading spinner
      const icon = this.querySelector("i");
      if (icon) {
        icon.className = "loading-spinner";
      }

      // Add loading text for better UX
      const textSpan = this.querySelector(".btn-text");
      if (textSpan) {
        textSpan.textContent = "Wird aktualisiert...";
      }
    });
  }
}

/**
 * Add loading states for better user feedback
 */
function addLoadingStates() {
  const buttons = document.querySelectorAll(".btn-custom");

  buttons.forEach((button) => {
    button.addEventListener("click", function () {
      // Don't add loading state to delete buttons (handled separately)
      if (
        this.classList.contains("delete-icon") ||
        this.href?.includes("delete_list")
      ) {
        return;
      }

      addLoadingState(this);
    });
  });
}

/**
 * Add loading state to an element
 * @param {HTMLElement} element - Element to add loading state to
 */
function addLoadingState(element) {
  element.style.opacity = "0.7";
  element.style.pointerEvents = "none";

  const icon = element.querySelector("i");
  if (icon && !icon.classList.contains("loading-spinner")) {
    icon.dataset.originalClass = icon.className;
    icon.className = "loading-spinner";
  }
}

/**
 * Handle viewport changes and responsive adjustments
 */
function handleViewportChanges() {
  let resizeTimeout;

  window.addEventListener("resize", function () {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
      // Adjust layout based on new viewport size
      adjustLayoutForViewport();
    }, 250);
  });

  // Initial adjustment
  adjustLayoutForViewport();
}

/**
 * Adjust layout based on current viewport
 */
function adjustLayoutForViewport() {
  const isMobile = window.innerWidth <= 768;
  const container = document.querySelector(".einkaufsliste-container");

  if (container) {
    // Adjust container padding based on screen size
    if (window.innerWidth <= 480) {
      container.style.padding = "0.75rem";
    } else if (window.innerWidth <= 768) {
      container.style.padding = "1rem";
    } else {
      container.style.padding = "2rem";
    }
  }

  // Adjust table vs card view
  const desktopView = document.querySelector(".desktop-view");
  const mobileView = document.querySelector(".mobile-view");

  if (desktopView && mobileView) {
    if (isMobile) {
      desktopView.style.display = "none";
      mobileView.style.display = "block";
    } else {
      desktopView.style.display = "block";
      mobileView.style.display = "none";
    }
  }
}

/**
 * Utility function to detect if device supports touch
 * @returns {boolean} - Whether device supports touch
 */
function isTouchDevice() {
  return (
    "ontouchstart" in window ||
    navigator.maxTouchPoints > 0 ||
    navigator.msMaxTouchPoints > 0
  );
}

/**
 * Add swipe gestures for mobile cards
 */
function addSwipeGestures() {
  if (!isTouchDevice()) return;

  const cards = document.querySelectorAll(".list-card");

  cards.forEach((card) => {
    let startX = 0;
    let startY = 0;
    let isScrolling = false;

    card.addEventListener(
      "touchstart",
      function (e) {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
        isScrolling = false;
      },
      { passive: true }
    );

    card.addEventListener(
      "touchmove",
      function (e) {
        if (!startX || !startY) return;

        const currentX = e.touches[0].clientX;
        const currentY = e.touches[0].clientY;

        const diffX = Math.abs(currentX - startX);
        const diffY = Math.abs(currentY - startY);

        // Determine if user is scrolling vertically
        if (diffY > diffX) {
          isScrolling = true;
        }

        // If swiping horizontally, show action hint
        if (!isScrolling && diffX > 50) {
          this.style.transform = `translateX(${(currentX - startX) * 0.3}px)`;
          this.style.opacity = "0.8";
        }
      },
      { passive: true }
    );

    card.addEventListener(
      "touchend",
      function (e) {
        if (!isScrolling && startX) {
          const endX = e.changedTouches[0].clientX;
          const diffX = endX - startX;

          // Reset transform
          this.style.transform = "";
          this.style.opacity = "";

          // If swiped significantly, show action buttons
          if (Math.abs(diffX) > 100) {
            const actionButtons = this.querySelector(".card-actions");
            if (actionButtons) {
              actionButtons.style.opacity = "1";
              actionButtons.style.transform = "scale(1.1)";

              setTimeout(() => {
                actionButtons.style.transform = "";
              }, 200);
            }
          }
        }

        startX = 0;
        startY = 0;
      },
      { passive: true }
    );
  });
}

// Initialize swipe gestures after DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  setTimeout(addSwipeGestures, 100);
});

/**
 * Handle print functionality for mobile devices
 */
function setupPrintStyles() {
  // Add print-specific styles if user tries to print
  window.addEventListener("beforeprint", function () {
    document.body.classList.add("printing");
  });

  window.addEventListener("afterprint", function () {
    document.body.classList.remove("printing");
  });
}

// Initialize print handling
setupPrintStyles();

/**
 * Performance optimization: Intersection Observer for animations
 */
function setupIntersectionObserver() {
  if (!("IntersectionObserver" in window)) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("animate-in");
        }
      });
    },
    {
      threshold: 0.1,
      rootMargin: "50px",
    }
  );

  // Observe cards and rows for staggered animations
  const elements = document.querySelectorAll(".list-card, .clickable-row");
  elements.forEach((el) => observer.observe(el));
}

// Initialize intersection observer
if (window.innerWidth <= 768) {
  setupIntersectionObserver();
}

// Aktuelles Datum setzen
function updateDateTime() {
  const now = new Date();
  const options = {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  };

  const dateElement = document.getElementById("currentDate");
  const lastUpdatedElement = document.getElementById("lastUpdated");

  if (dateElement) {
    dateElement.textContent = now.toLocaleDateString("de-DE", options);
  }

  if (lastUpdatedElement) {
    lastUpdatedElement.textContent = now.toLocaleTimeString("de-DE", {
      hour: "2-digit",
      minute: "2-digit",
    });
  }
}

// Beim Laden der Seite aufrufen
document.addEventListener("DOMContentLoaded", updateDateTime);

// Clickable rows für bessere Accessibility
document.querySelectorAll(".clickable-row").forEach((row) => {
  row.addEventListener("keydown", function (e) {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      this.click();
    }
  });
  row.setAttribute("tabindex", "0");
  row.setAttribute("role", "button");
});

// Mobile cards für bessere Accessibility
document.querySelectorAll(".list-card").forEach((card) => {
  card.addEventListener("keydown", function (e) {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      this.click();
    }
  });
  card.setAttribute("tabindex", "0");
  card.setAttribute("role", "button");
});

// Confirm dialogs mit besserem Styling
function confirmDelete(groupName) {
  return confirm(
    `Möchten Sie die Gruppe "${groupName}" wirklich löschen?\n\nDiese Aktion kann nicht rückgängig gemacht werden.`
  );
}

// Globale Funktionen für Kompatibilität mit bestehenden onclick-Handlers
function openDeleteModal(groupId, groupName, memberCount, deleteUrl) {
  deleteModal.open(groupId, groupName, memberCount, deleteUrl);
}

function closeDeleteModal() {
  deleteModal.close();
}

// Zusätzliche CSS-Animation per JavaScript hinzufügen
const style = document.createElement("style");
style.textContent = `
    @keyframes modalBounceIn {
        0% {
            transform: scale(0.3) translateY(-50px);
            opacity: 0;
        }
        50% {
            transform: scale(1.05) translateY(-10px);
        }
        70% {
            transform: scale(0.98) translateY(0);
        }
        100% {
            transform: scale(1) translateY(0);
            opacity: 1;
        }
    }
    
    /* Loading state für Delete-Button */
    .btn-danger.loading {
        pointer-events: none;
        opacity: 0.7;
        position: relative;
    }
    
    .btn-danger.loading::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 20px;
        height: 20px;
        border: 2px solid transparent;
        border-top: 2px solid white;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    .btn-danger.loading .btn-text {
        opacity: 0;
    }
    
    @keyframes spin {
        0% { transform: translate(-50%, -50%) rotate(0deg); }
        100% { transform: translate(-50%, -50%) rotate(360deg); }
    }
`;
document.head.appendChild(style);

// Enhanced delete functionality mit Loading-State
document.addEventListener("DOMContentLoaded", function () {
  const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");

  if (confirmDeleteBtn) {
    confirmDeleteBtn.addEventListener("click", function (e) {
      // Loading-State aktivieren
      this.classList.add("loading");
      this.innerHTML = '<span class="btn-text">Gruppe löschen</span>';

      // Nach kurzer Verzögerung zur ursprünglichen Aktion weiterleiten
      setTimeout(() => {
        window.location.href = this.href;
      }, 500);
    });
  }

  // Datum und Zeit Updates (bestehender Code verbessert)
  updateDateTime();

  // Update alle 30 Sekunden
  setInterval(updateDateTime, 30000);
});

function updateDateTime() {
  const now = new Date();

  const currentDateEl = document.getElementById("currentDate");
  if (currentDateEl) {
    currentDateEl.textContent = now.toLocaleDateString("de-DE", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  }

  const lastUpdatedEl = document.getElementById("lastUpdated");
  if (lastUpdatedEl) {
    lastUpdatedEl.textContent = now.toLocaleTimeString("de-DE", {
      hour: "2-digit",
      minute: "2-digit",
    });
  }
}

// Keyboard Navigation für Tabelle (Bonus-Feature)
document.addEventListener("keydown", function (e) {
  if (deleteModal.isOpen) return; // Ignore wenn Modal offen ist

  const rows = document.querySelectorAll(".clickable-row");
  let currentIndex = -1;

  // Finde aktuell fokussierte Zeile
  rows.forEach((row, index) => {
    if (row === document.activeElement) {
      currentIndex = index;
    }
  });

  // Arrow key navigation
  if (e.key === "ArrowDown") {
    e.preventDefault();
    const nextIndex = Math.min(currentIndex + 1, rows.length - 1);
    if (rows[nextIndex]) {
      rows[nextIndex].focus();
    }
  } else if (e.key === "ArrowUp") {
    e.preventDefault();
    const prevIndex = Math.max(currentIndex - 1, 0);
    if (rows[prevIndex]) {
      rows[prevIndex].focus();
    }
  } else if (e.key === "Enter" && currentIndex >= 0) {
    e.preventDefault();
    rows[currentIndex].click();
  }
});

// Mache Zeilen fokussierbar für Keyboard Navigation
document.querySelectorAll(".clickable-row").forEach((row) => {
  row.setAttribute("tabindex", "0");
  row.style.outline = "none";

  // Focus-Style per JavaScript
  row.addEventListener("focus", function () {
    this.style.boxShadow = "0 0 0 3px rgba(13, 110, 253, 0.25)";
  });

  row.addEventListener("blur", function () {
    this.style.boxShadow = "";
  });
});

/**
 * INTEGRIERTE MODAL-LÖSUNG
 * Fügen Sie diesen Code zu Ihrer bestehenden Einkaufsliste.js hinzu
 * oder ersetzen Sie die Modal-Funktionalität komplett
 */

// Universal Modal Manager - Behandelt beide Modal-Typen
class UniversalModalManager {
  constructor() {
    this.modals = new Map();
    this.currentModal = null;
    this.init();
  }

  init() {
    // Alle verfügbaren Modals finden und initialisieren
    this.initializeModal("deleteModal", "group");
    this.initializeModal("deleteListModal", "list");

    // Globale Event Listeners
    this.addGlobalEventListeners();
  }

  initializeModal(modalId, type) {
    const modalElement = document.getElementById(modalId);
    if (!modalElement) {
      console.log(`Modal ${modalId} not found - skipping initialization`);
      return;
    }

    const modal = {
      element: modalElement,
      type: type,
      isOpen: false,
    };

    this.modals.set(modalId, modal);
    this.setupModalEventListeners(modal);

    // ARIA Attributes setzen
    modalElement.setAttribute("aria-hidden", "true");
    modalElement.setAttribute("role", "dialog");

    console.log(`✓ Modal ${modalId} (${type}) initialized successfully`);
  }

  setupModalEventListeners(modal) {
    const { element } = modal;

    // Overlay click zum Schließen
    element.addEventListener("click", (e) => {
      if (e.target === element) {
        this.closeModal(element.id);
      }
    });

    // Modal content clicks verhindern das Schließen
    const modalContainer = element.querySelector(".modal-container");
    if (modalContainer) {
      modalContainer.addEventListener("click", (e) => {
        e.stopPropagation();
      });
    }

    // Close button
    const closeBtn = element.querySelector(".modal-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => this.closeModal(element.id));
    }

    // Cancel button
    const cancelBtn = element.querySelector(".btn-secondary");
    if (cancelBtn) {
      cancelBtn.addEventListener("click", () => this.closeModal(element.id));
    }
  }

  addGlobalEventListeners() {
    // ESC key zum Schließen aller Modals
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && this.currentModal) {
        this.closeModal(this.currentModal);
      }
    });
  }

  openModal(modalId, data = {}) {
    const modal = this.modals.get(modalId);
    if (!modal) {
      console.error(`Modal ${modalId} not found`);
      return;
    }

    // Andere Modals schließen
    this.closeAllModals();

    // Modal-spezifische Daten setzen
    this.setModalData(modal, data);

    // Modal anzeigen
    modal.element.classList.add("show");
    modal.isOpen = true;
    this.currentModal = modalId;

    // Hintergrund-Scroll deaktivieren
    document.body.style.overflow = "hidden";

    // Accessibility
    modal.element.setAttribute("aria-hidden", "false");
    this.focusModal(modal.element);

    // Animation
    this.animateModalOpen(modal.element);

    console.log(`✓ Modal ${modalId} opened`);
  }

  closeModal(modalId) {
    const modal = this.modals.get(modalId);
    if (!modal || !modal.isOpen) return;

    // Modal ausblenden
    modal.element.classList.remove("show");
    modal.isOpen = false;
    this.currentModal = null;

    // Hintergrund-Scroll wieder aktivieren
    document.body.style.overflow = "";

    // Accessibility
    modal.element.setAttribute("aria-hidden", "true");

    // Spezifische Cleanup-Aktionen
    this.cleanupModal(modal);

    console.log(`✓ Modal ${modalId} closed`);
  }

  closeAllModals() {
    this.modals.forEach((modal, modalId) => {
      if (modal.isOpen) {
        this.closeModal(modalId);
      }
    });
  }

  setModalData(modal, data) {
    const { element, type } = modal;

    if (type === "group") {
      this.setGroupModalData(element, data);
    } else if (type === "list") {
      this.setListModalData(element, data);
    }
  }

  setGroupModalData(element, data) {
    const { groupName, memberCount, deleteUrl } = data;

    const groupNameEl = element.querySelector("#modalGroupName");
    const memberCountEl = element.querySelector("#modalMemberCount");
    const confirmBtn = element.querySelector("#confirmDeleteBtn");

    if (groupNameEl) groupNameEl.textContent = groupName || "";
    if (memberCountEl) {
      const memberText = `${memberCount || 0} Mitglied${
        memberCount !== 1 ? "er" : ""
      }`;
      memberCountEl.textContent = memberText;
    }
    if (confirmBtn) confirmBtn.href = deleteUrl || "#";
  }

  setListModalData(element, data) {
    const { dateRange, groupName, deleteUrl, isActive } = data;

    const dateRangeEl = element.querySelector("#modalListDateRange");
    const groupNameEl = element.querySelector("#modalListGroupName");
    const statusEl = element.querySelector("#modalListStatus");
    const confirmBtn = element.querySelector("#confirmListDeleteBtn");

    if (dateRangeEl) dateRangeEl.textContent = dateRange || "";
    if (groupNameEl) groupNameEl.textContent = groupName || "";
    if (statusEl) {
      if (isActive) {
        statusEl.innerHTML =
          '<span style="color: #198754; font-weight: 700;"><i class="bi bi-star-fill"></i> Aktiv</span>';
        this.addActiveListWarning(element);
      } else {
        statusEl.innerHTML =
          '<span style="color: #6c757d; font-weight: 600;"><i class="bi bi-star"></i> Inaktiv</span>';
        this.removeActiveListWarning(element);
      }
    }
    if (confirmBtn) confirmBtn.href = deleteUrl || "#";
  }

  addActiveListWarning(element) {
    let warningEl = element.querySelector(".active-list-warning");
    if (!warningEl) {
      warningEl = document.createElement("div");
      warningEl.className = "active-list-warning";
      warningEl.style.cssText = `
                background: rgba(255, 193, 7, 0.15);
                border: 2px solid rgba(255, 193, 7, 0.4);
                border-radius: 8px;
                padding: 1rem;
                margin-top: 1rem;
                color: #856404;
                font-weight: 600;
                font-size: 0.9rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                animation: pulse-warning-soft 2s infinite;
            `;

      const warningBox = element.querySelector(".modal-warning-box");
      if (warningBox && warningBox.parentNode) {
        warningBox.parentNode.insertBefore(warningEl, warningBox.nextSibling);
      }
    }

    warningEl.innerHTML = `
            <i class="bi bi-star-fill" style="color: #ffc107;"></i>
            Diese Liste ist derzeit aktiv! Das Löschen betrifft alle Gruppenmitglieder.
        `;
  }

  removeActiveListWarning(element) {
    const warningEl = element.querySelector(".active-list-warning");
    if (warningEl) {
      warningEl.remove();
    }
  }

  cleanupModal(modal) {
    if (modal.type === "list") {
      this.removeActiveListWarning(modal.element);
    }
  }

  focusModal(element) {
    const focusableElements = element.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    if (focusableElements.length > 0) {
      focusableElements[0].focus();
    }
  }

  animateModalOpen(element) {
    const container = element.querySelector(".modal-container");
    if (container) {
      container.style.animation = "modalBounceIn 0.4s ease-out";
    }
  }
}

// Globale Modal-Manager Instanz
let modalManager = null;

// Sichere Initialisierung wenn DOM bereit ist
function initializeModalManager() {
  if (!modalManager) {
    modalManager = new UniversalModalManager();
  }
  return modalManager;
}

// Globale Funktionen für Kompatibilität mit bestehenden onclick-Handlers
function openDeleteModal(groupId, groupName, memberCount, deleteUrl) {
  const manager = modalManager || initializeModalManager();
  manager.openModal("deleteModal", {
    groupName,
    memberCount,
    deleteUrl,
  });
}

function closeDeleteModal() {
  if (modalManager) {
    modalManager.closeModal("deleteModal");
  }
}

function openListDeleteModal(
  dateRange,
  groupName,
  deleteUrl,
  isActive = false
) {
  const manager = modalManager || initializeModalManager();
  manager.openModal("deleteListModal", {
    dateRange,
    groupName,
    deleteUrl,
    isActive,
  });
}

function closeListDeleteModal() {
  if (modalManager) {
    modalManager.closeModal("deleteListModal");
  }
}

// Navigation-Funktion
function navigateToList(url) {
  if (url && url !== "#") {
    window.location.href = url;
  }
}

// DateTime Updates
function updateCurrentDateTime() {
  const now = new Date();

  const currentDateEl = document.querySelector(".current-date");
  if (currentDateEl) {
    currentDateEl.textContent = now.toLocaleDateString("de-DE", {
      day: "2-digit",
      month: "long",
      year: "numeric",
    });
  }

  const footerTimeEl = document.querySelector(
    "#footer-time-text, .footer-time small"
  );
  if (footerTimeEl) {
    footerTimeEl.textContent = `Letzte Aktualisierung: ${now.toLocaleTimeString(
      "de-DE",
      {
        hour: "2-digit",
        minute: "2-digit",
      }
    )}`;
  }
}

// Loading-State Management
function addLoadingStateToButton(button, text = "Wird bearbeitet...") {
  if (!button) return;

  button.classList.add("loading");
  button.disabled = true;

  const originalContent = button.innerHTML;
  button.setAttribute("data-original-content", originalContent);
  button.innerHTML = `<span class="btn-text">${text}</span>`;
}

// DOM Ready Handler
function handleDOMReady() {
  console.log("🚀 Enhanced Modal System Loading...");

  // Modal Manager initialisieren
  initializeModalManager();

  // DateTime Updates
  updateCurrentDateTime();
  setInterval(updateCurrentDateTime, 60000);

  // Loading-States für Delete-Buttons
  const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
  if (confirmDeleteBtn) {
    confirmDeleteBtn.addEventListener("click", function (e) {
      addLoadingStateToButton(this, "Gruppe wird gelöscht...");
      setTimeout(() => {
        if (this.href && this.href !== "#") {
          window.location.href = this.href;
        }
      }, 500);
    });
  }

  const confirmListDeleteBtn = document.getElementById("confirmListDeleteBtn");
  if (confirmListDeleteBtn) {
    confirmListDeleteBtn.addEventListener("click", function (e) {
      addLoadingStateToButton(this, "Liste wird gelöscht...");
      setTimeout(() => {
        if (this.href && this.href !== "#") {
          window.location.href = this.href;
        }
      }, 500);
    });
  }

  console.log("✅ Enhanced Modal System Ready");
}

// Multiple DOM Ready Handler für maximale Kompatibilität
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", handleDOMReady);
} else {
  // DOM ist bereits geladen
  handleDOMReady();
}

// Fallback für ältere Browser
if (document.addEventListener) {
  document.addEventListener("DOMContentLoaded", handleDOMReady, false);
} else if (document.attachEvent) {
  document.attachEvent("onreadystatechange", function () {
    if (document.readyState === "complete") {
      handleDOMReady();
    }
  });
}

// CSS Styles per JavaScript hinzufügen (falls externe CSS nicht geladen wird)
function injectModalStyles() {
  if (document.getElementById("modal-styles-injected")) return;

  const style = document.createElement("style");
  style.id = "modal-styles-injected";
  style.textContent = `
        @keyframes modalBounceIn {
            0% { transform: scale(0.3) translateY(-50px); opacity: 0; }
            50% { transform: scale(1.05) translateY(-10px); }
            70% { transform: scale(0.98) translateY(0); }
            100% { transform: scale(1) translateY(0); opacity: 1; }
        }
        
        @keyframes pulse-warning-soft {
            0%, 70%, 100% { transform: scale(1); box-shadow: 0 2px 8px rgba(255, 193, 7, 0.1); }
            35% { transform: scale(1.01); box-shadow: 0 4px 12px rgba(255, 193, 7, 0.2); }
        }
        
        .btn.loading { pointer-events: none; opacity: 0.7; position: relative; }
        .btn.loading::after {
            content: ''; position: absolute; top: 50%; left: 50%;
            transform: translate(-50%, -50%); width: 20px; height: 20px;
            border: 2px solid transparent; border-top: 2px solid white;
            border-radius: 50%; animation: spin 1s linear infinite;
        }
        .btn.loading .btn-text { opacity: 0; }
        
        @keyframes spin {
            0% { transform: translate(-50%, -50%) rotate(0deg); }
            100% { transform: translate(-50%, -50%) rotate(360deg); }
        }
    `;
  document.head.appendChild(style);
}

// Styles injizieren wenn DOM bereit ist
document.addEventListener("DOMContentLoaded", injectModalStyles);

// Error Handling
window.addEventListener("error", function (e) {
  if (e.error && e.error.message && e.error.message.includes("modal")) {
    console.error("Modal Error caught:", e.error);
    // Fallback: Page reload option
    if (
      confirm("Ein Fehler mit den Modals ist aufgetreten. Seite neu laden?")
    ) {
      window.location.reload();
    }
  }
});

console.log("📦 Universal Modal Manager loaded");

/**
 * SOFORTIGE LÖSUNG: Ersetzen Sie Ihre bestehende GroupDeleteModal Klasse
 * in der Einkaufsliste.js komplett durch diese Version
 */

// 1. LÖSCHEN Sie die alte GroupDeleteModal Klasse komplett
// 2. ERSETZEN Sie sie durch diese sichere Version:

class GroupDeleteModal {
  constructor() {
    this.modal = document.getElementById("deleteModal");
    this.isOpen = false;

    // KRITISCH: Prüfen ob Modal existiert
    if (!this.modal) {
      console.log(
        "GroupDeleteModal: Modal element not found - skipping initialization"
      );
      return;
    }

    console.log("✓ GroupDeleteModal: Modal found - initializing");
    this.init();
  }

  init() {
    // Nur initialisieren wenn Modal existiert
    if (!this.modal) return;

    this.addEventListeners();

    // Prevent modal content clicks from closing modal
    const modalContainer = this.modal.querySelector(".modal-container");
    if (modalContainer) {
      modalContainer.addEventListener("click", (e) => {
        e.stopPropagation();
      });
    }
  }

  addEventListeners() {
    // SICHERE Event Listener - nur wenn Modal existiert
    if (!this.modal) {
      console.warn(
        "GroupDeleteModal: Cannot add event listeners - modal is null"
      );
      return;
    }

    // Overlay click zum Schließen
    this.modal.addEventListener("click", (e) => {
      if (e.target === this.modal) {
        this.close();
      }
    });

    // ESC key zum Schließen - global listener
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && this.isOpen) {
        this.close();
      }
    });

    // Close button - mit null check
    const closeBtn = this.modal.querySelector(".modal-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => this.close());
    } else {
      console.log("GroupDeleteModal: Close button not found");
    }

    // Cancel button - mit null check
    const cancelBtn = this.modal.querySelector(".btn-secondary");
    if (cancelBtn) {
      cancelBtn.addEventListener("click", () => this.close());
    } else {
      console.log("GroupDeleteModal: Cancel button not found");
    }
  }

  open(groupId, groupName, memberCount, deleteUrl) {
    // Sichere Öffnung nur wenn Modal existiert
    if (!this.modal) {
      console.error("GroupDeleteModal: Cannot open modal - element not found");
      return;
    }

    // Daten in Modal einsetzen
    this.setModalData(groupName, memberCount, deleteUrl);

    // Modal anzeigen
    this.modal.classList.add("show");
    this.isOpen = true;

    // Hintergrund-Scroll deaktivieren
    document.body.style.overflow = "hidden";

    // Focus auf Modal setzen für Accessibility
    this.modal.setAttribute("aria-hidden", "false");
    this.focusModal();

    console.log("✓ GroupDeleteModal: Modal opened successfully");
  }

  close() {
    if (!this.modal || !this.isOpen) return;

    // Modal ausblenden
    this.modal.classList.remove("show");
    this.isOpen = false;

    // Hintergrund-Scroll wieder aktivieren
    document.body.style.overflow = "";

    // Accessibility
    this.modal.setAttribute("aria-hidden", "true");

    console.log("✓ GroupDeleteModal: Modal closed");
  }

  setModalData(groupName, memberCount, deleteUrl) {
    // Sichere Datenaktualisierung mit null checks
    const groupNameEl = document.getElementById("modalGroupName");
    const memberCountEl = document.getElementById("modalMemberCount");
    const confirmBtn = document.getElementById("confirmDeleteBtn");

    if (groupNameEl) {
      groupNameEl.textContent = groupName || "Unbekannte Gruppe";
    } else {
      console.log("GroupDeleteModal: modalGroupName element not found");
    }

    if (memberCountEl) {
      const memberText = `${memberCount || 0} Mitglied${
        memberCount !== 1 ? "er" : ""
      }`;
      memberCountEl.textContent = memberText;
    } else {
      console.log("GroupDeleteModal: modalMemberCount element not found");
    }

    if (confirmBtn) {
      confirmBtn.href = deleteUrl || "#";
    } else {
      console.log("GroupDeleteModal: confirmDeleteBtn element not found");
    }
  }

  focusModal() {
    if (!this.modal) return;

    const focusableElements = this.modal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    if (focusableElements.length > 0) {
      focusableElements[0].focus();
    }
  }
}

// 3. ERSETZEN Sie auch die Initialisierung durch diese sichere Version:

// ALTE Zeile auskommentieren:
// const deleteModal = new GroupDeleteModal();

// NEUE SICHERE Initialisierung:
let deleteModal = null;

// Sichere Initialisierung nur wenn DOM bereit ist
function initializeGroupModal() {
  try {
    if (document.getElementById("deleteModal")) {
      deleteModal = new GroupDeleteModal();
      console.log("✅ GroupDeleteModal initialized successfully");
    } else {
      console.log(
        "ℹ️  GroupDeleteModal: Modal not found on this page - skipping"
      );
    }
  } catch (error) {
    console.error("❌ GroupDeleteModal initialization failed:", error);
  }
}

// DOM Ready Handler
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeGroupModal);
} else {
  // DOM ist bereits geladen
  initializeGroupModal();
}

// 4. SICHERE globale Funktionen (falls noch nicht vorhanden):
function openDeleteModal(groupId, groupName, memberCount, deleteUrl) {
  if (deleteModal && deleteModal.modal) {
    deleteModal.open(groupId, groupName, memberCount, deleteUrl);
  } else {
    console.error("GroupDeleteModal not available");
    // Fallback: Browser-Confirm
    if (confirm(`Gruppe "${groupName}" wirklich löschen?`)) {
      window.location.href = deleteUrl;
    }
  }
}

function closeDeleteModal() {
  if (deleteModal && deleteModal.modal) {
    deleteModal.close();
  }
}

// 5. OPTIONAL: Ähnliche sichere Klasse für ListDeleteModal
class ListDeleteModal {
  constructor() {
    this.modal = document.getElementById("deleteListModal");
    this.isOpen = false;

    if (!this.modal) {
      console.log(
        "ListDeleteModal: Modal element not found - skipping initialization"
      );
      return;
    }

    console.log("✓ ListDeleteModal: Modal found - initializing");
    this.init();
  }

  init() {
    if (!this.modal) return;
    this.addEventListeners();

    const modalContainer = this.modal.querySelector(".modal-container");
    if (modalContainer) {
      modalContainer.addEventListener("click", (e) => {
        e.stopPropagation();
      });
    }
  }

  addEventListeners() {
    if (!this.modal) return;

    this.modal.addEventListener("click", (e) => {
      if (e.target === this.modal) {
        this.close();
      }
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && this.isOpen) {
        this.close();
      }
    });

    const closeBtn = this.modal.querySelector(".modal-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => this.close());
    }

    const cancelBtn = this.modal.querySelector(".btn-secondary");
    if (cancelBtn) {
      cancelBtn.addEventListener("click", () => this.close());
    }
  }

  open(dateRange, groupName, deleteUrl, isActive = false) {
    if (!this.modal) return;

    this.setModalData(dateRange, groupName, deleteUrl, isActive);
    this.modal.classList.add("show");
    this.isOpen = true;
    document.body.style.overflow = "hidden";
    this.modal.setAttribute("aria-hidden", "false");
    this.focusModal();
  }

  close() {
    if (!this.modal || !this.isOpen) return;

    this.modal.classList.remove("show");
    this.isOpen = false;
    document.body.style.overflow = "";
    this.modal.setAttribute("aria-hidden", "true");
    this.removeActiveListWarning();
  }

  setModalData(dateRange, groupName, deleteUrl, isActive) {
    const dateRangeEl = document.getElementById("modalListDateRange");
    const groupNameEl = document.getElementById("modalListGroupName");
    const statusEl = document.getElementById("modalListStatus");
    const confirmBtn = document.getElementById("confirmListDeleteBtn");

    if (dateRangeEl) dateRangeEl.textContent = dateRange || "";
    if (groupNameEl) groupNameEl.textContent = groupName || "";

    if (statusEl) {
      if (isActive) {
        statusEl.innerHTML =
          '<span style="color: #198754; font-weight: 700;"><i class="bi bi-star-fill"></i> Aktiv</span>';
        this.addActiveListWarning();
      } else {
        statusEl.innerHTML =
          '<span style="color: #6c757d; font-weight: 600;"><i class="bi bi-star"></i> Inaktiv</span>';
        this.removeActiveListWarning();
      }
    }

    if (confirmBtn) confirmBtn.href = deleteUrl || "#";
  }

  addActiveListWarning() {
    if (!this.modal) return;

    let warningEl = this.modal.querySelector(".active-list-warning");
    if (!warningEl) {
      warningEl = document.createElement("div");
      warningEl.className = "active-list-warning";
      warningEl.style.cssText = `
                background: rgba(255, 193, 7, 0.15);
                border: 2px solid rgba(255, 193, 7, 0.4);
                border-radius: 8px;
                padding: 1rem;
                margin-top: 1rem;
                color: #856404;
                font-weight: 600;
                font-size: 0.9rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            `;

      const warningBox = this.modal.querySelector(".modal-warning-box");
      if (warningBox && warningBox.parentNode) {
        warningBox.parentNode.insertBefore(warningEl, warningBox.nextSibling);
      }
    }

    warningEl.innerHTML = `
            <i class="bi bi-star-fill" style="color: #ffc107;"></i>
            Diese Liste ist derzeit aktiv! Das Löschen betrifft alle Gruppenmitglieder.
        `;
  }

  removeActiveListWarning() {
    if (!this.modal) return;

    const warningEl = this.modal.querySelector(".active-list-warning");
    if (warningEl) {
      warningEl.remove();
    }
  }

  focusModal() {
    if (!this.modal) return;

    const focusableElements = this.modal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    if (focusableElements.length > 0) {
      focusableElements[0].focus();
    }
  }
}

// ListDeleteModal sichere Initialisierung
let listDeleteModal = null;

function initializeListModal() {
  try {
    if (document.getElementById("deleteListModal")) {
      listDeleteModal = new ListDeleteModal();
      console.log("✅ ListDeleteModal initialized successfully");
    } else {
      console.log(
        "ℹ️  ListDeleteModal: Modal not found on this page - skipping"
      );
    }
  } catch (error) {
    console.error("❌ ListDeleteModal initialization failed:", error);
  }
}

// ListDeleteModal DOM Ready Handler
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeListModal);
} else {
  initializeListModal();
}

// Sichere globale Funktionen für ListDeleteModal
function openListDeleteModal(
  dateRange,
  groupName,
  deleteUrl,
  isActive = false
) {
  if (listDeleteModal && listDeleteModal.modal) {
    listDeleteModal.open(dateRange, groupName, deleteUrl, isActive);
  } else {
    console.error("ListDeleteModal not available");
    // Fallback: Browser-Confirm
    if (
      confirm(
        `Liste "${dateRange}" aus Gruppe "${groupName}" wirklich löschen?`
      )
    ) {
      window.location.href = deleteUrl;
    }
  }
}

function closeListDeleteModal() {
  if (listDeleteModal && listDeleteModal.modal) {
    listDeleteModal.close();
  }
}

// Navigation-Funktion
function navigateToList(url) {
  if (url && url !== "#") {
    window.location.href = url;
  }
}

console.log("🛡️ Safe Modal System loaded with defensive programming");
