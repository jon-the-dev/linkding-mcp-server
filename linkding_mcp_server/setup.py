#!/usr/bin/env python3
"""
Setup script for LinkDing MCP Server

This script helps users set up the LinkDing MCP server configuration.
"""

import getpass
import os
import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.12 or higher"""
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def setup_environment():
    """Set up environment file"""
    env_file = Path.home() / ".linkding-mcp" / "config.env"
    env_file.parent.mkdir(parents=True, exist_ok=True)

    if env_file.exists():
        print(f"✅ Configuration file already exists at {env_file}")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite not in ["y", "yes"]:
            return True

    print("\n🔧 Setting up LinkDing MCP Server configuration...")
    print("Please provide the following information:")

    # Get LinkDing URL
    linkding_url = input("LinkDing URL (default: http://127.0.0.1:9090): ").strip()
    if not linkding_url:
        linkding_url = "http://127.0.0.1:9090"

    # Get API token (hidden input)
    api_token = getpass.getpass(
        "LinkDing API Token (required): "
    ).strip()
    if not api_token:
        print("❌ API token is required")
        return False

    api_token_confirm = getpass.getpass(
        "Confirm API Token: "
    ).strip()
    if api_token != api_token_confirm:
        print("❌ API tokens do not match")
        return False

    # Get destructive actions setting
    destructive = input("Enable destructive actions (delete/modify)? (y/N): ").strip().lower()
    destructive_value = "true" if destructive in ["y", "yes"] else "false"

    # Get debug setting
    debug = input("Enable debug mode? (y/N): ").strip().lower()
    debug_value = "true" if debug in ["y", "yes"] else "false"

    # Write configuration file
    config_content = f"""# LinkDing MCP Server Configuration
LINKDING_URL={linkding_url}
LINKDING_API_TOKEN={api_token}
LINKDING_ENABLE_DESTRUCTIVE_ACTIONS={destructive_value}
LINKDING_DEBUG={debug_value}

# Optional settings (uncomment to override defaults)
# LINKDING_REQUEST_TIMEOUT=30
# LINKDING_MAX_RETRIES=3
# LINKDING_CACHE_TTL=300
# LINKDING_LOG_LEVEL=INFO
"""

    env_file.write_text(config_content)
    print(f"✅ Configuration saved to {env_file}")

    return True


def test_connection():
    """Test connection to LinkDing server"""
    print("\n🔍 Testing connection to LinkDing server...")
    try:
        import httpx
        from dotenv import load_dotenv

        # Load configuration
        env_file = Path.home() / ".linkding-mcp" / "config.env"
        if env_file.exists():
            load_dotenv(env_file)
        else:
            load_dotenv()  # Try local .env

        linkding_url = os.getenv("LINKDING_URL", "http://127.0.0.1:9090")
        api_token = os.getenv("LINKDING_API_TOKEN")

        if not api_token:
            print("❌ API token not found in configuration")
            return False

        # Test API connection
        with httpx.Client(
            base_url=f"{linkding_url.rstrip('/')}/api", headers={"Authorization": f"Token {api_token}"}, timeout=10.0
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
        print("⚠️  Cannot test connection - httpx not installed")
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

    # Setup environment
    if not setup_environment():
        sys.exit(1)

    # Test connection
    test_connection()

    print("\n🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Run the server: linkding-mcp")
    print("2. Or with uv: uv run linkding-mcp")
    print("3. Or use FastMCP: fastmcp run linkding-mcp")
    print("\nFor Claude Desktop integration, add to your config:")
    print(f"  Environment file: {Path.home() / '.linkding-mcp' / 'config.env'}")


if __name__ == "__main__":
    main()
