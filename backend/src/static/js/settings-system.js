// 🩺 HERZCHIRURG: Settings System Module
// Handles system health monitoring and performance metrics

export const SettingsSystem = {
  // ===== SYSTEM STATE =====
  state: {
    // System state
    systemLoading: false,
    systemHealthData: null,
    systemHealthRefreshing: false,
    systemHealthError: null
  },

  // ===== SYSTEM METHODS =====
  methods: {
    // System functions
    loadSystemInfo() {
      console.log('🩺 Loading system health data...');
      this.systemLoading = true;
      this.systemHealthError = null;
      
      fetch('/api/system/health')
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          console.log('🩺 System health data received:', data);
          
          if (data.success && data.data) {
            this.systemHealthData = data.data;
            console.log('🩺 System health data updated:', this.systemHealthData);
          } else {
            throw new Error('Invalid system health data format');
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