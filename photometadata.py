# -*- coding: utf-8 -*-
"""
ICSF Photo Info Tool
Class-based implementation by Somser SA
"""

import sys
import subprocess
import os
from fractions import Fraction

class PhotoInfoTool:
    def __init__(self):
        # Auto install required libraries if missing
        self.install_library("colorama")
        self.install_library("Pillow", "PIL")
        self.install_library("exifread")

        # Import after installation
        from colorama import Fore, Style, init
        from PIL import Image
        import exifread

        init(autoreset=True)

        # Save imported modules & styles as instance variables for easy access
        self.Fore = Fore
        self.Style = Style
        self.Image = Image
        self.exifread = exifread

    def install_library(self, library_name, import_name=None):
        if import_name is None:
            import_name = library_name
        try:
            __import__(import_name)
        except ImportError:
            print(f"[INFO] Installing {library_name}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", library_name])

    def print_banner(self):
        print(f"""{self.Fore.CYAN}{self.Style.BRIGHT}
██╗ ██████╗███████╗███████╗
██║██╔════╝██╔════╝██╔════╝
██║██║     ███████╗█████╗  
██║██║     ╚════██║██╔══╝  
██║╚██████╗███████║██║     
╚═╝ ╚═════╝╚══════╝╚═╝
{self.Fore.YELLOW}      ICSF - Photo Info Tool
{self.Fore.GREEN}   Developed by: Somser SA
{self.Style.RESET_ALL}""")

    def find_image_path(self, image_name):
        common_dirs = [
            os.path.join('/sdcard', 'DCIM', 'Camera'),
            os.path.join('/sdcard', 'Pictures'),
            os.path.join('/sdcard', 'Downloads'),
            os.getcwd()
        ]
        if os.path.exists(image_name):
            return image_name
        for dir_path in common_dirs:
            full_path = os.path.join(dir_path, image_name)
            if os.path.exists(full_path):
                return full_path
        return None

    def dms_to_decimal(self, dms, ref):
        degrees = float(dms.values[0].num) / float(dms.values[0].den)
        minutes = float(dms.values[1].num) / float(dms.values[1].den)
        seconds = float(dms.values[2].num) / float(dms.values[2].den)
        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
        if ref in ['S', 'W']:
            decimal = -decimal
        return decimal

    def extract_metadata(self, file_path):
        try:
            # Validate image
            try:
                img = self.Image.open(file_path)
                img.verify()
            except Exception:
                print(f"{self.Fore.RED}❌ This is not a valid image.")
                return

            img = self.Image.open(file_path)
            width, height = img.size
            img_format = img.format
            file_size = os.path.getsize(file_path) / 1024
            size_str = f"{file_size/1024:.2f} MB" if file_size > 1024 else f"{file_size:.0f} KB"

            with open(file_path, 'rb') as f:
                exif_data = self.exifread.process_file(f, details=True)

            date_taken = exif_data.get('EXIF DateTimeOriginal', "Not Available")
            camera_model = exif_data.get('Image Model', "Not Available")

            print(f"""{self.Fore.CYAN}──────────────────────────────────────────
🖼 File Name     : {os.path.basename(file_path)}
📂 File Path     : {file_path}
📏 Dimensions    : {width} x {height} pixels
🗂 File Size     : {size_str}
🖌 Format        : {img_format}
📅 Taken On      : {date_taken}
📷 Camera Model  : {camera_model}
──────────────────────────────────────────""")

            if all(k in exif_data for k in ['GPS GPSLatitude', 'GPS GPSLongitude', 'GPS GPSLatitudeRef', 'GPS GPSLongitudeRef']):
                lat = self.dms_to_decimal(exif_data['GPS GPSLatitude'], exif_data['GPS GPSLatitudeRef'].values[0])
                lon = self.dms_to_decimal(exif_data['GPS GPSLongitude'], exif_data['GPS GPSLongitudeRef'].values[0])
                print(f"""🌍 GPS Location Found!
   Latitude  : {lat}
   Longitude : {lon}
   🔗 Map Link: https://maps.google.com/?q={lat},{lon}
──────────────────────────────────────────""")
            else:
                print(f"""⚠ No GPS data found in this image.
──────────────────────────────────────────""")

        except Exception as e:
            print(f"{self.Fore.RED}🚫 Error: {e}")

    def run(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.print_banner()

        if 'TERMUX_VERSION' in os.environ and not os.path.exists('/sdcard'):
            print(f"{self.Fore.YELLOW}Requesting storage permission...{self.Style.RESET_ALL}")
            os.system('termux-setup-storage')

        while True:
            print(f"\n{self.Fore.GREEN}💡 Tip: Enter image file name (e.g., photo.jpg) or full path.")
            user_input = input(f"{self.Fore.MAGENTA}> Enter image name/path ({self.Fore.YELLOW}or 'exit' to quit{self.Fore.MAGENTA}): {self.Style.RESET_ALL}").strip()
            if user_input.lower() == 'exit':
                print(f"{self.Fore.YELLOW}👋 Goodbye!{self.Style.RESET_ALL}")
                break
            if not user_input:
                print(f"{self.Fore.RED}❌ Please enter a valid file name.")
                continue
            path = self.find_image_path(user_input)
            if path:
                self.extract_metadata(path)
            else:
                print(f"{self.Fore.RED}❌ Image not found: {user_input}")


if __name__ == "__main__":
    tool = PhotoInfoTool()
    tool.run()
