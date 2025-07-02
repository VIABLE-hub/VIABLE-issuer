"""
Perfect Tenant Detection System Tests
Tests the unified tenant detection with priority chain and caching
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from flask import Flask, g, session
import sys
sys.path.append('backend/src')

from src.tenants.detection import (
    TenantDetector, 
    get_current_tenant_id, 
    set_current_tenant, 
    clear_tenant_detection_cache
)


class TestTenantDetector:
    """Test the core TenantDetector class"""
    
    def setup_method(self):
        """Setup for each test"""
        self.detector = TenantDetector()
        clear_tenant_detection_cache()
    
    def test_priority_chain_order(self):
        """Test that detection priority is correct"""
        expected_priority = [
            'flask_g_context',
            'session_stored', 
            'environment_var',
            'domain_pattern',
            'default_fallback'
        ]
        assert self.detector.DETECTION_PRIORITY == expected_priority
    
    @patch('src.tenants.detection.has_request_context')
    @patch('src.tenants.detection.g')
    def test_flask_g_context_detection(self, mock_g, mock_has_context):
        """Test Flask g context detection (highest priority)"""
        mock_has_context.return_value = True
        mock_g.tenant_id = 'tub'
        
        result = self.detector.detect_tenant()
        assert result == 'tub'
        assert self.detector.detection_method == 'flask_g_context'
    
    @patch('src.tenants.detection.has_request_context')
    @patch('src.tenants.detection.session')
    def test_session_stored_detection(self, mock_session, mock_has_context):
        """Test session-stored tenant detection"""
        mock_has_context.return_value = True
        mock_session.get.return_value = 'fub'
        
        # Mock g to not have tenant_id (so session is next priority)
        with patch('src.tenants.detection.g') as mock_g:
            mock_g.tenant_id = None
            
            result = self.detector.detect_tenant()
            assert result == 'fub'
            assert self.detector.detection_method == 'session_stored'
    
    @patch.dict(os.environ, {'UNIVERSITY_TENANT': 'root'})
    @patch('src.tenants.detection.has_request_context')
    def test_environment_var_detection(self, mock_has_context):
        """Test environment variable detection"""
        mock_has_context.return_value = False
        
        result = self.detector.detect_tenant()
        assert result == 'root'
        assert self.detector.detection_method == 'environment_var'
    
    @patch('src.tenants.detection.has_request_context')
    @patch('src.tenants.detection.request')
    def test_domain_pattern_detection(self, mock_request, mock_has_context):
        """Test domain pattern detection"""
        mock_has_context.return_value = True
        mock_request.host = 'tub.studentvc.example.com'
        
        # Mock other detection methods to fail
        with patch('src.tenants.detection.g') as mock_g:
            mock_g.tenant_id = None
            with patch('src.tenants.detection.session') as mock_session:
                mock_session.get.return_value = None
                with patch.dict(os.environ, {}, clear=True):
                    
                    result = self.detector.detect_tenant()
                    assert result == 'tub'
                    assert self.detector.detection_method == 'domain_pattern'
    
    def test_default_fallback(self):
        """Test default fallback when all other methods fail"""
        with patch('src.tenants.detection.has_request_context') as mock_has_context:
            mock_has_context.return_value = False
            with patch.dict(os.environ, {}, clear=True):
                
                result = self.detector.detect_tenant()
                assert result == 'root'
                assert self.detector.detection_method == 'default_fallback'
    
    def test_caching_functionality(self):
        """Test that detection results are properly cached"""
        with patch.dict(os.environ, {'UNIVERSITY_TENANT': 'tub'}):
            with patch('src.tenants.detection.has_request_context') as mock_has_context:
                mock_has_context.return_value = False
                
                # First call should detect and cache
                result1 = self.detector.detect_tenant()
                assert result1 == 'tub'
                
                # Second call should use cache (change env var to verify)
                with patch.dict(os.environ, {'UNIVERSITY_TENANT': 'fub'}):
                    result2 = self.detector.detect_tenant()
                    assert result2 == 'tub'  # Should still be cached value
    
    def test_cache_invalidation(self):
        """Test that cache can be properly invalidated"""
        with patch.dict(os.environ, {'UNIVERSITY_TENANT': 'tub'}):
            with patch('src.tenants.detection.has_request_context') as mock_has_context:
                mock_has_context.return_value = False
                
                # First detection
                result1 = self.detector.detect_tenant()
                assert result1 == 'tub'
                
                # Clear cache and change environment
                clear_tenant_detection_cache()
                with patch.dict(os.environ, {'UNIVERSITY_TENANT': 'fub'}):
                    result2 = self.detector.detect_tenant()
                    assert result2 == 'fub'  # Should detect new value
    
    def test_valid_tenant_ids(self):
        """Test validation of tenant IDs"""
        assert self.detector.is_valid_tenant_id('tub')
        assert self.detector.is_valid_tenant_id('fub') 
        assert self.detector.is_valid_tenant_id('root')
        assert not self.detector.is_valid_tenant_id('invalid')
        assert not self.detector.is_valid_tenant_id('')
        assert not self.detector.is_valid_tenant_id(None)


class TestGlobalTenantFunctions:
    """Test the global tenant detection functions"""
    
    def setup_method(self):
        """Setup for each test"""
        clear_tenant_detection_cache()
    
    @patch('src.tenants.detection.TenantDetector')
    def test_get_current_tenant_id(self, mock_detector_class):
        """Test get_current_tenant_id function"""
        mock_detector = MagicMock()
        mock_detector.detect_tenant.return_value = 'tub'
        mock_detector_class.return_value = mock_detector
        
        result = get_current_tenant_id()
        assert result == 'tub'
        mock_detector.detect_tenant.assert_called_once()
    
    @patch('src.tenants.detection.has_request_context')
    @patch('src.tenants.detection.g')
    def test_set_current_tenant(self, mock_g, mock_has_context):
        """Test set_current_tenant function"""
        mock_has_context.return_value = True
        
        set_current_tenant('fub')
        assert mock_g.tenant_id == 'fub'
    
    def test_set_current_tenant_invalid(self):
        """Test set_current_tenant with invalid tenant ID"""
        with pytest.raises(ValueError, match="Invalid tenant ID"):
            set_current_tenant('invalid_tenant')
    
    def test_cache_clearing(self):
        """Test cache clearing functionality"""
        # This should not raise any exceptions
        clear_tenant_detection_cache()


class TestTenantDetectionEdgeCases:
    """Test edge cases and error conditions"""
    
    def setup_method(self):
        """Setup for each test"""
        self.detector = TenantDetector()
        clear_tenant_detection_cache()
    
    def test_malformed_domain_patterns(self):
        """Test handling of malformed domain patterns"""
        with patch('src.tenants.detection.has_request_context') as mock_has_context:
            mock_has_context.return_value = True
            with patch('src.tenants.detection.request') as mock_request:
                # Test various malformed domains
                test_cases = [
                    'localhost:8080',  # No subdomain
                    'invalid-tenant.example.com',  # Invalid tenant
                    '',  # Empty domain
                    'www.example.com'  # Generic domain
                ]
                
                for domain in test_cases:
                    mock_request.host = domain
                    with patch('src.tenants.detection.g') as mock_g:
                        mock_g.tenant_id = None
                        with patch('src.tenants.detection.session') as mock_session:
                            mock_session.get.return_value = None
                            with patch.dict(os.environ, {}, clear=True):
                                
                                result = self.detector.detect_tenant()
                                # Should fallback to default
                                assert result == 'root'
    
    def test_case_insensitive_detection(self):
        """Test that tenant detection is case insensitive"""
        with patch.dict(os.environ, {'UNIVERSITY_TENANT': 'TUB'}):
            with patch('src.tenants.detection.has_request_context') as mock_has_context:
                mock_has_context.return_value = False
                
                result = self.detector.detect_tenant()
                assert result == 'tub'  # Should be normalized to lowercase
    
    def test_whitespace_handling(self):
        """Test handling of whitespace in tenant IDs"""
        with patch.dict(os.environ, {'UNIVERSITY_TENANT': '  tub  '}):
            with patch('src.tenants.detection.has_request_context') as mock_has_context:
                mock_has_context.return_value = False
                
                result = self.detector.detect_tenant()
                assert result == 'tub'  # Should be stripped
    
    @patch('src.tenants.detection.logger')
    def test_logging_behavior(self, mock_logger):
        """Test that detection events are properly logged"""
        with patch.dict(os.environ, {'UNIVERSITY_TENANT': 'tub'}):
            with patch('src.tenants.detection.has_request_context') as mock_has_context:
                mock_has_context.return_value = False
                
                result = self.detector.detect_tenant()
                assert result == 'tub'
                
                # Check that info was logged
                mock_logger.info.assert_called()


@pytest.fixture
def app():
    """Create Flask app for testing"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.secret_key = 'test-secret-key'
    return app


class TestTenantDetectionWithFlask:
    """Test tenant detection within Flask application context"""
    
    def test_detection_with_flask_context(self, app):
        """Test detection works properly within Flask context"""
        with app.test_request_context('/'):
            with app.test_client():
                # Test that detection works in request context
                result = get_current_tenant_id()
                assert result in ['tub', 'fub', 'root']  # Should return valid tenant
    
    def test_session_persistence(self, app):
        """Test that tenant ID persists in session"""
        with app.test_request_context('/'):
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess['tenant_id'] = 'tub'
                
                result = get_current_tenant_id()
                assert result == 'tub'
    
    def test_g_context_priority(self, app):
        """Test that Flask g context has highest priority"""
        with app.test_request_context('/'):
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess['tenant_id'] = 'fub'  # Set session to different value
                
                # Set g context
                set_current_tenant('tub')
                
                # Should return g context value (higher priority)
                result = get_current_tenant_id()
                assert result == 'tub'


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '--tb=short']) 