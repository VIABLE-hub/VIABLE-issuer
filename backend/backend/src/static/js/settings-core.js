// 🩺 HERZCHIRURG: Settings Core Module
// Foundation module with shared state and utilities

export const SettingsCore = {
  // ===== SHARED STATE =====
  state: {
    // Global state
    currentTab: 'dashboard',
    theme: 'light',
    isLoading: false,
    showToast: false,
    toastMessage: '',
    toastType: 'success',
    lastUpdated: new Date().toLocaleTimeString(),
    tabsLoaded: {
      dashboard: false,
      system: false,
      database: false,
      network: false,
      api: false,
      keys: false,
      'selective-disclosure': false
    },
    
    // Core state
    isInitialized: false,
    activeTab: 'dashboard'
  },

  // ===== SHARED UTILITIES =====
  methods: {
    // Tab management
    switchToTab(tabName) {
      console.log('Loading data for tab:', tabName);
      
      // Set active tab
      this.activeTab = tabName;
      
      // Load data for the tab if not already loaded
      if (!this.tabsLoaded[tabName]) {
        this.loadTabData(tabName);
        this.tabsLoaded[tabName] = true;
      }
    },

    loadTabData(tabName) {
      switch(tabName) {
        case 'dashboard':
          this.loadDashboard();
          break;
        case 'system':
          this.loadSystemInfo();
          break;
        case 'database':
          this.loadDatabase();
          break;
        case 'network':
          this.loadSimplifiedNetworkData();
          break;
        case 'api':
          this.loadApiKeys();
          break;
        case 'keys':
          this.loadKeyInventory();
          break;
        case 'selective-disclosure':
          this.loadSelectiveDisclosureFields();
          break;
      }
    },

    // Utility functions
    formatUptime(seconds) {
      if (!seconds || seconds < 0) return 'Unknown';
      
      const days = Math.floor(seconds / 86400);
      const hours = Math.floor((seconds % 86400) / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      const secs = Math.floor(seconds % 60);
      
      if (days > 0) {
        return `${days}d ${hours}h ${minutes}m`;
      } else if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
      } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
      } else {
        return `${secs}s`;
      }
    },

    formatBytes(bytes, decimals = 2) {
      if (bytes === 0) return '0 Bytes';
      
      const k = 1024;
      const dm = decimals < 0 ? 0 : decimals;
      const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
      
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      
      return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    },

    formatDate(dateString) {
      try {
        const date = new Date(dateString);
        return date.toLocaleString();
      } catch (error) {
        console.error('Error formatting date:', error);
        return dateString;
      }
    },

    showNotification(message, type = 'info') {
      // Check if notification system exists
      if (typeof window.showNotification === 'function') {
        window.showNotification(message, type);
      } else {
        // Fallback to alert
        alert(message);
      }
    },

    copyToClipboard(text) {
      if (navigator.clipboard && window.isSecureContext) {
        // Use modern clipboard API
        navigator.clipboard.writeText(text).then(() => {
          this.showNotification('Copied to clipboard!', 'success');
        }).catch(err => {
          console.error('Failed to copy to clipboard:', err);
          this.showNotification('Failed to copy to clipboard', 'error');
        });
      } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
          document.execCommand('copy');
          this.showNotification('Copied to clipboard!', 'success');
        } catch (err) {
          console.error('Failed to copy to clipboard:', err);
          this.showNotification('Failed to copy to clipboard', 'error');
        } finally {
          document.body.removeChild(textArea);
        }
      }
    }
  }
}; 