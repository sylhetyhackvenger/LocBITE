#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import re
import hashlib
import struct
import zlib
import base64
import binascii
import xml.etree.ElementTree as ET
import io
import json
import sqlite3
import shutil
import socket
import ssl
import urllib.request
import urllib.parse
import datetime
from datetime import datetime
from collections import Counter, defaultdict
import warnings
warnings.filterwarnings('ignore')

try:
    from PIL import Image, ImageStat, ImageFile, ImageChops, ImageFilter, ImageDraw, ImageEnhance
    from PIL.ExifTags import TAGS, GPSTAGS
except ImportError:
    print("Error: PIL/Pillow not installed. Install with: pip install pillow")
    sys.exit(1)

try:
    import exifread
    EXIFREAD_AVAILABLE = True
except ImportError:
    EXIFREAD_AVAILABLE = False
    print("[!] exifread not installed. Some EXIF features disabled.")
    print("[!] Install with: pip install exifread")

try:
    from pyzbar.pyzbar import decode as pyzbar_decode
    ZBAR_AVAILABLE = True
except ImportError:
    ZBAR_AVAILABLE = False
    print("[!] pyzbar not installed. QR/Barcode detection disabled.")
    print("[!] Install with: pip install pyzbar")

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("[!] pytesseract not installed. OCR features disabled.")
    print("[!] Install with: pip install pytesseract")

try:
    from cryptography.hazmat.primitives import hashes, padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
    CRYPTO_LIB_AVAILABLE = True
except ImportError:
    CRYPTO_LIB_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

ORANGE = "\033[38;5;214m"
GREEN = "\033[92m"
LIME = "\033[38;5;118m"
YELLOW = "\033[93m"
GOLD = "\033[38;5;220m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
PURPLE = "\033[38;5;135m"
RED = "\033[91m"
PINK = "\033[38;5;205m"
WHITE = "\033[97m"
BOLD = "\033[1m"
DIM = "\033[2m"
UNDERLINE = "\033[4m"
REVERSE = "\033[7m"
RESET = "\033[0m"

def style_header(text):
    return f"{BOLD}{CYAN}╔{'═' * 68}╗{RESET}\n{BOLD}{CYAN}║{RESET} {BOLD}{WHITE}{text:^66}{RESET} {BOLD}{CYAN}║{RESET}\n{BOLD}{CYAN}╚{'═' * 68}╝{RESET}"

def style_field(name, value):
    return f"  {BOLD}{GREEN}├─{RESET} {BOLD}{WHITE}{name}:{RESET} {YELLOW}{value}{RESET}"

def style_success(text):
    return f"{BOLD}{GREEN}✅ {text}{RESET}"

def style_warning(text):
    return f"{BOLD}{YELLOW}⚠️ {text}{RESET}"

def style_error(text):
    return f"{BOLD}{RED}❌ {text}{RESET}"

def style_info(text):
    return f"{BOLD}{BLUE}ℹ️ {text}{RESET}"

def style_value(text):
    return f"{BOLD}{LIME}{text}{RESET}"

def style_hash(text):
    return f"{BOLD}{PURPLE}{text}{RESET}"

def style_link(text):
    return f"{BOLD}{CYAN}{UNDERLINE}{text}{RESET}"

def style_critical(text):
    return f"{BOLD}{RED}{REVERSE} {text} {RESET}"

def style_high(text):
    return f"{BOLD}{PINK}{text}{RESET}"

def print_banner():
    banner = f"""
{ORANGE}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⣦⡀⠀⠀⢀⣴⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣤⡀⠀⠀⢀⣾⣷⣄⠀⢰⣿⣿⣿⣷⡀⢀⣾⣿⣿⣿⣆⠀⢠⣾⣷⡀⠀⠀⢀⣴⡀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣼⣿⣷⡀⠀⣾⣿⣿⣿⡆⣿⣿⣿⣿⣿⣧⣼⣿⣿⣿⣿⣿⢠⣿⣿⣿⣷⡀⢀⣾⣿⣧⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣿⣿⣿⣷⡀⣿⣿⣿⣿⣧⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣸⣿⣿⣿⣿⠀⣾⣿⣿⣿⠀⠀⠀⠀
⠀⠀⠀⣰⣶⣿⣿⣿⣿⣇⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣸⣿⣿⣿⣿⣶⣦⠀⠀
⠀⣀⡀⣿⣿⣿⣿⣿⣿⣿⢿⣿⣿⣿⣿⠝⠻⠿⠿⠿⠋⠙⠿⠿⠿⠟⠋⣿⣿⣿⣿⡿⣿⣿⣿⣿⣿⣿⣟⡀⠀
⠰⣿⣷⢸⣿⣿⣿⣿⣿⣿⠀⠙⠛⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠛⠋⠀⣿⣿⣿⣿⣿⣿⣿⣿⠄
⠀⠹⣿⣏⠛⠃⠘⢿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⠃⠘⠛⣿⡟⠀
⠀⠀⠈⠃⠀⠀⠀⠈⠻⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⠟⠁⠀⠀⠀⠈⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠁⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⣴⠀⠀⠀
⠀⠀⠀⢀⣿⣷⣾⣇⠀⠀⠀⠀⢀⣾⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣷⡀⠀⠀⠀⠀⠀⠀⣼⣿⠀⠀⠀
⠀⠀⠀⢸⣿⣿⣿⣿⣧⣠⡄⢠⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⡆⣰⣦⣤⠀⣼⣿⣿⡀⠀⠀
⠀⠀⠀⠀⠛⢻⣿⣿⣿⣿⡏⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⢸⣿⣿⡇⢿⣿⣿⠁⠀⠀
⠀⠀⠀⠀⠀⠈⢿⡿⣿⣿⡇⣿⣿⣿⣾⣷⣦⣤⠀⠀⣀⣀⠀⠀⣤⣴⣾⣷⣿⣿⣿⢸⣿⣿⠃⠀⠈⠁⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⡅⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢠⣿⡟⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⡇⣿⣿⣿⣽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣏⣿⣿⣿⠸⠏⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⠋⢿⣿⡟⢿⣿⣿⣿⣿⡿⠻⣿⡿⠙⣿⣿⡧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠃⠀⠈⠋⠀⠀⠻⠏⠸⠟⠀⠀⠙⠁⠀⠈⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{RESET}
{ORANGE}               ═══════════════════════════════════
               {BOLD}🔍 LocBITE - Advanced Photo Forensics{ORANGE}
               ═══════════════════════════════════{RESET}
{GREEN}{BOLD}               ⚡ Author : SYLHETYHACKVENGER (THE-ERROR808){RESET}
{CYAN}{BOLD}               ⚡ Description : Advanced Image Forensics & Metadata Extraction{RESET}
{YELLOW}{BOLD}               ⚡ Features : File Analysis, JPEG Forensics, Steganography, Metadata, GPS, Device Info, QR, OCR, ELA, WhatsApp{RESET}
{ORANGE}               ═══════════════════════════════════{RESET}
"""
    print(banner)

def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')

def lock_and_redirect():
    print(f"{style_info('📱 Follow My Instagram: @shv.cyberlab')}")
    print(f"{style_info('Redirecting to Instagram...')}\n")
    time.sleep(1)
    
    for i in range(5, 0, -1):
        sys.stdout.write(f"\r{BOLD}{MAGENTA}⏳ Redirecting in: {i}...{RESET}")
        sys.stdout.flush()
        time.sleep(1)
    print("\n")
    
    url = "https://instagram.com/shv.cyberlab"
    try:
        if sys.platform == "linux" and "com.termux" in os.environ.get("PREFIX", ""):
            subprocess.Popen(["am", "start", "-a", "android.intent.action.VIEW", "-d", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif sys.platform == "win32":
            os.system(f"start {url}")
        else:
            os.system(f"xdg-open {url}")
    except Exception:
        pass

    print(f"{BOLD}{BLUE}═{'═' * 68}═{RESET}")
    input(f"{style_success('Click ENTER to continue')}")
    clear_screen()

def convert_to_degrees(value):
    try:
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return d + (m / 60.0) + (s / 3600.0)
    except Exception:
        return None

def human_readable_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def verify_file_integrity(file_path):
    try:
        with open(file_path, 'rb') as f:
            header = f.read(32)
            
            jpeg_sigs = [b'\xff\xd8\xff\xe0', b'\xff\xd8\xff\xe1', b'\xff\xd8\xff\xe2', b'\xff\xd8\xff\xe3', b'\xff\xd8\xff\xdb', b'\xff\xd8\xff\xc4']
            for sig in jpeg_sigs:
                if header[:4] == sig:
                    return "JPEG/JPG Image"
            
            if header[:4] == b'\x89PNG':
                return "PNG Image"
            elif header[:3] == b'GIF':
                return "GIF Image"
            elif header[:2] == b'BM':
                return "BMP Image"
            elif header[:2] in [b'II', b'MM']:
                return "TIFF Image"
            elif header[:4] == b'RIFF':
                return "WebP Image"
            elif header[:4] == b'\x00\x00\x01\x00':
                return "ICO Icon"
            elif header[:4] == b'\x00\x00\x02\x00':
                return "CUR Cursor"
            return "Unknown File Type"
    except Exception:
        return "Unable to read file"

def calculate_hashes(file_path):
    hashes = {}
    hash_functions = {
        'MD5': hashlib.md5(),
        'SHA1': hashlib.sha1(),
        'SHA224': hashlib.sha224(),
        'SHA256': hashlib.sha256(),
        'SHA384': hashlib.sha384(),
        'SHA512': hashlib.sha512(),
        'BLAKE2b': hashlib.blake2b(),
        'BLAKE2s': hashlib.blake2s(),
        'SHA3_224': hashlib.sha3_224(),
        'SHA3_256': hashlib.sha3_256(),
        'SHA3_384': hashlib.sha3_384(),
        'SHA3_512': hashlib.sha3_512(),
    }
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(8192), b""):
                for algo in hash_functions.values():
                    algo.update(byte_block)
        for name, algo in hash_functions.items():
            hashes[name] = algo.hexdigest().upper()
        return hashes
    except Exception:
        return {name: "ERROR" for name in hash_functions}

def print_section_header(title):
    print(f"\n{BOLD}{BLUE}┌{'─' * 68}┐{RESET}")
    print(f"{BOLD}{BLUE}│{RESET} {BOLD}{YELLOW}▶ {title}{RESET}{' ' * (68 - len(title) - 6)}{BOLD}{BLUE}│{RESET}")
    print(f"{BOLD}{BLUE}└{'─' * 68}┘{RESET}")

def print_field(name, value):
    print(f"  {BOLD}{GREEN}├─{RESET} {BOLD}{WHITE}{name}:{RESET} {style_value(value)}")

def print_hash_field(name, value):
    print(f"  {BOLD}{GREEN}├─{RESET} {BOLD}{WHITE}{name}:{RESET} {style_hash(value)}")

def print_status(message):
    print(f"  {BOLD}{GREEN}├─{RESET} {message}")

def print_critical(name, value):
    print(f"  {BOLD}{RED}├─{RESET} {BOLD}{WHITE}{name}:{RESET} {style_critical(value)}")

def get_image_info(image_path):
    print_section_header("IMAGE INFORMATION")
    
    try:
        img = Image.open(image_path)
        
        print_field("Format", img.format or "Unknown")
        print_field("Size", f"{img.size[0]} x {img.size[1]} pixels")
        print_field("Mode", img.mode)
        
        if hasattr(img, 'info'):
            print_field("Additional Info", str(list(img.info.keys()))[:100])
        
    except Exception as e:
        print_field("Error", f"{RED}{str(e)}{RESET}")

def exif_check(image_path):
    print_section_header("EXIF/GPS METADATA")
    
    try:
        if not EXIFREAD_AVAILABLE:
            print_status(f"{style_warning('exifread not installed')}")
            print_field("Install", "pip install exifread")
            return
        
        with open(image_path, 'rb') as f:
            data = exifread.process_file(f)
        
        if not data:
            print_status(f"{style_warning('No EXIF found')}")
            return
        
        exif_keys = [
            'Make', 'Model', 'Software', 'DateTime', 'DateTimeOriginal',
            'GPSLatitude', 'GPSLongitude', 'GPSAltitude', 'GPSDateStamp',
            'GPSTimeStamp', 'ImageDescription', 'Artist', 'Copyright',
            'ExposureTime', 'FNumber', 'ISOSpeedRatings', 'FocalLength',
            'Flash', 'WhiteBalance', 'Orientation', 'ExposureProgram',
            'MeteringMode', 'ExposureBiasValue', 'CompressedBitsPerPixel',
            'DigitalZoomRatio', 'ExifVersion', 'ColorSpace', 'SensingMethod',
            'SceneCaptureType', 'GainControl', 'Contrast', 'Saturation',
            'Sharpness', 'SubjectDistanceRange'
        ]
        
        found = False
        for key, value in data.items():
            for k in exif_keys:
                if k in key:
                    print_field(key, value)
                    found = True
                    break
        
        if not found:
            print_status(f"{style_warning('No EXIF data found')}")
        
    except Exception as e:
        print_field("Error", f"{RED}{str(e)}{RESET}")

def camera_check(image_path):
    print_section_header("CAMERA INFORMATION")
    
    try:
        if not EXIFREAD_AVAILABLE:
            print_status(f"{style_warning('exifread not installed')}")
            return
        
        with open(image_path, 'rb') as f:
            data = exifread.process_file(f)
        
        found = False
        for key, value in data.items():
            if 'Make' in key or 'Model' in key:
                print_field(key.replace('EXIF ', ''), value)
                found = True
        
        if not found:
            print_status(f"{style_warning('Camera information removed or not available')}")
        
    except Exception as e:
        print_field("Error", f"{RED}{str(e)}{RESET}")

def qr_check(image_path):
    print_section_header("QR CODE & BARCODE DETECTION")
    
    try:
        if not ZBAR_AVAILABLE:
            print_status(f"{style_warning('pyzbar not installed')}")
            print_field("Install", "pip install pyzbar")
            return
        
        img = Image.open(image_path)
        decoded = pyzbar_decode(img)
        
        if decoded:
            print_status(f"{style_success(f'Found {len(decoded)} codes')}")
            for i, code in enumerate(decoded):
                print_field(f"Code {i+1}", f"Type: {code.type}, Data: {code.data.decode('utf-8')[:100]}")
        else:
            print_status(f"{style_info('No QR codes or barcodes detected')}")
        
    except Exception as e:
        print_field("Error", f"{RED}{str(e)}{RESET}")

def ocr_check(image_path):
    print_section_header("OCR TEXT EXTRACTION")
    
    try:
        if not TESSERACT_AVAILABLE:
            print_status(f"{style_warning('pytesseract not installed')}")
            print_field("Install", "pip install pytesseract")
            return
        
        text = pytesseract.image_to_string(Image.open(image_path))
        
        if text.strip():
            print_status(f"{style_success('Text extracted')}")
            print_field("Text Length", len(text))
            print(f"\n  {BOLD}{CYAN}Extracted Text:{RESET}")
            print(f"  {WHITE}{text[:500]}{RESET}")
            if len(text) > 500:
                print(f"  {DIM}... ({len(text)-500} more characters){RESET}")
        else:
            print_status(f"{style_info('No text detected')}")
        
    except Exception as e:
        print_field("Error", f"{RED}{str(e)}{RESET}")

def ela_check(image_path):
    print_section_header("ERROR LEVEL ANALYSIS (TAMPERING DETECTION)")
    
    try:
        img = Image.open(image_path).convert('RGB')
        temp_path = "tmp_quality.jpg"
        img.save(temp_path, quality=95)
        
        comp = Image.open(temp_path)
        ela = ImageChops.difference(img, comp)
        
        extrema = ela.getextrema()
        if extrema and len(extrema) >= 3:
            level = max(x[1] for x in extrema[:3])
        else:
            level = 0
        
        print_field("Difference Level", f"{level:.2f}")
        
        if level > 50:
            print_status(f"{style_critical('High difference - Possible tampering detected!')}")
        elif level > 20:
            print_status(f"{style_warning('Medium difference - Possible editing detected')}")
        else:
            print_status(f"{style_success('Low difference - Likely original image')}")
        
        ela = ImageEnhance.Brightness(ela).enhance(10)
        ela_file = f"ELA_result_{int(time.time())}.jpg"
        ela.save(ela_file)
        print_status(f"{style_info(f'ELA result saved: {ela_file}')}")
        
        os.remove(temp_path)
        
    except Exception as e:
        print_field("Error", f"{RED}{str(e)}{RESET}")

def social_check(image_path):
    print_section_header("SOCIAL MEDIA CLUES")
    
    try:
        img = Image.open(image_path)
        w, h = img.size
        
        print_field("Resolution", f"{w} x {h}")
        
        social_resolutions = {
            (640, 640): "Instagram Square",
            (1080, 1080): "Instagram Square (HD)",
            (1080, 1350): "Instagram Portrait",
            (1080, 1920): "Instagram Story",
            (720, 1280): "Snapchat/WhatsApp Portrait",
            (1280, 720): "WhatsApp Landscape",
            (1080, 1080): "Facebook Square",
            (1200, 630): "Facebook Link Preview",
            (820, 360): "Twitter Card",
            (1024, 1024): "Telegram Square",
        }
        
        found = False
        for res, name in social_resolutions.items():
            if (w, h) == res:
                print_field("Possible Platform", f"{name} ({res[0]}x{res[1]})")
                found = True
                break
        
        if not found:
            print_status(f"{style_info('No specific social media pattern detected')}")
            print_field("Note", "Could still be from social media with custom dimensions")
        
        print(f"\n  {BOLD}{YELLOW}Common Social Media Resolutions:{RESET}")
        print(f"  {CYAN}• Instagram: 1080x1080, 1080x1350, 1080x1920{RESET}")
        print(f"  {CYAN}• WhatsApp: 720x1280, 1280x720{RESET}")
        print(f"  {CYAN}• Facebook: 1080x1080, 1200x630{RESET}")
        print(f"  {CYAN}• Twitter: 820x360{RESET}")
        print(f"  {CYAN}• Telegram: 1024x1024{RESET}")
        
    except Exception as e:
        print_field("Error", f"{RED}{str(e)}{RESET}")

def timeline_check(image_path):
    print_section_header("FILE TIMELINE")
    
    try:
        stat = os.stat(image_path)
        
        created = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        accessed = datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%d %H:%M:%S')
        
        print_field("Created", created)
        print_field("Modified", modified)
        print_field("Accessed", accessed)
        
    except Exception as e:
        print_field("Error", f"{RED}{str(e)}{RESET}")

def whatsapp_scan():
    print_section_header("WHATSAPP SCAN")
    
    locations = [
        "/sdcard/Android/media/com.whatsapp/WhatsApp/Media",
        "/data/data/com.whatsapp/databases",
        "/sdcard/WhatsApp/Media",
        "/storage/emulated/0/WhatsApp/Media",
    ]
    
    found = False
    for loc in locations:
        if os.path.exists(loc):
            print_status(f"{style_success(f'Found: {loc}')}")
            found = True
        else:
            print_status(f"{style_warning(f'Missing: {loc}')}")
    
    if not found:
        print_status(f"{style_info('No WhatsApp directories found')}")

def whatsapp_database():
    print_section_header("WHATSAPP DATABASE")
    
    db_paths = [
        "/data/data/com.whatsapp/databases/msgstore.db",
        "/sdcard/WhatsApp/Databases/msgstore.db",
        "/storage/emulated/0/WhatsApp/Databases/msgstore.db",
    ]
    
    found = False
    for db in db_paths:
        if os.path.exists(db):
            print_status(f"{style_success('Database found')}")
            print_field("Path", db)
            found = True
            
            try:
                conn = sqlite3.connect(db)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                print_field("Tables", f"{len(tables)} tables found")
                for table in tables[:5]:
                    print(f"  {BOLD}{CYAN}├─{RESET} {WHITE}{table[0]}{RESET}")
                conn.close()
            except Exception as e:
                print_field("Error", f"{RED}{str(e)}{RESET}")
            break
    
    if not found:
        print_status(f"{style_warning('WhatsApp database not found')}")
        print_field("Note", "Need root permission or database unavailable")

def extract_all_device_info(image_path):
    print_section_header("COMPLETE DEVICE INFORMATION")
    
    try:
        with open(image_path, 'rb') as f:
            data = f.read()
        
        print("\n  {BOLD}{CYAN}◆ Network Information{RESET}")
        ip_pattern = re.compile(rb'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
        ips = ip_pattern.findall(data)
        if ips:
            for ip in ips[:3]:
                print(f"  {BOLD}{GREEN}├─{RESET} {WHITE}IP Address: {ip.decode()}{RESET}")
        else:
            print(f"  {BOLD}{YELLOW}├─{RESET} {WHITE}No IP data found{RESET}")
        
        mac_pattern = re.compile(rb'([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})')
        macs = mac_pattern.findall(data)
        if macs:
            for mac in macs[:3]:
                print(f"  {BOLD}{GREEN}├─{RESET} {WHITE}MAC Address: {':'.join(mac)}{RESET}")
        
        print("\n  {BOLD}{CYAN}◆ Device Information{RESET}")
        imei_pattern = re.compile(rb'\b[0-9]{15}\b')
        imeis = imei_pattern.findall(data)
        if imeis:
            for imei in imeis[:3]:
                print(f"  {BOLD}{GREEN}├─{RESET} {WHITE}IMEI: {imei.decode()}{RESET}")
        
        phone_pattern = re.compile(rb'\+?[0-9]{10,15}')
        phones = phone_pattern.findall(data)
        if phones:
            for phone in phones[:3]:
                print(f"  {BOLD}{GREEN}├─{RESET} {WHITE}Phone Number: {phone.decode()}{RESET}")
        
        email_pattern = re.compile(rb'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        emails = email_pattern.findall(data)
        if emails:
            for email in emails[:3]:
                print(f"  {BOLD}{GREEN}├─{RESET} {WHITE}Email: {email.decode('utf-8', errors='ignore')}{RESET}")
        
        print("\n  {BOLD}{CYAN}◆ Operating System{RESET}")
        android_pattern = re.compile(rb'Android [0-9]')
        android = android_pattern.findall(data)
        if android:
            for a in android[:3]:
                print(f"  {BOLD}{GREEN}├─{RESET} {WHITE}Android Version: {a.decode('utf-8', errors='ignore')}{RESET}")
        
        ios_pattern = re.compile(rb'iOS [0-9]')
        ios = ios_pattern.findall(data)
        if ios:
            for i in ios[:3]:
                print(f"  {BOLD}{GREEN}├─{RESET} {WHITE}iOS Version: {i.decode('utf-8', errors='ignore')}{RESET}")
        
        print("\n  {BOLD}{CYAN}◆ Application Information{RESET}")
        apps = {
            b'com.whatsapp': 'WhatsApp',
            b'com.instagram': 'Instagram',
            b'com.facebook': 'Facebook',
            b'org.telegram': 'Telegram',
            b'org.thoughtcrime': 'Signal',
            b'com.snapchat': 'Snapchat',
            b'com.twitter': 'Twitter',
            b'com.linkedin': 'LinkedIn',
        }
        for pattern, name in apps.items():
            if pattern in data:
                print(f"  {BOLD}{GREEN}├─{RESET} {WHITE}Application: {name}{RESET}")
                break
        
    except Exception as e:
        print_field("Error", f"{RED}{str(e)}{RESET}")

def analyze_jpeg_quality(image_path):
    print_section_header("ADVANCED JPEG COMPRESSION FORENSICS")
    
    try:
        with open(image_path, 'rb') as f:
            data = f.read()
        
        if not data.startswith(b'\xff\xd8'):
            print_field("Status", "⚠️ Not a JPEG file")
            return
        
        pos = 0
        quality_found = False
        quantization_tables = []
        markers_found = []
        
        while pos < len(data) - 1:
            if data[pos] == 0xFF:
                marker = data[pos+1]
                markers_found.append(hex(marker))
                
                if marker == 0xDB:
                    length = struct.unpack('>H', data[pos+2:pos+4])[0]
                    table_data = data[pos+4:pos+4+length-2]
                    
                    if table_data and len(table_data) > 1:
                        table_type = "Luminance" if (table_data[0] & 0xF0) == 0x00 else "Chrominance"
                        table_values = list(table_data[1:65]) if len(table_data) > 65 else list(table_data[1:])
                        
                        if table_values:
                            avg = sum(table_values) / len(table_values)
                            if avg < 5:
                                quality = f"{BOLD}{GREEN}100% (Lossless-like){RESET}"
                            elif avg < 10:
                                quality = f"{BOLD}{LIME}95% (Premium){RESET}"
                            elif avg < 15:
                                quality = f"{BOLD}{GREEN}90% (Excellent){RESET}"
                            elif avg < 25:
                                quality = f"{BOLD}{YELLOW}80% (Good){RESET}"
                            elif avg < 35:
                                quality = f"{BOLD}{YELLOW}70% (Standard){RESET}"
                            elif avg < 50:
                                quality = f"{BOLD}{ORANGE}60% (Low){RESET}"
                            elif avg < 75:
                                quality = f"{BOLD}{RED}50% (Very Low){RESET}"
                            else:
                                quality = f"{BOLD}{RED}Below 50% (Extremely Low){RESET}"
                            
                            quantization_tables.append({
                                'type': table_type,
                                'quality': quality,
                                'avg': avg,
                                'values': table_values[:10]
                            })
                            quality_found = True
                
                pos += 1
            pos += 1
        
        if quality_found:
            print_field("Status", f"{BOLD}{GREEN}JPEG analysis complete{RESET}")
            for i, table in enumerate(quantization_tables):
                print_field(f"{table['type']} Quality", table['quality'])
                print_field(f"{table['type']} Avg Value", f"{table['avg']:.2f}")
        
        print_field("Total Markers", len(markers_found))
            
    except Exception as e:
        print_field("Error", f"{RED}{str(e)}{RESET}")

def detect_file_type(data):
    """Detect file type from binary data"""
    signatures = {
        b'\x89PNG': 'PNG Image',
        b'\xff\xd8': 'JPEG Image',
        b'GIF': 'GIF Image',
        b'BM': 'BMP Image',
        b'PK\x03\x04': 'ZIP Archive',
        b'%PDF': 'PDF Document',
        b'RIFF': 'WebP/RIFF',
        b'II': 'TIFF Image',
        b'MM': 'TIFF Image',
        b'\x00\x00\x01\x00': 'ICO Icon',
        b'{\\rtf': 'RTF Document',
        b'<?xml': 'XML Document',
        b'<html': 'HTML Document',
        b'<!DOCTYPE': 'HTML Document',
        b'#!': 'Script File',
        b'JFIF': 'JPEG (JFIF)',
        b'Exif': 'JPEG with EXIF',
        b'ID3': 'MP3 Audio',
        b'OggS': 'OGG Audio',
        b'fLaC': 'FLAC Audio',
        b'FORM': 'Audio File',
        b'MP+': 'MP3+',
        b'MDAT': 'QuickTime/MP4',
        b'ftyp': 'MP4/QuickTime',
        b'MOOV': 'MP4/QuickTime',
        b'\x1f\x8b': 'GZIP Archive',
        b'BZh': 'BZIP2 Archive',
        b'7z': '7-ZIP Archive',
        b'Rar!': 'RAR Archive',
        b'PK': 'ZIP/Archive',
    }
    
    for sig, name in signatures.items():
        if data.startswith(sig):
            return name
    return None

def analyze_file_append(image_path):
    print_section_header("FILE APPEND & HIDDEN DATA DETECTION")
    
    try:
        with open(image_path, 'rb') as f:
            data = f.read()
        
        # Multiple EOF markers to check
        eof_markers = [
            (b'\xff\xd9', 'JPEG'),
            (b'IEND', 'PNG'),
            (b'\x00;', 'GIF'),
            (b'\xff\xd8', 'JPEG (Alternative)'),
            (b'<\\?xml', 'XML'),
            (b'</html>', 'HTML'),
            (b'</body>', 'HTML'),
            (b'%PDF', 'PDF'),
            (b'PK\x03\x04', 'ZIP'),
            (b'\x1f\x8b', 'GZIP'),
            (b'BZh', 'BZIP2'),
            (b'7z\xbc\xaf', '7ZIP'),
            (b'Rar!', 'RAR'),
            (b'\x00\x00\x00\x00', 'NULL Terminator'),
        ]
        
        appended_found = False
        all_appends = []
        
        # Check each marker
        for marker, name in eof_markers:
            if marker in data:
                # Find all occurrences of this marker
                start_pos = 0
                while True:
                    pos = data.find(marker, start_pos)
                    if pos == -1:
                        break
                    
                    end_pos = pos + len(marker)
                    if name == 'PNG':
                        end_pos = pos + 12
                    
                    if end_pos < len(data):
                        appended_size = len(data) - end_pos
                        if appended_size > 10:  # Minimum size to consider
                            appended_data = data[end_pos:]
                            all_appends.append({
                                'marker': name,
                                'offset': pos,
                                'end_pos': end_pos,
                                'size': appended_size,
                                'data': appended_data
                            })
                            appended_found = True
                    start_pos = pos + 1
        
        if not appended_found:
            print_status(f"{style_success('No appended data found')}")
            return False, None
        
        # Sort by offset to show in order
        all_appends.sort(key=lambda x: x['offset'])
        
        # Show results for each appended data found
        print_status(f"{style_critical(f'Found {len(all_appends)} appended data segments')}")
        
        for idx, append in enumerate(all_appends):
            print(f"\n  {BOLD}{MAGENTA}─── Segment {idx+1}/{len(all_appends)} ───{RESET}")
            print_field("Marker Type", append['marker'])
            print_field("Offset", f"{append['offset']:,} bytes")
            print_field("End Position", f"{append['end_pos']:,} bytes")
            print_field("Appended Size", f"{append['size']:,} bytes")
            print_field("Hex Preview", f"{append['data'][:50].hex()}...")
            
            appended_data = append['data']
            
            # Try to detect data type
            file_type = detect_file_type(appended_data[:32])
            if file_type:
                print_field("Detected Type", file_type)
            else:
                # Check if it's text
                try:
                    text_preview = appended_data[:200].decode('utf-8', errors='ignore')
                    if len(text_preview.strip()) > 0:
                        print_field("Type", "Text/ASCII Data")
                    else:
                        print_field("Type", "Binary Data")
                except:
                    print_field("Type", "Binary Data")
            
            # UTF-8 text
            try:
                text = appended_data.decode('utf-8', errors='ignore')
                if text.strip() and len(text) > 10:
                    # Clean up the text for display
                    clean_text = text[:150].replace('\n', ' ').replace('\r', ' ')
                    print_field("UTF-8 Preview", f"{clean_text}...")
            except:
                pass
            
            # Latin-1 text
            try:
                latin1_text = appended_data.decode('latin-1', errors='ignore')
                if latin1_text.strip() and len(latin1_text) > 10:
                    clean_latin1 = latin1_text[:150].replace('\n', ' ').replace('\r', ' ')
                    print_field("Latin-1 Preview", f"{clean_latin1}...")
            except:
                pass
            
            # Check for base64
            try:
                ascii_text = appended_data.decode('ascii', errors='ignore')
                b64_matches = re.findall(r'[A-Za-z0-9+/]{30,}={0,2}', ascii_text)
                if b64_matches:
                    print_field("Base64 Found", f"{len(b64_matches)} segments")
                    for b64 in b64_matches[:2]:
                        try:
                            decoded = base64.b64decode(b64)
                            if len(decoded) > 10:
                                print_field("  Base64 Decoded", f"{decoded[:80]}...")
                        except:
                            pass
            except:
                pass
            
            # Check for zlib compression
            try:
                decompressed = zlib.decompress(appended_data)
                if len(decompressed) > 0:
                    print_field("zlib Decompressed", f"{len(decompressed):,} bytes")
                    try:
                        text = decompressed.decode('utf-8', errors='ignore')
                        if text.strip():
                            print_field("  Decompressed Text", f"{text[:100]}...")
                    except:
                        pass
            except:
                pass
            
            # Check for nested files
            nested_types = {
                b'\x89PNG': 'PNG Image',
                b'\xff\xd8': 'JPEG Image',
                b'GIF': 'GIF Image',
                b'PK\x03\x04': 'ZIP Archive',
                b'%PDF': 'PDF Document',
                b'\x1f\x8b': 'GZIP Archive',
            }
            nested_found = False
            for sig, name in nested_types.items():
                if appended_data.startswith(sig):
                    print_field("Nested File", f"{name} detected!")
                    nested_found = True
                    break
            
            if not nested_found and len(appended_data) > 1000:
                # Check for common file signatures anywhere in the appended data
                for sig, name in nested_types.items():
                    if sig in appended_data[:500]:
                        print_field("Nested File", f"{name} found inside!")
                        nested_found = True
                        break
            
            # Check for strings in the appended data
            string_pattern = re.compile(rb'[ -~]{10,}')
            strings = string_pattern.findall(appended_data[:500])
            if strings:
                print_field("Strings Found", f"{len(strings)}")
                for s in strings[:3]:
                    try:
                        text = s.decode('utf-8', errors='ignore')
                        if len(text.strip()) > 5:
                            print_field("  String", f"{text[:80]}...")
                    except:
                        pass
            
            # Check for URLs
            url_pattern = re.compile(rb'https?://[^\s<>"{}|\\^`\[\]]+', re.IGNORECASE)
            urls = url_pattern.findall(appended_data)
            if urls:
                print_field("URLs Found", f"{len(urls)}")
                for url in urls[:3]:
                    try:
                        print_field("  URL", url.decode('utf-8', errors='ignore'))
                    except:
                        pass
            
            # Check for emails
            email_pattern = re.compile(rb'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
            emails = email_pattern.findall(appended_data)
            if emails:
                print_field("Emails Found", f"{len(emails)}")
                for email in emails[:2]:
                    try:
                        print_field("  Email", email.decode('utf-8', errors='ignore'))
                    except:
                        pass
            
            # Check for phone numbers
            phone_pattern = re.compile(rb'\+?[0-9]{10,15}')
            phones = phone_pattern.findall(appended_data)
            if phones:
                print_field("Phone Numbers", f"{len(phones)}")
                for phone in phones[:2]:
                    try:
                        print_field("  Phone", phone.decode('utf-8', errors='ignore'))
                    except:
                        pass
        
        return True, all_appends
        
    except Exception as e:
        print_field("Error", f"{RED}{str(e)}{RESET}")
        return False, None

def extract_hidden_data(image_path):
    print_section_header("ADVANCED STEGANOGRAPHY & HIDDEN DATA EXTRACTION")
    
    try:
        with open(image_path, 'rb') as f:
            data = f.read()
        
        found = []
        hidden_results = []
        
        # Check EXIF metadata
        try:
            img = Image.open(image_path)
            exif = img._getexif()
            if exif:
                for tag_id, value in exif.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    if tag_name in ['UserComment', 'ImageDescription', 'Artist', 'Copyright']:
                        if isinstance(value, bytes):
                            try:
                                decoded = value.decode('utf-8', errors='ignore')
                                if len(decoded) > 5:
                                    found.append(f"📝 {tag_name}: {decoded[:150]}...")
                                    hidden_results.append({'type': 'EXIF', 'name': tag_name, 'data': decoded[:150]})
                            except:
                                pass
                        elif isinstance(value, str) and len(value) > 5:
                            found.append(f"📝 {tag_name}: {value[:150]}...")
                            hidden_results.append({'type': 'EXIF', 'name': tag_name, 'data': value[:150]})
        except:
            pass
        
        # Base64 detection
        b64_pattern = re.compile(r'[A-Za-z0-9+/]{30,}={0,2}')
        b64_matches = b64_pattern.findall(data.decode('latin-1', errors='ignore'))
        for match in b64_matches[:5]:
            try:
                decoded = base64.b64decode(match)
                if len(decoded) > 30:
                    try:
                        text = decoded.decode('utf-8', errors='ignore')
                        if len(text.strip()) > 10:
                            found.append(f"🔑 Base64 encoded: {text[:80]}...")
                            hidden_results.append({'type': 'Base64', 'data': text[:80]})
                            break
                    except:
                        pass
            except:
                pass
        
        # XOR detection
        xor_pattern = re.compile(rb'[\x00-\x08\x0b\x0c\x0e-\x1f]{20,}')
        xor_matches = xor_pattern.findall(data)
        for match in xor_matches[:3]:
            for key in range(256):
                try:
                    decoded = bytes([b ^ key for b in match[:100]])
                    if decoded.isprintable() and len(decoded) > 20:
                        text = decoded.decode('utf-8', errors='ignore')
                        if len(text.strip()) > 5:
                            found.append(f"🔐 XOR encrypted (Key: {key}): {text[:80]}...")
                            hidden_results.append({'type': 'XOR', 'key': key, 'data': text[:80]})
                            break
                except:
                    pass
            if hidden_results and hidden_results[-1].get('type') == 'XOR':
                break
        
        # Steganography detection - LSB analysis
        try:
            img = Image.open(image_path)
            if img.mode == 'RGB' or img.mode == 'RGBA':
                pixels = list(img.getdata())[:1000]
                lsb_bits = []
                for pixel in pixels:
                    if isinstance(pixel, tuple):
                        for channel in pixel[:3]:
                            lsb_bits.append(channel & 1)
                
                if len(lsb_bits) > 100:
                    # Check for patterns in LSB
                    bit_string = ''.join(str(b) for b in lsb_bits[:100])
                    # Check for ASCII characters
                    byte_chunks = [bit_string[i:i+8] for i in range(0, len(bit_string)-7, 8)]
                    ascii_chars = []
                    for chunk in byte_chunks:
                        try:
                            char = chr(int(chunk, 2))
                            if 32 <= ord(char) <= 126:
                                ascii_chars.append(char)
                        except:
                            pass
                    
                    if len(ascii_chars) > 20:
                        hidden_text = ''.join(ascii_chars)
                        found.append(f"🔍 LSB Steganography detected: {hidden_text[:80]}...")
                        hidden_results.append({'type': 'LSB', 'data': hidden_text[:80]})
        except:
            pass
        
        # Check for strings in file
        string_pattern = re.compile(rb'[ -~]{10,}')
        strings = string_pattern.findall(data)
        for s in strings[:10]:
            try:
                text = s.decode('utf-8', errors='ignore')
                if len(text.strip()) > 10 and not text.startswith('http'):
                    found.append(f"📄 Found string: {text[:80]}...")
                    hidden_results.append({'type': 'String', 'data': text[:80]})
            except:
                pass
        
        # Check for URLs
        url_pattern = re.compile(rb'https?://[^\s<>"{}|\\^`\[\]]+', re.IGNORECASE)
        urls = url_pattern.findall(data)
        for url in urls[:5]:
            try:
                text = url.decode('utf-8', errors='ignore')
                found.append(f"🌐 URL found: {text}")
                hidden_results.append({'type': 'URL', 'data': text})
            except:
                pass
        
        # Check for email addresses
        email_pattern = re.compile(rb'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        emails = email_pattern.findall(data)
        for email in emails[:5]:
            try:
                text = email.decode('utf-8', errors='ignore')
                found.append(f"✉️ Email found: {text}")
                hidden_results.append({'type': 'Email', 'data': text})
            except:
                pass
        
        # Check for phone numbers
        phone_pattern = re.compile(rb'\+?[0-9]{10,15}')
        phones = phone_pattern.findall(data)
        for phone in phones[:5]:
            try:
                text = phone.decode('utf-8', errors='ignore')
                found.append(f"📞 Phone: {text}")
                hidden_results.append({'type': 'Phone', 'data': text})
            except:
                pass
        
        if found:
            print_status(f"{style_high(f'Found {len(found)} hidden data artifacts')}")
            for item in found[:15]:
                print(f"  {BOLD}{CYAN}├─{RESET} {WHITE}{item}{RESET}")
            
            # Summary
            print(f"\n  {BOLD}{YELLOW}Hidden Data Summary:{RESET}")
            type_counts = Counter([item['type'] for item in hidden_results])
            for typ, count in type_counts.items():
                print(f"  {BOLD}{GREEN}├─{RESET} {WHITE}{typ}: {count} items{RESET}")
        else:
            print_status(f"{style_warning('No hidden data detected')}")
        
        return hidden_results
        
    except Exception as e:
        print_field("Error", f"{RED}{str(e)}{RESET}")
        return []

def analyze_encryption(image_path):
    print_section_header("ADVANCED ENCRYPTION DETECTION")
    
    try:
        with open(image_path, 'rb') as f:
            data = f.read()
        
        encryption = []
        
        crypt_patterns = [
            (b'TrueCrypt', 'TrueCrypt Volume'),
            (b'VeraCrypt', 'VeraCrypt Volume'),
            (b'-FVE-FS-', 'BitLocker Encrypted'),
            (b'BitLocker', 'BitLocker Encrypted'),
            (b'LUKS', 'LUKS Encrypted Partition'),
            (b'GPG', 'GPG Encrypted Data'),
            (b'PGP', 'PGP Encrypted Data'),
            (b'Salted__', 'OpenSSL Salted Encryption'),
            (b'AES', 'AES Encryption Marker'),
            (b'DES', 'DES/3DES Encryption Marker'),
            (b'RSA', 'RSA Encryption Marker'),
            (b'BEGIN PGP', 'PGP Message'),
            (b'BEGIN RSA', 'RSA Private Key'),
            (b'ENCRYPTED', 'Encrypted Content'),
            (b'----BEGIN', 'PGP/PKI Content'),
            (b'encrypted', 'Possible Encryption'),
        ]
        
        for sig, name in crypt_patterns:
            if sig in data:
                encryption.append(f"🔐 {name} detected")
        
        # Calculate entropy - FIXED
        entropy = 0
        if len(data) > 1000:
            freq = {}
            sample = data[:10000]
            for byte in sample:
                freq[byte] = freq.get(byte, 0) + 1
            sample_len = len(sample)
            import math
            for count in freq.values():
                p = count / sample_len
                if p > 0:
                    entropy -= p * math.log2(p)
            
            if entropy > 7.8:
                encryption.append(f"⚡ Very High entropy: {entropy:.3f} (Strong encryption)")
            elif entropy > 7.5:
                encryption.append(f"⚡ High entropy: {entropy:.3f} (Possible encryption)")
            elif entropy > 7.0:
                encryption.append(f"⚡ Medium entropy: {entropy:.3f} (May be compressed or encrypted)")
            else:
                encryption.append(f"📊 Normal entropy: {entropy:.3f} (Likely plaintext)")
        
        if encryption:
            print_status(f"{style_critical(f'Detected {len(encryption)} encryption signatures')}")
            for item in encryption:
                print(f"  {BOLD}{RED}├─{RESET} {WHITE}{item}{RESET}")
        else:
            print_status(f"{style_success('No encryption detected')}")
            
    except Exception as e:
        print_field("Error", f"{RED}{str(e)}{RESET}")

def analyze_forensic_artifacts(image_path):
    print_section_header("FORENSIC ARTIFACT ANALYSIS")
    
    try:
        with open(image_path, 'rb') as f:
            data = f.read()
        
        artifacts = []
        
        # Editing software
        if b'Edited' in data or b'edited' in data:
            artifacts.append("📝 Image has been edited")
        
        if b'Photoshop' in data or b'Lightroom' in data:
            artifacts.append("🎨 Adobe Creative Suite detected")
        
        if b'GIMP' in data:
            artifacts.append("🎨 GIMP editing detected")
        
        if b'Canon' in data:
            artifacts.append("📷 Canon camera detected")
        if b'NIKON' in data:
            artifacts.append("📷 Nikon camera detected")
        if b'SONY' in data:
            artifacts.append("📷 Sony camera detected")
        if b'FUJIFILM' in data:
            artifacts.append("📷 Fujifilm camera detected")
        if b'Panasonic' in data:
            artifacts.append("📷 Panasonic camera detected")
        if b'OLYMPUS' in data:
            artifacts.append("📷 Olympus camera detected")
        
        if b'AI' in data or b'Generated' in data:
            artifacts.append("🤖 AI/ML generated content detected")
        
        if b'Deepfake' in data:
            artifacts.append("⚠️ Deepfake marker detected")
        
        if b'Watermark' in data or b'watermark' in data:
            artifacts.append("©️ Watermark detected")
        
        if b'Copyright' in data or b'copyright' in data:
            artifacts.append("©️ Copyright information present")
        
        if b'Camera' in data:
            artifacts.append("📷 Camera metadata present")
        
        if b'Lens' in data:
            artifacts.append("🔭 Lens information present")
        
        if b'Flash' in data:
            artifacts.append("💡 Flash information present")
        
        if b'ISO' in data:
            artifacts.append("📊 ISO information present")
        
        if b'Exposure' in data:
            artifacts.append("⏱️ Exposure information present")
        
        # Social media traces
        if b'Instagram' in data:
            artifacts.append("📱 Instagram metadata detected")
        if b'Facebook' in data:
            artifacts.append("📱 Facebook metadata detected")
        if b'Twitter' in data:
            artifacts.append("🐦 Twitter metadata detected")
        if b'WhatsApp' in data:
            artifacts.append("💬 WhatsApp metadata detected")
        if b'Telegram' in data:
            artifacts.append("✈️ Telegram metadata detected")
        if b'Snapchat' in data:
            artifacts.append("👻 Snapchat metadata detected")
        
        # Compression artifacts
        if b'JFIF' in data:
            artifacts.append("📦 JPEG JFIF format")
        if b'Exif' in data:
            artifacts.append("📋 EXIF metadata present")
        if b'ICC_PROFILE' in data:
            artifacts.append("🎨 ICC Color Profile detected")
        
        if artifacts:
            print_field("Total Artifacts", f"{len(artifacts)}")
            for artifact in artifacts:
                print_field("Detection", artifact)
        else:
            print_status(f"{style_info('No forensic artifacts detected')}")
            
    except Exception as e:
        print_field("Error", f"{RED}{str(e)}{RESET}")

def deep_forensic(image_path):
    print_section_header("DEEP FORENSIC ANALYSIS")
    analyze_jpeg_quality(image_path)
    analyze_file_append(image_path)
    extract_hidden_data(image_path)
    analyze_encryption(image_path)
    analyze_forensic_artifacts(image_path)

def analyze_image(image_path):
    clear_screen()
    print_banner()
    print(f"\n{BOLD}{BLUE}═{'═' * 68}═{RESET}")
    print(f"{BOLD}{GREEN}📁 Analyzing: {YELLOW}{os.path.basename(image_path)}{RESET}")
    print(f"{BOLD}{BLUE}═{'═' * 68}═{RESET}")
    
    if not os.path.exists(image_path):
        print(f"\n{style_error('File not found!')}")
        return

    try:
        hashes = calculate_hashes(image_path)
        file_bytes = os.path.getsize(image_path)
        
        image = Image.open(image_path)
        width, height = image.size
        megapixels = round((width * height) / 1000000, 2)
        
        fmt = verify_file_integrity(image_path)
        
        def gcd(a, b):
            while b: a, b = b, a % b
            return a
        r_gcd = gcd(width, height)
        aspect = f"{int(width/r_gcd)}:{int(height/r_gcd)}"
        
        layout = "📱 Landscape" if width > height else "📱 Portrait"
        if width == height: layout = "📱 Square"
        
        cmode = image.mode
        depth_map = {
            "1": "Monochrome (1-bit)",
            "L": "Grayscale (8-bit)",
            "P": "Palette (8-bit)",
            "RGB": "True Color (24-bit)",
            "RGBA": "True Color + Alpha (32-bit)",
            "CMYK": "CMYK (32-bit)",
            "YCbCr": "YCbCr (24-bit)",
            "LAB": "LAB (24-bit)",
            "HSV": "HSV (24-bit)",
            "I": "Intensity (32-bit)",
            "F": "Float (32-bit)"
        }
        depth = depth_map.get(cmode, f"Custom ({cmode})")
        
        stats = ImageStat.Stat(image)
        means = stats.mean
        stdevs = stats.stddev
        
        if len(means) >= 3:
            r, g, b = means[0], means[1], means[2]
            mx = max(r, g, b)
            if mx == r:
                color = f"{BOLD}{RED}🔴 Warm/Red Tones{RESET}"
            elif mx == g:
                color = f"{BOLD}{GREEN}🟢 Green/Nature Tones{RESET}"
            else:
                color = f"{BOLD}{BLUE}🔵 Blue/Cool Tones{RESET}"
            
            avg_dev = sum(stdevs[:3]) / 3
            if avg_dev > 50:
                complexity = f"{BOLD}{YELLOW}High Detail & Complex Scene{RESET}"
            elif avg_dev > 25:
                complexity = f"{BOLD}{LIME}Medium Detail{RESET}"
            else:
                complexity = f"{BOLD}{GREEN}Smooth & Simple Scene{RESET}"
        else:
            color = f"{BOLD}{WHITE}⚫ Monochrome{RESET}"
            complexity = f"{BOLD}{CYAN}Grayscale Image{RESET}"
        
        filename = os.path.basename(image_path)
        lower = filename.lower()
        source = "📷 Original Camera Photo"
        if "whatsapp" in lower or lower.startswith("img-"):
            source = "📱 WhatsApp Image"
        elif "fb" in lower or "facebook" in lower:
            source = "📱 Facebook Image"
        elif "instagram" in lower or "ig_" in lower:
            source = "📱 Instagram Image"
        elif "screenshot" in lower:
            source = "🖥️ Screenshot"
        elif "download" in lower:
            source = "⬇️ Downloaded Image"
        elif "telegram" in lower or "tg_" in lower:
            source = "✈️ Telegram Image"
        elif "signal" in lower:
            source = "🔒 Signal Image"
        
        exif = image._getexif()
        exif_data = {}
        if exif:
            for tag, value in exif.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    gps = {}
                    for t in value:
                        sub = GPSTAGS.get(t, t)
                        gps[sub] = value[t]
                    exif_data[decoded] = gps
                else:
                    exif_data[decoded] = value
        
        time_taken = exif_data.get('DateTimeOriginal', exif_data.get('DateTime', '❌ Not Available'))
        brand = exif_data.get('Make', '❌ Not Available')
        model = exif_data.get('Model', '❌ Not Available')
        tz = exif_data.get('OffsetTimeOriginal', '❌ Not Available')
        lens = exif_data.get('LensModel', 'Standard')
        fnum = f"f/{exif_data.get('FNumber')}" if exif_data.get('FNumber') else '❌ Not Available'
        focal = f"{exif_data.get('FocalLength')} mm" if exif_data.get('FocalLength') else '❌ Not Available'
        iso = exif_data.get('ISOSpeedRatings', '❌ Not Available')
        exp = exif_data.get('ExposureTime', '❌ Not Available')
        
        flash = exif_data.get('Flash', 0)
        flash_status = "💡 Fired" if (flash & 1) else "💡 Did Not Fire"
        
        daynight = "❓ Unknown"
        if 'DateTime' in exif_data or 'DateTimeOriginal' in exif_data:
            try:
                ts = exif_data.get('DateTimeOriginal', exif_data.get('DateTime'))
                hour = int(ts.split()[1].split(':')[0])
                daynight = f"☀️ Day ({hour}:00)" if 6 <= hour < 18 else f"🌙 Night ({hour}:00)"
            except:
                pass
        
        orient = exif_data.get('Orientation', 1)
        angles = {
            1: "0° Normal",
            2: "0° Mirrored",
            3: "180°",
            4: "180° Mirrored",
            5: "90° Right Mirrored",
            6: "90° Right",
            7: "270° Left Mirrored",
            8: "270° Left"
        }
        angle = angles.get(orient, "Normal")
        
        print(f"\n{BOLD}{BLUE}┌{'═' * 68}┐{RESET}")
        print(f"{BOLD}{BLUE}│{RESET} {BOLD}{WHITE}{'📊 IMAGE INFORMATION':^66}{RESET} {BOLD}{BLUE}│{RESET}")
        print(f"{BOLD}{BLUE}└{'═' * 68}┘{RESET}")
        
        print(f"\n{BOLD}{GREEN}▶ FILE DETAILS{RESET}")
        print_field("Type", fmt)
        print_field("Size", f"{human_readable_size(file_bytes)} ({file_bytes:,} bytes)")
        print_field("Source", source)
        print_hash_field("MD5", hashes.get('MD5', 'ERROR'))
        print_hash_field("SHA1", hashes.get('SHA1', 'ERROR'))
        print_hash_field("SHA224", hashes.get('SHA224', 'ERROR'))
        print_hash_field("SHA256", hashes.get('SHA256', 'ERROR'))
        print_hash_field("SHA384", hashes.get('SHA384', 'ERROR'))
        print_hash_field("SHA512", hashes.get('SHA512', 'ERROR'))
        print_hash_field("BLAKE2b", hashes.get('BLAKE2b', 'ERROR'))
        print_hash_field("BLAKE2s", hashes.get('BLAKE2s', 'ERROR'))
        print_hash_field("SHA3-224", hashes.get('SHA3_224', 'ERROR'))
        print_hash_field("SHA3-256", hashes.get('SHA3_256', 'ERROR'))
        print_hash_field("SHA3-384", hashes.get('SHA3_384', 'ERROR'))
        print_hash_field("SHA3-512", hashes.get('SHA3_512', 'ERROR'))
        
        print(f"\n{BOLD}{GREEN}▶ IMAGE SPECS{RESET}")
        print_field("Resolution", f"{width}x{height} ({megapixels} MP)")
        print_field("Orientation", layout)
        print_field("Aspect Ratio", aspect)
        print_field("Color Depth", depth)
        print_field("Color Balance", color)
        print_field("Complexity", complexity)
        
        print(f"\n{BOLD}{GREEN}▶ CAMERA INFO{RESET}")
        print_field("Camera Angle", angle)
        print_field("Camera Brand", brand)
        print_field("Camera Model", model)
        print_field("Lens Type", lens)
        print_field("Aperture", fnum)
        print_field("Focal Length", focal)
        print_field("ISO", iso)
        print_field("Exposure Time", exp)
        print_field("Flash Status", flash_status)
        
        print(f"\n{BOLD}{GREEN}▶ TIME INFO{RESET}")
        print_field("Photo Taken", time_taken)
        print_field("Time Zone", tz)
        print_field("Day/Night", daynight)

        print(f"\n{BOLD}{BLUE}┌{'═' * 68}┐{RESET}")
        print(f"{BOLD}{BLUE}│{RESET} {BOLD}{WHITE}{'📍 LOCATION INFORMATION':^66}{RESET} {BOLD}{BLUE}│{RESET}")
        print(f"{BOLD}{BLUE}└{'═' * 68}┘{RESET}")
        
        maps_link = None
        gps_status = "❌ NO GPS DATA"
        
        if "GPSInfo" in exif_data:
            gps_info = exif_data["GPSInfo"]
            lat_val = gps_info.get("GPSLatitude")
            lat_ref = gps_info.get("GPSLatitudeRef")
            lon_val = gps_info.get("GPSLongitude")
            lon_ref = gps_info.get("GPSLongitudeRef")

            if lat_val and lat_ref and lon_val and lon_ref:
                lat = convert_to_degrees(lat_val)
                lon = convert_to_degrees(lon_val)
                if lat_ref != "N": lat = 0 - lat
                if lon_ref != "E": lon = 0 - lon
                
                gps_status = f"{BOLD}{GREEN}✅ GPS DATA FOUND{RESET}"
                maps_link = f"https://www.google.com/maps?q={lat},{lon}"
                
                print_status(f"{gps_status}")
                print_field("Latitude", f"{lat}° {lat_ref}")
                print_field("Longitude", f"{lon}° {lon_ref}")
                
                if "GPSAltitude" in gps_info:
                    print_field("Altitude", f"{gps_info['GPSAltitude']} meters")
                if "GPSDateStamp" in gps_info:
                    print_field("GPS Date", gps_info['GPSDateStamp'])
                if "GPSTimeStamp" in gps_info:
                    gps_time = gps_info['GPSTimeStamp']
                    if isinstance(gps_time, tuple) and len(gps_time) >= 3:
                        print_field("GPS Time", f"{int(gps_time[0]):02d}:{int(gps_time[1]):02d}:{int(gps_time[2]):02d}")
                
                print(f"\n  {BOLD}{YELLOW}├─{RESET} {BOLD}{YELLOW}📌 Google Maps Link:{RESET}")
                print(f"  {BOLD}{CYAN}├─{RESET} {style_link(maps_link)}")
            else:
                print_status(f"{style_warning('GPS DATA PARTIAL - Coordinates missing')}")
        else:
            print_status(f"{style_error('NO GPS DATA FOUND')}")
            print(f"  {BOLD}{BLUE}├─{RESET} {BOLD}{WHITE}💡 Why GPS might be missing:{RESET}")
            print(f"  {BOLD}{CYAN}├─{RESET} {DIM}• Location services were OFF when photo was taken{RESET}")
            print(f"  {BOLD}{CYAN}├─{RESET} {DIM}• Camera app didn't have GPS permission{RESET}")
            print(f"  {BOLD}{CYAN}├─{RESET} {DIM}• Image was compressed by social media apps{RESET}")
            print(f"  {BOLD}{CYAN}├─{RESET} {DIM}• EXIF data was manually stripped{RESET}")
            print(f"  {BOLD}{CYAN}└─{RESET} {DIM}• Photo was downloaded from the internet{RESET}")

        get_image_info(image_path)
        exif_check(image_path)
        camera_check(image_path)
        qr_check(image_path)
        ocr_check(image_path)
        ela_check(image_path)
        social_check(image_path)
        timeline_check(image_path)
        whatsapp_scan()
        whatsapp_database()
        extract_all_device_info(image_path)
        deep_forensic(image_path)

        report = f"LocBITE_Report_{os.path.splitext(filename)[0]}.txt"
        with open(report, 'w') as r:
            r.write("=" * 70 + "\n")
            r.write("              LocBITE FORENSIC REPORT              \n")
            r.write("=" * 70 + "\n\n")
            r.write(f"📁 File: {filename}\n")
            r.write(f"📷 Type: {fmt}\n")
            r.write(f"📏 Size: {human_readable_size(file_bytes)}\n")
            for name, val in hashes.items():
                r.write(f"🔍 {name}: {val}\n")
            r.write(f"📐 Resolution: {width}x{height}\n")
            r.write(f"📱 Orientation: {layout}\n")
            r.write(f"📷 Camera: {brand} {model}\n")
            r.write(f"⏰ Date: {time_taken}\n")
            r.write(f"📍 GPS: {gps_status}\n")
            if maps_link:
                r.write(f"🗺️ Google Maps: {maps_link}\n")
        
        print(f"\n{BOLD}{BLUE}┌{'═' * 68}┐{RESET}")
        print(f"{BOLD}{BLUE}│{RESET} {BOLD}{GREEN}📄 Report saved as: {style_value(report)}{' ' * (68 - len(report) - 22)}{BOLD}{BLUE}│{RESET}")
        print(f"{BOLD}{BLUE}└{'═' * 68}┘{RESET}")
        
        print(f"\n{style_success('Analysis Complete!')}")
        print(f"\n{YELLOW}Press ENTER to continue...{RESET}")
        input()

    except Exception as e:
        print(f"\n{style_error(f'Error: {str(e)}')}")
        print(f"\n{YELLOW}Press ENTER to continue...{RESET}")
        input()

def find_image(image_name):
    paths = [
        "/sdcard/DCIM/Camera/",
        "/sdcard/DCIM/",
        "/sdcard/Pictures/",
        "/sdcard/Download/",
        "/sdcard/WhatsApp/Media/WhatsApp Images/",
        "/sdcard/WhatsApp/Media/WhatsApp Video/",
        "/sdcard/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Images/",
        "/storage/emulated/0/DCIM/Camera/",
        "/storage/emulated/0/Pictures/",
        "/storage/emulated/0/Download/",
        "/storage/emulated/0/WhatsApp/Media/WhatsApp Images/",
        "/storage/emulated/0/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Images/",
        os.path.expanduser("~/Pictures/"),
        os.path.expanduser("~/Downloads/"),
        os.path.expanduser("~/Desktop/"),
        os.path.expanduser("~/Documents/"),
        "./",
        "",
    ]
    
    exts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.ico', '.cur']
    
    for path in paths:
        full = os.path.join(path, image_name)
        if os.path.exists(full):
            return full
        if not any(image_name.lower().endswith(ext) for ext in exts):
            for ext in exts:
                test = os.path.join(path, image_name + ext)
                if os.path.exists(test):
                    return test
    
    if os.path.exists(image_name):
        return image_name
    return None

def batch_scan_directory():
    print_section_header("BATCH FILE APPEND & HIDDEN DATA SCAN")
    
    print(f"\n{BOLD}{WHITE}This will scan ALL image files in a directory for:{RESET}")
    print(f"  {CYAN}• Appended data after EOF markers (GIF, JPEG, PNG, NULL){RESET}")
    print(f"  {CYAN}• Hidden text and binary data{RESET}")
    print(f"  {CYAN}• Nested file detection (ZIP, PDF, Images){RESET}")
    print(f"  {CYAN}• Device information extraction{RESET}")
    
    dir_path = input(f"\n{BOLD}{GREEN}➔ Enter directory path to scan: {RESET}").strip()
    
    if not dir_path:
        print(f"\n{style_warning('No directory provided')}")
        input(f"\n{YELLOW}Press ENTER to continue...{RESET}")
        return
    
    if not os.path.exists(dir_path):
        print(f"\n{style_error(f'Directory not found: {dir_path}')}")
        input(f"\n{YELLOW}Press ENTER to continue...{RESET}")
        return
    
    if not os.path.isdir(dir_path):
        print(f"\n{style_error('Path is not a directory')}")
        input(f"\n{YELLOW}Press ENTER to continue...{RESET}")
        return
    
    image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.ico', '.cur']
    found_files = []
    
    print(f"\n{style_info('Scanning directory...')}")
    
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_exts):
                full_path = os.path.join(root, file)
                found_files.append(full_path)
    
    if not found_files:
        print_status(f"{style_warning('No image files found in directory')}")
        input(f"\n{YELLOW}Press ENTER to continue...{RESET}")
        return
    
    print(f"\n{style_success(f'Found {len(found_files)} image files')}")
    print(f"\n{BOLD}{YELLOW}Limit: Scanning first 100 files to avoid overload{RESET}")
    
    max_files = min(100, len(found_files))
    total_detections = 0
    total_size = 0
    appended_count = 0
    hidden_data_count = 0
    
    print(f"\n{BOLD}{BLUE}┌{'═' * 68}┐{RESET}")
    print(f"{BOLD}{BLUE}│{RESET} {BOLD}{WHITE}{'📊 BATCH SCAN RESULTS':^66}{RESET} {BOLD}{BLUE}│{RESET}")
    print(f"{BOLD}{BLUE}└{'═' * 68}┘{RESET}")
    
    for i, file_path in enumerate(found_files[:max_files]):
        print(f"\n{BOLD}{CYAN}▶ [{i+1}/{max_files}] Analyzing: {os.path.basename(file_path)}{RESET}")
        print(f"  {BOLD}{DIM}Path: {file_path}{RESET}")
        
        appended_found, appended_data = analyze_file_append(file_path)
        hidden_data = extract_hidden_data(file_path)
        
        if appended_found:
            appended_count += 1
        if hidden_data:
            hidden_data_count += 1
        
        try:
            file_size = os.path.getsize(file_path)
            total_size += file_size
        except:
            pass
        
        total_detections += 1
        
        if i < max_files - 1:
            print(f"\n  {BOLD}{DIM}{'─' * 68}{RESET}")
    
    print(f"\n{BOLD}{BLUE}┌{'═' * 68}┐{RESET}")
    print(f"{BOLD}{BLUE}│{RESET} {BOLD}{GREEN}📊 BATCH SCAN SUMMARY{' ' * 51}{BOLD}{BLUE}│{RESET}")
    print(f"{BOLD}{BLUE}└{'═' * 68}┘{RESET}")
    print_field("Total Files Scanned", f"{total_detections}")
    print_field("Total Files Found", f"{len(found_files)}")
    print_field("Total Data Scanned", human_readable_size(total_size))
    print_field("Scan Limit", f"{max_files} files")
    print_field("Files with Appended Data", f"{appended_count}")
    print_field("Files with Hidden Data", f"{hidden_data_count}")
    
    if appended_count > 0:
        print_status(f"{style_high(f'{appended_count} files contain appended data!')}")
    else:
        print_status(f"{style_success('No appended data found in scanned files')}")
    
    if hidden_data_count > 0:
        print_status(f"{style_high(f'{hidden_data_count} files contain hidden data!')}")
    else:
        print_status(f"{style_success('No hidden data found in scanned files')}")
    
    if len(found_files) > max_files:
        print_status(f"{style_warning(f'{len(found_files) - max_files} more files not scanned (limit reached)')}")
    
    print(f"\n{style_success('Batch scan complete!')}")
    print(f"\n{YELLOW}Press ENTER to continue...{RESET}")
    input()

def main():
    clear_screen()
    lock_and_redirect()
    
    while True:
        clear_screen()
        print_banner()
        print(f"\n{BOLD}{BLUE}┌{'═' * 68}┐{RESET}")
        print(f"{BOLD}{BLUE}│{RESET} {BOLD}{CYAN}🔍 LocBITE - Advanced Photo Forensics{' ' * 37}{BOLD}{BLUE}│{RESET}")
        print(f"{BOLD}{BLUE}├{'═' * 68}┤{RESET}")
        print(f"{BOLD}{BLUE}│{RESET} {BOLD}{YELLOW}🔐 Complete Forensics Toolkit - EXIF | GPS | QR | OCR | ELA | WhatsApp{' ' * 9}{BOLD}{BLUE}│{RESET}")
        print(f"{BOLD}{BLUE}└{'═' * 68}┘{RESET}")
        print(f"""
{BOLD}{GREEN}Options:{RESET}
  {BOLD}{BLUE}[{RESET}{BOLD}{WHITE}1{BOLD}{BLUE}]{RESET} {BOLD}{CYAN}Full Forensic Scan (Single File){RESET}
  {BOLD}{BLUE}[{RESET}{BOLD}{WHITE}2{BOLD}{BLUE}]{RESET} {BOLD}{MAGENTA}Steganography & Hidden Data Only{RESET}
  {BOLD}{BLUE}[{RESET}{BOLD}{WHITE}3{BOLD}{BLUE}]{RESET} {BOLD}{PURPLE}QR/OCR/ELA Analysis Only{RESET}
  {BOLD}{BLUE}[{RESET}{BOLD}{WHITE}4{BOLD}{BLUE}]{RESET} {BOLD}{RED}Batch File Append & Hidden Data Scan (Directory){RESET}
  {BOLD}{BLUE}[{RESET}{BOLD}{WHITE}5{BOLD}{BLUE}]{RESET} {BOLD}{RED}Exit{RESET}
        """)
        print(f"{BOLD}{BLUE}┌{'─' * 68}┐{RESET}")
        print(f"{BOLD}{BLUE}│{RESET} {BOLD}{WHITE}💡 Features:{' ' * 57}{BOLD}{BLUE}│{RESET}")
        print(f"{BOLD}{BLUE}│{RESET} {CYAN}• File Analysis (12 Hashes, Type, Size){' ' * 31}{BOLD}{BLUE}│{RESET}")
        print(f"{BOLD}{BLUE}│{RESET} {CYAN}• JPEG Forensics (Quality, Huffman, Markers){' ' * 24}{BOLD}{BLUE}│{RESET}")
        print(f"{BOLD}{BLUE}│{RESET} {CYAN}• Steganography (LSB, XOR, Base64, zlib){' ' * 27}{BOLD}{BLUE}│{RESET}")
        print(f"{BOLD}{BLUE}│{RESET} {CYAN}• EXIF/GPS Metadata Extraction{' ' * 36}{BOLD}{BLUE}│{RESET}")
        print(f"{BOLD}{BLUE}│{RESET} {CYAN}• QR Code & Barcode Detection{' ' * 35}{BOLD}{BLUE}│{RESET}")
        print(f"{BOLD}{BLUE}│{RESET} {CYAN}• OCR Text Extraction (Tesseract){' ' * 32}{BOLD}{BLUE}│{RESET}")
        print(f"{BOLD}{BLUE}│{RESET} {CYAN}• Error Level Analysis (Tampering Detection){' ' * 21}{BOLD}{BLUE}│{RESET}")
        print(f"{BOLD}{BLUE}│{RESET} {CYAN}• WhatsApp Database Scan{' ' * 42}{BOLD}{BLUE}│{RESET}")
        print(f"{BOLD}{BLUE}│{RESET} {CYAN}• Social Media Resolution Detection{' ' * 28}{BOLD}{BLUE}│{RESET}")
        print(f"{BOLD}{BLUE}│{RESET} {CYAN}• Device/Network/OS Information{' ' * 30}{BOLD}{BLUE}│{RESET}")
        print(f"{BOLD}{BLUE}│{RESET} {CYAN}• BATCH Directory Scan (NEW){' ' * 39}{BOLD}{BLUE}│{RESET}")
        print(f"{BOLD}{BLUE}└{'─' * 68}┘{RESET}")
        
        choice = input(f"\n{BOLD}{GREEN}➔ Select (1-5): {RESET}").strip()
        
        if choice in ["1", "2", "3"]:
            clear_screen()
            print_banner()
            print(f"\n{BOLD}{BLUE}┌{'═' * 68}┐{RESET}")
            print(f"{BOLD}{BLUE}│{RESET} {BOLD}{CYAN}📷 ANALYZE PHOTO{' ' * 50}{BOLD}{BLUE}│{RESET}")
            print(f"{BOLD}{BLUE}└{'═' * 68}┘{RESET}")
            print(f"""
{BOLD}{WHITE}Enter photo name or path:{RESET}

{BOLD}{GREEN}Examples:{RESET}
  {CYAN}• photo.jpg{RESET}
  {CYAN}• IMG_20240824.jpg{RESET}
  {CYAN}• /sdcard/Pictures/photo.jpg{RESET}
  {CYAN}• /storage/emulated/0/DCIM/Camera/IMG_001.jpg{RESET}

{BOLD}{YELLOW}💡 Just type the filename - I'll search for it!{RESET}
{BOLD}{YELLOW}💡 Supports: JPG, PNG, GIF, BMP, TIFF, WebP, ICO{RESET}
            """)
            
            img_input = input(f"\n{BOLD}{GREEN}➔ Path/name: {RESET}").strip()
            
            if not img_input:
                print(f"\n{style_warning('No input provided')}")
                input()
                continue
            
            img_path = find_image(img_input)
            
            if img_path:
                if choice == "1":
                    analyze_image(img_path)
                elif choice == "2":
                    clear_screen()
                    print_banner()
                    print(f"\n{BOLD}{BLUE}┌{'═' * 68}┐{RESET}")
                    print(f"{BOLD}{BLUE}│{RESET} {BOLD}{GREEN}📁 {YELLOW}{os.path.basename(img_path)}{' ' * (68 - len(os.path.basename(img_path)) - 18)}{BOLD}{BLUE}│{RESET}")
                    print(f"{BOLD}{BLUE}└{'═' * 68}┘{RESET}")
                    extract_hidden_data(img_path)
                    analyze_file_append(img_path)
                    print(f"\n{style_success('Steganography Analysis Complete!')}")
                    print(f"\n{YELLOW}Press ENTER to continue...{RESET}")
                    input()
                elif choice == "3":
                    clear_screen()
                    print_banner()
                    print(f"\n{BOLD}{BLUE}┌{'═' * 68}┐{RESET}")
                    print(f"{BOLD}{BLUE}│{RESET} {BOLD}{GREEN}📁 {YELLOW}{os.path.basename(img_path)}{' ' * (68 - len(os.path.basename(img_path)) - 18)}{BOLD}{BLUE}│{RESET}")
                    print(f"{BOLD}{BLUE}└{'═' * 68}┘{RESET}")
                    qr_check(img_path)
                    ocr_check(img_path)
                    ela_check(img_path)
                    print(f"\n{style_success('QR/OCR/ELA Analysis Complete!')}")
                    print(f"\n{YELLOW}Press ENTER to continue...{RESET}")
                    input()
            else:
                clear_screen()
                print_banner()
                print(f"\n{BOLD}{RED}┌{'═' * 68}┐{RESET}")
                print(f"{BOLD}{RED}│{RESET} {BOLD}{WHITE}❌ ERROR: '{img_input}' not found{' ' * (68 - len(img_input) - 28)}{BOLD}{RED}│{RESET}")
                print(f"{BOLD}{RED}└{'═' * 68}┘{RESET}")
                print(f"\n{BOLD}{WHITE}Check:{RESET}")
                print(f"  {CYAN}• File name spelling{RESET}")
                print(f"  {CYAN}• File exists on device{RESET}")
                print(f"  {CYAN}• Try full path (e.g., /sdcard/Pictures/photo.jpg){RESET}")
                print(f"\n{YELLOW}Press ENTER to continue...{RESET}")
                input()
        
        elif choice == "4":
            clear_screen()
            print_banner()
            batch_scan_directory()
        
        elif choice == "5":
            clear_screen()
            print_banner()
            print(f"""
{BOLD}{GREEN}👋 Goodbye!{RESET}
{BOLD}{YELLOW}🔐 Advanced photo forensics & metadata extraction{RESET}
{BOLD}{BLUE}Made with ❤️ by Sylhet Hackvenger{RESET}
            """)
            time.sleep(2)
            sys.exit(0)
        else:
            print(f"\n{style_error('Invalid option. Press ENTER to continue...')}")
            input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}⚠️ Interrupted by user{RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{RED}❌ Fatal Error: {str(e)}{RESET}")
        sys.exit(1)
