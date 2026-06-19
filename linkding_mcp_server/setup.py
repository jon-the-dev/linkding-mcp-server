#!/usr/bin/env python3
"""Interactive setup helper for the LinkDing MCP Server."""

import os
import subprocess
import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.12 or higher."""
    if sys.version_info < (3, 12):
        print("❌ Python 3.12 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "linkding-mcp-server"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def setup_environment():
    """Set up environment file interactively."""
    env_file = Path(".env")

    if env_file.exists():
        print("✅ .env file already exists")
        return True

    print("\n🔧 Setting up environment file...")
    print("Please provide the following information:")

    linkding_url = input("LinkDing URL (default: http://127.0.0.1:9090): ").strip()
    if not linkding_url:
        linkding_url = "http://127.0.0.1:9090"

    api_token = input("LinkDing API Token (required): ").strip()
    if not api_token:
        print("❌ API token is required")
        return False

    debug = input("Enable debug mode? (y/N): ").strip().lower()
    debug_value = "true" if debug in ["y", "yes"] else "false"

    content = (
        f"LINKDING_URL={linkding_url}\n"
        f"LINKDING_API_TOKEN={api_token}\n"
        f"DEBUG={debug_value}\n"
        "LINKDING_ENABLE_DESTRUCTIVE_ACTIONS=false\n"
    )

    env_file.write_text(content)
    print("✅ Environment file created")
    return True


def test_connection():
    """Test connection to the LinkDing server."""
    print("\n🔍 Testing connection to LinkDing server...")
    try:
        import httpx
        from dotenv import load_dotenv

        load_dotenv()

        linkding_url = os.getenv("LINKDING_URL", "http://127.0.0.1:9090")
        api_token = os.getenv("LINKDING_API_TOKEN")

        if not api_token:
            print("❌ API token not found in environment")
            return False

        with httpx.Client(
            base_url=f"{linkding_url.rstrip('/')}/api",
            headers={"Authorization": f"Token {api_token}"},
            timeout=10.0,
        ) as http:
            response = http.get("/tags/", params={"limit": 1})

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
        return True
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False


def main():
    """Run the interactive LinkDing MCP Server setup."""
    print("🚀 LinkDing MCP Server Setup")
    print("=" * 30)

    if not check_python_version():
        sys.exit(1)

    if not install_dependencies():
        sys.exit(1)

    if not setup_environment():
        sys.exit(1)

    test_connection()

    print("\n🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Run the server: linkding-mcp-server")
    print("2. Or: python -m linkding_mcp_server.server")
    print("\nFor Claude Desktop integration, see README.md")


if __name__ == "__main__":
    main()
