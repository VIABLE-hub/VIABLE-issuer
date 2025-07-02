// 🩺 HERZCHIRURG: Settings Main Coordinator
// Imports and merges all settings modules into one Alpine.js component
// This maintains ALL functionality and references while providing clean modular architecture

import { SettingsCore } from './settings-core.js';
import { SettingsDashboard } from './settings-dashboard.js';
import { SettingsSystem } from './settings-system.js';
import { SettingsDatabase } from './settings-database.js';
import { SettingsNetwork } from './settings-network.js';
import { SettingsAPI } from './settings-api.js';
import { SettingsDisclosure } from './settings-disclosure.js';
import { SettingsKeys } from './settings-keys.js';

console.log("🩺 HERZCHIRURG: Settings component initializing...");

document.addEventListener('alpine:init', () => {
  console.log('🩺 HERZCHIRURG: Settings component initializing...');
  
  // Merge all module states
  const mergedState = {
    ...SettingsCore.state,
    ...SettingsDashboard.state,
    ...SettingsSystem.state,
    ...SettingsDatabase.state,
    ...SettingsNetwork.state,
    ...SettingsAPI.state,
    ...SettingsDisclosure.state,
    ...SettingsKeys.state
  };

  // Merge all module methods
  const mergedMethods = {
    ...SettingsCore.methods,
    ...SettingsDashboard.methods,
    ...SettingsSystem.methods,
    ...SettingsDatabase.methods,
    ...SettingsNetwork.methods,
    ...SettingsAPI.methods,
    ...SettingsDisclosure.methods,
    ...SettingsKeys.methods
  };

  // Create the complete Alpine.js component
  Alpine.data('settings', () => ({
    // ===== MERGED STATE =====
    ...mergedState,

    // ===== INITIALIZATION =====
    init() {
      console.log('🔧 Initializing settings component...');
      
      // Initialize state
      this.activeTab = 'dashboard';
      this.tabsLoaded = {};
      
      // Initialize dashboard state
      this.dashboardLoading = false;
      this.dashboardRefreshing = false;
      this.dashboardError = null;
      this.healthData = null;
      this.healthDataReady = false;
      this.systemData = null;
      this.systemDataReady = false;
      
      // Initialize system state
      this.systemLoading = false;
      this.systemHealthData = null;
      this.systemHealthRefreshing = false;
      this.systemHealthError = null;
      
      // Initialize database state
      this.databaseLoading = false;
      this.databaseData = {};
      this.backupListLoading = false;
      this.backupList = [];
      this.backupInProgress = false;
      this.selectedImportFile = null;
      this.databaseImporting = false;
      this.databaseImportProgress = 0;
      
      // Initialize network state
      this.networkLoading = false;
      this.networkData = {};
      this.networkConfigUpdating = false;
      this.testingConnection = false;
      this.connectionTestResults = null;
      this.ngrokDomain = '';
      this.useNgrok = false;
      this.useHttps = true;
      this.urlUpdating = false;
      this.issuerUrl = '';
      this.verifierUrl = '';
      
      // Initialize new connection mode variables
      this.connectionMode = 'local'; // 'local', 'public', 'ngrok'
      this.serverPort = 8080;
      
      // Initialize API state
      this.apiKeysLoading = false;
      this.apiKeys = [];
      this.apiKeyGenerating = false;
      this.keyRevoking = false;
      this.newKeyName = '';
      this.newApiKey = null;
      
      // Initialize selective disclosure state
      this.selectiveDisclosureLoading = false;
      this.selectiveDisclosureUpdating = false;
      this.selectiveDisclosureSaving = false;
      this.loadingFields = false;
      this.selectiveDisclosureEnabled = true;
      this.disclosureStrategy = 'required';
      this.zkProof = true;
      this.allowPartial = false;
      this.allFields = [];
      this.mandatoryFields = [];
      
      // Load dashboard data
      this.loadDashboard();
    },

    // ===== MERGED METHODS =====
    ...mergedMethods
  }));

  console.log('🩺 HERZCHIRURG: Settings component ready for Alpine.js initialization');
});

// Export for potential external use
export { 
  SettingsCore,
  SettingsDashboard, 
  SettingsSystem,
  SettingsDatabase,
  SettingsNetwork,
  SettingsAPI,
  SettingsDisclosure,
  SettingsKeys
}; 