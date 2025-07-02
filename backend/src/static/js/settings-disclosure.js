// 🩺 HERZCHIRURG: Settings Selective Disclosure Module
// Handles BBS+ selective disclosure field management

export const SettingsDisclosure = {
  // ===== DISCLOSURE STATE =====
  state: {
    // Selective disclosure state
    selectiveDisclosureLoading: false,
    selectiveDisclosureUpdating: false,
    selectiveDisclosureSaving: false,
    loadingFields: false,
    selectiveDisclosureEnabled: true,
    disclosureStrategy: 'required',
    zkProof: true,
    allowPartial: false,
    allFields: [],
    mandatoryFields: []
  },

  // ===== DISCLOSURE METHODS =====
  methods: {
    // Selective disclosure functions
    loadSelectiveDisclosureFields() {
      console.log('🔒 Loading selective disclosure fields...');
      this.selectiveDisclosureLoading = true;
      
      fetch('/settings/selective-disclosure')
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          console.log('🔒 Selective disclosure data loaded:', data);
          
          if (data && data.mandatory_fields) {
            this.mandatoryFields = data.mandatory_fields || [];
            
            // Define all available fields
            this.allFields = [
              'firstName',
              'lastName', 
              'studentId',
              'studentIdPrefix',
              'dateOfBirth',
              'email',
              'studyProgram',
              'faculty',
              'enrollmentDate',
              'expectedGraduation',
              'studentStatus',
              'academicLevel',
              'nationality',
              'address'
            ];
            
            this.selectiveDisclosureLoading = false;
          } else {
            console.error('🔒 Invalid selective disclosure data format:', data);
            this.selectiveDisclosureLoading = false;
          }
        })
        .catch(error => {
          console.error('🔒 Error loading selective disclosure fields:', error);
          this.showNotification(`Failed to load selective disclosure settings: ${error.message}`, 'error');
          this.selectiveDisclosureLoading = false;
        });
    },

    saveSelectiveDisclosureSettings() {
      console.log('🔒 Saving selective disclosure settings...');
      this.selectiveDisclosureSaving = true;
      
      const settings = {
        mandatory_fields: this.mandatoryFields
      };
      
      fetch('/settings/selective-disclosure', {
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
        if (data.success) {
          this.showNotification('Selective disclosure settings saved successfully', 'success');
        } else {
          this.showNotification(`Failed to save settings: ${data.message}`, 'error');
        }
      })
      .catch(error => {
        console.error('🔒 Error saving selective disclosure settings:', error);
        this.showNotification(`Failed to save settings: ${error.message}`, 'error');
      })
      .finally(() => {
        this.selectiveDisclosureSaving = false;
      });
    },

    selectAllFields() {
      this.mandatoryFields = [...this.allFields];
    },

    deselectAllOptionalFields() {
      // Keep only technical fields that are always required
      this.mandatoryFields = [];
    },

    getSelectedFields() {
      return this.mandatoryFields;
    },

    getSelectedFieldsCount() {
      return this.mandatoryFields.length;
    }
  }
}; 