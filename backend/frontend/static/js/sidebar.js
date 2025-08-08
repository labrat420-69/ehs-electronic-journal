/**
 * Sidebar functionality for EHS Electronic Journal
 * Handles collapsible sidebar, navigation, and mobile responsiveness
 */

/**
 * Initialize sidebar functionality
 */
function initializeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const navSections = document.querySelectorAll('.nav-section');
    
    if (!sidebar || !sidebarToggle) return;
    
    // Set initial state from localStorage
    if (EHSJournal.state.sidebarCollapsed) {
        sidebar.classList.add('collapsed');
    }
    
    // Toggle sidebar
    sidebarToggle.addEventListener('click', function() {
        toggleSidebar();
    });
    
    // Initialize navigation sections
    initializeNavSections(navSections);
    
    // Handle mobile responsiveness
    initializeMobileMenu();
    
    // Set active navigation item based on current page
    setActiveNavItem();
}

/**
 * Toggle sidebar collapsed state
 */
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const isCollapsed = sidebar.classList.contains('collapsed');
    
    if (isCollapsed) {
        sidebar.classList.remove('collapsed');
        EHSJournal.state.sidebarCollapsed = false;
    } else {
        sidebar.classList.add('collapsed');
        EHSJournal.state.sidebarCollapsed = true;
    }
    
    // Save state to localStorage
    localStorage.setItem('sidebarCollapsed', EHSJournal.state.sidebarCollapsed.toString());
    
    // Trigger resize event for any charts or components that need to adjust
    setTimeout(() => {
        window.dispatchEvent(new Event('resize'));
    }, 300);
}

/**
 * Initialize navigation sections (collapsible menus)
 */
function initializeNavSections(navSections) {
    navSections.forEach(section => {
        const header = section.querySelector('.nav-section-header');
        const subsection = section.querySelector('.nav-subsection');
        
        if (!header || !subsection) return;
        
        // Check if any subsection link is active
        const hasActiveLink = subsection.querySelector('.nav-link.active');
        if (hasActiveLink) {
            section.classList.add('expanded');
        }
        
        // Add click handler to toggle section
        header.addEventListener('click', function() {
            toggleNavSection(section);
        });
    });
}

/**
 * Toggle navigation section expanded state
 */
function toggleNavSection(section) {
    const isExpanded = section.classList.contains('expanded');
    
    if (isExpanded) {
        section.classList.remove('expanded');
    } else {
        section.classList.add('expanded');
    }
}

/**
 * Initialize mobile menu functionality
 */
function initializeMobileMenu() {
    const sidebar = document.getElementById('sidebar');
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            const isClickInsideSidebar = sidebar.contains(e.target);
            const isToggleButton = e.target.closest('#sidebar-toggle');
            
            if (!isClickInsideSidebar && !isToggleButton && sidebar.classList.contains('mobile-open')) {
                sidebar.classList.remove('mobile-open');
            }
        }
    });
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('mobile-open');
        }
    });
    
    // Modify toggle behavior for mobile
    const sidebarToggle = document.getElementById('sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                sidebar.classList.toggle('mobile-open');
            }
        });
    }
}

/**
 * Set active navigation item based on current page
 */
function setActiveNavItem() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Remove active class from all links
    navLinks.forEach(link => link.classList.remove('active'));
    
    // Find and set active link
    let activeLink = null;
    let bestMatch = 0;
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.startsWith(href) && href.length > bestMatch) {
            activeLink = link;
            bestMatch = href.length;
        }
    });
    
    if (activeLink) {
        activeLink.classList.add('active');
        
        // Expand parent section if link is in a subsection
        const parentSection = activeLink.closest('.nav-section');
        if (parentSection) {
            parentSection.classList.add('expanded');
        }
    }
}

/**
 * Highlight navigation item
 */
function highlightNavItem(path) {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        const href = link.getAttribute('href');
        if (href === path) {
            link.classList.add('active');
            
            // Expand parent section
            const parentSection = link.closest('.nav-section');
            if (parentSection) {
                parentSection.classList.add('expanded');
            }
        }
    });
}

/**
 * Add badge to navigation item
 */
function addNavBadge(selector, text, type = 'primary') {
    const navItem = document.querySelector(selector);
    if (!navItem) return;
    
    // Remove existing badge
    const existingBadge = navItem.querySelector('.nav-badge');
    if (existingBadge) existingBadge.remove();
    
    // Add new badge
    const badge = document.createElement('span');
    badge.className = `badge badge-${type} nav-badge`;
    badge.textContent = text;
    badge.style.marginLeft = 'auto';
    badge.style.fontSize = '0.7rem';
    
    navItem.appendChild(badge);
}

/**
 * Remove badge from navigation item
 */
function removeNavBadge(selector) {
    const navItem = document.querySelector(selector);
    if (!navItem) return;
    
    const badge = navItem.querySelector('.nav-badge');
    if (badge) badge.remove();
}

/**
 * Navigation utilities for programmatic navigation
 */
EHSJournal.nav = {
    /**
     * Navigate to a specific route
     */
    goto(path) {
        window.location.href = path;
    },
    
    /**
     * Navigate back
     */
    back() {
        window.history.back();
    },
    
    /**
     * Reload current page
     */
    reload() {
        window.location.reload();
    },
    
    /**
     * Set active navigation item
     */
    setActive(path) {
        highlightNavItem(path);
    },
    
    /**
     * Add notification badge to nav item
     */
    addBadge(selector, text, type = 'primary') {
        addNavBadge(selector, text, type);
    },
    
    /**
     * Remove notification badge from nav item
     */
    removeBadge(selector) {
        removeNavBadge(selector);
    }
};

// Add CSS for navigation badges
const navStyle = document.createElement('style');
navStyle.textContent = `
    .nav-badge {
        margin-left: auto !important;
        font-size: 0.7rem !important;
        padding: 2px 6px !important;
        min-width: 18px;
        height: 18px;
        display: flex !important;
        align-items: center;
        justify-content: center;
    }
    
    .nav-section-header .nav-badge {
        margin-right: 8px;
        margin-left: auto;
    }
    
    .sidebar.collapsed .nav-link .nav-badge {
        position: absolute;
        right: 8px;
        top: 50%;
        transform: translateY(-50%);
    }
    
    .sidebar.collapsed .nav-link span:not(.nav-badge) {
        opacity: 0;
        width: 0;
        overflow: hidden;
    }
    
    /* Mobile sidebar styles */
    @media (max-width: 768px) {
        .sidebar {
            transform: translateX(-100%);
            transition: transform 0.3s ease-in-out;
        }
        
        .sidebar.mobile-open {
            transform: translateX(0);
        }
        
        .sidebar-toggle {
            display: block;
        }
    }
    
    @media (min-width: 769px) {
        .sidebar.mobile-open {
            transform: none;
        }
    }
`;
document.head.appendChild(navStyle);