/**
 * 🚀 PERFECT TENANT INTEGRATION
 * Frontend integration for the new unified tenant system
 * 
 * This script enhances the existing settings.js to use the new perfect tenant APIs
 * while maintaining backward compatibility.
 */

console.log('🚀 Perfect Tenant Integration loading...');

// Wait for Alpine.js to be ready
document.addEventListener('alpine:init', () => {
  console.log('🚀 Perfect Tenant Integration initializing...');
  
  // Extend the existing settings component with perfect tenant features
  Alpine.data('perfectTenant', () => ({
    
    // Enhanced network loading with new API
    async loadPerfectNetworkSettings() {
      console.log('🚀 Loading network settings with perfect tenant system...');
      this.networkLoading = true;
      
      try {
        const response = await fetch('/api/network', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'same-origin'
        });
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('🚀 Perfect network data loaded:', data);
        
        if (data.status === 'success') {
          // Update network settings
          this.networkSettings = data.network_settings;
          
          // Update computed URLs
          this.computedUrls = data.computed_urls;
          
          // Update tenant info
          this.tenantInfo = {
            id: data.tenant_id,
            name: data.tenant_name,
            color: data.tenant_color
          };
          
          // Update network info
          this.networkInfo = data.network_info;
          
          // Update connection mode based on settings
          if (data.network_info.use_ngrok) {
            this.connectionMode = 'ngrok';
            this.ngrokDomain = data.network_settings.ngrok_url || '';
          } else {
            this.connectionMode = data.network_settings.connection_mode || 'local';
          }
          
          this.showNotification(`Network settings loaded for ${data.tenant_name}`, 'success');
        } else {
          throw new Error(data.message || 'Failed to load network settings');
        }
        
      } catch (error) {
        console.error('🚀 Error loading perfect network settings:', error);
        this.showNotification(`Error loading network settings: ${error.message}`, 'error');
      } finally {
        this.networkLoading = false;
      }
    },
    
    // Enhanced network saving with new API
    async savePerfectNetworkConfig() {
      console.log('🚀 Saving network config with perfect tenant system...');
      this.networkConfigUpdating = true;
      
      try {
        // Prepare network configuration data
        const networkData = {
          use_ngrok: this.connectionMode === 'ngrok',
          ngrok_url: this.connectionMode === 'ngrok' ? this.ngrokDomain : '',
          connection_mode: this.connectionMode,
          default_port: this.serverPort || 8080,
          use_https: true,
          auto_discovery: false,
          timeout: 30
        };
        
        console.log('🚀 Saving network data:', networkData);
        
        const response = await fetch('/api/network', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'same-origin',
          body: JSON.stringify(networkData)
        });
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('🚀 Perfect network save response:', data);
        
        if (data.status === 'success') {
          this.showNotification('Network configuration saved successfully!', 'success');
          
          // Update local data with response
          if (data.updated_config) {
            this.networkSettings = data.updated_config.network_settings;
            this.computedUrls = data.updated_config.urls;
          }
          
          // Reload to ensure consistency
          setTimeout(() => {
            this.loadPerfectNetworkSettings();
          }, 1000);
          
        } else {
          throw new Error(data.message || 'Failed to save network configuration');
        }
        
      } catch (error) {
        console.error('🚀 Error saving perfect network config:', error);
        this.showNotification(`Error saving network config: ${error.message}`, 'error');
      } finally {
        this.networkConfigUpdating = false;
      }
    },
    
    // Enhanced connection testing with new API
    async testPerfectConnection() {
      console.log('🚀 Testing connection with perfect tenant system...');
      this.testingConnection = true;
      this.connectionTestResults = null;
      
      try {
        const response = await fetch('/api/network/test', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'same-origin'
        });
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('🚀 Perfect connection test results:', data);
        
        if (data.status === 'success') {
          this.connectionTestResults = {
            success: data.overall_status === 'healthy',
            message: `${data.tests_passed}/${data.tests_total} tests passed`,
            components: {}
          };
          
          // Process test results
          Object.keys(data.test_results).forEach(component => {
            const result = data.test_results[component];
            this.connectionTestResults.components[component] = {
              success: result.status === 'success',
              latency: result.latency_ms,
              message: result.error || 'OK',
              url_tested: result.url_tested
            };
          });
          
          const message = data.overall_status === 'healthy' ? 
            'All connection tests passed!' : 
            'Some connection tests failed - check results below';
            
          this.showNotification(message, data.overall_status === 'healthy' ? 'success' : 'warning');
          
        } else {
          throw new Error(data.message || 'Connection test failed');
        }
        
      } catch (error) {
        console.error('🚀 Error testing perfect connection:', error);
        this.showNotification(`Connection test error: ${error.message}`, 'error');
        
        this.connectionTestResults = {
          success: false,
          message: error.message,
          components: {}
        };
      } finally {
        this.testingConnection = false;
      }
    },
    
    // Clear configuration cache
    async clearPerfectTenantCache() {
      console.log('🚀 Clearing perfect tenant cache...');
      
      try {
        const response = await fetch('/api/network/cache/clear', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'same-origin'
        });
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
          this.showNotification('Configuration cache cleared successfully', 'success');
          
          // Reload network settings
          this.loadPerfectNetworkSettings();
        } else {
          throw new Error(data.message || 'Failed to clear cache');
        }
        
      } catch (error) {
        console.error('🚀 Error clearing perfect tenant cache:', error);
        this.showNotification(`Error clearing cache: ${error.message}`, 'error');
      }
    },
    
    // Get perfect URLs for display
    getPerfectIssuerUrl() {
      if (this.computedUrls && this.computedUrls.issuer_url) {
        return this.computedUrls.issuer_url;
      }
      return this.getDynamicIssuerUrl(); // Fallback to original method
    },
    
    getPerfectVerifierUrl() {
      if (this.computedUrls && this.computedUrls.verifier_url) {
        return this.computedUrls.verifier_url;
      }
      return this.getDynamicVerifierUrl(); // Fallback to original method
    },
    
    getPerfectServerUrl() {
      if (this.computedUrls && this.computedUrls.server_url) {
        return this.computedUrls.server_url;
      }
      return 'Loading...';
    },
    
    // Initialize perfect tenant integration
    initPerfectTenant() {
      console.log('🚀 Initializing perfect tenant integration...');
      
      // Initialize state
      this.computedUrls = {};
      this.tenantInfo = {};
      this.networkInfo = {};
      
      // Auto-load network settings if we're on the network tab
      if (this.activeTab === 'network') {
        this.loadPerfectNetworkSettings();
      }
      
      console.log('🚀 Perfect tenant integration initialized!');
    }
  }));
  
  console.log('🚀 Perfect Tenant Integration ready!');
});

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  console.log('🚀 Perfect Tenant Integration DOM ready');
  
  // Add perfect tenant styles
  const style = document.createElement('style');
  style.textContent = `
    .perfect-tenant-indicator {
      background: linear-gradient(45deg, #4CAF50, #2196F3);
      color: white;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 0.8em;
      font-weight: bold;
      margin-left: 8px;
    }
    
    .perfect-tenant-status {
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
    
    .perfect-tenant-status.success::before {
      content: '✅';
    }
    
    .perfect-tenant-status.error::before {
      content: '❌';
    }
    
    .perfect-tenant-status.loading::before {
      content: '⏳';
    }
  `;
  document.head.appendChild(style);
});

// Export functions for global access
window.PerfectTenant = {
  // Check if perfect tenant system is available
  isAvailable() {
    return typeof Alpine !== 'undefined' && window.location.pathname.includes('settings');
  },
  
  // Get current tenant info
  getCurrentTenant() {
    if (this.isAvailable() && Alpine.store && Alpine.store('settings')) {
      return Alpine.store('settings').tenantInfo;
    }
    return null;
  },
  
  // Manually trigger network reload
  reloadNetworkSettings() {
    if (this.isAvailable()) {
      // Find settings component and trigger reload
      const settingsEl = document.querySelector('[x-data*="settings"]');
      if (settingsEl && settingsEl._x_dataStack) {
        const settingsData = settingsEl._x_dataStack[0];
        if (settingsData.loadPerfectNetworkSettings) {
          settingsData.loadPerfectNetworkSettings();
        }
      }
    }
  }
};

console.log('🚀 Perfect Tenant Integration loaded successfully!'); 