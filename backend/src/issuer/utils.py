import os
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from logging import getLogger

logger = getLogger("LOGGER")


def preprocess_image(path, resolution, keep_aspect_ratio=False):
    logger.info(f"preprocess_image called with path: {path}")
    try:
        img = Image.open(path)
        logger.info(f"Image loaded successfully - Size: {img.size}, Mode: {img.mode}")
        
        # Ensure image is valid
        if img.size[0] <= 0 or img.size[1] <= 0:
            raise ValueError("Invalid image size: {}".format(img.size))
            
        if img.mode != "RGB":
            if img.mode == "RGBA":
                # Intelligent background color detection
                logger.info(f"RGBA detected - analyzing image to choose background color")
                
                # Analysiere die durchschnittliche Helligkeit der nicht-transparenten Pixel
                rgba_data = img.getdata()
                non_transparent_pixels = [pixel[:3] for pixel in rgba_data if pixel[3] > 128]  # Alpha > 128
                
                if non_transparent_pixels:
                    avg_brightness = sum(sum(pixel) for pixel in non_transparent_pixels) / (len(non_transparent_pixels) * 3)
                    logger.info(f"Average brightness of logo: {avg_brightness:.1f}")
                    
                    # Use dark background for light logos, light background for dark logos
                    if avg_brightness > 200:
                        bg_color = (40, 40, 40)
                        logger.info(f"Light logo detected - using dark background: {bg_color}")
                    else:
                        bg_color = (255, 255, 255)
                        logger.info(f"Dark logo detected - using light background: {bg_color}")
                else:
                    # Fallback: white background
                    bg_color = (255, 255, 255)
                    logger.info(f"No non-transparent pixels found - using white background")
                
                smart_bg = Image.new('RGB', img.size, bg_color)
                smart_bg.paste(img, mask=img.split()[-1])  # Use alpha as mask
                img = smart_bg
            else:
                img = img.convert("RGB")
            logger.info(f"Image converted to RGB mode")

        if keep_aspect_ratio:
            original_width, original_height = img.size
            max_height = resolution[1]
            scale_factor = max_height / original_height
            new_width = int(original_width * scale_factor)
            img = img.resize((new_width, max_height))
            logger.info(f"Image resized (aspect ratio) to: {img.size}")
        else:
            img = img.resize(resolution)
            logger.info(f"Image resized to: {img.size}")

        # Base64 encode the image as jpg
        buffered = BytesIO()
        img.save(buffered, format="JPEG", quality=90)
        img_data = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        logger.info(f"Image successfully encoded to base64, length: {len(img_data)}")
        return img_data
    except Exception as e:
        logger.error(f"Image processing failed for {path}: {str(e)}")
        # Create fallback image with requested dimensions
        fallback_img = Image.new('RGB', resolution, color='#f0f0f0')
        
        # Add placeholder text
        draw = ImageDraw.Draw(fallback_img)
        text = "Placeholder"
        
        # Calculate text position for center of image
        text_x = resolution[0] // 2
        text_y = resolution[1] // 2
        
        # Draw text
        draw.text((text_x, text_y), text, fill='#555555', anchor='mm')
        
        # Base64 encode fallback image
        buffered = BytesIO()
        fallback_img.save(buffered, format="JPEG")
        fallback_img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        logger.info(f"Fallback image created, length: {len(fallback_img_str)}")
        return fallback_img_str


def preprocess_theme_icon(path, resolution, keep_aspect_ratio=False):
    """
    Special processing for theme icons that preserves transparency
    """
    logger.info(f"preprocess_theme_icon called with path: {path}")
    try:
        img = Image.open(path)
        logger.info(f"Theme icon loaded successfully - Size: {img.size}, Mode: {img.mode}")
        
        # Ensure image is valid
        if img.size[0] <= 0 or img.size[1] <= 0:
            raise ValueError("Invalid image size: {}".format(img.size))
        
        # For theme icons, preserve RGBA/transparency
        if img.mode != "RGBA":
            if img.mode == "RGB":
                # Convert RGB to RGBA (add alpha channel)
                img = img.convert("RGBA")
                logger.info(f"RGB converted to RGBA for transparency support")
            elif img.mode in ("L", "P"):
                img = img.convert("RGBA")
                logger.info(f"{img.mode} converted to RGBA for transparency support")

        if keep_aspect_ratio:
            original_width, original_height = img.size
            max_height = resolution[1]
            scale_factor = max_height / original_height
            new_width = int(original_width * scale_factor)
            img = img.resize((new_width, max_height), Image.Resampling.LANCZOS)
            logger.info(f"Theme icon resized (aspect ratio) to: {img.size}")
        else:
            img = img.resize(resolution, Image.Resampling.LANCZOS)
            logger.info(f"Theme icon resized to: {img.size}")

        # Save as PNG to preserve transparency
        buffered = BytesIO()
        img.save(buffered, format="PNG", optimize=True)
        img_data = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        logger.info(f"Theme icon successfully encoded to base64 PNG, length: {len(img_data)}")
        return img_data
        
    except Exception as e:
        logger.error(f"Theme icon processing failed for {path}: {str(e)}")
        # Create transparent fallback image
        fallback_img = Image.new('RGBA', resolution, color=(240, 240, 240, 128))
        
        # Add placeholder text
        draw = ImageDraw.Draw(fallback_img)
        text = "Logo"
        text_x = resolution[0] // 2
        text_y = resolution[1] // 2
        draw.text((text_x, text_y), text, fill=(85, 85, 85, 255), anchor='mm')
        
        # Base64 encode fallback image as PNG
        buffered = BytesIO()
        fallback_img.save(buffered, format="PNG")
        fallback_img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        logger.info(f"Transparent fallback theme icon created, length: {len(fallback_img_str)}")
        return fallback_img_str


def get_placeholders(logo_filename="studentVC-logo-sora-cropped-darkmode.png", profile_filename="student.png"):
    # Try to get tenant-specific logo first
    try:
        from ..tenants.registry import get_current_tenant_config
        tenant_config = get_current_tenant_config()
        if tenant_config:
            # Check if this is a tenant-specific logo
            tenant_static_path = tenant_config.static_path
            tenant_logo_path = os.path.join(tenant_static_path, logo_filename)
            
            logger.info(f"🎓 TENANT LOGO - Checking tenant static path: {tenant_static_path}")
            logger.info(f"🎓 TENANT LOGO - Looking for logo at: {tenant_logo_path}")
            
            if os.path.exists(tenant_logo_path):
                logger.info(f"Found tenant-specific logo: {tenant_logo_path}")
                logo_path = tenant_logo_path
            else:
                # Fall back to main static directory
                placeholder_path = os.path.join(os.path.dirname(__file__), "..", "static")
                logo_path = os.path.join(placeholder_path, logo_filename)
                logger.info(f"Tenant logo not found, falling back to: {logo_path}")
        else:
            # No tenant config, use main static directory
            placeholder_path = os.path.join(os.path.dirname(__file__), "..", "static")
            logo_path = os.path.join(placeholder_path, logo_filename)
            logger.info(f"Using main static logo: {logo_path}")
    except Exception as e:
        # Error accessing tenant system, fall back to main static directory
        logger.info(f"Tenant error - falling back to main static: {e}")
        placeholder_path = os.path.join(os.path.dirname(__file__), "..", "static")
        logo_path = os.path.join(placeholder_path, logo_filename)
    
    # Profile image always from main static directory
    placeholder_path = os.path.join(os.path.dirname(__file__), "..", "static")
    profile_path = os.path.join(placeholder_path, profile_filename)
    
    logger.debug(f"get_placeholders called - Logo: {logo_filename}, Profile: {profile_filename}")
    
    # Fallback to logo.png if specified file doesn't exist
    if not os.path.exists(logo_path):
        fallback_placeholder_path = os.path.join(os.path.dirname(__file__), "..", "static")
        logo_path = os.path.join(fallback_placeholder_path, "logo.png")
        logger.info(f"Logo fallback to: {logo_path}")
    
    # Fallback to student.png if specified file doesn't exist
    if not os.path.exists(profile_path):
        profile_path = os.path.join(placeholder_path, "student.png")
        logger.info(f"Profile fallback to: {profile_path}")
        
    # Note: Removed hardcoded macOS path fallback for cross-platform compatibility
    # If profile_path still doesn't exist, preprocess_image will handle it with a placeholder

    logo = preprocess_image(logo_path, (400, 300), keep_aspect_ratio=True)
    profile = preprocess_image(profile_path, (400, 400), keep_aspect_ratio=True)
    
    logger.debug(f"Final logo base64 length: {len(logo) if logo else 'None'}")
    logger.debug(f"Final profile base64 length: {len(profile) if profile else 'None'}")

    return logo, profile


if __name__ == "__main__":
    print(get_placeholders())
