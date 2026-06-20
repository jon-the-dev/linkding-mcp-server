#!/bin/bash
# Script to build and publish to PyPI

set -e

echo "🏗️ Building package..."
python -m build

echo "📦 Checking distribution..."
twine check dist/*

echo "🚀 Upload to PyPI?"
echo "Run: twine upload dist/*"
echo ""
echo "For testing, upload to TestPyPI first:"
echo "twine upload --repository testpypi dist/*"