// 🩺 HERZCHIRURG: Settings Dashboard Module
// Handles dashboard functionality and health monitoring

export const SettingsDashboard = {
  // ===== DASHBOARD STATE =====
  state: {
    // Dashboard state
    dashboardLoading: true,
    dashboardRefreshing: false,
    dashboardError: null,
    systemDataReady: false,
    healthDataReady: false,
    systemData: null,
    healthData: {
      issuer: { status: 'unknown', endpoint: '-', response_time: null },
      verifier: { status: 'unknown', endpoint: '-', response_time: null },
      database: { status: 'unknown', type: 'SQLite', size: '-' },
      websocket: { status: 'unknown', active_connections: 0, port: '-' },
      sse: { status: 'unknown', active_connections: 0, port: '-' }
    },

    // Initialize systemData with default values
    systemData: {
      cpu: { 
        usage: 0, 
        cores: 1, 
        logical_cores: 1, 
        temperature: null, 
        status: 'unknown' 
      },
      memory: { 
        percentage: 0, 
        used_gb: 0, 
        total_gb: 0, 
        status: 'unknown' 
      },
      disk: { 
        percentage: 0, 
        used_gb: 0, 
        total_gb: 0, 
        status: 'unknown' 
      },
      network: { 
        local_ip: 'Unknown', 
        public_ip: 'Unknown', 
        hostname: 'Unknown', 
        status: 'unknown' 
      },
      uptime: { 
        seconds: 0, 
        formatted: 'Unknown', 
        status: 'unknown' 
      },
      app_version: 'Unknown',
      python_version: 'Unknown',
      platform: 'Unknown'
    }
  },

  // ===== DASHBOARD METHODS =====
  methods: {
    // Compatibility getters for existing templates
    get loadingNetwork() { return this.networkLoading; },
    get loadingDatabase() { return this.databaseLoading; },
    get systemInfo() { return this.systemHealthData; },
    get systemInfoLoading() { return this.systemLoading; },
    get selectiveDisclosureFields() { return this.allFields; },

    // Dashboard functions
    loadDashboard() {
      console.log('🩺 Loading dashboard data...');
      this.dashboardLoading = true;
      this.dashboardError = null;
      
      // Load health data
      fetch('/api/health')
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json();
        })
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
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          console.log('🖥️ System data loaded:', data);
          if (data.success && data.data) {
            this.systemData = {
              ...this.systemData,
              ...data.data
            };
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