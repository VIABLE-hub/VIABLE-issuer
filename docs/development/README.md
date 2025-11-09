# StudentVC Development Guide

This directory contains guides and documentation for developing the StudentVC system.

## Contents

- [Deployment](deployment/README.md) - Guides for deploying StudentVC
- [Testing](testing/README.md) - Guides for testing StudentVC
- [Troubleshooting](troubleshooting/README.md) - Guides for troubleshooting common issues

## BBS+ Development and Debugging

The StudentVC system uses BBS+ signatures for credential issuance and verification. The following guides provide information on developing, debugging, and fixing BBS+ issues:

- [BBS+ UniFFI Linux Guide](bbs_uniffi_linux_guide.md) - Guide for handling BBS+ UniFFI contract differences between macOS and Linux
- [Docker BBS+ Debugging](docker_bbs_debugging.md) - Guide for debugging BBS+ issues in Docker containers
- [Docker BBS+ Hot-Patching](docker_bbs_hotpatch.md) - Guide for hot-patching BBS+ issues in running Docker containers
- [Docker BBS+ Monitoring](docker_bbs_monitoring.md) - Guide for continuously monitoring BBS+ health in Docker containers

## Development Environment

To set up a development environment for StudentVC, follow these steps:

1. Clone the repository
2. Install dependencies
3. Set up the environment
4. Run the development server

For detailed instructions, see the [Setup Guide](setup.md).

## Multi-Tenant Development

StudentVC supports multiple tenants (root, tuberlin, fuberlin). Each tenant has its own:

- Configuration
- Database
- Keys
- Static files

For more information on developing for multiple tenants, see the [Multi-Tenant Development Guide](multi_tenant.md).

## Docker Development

For Docker-based development, use the following commands:

```bash
# Build Docker images
make docker-build

# Run Docker containers
make docker-run

# Test BBS+ in Docker
make docker-bbs

# Test Docker API functionality
make test-docker-api

# Debug BBS+ in Docker containers
make debug-bbs-docker

# Hot-patch BBS+ in Docker containers
make hot-patch-bbs

# Monitor BBS+ health in Docker containers
make monitor-bbs
```

For more information on Docker development, see the [Docker Development Guide](docker.md).

## Getting Started

### Prerequisites
- Python 3.12+
- macOS, Linux, or Windows
- Virtual environment support

### Quick Setup

1. **Clone and Setup**
   ```bash
   git clone <repository>
   cd stvc
   make setup
   ```

2. **Start Development Server**
   ```bash
   make dev
   ```

3. **Access Application**
   - Frontend: https://localhost:8080
   - Issuer: https://localhost:8080/issuer
   - Verifier: https://localhost:8080/verifier
   - Settings: https://localhost:8080/settings

### Environment Configuration

The project uses `test_env` as the virtual environment:
- ✅ **Stable Environment**: `test_env/` with Python 3.12
- ✅ **Makefile Integration**: All commands use `test_env`
- ✅ **Production Ready**: Consistent dependency management

### Development Workflow

1. **Start Development**
   ```bash
   make dev                    # Start server
   make test                   # Run tests
   make clean                  # Clean environment
   ```

2. **File Organization**
   ```
   backend/src/               # Core application code
   ├── issuer/               # Credential issuance
   ├── verifier/             # Credential verification
   ├── settings/             # System configuration
   └── templates/            # HTML templates
   
   tests/                    # Test suites
   ├── backend/              # Backend tests
   ├── integration/          # Integration tests
   └── fixtures/             # Test data
   
   mobile/ios/               # iOS wallet app
   docs/                     # Documentation
   scripts/development/      # Development scripts
   ```

### Key Features
- 🔒 **HTTPS by Default**: Secure local development
- 🌐 **NGROK Integration**: Real-time URL updates
- 📱 **iOS Wallet**: Complete mobile integration
- 🧪 **Comprehensive Testing**: 28+ test files organized

### Development Resources
- [Troubleshooting](./troubleshooting/) - Common issues and solutions
- [Deployment](./deployment/) - Production deployment
- [Testing](./testing/) - Test suite documentation

# StudentVC · Verifiable Credential System for Education & Beyond

Digitale Nachweise, ausgestellt durch Hochschulen – überprüfbar per QR-Code mit Zero-Knowledge und BBS+ Signaturen. DSGVO-konform, interoperabel, datensouverän.

## Projektübersicht

Das StudentVC Projekt (ehem. STVC) ist ein vollständiges Multi-Tenant-System für Verifiable Credentials mit BBS+ Signaturen und Zero-Knowledge Proofs. Das System besteht aus:

- **iOS Wallet App**: Native iOS-Anwendung in SwiftUI
- **Flask Backend**: Python-basierter Server für die Ausstellung und Verifikation von Credentials
- **BBS Core**: Rust-basierte Kryptographie-Bibliothek für BBS+ Signaturen

## ✅ Funktionen im Überblick

* ✨ **BBS+ Signaturausstellung** mit Selective Disclosure
* 📲 QR-basierte **Verifikation in Echtzeit** via ZKP
* 🧾 Verifiable Credential Lifecycle (Issue, Revoke, Re-Enable)
* 📊 VC Status Management & Statistik-Dashboard
* 🧠 Use Case Overview (Health, KYC, Supply Chain...)
* 🌐 Mehrmandantenfähig und DSGVO-konform
* 🌓 **Light Mode ist default** (kein Dark Mode beim Start!)

## Projektstruktur

```
stvc/
├── ios/                          # iOS Wallet Anwendung
│   ├── StudentWallet/            # Haupt-iOS-App
│   │   ├── StudentWallet/        # App-Quellcode
│   │   │   ├── Views/           # SwiftUI Views
│   │   │   ├── Services/        # API Services und Business Logic
│   │   │   ├── Models/          # Datenmodelle
│   │   │   └── Utilities/       # Hilfsfunktionen
│   │   └── StudentWallet.xcodeproj  # Xcode-Projekt
│   └── BBSCoreIOS/              # Swift Package für BBS+ Kryptographie
├── backend-server/              # Flask Backend Server
│   ├── main.py                 # Server-Einstiegspunkt
│   ├── src/                    # Backend-Quellcode
│   │   ├── issuer/            # Credential-Ausstellung
│   │   ├── auth.py            # Authentifizierung
│   │   └── models.py          # Datenbankmodelle
│   ├── bbs-core/              # BBS+ Kryptographie (Submodul)
│   ├── requirements.txt       # Python-Abhängigkeiten
│   └── instance/              # SSL-Zertifikate und Datenbank
└── backend/                   # Ursprüngliche BBS Core (nur Rust)
```

## Installation und Setup

### Backend (Flask Server)

1. **Verzeichnis wechseln:**
   ```bash
   cd backend-server
   ```

2. **Virtuelle Python-Umgebung erstellen:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Dependencies installieren:**
   ```bash
   pip install -r requirements.txt
   ```

4. **BBS Core Submodule aktualisieren:**
   ```bash
   git submodule update --init --recursive
   ```

5. **Server starten:**
   ```bash
   PYTHONPATH=./bbs-core/python python main.py
   ```

Der Server läuft auf `https://192.168.178.122:8081` mit HTTPS und selbst-signiertem Zertifikat.

### iOS Wallet

1. **Xcode öffnen:**
   ```bash
   open ios/StudentWallet/StudentWallet.xcodeproj
   ```

2. **Projekt in Xcode kompilieren und starten**

Die iOS-App ist bereits für die Verbindung zum Backend (https://192.168.178.122:8081) konfiguriert.

## Konfiguration

### Backend-Konfiguration

- **Server-URL**: Konfiguriert in `backend-server/main.py`
- **SSL-Zertifikate**: Automatisch generiert in `backend-server/instance/`
- **Datenbank**: SQLite in `backend-server/instance/database.db`

### iOS-App-Konfiguration

- **Server-URL**: Konfigurierbar in der App unter Einstellungen  
- **Standard-URL**: `https://127.0.0.1:8080`
- **BBS Core**: Verwendet lokales Swift Package `BBSCoreIOS`

## Features

### Backend Features

- **OpenID4VCI Standard**: Vollständige Implementierung des OpenID for Verifiable Credential Issuance Standards
- **BBS+ Signaturen**: Unterstützung für privacy-preserving Zero-Knowledge Proofs
- **Multi-Tenant**: Unterstützung für mehrere Aussteller/Organisationen
- **JWT-basierte Authentifizierung**: Sichere Token-basierte Authentifizierung
- **HTTPS**: SSL/TLS-verschlüsselte Kommunikation

### iOS Wallet Features

- **Credential Management**: Speichern und Verwalten von Verifiable Credentials
- **QR-Code-Scanner**: Scannen von Credential-Angeboten
- **Biometrische Authentifizierung**: Face ID/Touch ID für Wallet-Zugriff
- **Zero-Knowledge Proofs**: Selective Disclosure mit BBS+ Signaturen
- **Modern UI**: Native SwiftUI-Interface

## Entwicklung

### Backend-Entwicklung

```bash
# Entwicklungsserver mit Debug-Modus
cd backend-server
source venv/bin/activate
PYTHONPATH=./bbs-core/python python main.py
```

### iOS-Entwicklung

- Öffne das Xcode-Projekt: `ios/StudentWallet/StudentWallet.xcodeproj`
- Minimal iOS 15.0 erforderlich
- Verwendet SwiftUI und Combine Framework

## API-Endpunkte

Der Backend-Server stellt folgende Hauptendpunkte bereit:

- `GET /.well-known/openid-credential-issuer` - Issuer-Metadaten
- `POST /authorize` - OAuth2-Autorisierung
- `POST /token` - Token-Austausch
- `POST /credential` - Credential-Ausstellung
- `GET /jwks` - JSON Web Key Set
- `GET /issuer` - Issuer-Interface

## Sicherheit

- **HTTPS-Only**: Alle Kommunikation über TLS verschlüsselt
- **BBS+ Signaturen**: Privacy-preserving Kryptographie
- **Biometrische Authentifizierung**: Sichere Wallet-Entsperrung
- **Zero-Knowledge Proofs**: Selective Disclosure ohne Preisgabe sensibler Daten

## 🔧 Schnellstart (Docker)

```bash
docker build -t studentvc .
docker run -d -p 8080:8080 studentvc
```

Zugriff unter: [http://localhost:8080](http://localhost:8080)

## ☸️ Kubernetes Quick-Start (Minimal)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: studentvc
spec:
  containers:
  - name: app
    image: studentvc:latest
    ports:
    - containerPort: 8080
```

```bash
kubectl apply -f studentvc-pod.yaml
kubectl port-forward pod/studentvc 8080:8080
```

## 🔍 Verifikationsprozess verstehen

Direkt in der App findest du unterhalb der QR-Code-Sektion eine neue Infobox:

> **🔍 Technischer Hintergrund der Verifikation**
> ZK-basiert. Flattened Messages. Öffentlicher Schlüssel. BBS+ Verify.

Beispielcode:

```js
const messages = flatten(presentation.attributes);
const pk = fetchPublicKey(presentation.verificationMethod);
const result = bbs.verify(messages, presentation.signature, pk);
```

## 🧪 Testdaten generieren

Nutze den Button `Zufällige Daten`, um eine VC mit Testdaten zu generieren. Anschließend: `QR-Code erzeugen`.

## Status

✅ **Backend**: Läuft erfolgreich auf `http://0.0.0.0:8080`
✅ **iOS Wallet**: TestFlight folgt
✅ **Android Wallet**: In Arbeit
✅ **BBS Core**: Python-Bindings erfolgreich kompiliert
✅ **Light-Mode**: Als Standard implementiert

## Troubleshooting

### Häufige Probleme

1. **Port bereits belegt**: Backend-Port in `main.py` ändern
2. **SSL-Zertifikat-Fehler**: In iOS-Einstellungen "Unsichere Verbindungen" für Entwicklung erlauben
3. **BBS Core Import-Fehler**: `PYTHONPATH` korrekt setzen

## 🏗️ Multi-Tenant Struktur

StudentVC wurde für eine flexible Multi-Tenant-Architektur konzipiert. Neue Tenants können einfach hinzugefügt werden:

```bash
# Neuen Tenant erstellen
./create_tenant.sh --name "HochschuleXYZ" --primary-color "#003f7f" --logo "/path/to/logo.png"
```

Jeder Tenant erhält:
- Eigene Datenbank-Instanz (isoliert)
- Individuelles Branding (Logo & Farbschema)
- Dedizierte Schlüsselverwaltung
- Separate Endpoints (z.B. xyz.studentvc.de)

Die Konfiguration erfolgt über eine einfache JSON-Datei:

```json
{
  "tenant_id": "hochschulexyz",
  "display_name": "Hochschule XYZ",
  "branding": {
    "primary_color": "#003f7f",
    "secondary_color": "#0066cc",
    "logo_path": "/static/tenants/xyz/logo.png"
  },
  "endpoints": {
    "base_url": "https://xyz.studentvc.de",
    "api_base": "/api/v1"
  }
}
```

## 📘 Dokumentation

Die vollständige technische Doku ist unter `/docs` erreichbar (lokal oder gehostet).

### Beispielstruktur:

* `/docs/verifikation` – Wie funktioniert die ZKP-basierte Verifikation?
* `/docs/krypto` – BBS+, Public Key Extraktion
* `/docs/deployment` – Docker, Kubernetes & Konfiguration

## 📬 Kontakt

Für Fragen oder Kooperationen: [p.herbke@tu-berlin.de](mailto:p.herbke@tu-berlin.de)

---

© StudentVC – TU Berlin - Verifiable Credentials für die Zukunft der digitalen Nachweise

### Log-Dateien

- Backend-Logs: `backend-server/instance/service.log`
- iOS-Logs: Xcode Debug Console

## Lizenz

Dieses Projekt wurde für die Technische Universität Berlin entwickelt und ist für Forschung und Bildung bestimmt.

## Kontakt

Bei Fragen zum STVC-Projekt wenden Sie sich an das Internet of Services Lab der TU Berlin.