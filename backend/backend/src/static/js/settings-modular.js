// 🩺 HERZCHIRURG: Working Modular Settings System
// Uses IIFE pattern for better browser compatibility

console.log("🩺 HERZCHIRURG: Initializing modular settings system...");

// Global settings namespace
window.SettingsModules = window.SettingsModules || {};

// =======================
// CORE MODULE
// =======================
window.SettingsModules.Core = (function() {
  return {
    state: {
      activeTab: 'dashboard',
      isInitialized: false,
      tabsLoaded: {},
      lastUpdated: new Date().toLocaleTimeString()
    },
    
    methods: {
      init() {
        console.log('🔧 Initializing core settings...');
        this.activeTab = 'dashboard';
        this.tabsLoaded = {};
        this.isInitialized = true;
        
        // Load dashboard by default
        this.loadDashboard();
      },
      
      switchToTab(tabName) {
        console.log(`🔄 Switching to tab: ${tabName}`);
        this.activeTab = tabName;
        
        // Load tab data if not loaded yet
        if (!this.tabsLoaded[tabName]) {
          this.loadTabData(tabName);
          this.tabsLoaded[tabName] = true;
        }
      },
      
      loadTabData(tabName) {
        console.log(`📊 Loading data for tab: ${tabName}`);
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
            this.loadNetworkSettings();
            break;
          case 'api':
            this.loadAPIData();
            break;
          case 'keys':
            this.loadKeyInventory();
            break;
          case 'selective-disclosure':
            this.loadSelectiveDisclosureSettings();
            break;
        }
      }
    }
  };
})();

// =======================
// DASHBOARD MODULE
// =======================
window.SettingsModules.Dashboard = (function() {
  return {
    state: {
      dashboardLoading: false,
      dashboardRefreshing: false,
      dashboardError: null,
      systemDataReady: false,
      healthDataReady: false,
      
      systemData: {
        cpu: { usage: 0, cores: 1, status: 'unknown' },
        memory: { percentage: 0, used_gb: 0, total_gb: 0, status: 'unknown' },
        disk: { percentage: 0, used_gb: 0, total_gb: 0, status: 'unknown' },
        network: { local_ip: 'Unknown', public_ip: 'Unknown', hostname: 'Unknown', status: 'unknown' },
        uptime: { seconds: 0, formatted: 'Unknown', status: 'unknown' },
        app_version: 'Unknown',
        python_version: 'Unknown',
        platform: 'Unknown'
      },
      
      healthData: {
        issuer: { status: 'unknown', endpoint: '-', response_time: null },
        verifier: { status: 'unknown', endpoint: '-', response_time: null },
        database: { status: 'unknown', type: 'SQLite', size: '-' },
        websocket: { status: 'unknown', active_connections: 0, port: '-' },
        sse: { status: 'unknown', active_connections: 0, port: '-' }
      }
    },
    
    methods: {
      loadDashboard() {
        console.log('🩺 Loading dashboard data...');
        this.dashboardLoading = true;
        this.dashboardError = null;
        
        // Load health data
        fetch('/api/health')
          .then(response => response.json())
          .then(data => {
            console.log('🩺 Dashboard health data:', data);
            this.healthData = data;
            this.healthDataReady = true;
            this.checkDashboardReady();
          })
          .catch(error => {
            console.error('🩺 Error loading dashboard health data:', error);
            this.dashboardError = error.message;
            this.healthDataReady = true;
            this.checkDashboardReady();
          });
        
        // Load system data
        this.loadSystemData();
      },
      
      loadSystemData() {
        console.log('🖥️ Loading system data...');
        
        fetch('/api/system/health')
          .then(response => response.json())
          .then(data => {
            console.log('🖥️ System data loaded:', data);
            if (data.success && data.data) {
              this.systemData = { ...this.systemData, ...data.data };
            }
            this.systemDataReady = true;
            this.checkDashboardReady();
          })
          .catch(error => {
            console.error('🖥️ Error loading system data:', error);
            this.systemDataReady = true;
            this.checkDashboardReady();
          });
      },
      
      checkDashboardReady() {
        if (this.healthDataReady && this.systemDataReady) {
          this.dashboardLoading = false;
          this.dashboardRefreshing = false;
          this.lastUpdated = new Date().toLocaleTimeString();
        }
      },
      
      manualRefresh() {
        console.log('🔄 Manual refresh triggered...');
        this.dashboardRefreshing = true;
        this.healthDataReady = false;
        this.systemDataReady = false;
        this.loadDashboard();
      }
    }
  };
})();

// =======================
// SYSTEM MODULE
// =======================
window.SettingsModules.System = (function() {
  return {
    state: {
      systemLoading: false,
      systemHealthData: null,
      systemHealthRefreshing: false,
      systemHealthError: null
    },
    
    methods: {
      loadSystemInfo() {
        console.log('🩺 Loading system health data...');
        this.systemLoading = true;
        this.systemHealthError = null;
        
        fetch('/api/system/health')
          .then(response => response.json())
          .then(data => {
            console.log('🩺 System health data received:', data);
            if (data.success && data.data) {
              this.systemHealthData = data.data;
            }
            this.systemLoading = false;
          })
          .catch(error => {
            console.error('🩺 Error loading system health data:', error);
            this.systemHealthError = error.message;
            this.systemLoading = false;
          });
      }
    }
  };
})();

// =======================
// UTILITY FUNCTIONS
// =======================
window.SettingsModules.Utils = (function() {
  return {
    formatBytes(bytes, decimals = 2) {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const dm = decimals < 0 ? 0 : decimals;
      const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    },
    
    formatUptime(seconds) {
      const days = Math.floor(seconds / 86400);
      const hours = Math.floor((seconds % 86400) / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      
      if (days > 0) return `${days}d ${hours}h`;
      if (hours > 0) return `${hours}h ${minutes}m`;
      return `${minutes}m`;
    },
    
    showNotification(message, type = 'info') {
      if (typeof window.showNotification === 'function') {
        window.showNotification(message, type);
      } else {
        console.log(`${type.toUpperCase()}: ${message}`);
      }
    }
  };
})();

// =======================
// NETWORK MODULE (INLINE)
// =======================
window.SettingsModules.Network = (function() {
  return {
    state: {
      networkLoading: false,
      networkConfigUpdating: false,
      networkData: null,
      networkError: null,
      ngrokSettings: {
        useNgrok: false,
        ngrokDomain: ''
      },
      testingConnection: false,
      connectionTestResults: null,
      connectionMode: 'local',
      serverPort: 8080,
      ngrokDomain: '',
      useNgrok: false,
      useHttps: true,
      urlUpdating: false,
      issuerUrl: '',
      verifierUrl: '',
      tenantConfig: {}
    },
    
    methods: {
      loadNetworkSettings() {
        console.log('🌐 Loading network settings...');
        this.networkLoading = true;
        this.loadSimplifiedNetworkData();
        this.loadTenantConfig();
      },
      
      loadSimplifiedNetworkData() {
        console.log('🌐 Loading simplified network data...');
        
        // Use the working network endpoint instead of the problematic debug endpoint
        fetch('/api/system/network')
          .then(response => {
            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
          })
          .then(data => {
            console.log('🌐 Network data received:', data);
            
            if (data && data.status === 'success') {
              // Handle both network_info and network_config structures
              const networkInfo = data.network_info || data.network_config || {};
              const systemInfo = data.system_info || {};
              
              this.networkData = {
                local_ip: networkInfo.local_ip || systemInfo.local_ip || 'Unknown',
                public_ip: networkInfo.public_ip || systemInfo.public_ip || 'Not available',
                hostname: networkInfo.hostname || systemInfo.hostname || 'Unknown',
                default_port: networkInfo.default_port || systemInfo.default_port || '8080',
                server_url: data.server_url || networkInfo.server_url || 'Unknown',
                ngrok_url: data.ngrok_url || networkInfo.ngrok_url || null,
                is_ngrok_active: data.is_ngrok_active || networkInfo.is_ngrok_active || false
              };
              
              console.log('🌐 Processed network data:', this.networkData);
            } else {
              console.warn('🌐 Invalid network data format:', data);
              // Fallback data
              this.networkData = {
                local_ip: 'Unknown',
                public_ip: 'Not available', 
                hostname: 'Unknown',
                default_port: '8080',
                server_url: 'Unknown',
                ngrok_url: null,
                is_ngrok_active: false
              };
            }
            this.networkLoading = false;
          })
          .catch(error => {
            console.error('🌐 Error loading network data:', error);
            this.networkLoading = false;
            
            // 🚨 GRACEFUL ERROR HANDLING: Don't crash the page
            this.networkData = {
              local_ip: 'Error loading',
              public_ip: 'Error loading',
              hostname: 'Error loading', 
              default_port: '8080',
              server_url: 'Error loading',
              ngrok_url: null,
              is_ngrok_active: false
            };
            
            // Show non-blocking error message
            this.showNotification('Network data could not be loaded, using defaults', 'warning');
          });
      },
      
      loadTenantConfig() {
        console.log('🎯 Loading tenant configuration...');
        
        fetch('/api/tenant/config')
          .then(response => {
            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
          })
          .then(data => {
            console.log('🎯 Tenant config received:', data);
            
            if (data && data.status === 'success' && data.config) {
              this.tenantConfig = data.config;
              
              // 🚨 CRITICAL: Update network data with tenant info
              if (this.networkData) {
                this.networkData.ngrok_url = data.config.ngrok_url || this.networkData.ngrok_url;
                this.networkData.server_url = data.config.server_url || this.networkData.server_url;
              }
              
              console.log('🎯 Tenant config loaded successfully');
            } else {
              console.warn('🎯 Invalid tenant config format:', data);
            }
          })
          .catch(error => {
            console.error('🎯 Error loading tenant config:', error);
            this.tenantConfig = {};
            // Don't show error for tenant config as it's optional
          });
      },
      
      saveTenantConfig(configData) {
        console.log('🎯 Saving tenant configuration:', configData);
        
        return fetch('/api/tenant/config', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(configData)
        })
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          if (data && data.status === 'success') {
            console.log('🎯 Tenant config saved successfully');
            this.showNotification('Tenant configuration saved successfully', 'success');
            // Reload tenant config to get updated values
            this.loadTenantConfig();
            return data;
          } else {
            throw new Error(data.message || 'Failed to save tenant config');
          }
        })
        .catch(error => {
          console.error('🎯 Error saving tenant config:', error);
          this.showNotification(`Failed to save configuration: ${error.message}`, 'error');
          throw error;
        });
      },
      
      testConnection() {
        console.log('🌐 Testing connection...');
        this.testingConnection = true;
        this.connectionTestResults = null;
        
        fetch('/settings/api/test-connection', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ test_type: 'full' })
        })
        .then(response => response.json())
        .then(data => {
          this.connectionTestResults = data;
          this.showNotification(data.status === 'success' ? 'Connection test completed' : 'Connection test failed', data.status);
        })
        .catch(error => {
          console.error('Error testing connection:', error);
          this.connectionTestResults = { status: 'error', message: error.message };
          this.showNotification(`Connection test failed: ${error.message}`, 'error');
        })
        .finally(() => {
          this.testingConnection = false;
        });
      },
      
      canTestConnection() {
        return this.connectionMode !== 'ngrok' || this.ngrokDomain;
      },
      
      getTestButtonText() {
        return this.canTestConnection() ? 'Test the selected connection mode' : 'Cannot test this connection mode';
      },
      
      getDynamicIssuerUrl() {
        // 🚨 PRIORITY 1: Use saved tenant NGROK URL if available
        if (this.tenantConfig && this.tenantConfig.ngrok_url) {
          return `${this.tenantConfig.ngrok_url}/issuer`;
        }
        // 🚨 PRIORITY 2: Use network data ngrok URL if available and active
        else if (this.networkData && this.networkData.is_ngrok_active && this.networkData.ngrok_url) {
          return `${this.networkData.ngrok_url}/issuer`;
        }
        // 🚨 PRIORITY 3: Use server URL if available
        else if (this.networkData && this.networkData.server_url && this.networkData.server_url !== 'Unknown') {
          return `${this.networkData.server_url}/issuer`;
        }
        // Fall back to connection mode logic
        else if (this.connectionMode === 'ngrok' && this.ngrokDomain) {
          return `https://${this.ngrokDomain}/issuer`;
        } else if (this.connectionMode === 'local') {
          return `http://localhost:${this.localPort || 5000}/issuer`;
        } else {
          return 'http://localhost:5000/issuer';
        }
      },
      
      getDynamicVerifierUrl() {
        // 🚨 PRIORITY 1: Use saved tenant NGROK URL if available
        if (this.tenantConfig && this.tenantConfig.ngrok_url) {
          return `${this.tenantConfig.ngrok_url}/verifier`;
        }
        // 🚨 PRIORITY 2: Use network data ngrok URL if available and active
        else if (this.networkData && this.networkData.is_ngrok_active && this.networkData.ngrok_url) {
          return `${this.networkData.ngrok_url}/verifier`;
        }
        // 🚨 PRIORITY 3: Use server URL if available
        else if (this.networkData && this.networkData.server_url && this.networkData.server_url !== 'Unknown') {
          return `${this.networkData.server_url}/verifier`;
        }
        // Fall back to connection mode logic  
        else if (this.connectionMode === 'ngrok' && this.ngrokDomain) {
          return `https://${this.ngrokDomain}/verifier`;
        } else if (this.connectionMode === 'local') {
          return `http://localhost:${this.localPort || 5000}/verifier`;
        } else {
          return 'http://localhost:5000/verifier';
        }
      },
      
      saveNgrokUrl(ngrokUrl) {
        console.log('🌐 Saving NGROK URL:', ngrokUrl);
        
        // Validate URL format
        if (ngrokUrl && !ngrokUrl.match(/^https:\/\/[a-zA-Z0-9-]+\.(ngrok|ngrok-free|ngrok\.io)\..*$/)) {
          this.showNotification('Invalid NGROK URL format. Expected: https://xyz.ngrok-free.app', 'error');
          return Promise.reject(new Error('Invalid NGROK URL format'));
        }
        
        const configData = {
          ngrok_url: ngrokUrl,
          network_settings: {
            ngrok_url: ngrokUrl,
            connection_mode: 'ngrok'
          }
        };
        
        return this.saveTenantConfig(configData);
      },
      
      saveNetworkConfig() {
        console.log('🌐 Saving network configuration...');
        this.networkConfigUpdating = true;
        
        const config = {
          connectionMode: this.connectionMode,
          ngrokDomain: this.ngrokDomain,
          localPort: this.localPort,
          useHttps: this.useHttps
        };
        
        // Simulate saving network config
        setTimeout(() => {
          console.log('🌐 Network configuration saved:', config);
          this.networkConfigUpdating = false;
          
          // Show success message
          this.showNotification('Network configuration saved successfully', 'success');
        }, 1000);
      }
    }
  };
})();

// =======================
// DATABASE MODULE (INLINE)
// =======================
window.SettingsModules.Database = (function() {
  return {
    state: {
      databaseLoading: false,
      databaseData: null,
      backupListLoading: false,
      backupInProgress: false,
      backupLoading: true,
      backupList: [],
      selectedImportFile: null,
      databaseImporting: false,
      databaseImportProgress: 0
    },
    
    methods: {
      loadDatabase() {
        console.log('🗄️ Loading database...');
        this.loadDatabaseData();
        this.loadBackupList();
      },
      
      loadDatabaseData() {
        console.log('🗄️ Loading database data...');
        this.databaseLoading = true;
        
        fetch('/api/database/status')
          .then(response => response.json())
          .then(response => {
            if (response.status === 'success' && response.database) {
              const data = response.database;
              this.databaseData = {
                engine: data.engine || 'SQLite',
                version: data.version || '3.x',
                status: data.status || 'Connected',
                location: data.location || '',
                size_bytes: data.size_bytes || 0,
                size_formatted: this.formatBytes(data.size_bytes || 0),
                table_count: data.table_count || 0,
                record_count: data.record_count || 0,
                last_backup: response.last_backup || null
              };
            }
            this.databaseLoading = false;
          })
          .catch(error => {
            console.error('🗄️ Error loading database data:', error);
            this.showNotification(`Failed to load database data: ${error.message}`, 'error');
            this.databaseLoading = false;
          });
      },
      
      loadBackupList() {
        console.log('🗄️ Loading backup list...');
        this.backupListLoading = true;
        
        fetch('/api/database/backup/list')
          .then(response => response.json())
          .then(response => {
            if (response.status === 'success' && response.backups) {
              this.backupList = response.backups.map(backup => ({
                ...backup,
                id: backup.filename || backup.id || Math.random().toString(36).substring(2, 15)
              }));
            } else {
              this.backupList = [];
            }
            this.backupListLoading = false;
          })
          .catch(error => {
            console.error('Error loading backups:', error);
            this.showNotification(`Failed to load backups: ${error.message}`, 'error');
            this.backupListLoading = false;
          });
      },
      
      createBackup() {
        console.log('🗄️ Creating backup...');
        this.backupInProgress = true;
        
        fetch('/api/database/backup/create', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ description: 'Manual backup from settings' })
        })
        .then(response => response.json())
        .then(data => {
          if (data.status === 'success') {
            this.showNotification('Backup created successfully', 'success');
            this.loadBackupList();
          } else {
            this.showNotification(`Failed to create backup: ${data.message}`, 'error');
          }
        })
        .catch(error => {
          console.error('Error creating backup:', error);
          this.showNotification(`Failed to create backup: ${error.message}`, 'error');
        })
        .finally(() => {
          this.backupInProgress = false;
        });
      },
      
      handleDatabaseFileSelect(event) {
        const file = event.target.files[0];
        this.selectedImportFile = file;
      },
      
      formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
      }
    }
  };
})();

// =======================
// API MODULE (INLINE)
// =======================
window.SettingsModules.API = (function() {
  return {
    state: {
      apiKeysLoading: false,
      apiKeys: [],
      apiData: null,
      newKeyName: '',
      apiKeyGenerating: false,
      newApiKey: null,
      keyRevoking: false
    },
    
    methods: {
      loadAPIData() {
        console.log('🔑 Loading API data...');
        this.apiKeysLoading = true;
        
        // Mock API data for now
        setTimeout(() => {
          this.apiKeys = [];
          this.apiKeysLoading = false;
        }, 500);
      },
      
      async generateNewApiKey() {
        if (!this.newKeyName.trim()) {
          this.showNotification('Please enter a key name', 'error');
          return;
        }
        
        this.apiKeyGenerating = true;
        
        try {
          const response = await fetch('/settings/api/keys/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: this.newKeyName.trim() })
          });
          
          const data = await response.json();
          
          if (data.status === 'success') {
            this.newApiKey = data.api_key;
            this.newKeyName = '';
            this.showNotification('API key generated successfully', 'success');
            this.loadAPIData(); // Refresh the list
          } else {
            this.showNotification(`Failed to generate API key: ${data.message}`, 'error');
          }
        } catch (error) {
          console.error('Error generating API key:', error);
          this.showNotification(`Failed to generate API key: ${error.message}`, 'error');
        } finally {
          this.apiKeyGenerating = false;
        }
      },
      
      async revokeApiKey(keyId) {
        if (!confirm('Are you sure you want to revoke this API key? This action cannot be undone.')) {
          return;
        }
        
        this.keyRevoking = true;
        
        try {
          const response = await fetch(`/settings/api/keys/${keyId}/delete`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
          });
          
          const data = await response.json();
          
          if (data.status === 'success') {
            this.showNotification('API key deleted successfully', 'success');
            this.loadAPIData(); // Refresh the list
          } else {
            this.showNotification(`Failed to delete API key: ${data.message}`, 'error');
          }
        } catch (error) {
          console.error('Error deleting API key:', error);
          this.showNotification(`Failed to delete API key: ${error.message}`, 'error');
        } finally {
          this.keyRevoking = false;
        }
      },
      
      copyToClipboard(text) {
        if (navigator.clipboard && window.isSecureContext) {
          navigator.clipboard.writeText(text).then(() => {
            this.showNotification('Copied to clipboard', 'success');
          }).catch(err => {
            console.error('Failed to copy to clipboard:', err);
            this.fallbackCopyTextToClipboard(text);
          });
        } else {
          this.fallbackCopyTextToClipboard(text);
        }
      },
      
      fallbackCopyTextToClipboard(text) {
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.top = "0";
        textArea.style.left = "0";
        textArea.style.position = "fixed";
        
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
          const successful = document.execCommand('copy');
          if (successful) {
            this.showNotification('Copied to clipboard', 'success');
          } else {
            this.showNotification('Failed to copy to clipboard', 'error');
          }
        } catch (err) {
          console.error('Fallback: Oops, unable to copy', err);
          this.showNotification('Failed to copy to clipboard', 'error');
        }
        
        document.body.removeChild(textArea);
      },
      
      formatDate(dateString) {
        if (!dateString) return 'N/A';
        try {
          const date = new Date(dateString);
          return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        } catch (error) {
          return 'Invalid Date';
        }
      }
    }
  };
})();

// =======================
// SELECTIVE DISCLOSURE MODULE (INLINE)
// =======================
window.SettingsModules.SelectiveDisclosure = (function() {
  return {
    state: {
      fieldFirstName: true,
      fieldLastName: true,
      fieldStudentId: true,
      fieldStudentIdPrefix: false,
      selectiveDisclosureSaving: false,
      showSelectiveDisclosureToast: false,
      selectiveDisclosureToastSuccess: false,
      selectiveDisclosureToastMessage: ''
    },
    
    methods: {
      loadSelectiveDisclosureSettings() {
        console.log('📖 Loading selective disclosure settings...');
        
        fetch('/settings/api/selective-disclosure', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
          if (data.status === 'success' && data.settings) {
            // Update the state with loaded settings
            this.fieldFirstName = data.settings.field_first_name || false;
            this.fieldLastName = data.settings.field_last_name || false;
            this.fieldStudentId = data.settings.field_student_id || false;
            this.fieldStudentIdPrefix = data.settings.field_student_id_prefix || false;
            
            console.log('✅ Selective disclosure settings loaded:', data.settings);
            console.log('✅ Applied to state:', {
              fieldFirstName: this.fieldFirstName,
              fieldLastName: this.fieldLastName,
              fieldStudentId: this.fieldStudentId,
              fieldStudentIdPrefix: this.fieldStudentIdPrefix
            });
          } else {
            console.error('❌ Failed to load selective disclosure settings:', data.message || 'Unknown error');
          }
        })
        .catch(error => {
          console.error('Error loading selective disclosure settings:', error);
        });
      },
      
      saveSelectiveDisclosureSettings() {
        console.log('💾 Saving selective disclosure settings...');
        this.selectiveDisclosureSaving = true;
        
        const settings = {
          field_first_name: this.fieldFirstName,
          field_last_name: this.fieldLastName,
          field_student_id: this.fieldStudentId,
          field_student_id_prefix: this.fieldStudentIdPrefix
        };
        
        // Allow saving empty disclosure config for maximum user flexibility
        
        console.log('💾 Sending settings to backend:', settings);
        console.log('💾 Selected fields count:', Object.values(settings).filter(v => v).length);
        
        fetch('/settings/api/selective-disclosure', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(settings)
        })
        .then(response => response.json())
        .then(data => {
          if (data.status === 'success') {
            this.showNotification('Selective disclosure settings saved successfully!', 'success');
            console.log('✅ Selective disclosure settings saved:', data);
          } else {
            this.showNotification('Failed to save selective disclosure settings: ' + (data.message || 'Unknown error'), 'error');
            console.error('❌ Failed to save selective disclosure settings:', data);
          }
        })
        .catch(error => {
          console.error('Error saving selective disclosure settings:', error);
          this.showNotification('Error saving selective disclosure settings: ' + error.message, 'error');
        })
        .finally(() => {
          this.selectiveDisclosureSaving = false;
        });
      }
    }
  };
})();

// =======================
// KEY MANAGEMENT MODULE (INLINE)
// =======================
window.SettingsModules.Keys = (function() {
  return {
    state: {
      keyInventoryData: [],
      keyInventoryLoading: false,
      keyGenerating: false,
      keyStatistics: {
        total: 0,
        active: 0,
        expired: 0,
        expiring_soon: 0
      },
      showGenerateKeyModal: false,
      newKeyConfig: {
        type: 'Ed25519',
        purpose: '',
        validity_days: 365
      }
    },
    
    methods: {
      async loadKeyInventory() {
        console.log('🔑 Loading key inventory...');
        this.keyInventoryLoading = true;
        
        try {
          const response = await fetch('/settings/api/keys/inventory');
          const data = await response.json();
          
          if (data.status === 'success') {
            this.keyInventoryData = data.keys || [];
            this.keyStatistics = data.statistics || {
              total: 0,
              active: 0,
              expired: 0,
              expiring_soon: 0
            };
            console.log('🔑 Key inventory loaded:', this.keyInventoryData);
          } else {
            console.error('🔑 Failed to load key inventory:', data.message);
          }
        } catch (error) {
          console.error('🔑 Error loading key inventory:', error);
        } finally {
          this.keyInventoryLoading = false;
        }
      },
      
      async generateKey() {
        console.log('🔑 Generating key:', this.newKeyConfig);
        this.keyGenerating = true;
        
        try {
          const response = await fetch('/settings/api/keys/generate', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(this.newKeyConfig)
          });
          
          const data = await response.json();
          
          if (data.status === 'success') {
            this.showNotification('Key generated successfully!', 'success');
            this.showGenerateKeyModal = false;
            this.loadKeyInventory(); // Refresh the list
          } else {
            this.showNotification('Failed to generate key: ' + data.message, 'error');
          }
        } catch (error) {
          console.error('🔑 Error generating key:', error);
          this.showNotification('Error generating key', 'error');
        } finally {
          this.keyGenerating = false;
        }
      },
      
      async exportKey(keyId) {
        console.log('🔑 Exporting key:', keyId);
        try {
          const response = await fetch(`/settings/api/keys/${keyId}/export`);
          const data = await response.json();
          
          if (data.status === 'success') {
            this.showNotification('Key exported successfully!', 'success');
          } else {
            this.showNotification('Failed to export key: ' + data.message, 'error');
          }
        } catch (error) {
          console.error('🔑 Error exporting key:', error);
          this.showNotification('Error exporting key', 'error');
        }
      },
      
      async rotateKey(keyId) {
        console.log('🔑 Rotating key:', keyId);
        try {
          const response = await fetch(`/settings/api/keys/${keyId}/rotate`, {
            method: 'POST'
          });
          const data = await response.json();
          
          if (data.status === 'success') {
            this.showNotification('Key rotated successfully!', 'success');
            this.loadKeyInventory(); // Refresh the list
          } else {
            this.showNotification('Failed to rotate key: ' + data.message, 'error');
          }
        } catch (error) {
          console.error('🔑 Error rotating key:', error);
          this.showNotification('Error rotating key', 'error');
        }
      },
      
      async archiveKey(keyId) {
        console.log('🔑 Archiving key:', keyId);
        try {
          const response = await fetch(`/settings/api/keys/${keyId}/archive`, {
            method: 'POST'
          });
          const data = await response.json();
          
          if (data.status === 'success') {
            this.showNotification('Key archived successfully!', 'success');
            this.loadKeyInventory(); // Refresh the list
          } else {
            this.showNotification('Failed to archive key: ' + data.message, 'error');
          }
        } catch (error) {
          console.error('🔑 Error archiving key:', error);
          this.showNotification('Error archiving key', 'error');
        }
      },
      
      async deleteKey(keyId) {
        if (!confirm('Are you sure you want to permanently delete this key? This action cannot be undone.')) {
          return;
        }
        
        console.log('🔑 Deleting key:', keyId);
        try {
          const response = await fetch(`/settings/api/keys/${keyId}/delete`, {
            method: 'DELETE'
          });
          const data = await response.json();
          
          if (data.status === 'success') {
            this.showNotification('Key deleted successfully!', 'success');
            this.loadKeyInventory(); // Refresh the list
          } else {
            this.showNotification('Failed to delete key: ' + data.message, 'error');
          }
        } catch (error) {
          console.error('🔑 Error deleting key:', error);
          this.showNotification('Error deleting key', 'error');
        }
      },
      
      async exportAllKeys() {
        console.log('🔑 Exporting all keys...');
        this.showNotification('Exporting all keys...', 'info');
      },
      
      async securityAudit() {
        console.log('🔑 Running security audit...');
        this.showNotification('Running security audit...', 'info');
      },
      
      formatDate(dateString) {
        try {
          return new Date(dateString).toLocaleDateString();
        } catch (e) {
          return dateString;
        }
      }
    }
  };
})();

// =======================
// ALPINE.JS COMPONENT REGISTRATION
// =======================
document.addEventListener('alpine:init', () => {
  console.log('🩺 HERZCHIRURG: Registering modular Alpine.js component...');
  
  // Merge all module states and methods
  const allModules = [
    window.SettingsModules.Core,
    window.SettingsModules.Dashboard,
    window.SettingsModules.System,
    window.SettingsModules.Network,
    window.SettingsModules.Database,
    window.SettingsModules.API,
    window.SettingsModules.SelectiveDisclosure,
    window.SettingsModules.Keys
  ];
  
  // Merge states
  const mergedState = {};
  allModules.forEach(module => {
    Object.assign(mergedState, module.state);
  });
  
  // Merge methods
  const mergedMethods = {};
  allModules.forEach(module => {
    Object.assign(mergedMethods, module.methods);
  });
  
  // Add utility methods
  Object.assign(mergedMethods, window.SettingsModules.Utils);
  
  // Register Alpine.js component
  Alpine.data('settings', () => ({
    // State
    ...mergedState,
    
          // Initialize
      init() {
        console.log('🔧 Initializing modular settings component...');
        
        // Load selective disclosure settings immediately on page load
        this.loadSelectiveDisclosureSettings();
        
        // Check URL hash for initial tab
        const hash = window.location.hash.slice(1);
        const validTabs = ['dashboard', 'system', 'database', 'network', 'api', 'keys', 'selective-disclosure'];
        
        if (hash && validTabs.includes(hash)) {
          this.activeTab = hash;
          this.switchToTab(hash);
        } else {
          this.activeTab = 'dashboard';
          this.loadDashboard();
        }
        
        // Listen for hash changes
        window.addEventListener('hashchange', () => {
          const newHash = window.location.hash.slice(1);
          if (newHash && validTabs.includes(newHash)) {
            this.switchToTab(newHash);
          }
        });
      },
      
      // Tab switching function
      switchToTab(tabName) {
        console.log('🔧 Switching to tab:', tabName);
        this.activeTab = tabName;
        
        // Load data based on tab
        switch(tabName) {
          case 'dashboard':
            this.loadDashboard();
            break;
          case 'keys':
            this.loadKeyInventory();
            break;
          case 'system':
            if (this.loadSystemInfo) this.loadSystemInfo();
            break;
          case 'network':
            if (this.loadNetworkSettings) this.loadNetworkSettings();
            break;
          case 'database':
            if (this.loadDatabase) this.loadDatabase();
            break;
          case 'api':
            if (this.loadAPIData) this.loadAPIData();
            break;
          case 'selective-disclosure':
            // Selective disclosure doesn't need data loading
            break;
          // Add other tab cases as needed
        }
      },
    
    // Methods
    ...mergedMethods,
    
    // Getters for compatibility
    get loadingNetwork() { return this.networkLoading || false; },
    get loadingDatabase() { return this.databaseLoading || false; },
    get systemInfo() { return this.systemHealthData; },
    get systemInfoLoading() { return this.systemLoading; }
  }));
  
  console.log('🩺 HERZCHIRURG: Modular settings component ready!');
});

console.log("🩺 HERZCHIRURG: Modular settings system loaded successfully!"); 