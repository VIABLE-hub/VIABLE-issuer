from flask import Blueprint, render_template, current_app, request, jsonify
from src.utils import get_current_server_url
from logging import getLogger
from ..verifier.utils import generate_qr_code, get_demo_credential
from datetime import datetime

logger = getLogger(__name__)

usecases = Blueprint('usecases', __name__, url_prefix='/usecases')

# Definierte Use Case Metadaten für konsistente Darstellung
USECASE_METADATA = {
    'health': {
        'name': 'Gesundheitswesen',
        'icon': 'fa-heartbeat',
        'color': 'blue',
        'description': 'Datenschutzkonforme Zertifikate fuer medizinische Nachweise mit Zero-Knowledge Verifikation',
        'tech_standards': ['HL7 FHIR', 'IHE XDS.b', 'DICOM'],
        'related': ['kyc', 'education']
    },
    'supply-chain': {
        'name': 'Lieferkette',
        'icon': 'fa-truck-loading',
        'color': 'green',
        'description': 'Kryptographisch verifizierbare Herkunftsnachweise und Produktinformationen',
        'tech_standards': ['GS1 EPCIS', 'ISO 9001'],
        'related': ['kyc']
    },
    'kyc': {
        'name': 'KYC und Identifikation',
        'icon': 'fa-id-card',
        'color': 'indigo',
        'description': 'Rechtssichere Identitaetsverifikation ohne unnotige Datenpreisgabe',
        'tech_standards': ['eIDAS', 'FATF'],
        'related': ['health', 'education']
    },
    'education': {
        'name': 'Bildung und Zertifikate',
        'icon': 'fa-graduation-cap',
        'color': 'purple',
        'description': 'Faelschungssichere akademische Abschluesse und Bildungsnachweise',
        'tech_standards': ['Open Badges', 'ELMO'],
        'related': ['recruiting']
    },
    'recruiting': {
        'name': 'Recruiting und Arbeitszeugnisse',
        'icon': 'fa-briefcase',
        'color': 'amber',
        'description': 'Verifizierbare Berufserfahrung und Kompetenznachweise',
        'tech_standards': ['HR-XML', 'EuroPass'],
        'related': ['education']
    }
}

@usecases.route('/')
def index():
    """Hauptseite des Use Case Hubs mit Übersicht der verfügbaren Anwendungsfälle"""
    return render_template(
        'usecases/index.html', 
        year=datetime.now().year,
        usecases=USECASE_METADATA
    )

@usecases.route('/test')
def test():
    """Einfache Test-Seite für Alpine.js"""
    return render_template(
        'usecases/test.html',
        year=datetime.now().year
    )

@usecases.route('/simple')
def simple():
    """Vereinfachte Use Case Seite mit minimaler Alpine.js Struktur"""
    return render_template(
        'usecases/simple.html',
        year=datetime.now().year
    )

@usecases.route('/api/metadata')
def get_metadata():
    """API-Endpunkt für Use Case-Metadaten"""
    return jsonify(USECASE_METADATA)

@usecases.route('/health')
def health():
    """Gesundheitsanwendungen für Verifiable Credentials"""
    server_url = get_current_server_url() + "/verifier/"
    img = generate_qr_code(
        f"openid4vp://?request_uri={server_url}presentation-request")
    return render_template(
        'usecases/health.html', 
        img_data=img, 
        demo_credential=get_demo_credential(), 
        year=datetime.now().year,
        usecase="health",
        metadata=USECASE_METADATA['health']
    )

@usecases.route('/supply-chain')
def supply_chain():
    """Lieferketten- und Logistikanwendungen für Verifiable Credentials"""
    server_url = get_current_server_url() + "/verifier/"
    img = generate_qr_code(
        f"openid4vp://?request_uri={server_url}presentation-request")
    return render_template(
        'usecases/supply-chain.html', 
        img_data=img, 
        demo_credential=get_demo_credential(), 
        year=datetime.now().year,
        usecase="supply-chain",
        metadata=USECASE_METADATA['supply-chain']
    )

@usecases.route('/kyc')
def kyc():
    """KYC und Identifikationsanwendungen für Verifiable Credentials"""
    server_url = get_current_server_url() + "/verifier/"
    img = generate_qr_code(
        f"openid4vp://?request_uri={server_url}presentation-request")
    return render_template(
        'usecases/kyc.html', 
        img_data=img, 
        demo_credential=get_demo_credential(), 
        year=datetime.now().year,
        usecase="kyc",
        metadata=USECASE_METADATA['kyc']
    )

@usecases.route('/education')
def education():
    """Bildungsanwendungen für Verifiable Credentials"""
    server_url = get_current_server_url() + "/verifier/"
    img = generate_qr_code(
        f"openid4vp://?request_uri={server_url}presentation-request")
    return render_template(
        'usecases/education.html', 
        img_data=img, 
        demo_credential=get_demo_credential(), 
        year=datetime.now().year,
        usecase="education",
        metadata=USECASE_METADATA['education']
    )

@usecases.route('/recruiting')
def recruiting():
    """Recruiting und Arbeitszeugnis-Anwendungen für Verifiable Credentials"""
    server_url = get_current_server_url() + "/verifier/"
    img = generate_qr_code(
        f"openid4vp://?request_uri={server_url}presentation-request")
    return render_template(
        'usecases/recruiting.html', 
        img_data=img, 
        demo_credential=get_demo_credential(), 
        year=datetime.now().year,
        usecase="recruiting",
        metadata=USECASE_METADATA['recruiting']
    )

@usecases.route('/more-info')
def more_info():
    """Informationsseite zu weiteren und zukünftigen Anwendungsfällen"""
    return render_template(
        'usecases/more-info.html', 
        year=datetime.now().year
    )

@usecases.route('/related/<usecase>')
def related_usecases(usecase):
    """API-Endpunkt für verwandte Use Cases"""
    if usecase not in USECASE_METADATA:
        return jsonify({'error': 'Usecase not found'}), 404
        
    related_ids = USECASE_METADATA[usecase].get('related', [])
    related_data = {id: USECASE_METADATA[id] for id in related_ids if id in USECASE_METADATA}
    
    return jsonify(related_data)
