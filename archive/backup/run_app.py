#!/usr/bin/env python3
"""
Application runner with error handling
"""

import sys
import traceback

try:
    # Try to run the new refactored app
    print("🚀 Starting Invoice Manager v2.0...")
    from main_refactored import main
    main()
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Trying to run the original application...")
    try:
        from main import main as original_main
        original_main()
    except Exception as e2:
        print(f"❌ Original app also failed: {e2}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Application error: {e}")
    print("\n📋 Full traceback:")
    traceback.print_exc()
    sys.exit(1)
