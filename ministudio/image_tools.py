"""
Image Processing Tools
======================
Image manipulation, generation, and analysis utilities.

Features:
- Image loading, saving, resizing
- Text rendering on images
- Color manipulation
- Image composition
- Thumbnail generation

Dependencies:
    pip install pillow numpy

Optional:
    pip install opencv-python
"""

import os
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ============ Check Dependencies ============

def _has_pillow() -> bool:
    try:
        from PIL import Image
        return True
    except ImportError:
        return False


def _has_opencv() -> bool:
    try:
        import cv2
        return True
    except ImportError:
        return False


# ============ Image Information ============

@dataclass
class ImageInfo:
    """Image file metadata."""
    
    path: str
    width: int = 0
    height: int = 0
    format: str = ""
    mode: str = ""  # RGB, RGBA, L, etc.
    channels: int = 3
    file_size: int = 0
    dpi: Optional[Tuple[int, int]] = None
    
    @property
    def resolution(self) -> str:
        return f"{self.width}x{self.height}"
    
    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height if self.height > 0 else 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "width": self.width,
            "height": self.height,
            "format": self.format,
            "mode": self.mode,
            "resolution": self.resolution
        }


def get_image_info(image_path: str) -> ImageInfo:
    """Get image information."""
    if not _has_pillow():
        raise ImportError("Pillow required: pip install pillow")
    
    from PIL import Image
    
    img = Image.open(image_path)
    
    info = ImageInfo(
        path=image_path,
        width=img.width,
        height=img.height,
        format=img.format or "",
        mode=img.mode,
        channels=len(img.getbands()),
        file_size=os.path.getsize(image_path),
        dpi=img.info.get('dpi')
    )
    
    img.close()
    return info


# ============ Image Operations ============

class ImageOperations:
    """Common image operations."""
    
    @staticmethod
    def load(image_path: str) -> Any:
        """Load image as PIL Image or numpy array."""
        if not _has_pillow():
            raise ImportError("Pillow required: pip install pillow")
        
        from PIL import Image
        return Image.open(image_path)
    
    @staticmethod
    def save(
        image: Any,
        output_path: str,
        quality: int = 95,
        optimize: bool = True
    ) -> str:
        """
        Save image to file.
        
        Args:
            image: PIL Image or numpy array
            output_path: Output file path
            quality: JPEG quality (1-100)
            optimize: Optimize file size
        
        Returns:
            Path to saved image
        """
        from PIL import Image
        
        # Convert numpy array to PIL
        if hasattr(image, 'shape'):
            import numpy as np
            if len(image.shape) == 3 and image.shape[2] == 3:
                image = Image.fromarray(image.astype(np.uint8))
            elif len(image.shape) == 3 and image.shape[2] == 4:
                image = Image.fromarray(image.astype(np.uint8), mode='RGBA')
            else:
                image = Image.fromarray(image.astype(np.uint8))
        
        # Determine format from extension
        ext = Path(output_path).suffix.lower()
        
        save_kwargs = {}
        if ext in ['.jpg', '.jpeg']:
            save_kwargs['quality'] = quality
            save_kwargs['optimize'] = optimize
            # Convert RGBA to RGB for JPEG
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
        elif ext == '.png':
            save_kwargs['optimize'] = optimize
        elif ext == '.webp':
            save_kwargs['quality'] = quality
        
        image.save(output_path, **save_kwargs)
        return output_path
    
    @staticmethod
    def resize(
        image: Any,
        width: Optional[int] = None,
        height: Optional[int] = None,
        maintain_aspect: bool = True,
        resample: str = "lanczos"
    ) -> Any:
        """
        Resize image.
        
        Args:
            image: PIL Image
            width: Target width
            height: Target height
            maintain_aspect: Maintain aspect ratio
            resample: Resampling filter
        
        Returns:
            Resized PIL Image
        """
        from PIL import Image
        
        # Get resampling filter
        resample_map = {
            "nearest": Image.Resampling.NEAREST,
            "bilinear": Image.Resampling.BILINEAR,
            "bicubic": Image.Resampling.BICUBIC,
            "lanczos": Image.Resampling.LANCZOS,
        }
        resample_filter = resample_map.get(resample, Image.Resampling.LANCZOS)
        
        if maintain_aspect:
            if width and height:
                # Fit within box
                image.thumbnail((width, height), resample_filter)
                return image
            elif width:
                ratio = width / image.width
                height = int(image.height * ratio)
            elif height:
                ratio = height / image.height
                width = int(image.width * ratio)
            else:
                return image
        else:
            width = width or image.width
            height = height or image.height
        
        return image.resize((width, height), resample_filter)
    
    @staticmethod
    def crop(
        image: Any,
        left: int,
        top: int,
        right: int,
        bottom: int
    ) -> Any:
        """Crop image to box."""
        return image.crop((left, top, right, bottom))
    
    @staticmethod
    def rotate(
        image: Any,
        angle: float,
        expand: bool = True,
        fill_color: Tuple[int, int, int] = (0, 0, 0)
    ) -> Any:
        """Rotate image by angle (degrees)."""
        return image.rotate(angle, expand=expand, fillcolor=fill_color)
    
    @staticmethod
    def flip_horizontal(image: Any) -> Any:
        """Flip image horizontally."""
        from PIL import Image
        return image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    
    @staticmethod
    def flip_vertical(image: Any) -> Any:
        """Flip image vertically."""
        from PIL import Image
        return image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    
    @staticmethod
    def to_grayscale(image: Any) -> Any:
        """Convert to grayscale."""
        return image.convert('L')
    
    @staticmethod
    def adjust_brightness(image: Any, factor: float) -> Any:
        """
        Adjust brightness.
        
        Args:
            image: PIL Image
            factor: Brightness factor (1.0 = original)
        """
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def adjust_contrast(image: Any, factor: float) -> Any:
        """Adjust contrast."""
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def adjust_saturation(image: Any, factor: float) -> Any:
        """Adjust saturation."""
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Color(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def blur(image: Any, radius: float = 2.0) -> Any:
        """Apply gaussian blur."""
        from PIL import ImageFilter
        return image.filter(ImageFilter.GaussianBlur(radius))
    
    @staticmethod
    def sharpen(image: Any) -> Any:
        """Apply sharpening filter."""
        from PIL import ImageFilter
        return image.filter(ImageFilter.SHARPEN)


# ============ Text Rendering ============

@dataclass
class TextRenderConfig:
    """Configuration for text rendering on images."""
    
    font_path: Optional[str] = None
    font_size: int = 32
    text_color: Tuple[int, int, int, int] = (255, 255, 255, 255)
    background_color: Optional[Tuple[int, int, int, int]] = None
    outline_color: Optional[Tuple[int, int, int, int]] = (0, 0, 0, 255)
    outline_width: int = 2
    padding: Tuple[int, int, int, int] = (10, 5, 10, 5)  # left, top, right, bottom
    align: str = "center"  # left, center, right
    max_width: Optional[int] = None


class TextRenderer:
    """
    Render text on images with various styles.
    
    TODO: Add more advanced text effects
    """
    
    def __init__(self, config: Optional[TextRenderConfig] = None):
        self.config = config or TextRenderConfig()
        self._font = None
    
    def _get_font(self, size: Optional[int] = None):
        """Get PIL font."""
        from PIL import ImageFont
        
        size = size or self.config.font_size
        
        if self.config.font_path:
            return ImageFont.truetype(self.config.font_path, size)
        
        # Try common fonts
        font_names = [
            "arial.ttf",
            "Arial.ttf",
            "DejaVuSans.ttf",
            "FreeSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "C:/Windows/Fonts/arial.ttf"
        ]
        
        for font_name in font_names:
            try:
                return ImageFont.truetype(font_name, size)
            except (IOError, OSError):
                continue
        
        # Fallback to default
        return ImageFont.load_default()
    
    def get_text_size(self, text: str, font_size: Optional[int] = None) -> Tuple[int, int]:
        """Get text dimensions."""
        from PIL import Image, ImageDraw
        
        font = self._get_font(font_size)
        
        # Create temporary image for measuring
        tmp_img = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(tmp_img)
        
        bbox = draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        
        return (width, height)
    
    def render_text(
        self,
        text: str,
        width: int,
        height: int,
        config: Optional[TextRenderConfig] = None
    ) -> Any:
        """
        Render text to a new image.
        
        Args:
            text: Text to render
            width: Image width
            height: Image height
            config: Optional override config
        
        Returns:
            PIL Image with rendered text
        """
        from PIL import Image, ImageDraw
        
        cfg = config or self.config
        font = self._get_font(cfg.font_size)
        
        # Create image with transparency
        if cfg.background_color:
            img = Image.new('RGBA', (width, height), cfg.background_color)
        else:
            img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        
        draw = ImageDraw.Draw(img)
        
        # Calculate text position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        if cfg.align == "center":
            x = (width - text_width) // 2
        elif cfg.align == "right":
            x = width - text_width - cfg.padding[2]
        else:
            x = cfg.padding[0]
        
        y = (height - text_height) // 2
        
        # Draw outline if specified
        if cfg.outline_color and cfg.outline_width > 0:
            for dx in range(-cfg.outline_width, cfg.outline_width + 1):
                for dy in range(-cfg.outline_width, cfg.outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text(
                            (x + dx, y + dy),
                            text,
                            font=font,
                            fill=cfg.outline_color
                        )
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=cfg.text_color)
        
        return img
    
    def draw_text_on_image(
        self,
        image: Any,
        text: str,
        position: Tuple[int, int],
        config: Optional[TextRenderConfig] = None
    ) -> Any:
        """
        Draw text on existing image.
        
        Args:
            image: PIL Image
            text: Text to draw
            position: (x, y) position
            config: Optional override config
        
        Returns:
            Image with text
        """
        from PIL import Image, ImageDraw
        
        cfg = config or self.config
        font = self._get_font(cfg.font_size)
        
        # Ensure RGBA mode
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Create text layer
        text_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_layer)
        
        x, y = position
        
        # Draw outline
        if cfg.outline_color and cfg.outline_width > 0:
            for dx in range(-cfg.outline_width, cfg.outline_width + 1):
                for dy in range(-cfg.outline_width, cfg.outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text(
                            (x + dx, y + dy),
                            text,
                            font=font,
                            fill=cfg.outline_color
                        )
        
        # Draw text
        draw.text((x, y), text, font=font, fill=cfg.text_color)
        
        # Composite
        result = Image.alpha_composite(image, text_layer)
        
        return result
    
    def draw_text_box(
        self,
        image: Any,
        text: str,
        position: Tuple[int, int],
        config: Optional[TextRenderConfig] = None
    ) -> Any:
        """
        Draw text with background box on image.
        
        Args:
            image: PIL Image
            text: Text to draw
            position: (x, y) position
            config: Optional override config
        
        Returns:
            Image with text box
        """
        from PIL import Image, ImageDraw
        
        cfg = config or self.config
        font = self._get_font(cfg.font_size)
        
        # Ensure RGBA
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Calculate text size
        tmp_draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
        bbox = tmp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Calculate box dimensions
        box_width = text_width + cfg.padding[0] + cfg.padding[2]
        box_height = text_height + cfg.padding[1] + cfg.padding[3]
        
        x, y = position
        
        # Create layer
        layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        
        # Draw background box
        if cfg.background_color:
            draw.rectangle(
                [x, y, x + box_width, y + box_height],
                fill=cfg.background_color
            )
        
        # Draw text
        text_x = x + cfg.padding[0]
        text_y = y + cfg.padding[1]
        
        draw.text((text_x, text_y), text, font=font, fill=cfg.text_color)
        
        # Composite
        return Image.alpha_composite(image, layer)


# ============ Image Composition ============

class ImageCompositor:
    """Composite multiple images together."""
    
    @staticmethod
    def overlay(
        background: Any,
        foreground: Any,
        position: Tuple[int, int] = (0, 0),
        opacity: float = 1.0
    ) -> Any:
        """
        Overlay foreground on background.
        
        Args:
            background: Background PIL Image
            foreground: Foreground PIL Image
            position: (x, y) position
            opacity: Foreground opacity (0-1)
        
        Returns:
            Composited image
        """
        from PIL import Image
        
        # Ensure RGBA
        if background.mode != 'RGBA':
            background = background.convert('RGBA')
        if foreground.mode != 'RGBA':
            foreground = foreground.convert('RGBA')
        
        # Apply opacity
        if opacity < 1.0:
            alpha = foreground.split()[3]
            alpha = alpha.point(lambda p: int(p * opacity))
            foreground.putalpha(alpha)
        
        # Create output
        result = background.copy()
        result.paste(foreground, position, foreground)
        
        return result
    
    @staticmethod
    def blend(
        image1: Any,
        image2: Any,
        alpha: float = 0.5
    ) -> Any:
        """
        Blend two images.
        
        Args:
            image1: First image
            image2: Second image
            alpha: Blend factor (0 = image1, 1 = image2)
        
        Returns:
            Blended image
        """
        from PIL import Image
        
        # Ensure same size
        if image1.size != image2.size:
            image2 = image2.resize(image1.size)
        
        # Ensure same mode
        if image1.mode != image2.mode:
            image2 = image2.convert(image1.mode)
        
        return Image.blend(image1, image2, alpha)
    
    @staticmethod
    def create_grid(
        images: List[Any],
        columns: int,
        spacing: int = 10,
        background_color: Tuple[int, int, int] = (0, 0, 0)
    ) -> Any:
        """
        Create image grid.
        
        Args:
            images: List of PIL Images
            columns: Number of columns
            spacing: Space between images
            background_color: Background color
        
        Returns:
            Grid image
        """
        from PIL import Image
        
        if not images:
            return Image.new('RGB', (100, 100), background_color)
        
        # Assume all images same size (or resize to first)
        thumb_width = images[0].width
        thumb_height = images[0].height
        
        rows = (len(images) + columns - 1) // columns
        
        grid_width = columns * thumb_width + (columns + 1) * spacing
        grid_height = rows * thumb_height + (rows + 1) * spacing
        
        grid = Image.new('RGB', (grid_width, grid_height), background_color)
        
        for i, img in enumerate(images):
            row = i // columns
            col = i % columns
            
            x = spacing + col * (thumb_width + spacing)
            y = spacing + row * (thumb_height + spacing)
            
            # Resize if needed
            if img.size != (thumb_width, thumb_height):
                img = img.resize((thumb_width, thumb_height))
            
            # Convert mode if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            grid.paste(img, (x, y))
        
        return grid


# ============ Convenience Functions ============

def load_image(path: str) -> Any:
    """Load image from file."""
    return ImageOperations.load(path)


def save_image(image: Any, path: str, quality: int = 95) -> str:
    """Save image to file."""
    return ImageOperations.save(image, path, quality=quality)


def resize_image(
    image: Any,
    width: Optional[int] = None,
    height: Optional[int] = None
) -> Any:
    """Resize image."""
    return ImageOperations.resize(image, width, height)


def create_text_image(
    text: str,
    width: int,
    height: int,
    font_size: int = 32,
    text_color: Tuple[int, int, int] = (255, 255, 255)
) -> Any:
    """Create image with text."""
    config = TextRenderConfig(
        font_size=font_size,
        text_color=(*text_color, 255)
    )
    renderer = TextRenderer(config)
    return renderer.render_text(text, width, height)
