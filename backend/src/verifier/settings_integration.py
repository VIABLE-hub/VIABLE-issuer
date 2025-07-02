"""
Settings integration for the Verifier.

Provides functions to get and update selective disclosure settings from the database.
"""

from logging import getLogger
import json

logger = getLogger("LOGGER")

def get_current_selective_disclosure_settings():
    """
    Fetch current selective disclosure settings and return COMBINED mandatory fields
    Returns: List of ALL fields (technical + user selected) for the verifier
    """
    try:
        # Import inside function to avoid circular imports
        from src.models import TenantSettings
        from src.tenants import get_current_tenant_id
        from .constants import TECHNICAL_FIELDS
        
        # Start with mandatory technical fields (always required)
        mandatory_fields = TECHNICAL_FIELDS.copy()
        
        # Get current tenant ID using the proper tenant detection system
        tenant_id = get_current_tenant_id()
        if not tenant_id:
            logger.warning("No tenant ID detected, using technical fields only")
            return mandatory_fields
            
        # Get tenant settings for the detected tenant
        tenant_settings = TenantSettings.get_or_create_default(tenant_id)
        
        if (tenant_settings.disclosure_settings and 
            'selective_disclosure' in tenant_settings.disclosure_settings and
            'mandatory_fields' in tenant_settings.disclosure_settings['selective_disclosure']):
            
            stored_fields = tenant_settings.disclosure_settings['selective_disclosure']['mandatory_fields']
            logger.debug(f"Got user-selected fields from database: {stored_fields}")
            
            # Add user-selected fields to the mandatory technical fields
            from .constants import ALL_SELECTABLE_FIELDS
            
            for field in stored_fields:
                # Skip technical fields (already included)
                if field not in TECHNICAL_FIELDS:
                    # Only add the simple field name - no duplicates
                    if field in ALL_SELECTABLE_FIELDS:
                        mandatory_fields.append(field)  # Simple name like "lastName"
                        logger.debug(f"✅ Added user field: '{field}'")
                    elif field.startswith('vc.credentialSubject.'):
                        # Convert full path to simple name
                        simple_field = field.replace('vc.credentialSubject.', '')
                        if simple_field in ALL_SELECTABLE_FIELDS and simple_field not in mandatory_fields:
                            mandatory_fields.append(simple_field)  # Add simple name only
                            logger.debug(f"✅ Added user field: '{simple_field}' (converted from {field})")
            
            logger.debug(f"Combined mandatory fields (technical + user selected): {mandatory_fields}")
            return mandatory_fields
        
        logger.debug(f"No user-selected fields found, using technical fields only: {mandatory_fields}")
        return mandatory_fields
        
    except Exception as e:
        logger.error(f"Error getting selective disclosure settings: {e}")
        logger.error(f"This causes user fields to be missing from verification!")
        
        # Only use technical fields as fallback - respect user's choice for empty selection
        from .constants import TECHNICAL_FIELDS
        fallback_fields = TECHNICAL_FIELDS.copy()
        
        logger.warning(f"Database error, using technical fields only: {fallback_fields}")
        return fallback_fields


def update_selective_disclosure_settings(mandatory_fields):
    """
    Update selective disclosure settings in the database
    
    Args:
        mandatory_fields: List of mandatory fields to store
    """
    try:
        # Import inside function to avoid circular imports
        from src.models import TenantSettings
        from src.tenants import get_current_tenant_id
        from src import db
        
        # Filter to only include selectable user fields (no technical fields)
        from .constants import ALL_SELECTABLE_FIELDS, TECHNICAL_FIELDS
        filtered_fields = []
        
        for field in mandatory_fields:
            # Check if field is directly in selectable fields (simple name)
            if field in ALL_SELECTABLE_FIELDS:
                filtered_fields.append(field)
            # Check if field is a full path that maps to a selectable field
            elif field.startswith('vc.credentialSubject.'):
                simple_field = field.replace('vc.credentialSubject.', '')
                if simple_field in ALL_SELECTABLE_FIELDS:
                    filtered_fields.append(field)  # Keep the full path
            # Don't include technical fields
            elif field not in TECHNICAL_FIELDS:
                logger.warning(f"Unknown field '{field}' not in selectable fields, skipping")
        
        logger.info(f"Updating selective disclosure: input={mandatory_fields}, filtered={filtered_fields}")
        
        # Get current tenant ID using the proper tenant detection system
        tenant_id = get_current_tenant_id()
        if not tenant_id:
            logger.error("No tenant ID detected, cannot update settings")
            return False
            
        # Get tenant settings for the detected tenant
        tenant_settings = TenantSettings.get_or_create_default(tenant_id)
        
        # Initialize disclosure_settings if not exists
        if not tenant_settings.disclosure_settings:
            tenant_settings.disclosure_settings = {}
        
        if 'selective_disclosure' not in tenant_settings.disclosure_settings:
            tenant_settings.disclosure_settings['selective_disclosure'] = {}
        
        # Update the mandatory fields (only user-selectable fields)
        tenant_settings.disclosure_settings['selective_disclosure']['mandatory_fields'] = filtered_fields
        
        # Mark as modified for SQLAlchemy
        tenant_settings.disclosure_settings = tenant_settings.disclosure_settings.copy()
        
        # Save to database
        db.session.commit()
        
        logger.info(f"Updated selective disclosure settings with {len(filtered_fields)} mandatory user fields")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update selective disclosure settings: {e}")
        return False


def get_presentation_definition():
    """
    Get a structured presentation definition based on current settings
    
    Returns:
        dict: Structured presentation definition with categorized fields
    """
    try:
        from .constants import TECHNICAL_FIELDS, FIELD_MAPPINGS, FIELD_EXPLANATIONS, ALL_SELECTABLE_FIELDS
        
        # Get current mandatory fields from settings
        current_mandatory_fields = get_current_selective_disclosure_settings()
        
        # Separate technical fields from user fields
        technical_fields = []
        user_mandatory_fields = []
        
        for field in current_mandatory_fields:
            if field in TECHNICAL_FIELDS:
                technical_fields.append(field)
            elif field.startswith('vc.credentialSubject.'):
                # This is a user field stored as full path
                user_mandatory_fields.append(field)
            elif field in ALL_SELECTABLE_FIELDS:
                # This is a user field stored as simple name
                user_mandatory_fields.append(field)
            else:
                # Unknown field, skip it
                logger.warning(f"Unknown field '{field}' in mandatory fields, skipping")
        
        # Ensure all technical fields are included
        for tech_field in TECHNICAL_FIELDS:
            if tech_field not in technical_fields:
                technical_fields.append(tech_field)
        
        # Create structured presentation definition
        presentation_def = {
            "technical_fields": technical_fields,
            "user_mandatory_fields": user_mandatory_fields,
            "optional_fields": [],  # Could be populated from a separate setting
            "field_mappings": FIELD_MAPPINGS,
            "field_explanations": FIELD_EXPLANATIONS,
            "mandatory_fields": current_mandatory_fields  # For backward compatibility
        }
        
        logger.debug(f"Generated presentation definition with {len(technical_fields)} technical and {len(user_mandatory_fields)} user fields")
        return presentation_def
        
    except Exception as e:
        logger.error(f"Error generating presentation definition: {e}")
        # Fallback to minimal technical fields only
        from .constants import TECHNICAL_FIELDS, FIELD_MAPPINGS
        return {
            "technical_fields": TECHNICAL_FIELDS,
            "user_mandatory_fields": [],
            "optional_fields": [],
            "field_mappings": FIELD_MAPPINGS,
            "field_explanations": {},
            "mandatory_fields": TECHNICAL_FIELDS
        }


def translate_field_name(field_name):
    """
    Translate simple field names to their actual credential structure paths
    
    Args:
        field_name: The field name to translate
        
    Returns:
        str: The translated field name (credential path)
    """
    credential_field_mappings = {
        # Personal data fields
        "firstName": "vc.credentialSubject.firstName",
        "lastName": "vc.credentialSubject.lastName", 
        "email": "vc.credentialSubject.email",
        "dateOfBirth": "vc.credentialSubject.dateOfBirth",
        
        # Student data fields  
        "studentId": "vc.credentialSubject.studentId",
        "studentIdPrefix": "vc.credentialSubject.studentIdPrefix",
        "studyProgram": "vc.credentialSubject.studyProgram",
        "faculty": "vc.credentialSubject.faculty",
        "enrollmentDate": "vc.credentialSubject.enrollmentDate",
        "expectedGraduation": "vc.credentialSubject.expectedGraduation",
        "studentStatus": "vc.credentialSubject.studentStatus",
        "academicLevel": "vc.credentialSubject.academicLevel",
        
        # Visual/theme fields
        "profileImage": "vc.credentialSubject.image",
        "image": "vc.credentialSubject.image", 
        "themeName": "vc.credentialSubject.theme.name",
        "themeIcon": "vc.credentialSubject.theme.icon",
        "bgColorCard": "vc.credentialSubject.theme.bgColorCard",
        "fgColorTitle": "vc.credentialSubject.theme.fgColorTitle",
        "accentColor": "vc.credentialSubject.theme.accentColor",
        "textColor": "vc.credentialSubject.theme.textColor",
        
        # Credential metadata fields
        "issuanceDate": "vc.issuanceDate",
        "expiryDate": "vc.expirationDate",
        "validFrom": "vc.validFrom",
        "issuer": "vc.issuer",
        "credentialSchema": "vc.credentialSchema.id",
        "issuanceCount": "vc.credentialSubject.issuanceCount"
    }
    return credential_field_mappings.get(field_name, field_name)