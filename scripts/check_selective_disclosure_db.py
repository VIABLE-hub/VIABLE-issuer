#!/usr/bin/env python3
"""
Simple database checker for selective disclosure settings
Does not require Flask app initialization
"""

import sqlite3
import json
import os
from pathlib import Path

def check_tenant_database(tenant_id):
    """Check selective disclosure settings in a tenant's database"""
    db_path = f"/Volumes/herbke/studentvc_backups/stvc_latest/backend/src/tenants/instances/{tenant_id}/database.db"
    
    if not os.path.exists(db_path):
        return {"status": "error", "message": f"Database not found: {db_path}"}
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if tenant_settings table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tenant_settings'")
        if not cursor.fetchone():
            return {"status": "error", "message": "tenant_settings table not found"}
        
        # Get settings for this tenant
        cursor.execute("SELECT disclosure_settings FROM tenant_settings WHERE tenant_id=?", (tenant_id,))
        result = cursor.fetchone()
        
        if not result or not result[0]:
            return {"status": "success", "configured": False, "fields": []}
        
        # Parse the JSON
        disclosure_settings = json.loads(result[0])
        selective_disclosure = disclosure_settings.get('selective_disclosure', {})
        mandatory_fields = selective_disclosure.get('mandatory_fields', [])
        
        conn.close()
        
        return {
            "status": "success",
            "configured": len(mandatory_fields) > 0,
            "fields": mandatory_fields,
            "count": len(mandatory_fields)
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


def main():
    print("="*80)
    print("SELECTIVE DISCLOSURE DATABASE VERIFICATION")
    print("="*80)
    print("\nChecking selective disclosure settings directly from databases...")
    
    tenants = ['root', 'tub', 'fub', 'veritas']
    results = {}
    
    for tenant_id in tenants:
        print(f"\n📋 Checking tenant: {tenant_id}")
        result = check_tenant_database(tenant_id)
        results[tenant_id] = result
        
        if result['status'] == 'error':
            print(f"  ❌ Error: {result['message']}")
        elif result['configured']:
            print(f"  ✅ Configured with {result['count']} fields: {result['fields']}")
        else:
            print(f"  ℹ️  No selective disclosure fields configured")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    configured_tenants = [t for t, r in results.items() if r.get('configured', False)]
    if configured_tenants:
        print(f"\n✅ {len(configured_tenants)} tenant(s) have selective disclosure configured:")
        for tenant in configured_tenants:
            fields = results[tenant]['fields']
            print(f"   - {tenant}: {fields}")
    else:
        print(f"\n⚠️  No tenants have selective disclosure fields configured")
        print(f"   This is normal - configure fields in Settings → Selective Disclosure")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()

