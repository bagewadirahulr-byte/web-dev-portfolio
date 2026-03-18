/**
 * Shared Error Handling & Ultra-Stability Utility
 * Future-proofed for 5+ years (2025-2030+)
 */

window.ErrorHandler = {
    /**
     * Display a toast notification on the screen.
     */
    showToast: function(message, type = 'error') {
        let toast = document.getElementById('error-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'error-toast';
            toast.style.cssText = `
                position: fixed;
                bottom: 30px;
                left: 50%;
                transform: translateX(-50%) translateY(100px);
                padding: 14px 28px;
                border-radius: 16px;
                color: white;
                font-family: 'Outfit', sans-serif;
                font-weight: 600;
                z-index: 10000;
                transition: transform 0.5s cubic-bezier(0.19, 1, 0.22, 1);
                box-shadow: 0 15px 40px rgba(0,0,0,0.4);
                text-align: center;
                pointer-events: none;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.1);
            `;
            document.body.appendChild(toast);
        }

        const colors = {
            error: 'linear-gradient(135deg, rgba(239,68,68,0.9), rgba(185,28,28,0.9))',
            success: 'linear-gradient(135deg, rgba(16,185,129,0.9), rgba(5,150,105,0.9))',
            info: 'linear-gradient(135deg, rgba(59,130,246,0.9), rgba(29,78,216,0.9))'
        };

        toast.style.background = colors[type] || colors.error;
        toast.textContent = message;
        toast.style.transform = 'translateX(-50%) translateY(0)';

        setTimeout(() => {
            toast.style.transform = 'translateX(-50%) translateY(100px)';
        }, 5000);
    },

    /**
     * Fetch wrapper with timeout and retry logic for 5-year stability.
     */
    fetchWithTimeout: async function(url, options = {}, timeout = 8000, retries = 2) {
        const controller = new AbortController();
        const id = setTimeout(() => controller.abort(), timeout);

        try {
            const response = await fetch(url, { ...options, signal: controller.signal });
            clearTimeout(id);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response;
        } catch (err) {
            clearTimeout(id);
            if (retries > 0 && err.name !== 'AbortError') {
                console.warn(`Retrying fetch: ${url} (${retries} left)`);
                await new Promise(res => setTimeout(res, 1500)); // wait before retry
                return this.fetchWithTimeout(url, options, timeout, retries - 1);
            }
            throw err;
        }
    },

    /**
     * Check if a service is online.
     */
    checkHealth: async function(url) {
        try {
            const res = await fetch(url, { method: 'HEAD', mode: 'no-cors', cache: 'no-store' });
            return true;
        } catch (e) {
            return false;
        }
    },

    /**
     * Dynamic Copyright Year logic.
     */
    updateCopyright: function(id, startYear = 2025) {
        const el = document.getElementById(id);
        const currentYear = new Date().getFullYear();
        if (el) {
            el.textContent = currentYear > startYear ? `${startYear}–${currentYear}` : startYear;
        }
    },

    init: function() {
        window.addEventListener('error', (event) => {
            console.error('Stability Monitor - Uncaught Error:', event.error);
        });

        window.addEventListener('unhandledrejection', (event) => {
            console.error('Stability Monitor - Promise Rejection:', event.reason);
            // Only show toast for actual user-facing failures if they happen
        });
        
        console.log('🚀 Stability Monitor Active (2025-2031+)');
    }
};

window.ErrorHandler.init();
