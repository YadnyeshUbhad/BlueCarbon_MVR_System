/**
 * Automatic Responsive Navigation System
 * Professional, Clean UI/UX - Completely automatic based on device type
 * No manual intervention required
 */

class AutoResponsiveNav {
    constructor() {
        this.mobileBreakpoint = 768;
        this.tabletBreakpoint = 992;
        this.currentState = 'unknown';
        this.sidebar = null;
        this.overlay = null;
        this.toggleButton = null;
        this.isInitialized = false;
        
        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        // Find sidebar and overlay elements
        this.sidebar = document.querySelector('.sidebar, .admin-sidebar, .ngo-sidebar, .industry-sidebar');
        this.overlay = document.querySelector('.mobile-nav-overlay');
        this.toggleButton = document.querySelector('.mobile-nav-toggle');

        if (!this.sidebar) {
            console.warn('AutoResponsiveNav: No sidebar found');
            return;
        }

        // Initialize responsive state
        this.updateResponsiveState();
        this.attachEventListeners();
        this.isInitialized = true;

        console.log('🎯 AutoResponsiveNav: Initialized successfully');
        console.log(`📱 Current state: ${this.currentState}`);
    }

    updateResponsiveState() {
        const width = window.innerWidth;
        let newState;

        if (width < this.mobileBreakpoint) {
            newState = 'mobile';
        } else if (width < this.tabletBreakpoint) {
            newState = 'tablet';
        } else {
            newState = 'desktop';
        }

        // Only act if state changed
        if (newState !== this.currentState) {
            this.currentState = newState;
            this.applyResponsiveState();
        }
    }

    applyResponsiveState() {
        if (!this.sidebar) return;

        switch (this.currentState) {
            case 'mobile':
            case 'tablet':
                this.enableMobileMode();
                break;
            case 'desktop':
                this.enableDesktopMode();
                break;
        }

        console.log(`🔄 AutoResponsiveNav: Switched to ${this.currentState} mode`);
    }

    enableMobileMode() {
        if (!this.sidebar) return;

        // Force sidebar closed on mobile
        this.sidebar.classList.remove('active');
        if (this.overlay) {
            this.overlay.classList.remove('active');
        }

        // Ensure mobile toggle is visible (CSS handles this, but we can add class for extra specificity)
        if (this.toggleButton) {
            this.toggleButton.classList.add('mobile-visible');
        }

        // Add mobile class to body for additional styling hooks
        document.body.classList.add('mobile-mode');
        document.body.classList.remove('desktop-mode');

        // Prevent body scroll when sidebar is open on mobile
        this.updateBodyScroll();
    }

    enableDesktopMode() {
        if (!this.sidebar) return;

        // Force sidebar visible on desktop (CSS handles positioning)
        this.sidebar.classList.remove('active');
        if (this.overlay) {
            this.overlay.classList.remove('active');
        }

        // Ensure mobile toggle is hidden (CSS handles this)
        if (this.toggleButton) {
            this.toggleButton.classList.remove('mobile-visible');
        }

        // Add desktop class to body
        document.body.classList.add('desktop-mode');
        document.body.classList.remove('mobile-mode');

        // Restore body scroll
        document.body.style.overflow = '';
    }

    toggleMobileNav() {
        if (this.currentState === 'desktop') {
            // Don't allow toggle on desktop
            return;
        }

        if (!this.sidebar || !this.overlay) return;

        const isActive = this.sidebar.classList.contains('active');
        
        if (isActive) {
            this.closeMobileNav();
        } else {
            this.openMobileNav();
        }
    }

    openMobileNav() {
        if (!this.sidebar || !this.overlay) return;

        this.sidebar.classList.add('active');
        this.overlay.classList.add('active');
        
        // Prevent body scroll when menu is open
        document.body.style.overflow = 'hidden';
        
        // Add ARIA attributes for accessibility
        if (this.toggleButton) {
            this.toggleButton.setAttribute('aria-expanded', 'true');
        }
        this.sidebar.setAttribute('aria-hidden', 'false');

        console.log('📱 Mobile nav: Opened');
    }

    closeMobileNav() {
        if (!this.sidebar || !this.overlay) return;

        this.sidebar.classList.remove('active');
        this.overlay.classList.remove('active');
        
        // Restore body scroll
        document.body.style.overflow = '';
        
        // Update ARIA attributes
        if (this.toggleButton) {
            this.toggleButton.setAttribute('aria-expanded', 'false');
        }
        this.sidebar.setAttribute('aria-hidden', 'true');

        console.log('📱 Mobile nav: Closed');
    }

    updateBodyScroll() {
        // Only prevent scroll when sidebar is active on mobile/tablet
        if ((this.currentState === 'mobile' || this.currentState === 'tablet') && 
            this.sidebar && this.sidebar.classList.contains('active')) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
    }

    attachEventListeners() {
        // Throttled resize listener for better performance
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.updateResponsiveState();
            }, 100);
        });

        // Mobile toggle button click
        if (this.toggleButton) {
            this.toggleButton.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.toggleMobileNav();
            });
        }

        // Overlay click to close
        if (this.overlay) {
            this.overlay.addEventListener('click', (e) => {
                e.preventDefault();
                this.closeMobileNav();
            });
        }

        // Close on navigation link click (mobile only)
        const navLinks = document.querySelectorAll('.nav a, .admin-nav a, .sidebar-nav a, .ngo-nav a');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (this.currentState === 'mobile' || this.currentState === 'tablet') {
                    // Small delay to allow navigation to start
                    setTimeout(() => {
                        this.closeMobileNav();
                    }, 150);
                }
            });
        });

        // Handle orientation change
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.updateResponsiveState();
                // Close mobile nav on orientation change to prevent UI issues
                if (this.currentState === 'mobile' || this.currentState === 'tablet') {
                    this.closeMobileNav();
                }
            }, 100);
        });

        // Keyboard accessibility
        document.addEventListener('keydown', (e) => {
            // ESC key to close mobile nav
            if (e.key === 'Escape' && (this.currentState === 'mobile' || this.currentState === 'tablet')) {
                this.closeMobileNav();
            }
            
            // Handle focus trap in mobile nav when open
            if (this.sidebar && this.sidebar.classList.contains('active')) {
                this.handleFocusTrap(e);
            }
        });

        // Handle page visibility change (e.g., tab switching)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                // Close mobile nav when page becomes hidden
                this.closeMobileNav();
            }
        });
    }

    handleFocusTrap(e) {
        if (this.currentState === 'desktop') return;

        const focusableElements = this.sidebar.querySelectorAll(
            'a, button, [tabindex]:not([tabindex="-1"]), input, select, textarea'
        );
        
        if (focusableElements.length === 0) return;

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (e.key === 'Tab') {
            if (e.shiftKey) {
                // Shift + Tab
                if (document.activeElement === firstElement) {
                    e.preventDefault();
                    lastElement.focus();
                }
            } else {
                // Tab
                if (document.activeElement === lastElement) {
                    e.preventDefault();
                    firstElement.focus();
                }
            }
        }
    }

    // Public method to manually refresh the responsive state
    refresh() {
        this.updateResponsiveState();
    }

    // Public method to get current state
    getCurrentState() {
        return this.currentState;
    }

    // Public method to check if mobile mode is active
    isMobileMode() {
        return this.currentState === 'mobile' || this.currentState === 'tablet';
    }

    // Public method for debugging
    getDebugInfo() {
        return {
            currentState: this.currentState,
            windowWidth: window.innerWidth,
            sidebarActive: this.sidebar ? this.sidebar.classList.contains('active') : false,
            overlayActive: this.overlay ? this.overlay.classList.contains('active') : false,
            isInitialized: this.isInitialized
        };
    }
}

// Auto-initialize when script loads
let autoResponsiveNav;

// Initialize with error handling
try {
    autoResponsiveNav = new AutoResponsiveNav();
    
    // Expose globally for debugging and manual control if needed
    window.autoResponsiveNav = autoResponsiveNav;
    
    // Backward compatibility functions
    window.toggleMobileNav = function() {
        if (autoResponsiveNav) {
            autoResponsiveNav.toggleMobileNav();
        }
    };
    
    window.closeMobileNav = function() {
        if (autoResponsiveNav) {
            autoResponsiveNav.closeMobileNav();
        }
    };

} catch (error) {
    console.error('❌ AutoResponsiveNav initialization failed:', error);
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AutoResponsiveNav;
}