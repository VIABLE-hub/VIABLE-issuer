// 🩺 HERZCHIRURG: Settings Database Module
// Handles database operations, backups, exports, and imports

export const SettingsDatabase = {
  // ===== DATABASE STATE =====
  state: {
    // Database state
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

  // ===== DATABASE METHODS =====
  methods: {
    // Database functions
    loadDatabase() {
      console.log('🗄️ Loading database...');
      this.loadDatabaseData();
      this.loadBackupList();
    },

    loadDatabaseData() {
      console.log('🗄️ Loading database data...');
      this.databaseLoading = true;
      
      fetch('/api/database/status')
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json();
        })
        .then(response => {
          console.log('Database response:', response);
          
          if (response.status === 'success' && response.database) {
            // Process the database data
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
            
            console.log('Database data processed:', this.databaseData);
            
            this.databaseLoading = false;
          } else {
            if (response.status !== 'success') {
              throw new Error(response.message || 'Failed to load database data');
            }
            
            // Fallback for unexpected structure
            this.databaseData = {
              engine: 'SQLite',
              version: '3.x',
              status: 'Connected',
              location: '',
              size_bytes: 0,
              size_formatted: '0 Bytes',
              table_count: 0,
              record_count: 0,
              last_backup: null
            };
            this.databaseLoading = false;
          }
          
          console.log('🗄️ Database data loading completed, setting databaseLoading = false');
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
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json();
        })
        .then(response => {
          console.log('Backup list response:', response);
          
          if (response.status === 'success' && response.backups) {
            this.backupList = response.backups.map(backup => ({
              ...backup,
              id: backup.filename || backup.id || Math.random().toString(36).substring(2, 15)
            }));
          } else {
            this.backupList = [];
            if (response.status !== 'success') {
              throw new Error(response.message || 'Failed to load backups');
            }
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
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          description: 'Manual backup from settings'
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
          this.showNotification('Backup created successfully', 'success');
          this.loadBackupList(); // Reload backup list
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

    downloadBackup(backup) {
      console.log('🗄️ Downloading backup:', backup.filename);
      
      const url = `/api/database/backup/download/${backup.filename}`;
      const link = document.createElement('a');
      link.href = url;
      link.download = backup.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      this.showNotification('Backup download started', 'success');
    },

    restoreBackup(backup) {
      if (!confirm(`Are you sure you want to restore from backup "${backup.filename}"? This will overwrite the current database.`)) {
        return;
      }
      
      console.log('🗄️ Restoring backup:', backup.filename);
      
      fetch(`/api/database/backup/restore/${backup.filename}`, {
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
          this.showNotification('Database restored successfully', 'success');
          this.loadDatabaseData(); // Reload database data
        } else {
          this.showNotification(`Failed to restore backup: ${data.message}`, 'error');
        }
      })
      .catch(error => {
        console.error('Error restoring backup:', error);
        this.showNotification(`Failed to restore backup: ${error.message}`, 'error');
      });
    },

    deleteBackup(backup) {
      if (!confirm(`Are you sure you want to delete backup "${backup.filename}"? This action cannot be undone.`)) {
        return;
      }
      
      console.log('🗄️ Deleting backup:', backup.filename);
      
      fetch(`/api/database/backup/delete/${backup.filename}`, {
        method: 'DELETE'
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        if (data.status === 'success') {
          this.showNotification('Backup deleted successfully', 'success');
          this.loadBackupList(); // Reload backup list
        } else {
          this.showNotification(`Failed to delete backup: ${data.message}`, 'error');
        }
      })
      .catch(error => {
        console.error('Error deleting backup:', error);
        this.showNotification(`Failed to delete backup: ${error.message}`, 'error');
      });
    },

    exportDatabaseSQL() {
      console.log('🗄️ Exporting database as SQL...');
      
      const url = '/api/database/export/sql';
      const link = document.createElement('a');
      link.href = url;
      link.download = `database_export_${new Date().toISOString().split('T')[0]}.sql`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      this.showNotification('SQL export started', 'success');
    },

    handleDatabaseFileSelect(event) {
      const file = event.target.files[0];
      if (file) {
        this.selectedImportFile = {
          name: file.name,
          size: file.size,
          type: file.type,
          file: file
        };
        console.log('Selected file for import:', this.selectedImportFile);
      }
    },

    clearImportFile() {
      this.selectedImportFile = null;
      // Clear the file input
      const fileInput = document.querySelector('input[type="file"]');
      if (fileInput) {
        fileInput.value = '';
      }
    },

    importDatabaseSQL() {
      if (!this.selectedImportFile) {
        this.showNotification('Please select a file to import', 'error');
        return;
      }
      
      if (!confirm('Are you sure you want to import this SQL file? This will overwrite the current database.')) {
        return;
      }
      
      console.log('🗄️ Importing SQL file...');
      this.databaseImporting = true;
      this.databaseImportProgress = 0;
      
      const formData = new FormData();
      formData.append('sql_file', this.selectedImportFile.file);
      
      fetch('/api/database/import/sql', {
        method: 'POST',
        body: formData
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        if (data.status === 'success') {
          this.showNotification('SQL import completed successfully', 'success');
          this.loadDatabaseData(); // Reload database data
          this.clearImportFile();
        } else {
          this.showNotification(`Failed to import SQL: ${data.message}`, 'error');
        }
      })
      .catch(error => {
        console.error('Error importing SQL:', error);
        this.showNotification(`Failed to import SQL: ${error.message}`, 'error');
      })
      .finally(() => {
        this.databaseImporting = false;
        this.databaseImportProgress = 0;
      });
    }
  }
}; 