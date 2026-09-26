#!/usr/bin/env python3
"""
Quick Launcher for Yaoundé Compiler GUI
Simply run: python run_gui.py
"""

import sys
import os

# Add project directories to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'src'))
sys.path.insert(0, os.path.join(project_root, 'tests'))

# Import and run GUI
try:
    from gui_application import main
    print("🚀 Launching Yaoundé Compiler GUI...")
    print("📊 Interactive Analysis & Testing Interface")
    print("=" * 50)
    main()
except ImportError as e:
    print(f"❌ Error: Could not import required modules\n{e}")
    print("\n💡 Make sure all source files are in place:")
    print("   - src/lexical_analyzer.py")
    print("   - src/parser.py")
    print("   - src/semantic_analyzer.py")
    print("   - tests/test_cases.py")
except Exception as e:
    print(f"❌ Error launching GUI:\n{e}")
    sys.exit(1)
