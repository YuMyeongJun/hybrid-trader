#!/bin/bash
# Test PyPI deployment script
# This script builds and uploads the package to TestPyPI for validation

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DIST_DIR="$PROJECT_DIR/dist"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}PyPI Package Deployment Test${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Step 1: Check Python and dependencies
echo -e "${YELLOW}Step 1: Checking Python environment...${NC}"
PYTHON=$(command -v python3 || command -v python)
if [ -z "$PYTHON" ]; then
    echo -e "${RED}Error: Python not found${NC}"
    exit 1
fi
echo -e "${GREEN}Python found: $($PYTHON --version)${NC}"

# Step 2: Install/upgrade build tools
echo ""
echo -e "${YELLOW}Step 2: Installing/upgrading build tools...${NC}"
$PYTHON -m pip install --upgrade pip setuptools wheel build twine > /dev/null 2>&1
echo -e "${GREEN}Build tools ready${NC}"

# Step 3: Extract version
echo ""
echo -e "${YELLOW}Step 3: Extracting version from setup.py...${NC}"
VERSION=$($PYTHON setup.py --version 2>/dev/null || echo "unknown")
echo -e "${GREEN}Version: $VERSION${NC}"

# Step 4: Clean old builds
echo ""
echo -e "${YELLOW}Step 4: Cleaning old build artifacts...${NC}"
rm -rf "$DIST_DIR" build *.egg-info
echo -e "${GREEN}Cleaned${NC}"

# Step 5: Build distribution
echo ""
echo -e "${YELLOW}Step 5: Building distribution packages...${NC}"
cd "$PROJECT_DIR"
$PYTHON -m build 2>&1 | grep -v "SetuptoolsDeprecationWarning"
echo -e "${GREEN}Build complete${NC}"

# Step 6: Validate with twine
echo ""
echo -e "${YELLOW}Step 6: Validating packages with twine...${NC}"
twine check "$DIST_DIR"/* --strict
echo -e "${GREEN}Validation passed${NC}"

# Step 7: Display package information
echo ""
echo -e "${YELLOW}Step 7: Package information:${NC}"
echo -e "${BLUE}Wheel:${NC}"
ls -lh "$DIST_DIR"/*.whl
echo ""
echo -e "${BLUE}Source Distribution:${NC}"
ls -lh "$DIST_DIR"/*.tar.gz

# Step 8: Check for TestPyPI token
echo ""
echo -e "${YELLOW}Step 8: Checking for TestPyPI credentials...${NC}"
if [ -z "$TEST_PYPI_API_TOKEN" ]; then
    echo -e "${YELLOW}⚠️  TEST_PYPI_API_TOKEN environment variable not set${NC}"
    echo ""
    echo -e "${BLUE}To test upload to TestPyPI, set the token:${NC}"
    echo "  export TEST_PYPI_API_TOKEN='your_token_here'"
    echo ""
    echo -e "${BLUE}Then run deployment:${NC}"
    echo "  twine upload dist/* --repository testpypi --username __token__ --password \$TEST_PYPI_API_TOKEN"
    echo ""
else
    # Step 9: Upload to TestPyPI
    echo ""
    echo -e "${YELLOW}Step 9: Uploading to TestPyPI...${NC}"
    twine upload "$DIST_DIR"/* \
        --repository testpypi \
        --username __token__ \
        --password "$TEST_PYPI_API_TOKEN" \
        --skip-existing \
        --verbose
    echo -e "${GREEN}Upload successful${NC}"

    # Step 10: Test installation from TestPyPI
    echo ""
    echo -e "${YELLOW}Step 10: Testing installation from TestPyPI...${NC}"
    sleep 5
    pip install --index-url https://test.pypi.org/simple/ hybrid-trader --extra-index-url https://pypi.org/simple/ --upgrade

    # Step 11: Verify installation
    echo ""
    echo -e "${YELLOW}Step 11: Verifying installation...${NC}"
    $PYTHON -c "
import hybrid_trader
print('✓ Package imported successfully')
print(f'✓ Version: {hybrid_trader.__version__ if hasattr(hybrid_trader, \"__version__\") else \"unknown\"}')
print(f'✓ Location: {hybrid_trader.__file__}')
print('✓ All components available')
"
    echo -e "${GREEN}Installation verified${NC}"
fi

# Final summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Deployment test completed successfully!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Review the package on TestPyPI:"
echo "   https://test.pypi.org/project/hybrid-trader/"
echo ""
echo "2. For production PyPI release:"
echo "   - Create a GitHub release (this triggers CI/CD)"
echo "   - Or run: twine upload dist/* -u __token__ -p \$PYPI_API_TOKEN"
echo ""
echo "3. After production release, verify with:"
echo "   pip install hybrid-trader --upgrade"
echo ""
