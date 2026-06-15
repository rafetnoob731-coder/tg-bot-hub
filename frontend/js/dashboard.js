/* =============================================
   TG BOT HUB - Dashboard JavaScript
   Complete dashboard functionality
   ============================================= */

// =============================================
// DASHBOARD CONTROLLER
// =============================================

const Dashboard = {
    currentPage: 'overview',
    currentView: null,
    selectedBotId: null,
    chartInstances: {},

    async init() {
        this.setupNavigation();
        this.setupSearch();
        this.loadPage('overview');
    },

    setupNavigation() {
        document.querySelectorAll('.nav-item[data-page]').forEach(item => {
            item.addEventListener('click', async (e) => {
                e.preventDefault();
                const page = item.dataset.page;
                
                // Update active nav
                document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
                item.classList.add('active');
                
                await this.loadPage(page);
            });
        });
    },

    setupSearch() {
        const searchInput = document.querySelector('.topbar-search input');
        if (searchInput) {
            const debouncedSearch = UI.debounce((value) => {
                if (this.currentView && this.currentView.search) {
                    this.currentView.search(value);
                }
            }, 300);
            
            searchInput.addEventListener('input', (e) => {
                debouncedSearch(e.target.value);
            });
        }
    },

    async loadPage(page) {
        this.currentPage = page;
        const container = document.getElementById('page-content');
        if (!container) return;

        // Update page title
        const titles = {
            'overview': { title: 'Dashboard Overview', subtitle: 'Welcome back! Here\'s your summary.' },
            'bots': { title: 'Bot Management', subtitle: 'Manage your Telegram bots' },
            'commands': { title: 'Command Manager', subtitle: 'Create and manage bot commands' },
            'analytics': { title: 'Analytics', subtitle: 'Detailed insights and reports' },
            'logs': { title: 'Activity Logs', subtitle: 'Monitor bot activity' },
            'marketplace': { title: 'Bot Marketplace', subtitle: 'Discover and sell bot templates' },
            'plugins': { title: 'Plugin System', subtitle: 'Extend functionality with plugins' },
            'settings': { title: 'Settings', subtitle: 'Configure your account and preferences' },
            'users': { title: 'User Management', subtitle: 'Manage platform users (Admin)' },
            'security': { title: 'Security Dashboard', subtitle: 'Monitor security events' },
            'profile': { title: 'My Profile', subtitle: 'Manage your profile and preferences' },
        };

        const info = titles[page] || { title: 'Dashboard', subtitle: '' };
        document.querySelector('.page-title').textContent = info.title;
        document.querySelector('.page-subtitle').textContent = info.subtitle;

        // Load page content
        switch(page) {
            case 'overview':
                await this.loadOverview(container);
                break;
            case 'bots':
                await this.loadBots(container);
                break;
            case 'commands':
                await this.loadCommands(container);
                break;
            case 'analytics':
                await this.loadAnalytics(container);
                break;
            case 'logs':
                await this.loadLogs(container);
                break;
            case 'marketplace':
                await this.loadMarketplace(container);
                break;
            case 'plugins':
                await this.loadPlugins(container);
                break;
            case 'settings':
                await this.loadSettings(container);
                break;
            case 'users':
                await this.loadUsers(container);
                break;
            case 'security':
                await this.loadSecurity(container);
                break;
            case 'profile':
                await this.loadProfile(container);
                break;
            default:
                container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">🚧</div><div class="empty-state-title">Coming Soon</div><div class="empty-state-text">This feature is under development.</div></div>';
        }
    },

    // =============================================
    // OVERVIEW PAGE
    // =============================================
    async loadOverview(container) {
        container.innerHTML = `
            <div class="grid grid-4" id="stats-grid">
                <div class="stat-card"><div class="skeleton skeleton-text"></div><div class="skeleton skeleton-text" style="width:60%"></div></div>
                <div class="stat-card"><div class="skeleton skeleton-text"></div><div class="skeleton skeleton-text" style="width:60%"></div></div>
                <div class="stat-card"><div class="skeleton skeleton-text"></div><div class="skeleton skeleton-text" style="width:60%"></div></div>
                <div class="stat-card"><div class="skeleton skeleton-text"></div><div class="skeleton skeleton-text" style="width:60%"></div></div>
            </div>
            <div class="grid grid-2 mt-lg">
                <div class="chart-container" id="activity-chart">
                    <div class="chart-placeholder">Loading chart...</div>
                </div>
                <div class="chart-container" id="bots-chart">
                    <div class="chart-placeholder">Loading chart...</div>
                </div>
            </div>
            <div class="section mt-xl">
                <div class="section-header">
                    <h3 class="section-title">Quick Actions</h3>
                </div>
                <div class="quick-actions">
                    <a href="#" class="quick-action" data-page="bots">
                        <div class="quick-action-icon">🤖</div>
                        <span class="quick-action-label">Add Bot</span>
                    </a>
                    <a href="#" class="quick-action" data-page="commands">
                        <div class="quick-action-icon">⚡</div>
                        <span class="quick-action-label">Create Command</span>
                    </a>
                    <a href="#" class="quick-action" data-page="analytics">
                        <div class="quick-action-icon">📊</div>
                        <span class="quick-action-label">View Analytics</span>
                    </a>
                    <a href="#" class="quick-action" data-page="marketplace">
                        <div class="quick-action-icon">🛒</div>
                        <span class="quick-action-label">Marketplace</span>
                    </a>
                </div>
            </div>
        `;

        // Load stats
        try {
            const data = await api.getStats();
            if (data.success) {
                const stats = data.stats;
                document.getElementById('stats-grid').innerHTML = `
                    <div class="stat-card">
                        <div class="stat-icon">🤖</div>
                        <div class="stat-value">${UI.formatNumber(stats.total_bots || 0)}</div>
                        <div class="stat-label">Total Bots</div>
                        <div class="stat-change up">↑ Active: ${stats.bots?.active || 0}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">⚡</div>
                        <div class="stat-value">${UI.formatNumber(stats.total_commands || 0)}</div>
                        <div class="stat-label">Total Commands</div>
                        <div class="stat-change up">↑ Active</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">📊</div>
                        <div class="stat-value">${UI.formatNumber(stats.today_activity || 0)}</div>
                        <div class="stat-label">Today's Activity</div>
                        <div class="stat-change up">↑ Events today</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">📝</div>
                        <div class="stat-value">${UI.formatNumber(stats.total_logs || 0)}</div>
                        <div class="stat-label">Total Logs</div>
                        <div class="stat-change">System running</div>
                    </div>
                `;
            }
        } catch (e) {
            UI.showError(document.getElementById('stats-grid'), 'Failed to load stats');
        }

        // Load charts with canvas
        this.renderActivityChart();
        this.renderBotsChart();

        // Quick action links
        container.querySelectorAll('.quick-action[data-page]').forEach(el => {
            el.addEventListener('click', (e) => {
                e.preventDefault();
                const page = el.dataset.page;
                document.querySelector(`.nav-item[data-page="${page}"]`)?.click();
            });
        });
    },

    renderActivityChart() {
        const container = document.getElementById('activity-chart');
        if (!container) return;
        
        container.innerHTML = `
            <div style="padding: 1rem;">
                <h4 style="font-weight: 600; margin-bottom: 1rem;">Activity (Last 7 Days)</h4>
                <canvas id="activityChartCanvas" style="width:100%;height:220px;"></canvas>
            </div>
        `;

        setTimeout(() => this.drawActivityChart(), 100);
    },

    drawActivityChart() {
        const canvas = document.getElementById('activityChartCanvas');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        
        const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        const values = [12, 19, 15, 27, 22, 18, 30];
        
        const width = canvas.offsetWidth || 400;
        const height = canvas.offsetHeight || 220;
        canvas.width = width * 2;
        canvas.height = height * 2;
        canvas.style.width = width + 'px';
        canvas.style.height = height + 'px';
        
        ctx.scale(2, 2);
        ctx.clearRect(0, 0, width, height);
        
        const padding = { top: 20, bottom: 30, left: 30, right: 20 };
        const chartWidth = width - padding.left - padding.right;
        const chartHeight = height - padding.top - padding.bottom;
        const maxVal = Math.max(...values);
        
        // Grid lines
        ctx.strokeStyle = 'rgba(108, 92, 231, 0.1)';
        ctx.lineWidth = 1;
        for (let i = 0; i <= 4; i++) {
            const y = padding.top + (chartHeight / 4) * i;
            ctx.beginPath();
            ctx.moveTo(padding.left, y);
            ctx.lineTo(width - padding.right, y);
            ctx.stroke();
        }
        
        // Data line
        ctx.beginPath();
        ctx.strokeStyle = '#6C5CE7';
        ctx.lineWidth = 3;
        ctx.lineJoin = 'round';
        
        values.forEach((val, i) => {
            const x = padding.left + (chartWidth / (values.length - 1)) * i;
            const y = padding.top + chartHeight - (val / maxVal) * chartHeight;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        });
        ctx.stroke();
        
        // Fill area
        const lastX = padding.left + chartWidth;
        const lastY = padding.top + chartHeight;
        ctx.lineTo(lastX, lastY);
        ctx.lineTo(padding.left, lastY);
        ctx.closePath();
        
        const gradient = ctx.createLinearGradient(0, padding.top, 0, padding.top + chartHeight);
        gradient.addColorStop(0, 'rgba(108, 92, 231, 0.3)');
        gradient.addColorStop(1, 'rgba(108, 92, 231, 0.0)');
        ctx.fillStyle = gradient;
        ctx.fill();
        
        // Data points
        values.forEach((val, i) => {
            const x = padding.left + (chartWidth / (values.length - 1)) * i;
            const y = padding.top + chartHeight - (val / maxVal) * chartHeight;
            
            ctx.beginPath();
            ctx.arc(x, y, 5, 0, Math.PI * 2);
            ctx.fillStyle = '#6C5CE7';
            ctx.fill();
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 2;
            ctx.stroke();
        });
        
        // Labels
        ctx.fillStyle = '#B8B8D0';
        ctx.font = '12px Inter, sans-serif';
        ctx.textAlign = 'center';
        days.forEach((day, i) => {
            const x = padding.left + (chartWidth / (days.length - 1)) * i;
            ctx.fillText(day, x, height - 5);
        });
    },

    renderBotsChart() {
        const container = document.getElementById('bots-chart');
        if (!container) return;
        
        container.innerHTML = `
            <div style="padding: 1rem;">
                <h4 style="font-weight: 600; margin-bottom: 1rem;">Bot Status Distribution</h4>
                <canvas id="botsChartCanvas" style="width:100%;height:220px;"></canvas>
            </div>
        `;

        setTimeout(() => this.drawBotsChart(), 100);
    },

    drawBotsChart() {
        const canvas = document.getElementById('botsChartCanvas');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        
        const width = canvas.offsetWidth || 400;
        const height = canvas.offsetHeight || 220;
        canvas.width = width * 2;
        canvas.height = height * 2;
        canvas.style.width = width + 'px';
        canvas.style.height = height + 'px';
        
        ctx.scale(2, 2);
        ctx.clearRect(0, 0, width, height);
        
        const data = [
            { label: 'Online', value: 4, color: '#00B894' },
            { label: 'Stopped', value: 2, color: '#74B9FF' },
            { label: 'Error', value: 1, color: '#FF6B6B' },
        ];
        
        const total = data.reduce((s, d) => s + d.value, 0);
        const cx = width / 2;
        const cy = height / 2;
        const radius = Math.min(width, height) / 2 - 40;
        
        let startAngle = -Math.PI / 2;
        
        data.forEach(item => {
            const sliceAngle = (item.value / total) * Math.PI * 2;
            
            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.arc(cx, cy, radius, startAngle, startAngle + sliceAngle);
            ctx.closePath();
            ctx.fillStyle = item.color;
            ctx.fill();
            
            // Label
            const midAngle = startAngle + sliceAngle / 2;
            const labelRadius = radius * 0.65;
            const lx = cx + Math.cos(midAngle) * labelRadius;
            const ly = cy + Math.sin(midAngle) * labelRadius;
            
            ctx.fillStyle = '#fff';
            ctx.font = 'bold 14px Inter, sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(Math.round((item.value / total) * 100) + '%', lx, ly);
            
            startAngle += sliceAngle;
        });
        
        // Legend
        let legendY = 10;
        data.forEach(item => {
            ctx.fillStyle = item.color;
            ctx.fillRect(10, legendY, 12, 12);
            ctx.fillStyle = '#B8B8D0';
            ctx.font = '12px Inter, sans-serif';
            ctx.textAlign = 'left';
            ctx.textBaseline = 'middle';
            ctx.fillText(`${item.label}: ${item.value}`, 28, legendY + 6);
            legendY += 20;
        });
    },

    // =============================================
    // BOTS PAGE
    // =============================================
    async loadBots(container) {
        container.innerHTML = `
            <div class="section-header">
                <h3 class="section-title">Your Bots</h3>
                <div class="section-header-actions">
                    <button class="btn btn-primary" onclick="Dashboard.showAddBotModal()">
                        ➕ Add Bot
                    </button>
                </div>
            </div>
            <div id="bots-list">
                <div class="loading-overlay">
                    <div class="spinner spinner-lg"></div>
                    <p>Loading bots...</p>
                </div>
            </div>
        `;

        await this.refreshBotsList();
    },

    async refreshBotsList() {
        const container = document.getElementById('bots-list');
        if (!container) return;

        try {
            const data = await api.getBots();
            const bots = data.bots || [];

            if (bots.length === 0) {
                UI.showEmpty(container, {
                    icon: '🤖',
                    title: 'No Bots Yet',
                    message: 'Add your first Telegram bot to get started.',
                    action: '<button class="btn btn-primary" onclick="Dashboard.showAddBotModal()">➕ Add Your First Bot</button>'
                });
                return;
            }

            container.innerHTML = `
                <div class="grid grid-2" id="bots-grid">
                    ${bots.map(bot => this.renderBotCard(bot)).join('')}
                </div>
            `;

            // Attach event listeners
            container.querySelectorAll('.start-bot-btn').forEach(btn => {
                btn.addEventListener('click', () => this.startBot(parseInt(btn.dataset.botId)));
            });
            container.querySelectorAll('.stop-bot-btn').forEach(btn => {
                btn.addEventListener('click', () => this.stopBot(parseInt(btn.dataset.botId)));
            });
            container.querySelectorAll('.edit-bot-btn').forEach(btn => {
                btn.addEventListener('click', () => this.showEditBotModal(parseInt(btn.dataset.botId)));
            });
            container.querySelectorAll('.delete-bot-btn').forEach(btn => {
                btn.addEventListener('click', () => this.deleteBot(parseInt(btn.dataset.botId)));
            });
            container.querySelectorAll('.bot-card').forEach(card => {
                card.addEventListener('click', (e) => {
                    if (!e.target.closest('button')) {
                        this.showBotDetail(parseInt(card.dataset.botId));
                    }
                });
            });
        } catch (e) {
            UI.showError(container, e.message);
        }
    },

    renderBotCard(bot) {
        const status = bot.status === 'running' ? 'online' : bot.status;
        const statusBadge = UI.getStatusBadge(status);
        
        return `
            <div class="bot-card" data-bot-id="${bot.id}">
                <div class="bot-card-header">
                    <div class="bot-avatar">🤖</div>
                    <div class="bot-info">
                        <div class="bot-name">${UI.escapeHtml(bot.name)}</div>
                        <div class="bot-username">@${bot.username || 'unknown'}</div>
                    </div>
                    ${statusBadge}
                </div>
                <div class="bot-card-body">
                    <div class="bot-card-stats">
                        <div class="bot-stat">
                            <div class="bot-stat-value">${UI.formatNumber(bot.command_count || 0)}</div>
                            <div class="bot-stat-label">Commands</div>
                        </div>
                        <div class="bot-stat">
                            <div class="bot-stat-value">${bot.category || 'General'}</div>
                            <div class="bot-stat-label">Category</div>
                        </div>
                        <div class="bot-stat">
                            <div class="bot-stat-value">${UI.formatDate(bot.created_at)}</div>
                            <div class="bot-stat-label">Created</div>
                        </div>
                    </div>
                </div>
                <div class="bot-card-actions">
                    ${bot.status !== 'running' 
                        ? `<button class="btn btn-sm btn-success start-bot-btn" data-bot-id="${bot.id}">▶ Start</button>`
                        : `<button class="btn btn-sm btn-danger stop-bot-btn" data-bot-id="${bot.id}">⏹ Stop</button>`
                    }
                    <button class="btn btn-sm btn-secondary edit-bot-btn" data-bot-id="${bot.id}">✏️ Edit</button>
                    <button class="btn btn-sm btn-ghost delete-bot-btn" data-bot-id="${bot.id}">🗑️</button>
                </div>
            </div>
        `;
    },

    async startBot(botId) {
        try {
            const result = await api.startBot(botId);
            if (result.success) {
                UI.showToast('Bot started successfully', 'success');
                await this.refreshBotsList();
            } else {
                UI.showToast(result.errors?.[0] || 'Failed to start bot', 'error');
            }
        } catch (e) {
            UI.showToast(e.message, 'error');
        }
    },

    async stopBot(botId) {
        try {
            const result = await api.stopBot(botId);
            if (result.success) {
                UI.showToast('Bot stopped', 'info');
                await this.refreshBotsList();
            } else {
                UI.showToast(result.errors?.[0] || 'Failed to stop bot', 'error');
            }
        } catch (e) {
            UI.showToast(e.message, 'error');
        }
    },

    async deleteBot(botId) {
        const confirmed = await UI.showConfirm('Are you sure you want to delete this bot? All commands and data will be permanently lost.', 'Delete Bot');
        if (!confirmed) return;

        try {
            const result = await api.deleteBot(botId);
            if (result.success) {
                UI.showToast('Bot deleted', 'success');
                await this.refreshBotsList();
            } else {
                UI.showToast(result.errors?.[0] || 'Failed to delete bot', 'error');
            }
        } catch (e) {
            UI.showToast(e.message, 'error');
        }
    },

    showAddBotModal() {
        const html = `
            <div class="form-group">
                <label class="form-label">Bot Name</label>
                <input class="form-input" id="bot-name" placeholder="My Awesome Bot" required>
            </div>
            <div class="form-group">
                <label class="form-label">Bot Token</label>
                <input class="form-input" id="bot-token" placeholder="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz" required>
                <small class="text-muted">Get from @BotFather on Telegram</small>
            </div>
            <div class="form-group">
                <label class="form-label">Description (optional)</label>
                <textarea class="form-textarea" id="bot-description" placeholder="What does this bot do?" rows="3"></textarea>
            </div>
            <div id="token-verify-result"></div>
        `;

        const footer = `
            <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
            <button class="btn btn-primary" id="add-bot-submit">Add Bot</button>
        `;

        UI.showModal(html, { title: 'Add New Bot', footer });

        // Token verification
        const tokenInput = document.getElementById('bot-token');
        const verifyResult = document.getElementById('token-verify-result');
        
        tokenInput.addEventListener('blur', async () => {
            const token = tokenInput.value.trim();
            if (token.length > 20) {
                verifyResult.innerHTML = '<p class="text-muted">Verifying token...</p>';
                try {
                    const result = await api.verifyBotToken(token);
                    if (result.valid) {
                        verifyResult.innerHTML = `<p class="text-success">✅ Token verified! Bot: @${result.username}</p>`;
                    } else {
                        verifyResult.innerHTML = `<p class="text-danger">❌ ${result.error || 'Invalid token'}</p>`;
                    }
                } catch (e) {
                    verifyResult.innerHTML = `<p class="text-danger">❌ Verification failed</p>`;
                }
            }
        });

        document.getElementById('add-bot-submit').addEventListener('click', async () => {
            const name = document.getElementById('bot-name').value.trim();
            const token = document.getElementById('bot-token').value.trim();
            const description = document.getElementById('bot-description').value.trim();

            if (!name) { UI.showToast('Please enter a bot name', 'error'); return; }
            if (!token) { UI.showToast('Please enter a bot token', 'error'); return; }

            const btn = document.getElementById('add-bot-submit');
            btn.disabled = true;
            btn.textContent = 'Adding...';

            try {
                const result = await api.addBot(name, token, description);
                if (result.success) {
                    UI.showToast('Bot added successfully!', 'success');
                    document.querySelector('.modal-overlay').remove();
                    await this.refreshBotsList();
                } else {
                    UI.showToast(result.errors?.[0] || 'Failed to add bot', 'error');
                }
            } catch (e) {
                UI.showToast(e.message, 'error');
            }

            btn.disabled = false;
            btn.textContent = 'Add Bot';
        });
    },

    showEditBotModal(botId) {
        // Fetch bot data and show edit form
        api.getBot(botId).then(data => {
            if (!data.success) return;
            const bot = data.bot;

            const html = `
                <div class="form-group">
                    <label class="form-label">Bot Name</label>
                    <input class="form-input" id="edit-bot-name" value="${UI.escapeHtml(bot.name)}">
                </div>
                <div class="form-group">
                    <label class="form-label">Category</label>
                    <select class="form-select" id="edit-bot-category">
                        <option value="General" ${bot.category === 'General' ? 'selected' : ''}>General</option>
                        <option value="Utility" ${bot.category === 'Utility' ? 'selected' : ''}>Utility</option>
                        <option value="Fun" ${bot.category === 'Fun' ? 'selected' : ''}>Fun</option>
                        <option value="Admin" ${bot.category === 'Admin' ? 'selected' : ''}>Admin</option>
                        <option value="Moderation" ${bot.category === 'Moderation' ? 'selected' : ''}>Moderation</option>
                        <option value="Games" ${bot.category === 'Games' ? 'selected' : ''}>Games</option>
                        <option value="Music" ${bot.category === 'Music' ? 'selected' : ''}>Music</option>
                        <option value="News" ${bot.category === 'News' ? 'selected' : ''}>News</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Description</label>
                    <textarea class="form-textarea" id="edit-bot-description" rows="3">${UI.escapeHtml(bot.description || '')}</textarea>
                </div>
                <div class="divider"></div>
                <h4 style="font-weight:600;margin-bottom:1rem;">Bot Features</h4>
                <div class="form-checkbox" style="margin-bottom:0.5rem;">
                    <input type="checkbox" id="edit-welcome" ${bot.welcome_enabled ? 'checked' : ''}>
                    <label>Welcome Message</label>
                </div>
                <div class="form-checkbox" style="margin-bottom:0.5rem;">
                    <input type="checkbox" id="edit-force-sub" ${bot.force_subscribe_enabled ? 'checked' : ''}>
                    <label>Force Subscribe</label>
                </div>
                <div class="form-checkbox" style="margin-bottom:0.5rem;">
                    <input type="checkbox" id="edit-anti-spam" ${bot.anti_spam_enabled ? 'checked' : ''}>
                    <label>Anti-Spam Protection</label>
                </div>
                <div class="form-checkbox" style="margin-bottom:0.5rem;">
                    <input type="checkbox" id="edit-verification" ${bot.verification_enabled ? 'checked' : ''}>
                    <label>User Verification</label>
                </div>
                <div class="form-checkbox" style="margin-bottom:0.5rem;">
                    <input type="checkbox" id="edit-ai" ${bot.ai_enabled ? 'checked' : ''}>
                    <label>AI Chat Integration</label>
                </div>
            `;

            const footer = `
                <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                <button class="btn btn-primary" id="edit-bot-submit">Save Changes</button>
            `;

            UI.showModal(html, { title: `Edit Bot - ${bot.name}`, footer });

            document.getElementById('edit-bot-submit').addEventListener('click', async () => {
                const updateData = {
                    name: document.getElementById('edit-bot-name').value.trim(),
                    category: document.getElementById('edit-bot-category').value,
                    description: document.getElementById('edit-bot-description').value.trim(),
                    welcome_enabled: document.getElementById('edit-welcome').checked ? 1 : 0,
                    force_subscribe_enabled: document.getElementById('edit-force-sub').checked ? 1 : 0,
                    anti_spam_enabled: document.getElementById('edit-anti-spam').checked ? 1 : 0,
                    verification_enabled: document.getElementById('edit-verification').checked ? 1 : 0,
                    ai_enabled: document.getElementById('edit-ai').checked ? 1 : 0,
                };

                try {
                    const result = await api.updateBot(botId, updateData);
                    if (result.success) {
                        UI.showToast('Bot updated successfully', 'success');
                        document.querySelector('.modal-overlay').remove();
                        await this.refreshBotsList();
                    } else {
                        UI.showToast(result.error || 'Failed to update bot', 'error');
                    }
                } catch (e) {
                    UI.showToast(e.message, 'error');
                }
            });
        });
    },

    showBotDetail(botId) {
        this.selectedBotId = botId;
        api.getBot(botId).then(data => {
            if (!data.success) return;
            const bot = data.bot;
            const commands = data.commands || [];
            const logs = data.logs || [];

            const html = `
                <div class="section-header">
                    <h3 class="section-title">${UI.escapeHtml(bot.name)}</h3>
                    <div class="section-header-actions">
                        ${bot.status !== 'running' 
                            ? `<button class="btn btn-sm btn-success" onclick="Dashboard.startBot(${bot.id})">▶ Start</button>`
                            : `<button class="btn btn-sm btn-danger" onclick="Dashboard.stopBot(${bot.id})">⏹ Stop</button>`
                        }
                        <button class="btn btn-sm btn-secondary" onclick="Dashboard.showEditBotModal(${bot.id})">✏️ Edit</button>
                        <button class="btn btn-sm btn-ghost" onclick="Dashboard.loadPage('bots')">← Back</button>
                    </div>
                </div>

                <div class="grid grid-2">
                    <div class="stat-card">
                        <div class="stat-value" style="font-size:1rem;">${UI.getStatusBadge(bot.status === 'running' ? 'online' : bot.status)}</div>
                        <div class="stat-label">Status</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" style="font-size:1rem;">@${bot.username || 'unknown'}</div>
                        <div class="stat-label">Username</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" style="font-size:1rem;">${commands.length}</div>
                        <div class="stat-label">Commands</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" style="font-size:1rem;">${logs.length}</div>
                        <div class="stat-label">Log Entries</div>
                    </div>
                </div>

                <div class="section mt-lg">
                    <div class="section-header">
                        <h3 class="section-title">Commands (${commands.length})</h3>
                        <button class="btn btn-sm btn-primary" onclick="Dashboard.showAddCommandModal(${bot.id})">➕ Add Command</button>
                    </div>
                    <div id="bot-commands-list">
                        ${commands.length === 0 
                            ? '<div class="empty-state"><div class="empty-state-icon">⚡</div><div class="empty-state-title">No Commands</div><div class="empty-state-text">Create your first command for this bot.</div></div>'
                            : commands.map(cmd => `
                                <div class="command-item">
                                    <span class="command-name">${UI.escapeHtml(cmd.command)}</span>
                                    <span class="command-response">${UI.escapeHtml(cmd.response.substring(0, 80))}${cmd.response.length > 80 ? '...' : ''}</span>
                                    <span>${cmd.is_enabled ? UI.getStatusBadge('active') : UI.getStatusBadge('inactive')}</span>
                                    <div class="command-actions">
                                        <button class="btn-icon" onclick="Dashboard.showEditCommandModal(${cmd.id})" title="Edit">✏️</button>
                                        <button class="btn-icon" onclick="Dashboard.toggleCommand(${cmd.id})" title="Toggle">🔄</button>
                                        <button class="btn-icon" onclick="Dashboard.deleteCommand(${cmd.id})" title="Delete">🗑️</button>
                                    </div>
                                </div>
                            `).join('')
                        }
                    </div>
                </div>

                <div class="section mt-lg">
                    <div class="section-header">
                        <h3 class="section-title">Activity Logs</h3>
                    </div>
                    <div id="bot-logs-list">
                        ${logs.length === 0
                            ? '<div class="empty-state"><div class="empty-state-icon">📝</div><div class="empty-state-text">No logs yet.</div></div>'
                            : logs.slice(0, 20).map(log => `
                                <div class="activity-item">
                                    <div class="activity-icon">${log.level === 'error' ? '❌' : log.level === 'warning' ? '⚠️' : 'ℹ️'}</div>
                                    <div class="activity-content">
                                        <div class="activity-text" style="${log.level === 'error' ? 'color:var(--danger)' : ''}">${UI.escapeHtml(log.message)}</div>
                                        <div class="activity-time">${UI.formatDate(log.created_at)}</div>
                                    </div>
                                </div>
                            `).join('')
                        }
                    </div>
                </div>
            `;

            // Replace page content with bot detail view
            const container = document.getElementById('page-content');
            container.innerHTML = html;
        });
    },

    // =============================================
    // COMMANDS PAGE
    // =============================================
    async loadCommands(container) {
        // First, get bots to select from
        try {
            const botsData = await api.getBots();
            const bots = botsData.bots || [];

            if (bots.length === 0) {
                UI.showEmpty(container, {
                    icon: '🤖',
                    title: 'No Bots',
                    message: 'Add a bot first to manage commands.',
                    action: '<button class="btn btn-primary" onclick="Dashboard.showAddBotModal()">Add Bot</button>'
                });
                return;
            }

            container.innerHTML = `
                <div class="section-header">
                    <h3 class="section-title">Command Manager</h3>
                    <div class="section-header-actions">
                        <select class="form-select" id="command-bot-select" style="max-width:200px;">
                            ${bots.map(b => `<option value="${b.id}">${UI.escapeHtml(b.name)}</option>`).join('')}
                        </select>
                        <button class="btn btn-primary" onclick="Dashboard.showAddCommandModal(parseInt(document.getElementById('command-bot-select').value))">
                            ➕ Add Command
                        </button>
                    </div>
                </div>
                <div id="commands-list">
                    <div class="loading-overlay">
                        <div class="spinner spinner-lg"></div>
                        <p>Loading commands...</p>
                    </div>
                </div>
            `;

            document.getElementById('command-bot-select').addEventListener('change', () => {
                this.refreshCommandsList();
            });

            await this.refreshCommandsList();
        } catch (e) {
            UI.showError(container, e.message);
        }
    },

    async refreshCommandsList() {
        const container = document.getElementById('commands-list');
        const botSelect = document.getElementById('command-bot-select');
        if (!container || !botSelect) return;

        const botId = parseInt(botSelect.value);
        if (!botId) {
            UI.showEmpty(container, { icon: '🤖', title: 'Select a Bot', message: 'Choose a bot to view its commands.' });
            return;
        }

        try {
            const data = await api.getCommands(botId);
            const commands = data.commands || [];
            const categories = data.categories || [];

            if (commands.length === 0) {
                UI.showEmpty(container, {
                    icon: '⚡',
                    title: 'No Commands',
                    message: 'Create your first command for this bot.',
                    action: '<button class="btn btn-primary" onclick="Dashboard.showAddCommandModal(' + botId + ')">➕ Add Command</button>'
                });
                return;
            }

            container.innerHTML = `
                <div class="flex gap-sm mb-lg flex-wrap">
                    <button class="btn btn-sm btn-ghost category-filter active" data-cat="all">All (${commands.length})</button>
                    ${categories.map(cat => `
                        <button class="btn btn-sm btn-ghost category-filter" data-cat="${UI.escapeHtml(cat)}">${UI.escapeHtml(cat)}</button>
                    `).join('')}
                    <button class="btn btn-sm btn-ghost" onclick="Dashboard.showImportCommandsModal(${botId})" style="margin-left:auto;">📥 Import</button>
                    <button class="btn btn-sm btn-ghost" onclick="Dashboard.exportCommands(${botId})">📤 Export</button>
                </div>
                <div class="data-table-wrapper">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Command</th>
                                <th>Type</th>
                                <th>Response</th>
                                <th>Category</th>
                                <th>Usage</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="commands-table-body">
                            ${commands.map(cmd => `
                                <tr data-category="${UI.escapeHtml(cmd.category)}">
                                    <td><code style="color:var(--primary-light);font-family:var(--font-mono);">${UI.escapeHtml(cmd.command)}</code></td>
                                    <td><span class="badge">${cmd.response_type}</span></td>
                                    <td class="truncate" style="max-width:200px;">${UI.escapeHtml(cmd.response.substring(0, 60))}</td>
                                    <td><span class="badge badge-info">${UI.escapeHtml(cmd.category)}</span></td>
                                    <td>${UI.formatNumber(cmd.usage_count || 0)}</td>
                                    <td>${cmd.is_enabled ? UI.getStatusBadge('active') : UI.getStatusBadge('inactive')}</td>
                                    <td>
                                        <button class="btn-icon" onclick="Dashboard.showEditCommandModal(${cmd.id})" title="Edit">✏️</button>
                                        <button class="btn-icon" onclick="Dashboard.toggleCommand(${cmd.id})" title="Toggle">🔄</button>
                                        <button class="btn-icon" onclick="Dashboard.deleteCommand(${cmd.id})" title="Delete">🗑️</button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;

            // Category filter
            container.querySelectorAll('.category-filter').forEach(btn => {
                btn.addEventListener('click', function() {
                    container.querySelectorAll('.category-filter').forEach(b => b.classList.remove('active'));
                    this.classList.add('active');
                    
                    const cat = this.dataset.cat;
                    document.querySelectorAll('#commands-table-body tr').forEach(row => {
                        if (cat === 'all' || row.dataset.category === cat) {
                            row.style.display = '';
                        } else {
                            row.style.display = 'none';
                        }
                    });
                });
            });
        } catch (e) {
            UI.showError(container, e.message);
        }
    },

    showAddCommandModal(botId) {
        const html = `
            <div class="form-group">
                <label class="form-label">Command</label>
                <input class="form-input" id="cmd-command" placeholder="/start" value="/">
            </div>
            <div class="form-group">
                <label class="form-label">Response Type</label>
                <select class="form-select" id="cmd-response-type">
                    <option value="text">Text</option>
                    <option value="photo">Photo</option>
                    <option value="video">Video</option>
                    <option value="audio">Audio</option>
                    <option value="document">Document</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Response</label>
                <textarea class="form-textarea" id="cmd-response" rows="4" placeholder="Enter response text or URL for media..."></textarea>
            </div>
            <div class="form-group" id="media-url-group" style="display:none;">
                <label class="form-label">Media URL</label>
                <input class="form-input" id="cmd-media-url" placeholder="https://example.com/image.jpg">
            </div>
            <div class="form-group">
                <label class="form-label">Category</label>
                <input class="form-input" id="cmd-category" placeholder="General" value="General">
            </div>
            <div class="form-group">
                <label class="form-label">Description</label>
                <input class="form-input" id="cmd-description" placeholder="What does this command do?">
            </div>
            <div class="divider"></div>
            <h4 style="font-weight:600;margin-bottom:1rem;">Advanced Options</h4>
            <div class="form-group">
                <label class="form-label">Inline Keyboard (JSON)</label>
                <textarea class="form-textarea" id="cmd-inline-keyboard" rows="2" placeholder='[[{"text":"Button","callback_data":"btn1"}]]'></textarea>
            </div>
            <div class="form-group">
                <label class="form-label">Reply Keyboard (JSON)</label>
                <textarea class="form-textarea" id="cmd-reply-keyboard" rows="2" placeholder='[["Button1","Button2"],["Button3"]]'></textarea>
            </div>
            <div class="form-group">
                <label class="form-label">Custom Variables (JSON)</label>
                <textarea class="form-textarea" id="cmd-variables" rows="2" placeholder='{"key":"value"}'></textarea>
            </div>
            <div class="form-checkbox" style="margin-bottom:0.5rem;">
                <input type="checkbox" id="cmd-is-welcome">
                <label>Welcome Command</label>
            </div>
            <div class="form-checkbox" style="margin-bottom:0.5rem;">
                <input type="checkbox" id="cmd-is-auto-reply">
                <label>Auto-Reply Command</label>
            </div>
        `;

        const footer = `
            <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
            <button class="btn btn-primary" id="add-cmd-submit">Create Command</button>
        `;

        UI.showModal(html, { title: 'Create Command', footer });

        // Show/hide media URL based on response type
        document.getElementById('cmd-response-type').addEventListener('change', function() {
            document.getElementById('media-url-group').style.display = 
                ['photo', 'video', 'audio', 'document'].includes(this.value) ? 'block' : 'none';
        });

        document.getElementById('add-cmd-submit').addEventListener('click', async () => {
            const command = document.getElementById('cmd-command').value.trim();
            const responseType = document.getElementById('cmd-response-type').value;
            const response = document.getElementById('cmd-response').value.trim();
            const category = document.getElementById('cmd-category').value.trim() || 'General';
            const description = document.getElementById('cmd-description').value.trim();
            const mediaUrl = document.getElementById('cmd-media-url')?.value.trim() || '';
            const inlineKeyboard = document.getElementById('cmd-inline-keyboard')?.value.trim() || '';
            const replyKeyboard = document.getElementById('cmd-reply-keyboard')?.value.trim() || '';
            const variables = document.getElementById('cmd-variables')?.value.trim() || '';
            const isWelcome = document.getElementById('cmd-is-welcome').checked ? 1 : 0;
            const isAutoReply = document.getElementById('cmd-is-auto-reply').checked ? 1 : 0;

            if (!command || command === '/') { UI.showToast('Please enter a command', 'error'); return; }
            if (!response) { UI.showToast('Please enter a response', 'error'); return; }

            try {
                const result = await api.createCommand(botId, command, responseType, response, {
                    category,
                    description,
                    media_url: mediaUrl,
                    inline_keyboard: inlineKeyboard,
                    reply_keyboard: replyKeyboard,
                    variables,
                    is_welcome: isWelcome,
                    is_auto_reply: isAutoReply,
                });
                if (result.success) {
                    UI.showToast('Command created!', 'success');
                    document.querySelector('.modal-overlay').remove();
                    await this.refreshCommandsList();
                } else {
                    UI.showToast(result.errors?.[0] || 'Failed to create command', 'error');
                }
            } catch (e) {
                UI.showToast(e.message, 'error');
            }
        });
    },

    showEditCommandModal(cmdId) {
        api.getCommand(cmdId).then(data => {
            if (!data.success) return;
            const cmd = data.command;

            const html = `
                <div class="form-group">
                    <label class="form-label">Command</label>
                    <input class="form-input" id="edit-cmd-command" value="${UI.escapeHtml(cmd.command)}">
                </div>
                <div class="form-group">
                    <label class="form-label">Response Type</label>
                    <select class="form-select" id="edit-cmd-response-type">
                        <option value="text" ${cmd.response_type === 'text' ? 'selected' : ''}>Text</option>
                        <option value="photo" ${cmd.response_type === 'photo' ? 'selected' : ''}>Photo</option>
                        <option value="video" ${cmd.response_type === 'video' ? 'selected' : ''}>Video</option>
                        <option value="audio" ${cmd.response_type === 'audio' ? 'selected' : ''}>Audio</option>
                        <option value="document" ${cmd.response_type === 'document' ? 'selected' : ''}>Document</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Response</label>
                    <textarea class="form-textarea" id="edit-cmd-response" rows="4">${UI.escapeHtml(cmd.response)}</textarea>
                </div>
                <div class="form-group">
                    <label class="form-label">Category</label>
                    <input class="form-input" id="edit-cmd-category" value="${UI.escapeHtml(cmd.category)}">
                </div>
                <div class="form-group">
                    <label class="form-label">Description</label>
                    <input class="form-input" id="edit-cmd-description" value="${UI.escapeHtml(cmd.description || '')}">
                </div>
            `;

            const footer = `
                <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                <button class="btn btn-primary" id="edit-cmd-submit">Save Changes</button>
            `;

            UI.showModal(html, { title: `Edit Command - ${cmd.command}`, footer });

            document.getElementById('edit-cmd-submit').addEventListener('click', async () => {
                const updateData = {
                    command: document.getElementById('edit-cmd-command').value.trim(),
                    response_type: document.getElementById('edit-cmd-response-type').value,
                    response: document.getElementById('edit-cmd-response').value.trim(),
                    category: document.getElementById('edit-cmd-category').value.trim(),
                    description: document.getElementById('edit-cmd-description').value.trim(),
                };

                try {
                    const result = await api.editCommand(cmdId, updateData);
                    if (result.success) {
                        UI.showToast('Command updated', 'success');
                        document.querySelector('.modal-overlay').remove();
                        await this.refreshCommandsList();
                    } else {
                        UI.showToast(result.errors?.[0] || 'Failed to update', 'error');
                    }
                } catch (e) {
                    UI.showToast(e.message, 'error');
                }
            });
        });
    },

    async toggleCommand(cmdId) {
        try {
            const result = await api.toggleCommand(cmdId);
            if (result.success) {
                UI.showToast(result.is_enabled ? 'Command enabled' : 'Command disabled', 'info');
                await this.refreshCommandsList();
            }
        } catch (e) {
            UI.showToast(e.message, 'error');
        }
    },

    async deleteCommand(cmdId) {
        const confirmed = await UI.showConfirm('Delete this command?', 'Delete Command');
        if (!confirmed) return;

        try {
            const result = await api.deleteCommand(cmdId);
            if (result.success) {
                UI.showToast('Command deleted', 'success');
                await this.refreshCommandsList();
            }
        } catch (e) {
            UI.showToast(e.message, 'error');
        }
    },

    showImportCommandsModal(botId) {
        const html = `
            <div class="form-group">
                <label class="form-label">Paste commands JSON</label>
                <textarea class="form-textarea" id="import-commands-json" rows="10" placeholder='[{"command":"/start","response":"Hello!","response_type":"text"}]'></textarea>
            </div>
            <p class="text-sm text-muted">Format: Array of command objects with "command", "response", and optionally "response_type", "category"</p>
        `;

        const footer = `
            <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
            <button class="btn btn-primary" id="import-cmd-submit">Import</button>
        `;

        UI.showModal(html, { title: 'Import Commands', footer });

        document.getElementById('import-cmd-submit').addEventListener('click', async () => {
            const json = document.getElementById('import-commands-json').value.trim();
            if (!json) { UI.showToast('Please enter commands JSON', 'error'); return; }

            try {
                const result = await api.importCommands(botId, JSON.parse(json));
                if (result.imported > 0) {
                    UI.showToast(`Imported ${result.imported} commands${result.failed > 0 ? `, ${result.failed} failed` : ''}`, result.failed > 0 ? 'warning' : 'success');
                    document.querySelector('.modal-overlay').remove();
                    await this.refreshCommandsList();
                } else {
                    UI.showToast('No commands were imported', 'error');
                }
            } catch (e) {
                UI.showToast('Invalid JSON format: ' + e.message, 'error');
            }
        });
    },

    async exportCommands(botId) {
        try {
            const data = await api.exportCommands(botId);
            if (data.success) {
                const blob = new Blob([JSON.stringify(data.commands, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `commands_export_${botId}.json`;
                a.click();
                URL.revokeObjectURL(url);
                UI.showToast('Commands exported', 'success');
            }
        } catch (e) {
            UI.showToast(e.message, 'error');
        }
    },

    // =============================================
    // ANALYTICS PAGE
    // =============================================
    async loadAnalytics(container) {
        container.innerHTML = `
            <div class="grid grid-4" id="analytics-stats">
                <div class="stat-card"><div class="skeleton skeleton-text"></div><div class="skeleton skeleton-text" style="width:60%"></div></div>
                <div class="stat-card"><div class="skeleton skeleton-text"></div><div class="skeleton skeleton-text" style="width:60%"></div></div>
                <div class="stat-card"><div class="skeleton skeleton-text"></div><div class="skeleton skeleton-text" style="width:60%"></div></div>
                <div class="stat-card"><div class="skeleton skeleton-text"></div><div class="skeleton skeleton-text" style="width:60%"></div></div>
            </div>
            <div class="grid grid-2 mt-lg">
                <div class="chart-container" id="growth-chart">
                    <div class="chart-placeholder">Growth chart loading...</div>
                </div>
                <div class="chart-container" id="command-usage-chart">
                    <div class="chart-placeholder">Command usage chart loading...</div>
                </div>
            </div>
            <div class="grid grid-2 mt-lg">
                <div class="settings-group">
                    <div class="settings-group-header">Command Usage Statistics</div>
                    <div class="settings-group-body" id="command-usage-stats">
                        <div class="loading-overlay"><div class="spinner"></div></div>
                    </div>
                </div>
                <div class="settings-group">
                    <div class="settings-group-header">Engagement Overview</div>
                    <div class="settings-group-body" id="engagement-stats">
                        <div class="loading-overlay"><div class="spinner"></div></div>
                    </div>
                </div>
            </div>
        `;

        // Load stats
        try {
            const statsData = await api.getStats();
            if (statsData.success) {
                const s = statsData.stats;
                document.getElementById('analytics-stats').innerHTML = `
                    <div class="stat-card">
                        <div class="stat-icon">📈</div>
                        <div class="stat-value">${s.today_activity || 0}</div>
                        <div class="stat-label">Today's Activity</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">📊</div>
                        <div class="stat-value">${s.total_logs || 0}</div>
                        <div class="stat-label">Total Events</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">👥</div>
                        <div class="stat-value">${s.total_users || 0}</div>
                        <div class="stat-label">Total Users</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">🚀</div>
                        <div class="stat-value">${s.today_users || 0}</div>
                        <div class="stat-label">New Users Today</div>
                    </div>
                `;
            }
        } catch (e) { /* ignore */ }

        // Load command usage stats
        try {
            const usageData = await api.getCommandUsage();
            if (usageData.success) {
                const items = usageData.data || [];
                document.getElementById('command-usage-stats').innerHTML = items.length === 0
                    ? '<p class="text-muted">No command usage data yet.</p>'
                    : items.map(item => `
                        <div class="flex justify-between items-center" style="padding:8px 0;border-bottom:1px solid var(--border-color);">
                            <span><code style="color:var(--primary-light)">${UI.escapeHtml(item.command)}</code></span>
                            <span class="font-bold">${UI.formatNumber(item.total_usage)}</span>
                        </div>
                    `).join('');
            }
        } catch (e) { /* ignore */ }

        // Load engagement stats
        try {
            const engData = await api.getEngagement();
            if (engData.success) {
                const data = engData.data || {};
                document.getElementById('engagement-stats').innerHTML = `
                    <p><strong>Status Distribution:</strong></p>
                    ${(data.status_distribution || []).map(d => `
                        <div class="flex justify-between items-center" style="padding:4px 0;">
                            <span>${d.status}:</span>
                            <span class="font-bold">${d.count}</span>
                        </div>
                    `).join('') || '<p class="text-muted">No data</p>'}
                `;
            }
        } catch (e) { /* ignore */ }

        // Render charts
        this.renderGrowthChart();
        this.renderCommandUsageChart();
    },

    renderGrowthChart() {
        const container = document.getElementById('growth-chart');
        if (!container) return;
        container.innerHTML = `
            <div style="padding:1rem;">
                <h4 style="font-weight:600;margin-bottom:1rem;">Growth Trend</h4>
                <canvas id="growthCanvas" style="width:100%;height:220px;"></canvas>
            </div>
        `;
        setTimeout(() => {
            const canvas = document.getElementById('growthCanvas');
            if (!canvas) return;
            const ctx = canvas.getContext('2d');
            const width = canvas.offsetWidth || 400;
            const height = canvas.offsetHeight || 220;
            canvas.width = width * 2;
            canvas.height = height * 2;
            canvas.style.width = width + 'px';
            canvas.style.height = height + 'px';
            ctx.scale(2, 2);
            
            // Draw simple bar chart
            const data = [5, 8, 12, 10, 15, 22, 18, 25, 30, 28, 35, 40];
            const labels = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
            
            const padding = { top: 20, bottom: 30, left: 20, right: 20 };
            const chartW = width - padding.left - padding.right;
            const chartH = height - padding.top - padding.bottom;
            const barWidth = chartW / data.length - 4;
            
            data.forEach((val, i) => {
                const x = padding.left + (chartW / data.length) * i + 2;
                const barH = (val / Math.max(...data)) * chartH;
                const y = padding.top + chartH - barH;
                
                const gradient = ctx.createLinearGradient(x, y, x, padding.top + chartH);
                gradient.addColorStop(0, '#6C5CE7');
                gradient.addColorStop(1, 'rgba(108,92,231,0.3)');
                
                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.roundRect(x, y, barWidth, barH, [4, 4, 0, 0]);
                ctx.fill();
            });
            
            ctx.fillStyle = '#B8B8D0';
            ctx.font = '10px Inter, sans-serif';
            ctx.textAlign = 'center';
            data.forEach((val, i) => {
                const x = padding.left + (chartW / data.length) * i + barWidth / 2 + 2;
                ctx.fillText(labels[i], x, height - 5);
            });
        }, 100);
    },

    renderCommandUsageChart() {
        const container = document.getElementById('command-usage-chart');
        if (!container) return;
        container.innerHTML = `
            <div style="padding:1rem;">
                <h4 style="font-weight:600;margin-bottom:1rem;">Most Used Commands</h4>
                <canvas id="cmdUsageCanvas" style="width:100%;height:220px;"></canvas>
            </div>
        `;
        setTimeout(() => {
            const canvas = document.getElementById('cmdUsageCanvas');
            if (!canvas) return;
            const ctx = canvas.getContext('2d');
            const width = canvas.offsetWidth || 400;
            const height = canvas.offsetHeight || 220;
            canvas.width = width * 2;
            canvas.height = height * 2;
            canvas.style.width = width + 'px';
            canvas.style.height = height + 'px';
            ctx.scale(2, 2);
            
            const data = [
                { label: '/start', value: 45 },
                { label: '/help', value: 32 },
                { label: '/info', value: 28 },
                { label: '/stats', value: 20 },
            ];
            
            const maxVal = Math.max(...data.map(d => d.value));
            const padding = { top: 10, bottom: 20, left: 80, right: 20 };
            const chartW = width - padding.left - padding.right;
            const barHeight = 35;
            const gap = 10;
            
            data.forEach((item, i) => {
                const y = padding.top + i * (barHeight + gap);
                const barW = (item.value / maxVal) * chartW;
                
                const gradient = ctx.createLinearGradient(padding.left, y, padding.left + barW, y);
                gradient.addColorStop(0, '#6C5CE7');
                gradient.addColorStop(1, '#A29BFE');
                
                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.roundRect(padding.left, y, barW, barHeight, [0, 6, 6, 0]);
                ctx.fill();
                
                ctx.fillStyle = '#B8B8D0';
                ctx.font = '12px Inter, sans-serif';
                ctx.textAlign = 'right';
                ctx.textBaseline = 'middle';
                ctx.fillText(item.label, padding.left - 8, y + barHeight / 2);
                
                ctx.fillStyle = '#fff';
                ctx.textAlign = 'left';
                ctx.font = 'bold 12px Inter, sans-serif';
                ctx.fillText(item.value.toString(), padding.left + 8, y + barHeight / 2);
            });
        }, 100);
    },

    // =============================================
    // LOGS PAGE
    // =============================================
    async loadLogs(container) {
        container.innerHTML = `
            <div class="section-header">
                <h3 class="section-title">Activity Logs</h3>
                <button class="btn btn-sm btn-secondary" onclick="Dashboard.loadLogs(document.getElementById('page-content'))">🔄 Refresh</button>
            </div>
            <div id="logs-list">
                <div class="loading-overlay">
                    <div class="spinner spinner-lg"></div>
                    <p>Loading logs...</p>
                </div>
            </div>
        `;

        try {
            const data = await api.getLogs();
            const logs = data.logs || [];

            const container2 = document.getElementById('logs-list');
            if (logs.length === 0) {
                UI.showEmpty(container2, {
                    icon: '📝',
                    title: 'No Logs',
                    message: 'No activity logs yet.'
                });
                return;
            }

            container2.innerHTML = `
                <div class="settings-group">
                    <div class="settings-group-body" style="max-height:500px;overflow-y:auto;">
                        ${logs.map(log => `
                            <div class="activity-item">
                                <div class="activity-icon">${log.level === 'error' ? '❌' : log.level === 'warning' ? '⚠️' : 'ℹ️'}</div>
                                <div class="activity-content">
                                    <div class="activity-text">${UI.escapeHtml(log.message)}</div>
                                    <div class="activity-time">
                                        ${UI.formatDate(log.created_at)}
                                        ${log.bot_name ? `· Bot: ${UI.escapeHtml(log.bot_name)}` : ''}
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        } catch (e) {
            UI.showError(document.getElementById('logs-list'), e.message);
        }
    },

    // =============================================
    // MARKETPLACE PAGE
    // =============================================
    async loadMarketplace(container) {
        container.innerHTML = `
            <div class="section-header">
                <h3 class="section-title">Bot Marketplace</h3>
                <button class="btn btn-primary" onclick="Dashboard.showAddMarketplaceModal()">➕ Sell Bot</button>
            </div>
            <div id="marketplace-grid" class="grid grid-3">
                <div class="loading-overlay"><div class="spinner spinner-lg"></div><p>Loading marketplace...</p></div>
            </div>
        `;

        try {
            const data = await api.getMarketplace();
            const items = data.items || [];

            const grid = document.getElementById('marketplace-grid');
            if (items.length === 0) {
                UI.showEmpty(grid, {
                    icon: '🛒',
                    title: 'Marketplace Empty',
                    message: 'No items listed yet. Be the first to sell!'
                });
                return;
            }

            grid.innerHTML = items.map(item => `
                <div class="marketplace-card">
                    <div class="marketplace-card-image">🤖</div>
                    <div class="marketplace-card-body">
                        <div class="marketplace-card-title">${UI.escapeHtml(item.name)}</div>
                        <div class="marketplace-card-seller">by ${UI.escapeHtml(item.seller_name || 'Unknown')}</div>
                        <div class="marketplace-card-price">${item.price > 0 ? '$' + item.price.toFixed(2) : 'Free'}</div>
                        <div class="marketplace-card-rating">⭐ ${item.rating || '0.0'}</div>
                        <div style="margin-top:0.5rem;">
                            <span class="badge badge-info">${item.type}</span>
                            <span class="badge">${item.downloads || 0} downloads</span>
                        </div>
                    </div>
                </div>
            `).join('');
        } catch (e) {
            UI.showError(document.getElementById('marketplace-grid'), e.message);
        }
    },

    showAddMarketplaceModal() {
        const html = `
            <div class="form-group">
                <label class="form-label">Item Name</label>
                <input class="form-input" id="mp-name" placeholder="My Bot Template">
            </div>
            <div class="form-group">
                <label class="form-label">Description</label>
                <textarea class="form-textarea" id="mp-description" rows="4" placeholder="Describe your template..."></textarea>
            </div>
            <div class="form-group">
                <label class="form-label">Price ($)</label>
                <input class="form-input" id="mp-price" type="number" step="0.01" value="0" placeholder="0 = Free">
            </div>
            <div class="form-group">
                <label class="form-label">Type</label>
                <select class="form-select" id="mp-type">
                    <option value="bot">Bot Template</option>
                    <option value="plugin">Plugin</option>
                    <option value="theme">Theme</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Category</label>
                <select class="form-select" id="mp-category">
                    <option value="General">General</option>
                    <option value="Utility">Utility</option>
                    <option value="Fun">Fun</option>
                    <option value="Admin">Admin</option>
                    <option value="Games">Games</option>
                </select>
            </div>
        `;

        const footer = `
            <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
            <button class="btn btn-primary" id="add-mp-submit">List Item</button>
        `;

        UI.showModal(html, { title: 'Sell on Marketplace', footer });

        document.getElementById('add-mp-submit').addEventListener('click', async () => {
            const name = document.getElementById('mp-name').value.trim();
            const description = document.getElementById('mp-description').value.trim();
            const price = parseFloat(document.getElementById('mp-price').value) || 0;
            const type = document.getElementById('mp-type').value;
            const category = document.getElementById('mp-category').value;

            if (!name) { UI.showToast('Please enter a name', 'error'); return; }

            try {
                const result = await api.addMarketplaceItem(name, description, price, type, category);
                if (result.success) {
                    UI.showToast('Item listed on marketplace!', 'success');
                    document.querySelector('.modal-overlay').remove();
                    await this.loadMarketplace(document.getElementById('page-content'));
                }
            } catch (e) {
                UI.showToast(e.message, 'error');
            }
        });
    },

    // =============================================
    // PLUGINS PAGE
    // =============================================
    async loadPlugins(container) {
        container.innerHTML = `
            <div class="section-header">
                <h3 class="section-title">Plugin System</h3>
                <button class="btn btn-sm btn-primary" onclick="UI.showToast('Plugin upload coming soon','info')">📥 Install Plugin</button>
            </div>
            <div id="plugins-list" class="grid grid-2">
                <div class="loading-overlay"><div class="spinner spinner-lg"></div></div>
            </div>
        `;

        try {
            const data = await api.getPlugins();
            const plugins = data.plugins || [];

            const list = document.getElementById('plugins-list');
            list.innerHTML = plugins.map(p => `
                <div class="bot-card">
                    <div class="bot-card-header">
                        <div class="bot-avatar">🔌</div>
                        <div class="bot-info">
                            <div class="bot-name">${UI.escapeHtml(p.name)}</div>
                            <div class="bot-username">v${p.version} by ${UI.escapeHtml(p.author)}</div>
                        </div>
                        <span class="form-switch">
                            <input type="checkbox" ${p.is_enabled ? 'checked' : ''} onchange="Dashboard.togglePlugin(${p.id}, this.checked)">
                            <span class="slider"></span>
                        </span>
                    </div>
                    <div class="bot-card-body">
                        <p class="text-sm text-muted">${UI.escapeHtml(p.description || 'No description')}</p>
                    </div>
                </div>
            `).join('');
        } catch (e) {
            UI.showError(document.getElementById('plugins-list'), e.message);
        }
    },

    async togglePlugin(pluginId, isEnabled) {
        try {
            const result = await api.togglePlugin(pluginId, isEnabled ? 1 : 0);
            if (result.success) {
                UI.showToast(`Plugin ${isEnabled ? 'enabled' : 'disabled'}`, 'success');
            }
        } catch (e) {
            UI.showToast(e.message, 'error');
        }
    },

    // =============================================
    // SETTINGS PAGE
    // =============================================
    loadSettings(container) {
        container.innerHTML = `
            <div class="settings-group">
                <div class="settings-group-header">Notifications</div>
                <div class="settings-group-body">
                    <div class="settings-row">
                        <div>
                            <div class="settings-row-label">Email Notifications</div>
                            <div class="settings-row-desc">Receive email updates about your bots</div>
                        </div>
                        <span class="form-switch">
                            <input type="checkbox" id="setting-email-notif">
                            <span class="slider"></span>
                        </span>
                    </div>
                    <div class="settings-row">
                        <div>
                            <div class="settings-row-label">Bot Status Alerts</div>
                            <div class="settings-row-desc">Get notified when bots go offline</div>
                        </div>
                        <span class="form-switch">
                            <input type="checkbox" id="setting-bot-alerts" checked>
                            <span class="slider"></span>
                        </span>
                    </div>
                </div>
            </div>

            <div class="settings-group">
                <div class="settings-group-header">Theme</div>
                <div class="settings-group-body">
                    <div class="settings-row">
                        <div>
                            <div class="settings-row-label">Appearance</div>
                            <div class="settings-row-desc">Toggle between dark and light mode</div>
                        </div>
                        <button class="btn btn-secondary btn-sm theme-toggle" onclick="ThemeManager.toggle()">${localStorage.getItem('tgbh_theme') === 'light' ? '☀️ Light' : '🌙 Dark'}</button>
                    </div>
                </div>
            </div>

            <div class="settings-group">
                <div class="settings-group-header">API Access</div>
                <div class="settings-group-body">
                    <div class="settings-row">
                        <div>
                            <div class="settings-row-label">API Key</div>
                            <div class="settings-row-desc">Use for programmatic access</div>
                        </div>
                        <div class="flex items-center gap-sm">
                            <code class="font-mono text-sm" id="api-key-display">${api.user?.api_key || 'Loading...'}</code>
                            <button class="btn-icon" onclick="navigator.clipboard.writeText(document.getElementById('api-key-display').textContent);UI.showToast('Copied!','success')">📋</button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="settings-group">
                <div class="settings-group-header">Account</div>
                <div class="settings-group-body">
                    <div class="settings-row">
                        <div>
                            <div class="settings-row-label">Delete Account</div>
                            <div class="settings-row-desc text-danger">This action cannot be undone</div>
                        </div>
                        <button class="btn btn-danger btn-sm" onclick="UI.showToast('Account deletion not available in demo','warning')">Delete Account</button>
                    </div>
                </div>
            </div>
        `;

        // Load saved settings
        const emailNotif = document.getElementById('setting-email-notif');
        const botAlerts = document.getElementById('setting-bot-alerts');
        
        emailNotif?.addEventListener('change', () => api.saveSetting('email_notifications', emailNotif.checked ? '1' : '0'));
        botAlerts?.addEventListener('change', () => api.saveSetting('bot_alerts', botAlerts.checked ? '1' : '0'));
    },

    // =============================================
    // PROFILE PAGE
    // =============================================
    loadProfile(container) {
        const user = api.user || {};
        
        container.innerHTML = `
            <div class="settings-group">
                <div class="settings-group-header">Profile Information</div>
                <div class="settings-group-body">
                    <div class="flex items-center gap-lg mb-lg">
                        <div class="sidebar-user-avatar" style="width:80px;height:80px;font-size:2rem;border-radius:var(--radius-lg);">${(user.full_name || user.username || 'U').charAt(0).toUpperCase()}</div>
                        <div>
                            <h3 style="font-weight:700;">${UI.escapeHtml(user.full_name || user.username || 'User')}</h3>
                            <p class="text-muted">${user.email || ''}</p>
                            <span class="badge badge-primary">${user.role || 'user'}</span>
                            <span class="badge badge-info">${user.plan || 'free'} plan</span>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Full Name</label>
                        <input class="form-input" id="profile-name" value="${UI.escapeHtml(user.full_name || '')}">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Username</label>
                        <input class="form-input" value="${UI.escapeHtml(user.username || '')}" disabled style="opacity:0.6;">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Email</label>
                        <input class="form-input" value="${UI.escapeHtml(user.email || '')}" disabled style="opacity:0.6;">
                    </div>
                    <button class="btn btn-primary" onclick="Dashboard.saveProfile()">Save Changes</button>
                </div>
            </div>

            <div class="settings-group">
                <div class="settings-group-header">Security</div>
                <div class="settings-group-body">
                    <div class="settings-row">
                        <div>
                            <div class="settings-row-label">Password</div>
                            <div class="settings-row-desc">Change your account password</div>
                        </div>
                        <button class="btn btn-secondary btn-sm" onclick="Dashboard.showChangePasswordModal()">Change Password</button>
                    </div>
                    <div class="settings-row">
                        <div>
                            <div class="settings-row-label">Two-Factor Authentication</div>
                            <div class="settings-row-desc">Add an extra layer of security</div>
                        </div>
                        <button class="btn ${user.twofa_enabled ? 'btn-danger' : 'btn-success'} btn-sm" onclick="Dashboard.toggle2FA(${user.twofa_enabled ? 0 : 1})">
                            ${user.twofa_enabled ? 'Disable 2FA' : 'Enable 2FA'}
                        </button>
                    </div>
                </div>
            </div>

            <div class="settings-group">
                <div class="settings-group-header">Plan & Limits</div>
                <div class="settings-group-body">
                    <div class="settings-row">
                        <div>
                            <div class="settings-row-label">Current Plan: <strong>${user.plan || 'free'}</strong></div>
                        </div>
                        <button class="btn btn-primary btn-sm" onclick="UI.showToast('Upgrade options coming soon','info')">Upgrade →</button>
                    </div>
                    <div class="settings-row">
                        <div>
                            <div class="settings-row-label">Max Bots: ${user.max_bots || 5}</div>
                        </div>
                    </div>
                    <div class="settings-row">
                        <div>
                            <div class="settings-row-label">Max Commands: ${user.max_commands || 50}</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    async saveProfile() {
        const fullName = document.getElementById('profile-name').value.trim();
        try {
            const result = await api.updateProfile(fullName);
            if (result.success) {
                api.user.full_name = fullName;
                localStorage.setItem('tgbh_user', JSON.stringify(api.user));
                SidebarManager.updateUser(api.user);
                UI.showToast('Profile updated!', 'success');
            }
        } catch (e) {
            UI.showToast(e.message, 'error');
        }
    },

    showChangePasswordModal() {
        const html = `
            <div class="form-group">
                <label class="form-label">Current Password</label>
                <input class="form-input" id="current-pw" type="password">
            </div>
            <div class="form-group">
                <label class="form-label">New Password</label>
                <input class="form-input" id="new-pw" type="password">
            </div>
            <div class="form-group">
                <label class="form-label">Confirm New Password</label>
                <input class="form-input" id="confirm-pw" type="password">
            </div>
        `;

        const footer = `
            <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
            <button class="btn btn-primary" id="change-pw-submit">Change Password</button>
        `;

        UI.showModal(html, { title: 'Change Password', footer });

        document.getElementById('change-pw-submit').addEventListener('click', async () => {
            const current = document.getElementById('current-pw').value;
            const newPw = document.getElementById('new-pw').value;
            const confirm = document.getElementById('confirm-pw').value;

            if (!current || !newPw) { UI.showToast('Please fill all fields', 'error'); return; }
            if (newPw !== confirm) { UI.showToast('Passwords do not match', 'error'); return; }

            try {
                const result = await api.changePassword(current, newPw);
                if (result.success) {
                    UI.showToast('Password changed! Please login again.', 'success');
                    setTimeout(() => api.logout(), 2000);
                } else {
                    UI.showToast(result.errors?.[0] || 'Failed to change password', 'error');
                }
            } catch (e) {
                UI.showToast(e.message, 'error');
            }
        });
    },

    async toggle2FA(enable) {
        try {
            const result = enable ? await api.enable2FA() : await api.disable2FA();
            if (result.success) {
                UI.showToast(result.message, 'success');
                if (enable) {
                    UI.showModal(`
                        <p style="margin-bottom:1rem;">Scan this secret with your authenticator app:</p>
                        <div class="code-block text-center">${result.secret}</div>
                    `, { title: '2FA Enabled' });
                }
                // Reload profile to reflect change
                this.loadProfile(document.getElementById('page-content'));
            }
        } catch (e) {
            UI.showToast(e.message, 'error');
        }
    },

    // =============================================
    // ADMIN PAGES
    // =============================================
    async loadUsers(container) {
        container.innerHTML = `
            <div class="section-header">
                <h3 class="section-title">User Management</h3>
                <div class="section-header-actions">
                    <div class="search-bar">
                        <span class="search-icon">🔍</span>
                        <input type="text" id="user-search" placeholder="Search users...">
                    </div>
                </div>
            </div>
            <div id="users-list">
                <div class="loading-overlay"><div class="spinner spinner-lg"></div></div>
            </div>
        `;

        await this.refreshUsersList();

        document.getElementById('user-search')?.addEventListener('input', UI.debounce(() => {
            this.refreshUsersList();
        }, 300));
    },

    async refreshUsersList() {
        const container = document.getElementById('users-list');
        if (!container) return;

        try {
            const search = document.getElementById('user-search')?.value || '';
            const data = await api.getUsers(1, search);
            const users = data.users || [];

            if (users.length === 0) {
                UI.showEmpty(container, { icon: '👥', title: 'No Users Found', message: search ? 'Try a different search.' : 'No users registered yet.' });
                return;
            }

            container.innerHTML = `
                <div class="settings-group">
                    <div class="settings-group-body" style="max-height:600px;overflow-y:auto;">
                        ${users.map(u => `
                            <div class="user-card">
                                <div class="user-card-avatar">${(u.username || 'U').charAt(0).toUpperCase()}</div>
                                <div class="user-card-info">
                                    <div class="user-card-name">${UI.escapeHtml(u.full_name || u.username)}</div>
                                    <div class="user-card-email">${u.email || ''} · ${UI.formatDate(u.created_at)}</div>
                                </div>
                                <span>${UI.getStatusBadge(u.is_active ? 'active' : 'inactive')}</span>
                                <span class="badge badge-primary">${u.role}</span>
                                <span class="badge badge-info">${u.plan}</span>
                                <div class="user-card-actions">
                                    <button class="btn-icon" onclick="Dashboard.showEditUserModal(${u.id}, '${u.role}', ${u.is_active}, ${u.max_bots}, ${u.max_commands})" title="Edit User">✏️</button>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                <p class="text-sm text-muted mt-md">Total: ${data.total || users.length} users</p>
            `;
        } catch (e) {
            UI.showError(container, e.message);
        }
    },

    showEditUserModal(userId, currentRole, isActive, maxBots, maxCommands) {
        const html = `
            <div class="form-group">
                <label class="form-label">Role</label>
                <select class="form-select" id="edit-user-role">
                    <option value="user" ${currentRole === 'user' ? 'selected' : ''}>User</option>
                    <option value="moderator" ${currentRole === 'moderator' ? 'selected' : ''}>Moderator</option>
                    <option value="admin" ${currentRole === 'admin' ? 'selected' : ''}>Admin</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Account Status</label>
                <select class="form-select" id="edit-user-status">
                    <option value="1" ${isActive ? 'selected' : ''}>Active</option>
                    <option value="0" ${!isActive ? 'selected' : ''}>Inactive</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Max Bots</label>
                <input class="form-input" id="edit-user-maxbots" type="number" value="${maxBots || 5}">
            </div>
            <div class="form-group">
                <label class="form-label">Max Commands</label>
                <input class="form-input" id="edit-user-maxcmds" type="number" value="${maxCommands || 50}">
            </div>
        `;

        const footer = `
            <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
            <button class="btn btn-primary" id="edit-user-submit">Save</button>
        `;

        UI.showModal(html, { title: `Edit User #${userId}`, footer });

        document.getElementById('edit-user-submit').addEventListener('click', async () => {
            const data = {
                role: document.getElementById('edit-user-role').value,
                is_active: parseInt(document.getElementById('edit-user-status').value),
                max_bots: parseInt(document.getElementById('edit-user-maxbots').value) || 5,
                max_commands: parseInt(document.getElementById('edit-user-maxcmds').value) || 50,
            };

            try {
                const result = await api.updateUser(userId, data);
                if (result.success) {
                    UI.showToast('User updated', 'success');
                    document.querySelector('.modal-overlay').remove();
                    await this.refreshUsersList();
                } else {
                    UI.showToast(result.error || 'Failed to update user', 'error');
                }
            } catch (e) {
                UI.showToast(e.message, 'error');
            }
        });
    },

    // =============================================
    // SECURITY PAGE
    // =============================================
    async loadSecurity(container) {
        container.innerHTML = `
            <div class="section-header">
                <h3 class="section-title">Security Dashboard</h3>
                <button class="btn btn-sm btn-secondary" onclick="Dashboard.loadSecurity(document.getElementById('page-content'))">🔄 Refresh</button>
            </div>
            <div class="grid grid-3" id="security-stats">
                <div class="stat-card"><div class="skeleton skeleton-text"></div></div>
                <div class="stat-card"><div class="skeleton skeleton-text"></div></div>
                <div class="stat-card"><div class="skeleton skeleton-text"></div></div>
            </div>
            <div class="section mt-lg">
                <h3 class="section-title mb-md">Recent Security Events</h3>
                <div id="security-events">
                    <div class="loading-overlay"><div class="spinner"></div></div>
                </div>
            </div>
        `;

        try {
            const data = await api.getSecurityDashboard();
            if (data.success) {
                const sd = data.data;
                document.getElementById('security-stats').innerHTML = `
                    <div class="stat-card">
                        <div class="stat-icon">🔐</div>
                        <div class="stat-value">${sd.failed_logins_today || 0}</div>
                        <div class="stat-label">Failed Logins Today</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">👥</div>
                        <div class="stat-value">${sd.twofa_users || 0}</div>
                        <div class="stat-label">2FA Enabled Users</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">🔑</div>
                        <div class="stat-value">${sd.active_sessions || 0}</div>
                        <div class="stat-label">Active Sessions</div>
                    </div>
                `;

                const events = sd.security_events || [];
                document.getElementById('security-events').innerHTML = events.length === 0
                    ? '<p class="text-muted">No security events recorded.</p>'
                    : `<div class="settings-group"><div class="settings-group-body" style="max-height:400px;overflow-y:auto;">
                        ${events.map(e => `
                            <div class="activity-item">
                                <div class="activity-icon">🛡️</div>
                                <div class="activity-content">
                                    <div class="activity-text">${UI.escapeHtml(e.action)}: ${UI.escapeHtml(e.details)}</div>
                                    <div class="activity-time">${UI.formatDate(e.created_at)} · ${e.ip_address || 'Unknown IP'}</div>
                                </div>
                            </div>
                        `).join('')}
                    </div></div>`;
            }
        } catch (e) {
            UI.showError(document.getElementById('security-events'), e.message);
        }
    }
};

// =============================================
// POLYFILL FOR CANVAS ROUNDRECT
// =============================================
if (!CanvasRenderingContext2D.prototype.roundRect) {
    CanvasRenderingContext2D.prototype.roundRect = function(x, y, w, h, radii) {
        const r = Array.isArray(radii) ? radii : [radii, radii, radii, radii];
        const [tl, tr, br, bl] = r.map(v => Math.min(v || 0, Math.min(w, h) / 2));
        this.moveTo(x + tl, y);
        this.lineTo(x + w - tr, y);
        this.quadraticCurveTo(x + w, y, x + w, y + tr);
        this.lineTo(x + w, y + h - br);
        this.quadraticCurveTo(x + w, y + h, x + w - br, y + h);
        this.lineTo(x + bl, y + h);
        this.quadraticCurveTo(x, y + h, x, y + h - bl);
        this.lineTo(x, y + tl);
        this.quadraticCurveTo(x, y, x + tl, y);
        this.closePath();
        return this;
    };
}

// =============================================
// MOBILE ENHANCEMENTS
// =============================================

// Re-render charts on resize/orientation change
let resizeTimer;
window.addEventListener('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {
        // Only re-render if on overview or analytics page
        const page = Dashboard.currentPage;
        if (page === 'overview') {
            Dashboard.renderActivityChart();
            Dashboard.renderBotsChart();
        } else if (page === 'analytics') {
            Dashboard.renderGrowthChart();
            Dashboard.renderCommandUsageChart();
        }
        // Fix chart container heights on mobile
        document.querySelectorAll('.chart-container').forEach(function(el) {
            if (window.innerWidth <= 768) {
                el.style.height = '200px';
            } else {
                el.style.height = '300px';
            }
        });
    }, 300);
});

// Handle mobile viewport height (fix for mobile browser address bars)
function setVH() {
    const vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', vh + 'px');
}
setVH();
window.addEventListener('resize', setVH);

// Touch-friendly: prevent double-tap zoom on buttons
if ('ontouchstart' in window) {
    document.addEventListener('touchend', function(e) {
        const target = e.target.closest('button, .btn, .nav-item, .nav-item-mob');
        if (target) {
            e.preventDefault();
            target.click();
        }
    }, { passive: false });
}

// =============================================
// INITIALIZE DASHBOARD
// =============================================
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname.includes('dashboard.html') || window.location.pathname.includes('admin.html')) {
        Dashboard.init();
        // Fix initial chart heights for mobile
        if (window.innerWidth <= 768) {
            document.querySelectorAll('.chart-container').forEach(function(el) {
                el.style.height = '200px';
            });
        }
    }
});
