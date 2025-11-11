"""
Base Tenant Configuration

Defines the interface and common functionality for all tenant configurations.
Each university tenant inherits from this base class.
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class BaseTenantConfig(ABC):
    """
    Abstract base class for tenant configurations.
    
    Each university tenant (TU Berlin, FU Berlin, etc.) implements this interface
    to provide tenant-specific configurations, database settings, and customizations.
    """
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.base_path = Path(__file__).parent / "instances" / tenant_id
        
    # === CORE TENANT PROPERTIES === #
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Full university name (e.g., 'Technische Universität Berlin')"""
        pass
    
    @property
    @abstractmethod
    def short_name(self) -> str:
        """Short university name (e.g., 'TU Berlin')"""
        pass
    
    @property
    @abstractmethod
    def domain_patterns(self) -> list:
        """Domain patterns for auto-detection (e.g., ['tu-berlin', 'tub'])"""
        pass
    
    # === VISUAL BRANDING === #
    
    @property
    @abstractmethod
    def primary_color(self) -> str:
        """Primary university color (hex, e.g., '#c50e1f')"""
        pass
    
    @property
    @abstractmethod
    def logo_filename(self) -> str:
        """University logo filename (e.g., 'tub_logo.png')"""
        pass
    
    @property
    def accent_color(self) -> str:
        """Accent color (defaults to primary if not overridden)"""
        return self.primary_color
    
    @property
    def text_color(self) -> str:
        """Text color (defaults to dark gray)"""
        return "#333333"
    
    # === DATABASE CONFIGURATION === #
    
    @property
    def database_path(self) -> str:
        """Tenant-specific database path"""
        return str(self.base_path / "database.db")
    
    @property
    def backup_path(self) -> str:
        """Tenant-specific backup directory"""
        backup_dir = self.base_path / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        return str(backup_dir)
    
    # === CRYPTOGRAPHIC KEYS === #
    
    @property
    def keys_path(self) -> str:
        """Tenant-specific keys directory"""
        keys_dir = self.base_path / "keys"
        keys_dir.mkdir(parents=True, exist_ok=True)
        return str(keys_dir)
    
    @property
    def issuer_key_path(self) -> str:
        """Path to tenant's issuer private key"""
        return os.path.join(self.keys_path, "issuer_private_key.pem")
    
    @property
    def issuer_public_key_path(self) -> str:
        """Path to tenant's issuer public key"""
        return os.path.join(self.keys_path, "issuer_public_key.pem")
    
    @property
    def bbs_key_path(self) -> str:
        """Path to tenant's BBS+ key"""
        return os.path.join(self.keys_path, "bbs_private_key.pem")
    
    # === STATIC ASSETS === #
    
    @property
    def static_path(self) -> str:
        """Tenant-specific static assets directory"""
        static_dir = self.base_path / "static"
        static_dir.mkdir(parents=True, exist_ok=True)
        return str(static_dir)
    
    @property
    def logo_path(self) -> str:
        """Full path to university logo"""
        return os.path.join(self.static_path, self.logo_filename)
    
    # === TENANT-SPECIFIC SETTINGS === #
    
    def get_issuer_config(self) -> Dict[str, Any]:
        """Get tenant-specific issuer configuration"""
        return {
            "issuer_name": self.name,
            "issuer_display_name": self.short_name,
            "issuer_logo": self.logo_filename,
            "primary_color": self.primary_color,
            "accent_color": self.accent_color,
            "text_color": self.text_color
        }
    
    def get_verifier_config(self) -> Dict[str, Any]:
        """Get tenant-specific verifier configuration"""
        return {
            "verifier_name": f"{self.short_name} Verifier",
            "accepted_issuers": [self.name],
            "primary_color": self.primary_color
        }
    
    def get_credential_template(self) -> Dict[str, Any]:
        """Get tenant-specific credential template"""
        # Get theme colors if available, otherwise use defaults
        theme_colors = getattr(self, 'theme_colors', {})
        
        return {
            "issuer": self.name,
            "issuerDisplayName": self.short_name,
            "credentialSubject": {
                "credentialBranding": {
                    "backgroundColor": "#FFFFFF",  # White background as requested
                    "textColor": theme_colors.get('textColor', self.text_color.lstrip('#')),
                    "logo": self.logo_filename,
                    "vcLogo": self.logo_filename,
                    "bgColorCard": theme_colors.get('bgColorCard', 'FFFFFF'),
                    "bgColorSectionTop": theme_colors.get('bgColorTop', self.primary_color.lstrip('#')),
                    "bgColorSectionBot": theme_colors.get('bgColorBot', self.accent_color.lstrip('#')),
                    "fgColorTitle": theme_colors.get('fgColorTitle', self.text_color.lstrip('#'))
                }
            }
        }
    
    # === UTILITY METHODS === #
    
    def ensure_directories(self):
        """Ensure all tenant directories exist"""
        directories = [
            self.base_path,
            self.keys_path,
            self.static_path,
            self.backup_path
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured directory exists: {directory}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tenant config to dictionary (for compatibility with legacy system)"""
        return {
            'id': self.tenant_id,
            'name': self.name,
            'short_name': self.short_name,
            'logo': self.logo_filename,
            'color': self.primary_color,
            'domain_patterns': self.domain_patterns,
            'database_path': self.database_path,
            'keys_path': self.keys_path,
            'static_path': self.static_path
        } 