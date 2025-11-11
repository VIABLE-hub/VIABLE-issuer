"""
FU Berlin Tenant Configuration

Configuration for Freie Universität Berlin tenant.
"""

from ...base_config import BaseTenantConfig


class FUBerlinConfig(BaseTenantConfig):
    """FU Berlin tenant configuration."""
    
    def __init__(self):
        super().__init__(tenant_id="fub")
    
    @property
    def name(self) -> str:
        """Full university name"""
        return "Freie Universität Berlin"
    
    @property
    def short_name(self) -> str:
        """Short university name"""
        return "FU Berlin"
    
    @property
    def domain_patterns(self) -> list:
        """Domain patterns for auto-detection"""
        return ['fu-berlin', 'fub']
    
    @property
    def primary_color(self) -> str:
        """Primary university color"""
        return "#007a3e"  # FU Green
    
    @property
    def logo_filename(self) -> str:
        """🚨 FIXED: University logo filename for university branding section only"""
        return "fub-logo.png"
    
    @property
    def main_logo_filename(self) -> str:
        """🚨 FIXED: Main logo filename should ALWAYS be StudentVC logo for header"""
        return "studentVC-logo-sora-cropped.png"
    
    @property
    def accent_color(self) -> str:
        """Accent color"""
        return "#00a84f"  # Light Green
    
    @property
    def text_color(self) -> str:
        """Text color"""
        return "#FFFFFF"  # White for contrast on green
    
    @property
    def tenant_color(self) -> str:
        """Color used in templates and UI."""
        return self.primary_color.lstrip('#')
    
    @property
    def theme_colors(self) -> dict:
        """FU Berlin theme colors - USER SPECIFIED COLORS."""
        return {
            'bgColorCard': '007a3e',                         # BG Color (Card) #007a3e (CORRECTED: was 00a84f)
            'bgColorTop': '007a3e',                          # BG Color (Top) #007a3e (CORRECTED: was 00a84f)
            'bgColorBot': 'FFFFFF',                          # BG Color (Bottom) #FFFFFF
            'fgColorTitle': 'FFFFFF',                        # FG Color (Title) #FFFFFF
            'accentColor': self.accent_color.lstrip('#'),    # Light green accent
            'textColor': 'FFFFFF'                            # White text as specified
        } 