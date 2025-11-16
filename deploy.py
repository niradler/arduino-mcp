#!/usr/bin/env python3
"""
Arduino MCP Deployment Script

This script automates the process of building and publishing the package to PyPI.
"""

import re
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None):
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        cwd=cwd,
        encoding='utf-8',
        errors='ignore'
    )
    return result.returncode, result.stdout, result.stderr


def get_current_version():
    pyproject = Path("pyproject.toml")
    if not pyproject.exists():
        print("❌ pyproject.toml not found!")
        sys.exit(1)
    
    content = pyproject.read_text()
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if match:
        return match.group(1)
    return None


def get_pypi_token():
    pypirc = Path.home() / ".pypirc"
    if not pypirc.exists():
        print("❌ .pypirc not found in home directory!")
        return None
    
    content = pypirc.read_text()
    match = re.search(r'password\s*=\s*(.+)', content)
    if match:
        return match.group(1).strip()
    return None


def clean_dist():
    print("🧹 Cleaning old dist files...")
    dist_dir = Path("dist")
    if dist_dir.exists():
        current_version = get_current_version()
        for file in dist_dir.glob(f"arduino_mcp-{current_version}*"):
            file.unlink()
            print(f"   Removed: {file.name}")


def build_package():
    print("📦 Building package...")
    returncode, stdout, stderr = run_command("uv build")
    
    if returncode != 0:
        print(f"❌ Build failed!")
        print(stderr)
        return False
    
    print("✅ Build successful!")
    version = get_current_version()
    print(f"   Version: {version}")
    return True


def publish_package():
    print("🚀 Publishing to PyPI...")
    
    token = get_pypi_token()
    if not token:
        print("❌ Could not find PyPI token in .pypirc")
        return False
    
    version = get_current_version()
    
    cmd = f'uv publish --token "{token}" dist/arduino_mcp-{version}*'
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode != 0:
        print(f"❌ Publish failed!")
        print(stderr)
        return False
    
    print(f"✅ Published version {version} to PyPI!")
    print(f"   View at: https://pypi.org/project/arduino-mcp/{version}/")
    return True


def main():
    print("=" * 60)
    print("Arduino MCP Deployment Script")
    print("=" * 60)
    
    root_dir = Path(__file__).parent
    
    version = get_current_version()
    if not version:
        print("❌ Could not determine current version!")
        sys.exit(1)
    
    print(f"\n📌 Current version: {version}")
    
    response = input("\n❓ Continue with deployment? (y/n): ")
    if response.lower() != 'y':
        print("❌ Deployment cancelled.")
        sys.exit(0)
    
    print("\n" + "=" * 60)
    
    clean_dist()
    
    print("\n" + "=" * 60)
    
    if not build_package():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    
    if not publish_package():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 Deployment complete!")
    print("=" * 60)
    
    print("\n📝 Next steps:")
    print("   1. Test installation: pip install --upgrade arduino-mcp")
    print(f"   2. Check PyPI: https://pypi.org/project/arduino-mcp/{version}/")
    print("   3. Update documentation if needed")
    print("   4. Tag release in git: git tag v{version}")


if __name__ == "__main__":
    main()

