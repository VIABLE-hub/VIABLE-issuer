// 🩺 HERZCHIRURG: Settings API Module
// Handles API key management, generation, and revocation

export const SettingsAPI = {
  // ===== API STATE =====
  state: {
    // API keys state
    apiKeys: [],
    apiKeysLoading: false,
    apiKeyGenerating: false,
    newKeyName: '',
    newApiKey: null,
    keyRevoking: false
  },

  // ===== API METHODS =====
  methods: {
    // API key functions
    loadApiKeys() {
      console.log('🔑 Loading API keys...');
      this.apiKeysLoading = true;
      
      fetch('/api/keys/list')
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          console.log('API keys loaded:', data);
          this.apiKeys = data.keys || [];
          this.apiKeysLoading = false;
        })
        .catch(error => {
          console.error('Error loading API keys:', error);
          this.showNotification(`Failed to load API keys: ${error.message}`, 'error');
          this.apiKeysLoading = false;
        });
    },

    generateNewApiKey() {
      if (!this.newKeyName.trim()) {
        this.showNotification('Please enter a name for the API key', 'error');
        return;
      }
      
      console.log('🔑 Generating new API key...');
      this.apiKeyGenerating = true;
      this.newApiKey = null;
      
      fetch('/api/keys/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: this.newKeyName.trim(),
          permissions: ['read', 'write'] // Default permissions
        })
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        if (data.status === 'success') {
          this.newApiKey = data.api_key;
          this.showNotification('API key generated successfully', 'success');
          this.loadApiKeys(); // Reload the list
          this.newKeyName = ''; // Clear the input
        } else {
          this.showNotification(`Failed to generate API key: ${data.message}`, 'error');
        }
      })
      .catch(error => {
        console.error('Error generating API key:', error);
        this.showNotification(`Failed to generate API key: ${error.message}`, 'error');
      })
      .finally(() => {
        this.apiKeyGenerating = false;
      });
    },

    revokeApiKey(keyId) {
      if (!confirm('Are you sure you want to revoke this API key? This action cannot be undone.')) {
        return;
      }
      
      console.log('🔑 Revoking API key:', keyId);
      this.keyRevoking = true;
      
      fetch(`/api/keys/${keyId}/revoke`, {
        method: 'POST'
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        if (data.status === 'success') {
          this.showNotification('API key revoked successfully', 'success');
          this.loadApiKeys(); // Reload the list
        } else {
          this.showNotification(`Failed to revoke API key: ${data.message}`, 'error');
        }
      })
      .catch(error => {
        console.error('Error revoking API key:', error);
        this.showNotification(`Failed to revoke API key: ${error.message}`, 'error');
      })
      .finally(() => {
        this.keyRevoking = false;
      });
    },

    copyToSwagger(apiKey) {
      const swaggerUrl = `${window.location.origin}/api/docs?api_key=${apiKey}`;
      this.copyToClipboard(swaggerUrl);
    }
  }
}; 