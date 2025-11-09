#!/usr/bin/env python3
"""
Quick diagnostic script to check selective disclosure settings in the database.
"""
import sqlite3
import os
import json
import sys

def check_disclosure_settings(tenant_name):
    """Check the selective disclosure settings for a specific tenant"""
    
    db_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'src', 
        'tenants', 
        'instances', 
        tenant_name, 
        'database.db'
    ))
    
    print("="*80)
    print(f"🔍 CHECKING SELECTIVE DISCLOSURE SETTINGS FOR: {tenant_name.upper()}")
    print("="*80)
    print(f"📂 Database path: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if tenant_settings table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='tenant_settings'
        """)
        
        if not cursor.fetchone():
            print("❌ Table 'tenant_settings' does not exist!")
            conn.close()
            return False
        
        print("✅ Table 'tenant_settings' exists")
        
        # Get tenant settings
        cursor.execute("""
            SELECT tenant_id, disclosure_settings 
            FROM tenant_settings 
            WHERE tenant_id = ?
        """, (tenant_name,))
        
        result = cursor.fetchone()
        
        if not result:
            print(f"⚠️  No settings found for tenant: {tenant_name}")
            print(f"💡 Try saving settings in the UI first: http://localhost:5005/{tenant_name}/settings")
            conn.close()
            return False
        
        tenant_id, disclosure_settings_json = result
        print(f"✅ Found settings for tenant: {tenant_id}")
        print()
        
        # Parse disclosure settings
        if not disclosure_settings_json:
            print("⚠️  disclosure_settings column is NULL")
            print("💡 Try saving settings in the UI: http://localhost:5005/{tenant_name}/settings")
            conn.close()
            return False
        
        try:
            disclosure_settings = json.loads(disclosure_settings_json)
            print("📊 Raw disclosure_settings JSON:")
            print(json.dumps(disclosure_settings, indent=2))
            print()
            
            # Check selective disclosure structure
            if 'selective_disclosure' not in disclosure_settings:
                print("⚠️  'selective_disclosure' key not found!")
                print("💡 Expected structure: {'selective_disclosure': {'mandatory_fields': [...]}}")
                conn.close()
                return False
            
            print("✅ 'selective_disclosure' key exists")
            
            selective_disclosure = disclosure_settings['selective_disclosure']
            
            if 'mandatory_fields' not in selective_disclosure:
                print("⚠️  'mandatory_fields' key not found in selective_disclosure!")
                conn.close()
                return False
            
            print("✅ 'mandatory_fields' key exists")
            
            mandatory_fields = selective_disclosure['mandatory_fields']
            print()
            print("="*80)
            print("📋 MANDATORY FIELDS:")
            print("="*80)
            print(f"Total count: {len(mandatory_fields)}")
            print(f"Fields: {mandatory_fields}")
            print()
            
            # Categorize fields
            technical_fields = ['iss', 'sub', 'exp', 'nbf', 'jti', 'nonce', 'signed_nonce', 'bbs_dpk', 'total_messages', 'validity_identifier']
            user_fields = [f for f in mandatory_fields if f not in technical_fields]
            
            print(f"👤 User fields: {user_fields}")
            print(f"🔧 Technical fields: {[f for f in mandatory_fields if f in technical_fields]}")
            print()
            
            if not user_fields:
                print("⚠️  WARNING: No user fields selected!")
                print("💡 Go to settings and select firstName, lastName, etc.")
                print(f"   URL: http://localhost:5005/{tenant_name}/settings")
            else:
                print("✅ User fields are configured correctly!")
                print()
                print("🧪 Expected behavior when verifying:")
                print(f"   - Wallet should request: {', '.join(user_fields)}")
                print(f"   - Plus technical fields: {', '.join(technical_fields[:3])}...")
            
            conn.close()
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse disclosure_settings JSON: {e}")
            print(f"Raw value: {disclosure_settings_json}")
            conn.close()
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("="*80)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        tenant = sys.argv[1]
    else:
        # Default to veritas
        tenant = 'veritas'
        print(f"💡 No tenant specified, checking: {tenant}")
        print(f"   Usage: python3 check_disclosure_settings.py <tenant_name>")
        print()
    
    success = check_disclosure_settings(tenant)
    
    print()
    print("="*80)
    if success:
        print("✅ CHECK COMPLETED SUCCESSFULLY")
    else:
        print("❌ CHECK FOUND ISSUES")
    print("="*80)
    
    sys.exit(0 if success else 1)

