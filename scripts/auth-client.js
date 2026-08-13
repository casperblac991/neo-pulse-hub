/**
 * Neo Pulse Hub - Client-side Auth Helper
 * Handles session checking and UI updates for static HTML pages.
 */

const AuthClient = {
    user: null,
    loading: true,

    async checkAuth() {
        try {
            const response = await fetch('/api/trpc/auth.me?batch=1&input=%7B%7D');
            if (response.ok) {
                const data = await response.json();
                if (data && data[0] && data[0].result && data[0].result.data) {
                    this.user = data[0].result.data;
                    this.updateUI();
                    return this.user;
                }
            }
        } catch (error) {
            console.error('[Auth] Failed to check auth state:', error);
        } finally {
            this.loading = false;
        }
        this.updateUI();
        return null;
    },

    getLoginUrl() {
        // This should match the logic in const.ts
        const appId = 'neo-pulse-hub'; // Default fallback
        const redirectUri = `${window.location.origin}/api/oauth/callback`;
        const state = btoa(redirectUri);
        // We'll try to fetch config if needed, but for now use a standard pattern
        return `https://manus.im/app-auth?appId=${appId}&redirectUri=${encodeURIComponent(redirectUri)}&state=${state}&type=signIn`;
    },

    updateUI() {
        const authContainer = document.getElementById('auth-nav-item');
        if (!authContainer) return;

        if (this.user) {
            authContainer.innerHTML = `
                <div class="user-dropdown">
                    <button class="nav-cart" style="background:rgba(16,185,129,0.1);border-color:rgba(16,185,129,0.2)">
                        👤 ${this.user.name || 'User'}
                    </button>
                    <div class="dropdown-content">
                        <a href="/dashboard">Dashboard</a>
                        <a href="#" onclick="AuthClient.logout(event)">Logout</a>
                    </div>
                </div>
            `;
        } else {
            authContainer.innerHTML = `
                <a href="${this.getLoginUrl()}" class="nav-cart">
                    🔐 Login
                </a>
            `;
        }
    },

    async logout(e) {
        if (e) e.preventDefault();
        try {
            await fetch('/api/trpc/auth.logout', { method: 'POST' });
            window.location.reload();
        } catch (error) {
            console.error('[Auth] Logout failed:', error);
        }
    }
};

// Initialize on load
window.addEventListener('DOMContentLoaded', () => {
    AuthClient.checkAuth();
});
