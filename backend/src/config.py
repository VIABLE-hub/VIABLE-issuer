import os

class Config:
    # Branding
    UNIVERSITY_NAME = "Berliner Verkehrsbetriebe"
    UNIVERSITY_SHORT_NAME = "BVG"
    PRIMARY_COLOR = "#F0D722"
    ACCENT_COLOR = "#F0D722"
    TEXT_COLOR = "#FFFFFF"
    
    # Logos
    LOGO_FILENAME = "BVG_Logo_07.2021.svg"
    HOCHSCHUL_BRANDING_LOGO = "BVG_Logo_07.2021.svg"
    MAIN_LOGO_FILENAME = "BVG_Logo_07.2021.svg"

    # Theme Colors
    THEME_COLORS = {
        'bgColorCard': 'F0D722',
        'bgColorTop': 'F0D722',
        'bgColorBot': 'FFFFFF',
        'fgColorTitle': 'FFFFFF',
        'accentColor': 'F0D722',
        'textColor': 'FFFFFF'
    }

    # Credential Template
    CREDENTIAL_TEMPLATE = {
        "issuer": UNIVERSITY_NAME,
        "issuerDisplayName": UNIVERSITY_SHORT_NAME,
        "credentialSubject": {
            "credentialBranding": {
                "backgroundColor": "#FFFFFF",
                "textColor": "FFFFFF",
                "logo": HOCHSCHUL_BRANDING_LOGO,
                "vcLogo": HOCHSCHUL_BRANDING_LOGO,
                "bgColorCard": "F0D722",
                "bgColorSectionTop": "F0D722",
                "bgColorSectionBot": "FFFFFF",
                "fgColorTitle": "FFFFFF"
            }
        }
    }

    # Database
    INSTANCE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(INSTANCE_PATH, 'studentvc.sqlite')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Issuer Identity
    # If set, this DID will be used as the 'iss' claim in VCs.
    # If empty, a dynamic did:key will be generated from the keys.
    # Example: "did:web:tu-berlin.de"
    ISSUER_DID = os.environ.get("ISSUER_DID", "did:web:bvg.viable-project.de")

