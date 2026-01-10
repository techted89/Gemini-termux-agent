import subprocess

def display_image(image_path):
    """Opens an image using xdg-open."""
    try:
        subprocess.run(["xdg-open", image_path], check=True, capture_output=True)
        print(f"Image opened in default viewer: {image_path}")
    except Exception as e:
        print(f"Warning: Failed to open image. {e}")
