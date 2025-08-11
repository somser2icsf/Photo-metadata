
import sys
import subprocess
import os

class PhotoInfoTool:
    def __init__(self):
        self.install_library("colorama")
        self.install_library("Pillow", "PIL")
        self.install_library("exifread")

        from colorama import Fore, Style, init
        from PIL import Image
        import exifread

        init(autoreset=True)

        self.Fore = Fore
        self.Style = Style
        self.Image = Image
        self.exifread = exifread

    def install_library(self, lib, imp=None):
        if imp is None:
            imp = lib
        try:
            __import__(imp)
        except ImportError:
            print(f"{self.Fore.YELLOW}[INFO] Installing {lib}...{self.Style.RESET_ALL}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

    def print_banner(self):
        print(f"""{self.Fore.CYAN}{self.Style.BRIGHT}
██╗ ██████╗███████╗███████╗
██║██╔════╝██╔════╝██╔════╝
██║██║     ███████╗█████╗  
██║██║     ╚════██║██╔══╝  
██║╚██████╗███████║██║     
╚═╝ ╚═════╝╚══════╝╚═╝
{self.Fore.GREEN}{'='*45}
{self.Fore.YELLOW}  ____  _   _ ____    _____ ___  ____  _____ 
 {self.Fore.YELLOW}|  _ \| | | |  _ \  |  ___/ _ \|  _ \| ____|
 {self.Fore.YELLOW}| |_) | |_| | | | | | |_ | | | | |_) |  _|  
 {self.Fore.YELLOW}|  __/|  _  | |_| | |  _|| |_| |  _ <| |___ 
 {self.Fore.YELLOW}|_|   |_| |_|____/  |_|   \___/|_| \_\_____|
{self.Fore.GREEN}{'='*45}
{self.Fore.CYAN}  Developed by: {self.Style.BRIGHT}Somser SA
{self.Fore.CYAN}  Tool: {self.Style.BRIGHT}Photo MetaData
{self.Fore.CYAN}  GitHub: {self.Style.BRIGHT}https://github.com/somser2icsf
{self.Fore.GREEN}{'='*45}{self.Style.RESET_ALL}""")

    def find_image_path(self, image_name):
        common_dirs = [
            os.path.join('/sdcard', 'DCIM', 'Camera'),
            os.path.join('/sdcard', 'Pictures'),
            os.path.join('/sdcard', 'Downloads'),
            os.getcwd()
        ]
        if os.path.exists(image_name):
            return image_name
        for d in common_dirs:
            p = os.path.join(d, image_name)
            if os.path.exists(p):
                return p
        return None

    def dms_to_decimal(self, dms, ref):
        degrees = float(dms.values[0].num) / float(dms.values[0].den)
        minutes = float(dms.values[1].num) / float(dms.values[1].den)
        seconds = float(dms.values[2].num) / float(dms.values[2].den)
        dec = degrees + (minutes / 60.0) + (seconds / 3600.0)
        if ref in ['S', 'W']:
            dec = -dec
        return dec

    def format_fraction(self, val):
        try:
            f = val.num / val.den
            if f.is_integer():
                return str(int(f))
            else:
                return str(round(f, 4))
        except:
            return str(val)

    def extract_metadata(self, file_path):
        try:
            img = self.Image.open(file_path)
            img.verify()
        except Exception:
            print(f"{self.Fore.RED}❌ Invalid image file.{self.Style.RESET_ALL}")
            return

        img = self.Image.open(file_path)
        width, height = img.size
        img_format = img.format
        file_size_kb = os.path.getsize(file_path) / 1024
        size_str = f"{file_size_kb/1024:.2f} MB" if file_size_kb > 1024 else f"{file_size_kb:.0f} KB"

        with open(file_path, 'rb') as f:
            exif_data = self.exifread.process_file(f, details=True)

        print(f"\n{self.Fore.CYAN}{'-'*50}{self.Style.RESET_ALL}")
        print(f"{self.Fore.GREEN}📂 File        : {self.Style.BRIGHT}{os.path.basename(file_path)}")
        print(f"{self.Fore.GREEN}📁 Path        : {file_path}")
        print(f"{self.Fore.GREEN}📐 Dimensions  : {width} x {height} pixels")
        print(f"{self.Fore.GREEN}💾 Size        : {size_str}")
        print(f"{self.Fore.GREEN}🖼 Format      : {img_format}")
        print(f"{self.Fore.CYAN}{'-'*50}{self.Style.RESET_ALL}")

        # Key EXIF tags to look for:
        keys_of_interest = {
            "Image Make": "Camera Make",
            "Image Model": "Camera Model",
            "EXIF DateTimeOriginal": "Date Taken",
            "EXIF ExposureTime": "Exposure Time",
            "EXIF FNumber": "Aperture (F-Stop)",
            "EXIF ISOSpeedRatings": "ISO",
            "EXIF FocalLength": "Focal Length",
            "EXIF Flash": "Flash",
            "EXIF LensModel": "Lens Model",
            "EXIF WhiteBalance": "White Balance",
            "EXIF ExposureProgram": "Exposure Program",
            "EXIF MeteringMode": "Metering Mode",
            "EXIF LightSource": "Light Source",
            "EXIF ExposureBiasValue": "Exposure Bias",
            "EXIF ShutterSpeedValue": "Shutter Speed",
            "EXIF MaxApertureValue": "Max Aperture",
            "EXIF SubjectDistance": "Subject Distance",
            "EXIF SceneCaptureType": "Scene Capture Type",
            "EXIF Contrast": "Contrast",
            "EXIF Saturation": "Saturation",
            "EXIF Sharpness": "Sharpness",
        }

        for tag, desc in keys_of_interest.items():
            if tag in exif_data:
                val = exif_data[tag]
                if hasattr(val, 'values'):
                    if isinstance(val.values, list) and len(val.values) == 1:
                        v = val.values[0]
                        val = self.format_fraction(v)
                    else:
                        val = str(val)
                print(f"{self.Fore.YELLOW}{desc}: {self.Fore.WHITE}{val}")

        # GPS Info
        gps_keys = ['GPS GPSLatitude', 'GPS GPSLongitude', 'GPS GPSLatitudeRef', 'GPS GPSLongitudeRef']
        if all(k in exif_data for k in gps_keys):
            try:
                lat = self.dms_to_decimal(exif_data['GPS GPSLatitude'], exif_data['GPS GPSLatitudeRef'].values[0])
                lon = self.dms_to_decimal(exif_data['GPS GPSLongitude'], exif_data['GPS GPSLongitudeRef'].values[0])
                print(f"\n{self.Fore.BLUE}🌍 GPS Location:")
                print(f"   Latitude : {self.Fore.WHITE}{lat}")
                print(f"   Longitude: {self.Fore.WHITE}{lon}")
                print(f"   Map Link : {self.Fore.CYAN}https://maps.google.com/?q={lat},{lon}")
            except Exception as e:
                print(f"{self.Fore.RED}❌ Error parsing GPS data: {e}")
        else:
            print(f"\n{self.Fore.YELLOW}⚠️ No GPS data found in this image.{self.Style.RESET_ALL}")

        print(f"{self.Fore.CYAN}{'-'*50}{self.Style.RESET_ALL}")

    def run(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.print_banner()

        if 'TERMUX_VERSION' in os.environ and not os.path.exists('/sdcard'):
            print(f"{self.Fore.YELLOW}Requesting storage permission...{self.Style.RESET_ALL}")
            os.system('termux-setup-storage')

        while True:
            print(f"\n{self.Fore.GREEN}💡 Enter image file name (e.g., photo.jpg) or full path.")
            user_input = input(f"{self.Fore.MAGENTA}> Enter name/path ({self.Fore.YELLOW}or 'exit' to quit{self.Fore.MAGENTA}): {self.Style.RESET_ALL}").strip()
            if user_input.lower() == 'exit':
                print(f"{self.Fore.YELLOW}👋 Goodbye!{self.Style.RESET_ALL}")
                break
            if not user_input:
                print(f"{self.Fore.RED}❌ Please enter a valid file name or path.")
                continue
            path = self.find_image_path(user_input)
            if path:
                self.extract_metadata(path)
            else:
                print(f"{self.Fore.RED}❌ Image not found: {user_input}")

if __name__ == "__main__":
    tool = PhotoInfoTool()
    tool.run()
