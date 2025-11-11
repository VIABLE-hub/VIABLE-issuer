"""
Veritas Tenant Configuration

Configuration for Veritas University tenant.
"""

from ...base_config import BaseTenantConfig


class VeritasConfig(BaseTenantConfig):
    """Veritas University tenant configuration."""
    
    def __init__(self):
        super().__init__(tenant_id="veritas")
    
    @property
    def name(self) -> str:
        """Full university name"""
        return "Veritas University"
    
    @property
    def short_name(self) -> str:
        """Short university name"""
        return "Veritas"
    
    @property
    def domain_patterns(self) -> list:
        """Domain patterns for auto-detection"""
        return ['veritas', 'veritas-university']
    
    @property
    def primary_color(self) -> str:
        """Primary university color"""
        return "#003f7f"  # Berlin Blue
    
    @property
    def logo_filename(self) -> str:
        """🚨 FIXED: University logo filename for university branding section only"""
        return "veritas-logo.png"
    
    @property
    def main_logo_filename(self) -> str:
        """🚨 FIXED: Main logo filename should ALWAYS be StudentVC logo for header"""
        return "studentVC-logo-sora-cropped.png"
    
    @property
    def accent_color(self) -> str:
        """Accent color"""
        return "#4A90E2"  # Light Blue
    
    @property
    def text_color(self) -> str:
        """Text color"""
        return "#FFFFFF"  # White for contrast on blue
    
    @property
    def tenant_color(self) -> str:
        """Color used in templates and UI."""
        return self.primary_color.lstrip('#')
    
    @property
    def theme_colors(self) -> dict:
        """Veritas theme colors - USER SPECIFIED COLORS."""
        return {
            'bgColorCard': '003f7f',                         # BG Color (Card) #003f7f
            'bgColorTop': '003f7f',                          # BG Color (Top) #003f7f
            'bgColorBot': 'FFFFFF',                          # BG Color (Bottom) #FFFFFF
            'fgColorTitle': 'FFFFFF',                        # FG Color (Title) #FFFFFF
            'accentColor': self.accent_color.lstrip('#'),    # Light blue accent
            'textColor': 'FFFFFF'                            # White text for contrast on blue
        }
    
    def get_credential_template(self) -> dict:
        """Get Veritas credential template"""
        theme_colors = self.theme_colors
        
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

