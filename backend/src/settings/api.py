#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""API key management routes – DB-backed via APIKey model."""

import logging
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

api_settings = Blueprint('api_settings', __name__)
logger = logging.getLogger(__name__)

SCOPE_MAP = {
    'issuer':   ['credentials:issue', 'qr:issuance'],
    'verifier': ['credentials:verify', 'qr:verification'],
    'admin':    ['credentials:issue', 'credentials:verify', 'credentials:revoke',
                 'qr:issuance', 'qr:verification', 'system:health', 'admin'],
}


def _caller():
    try:
        return current_user.name if current_user.is_authenticated else 'system'
    except Exception:
        return 'system'


def _key_to_dict(k):
    return {
        'id':           k.key_id,
        'name':         k.name,
        'description':  k.description or '',
        'prefix':       k.key_prefix,
        'scopes':       k.scopes or [],
        'is_active':    k.is_active,
        'created_at':   k.created_at.isoformat() if k.created_at else None,
        'last_used_at': k.last_used_at.isoformat() if k.last_used_at else None,
        'usage_count':  k.usage_count or 0,
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@api_settings.route('/api/keys/list', methods=['GET'])
@login_required
def list_api_keys():
    try:
        from ..models import APIKey
        keys = APIKey.query.order_by(APIKey.created_at.desc()).all()
        return jsonify({'success': True, 'keys': [_key_to_dict(k) for k in keys]})
    except Exception as e:
        logger.error('Error listing API keys: %s', e)
        return jsonify({'success': False, 'message': str(e)}), 500


@api_settings.route('/api/keys/generate', methods=['POST'])
@login_required
def generate_api_key():
    try:
        from ..models import APIKey
        data = request.get_json() or {}
        name = (data.get('name') or '').strip()
        if not name:
            return jsonify({'success': False, 'message': 'Name ist erforderlich'}), 400

        scope = data.get('scope', 'issuer')
        scopes = SCOPE_MAP.get(scope, SCOPE_MAP['issuer'])
        description = (data.get('description') or f'{scope.capitalize()} API-Key').strip()

        api_key_record, raw_key = APIKey.generate_new_key(
            name=name,
            description=description,
            scopes=scopes,
            created_by=_caller(),
        )

        return jsonify({
            'success':  True,
            'message':  'API-Key erfolgreich generiert',
            'key_id':   api_key_record.key_id,
            'key':      raw_key,
            'api_key':  raw_key,
            'prefix':   api_key_record.key_prefix,
            'scopes':   scopes,
        })
    except Exception as e:
        logger.error('Error generating API key: %s', e)
        return jsonify({'success': False, 'message': str(e)}), 500


@api_settings.route('/api/keys/revoke/<key_id>', methods=['POST'])
@api_settings.route('/api/keys/<key_id>/revoke', methods=['POST'])
@login_required
def revoke_api_key(key_id):
    try:
        from ..models import APIKey
        key = APIKey.query.filter_by(key_id=key_id).first()
        if not key:
            return jsonify({'success': False, 'message': 'Key nicht gefunden'}), 404
        data = request.get_json() or {}
        key.revoke(revoked_by=_caller(), reason=data.get('reason', 'Manuell widerrufen'))
        return jsonify({'success': True, 'message': 'API-Key widerrufen'})
    except Exception as e:
        logger.error('Error revoking API key: %s', e)
        return jsonify({'success': False, 'message': str(e)}), 500


# ---------------------------------------------------------------------------
# OpenAPI spec for Swagger UI
# ---------------------------------------------------------------------------

@api_settings.route('/api/openapi.json', methods=['GET'])
def openapi_spec():
    from flask import request as req
    base = req.host_url.rstrip('/')
    spec = {
        'openapi': '3.0.3',
        'info': {
            'title': 'BVG VERITAS API',
            'description': (
                'API zum Ausstellen & Verifizieren von BVG-Mitarbeiter-Credentials '
                '(OID4VCI + SD-JWT).\n\n'
                '**Authentifizierung:** API-Key aus dem Einstellungen-Tab als '
                'Bearer-Token:\n```\nAuthorization: Bearer stvc_xxx\n```'
            ),
            'version': '2.0.0',
        },
        'servers': [{'url': base, 'description': 'Aktueller Server'}],
        'security': [{'BearerAuth': []}],
        'components': {
            'securitySchemes': {
                'BearerAuth': {
                    'type': 'http',
                    'scheme': 'bearer',
                    'description': 'API-Key (stvc_...) aus dem API-Tab der Einstellungen',
                }
            },
            'schemas': {
                'IssuanceRequest': {
                    'type': 'object',
                    'required': ['mitarbeiterId', 'firstName', 'lastName'],
                    'properties': {
                        'mitarbeiterId': {'type': 'string', 'example': 'BVG-12345'},
                        'firstName':     {'type': 'string', 'example': 'Max'},
                        'lastName':      {'type': 'string', 'example': 'Mustermann'},
                        'department':    {'type': 'string', 'example': 'Fahrbetrieb'},
                        'role':          {'type': 'string', 'example': 'Busfahrer'},
                        'validity_seconds': {
                            'type': 'integer', 'default': 120,
                            'minimum': 30, 'maximum': 86400,
                        },
                    },
                },
                'QRResponse': {
                    'type': 'object',
                    'properties': {
                        'success':   {'type': 'boolean'},
                        'offer_url': {'type': 'string'},
                        'qr_code': {
                            'type': 'object',
                            'properties': {
                                'data':   {'type': 'string', 'description': 'Base64 PNG'},
                                'format': {'type': 'string', 'example': 'png'},
                            },
                        },
                        'expires_at': {'type': 'string', 'format': 'date-time'},
                    },
                },
                'GenerateKeyRequest': {
                    'type': 'object',
                    'required': ['name'],
                    'properties': {
                        'name':        {'type': 'string', 'example': 'Issuer-Integration'},
                        'description': {'type': 'string'},
                        'scope': {
                            'type': 'string',
                            'enum': ['issuer', 'verifier', 'admin'],
                            'default': 'issuer',
                        },
                    },
                },
            },
        },
        'paths': {
            '/api/v1/qr/issuance': {
                'post': {
                    'tags': ['QR Codes'],
                    'summary': 'Issuance-QR generieren',
                    'description': (
                        'Erstellt einen `openid-credential-offer://`-Link + QR-Code '
                        'für die BVG Wallet App.\n\n'
                        'Scope erforderlich: `qr:issuance`'
                    ),
                    'requestBody': {
                        'required': True,
                        'content': {
                            'application/json': {
                                'schema': {'$ref': '#/components/schemas/IssuanceRequest'}
                            }
                        },
                    },
                    'responses': {
                        '200': {
                            'description': 'QR-Code generiert',
                            'content': {
                                'application/json': {
                                    'schema': {'$ref': '#/components/schemas/QRResponse'}
                                }
                            },
                        }
                    },
                }
            },
            '/api/v1/qr/verification': {
                'post': {
                    'tags': ['QR Codes'],
                    'summary': 'Verification-QR generieren',
                    'description': 'Erstellt einen QR-Code der zur Verifier-Domain führt.\n\nScope: `qr:verification`',
                    'requestBody': {
                        'required': False,
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object',
                                    'properties': {
                                        'verifier_domain': {
                                            'type': 'string',
                                            'default': 'gv.viable-project.de',
                                        }
                                    },
                                }
                            }
                        },
                    },
                    'responses': {
                        '200': {'description': 'QR-Code generiert'}
                    },
                }
            },
            '/api/credentials': {
                'get': {
                    'tags': ['Credentials'],
                    'summary': 'Alle Credentials auflisten',
                    'description': 'Gibt alle ausgestellten Credentials zurück.\n\nScope: `credentials:verify`',
                    'responses': {'200': {'description': 'Credential-Liste'}},
                }
            },
            '/api/credential/{identifier}/revoke': {
                'post': {
                    'tags': ['Credentials'],
                    'summary': 'Credential widerrufen',
                    'description': 'Scope: `credentials:revoke`',
                    'parameters': [{
                        'name': 'identifier', 'in': 'path',
                        'required': True, 'schema': {'type': 'string'},
                    }],
                    'responses': {'200': {'description': 'Widerrufen'}},
                }
            },
            '/api/credential/{identifier}/restore': {
                'post': {
                    'tags': ['Credentials'],
                    'summary': 'Credential wiederherstellen',
                    'description': 'Scope: `credentials:revoke`',
                    'parameters': [{
                        'name': 'identifier', 'in': 'path',
                        'required': True, 'schema': {'type': 'string'},
                    }],
                    'responses': {'200': {'description': 'Wiederhergestellt'}},
                }
            },
            '/api/system/health': {
                'get': {
                    'tags': ['System'],
                    'summary': 'System-Health-Check',
                    'security': [],
                    'responses': {'200': {'description': 'System-Status'}},
                }
            },
            '/api/keys/list': {
                'get': {
                    'tags': ['API Keys'],
                    'summary': 'API-Keys auflisten',
                    'responses': {'200': {'description': 'Key-Liste'}},
                }
            },
            '/api/keys/generate': {
                'post': {
                    'tags': ['API Keys'],
                    'summary': 'Neuen API-Key generieren',
                    'requestBody': {
                        'required': True,
                        'content': {
                            'application/json': {
                                'schema': {'$ref': '#/components/schemas/GenerateKeyRequest'}
                            }
                        },
                    },
                    'responses': {'200': {'description': 'Neuer API-Key (einmalig sichtbar)'}},
                }
            },
            '/api/keys/revoke/{key_id}': {
                'post': {
                    'tags': ['API Keys'],
                    'summary': 'API-Key widerrufen',
                    'parameters': [{
                        'name': 'key_id', 'in': 'path',
                        'required': True, 'schema': {'type': 'string'},
                    }],
                    'responses': {'200': {'description': 'Widerrufen'}},
                }
            },
        },
    }
    return jsonify(spec)


@api_settings.route('/docs', methods=['GET'])
def api_docs():
    return jsonify({
        'swagger_ui': '/settings',
        'openapi_spec': '/api/openapi.json',
    })
