# 🧪 PERFECT TENANT SYSTEM - TESTING GUIDE

## **MUST RUN TESTS BEFORE PRODUCTION USE**

The Perfect Tenant System includes comprehensive tests that **MUST** be run before using `make dev-tub`, `make dev-fub`, or `make dev-root` commands.

## **Quick Start**

### **1. Run All Tests (Recommended)**
```bash
python run_perfect_tenant_tests.py
```

### **2. Run Quick Smoke Test**
```bash
python run_perfect_tenant_tests.py --smoke
```

### **3. Run Individual Test Suites**
```bash
# Tenant detection system
python -m pytest tests/test_tenant_detection.py -v

# Configuration manager
python -m pytest tests/test_config_manager.py -v

# Network API endpoints
python -m pytest tests/test_network_api.py -v

# Tenant middleware
python -m pytest tests/test_middleware.py -v

# Cross-tenant isolation
python -m pytest tests/test_tenant_isolation.py -v

# Makefile commands
python -m pytest tests/test_makefile_commands.py -v

# Integration tests
python -m pytest tests/test_integration.py -v
```

## **Test Coverage**

### **🔍 Tenant Detection Tests** (`test_tenant_detection.py`)
- ✅ Priority chain validation (Flask g → Session → Environment → Domain → Default)
- ✅ Environment variable detection (`UNIVERSITY_TENANT`)
- ✅ Domain pattern matching
- ✅ Caching functionality
- ✅ Cache invalidation
- ✅ Error handling and fallbacks

### **⚙️ Configuration Manager Tests** (`test_config_manager.py`)
- ✅ Static configuration loading (JSON files)
- ✅ Dynamic settings (database integration)
- ✅ Complete tenant configuration assembly
- ✅ URL generation (NGROK vs local)
- ✅ Caching and cache invalidation
- ✅ Error handling and defaults

### **🌐 Network API Tests** (`test_network_api.py`)
- ✅ GET `/api/network` endpoint
- ✅ POST `/api/network` configuration updates
- ✅ POST `/api/network/test` connection testing
- ✅ Input validation (NGROK URLs, ports, modes)
- ✅ Tenant isolation in API calls
- ✅ Error handling and edge cases

### **🔀 Middleware Tests** (`test_middleware.py`)
- ✅ Flask application integration
- ✅ Automatic tenant context setting
- ✅ Request/response cycle handling
- ✅ Error graceful handling
- ✅ Decorator functionality
- ✅ Configuration options

### **🔒 Tenant Isolation Tests** (`test_tenant_isolation.py`)
- ✅ Configuration isolation between tenants
- ✅ Cache isolation and no cross-contamination
- ✅ URL generation isolation
- ✅ Database query isolation
- ✅ Security validation

### **📝 Makefile Commands Tests** (`test_makefile_commands.py`)
- ✅ Makefile existence and syntax
- ✅ `dev-tub`, `dev-fub`, `dev-root` command presence
- ✅ Environment variable setting
- ✅ Tenant configuration files
- ✅ Application startup simulation

### **🔗 Integration Tests** (`test_integration.py`)
- ✅ End-to-end tenant workflows
- ✅ Cross-module communication
- ✅ System readiness validation
- ✅ Import verification

## **Expected Test Results**

When all tests pass, you should see:

```
🎉 PERFECT TENANT SYSTEM READY FOR PRODUCTION!
✅ All critical tests passed
✅ Tenant isolation verified
✅ API endpoints validated
✅ Configuration management tested
✅ Detection system working

🚀 You can now safely run:
   • make dev-tub
   • make dev-fub
   • make dev-root
```

## **Troubleshooting Test Failures**

### **Common Issues**

#### **Import Errors**
```bash
ModuleNotFoundError: No module named 'src.tenants.detection'
```
**Solution**: Ensure all new tenant files are created and properly placed:
- `backend/src/tenants/__init__.py`
- `backend/src/tenants/detection.py`
- `backend/src/tenants/config_manager.py`
- `backend/src/tenants/middleware.py`

#### **Configuration File Errors**
```bash
assert 'id' in config_data
```
**Solution**: Ensure tenant config files exist and are valid:
- `backend/src/tenants/instances/tub/config.json`
- `backend/src/tenants/instances/fub/config.json`
- `backend/src/tenants/instances/root/config.json`

#### **Environment Variable Issues**
```bash
Expected 'tub', got 'root'
```
**Solution**: Clear any conflicting environment variables:
```bash
unset UNIVERSITY_TENANT
unset CURRENT_TENANT
unset RUNTIME_TENANT
```

#### **Database Connection Issues**
```bash
Failed to load tenant configuration
```
**Solution**: Ensure database models are properly migrated and TenantSettings table exists.

### **Test Environment Setup**

#### **Prerequisites**
- Python 3.8+
- pytest (`pip install pytest`)
- All new tenant modules created
- Tenant configuration files in place

#### **Environment Variables**
Tests automatically manage environment variables. No manual setup required.

#### **Database Requirements**
Tests use mocks for database operations. No database setup required for testing.

## **Manual Verification Steps**

After tests pass, manually verify:

### **1. Tenant Detection**
```python
# In Python shell
import os
os.environ['UNIVERSITY_TENANT'] = 'tub'

import sys
sys.path.append('backend/src')
from src.tenants.detection import get_current_tenant_id

print(get_current_tenant_id())  # Should print: tub
```

### **2. Configuration Loading**
```python
from src.tenants.config_manager import TenantConfigManager

config_manager = TenantConfigManager()
config = config_manager.get_complete_tenant_config('tub')
print(config['name'])  # Should print tenant name
```

### **3. URL Generation**
```python
test_config = {
    'network_config': {
        'use_ngrok': True,
        'ngrok_url': 'https://test.ngrok.io'
    }
}

urls = config_manager.compute_effective_urls(test_config)
print(urls['issuer_url'])  # Should print: https://test.ngrok.io/issuer
```

## **Production Deployment Checklist**

Before using in production:

- [ ] All tests pass (run `python run_perfect_tenant_tests.py`)
- [ ] Tenant configuration files created and validated
- [ ] Database migrations applied (if using TenantSettings)
- [ ] Network settings configured per tenant
- [ ] NGROK URLs configured (if using NGROK mode)
- [ ] Makefile commands tested (`make dev-tub --dry-run`)
- [ ] Environment variables cleared from previous setups

## **Continuous Integration**

Add to your CI/CD pipeline:

```yaml
# .github/workflows/tenant-tests.yml
- name: Run Perfect Tenant Tests
  run: |
    python run_perfect_tenant_tests.py
    if [ $? -ne 0 ]; then
      echo "❌ Tenant tests failed - deployment aborted"
      exit 1
    fi
```

## **Support**

If tests fail or you encounter issues:

1. **Check file structure**: Ensure all new files are in correct locations
2. **Verify imports**: Test individual module imports
3. **Check dependencies**: Ensure all required packages installed
4. **Review logs**: Check test output for specific error messages
5. **Reset environment**: Clear all tenant-related environment variables

---

**⚠️ CRITICAL: Do not use `make dev-tub`, `make dev-fub`, or `make dev-root` until all tests pass!** 