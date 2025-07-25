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
