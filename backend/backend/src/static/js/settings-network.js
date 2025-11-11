// 🩺 HERZCHIRURG: Settings Network Module
// Handles network configuration, NGROK settings, and connection testing

export const SettingsNetwork = {
  // ===== NETWORK STATE =====
  state: {
    // Network state
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
    
    // Network configuration variables
    connectionMode: 'local', // 'local', 'public', 'ngrok'
    serverPort: 8080,
    ngrokDomain: '',
    useNgrok: false,
    useHttps: true,
    urlUpdating: false,
    issuerUrl: '',
    verifierUrl: ''
  },

  // ===== NETWORK METHODS =====
  methods: {
    // Network data and settings
    get isValidNgrokUrl() {
      if (!this.ngrokSettings.ngrokDomain) return false;
      
      try {
        const url = new URL(this.ngrokSettings.ngrokDomain);
        const isHttps = url.protocol === 'https:';
        const isNgrokDomain = url.hostname.endsWith('.ngrok.io') || 
                              url.hostname.endsWith('.ngrok-free.app') || 
                              url.hostname.endsWith('.ngrok.app');
        return isHttps && isNgrokDomain;
      } catch (e) {
        // If URL parsing fails, check if it's because the protocol is missing
        if (!this.ngrokSettings.ngrokDomain.startsWith('http')) {
          // Try again with https:// prefix
          try {
            const urlWithProtocol = new URL('https://' + this.ngrokSettings.ngrokDomain);
            const isNgrokDomain = urlWithProtocol.hostname.endsWith('.ngrok.io') || 
                                  urlWithProtocol.hostname.endsWith('.ngrok-free.app') || 
                                  urlWithProtocol.hostname.endsWith('.ngrok.app');
            // If valid, suggest adding https:// prefix
            if (isNgrokDomain) {
              console.log('Valid ngrok domain but missing https:// prefix');
              // Don't auto-update the input field to avoid confusion
              return false;
            }
          } catch (e2) {
            // Still invalid even with protocol
          }
        }
        return false;
      }
    },

    // URL generation functions
    getIssuerUrl() {
      // Check if network data is loaded
      if (!this.networkData) {
        return 'Loading...';
      }
      
      // Get base URL components
      const useHttps = this.networkData.network_config?.use_https !== false;
      const protocol = useHttps ? 'https://' : 'http://';
      
      // If ngrok is enabled and we have a domain, use that
      if (this.ngrokSettings.useNgrok && this.ngrokSettings.ngrokDomain) {
        return `${this.ngrokSettings.ngrokDomain}/issuer`;
      }
      
      // Otherwise use the local IP and port
      const ip = this.networkData.local_ip || 'localhost';
      const port = this.networkData.default_port || '8080';
      return `${protocol}${ip}:${port}/issuer`;
    },

    getVerifierUrl() {
      // Check if network data is loaded
      if (!this.networkData) {
        return 'Loading...';
      }
      
      // Get base URL components
      const useHttps = this.networkData.network_config?.use_https !== false;
      const protocol = useHttps ? 'https://' : 'http://';
      
      // If ngrok is enabled and we have a domain, use that
      if (this.ngrokSettings.useNgrok && this.ngrokSettings.ngrokDomain) {
        return `${this.ngrokSettings.ngrokDomain}/verifier`;
      }
      
      // Otherwise use the local IP and port
      const ip = this.networkData.local_ip || 'localhost';
      const port = this.networkData.default_port || '8080';
      return `${protocol}${ip}:${port}/verifier`;
    },

    loadSimplifiedNetworkData() {
      console.log('🌐 Loading simplified network data...');
      this.networkLoading = true;
      
      fetch('/api/system/network/debug')
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          console.log('🌐 Simplified network data loaded:', data);
          
          if (data && data.status === 'success' && data.network_info) {
            // Update network data with simplified structure
            this.networkData = {
              ...this.networkData,
              local_ip: data.network_info.local_ip || 'Unknown',
              public_ip: data.network_info.public_ip || 'Not available',
              hostname: data.network_info.hostname || 'Unknown',
              default_port: data.network_info.default_port || '8080'
            };
            
            console.log('🌐 Network data updated with simplified endpoint:', this.networkData);
          } else {
            console.error('🌐 Invalid simplified network data format:', data);
          }
          
          this.networkLoading = false;
        })
        .catch(error => {
          console.error('🌐 Error loading simplified network data:', error);
          this.networkLoading = false;
        });
    },

    testConnection() {
      console.log('🌐 Testing connection...');
      this.testingConnection = true;
      this.connectionTestResults = null;
      
      fetch('/settings/api/test-connection', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          test_type: 'full'
        })
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        this.connectionTestResults = data;
        if (data.status === 'success') {
          this.showNotification('Connection test completed', 'success');
        } else {
          this.showNotification('Connection test failed', 'error');
        }
      })
      .catch(error => {
        console.error('Error testing connection:', error);
        this.connectionTestResults = {
          status: 'error',
          message: error.message
        };
        this.showNotification(`Connection test failed: ${error.message}`, 'error');
      })
      .finally(() => {
        this.testingConnection = false;
      });
    },

    saveNgrokSettings() {
      console.log('🌐 Saving NGROK settings...');
      this.networkConfigUpdating = true;
      
      const settings = {
        use_ngrok: this.ngrokSettings.useNgrok,
        ngrok_domain: this.ngrokSettings.ngrokDomain
      };
      
      fetch('/settings/api/network', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        if (data.status === 'success') {
          this.showNotification('NGROK settings saved successfully', 'success');
        } else {
          this.showNotification(`Failed to save settings: ${data.message}`, 'error');
        }
      })
      .catch(error => {
        console.error('Error saving NGROK settings:', error);
        this.showNotification(`Failed to save settings: ${error.message}`, 'error');
      })
      .finally(() => {
        this.networkConfigUpdating = false;
      });
    }
  }
}; 