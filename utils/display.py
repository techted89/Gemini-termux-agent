import subprocess


def display_image_termux(image_path):
    """Opens an image using termux-open."""
    try:
        subprocess.run(["termux-open", image_path], check=True, capture_output=True)
        print(f"Image opened in default viewer: {image_path}")
    except Exception:
        print("Warning: Failed to open image. Is 'termux-api' installed?")
