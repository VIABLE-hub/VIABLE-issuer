"""
Root Tenant Configuration

Default tenant configuration for the main StudentVC instance.
Used when no specific university tenant is selected.
"""

from ...base_config import BaseTenantConfig


class RootConfig(BaseTenantConfig):
    """Root tenant configuration - the default StudentVC instance."""
    
    def __init__(self):
        super().__init__(tenant_id="root")
    
    @property
    def name(self) -> str:
        """Full name"""
        return "StudentVC Default"
    
    @property
    def short_name(self) -> str:
        """Short name"""
        return "Default"
    
    @property
    def domain_patterns(self) -> list:
        """Domain patterns for auto-detection"""
        return ['root', 'default', 'studentvc']
    
    @property
    def primary_color(self) -> str:
        """Primary color"""
        return "#003f7f"  # Berlin Blue default
    
    @property
    def logo_filename(self) -> str:
        """Logo filename for hochschul-branding"""
        return "studentVC-logo-sora-cropped-darkmode.png"
    
    @property
    def main_logo_filename(self) -> str:
        """Main logo filename for top-left corner"""
        return "studentVC-logo-sora-cropped.png"
    
    @property
    def accent_color(self) -> str:
        """Accent color"""
        return "#FFD700"  # Gold
    
    @property
    def text_color(self) -> str:
        """Text color"""
        return "#333333"  # Dark gray
    
    @property
    def tenant_color(self) -> str:
        """Color used in templates and UI."""
        return self.primary_color.lstrip('#')
    
    @property
    def theme_colors(self) -> dict:
        """Default theme colors for root tenant."""
        return {
            'bgColorCard': self.primary_color.lstrip('#'),
            'fgColorTitle': '#FFFFFF',
            'accentColor': self.accent_color.lstrip('#'),
            'textColor': self.text_color.lstrip('#')
        } 