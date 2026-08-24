#!/data/data/com.termux/files/usr/bin/bash

# =============================================
# LocBITE - Termux Dependencies Installer
# Advanced Photo Forensics Tool
# Author: SYLHETYHACKVENGER (THE-ERROR808)
# =============================================

# Colors
RED='\033[1;91m'
GREEN='\033[1;92m'
YELLOW='\033[1;93m'
BLUE='\033[1;94m'
PURPLE='\033[1;95m'
CYAN='\033[1;96m'
WHITE='\033[1;97m'
ORANGE='\033[38;5;214m'
RESET='\033[0m'
BOLD='\033[1m'

# Print functions
print_status() { echo -e "${BLUE}[${BOLD}*${RESET}${BLUE}]${RESET} $1"; }
print_success() { echo -e "${GREEN}[${BOLD}✓${RESET}${GREEN}]${RESET} $1"; }
print_error() { echo -e "${RED}[${BOLD}✗${RESET}${RED}]${RESET} $1"; }
print_info() { echo -e "${CYAN}[${BOLD}i${RESET}${CYAN}]${RESET} $1"; }

clear
echo -e "${ORANGE}"
echo "    ╔═══════════════════════════════════════╗"
echo "    ║  🔍 LocBITE - Dependencies Installer  ║"
echo "    ╚═══════════════════════════════════════╝"
echo -e "${RESET}"
echo ""

# Check if running in Termux
if [ ! -d "/data/data/com.termux" ]; then
    echo -e "${RED}${BOLD}Error: This script is only for Termux on Android!${RESET}"
    exit 1
fi

# Update packages
print_status "Updating Termux packages..."
pkg update -y && pkg upgrade -y

# Install system packages
print_status "Installing system dependencies..."
pkg install -y python python-pip openssl tesseract tesseract-ocr zbar curl wget git

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python packages..."

# Core packages
print_status "Installing Pillow..."
pip install Pillow

print_status "Installing exifread..."
pip install exifread

print_status "Installing pyzbar..."
pip install pyzbar

print_status "Installing pytesseract..."
pip install pytesseract

print_status "Installing cryptography..."
pip install cryptography

print_status "Installing pycryptodome..."
pip install pycryptodome

print_status "Installing requests..."
pip install requests

print_status "Installing numpy..."
pip install numpy

print_status "Installing opencv-python-headless..."
pip install opencv-python-headless

print_status "Installing scikit-image..."
pip install scikit-image

# Additional utilities
print_status "Installing additional utilities..."
pip install matplotlib scipy pandas

# Setup Tesseract
print_status "Setting up Tesseract..."
export TESSDATA_PREFIX=$PREFIX/share/tessdata
mkdir -p $TESSDATA_PREFIX

if [ ! -f "$TESSDATA_PREFIX/eng.traineddata" ]; then
    print_info "Downloading English language data for Tesseract..."
    curl -L -o $TESSDATA_PREFIX/eng.traineddata https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata
fi

# Setup ZBar
print_status "Setting up ZBar..."
export PYTHONPATH=$PYTHONPATH:$PREFIX/lib/python3.11/site-packages

# Verify installations
echo ""
print_status "Verifying installations..."

# Check Python packages
packages=("PIL" "exifread" "pyzbar" "pytesseract" "cryptography" "Crypto" "requests" "numpy" "cv2" "skimage")
missing=()

for pkg in "${packages[@]}"; do
    if python -c "import $pkg" 2>/dev/null; then
        print_success "$pkg installed"
    else
        print_error "$pkg not installed"
        missing+=($pkg)
    fi
done

# Reinstall missing packages
if [ ${#missing[@]} -ne 0 ]; then
    print_info "Reinstalling missing packages..."
    for pkg in "${missing[@]}"; do
        case $pkg in
            "PIL") pip install Pillow ;;
            "exifread") pip install exifread ;;
            "pyzbar") pip install pyzbar ;;
            "pytesseract") pip install pytesseract ;;
            "cryptography") pip install cryptography ;;
            "Crypto") pip install pycryptodome ;;
            "requests") pip install requests ;;
            "numpy") pip install numpy ;;
            "cv2") pip install opencv-python-headless ;;
            "skimage") pip install scikit-image ;;
        esac
    done
fi

# Show summary
echo ""
echo -e "${GREEN}${BOLD}╔═══════════════════════════════════════════════════════════╗${RESET}"
echo -e "${GREEN}${BOLD}║      ✅ ALL DEPENDENCIES INSTALLED SUCCESSFULLY        ║${RESET}"
echo -e "${GREEN}${BOLD}╚═══════════════════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "${CYAN}${BOLD}📦 Installed Packages:${RESET}"
echo "  • Pillow (Image Processing)"
echo "  • exifread (EXIF Metadata)"
echo "  • pyzbar (QR/Barcode)"
echo "  • pytesseract (OCR)"
echo "  • cryptography (Encryption)"
echo "  • pycryptodome (Crypto)"
echo "  • requests (HTTP)"
echo "  • numpy (Numerical)"
echo "  • opencv-python (Computer Vision)"
echo "  • scikit-image (Image Processing)"
echo ""
echo -e "${YELLOW}${BOLD}📱 System Packages:${RESET}"
echo "  • python"
echo "  • openssl"
echo "  • tesseract-ocr"
echo "  • zbar"
echo ""
echo -e "${PURPLE}${BOLD}💡 Now you can run LocBITE:${RESET}"
echo "  python locbite.py"
echo ""
echo -e "${ORANGE}═══════════════════════════════════════════════════════════${RESET}"
echo -e "${GREEN}${BOLD}❤️  Made with love by SYLHETYHACKVENGER${RESET}"
echo -e "${CYAN}${BOLD}📱 Follow: @shv.cyberlab on Instagram${RESET}"
echo -e "${ORANGE}═══════════════════════════════════════════════════════════${RESET}"
