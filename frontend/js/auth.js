/* =============================================
   TG BOT HUB - Auth Check & Dashboard Init
   ============================================= */

(function() {
    // Check authentication on page load
    const token = localStorage.getItem('tgbh_token');
    const userData = localStorage.getItem('tgbh_user');
    
    if (token && userData) {
        api.token = token;
        try {
            api.user = JSON.parse(userData);
        } catch (e) {
            api.user = null;
        }
    }

    // Redirect to login if not authenticated (for protected pages)
    const protectedPages = ['dashboard.html', 'admin.html'];
    const currentPage = window.location.pathname.split('/').pop();
    
    if (protectedPages.includes(currentPage)) {
        if (!api.isAuthenticated()) {
            window.location.href = '/login.html';
            return;
        }
    }

    // If on login/register page and already authenticated, redirect to dashboard
    if (['login.html', 'register.html'].includes(currentPage)) {
        if (api.isAuthenticated()) {
            window.location.href = '/dashboard.html';
            return;
        }
    }
})();

// =============================================
// THEME MANAGEMENT
// =============================================

const ThemeManager = {
    init() {
        const saved = localStorage.getItem('tgbh_theme') || 'dark';
        this.setTheme(saved);
    },

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('tgbh_theme', theme);
        
        document.querySelectorAll('.theme-toggle').forEach(btn => {
            btn.innerHTML = theme === 'dark' ? '🌙' : '☀️';
            btn.title = theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode';
        });
    },

    toggle() {
        const current = localStorage.getItem('tgbh_theme') || 'dark';
        this.setTheme(current === 'dark' ? 'light' : 'dark');
    }
};

// =============================================
// SIDEBAR MANAGEMENT
// =============================================

const SidebarManager = {
    init() {
        const toggle = document.querySelector('.mobile-menu-toggle');
        if (toggle) {
            toggle.addEventListener('click', () => {
                document.querySelector('.sidebar').classList.toggle('open');
            });
        }

        // Highlight active nav item
        const currentPage = window.location.pathname.split('/').pop();
        document.querySelectorAll('.nav-item').forEach(item => {
            const href = item.getAttribute('href');
            if (href && currentPage.includes(href.replace('.html', ''))) {
                item.classList.add('active');
            }
        });

        // Close sidebar on nav click (mobile)
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                if (window.innerWidth <= 1024) {
                    document.querySelector('.sidebar').classList.remove('open');
                }
            });
        });
    },

    updateUser(user) {
        const avatarEl = document.querySelector('.sidebar-user-avatar');
        const nameEl = document.querySelector('.sidebar-user-name');
        const roleEl = document.querySelector('.sidebar-user-role');

        if (avatarEl) {
            avatarEl.textContent = (user.full_name || user.username).charAt(0).toUpperCase();
        }
        if (nameEl) {
            nameEl.textContent = user.full_name || user.username;
        }
        if (roleEl) {
            roleEl.textContent = user.role.charAt(0).toUpperCase() + user.role.slice(1);
        }

        // Show/hide admin nav items
        const adminItems = document.querySelectorAll('.nav-item.admin-only');
        adminItems.forEach(item => {
            item.style.display = (user.role === 'admin' || user.role === 'superadmin') ? 'flex' : 'none';
        });
    }
};

// =============================================
// DASHBOARD INITIALIZATION
// =============================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme
    ThemeManager.init();

    // Initialize sidebar
    SidebarManager.init();

    // Update user info if logged in
    if (api.isAuthenticated() && api.user) {
        SidebarManager.updateUser(api.user);
    }

    // Theme toggle listeners
    document.querySelectorAll('.theme-toggle').forEach(btn => {
        btn.addEventListener('click', ThemeManager.toggle);
    });

    // Logout buttons
    document.querySelectorAll('.logout-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const confirmed = await UI.showConfirm('Are you sure you want to logout?', 'Logout');
            if (confirmed) {
                api.logout();
            }
        });
    });

    // Notification bell
    const notifBtn = document.querySelector('.notification-btn');
    if (notifBtn) {
        notifBtn.addEventListener('click', () => {
            UI.showToast('No new notifications', 'info');
        });
    }
});
