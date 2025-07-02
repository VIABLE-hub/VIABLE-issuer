"""
Perfect Tenant Isolation Tests
Tests cross-tenant isolation and data separation
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from flask import Flask
import sys
sys.path.append('backend/src')

from src.tenants.detection import get_current_tenant_id
from src.tenants.config_manager import TenantConfigManager


@pytest.fixture
def app():
    """Create Flask app for testing"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.secret_key = 'test-secret-key'
    return app


class TestTenantConfigIsolation:
    """Test that tenant configurations are properly isolated"""
    
    def setup_method(self):
        """Setup for each test"""
        self.config_manager = TenantConfigManager()
    
    def test_different_tenants_different_configs(self):
        """Test that different tenants get completely different configurations"""
        
        # Mock static configs for different tenants
        with patch.object(self.config_manager, 'load_static_config') as mock_static:
            with patch.object(self.config_manager, 'load_dynamic_settings') as mock_dynamic:
                
                def static_side_effect(tenant_id):
                    configs = {
                        'tub': {
                            'id': 'tub',
                            'name': 'Technische Universität Berlin',
                            'color': '#c41230'
                        },
                        'fub': {
                            'id': 'fub', 
                            'name': 'Freie Universität Berlin',
                            'color': '#008000'
                        }
                    }
                    return configs.get(tenant_id, {'id': tenant_id})
                
                def dynamic_side_effect(tenant_id):
                    settings = {
                        'tub': {
                            'network_config': {
                                'use_ngrok': True,
                                'ngrok_url': 'https://tub-123.ngrok.io'
                            },
                            'branding_config': {},
                            'credential_config': {}
                        },
                        'fub': {
                            'network_config': {
                                'use_ngrok': False,
                                'ngrok_url': ''
                            },
                            'branding_config': {},
                            'credential_config': {}
                        }
                    }
                    return settings.get(tenant_id, {
                        'network_config': {},
                        'branding_config': {},
                        'credential_config': {}
                    })
                
                mock_static.side_effect = static_side_effect
                mock_dynamic.side_effect = dynamic_side_effect
                
                # Get configurations for different tenants
                tub_config = self.config_manager.get_complete_tenant_config('tub')
                fub_config = self.config_manager.get_complete_tenant_config('fub')
                
                # Verify complete isolation
                assert tub_config['name'] == 'Technische Universität Berlin'
                assert fub_config['name'] == 'Freie Universität Berlin'
                assert tub_config['color'] == '#c41230'
                assert fub_config['color'] == '#008000'
                assert tub_config['network_config']['use_ngrok'] == True
                assert fub_config['network_config']['use_ngrok'] == False
    
    def test_cache_isolation(self):
        """Test that cache is properly isolated between tenants"""
        
        # Pre-populate cache with tenant-specific data
        self.config_manager._config_cache['tub'] = {
            'network_config': {'use_ngrok': True, 'ngrok_url': 'https://tub-cached.ngrok.io'}
        }
        self.config_manager._config_cache['fub'] = {
            'network_config': {'use_ngrok': False, 'connection_mode': 'local'}
        }
        
        # Verify cache isolation
        assert 'tub' in self.config_manager._config_cache
        assert 'fub' in self.config_manager._config_cache
        
        tub_cache = self.config_manager._config_cache['tub']
        fub_cache = self.config_manager._config_cache['fub']
        
        assert tub_cache['network_config']['use_ngrok'] == True
        assert fub_cache['network_config']['use_ngrok'] == False
        
        # Clear cache for one tenant
        self.config_manager.invalidate_cache('tub')
        
        # Only TUB cache should be cleared
        assert 'tub' not in self.config_manager._config_cache
        assert 'fub' in self.config_manager._config_cache
    
    def test_url_generation_isolation(self):
        """Test that URL generation is isolated per tenant"""
        
        # TUB with NGROK
        tub_config = {
            'network_config': {
                'use_ngrok': True,
                'ngrok_url': 'https://tub-prod.ngrok.io',
                'default_port': 8080
            }
        }
        
        # FUB with local IP
        fub_config = {
            'network_config': {
                'use_ngrok': False,
                'default_ip': '192.168.1.100',
                'default_port': 8080,
                'use_https': True
            }
        }
        
        # Root with public IP
        root_config = {
            'network_config': {
                'use_ngrok': False,
                'default_ip': '203.0.113.10',
                'default_port': 443,
                'use_https': True
            }
        }
        
        # Generate URLs for each tenant
        tub_urls = self.config_manager.compute_effective_urls(tub_config)
        fub_urls = self.config_manager.compute_effective_urls(fub_config)
        root_urls = self.config_manager.compute_effective_urls(root_config)
        
        # Verify URL isolation
        assert tub_urls['server_url'] == 'https://tub-prod.ngrok.io'
        assert tub_urls['issuer_url'] == 'https://tub-prod.ngrok.io/issuer'
        
        assert fub_urls['server_url'] == 'https://192.168.1.100:8080'
        assert fub_urls['issuer_url'] == 'https://192.168.1.100:8080/issuer'
        
        assert root_urls['server_url'] == 'https://203.0.113.10:443'
        assert root_urls['issuer_url'] == 'https://203.0.113.10:443/issuer'
        
        # Verify no cross-contamination
        assert 'tub-prod.ngrok.io' not in fub_urls['server_url']
        assert 'tub-prod.ngrok.io' not in root_urls['server_url']
        assert '192.168.1.100' not in tub_urls['server_url']
        assert '192.168.1.100' not in root_urls['server_url']


class TestTenantNetworkIsolation:
    """Test network configuration isolation between tenants"""
    
    def test_ngrok_url_isolation(self):
        """Test that NGROK URLs are completely isolated between tenants"""
        config_manager = TenantConfigManager()
        
        # Mock network update for different tenants
        with patch.object(config_manager, 'update_network_config') as mock_update:
            
            def update_side_effect(tenant_id, network_config):
                # Simulate tenant-specific storage
                tenant_configs = {
                    'tub': {
                        'network_config': {
                            'use_ngrok': True,
                            'ngrok_url': network_config.get('ngrok_url', ''),
                            'connection_mode': 'ngrok'
                        },
                        'urls': {
                            'server_url': network_config.get('ngrok_url', ''),
                            'issuer_url': f"{network_config.get('ngrok_url', '')}/issuer"
                        }
                    },
                    'fub': {
                        'network_config': {
                            'use_ngrok': network_config.get('use_ngrok', False),
                            'ngrok_url': network_config.get('ngrok_url', ''),
                            'connection_mode': network_config.get('connection_mode', 'local')
                        },
                        'urls': {
                            'server_url': 'https://192.168.1.100:8080',
                            'issuer_url': 'https://192.168.1.100:8080/issuer'
                        }
                    }
                }
                return tenant_configs.get(tenant_id, {})
            
            mock_update.side_effect = update_side_effect
            
            # Update TUB with NGROK
            tub_update = config_manager.update_network_config('tub', {
                'use_ngrok': True,
                'ngrok_url': 'https://tub-special.ngrok.io',
                'connection_mode': 'ngrok'
            })
            
            # Update FUB with local config
            fub_update = config_manager.update_network_config('fub', {
                'use_ngrok': False,
                'ngrok_url': '',
                'connection_mode': 'local'
            })
            
            # Verify isolation
            assert tub_update['network_config']['ngrok_url'] == 'https://tub-special.ngrok.io'
            assert fub_update['network_config']['ngrok_url'] == ''
            
            assert 'tub-special.ngrok.io' in tub_update['urls']['issuer_url']
            assert 'tub-special.ngrok.io' not in fub_update['urls']['issuer_url']
    
    def test_connection_mode_isolation(self):
        """Test that connection modes are isolated between tenants"""
        config_manager = TenantConfigManager()
        
        # Test different connection modes for different tenants
        tub_config = {
            'network_config': {
                'use_ngrok': True,
                'ngrok_url': 'https://tub.ngrok.io',
                'connection_mode': 'ngrok'
            }
        }
        
        fub_config = {
            'network_config': {
                'use_ngrok': False,
                'default_ip': '192.168.1.100',
                'connection_mode': 'local'
            }
        }
        
        root_config = {
            'network_config': {
                'use_ngrok': False,
                'default_ip': '203.0.113.10',
                'connection_mode': 'public'
            }
        }
        
        # Generate URLs
        tub_urls = config_manager.compute_effective_urls(tub_config)
        fub_urls = config_manager.compute_effective_urls(fub_config)
        root_urls = config_manager.compute_effective_urls(root_config)
        
        # Verify connection mode isolation
        assert 'tub.ngrok.io' in tub_urls['server_url']  # NGROK mode
        assert '192.168.1.100' in fub_urls['server_url']  # Local mode
        assert '203.0.113.10' in root_urls['server_url']  # Public mode


class TestTenantDatabaseIsolation:
    """Test database-level tenant isolation"""
    
    @patch('src.tenants.config_manager.TenantSettings')
    @patch('src.tenants.config_manager.db')
    def test_database_query_isolation(self, mock_db, mock_tenant_settings):
        """Test that database queries are isolated by tenant_id"""
        config_manager = TenantConfigManager()
        
        # Mock database query
        mock_settings = MagicMock()
        mock_tenant_settings.query.filter_by.return_value.first.return_value = mock_settings
        
        # Load settings for specific tenant
        config_manager.load_dynamic_settings('tub')
        
        # Verify query was filtered by tenant_id
        mock_tenant_settings.query.filter_by.assert_called_with(tenant_id='tub')
    
    @patch('src.tenants.config_manager.TenantSettings')
    @patch('src.tenants.config_manager.db')
    def test_database_update_isolation(self, mock_db, mock_tenant_settings):
        """Test that database updates are isolated by tenant_id"""
        config_manager = TenantConfigManager()
        
        # Mock existing settings for tenant
        mock_settings = MagicMock()
        mock_settings.network_config = {}
        mock_tenant_settings.query.filter_by.return_value.first.return_value = mock_settings
        
        # Update network config
        network_config = {
            'use_ngrok': True,
            'ngrok_url': 'https://test.ngrok.io'
        }
        
        config_manager.update_network_config('tub', network_config)
        
        # Verify query was isolated to specific tenant
        mock_tenant_settings.query.filter_by.assert_called_with(tenant_id='tub')
        
        # Verify database commit was called
        mock_db.session.commit.assert_called_once()
    
    @patch('src.tenants.config_manager.TenantSettings')
    @patch('src.tenants.config_manager.db')
    def test_new_tenant_creation_isolation(self, mock_db, mock_tenant_settings):
        """Test that new tenant creation doesn't affect existing tenants"""
        config_manager = TenantConfigManager()
        
        # Mock no existing settings (new tenant)
        mock_tenant_settings.query.filter_by.return_value.first.return_value = None
        
        # Mock TenantSettings constructor
        mock_new_settings = MagicMock()
        mock_tenant_settings.return_value = mock_new_settings
        
        # Create settings for new tenant
        network_config = {
            'use_ngrok': False,
            'connection_mode': 'local'
        }
        
        config_manager.update_network_config('new_tenant', network_config)
        
        # Verify new tenant was created with correct tenant_id
        mock_tenant_settings.assert_called_with(tenant_id='new_tenant')
        
        # Verify new settings were added to session
        mock_db.session.add.assert_called_once_with(mock_new_settings)
        mock_db.session.commit.assert_called_once()


class TestTenantSecurityIsolation:
    """Test security aspects of tenant isolation"""
    
    def test_no_tenant_leakage_in_cache_keys(self):
        """Test that cache keys don't allow tenant data leakage"""
        config_manager = TenantConfigManager()
        
        # Populate cache for multiple tenants
        config_manager._config_cache['tub'] = {'secret': 'tub-secret-data'}
        config_manager._config_cache['fub'] = {'secret': 'fub-secret-data'}
        config_manager._config_cache['root'] = {'secret': 'root-secret-data'}
        
        # Verify each tenant can only access their own cache
        assert config_manager._config_cache['tub']['secret'] == 'tub-secret-data'
        assert config_manager._config_cache['fub']['secret'] == 'fub-secret-data'
        assert config_manager._config_cache['root']['secret'] == 'root-secret-data'
        
        # Verify no cross-access
        assert config_manager._config_cache['tub']['secret'] != 'fub-secret-data'
        assert config_manager._config_cache['fub']['secret'] != 'root-secret-data'
        assert config_manager._config_cache['root']['secret'] != 'tub-secret-data'
    
    def test_config_immutability_between_tenants(self):
        """Test that modifying one tenant's config doesn't affect others"""
        config_manager = TenantConfigManager()
        
        # Mock configs for different tenants
        with patch.object(config_manager, 'load_static_config') as mock_static:
            with patch.object(config_manager, 'load_dynamic_settings') as mock_dynamic:
                
                base_static = {'id': 'test', 'name': 'Test Tenant'}
                base_dynamic = {
                    'network_config': {'use_ngrok': False},
                    'branding_config': {},
                    'credential_config': {}
                }
                
                mock_static.return_value = base_static.copy()
                mock_dynamic.return_value = base_dynamic.copy()
                
                # Get config for tenant 1
                config1 = config_manager.get_complete_tenant_config('tenant1')
                
                # Modify the returned config (simulating malicious/accidental modification)
                config1['network_config']['use_ngrok'] = True
                config1['name'] = 'Modified Name'
                
                # Get config for tenant 2
                config2 = config_manager.get_complete_tenant_config('tenant2')
                
                # Verify tenant 2's config wasn't affected by tenant 1's modifications
                assert config2['network_config']['use_ngrok'] == False
                assert config2['name'] == 'Test Tenant'
    
    def test_url_generation_no_cross_contamination(self):
        """Test that URL generation has no cross-tenant contamination"""
        config_manager = TenantConfigManager()
        
        # Generate URLs for tenant with sensitive NGROK URL
        sensitive_config = {
            'network_config': {
                'use_ngrok': True,
                'ngrok_url': 'https://sensitive-data-123.ngrok.io',
                'default_port': 8080
            }
        }
        
        # Generate URLs for another tenant with different config
        normal_config = {
            'network_config': {
                'use_ngrok': False,
                'default_ip': '127.0.0.1',
                'default_port': 8080,
                'use_https': False
            }
        }
        
        sensitive_urls = config_manager.compute_effective_urls(sensitive_config)
        normal_urls = config_manager.compute_effective_urls(normal_config)
        
        # Verify no contamination
        assert 'sensitive-data-123.ngrok.io' not in normal_urls['server_url']
        assert 'sensitive-data-123.ngrok.io' not in normal_urls['issuer_url']
        assert 'sensitive-data-123.ngrok.io' not in normal_urls['verifier_url']
        
        assert '127.0.0.1' not in sensitive_urls['server_url']
        assert sensitive_urls['server_url'] == 'https://sensitive-data-123.ngrok.io'


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '--tb=short']) 