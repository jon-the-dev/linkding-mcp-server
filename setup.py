#!/usr/bin/env python3
"""
Setup script for LinkDing MCP Server

This script helps users set up the LinkDing MCP server quickly.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.12 or higher"""
    if sys.version_info < (3, 12):
        print("❌ Python 3.12 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Set up environment file"""
    env_file = Path(".env")
    env_sample = Path(".env.sample")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_sample.exists():
        print("❌ .env.sample file not found")
        return False
    
    print("\n🔧 Setting up environment file...")
    
    # Copy sample to .env
    with open(env_sample, 'r') as f:
        content = f.read()
    
    print("Please provide the following information:")
    
    # Get LinkDing URL
    linkding_url = input("LinkDing URL (default: http://127.0.0.1:9090): ").strip()
    if not linkding_url:
        linkding_url = "http://127.0.0.1:9090"
    
    # Get API token
    api_token = input("LinkDing API Token (required): ").strip()
    if not api_token:
        print("❌ API token is required")
        return False
    
    # Get debug setting
    debug = input("Enable debug mode? (y/N): ").strip().lower()
    debug_value = "true" if debug in ['y', 'yes'] else "false"
    
    # Replace placeholders
    content = content.replace("http://127.0.0.1:9090", linkding_url)
    content = content.replace("your_api_token_here", api_token)
    content = content.replace("false", debug_value)
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ Environment file created")
    return True

def test_connection():
    """Test connection to LinkDing server"""
    print("\n🔍 Testing connection to LinkDing server...")
    try:
        # Import here to avoid issues if dependencies aren't installed yet
        import httpx
        from dotenv import load_dotenv
        
        load_dotenv()
        
        linkding_url = os.getenv("LINKDING_URL", "http://127.0.0.1:9090")
        api_token = os.getenv("LINKDING_API_TOKEN")
        
        if not api_token:
            print("❌ API token not found in environment")
            return False
        
        # Test API connection
        with httpx.Client(
            base_url=f"{linkding_url.rstrip('/')}/api",
            headers={"Authorization": f"Token {api_token}"},
            timeout=10.0
        ) as client:
            response = client.get("/tags/", params={"limit": 1})
            
            if response.status_code == 200:
                print("✅ Successfully connected to LinkDing server")
                return True
            elif response.status_code == 401:
                print("❌ Authentication failed - check your API token")
                return False
            else:
                print(f"❌ Connection failed with status {response.status_code}")
                return False
                
    except ImportError:
        print("⚠️  Cannot test connection - dependencies not installed")
        return True  # Don't fail setup for this
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 LinkDing MCP Server Setup")
    print("=" * 30)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Test connection
    test_connection()
    
    print("\n🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Run the server: python linkding_server.py")
    print("2. Or use FastMCP CLI: fastmcp run linkding_server.py")
    print("3. Test with: python test_server.py")
    print("\nFor Claude Desktop integration, see README.md")

if __name__ == "__main__":
    main()
