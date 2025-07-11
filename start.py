#!/usr/bin/env python3
"""
Startup script for iTrash unified system.
Provides different options for running the system.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    # Map package names to their import names
    package_mapping = {
        'opencv-python': 'cv2',
        'pymongo': 'pymongo',
        'python-dotenv': 'dotenv',
        'pillow': 'PIL',
        'requests': 'requests',
        'streamlit': 'streamlit',
        'plotly': 'plotly',
        'pandas': 'pandas',
        'numpy': 'numpy'
    }
    
    missing_packages = []
    
    for package, import_name in package_mapping.items():
        try:
            __import__(import_name)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r requirements.txt")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists"""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        print("Please create a .env file with the following variables:")
        print("MONGO_CONNECTION_STRING=your_mongodb_connection_string")
        print("MONGO_DB_NAME=your_database_name")
        print("OPENAI_API_KEY=your_openai_api_key")
        print("YOLO_API_KEY=your_yolo_api_key")
        return False
    
    print("✅ .env file found")
    return True

def check_images():
    """Check if display images exist"""
    images_dir = Path('display/images')
    if not images_dir.exists():
        print("❌ Display images directory not found")
        return False
    
    required_images = [
        'white.png',
        'processing_new.png',
        'show_trash.png',
        'try_again_green.png',
        'great_job.png',
        'qr_codes.png',
        'reward_received_new.png'
    ]
    
    missing_images = []
    for image in required_images:
        if not (images_dir / image).exists():
            missing_images.append(image)
    
    if missing_images:
        print(f"❌ Missing images: {', '.join(missing_images)}")
        return False
    
    print("✅ Display images found")
    return True

def run_tests():
    """Run system tests"""
    print("Running system tests...")
    result = subprocess.run([sys.executable, 'test_system.py'], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ All tests passed")
        return True
    else:
        print("❌ Some tests failed")
        print(result.stdout)
        print(result.stderr)
        return False

def start_main_system():
    """Start the main iTrash system"""
    print("Starting main iTrash system...")
    subprocess.run([sys.executable, 'main.py'])

def start_display_only():
    """Start only the display interface"""
    print("Starting display interface only...")
    subprocess.run([sys.executable, 'display/media_display.py'])

def start_analytics():
    """Start the analytics dashboard"""
    print("Starting analytics dashboard...")
    subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'analytics/dashboard.py'])

def start_camera_test():
    """Start camera test"""
    print("Starting camera test...")
    # This would need to be implemented or use existing test
    subprocess.run([sys.executable, 'test_system.py'])

def main():
    """Main startup function"""
    parser = argparse.ArgumentParser(description='iTrash System Startup')
    parser.add_argument('--mode', choices=['main', 'display', 'analytics', 'test', 'check'], 
                       default='check', help='Mode to run')
    parser.add_argument('--skip-checks', action='store_true', help='Skip dependency checks')
    
    args = parser.parse_args()
    
    print("🗑️  iTrash Unified System")
    print("=" * 40)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    if not args.skip_checks:
        print("\n🔍 Running pre-flight checks...")
        
        checks_passed = True
        checks_passed &= check_dependencies()
        checks_passed &= check_env_file()
        checks_passed &= check_images()
        
        if not checks_passed:
            print("\n❌ Pre-flight checks failed. Please fix the issues above.")
            return 1
    
    if args.mode == 'check':
        print("\n✅ All checks passed!")
        print("\nAvailable modes:")
        print("  main      - Start the complete iTrash system")
        print("  display   - Start only the display interface")
        print("  analytics - Start the analytics dashboard")
        print("  test      - Run system tests")
        return 0
    
    elif args.mode == 'test':
        return 0 if run_tests() else 1
    
    elif args.mode == 'main':
        if not args.skip_checks and not run_tests():
            print("❌ Tests failed. Use --skip-checks to bypass.")
            return 1
        start_main_system()
    
    elif args.mode == 'display':
        start_display_only()
    
    elif args.mode == 'analytics':
        start_analytics()
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 