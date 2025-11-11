"""
Selective disclosure validator for StudentVC verifier component.
Validates that credentials have the required fields disclosed based on tenant settings.
"""
from logging import getLogger
from typing import Dict, List, Any, Tuple, Set, Optional

logger = getLogger("LOGGER")

# Field disclosure categories
class DisclosureCategory:
    MANDATORY = "mandatory"
    OPTIONAL = "optional"
    HIDDEN = "hidden"
    TECHNICAL = "technical"  # Special fields required for verification

class DisclosureStatus:
    VALID = "valid"
    MISSING_MANDATORY = "missing_mandatory"
    MISSING_OPTIONAL = "missing_optional"
    UNNECESSARY_DISCLOSURE = "unnecessary_disclosure"

class SelectiveDisclosureValidator:
    """
    Validates selective disclosure compliance based on disclosure settings
    """
    
    def __init__(self, technical_fields: List[str]):
        """
        Initialize the validator
        
        Args:
            technical_fields: List of technical fields always required for verification
        """
        self.technical_fields = set(technical_fields)
        logger.info(f"🔒 SelectiveDisclosureValidator initialized with {len(technical_fields)} technical fields")
        
        # Define field mappings for iOS wallet compatibility
        self.field_mappings = {
            'totalMessages': ['totalMessages', 'total_messages'],
            'bbsDPK': ['bbsDPK', 'bbs_dpk'],
            'signedNonce': ['signedNonce', 'signed_nonce'],
            'validityIdentifier': ['validityIdentifier', 'validity_identifier'],
            'vc.credentialSubject.firstName': ['firstName', 'first_name'],
            'vc.credentialSubject.lastName': ['lastName', 'last_name'],
            'vc.credentialSubject.studentId': ['studentId', 'student_id'],
            'vc.credentialSubject.studentIdPrefix': ['studentIdPrefix', 'student_id_prefix'],
            'vc.credentialSubject.email': ['email'],
            'vc.credentialSubject.dateOfBirth': ['dateOfBirth', 'date_of_birth'],
            'vc.credentialSubject.studyProgram': ['studyProgram', 'study_program']
        }
        
    def get_disclosure_settings(self, tenant_settings) -> Dict[str, str]:
        """
        Extract disclosure settings from tenant settings
        
        Args:
            tenant_settings: TenantSettings object
            
        Returns:
            Dictionary mapping field names to disclosure categories
        """
        try:
            if (tenant_settings and 
                tenant_settings.disclosure_settings and 
                'selective_disclosure' in tenant_settings.disclosure_settings):
                
                sd_settings = tenant_settings.disclosure_settings['selective_disclosure']
                
                # Get mandatory fields
                mandatory_fields = set(sd_settings.get('mandatory_fields', []))
                
                # Get optional fields 
                optional_fields = set(sd_settings.get('optional_fields', []))
                
                # Get hidden fields
                hidden_fields = set(sd_settings.get('hidden_fields', []))
                
                # Build complete field mapping
                disclosure_settings = {}
                
                # Technical fields are always required
                for field in self.technical_fields:
                    disclosure_settings[field] = DisclosureCategory.TECHNICAL
                
                # Add mandatory fields
                for field in mandatory_fields:
                    if field not in self.technical_fields:
                        disclosure_settings[field] = DisclosureCategory.MANDATORY
                
                # Add optional fields
                for field in optional_fields:
                    if field not in self.technical_fields and field not in mandatory_fields:
                        disclosure_settings[field] = DisclosureCategory.OPTIONAL
                        
                # Add hidden fields
                for field in hidden_fields:
                    if field not in self.technical_fields and field not in mandatory_fields:
                        disclosure_settings[field] = DisclosureCategory.HIDDEN
                
                logger.info(f"🔒 Disclosure settings loaded: {len(disclosure_settings)} fields configured")
                logger.debug(f"🔒 Technical: {len(self.technical_fields)}, Mandatory: {len(mandatory_fields)}, "
                           f"Optional: {len(optional_fields)}, Hidden: {len(hidden_fields)}")
                return disclosure_settings
                
            else:
                logger.warning("🔒 No selective disclosure settings found in tenant settings")
                return {field: DisclosureCategory.TECHNICAL for field in self.technical_fields}
                
        except Exception as e:
            logger.error(f"🔒 Error getting disclosure settings: {e}")
            return {field: DisclosureCategory.TECHNICAL for field in self.technical_fields}

    def validate_disclosure(self, 
                           disclosed_fields: Set[str], 
                           disclosure_settings: Dict[str, str],
                           credential_subject: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        Validate if the disclosure complies with the settings
        
        Args:
            disclosed_fields: Set of disclosed field names
            disclosure_settings: Dictionary mapping field names to disclosure categories
            credential_subject: The credential subject data
            
        Returns:
            Tuple of:
            - Boolean indicating if the disclosure is valid
            - Dictionary with disclosure validation results per field
            - List of error messages
        """
        # Track validation results for each field
        validation_results = {}
        
        # Track errors
        errors = []
        
        # Check all required fields are present
        missing_mandatory = []
        missing_optional = []
        
        # Create an expanded set of disclosed fields with alternative names
        expanded_disclosed = set(disclosed_fields)
        for field in disclosed_fields:
            # Add potential alternative names to the expanded set
            for canonical, alternatives in self.field_mappings.items():
                if field in alternatives:
                    expanded_disclosed.add(canonical)
                    break
        
        logger.info(f"🔒 Original disclosed fields: {disclosed_fields}")
        logger.info(f"🔒 Expanded disclosed fields: {expanded_disclosed}")
        
        for field, category in disclosure_settings.items():
            # Check if the field or any of its alternative names are disclosed
            is_disclosed = field in expanded_disclosed
            
            # For non-technical fields with dot notation, check if the base field is disclosed
            if not is_disclosed and '.' in field and category != DisclosureCategory.TECHNICAL:
                base_field = field.split('.')[-1]  # Get the last part after the dot
                alternatives = self.field_mappings.get(field, [])
                
                # Check if any alternative is disclosed
                for alt in alternatives:
                    if alt in disclosed_fields:
                        is_disclosed = True
                        logger.info(f"🔒 Field '{field}' matched via alternative '{alt}'")
                        break
                
                # Also check if the base field is disclosed
                if base_field in disclosed_fields:
                    is_disclosed = True
                    logger.info(f"🔒 Field '{field}' matched via base field '{base_field}'")
            
            # Field is disclosed
            if is_disclosed:
                if category in [DisclosureCategory.MANDATORY, DisclosureCategory.TECHNICAL, DisclosureCategory.OPTIONAL]:
                    validation_results[field] = {
                        'status': DisclosureStatus.VALID,
                        'category': category,
                        'value': self._get_field_value(field, credential_subject)
                    }
                elif category == DisclosureCategory.HIDDEN:
                    validation_results[field] = {
                        'status': DisclosureStatus.UNNECESSARY_DISCLOSURE,
                        'category': category,
                        'value': self._get_field_value(field, credential_subject)
                    }
                    logger.warning(f"🔒 Hidden field '{field}' was unnecessarily disclosed")
            # Field is not disclosed
            else:
                if category == DisclosureCategory.MANDATORY:
                    missing_mandatory.append(field)
                    validation_results[field] = {
                        'status': DisclosureStatus.MISSING_MANDATORY,
                        'category': category,
                        'value': None
                    }
                elif category == DisclosureCategory.TECHNICAL:
                    missing_mandatory.append(field) 
                    validation_results[field] = {
                        'status': DisclosureStatus.MISSING_MANDATORY,
                        'category': category,
                        'value': None
                    }
                elif category == DisclosureCategory.OPTIONAL:
                    missing_optional.append(field)
                    validation_results[field] = {
                        'status': DisclosureStatus.MISSING_OPTIONAL,
                        'category': category,
                        'value': None
                    }
                elif category == DisclosureCategory.HIDDEN:
                    validation_results[field] = {
                        'status': DisclosureStatus.VALID,
                        'category': category,
                        'value': None
                    }
        
        # Check for any undeclared fields that were disclosed
        undeclared_fields = disclosed_fields - set(disclosure_settings.keys())
        for field in undeclared_fields:
            # Skip fields that are alternative names for known fields
            is_alternative = False
            for canonical, alternatives in self.field_mappings.items():
                if field in alternatives and canonical in disclosure_settings:
                    is_alternative = True
                    break
                    
            if not is_alternative:
                validation_results[field] = {
                    'status': DisclosureStatus.VALID,  # We accept additional fields
                    'category': 'undeclared',
                    'value': self._get_field_value(field, credential_subject)
                }
                logger.info(f"🔒 Undeclared field '{field}' was disclosed")
        
        # Generate error messages
        if missing_mandatory:
            errors.append(f"Missing mandatory fields: {', '.join(missing_mandatory)}")
            
        if missing_optional:
            logger.info(f"🔒 Optional fields not disclosed: {', '.join(missing_optional)}")
        
        # Validation is successful if no mandatory fields are missing
        is_valid = len(missing_mandatory) == 0
        
        return is_valid, validation_results, errors
    
    def _get_field_value(self, field: str, credential_subject: Dict[str, Any]) -> Any:
        """
        Extract field value from credential subject using dot notation support
        
        Args:
            field: Field name with potential dot notation
            credential_subject: The credential subject data
            
        Returns:
            The field value or None if not found
        """
        try:
            # Direct field access
            if field in credential_subject:
                return credential_subject[field]
                
            # Check alternative field names
            alternatives = self.field_mappings.get(field, [])
            for alt in alternatives:
                if alt in credential_subject:
                    return credential_subject[alt]
            
            # Handle dot notation (e.g., "vc.credentialSubject.firstName")
            if '.' in field:
                # Try full path
                parts = field.split('.')
                current = credential_subject
                
                for part in parts:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        # Path not found, try just the last part
                        last_part = parts[-1]
                        if last_part in credential_subject:
                            return credential_subject[last_part]
                            
                        # Try alternatives for the last part
                        base_alternatives = self.field_mappings.get(field, [])
                        for alt in base_alternatives:
                            if alt in credential_subject:
                                return credential_subject[alt]
                                
                        return None
                        
                return current
                    
            return None
        except Exception as e:
            logger.error(f"Error getting field value for {field}: {e}")
            return None

    def categorize_fields(self, all_fields: List[str], 
                        disclosure_settings: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Categorize fields based on disclosure settings
        
        Args:
            all_fields: List of all field names
            disclosure_settings: Dictionary mapping field names to disclosure categories
            
        Returns:
            Dictionary with field lists by category
        """
        categorized = {
            DisclosureCategory.TECHNICAL: [],
            DisclosureCategory.MANDATORY: [],
            DisclosureCategory.OPTIONAL: [],
            DisclosureCategory.HIDDEN: [],
            'undeclared': []
        }
        
        for field in all_fields:
            category = disclosure_settings.get(field)
            if category:
                categorized[category].append(field)
            else:
                categorized['undeclared'].append(field)
                
        return categorized

    def prepare_disclosure_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare a summary of disclosure validation for frontend display
        
        Args:
            results: Dictionary with validation results per field
            
        Returns:
            Summary object structured for frontend display
        """
        summary = {
            'mandatory': {
                'disclosed': [],
                'missing': [],
                'values': {}
            },
            'optional': {
                'disclosed': [],
                'missing': [],
                'values': {}
            },
            'technical': {
                'disclosed': [],
                'missing': [],
                'values': {}
            },
            'undeclared': {
                'disclosed': [],
                'values': {}
            }
        }
        
        # Process each field result
        for field, result in results.items():
            category = result.get('category', 'undeclared')
            status = result.get('status')
            value = result.get('value')
            
            # Skip hidden fields in summary
            if category == DisclosureCategory.HIDDEN:
                continue
                
            # Map to summary structure
            if category == DisclosureCategory.MANDATORY:
                if status == DisclosureStatus.VALID:
                    summary['mandatory']['disclosed'].append(field)
                    summary['mandatory']['values'][field] = value
                elif status == DisclosureStatus.MISSING_MANDATORY:
                    summary['mandatory']['missing'].append(field)
            elif category == DisclosureCategory.OPTIONAL:
                if status == DisclosureStatus.VALID:
                    summary['optional']['disclosed'].append(field)
                    summary['optional']['values'][field] = value
                elif status == DisclosureStatus.MISSING_OPTIONAL:
                    summary['optional']['missing'].append(field)
            elif category == DisclosureCategory.TECHNICAL:
                if status == DisclosureStatus.VALID:
                    summary['technical']['disclosed'].append(field)
                    summary['technical']['values'][field] = value
                else:
                    summary['technical']['missing'].append(field)
            elif category == 'undeclared':
                summary['undeclared']['disclosed'].append(field)
                summary['undeclared']['values'][field] = value
                
        return summary