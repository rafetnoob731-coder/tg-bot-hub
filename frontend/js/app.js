/* =============================================
   TG BOT HUB - Auth Module
   Authentication & API client
   ============================================= */

const API_BASE = '/api';

class TGBotHubAPI {
    constructor() {
        this.token = localStorage.getItem('tgbh_token') || '';
        this.user = null;
        this.baseUrl = API_BASE;
    }

    isAuthenticated() {
        return !!this.token;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        // Check for API key
        const apiKey = localStorage.getItem('tgbh_api_key');
        if (apiKey && !this.token) {
            headers['X-API-Key'] = apiKey;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers,
                credentials: 'same-origin',
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || data.errors?.[0] || 'Request failed');
            }

            return data;
        } catch (error) {
            if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
                throw new Error('Network error. Please check your connection.');
            }
            throw error;
        }
    }

    // ========== AUTH ==========
    async login(username, password) {
        const data = await this.request('/login', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });
        if (data.success) {
            this.token = data.token;
            this.user = data.user;
            localStorage.setItem('tgbh_token', data.token);
            localStorage.setItem('tgbh_user', JSON.stringify(data.user));
        }
        return data;
    }

    async register(username, email, password, fullName = '') {
        const data = await this.request('/register', {
            method: 'POST',
            body: JSON.stringify({ username, email, password, full_name: fullName }),
        });
        if (data.success) {
            this.token = data.token;
            this.user = data.user;
            localStorage.setItem('tgbh_token', data.token);
            localStorage.setItem('tgbh_user', JSON.stringify(data.user));
        }
        return data;
    }

    async logout() {
        try {
            await this.request('/logout', {
                method: 'POST',
                body: JSON.stringify({ token: this.token }),
            });
        } catch (e) { /* ignore */ }
        this.token = '';
        this.user = null;
        localStorage.removeItem('tgbh_token');
        localStorage.removeItem('tgbh_user');
        window.location.href = '/login.html';
    }

    async getMe() {
        const data = await this.request('/me');
        if (data.success) {
            this.user = data.user;
            localStorage.setItem('tgbh_user', JSON.stringify(data.user));
        }
        return data;
    }

    async changePassword(currentPassword, newPassword) {
        return this.request('/change-password', {
            method: 'POST',
            body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
        });
    }

    // ========== BOTS ==========
    async getBots() {
        return this.request('/bots');
    }

    async getBot(id) {
        return this.request(`/bot?id=${id}`);
    }

    async addBot(name, token, description = '') {
        return this.request('/add-bot', {
            method: 'POST',
            body: JSON.stringify({ name, token, description }),
        });
    }

    async deleteBot(botId) {
        return this.request('/delete-bot', {
            method: 'POST',
            body: JSON.stringify({ bot_id: botId }),
        });
    }

    async startBot(botId) {
        return this.request('/start-bot', {
            method: 'POST',
            body: JSON.stringify({ bot_id: botId }),
        });
    }

    async stopBot(botId) {
        return this.request('/stop-bot', {
            method: 'POST',
            body: JSON.stringify({ bot_id: botId }),
        });
    }

    async restartBot(botId) {
        return this.request('/restart-bot', {
            method: 'POST',
            body: JSON.stringify({ bot_id: botId }),
        });
    }

    async updateBot(botId, data) {
        return this.request('/update-bot', {
            method: 'POST',
            body: JSON.stringify({ bot_id: botId, ...data }),
        });
    }

    async verifyBotToken(token) {
        return this.request('/verify-bot-token', {
            method: 'POST',
            body: JSON.stringify({ token }),
        });
    }

    async getBotStatus(botId) {
        return this.request(`/bot/status?id=${botId}`);
    }

    async setWebhook(botId, webhookUrl) {
        return this.request('/bot/set-webhook', {
            method: 'POST',
            body: JSON.stringify({ bot_id: botId, webhook_url: webhookUrl }),
        });
    }

    async deleteWebhook(botId) {
        return this.request('/bot/delete-webhook', {
            method: 'POST',
            body: JSON.stringify({ bot_id: botId }),
        });
    }

    // ========== COMMANDS ==========
    async getCommands(botId) {
        return this.request(`/commands?bot_id=${botId}`);
    }

    async getCommand(id) {
        return this.request(`/command?id=${id}`);
    }

    async createCommand(botId, command, responseType, response, options = {}) {
        return this.request('/create-command', {
            method: 'POST',
            body: JSON.stringify({
                bot_id: botId,
                command,
                response_type: responseType,
                response,
                ...options,
            }),
        });
    }

    async editCommand(commandId, data) {
        return this.request('/edit-command', {
            method: 'POST',
            body: JSON.stringify({ command_id: commandId, ...data }),
        });
    }

    async deleteCommand(commandId) {
        return this.request('/delete-command', {
            method: 'POST',
            body: JSON.stringify({ command_id: commandId }),
        });
    }

    async toggleCommand(commandId) {
        return this.request('/toggle-command', {
            method: 'POST',
            body: JSON.stringify({ command_id: commandId }),
        });
    }

    async importCommands(botId, commands) {
        return this.request('/commands/import', {
            method: 'POST',
            body: JSON.stringify({ bot_id: botId, commands: JSON.stringify(commands) }),
        });
    }

    async exportCommands(botId) {
        return this.request(`/commands/export?bot_id=${botId}`);
    }

    // ========== STATS & ANALYTICS ==========
    async getStats() {
        return this.request('/stats');
    }

    async getAdminStats() {
        return this.request('/admin/stats');
    }

    async getCommandUsage() {
        return this.request('/analytics/command-usage');
    }

    async getEngagement() {
        return this.request('/analytics/engagement');
    }

    async getGrowth() {
        return this.request('/analytics/growth');
    }

    async getTrafficAnalytics() {
        return this.request('/analytics/traffic');
    }

    async getReport(type = 'full') {
        return this.request(`/analytics/report?type=${type}`);
    }

    // ========== USER MANAGEMENT ==========
    async getUsers(page = 1, search = '') {
        return this.request(`/users?page=${page}&search=${encodeURIComponent(search)}`);
    }

    async getUser(id) {
        return this.request(`/user?id=${id}`);
    }

    async updateProfile(fullName, avatar = '') {
        return this.request('/update-profile', {
            method: 'POST',
            body: JSON.stringify({ full_name: fullName, avatar }),
        });
    }

    async enable2FA() {
        return this.request('/enable-2fa', { method: 'POST' });
    }

    async disable2FA() {
        return this.request('/disable-2fa', { method: 'POST' });
    }

    async updateUser(userId, data) {
        return this.request('/admin/update-user', {
            method: 'POST',
            body: JSON.stringify({ user_id: userId, ...data }),
        });
    }

    // ========== SETTINGS ==========
    async saveSetting(key, value) {
        return this.request('/settings', {
            method: 'POST',
            body: JSON.stringify({ key, value }),
        });
    }

    // ========== LOGS ==========
    async getLogs(page = 1) {
        return this.request(`/logs?page=${page}`);
    }

    async getAuditLogs(page = 1) {
        return this.request(`/audit-logs?page=${page}`);
    }

    // ========== BROADCAST ==========
    async broadcast(botId, message, chatIds) {
        return this.request('/broadcast', {
            method: 'POST',
            body: JSON.stringify({ bot_id: botId, message, chat_ids: chatIds }),
        });
    }

    // ========== MARKETPLACE ==========
    async getMarketplace(page = 1, category = '') {
        return this.request(`/marketplace?page=${page}&category=${encodeURIComponent(category)}`);
    }

    async addMarketplaceItem(name, description, price, type, category) {
        return this.request('/marketplace/add', {
            method: 'POST',
            body: JSON.stringify({ name, description, price, type, category }),
        });
    }

    // ========== PLUGINS ==========
    async getPlugins() {
        return this.request('/plugins');
    }

    async togglePlugin(pluginId, isEnabled) {
        return this.request('/plugins/toggle', {
            method: 'POST',
            body: JSON.stringify({ plugin_id: pluginId, is_enabled: isEnabled }),
        });
    }

    // ========== SECURITY ==========
    async getSecurityDashboard() {
        return this.request('/security/dashboard');
    }

    // ========== HEALTH ==========
    async healthCheck() {
        return this.request('/health');
    }
}

// =============================================
// UI UTILITIES
// =============================================

class UI {
    static showToast(message, type = 'info', duration = 4000) {
        const container = document.querySelector('.toast-container');
        if (!container) {
            const div = document.createElement('div');
            div.className = 'toast-container';
            document.body.appendChild(div);
        }

        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️',
        };

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <span class="toast-icon">${icons[type] || 'ℹ️'}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="this.parentElement.remove()">✕</button>
        `;

        document.querySelector('.toast-container').appendChild(toast);

        setTimeout(() => {
            if (toast.parentElement) {
                toast.style.animation = 'none';
                toast.style.opacity = '0';
                toast.style.transform = 'translateX(100%)';
                setTimeout(() => toast.remove(), 300);
            }
        }, duration);
    }

    static showModal(html, options = {}) {
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay active';
        overlay.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3 class="modal-title">${options.title || 'Modal'}</h3>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">✕</button>
                </div>
                <div class="modal-body">
                    ${html}
                </div>
                ${options.footer ? `<div class="modal-footer">${options.footer}</div>` : ''}
            </div>
        `;

        document.body.appendChild(overlay);

        // Close on overlay click
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.remove();
            }
        });

        return overlay;
    }

    static showConfirm(message, title = 'Confirm') {
        return new Promise((resolve) => {
            const overlay = document.createElement('div');
            overlay.className = 'modal-overlay active';
            overlay.innerHTML = `
                <div class="modal">
                    <div class="modal-header">
                        <h3 class="modal-title">${title}</h3>
                        <button class="modal-close" onclick="this.closest('.modal-overlay').remove(); resolve(false)">✕</button>
                    </div>
                    <div class="modal-body">
                        <p style="color: var(--text-secondary);">${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove(); resolve(false)">Cancel</button>
                        <button class="btn btn-danger" onclick="this.closest('.modal-overlay').remove(); resolve(true)">Confirm</button>
                    </div>
                </div>
            `;

            document.body.appendChild(overlay);

            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    overlay.remove();
                    resolve(false);
                }
            });
        });
    }

    static showLoading(container) {
        container.innerHTML = `
            <div class="loading-overlay">
                <div class="spinner spinner-lg"></div>
                <p>Loading...</p>
            </div>
        `;
    }

    static showEmpty(container, { icon = '📦', title = 'Nothing here', message = 'No items to display.', action = '' } = {}) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">${icon}</div>
                <div class="empty-state-title">${title}</div>
                <div class="empty-state-text">${message}</div>
                ${action}
            </div>
        `;
    }

    static showError(container, message = 'An error occurred') {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">❌</div>
                <div class="empty-state-title">Error</div>
                <div class="empty-state-text">${message}</div>
                <button class="btn btn-primary" onclick="location.reload()">Try Again</button>
            </div>
        `;
    }

    static formatDate(dateStr) {
        const date = new Date(dateStr);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
        if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`;
        
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
        });
    }

    static formatNumber(num) {
        if (!num) return '0';
        if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
        return num.toLocaleString();
    }

    static getStatusBadge(status) {
        const statuses = {
            running: '<span class="badge badge-success"><span class="status-dot running"></span>Online</span>',
            online: '<span class="badge badge-success"><span class="status-dot online"></span>Online</span>',
            stopped: '<span class="badge badge-info"><span class="status-dot stopped"></span>Stopped</span>',
            offline: '<span class="badge"><span class="status-dot offline"></span>Offline</span>',
            error: '<span class="badge badge-danger"><span class="status-dot error"></span>Error</span>',
            active: '<span class="badge badge-success">Active</span>',
            inactive: '<span class="badge">Inactive</span>',
        };
        return statuses[status] || `<span class="badge">${status}</span>`;
    }

    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialize global API instance
const api = new TGBotHubAPI();
