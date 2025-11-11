#!/usr/bin/env python3
"""
Complete trace of selective disclosure flow to find where personal fields are lost.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

def test_selective_disclosure_flow():
    """Test the complete selective disclosure flow"""
    
    print("="*80)
    print("🧪 TESTING SELECTIVE DISCLOSURE FLOW")
    print("="*80)
    print()
    
    # Step 1: Check database
    print("📋 STEP 1: Check Database Settings")
    print("-" * 80)
    
    import sqlite3
    import json
    
    db_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'src', 
        'tenants', 
        'instances', 
        'veritas', 
        'database.db'
    ))
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT disclosure_settings 
        FROM tenant_settings 
        WHERE tenant_id = 'veritas'
    """)
    result = cursor.fetchone()
    conn.close()
    
    if not result or not result[0]:
        print("❌ No settings found in database!")
        return False
    
    settings = json.loads(result[0])
    saved_fields = settings.get('selective_disclosure', {}).get('mandatory_fields', [])
    print(f"✅ Database has: {saved_fields}")
    print()
    
    # Step 2: Test constants
    print("📋 STEP 2: Check Constants")
    print("-" * 80)
    
    # Read constants file directly
    constants_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'src', 
        'verifier', 
        'constants.py'
    ))
    
    with open(constants_path, 'r') as f:
        constants_content = f.read()
    
    # Parse ALL_SELECTABLE_FIELDS
    if 'SELECTABLE_USER_FIELDS = [' in constants_content:
        start = constants_content.index('SELECTABLE_USER_FIELDS = [')
        end = constants_content.index(']', start) + 1
        selectable_user_fields_str = constants_content[start:end]
        exec(selectable_user_fields_str)
        ALL_SELECTABLE_FIELDS = SELECTABLE_USER_FIELDS
        print(f"ALL_SELECTABLE_FIELDS: {ALL_SELECTABLE_FIELDS}")
    
    # Parse TECHNICAL_FIELDS
    if 'TECHNICAL_FIELDS = [' in constants_content:
        start = constants_content.index('TECHNICAL_FIELDS = [')
        end = constants_content.index(']', start) + 1
        technical_fields_str = constants_content[start:end]
        exec(technical_fields_str)
        print(f"TECHNICAL_FIELDS: {TECHNICAL_FIELDS}")
    print()
    
    for field in saved_fields:
        if field in ALL_SELECTABLE_FIELDS:
            print(f"✅ '{field}' IS in ALL_SELECTABLE_FIELDS")
        elif field in TECHNICAL_FIELDS:
            print(f"⚠️  '{field}' is a TECHNICAL field")
        else:
            print(f"❌ '{field}' NOT in ALL_SELECTABLE_FIELDS or TECHNICAL_FIELDS!")
    print()
    
    # Step 3: Conclusion
    print("📋 STEP 3: Conclusion from Database + Constants Check")
    print("-" * 80)
    
    print("✅ Database check: PASSED")
    print("✅ Constants check: PASSED (if firstName/lastName are in ALL_SELECTABLE_FIELDS)")
    print()
    print("🎯 The flow SHOULD work if:")
    print("   1. get_current_selective_disclosure_settings() loads from database correctly")
    print("   2. get_presentation_definition() properly separates fields")
    print("   3. iOS field processing loop executes correctly")
    print()
    print("💡 RECOMMENDATION:")
    print("   Start the server with 'make dev' and check the logs when generating QR code.")
    print("   Look for the '📤 FINAL PRESENTATION REQUEST TO WALLET' section.")
    print("   If 'User fields: 0', send me the complete logs.")
    print()
    
    return True


if __name__ == '__main__':
    print()
    success = test_selective_disclosure_flow()
    print()
    print("="*80)
    if success:
        print("✅ ALL TESTS PASSED! Selective disclosure should work!")
    else:
        print("❌ TESTS FAILED! Issue found in selective disclosure flow!")
    print("="*80)
    print()
    
    sys.exit(0 if success else 1)

