import subprocess
import shutil

def display_image(image_path):
    """Opens an image using a suitable command for the environment."""
    if shutil.which("xdg-open"):
        try:
            subprocess.run(["xdg-open", image_path], check=True, capture_output=True)
            print(f"Image opened with xdg-open: {image_path}")
            return
        except Exception as e:
            print(f"xdg-open failed: {e}")

    if shutil.which("termux-open"):
        try:
            subprocess.run(["termux-open", image_path], check=True, capture_output=True)
            print(f"Image opened with termux-open: {image_path}")
            return
        except Exception as e:
            print(f"termux-open failed: {e}")

    print("Warning: Could not find a suitable command to open the image.")
