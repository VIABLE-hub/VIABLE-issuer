"""
TU Berlin Tenant Configuration

Configuration for Technische Universität Berlin tenant.
"""

from ...base_config import BaseTenantConfig


class TUBerlinConfig(BaseTenantConfig):
    """TU Berlin tenant configuration."""
    
    def __init__(self):
        super().__init__(tenant_id="tub")
    
    @property
    def name(self) -> str:
        """Full university name"""
        return "Technische Universität Berlin"
    
    @property
    def short_name(self) -> str:
        """Short university name"""
        return "TU Berlin"
    
    @property
    def domain_patterns(self) -> list:
        """Domain patterns for auto-detection"""
        return ['tu-berlin', 'tub']
    
    @property
    def primary_color(self) -> str:
        """Primary university color"""
        return "#c50e1f"  # TU Red
    
    @property
    def logo_filename(self) -> str:
        """🚨 FIXED: University logo filename for header (RED LOGO)"""
        return "tub_logo.png"
    
    @property
    def hochschul_branding_logo(self) -> str:
        """🚨 FIXED: White/Red logo filename for hochschul-branding forms"""
        return "tub_logo_white_red.png"
    
    @property
    def main_logo_filename(self) -> str:
        """🚨 FIXED: Main logo filename should ALWAYS be StudentVC logo for header"""
        return "studentVC-logo-sora-cropped.png"
    
    @property
    def accent_color(self) -> str:
        """Accent color"""
        return "#FFD700"  # Gold
    
    @property
    def text_color(self) -> str:
        """Text color"""
        return "#FFFFFF"  # White
    
    @property
    def tenant_color(self) -> str:
        """Color used in templates and UI."""
        return self.primary_color.lstrip('#')
    
    @property
    def theme_colors(self) -> dict:
        """TU Berlin theme colors - USER SPECIFIED COLORS."""
        return {
            'bgColorCard': 'c50e1f',                         # BG Color (Card) #c50e1f
            'bgColorTop': 'c50e1f',                          # BG Color (Top) #c50e1f  
            'bgColorBot': 'FFFFFF',                          # BG Color (Bottom) #FFFFFF
            'fgColorTitle': 'FFFFFF',                        # FG Color (Title) #FFFFFF
            'accentColor': self.accent_color.lstrip('#'),    # Gold accent
            'textColor': 'FFFFFF'                            # White text for contrast on red
        } 
    
    def get_credential_template(self) -> dict:
        """🚨 OVERRIDE: Use WHITE logo for credential branding forms"""
        theme_colors = self.theme_colors
        
        return {
            "issuer": self.name,
            "issuerDisplayName": self.short_name,
            "credentialSubject": {
                "credentialBranding": {
                    "backgroundColor": "#FFFFFF",  # White background as requested
                    "textColor": theme_colors.get('textColor', self.text_color.lstrip('#')),
                    "logo": self.hochschul_branding_logo,  # 🚨 USE WHITE LOGO for forms
                    "vcLogo": self.hochschul_branding_logo,  # 🚨 USE WHITE LOGO for forms
                    "bgColorCard": theme_colors.get('bgColorCard', 'FFFFFF'),
                    "bgColorSectionTop": theme_colors.get('bgColorTop', self.primary_color.lstrip('#')),
                    "bgColorSectionBot": theme_colors.get('bgColorBot', self.accent_color.lstrip('#')),
                    "fgColorTitle": theme_colors.get('fgColorTitle', self.text_color.lstrip('#'))
                }
            }
        } 