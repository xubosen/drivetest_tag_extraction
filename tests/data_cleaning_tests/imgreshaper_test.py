# Tests for the ImgReshaper class

# Library Imports
import pytest
from PIL import Image
import os
# Do not import mock

# Local Imports
from data_cleaning.img_reshaper import ImgReshaper

TEST_IMG_DIR = "test_db/img"
TEST_NEW_IMG_DIR = "test_db/new_img"
VALID_IMG_NAMES = ["331x653",
                   "500x249",
                   "500x250",
                   "663x399",
                   "900x450",
                   "900x900"]


def _load_image(img_path) -> Image:
    """
    Helper function to load a saved image.

    :param img_path: Path to the saved image
    :return: PIL Image object of the loaded image
    """
    try:
        return Image.open(img_path)
    except Exception as e:
        pytest.fail(f"Failed to load saved image at {img_path}: {e}")

class TestImgReshaperInit:
    """Tests for the ImgReshaper constructor."""

    def test_valid_initialization(self):
        """Test that ImgReshaper initializes correctly with valid parameters."""
        pass


class TestReshape:
    """Tests for the reshape method."""

    def test_reshape_larger_image(self):
        """Test reshaping an image larger than target size."""
        pass

    def test_reshape_smaller_image(self):
        """Test reshaping an image smaller than target size."""
        pass

    def test_reshape_exact_size_image(self):
        """Test reshaping an image with exact target size."""
        pass

    def test_reshape_different_aspect_ratio(self):
        """Test reshaping an image with different aspect ratio."""
        pass


class TestFetchImg:
    """Tests for the _fetch_img method."""

    def test_fetch_existing_image(self):
        """Test fetching an existing image."""
        pass


class TestSaveImg:
    """Tests for the _save_img method."""

    def test_save_rgb_image(self):
        """Test saving an RGB image."""
        # Create directories if they don't exist
        os.makedirs(TEST_NEW_IMG_DIR, exist_ok=True)

        # Create a reshaper
        reshaper = ImgReshaper((400, 300))

        # Create a test RGB image
        test_img = Image.new('RGB', (400, 300), color=(255, 0, 0))  # Red image

        # Generate a unique image name
        img_name = "test_rgb_image"
        img_path = os.path.join(TEST_NEW_IMG_DIR, f"{img_name}.jpg")

        # Save the image
        reshaper._save_img(test_img, TEST_NEW_IMG_DIR, img_name)

        # Verify the image was saved
        assert os.path.exists(img_path)

        # Load the saved image and verify its properties
        saved_img = _load_image(img_path)

        assert saved_img.mode == 'RGB'
        assert saved_img.size == (400, 300)

        # Verify image content (sample a pixel to ensure it's still red)
        # Note: Some slight color variation may occur due to JPEG compression
        red_value = saved_img.getpixel((200, 150))[0]
        assert red_value > 250  # Should still be very red

        # Clean up the test file
        os.remove(img_path)

    def test_save_rgba_image(self):
        """Test saving an RGBA image (should convert to RGB)."""
        # Create directories if they don't exist
        os.makedirs(TEST_NEW_IMG_DIR, exist_ok=True)

        # Create a reshaper
        reshaper = ImgReshaper((400, 300))

        # Create a test RGBA image with transparency
        test_img = Image.new('RGBA', (400, 300), color=(0, 255, 0, 128))  # Semi-transparent green

        # Generate a unique image name
        img_name = "test_rgba_image"
        img_path = os.path.join(TEST_NEW_IMG_DIR, f"{img_name}.jpg")

        # Save the image
        reshaper._save_img(test_img, TEST_NEW_IMG_DIR, img_name)

        # Verify the image was saved
        assert os.path.exists(img_path)

        # Load the saved image and verify its properties
        saved_img = _load_image(img_path)

        # Verify the image was converted to RGB (no alpha channel)
        assert saved_img.mode == 'RGB'
        assert saved_img.size == (400, 300)

        # Verify image content (should have preserved the green component)
        green_value = saved_img.getpixel((200, 150))[1]
        assert green_value > 250  # Should still be very green

        # Clean up the test file
        os.remove(img_path)


class TestDownscaleImg:
    """Tests for the _downscale_img method."""

    def test_downscale_larger_width_height(self):
        """Test downscaling an image larger in both dimensions."""
        # Create a reshaper with target size (400, 300)
        reshaper = ImgReshaper((400, 300))

        # Create a test image that is larger in both dimensions (800, 600)
        test_img = Image.new('RGB', (800, 600), color=(100, 100, 100))

        # Downscale the image
        result = reshaper._downscale_img(test_img)

        # Verify the result fits within target dimensions
        assert result.width <= 400
        assert result.height <= 300

        # Verify aspect ratio is maintained (should be 400x300)
        assert result.width == 400
        assert result.height == 300

    def test_downscale_larger_width_only(self):
        """Test downscaling an image larger in width only."""
        # Create a reshaper with target size (400, 300)
        reshaper = ImgReshaper((400, 300))

        # Create a test image larger in width only (800, 200)
        test_img = Image.new('RGB', (800, 200), color=(100, 100, 100))

        # Downscale the image
        result = reshaper._downscale_img(test_img)

        # Verify the width is reduced to fit within target size
        assert result.width <= 400

        # Verify aspect ratio is maintained
        # Original aspect ratio: 800/200 = 4
        # New width should be 400, so height should be 400/4 = 100
        assert result.width == 400
        assert result.height == 100

    def test_downscale_larger_height_only(self):
        """Test downscaling an image larger in height only."""
        # Create a reshaper with target size (400, 300)
        reshaper = ImgReshaper((400, 300))

        # Create a test image larger in height only (300, 600)
        test_img = Image.new('RGB', (300, 600), color=(100, 100, 100))

        # Downscale the image
        result = reshaper._downscale_img(test_img)

        # Verify the height is reduced to fit within target size
        assert result.height <= 300

        # Verify aspect ratio is maintained
        # Original aspect ratio: 300/600 = 0.5
        # New height should be 300, so width should be 300*0.5 = 150
        assert result.width == 150
        assert result.height == 300


class TestFillImg:
    """Tests for the _fill_img method."""

    def test_fill_smaller_image(self):
        """Test filling a smaller image with white pixels."""
        # Create a reshaper with target size (400, 300)
        reshaper = ImgReshaper((400, 300))

        # Create a smaller test image (200, 150) with a colored rectangle
        img = Image.new('RGB', (200, 150), (0, 0, 0))  # Black image

        # Fill the image to match target size
        filled_img = reshaper._fill_img(img)

        # Verify the result has the correct size
        assert filled_img.size == (400, 300)

        # Verify the image is centered - check corner pixels are white
        assert filled_img.getpixel((0, 0)) == (255, 255, 255)  # Top-left
        assert filled_img.getpixel((399, 0)) == (255, 255, 255)  # Top-right
        assert filled_img.getpixel((0, 299)) == (255, 255, 255)  # Bottom-left
        assert filled_img.getpixel((399, 299)) == (255, 255, 255)  # Bottom-right

        # Calculate where the original image should be placed
        paste_x = (400 - 200) // 2  # = 100
        paste_y = (300 - 150) // 2  # = 75

        # Verify center of pasted image is black
        assert filled_img.getpixel((paste_x + 100, paste_y + 75)) == (0, 0, 0)  # Center

    def test_fill_exact_size_image(self):
        """Test filling an image that already matches target size."""
        # Create a reshaper with target size (400, 300)
        reshaper = ImgReshaper((400, 300))

        # Create an image with exact target size
        original_img = Image.new('RGB', (400, 300), (100, 150, 200))  # Blue-ish image

        # Fill the image
        filled_img = reshaper._fill_img(original_img)

        # Verify the image is returned unchanged (same size)
        assert filled_img.size == (400, 300)

        # Check a few pixels to make sure content is preserved
        assert filled_img.getpixel((0, 0)) == (100, 150, 200)
        assert filled_img.getpixel((399, 299)) == (100, 150, 200)

        # For exact-sized images, the original image should be returned directly
        # We can verify this by checking if the images have the same content
        assert filled_img.tobytes() == original_img.tobytes()

class TestIsLarger:
    """Tests for the _is_larger method."""

    def test_larger_width_height(self):
        """Test detection of image larger in both dimensions."""
        # Create a reshaper with target size (400, 300)
        reshaper = ImgReshaper((400, 300))

        # Create an image larger in both dimensions (500, 400)
        img = Image.new('RGB', (500, 400))

        # Test the _is_larger method
        assert reshaper._is_larger(img) is True

    def test_larger_width_only(self):
        """Test detection of image larger in width only."""
        # Create a reshaper with target size (400, 300)
        reshaper = ImgReshaper((400, 300))

        # Create an image larger in width only (500, 200)
        img = Image.new('RGB', (500, 200))

        # Test the _is_larger method
        assert reshaper._is_larger(img) is True

    def test_larger_height_only(self):
        """Test detection of image larger in height only."""
        # Create a reshaper with target size (400, 300)
        reshaper = ImgReshaper((400, 300))

        # Create an image larger in height only (300, 400)
        img = Image.new('RGB', (300, 400))

        # Test the _is_larger method
        assert reshaper._is_larger(img) is True

    def test_smaller_image(self):
        """Test detection of image smaller in both dimensions."""
        # Create a reshaper with target size (400, 300)
        reshaper = ImgReshaper((400, 300))

        # Create an image smaller in both dimensions (300, 200)
        img = Image.new('RGB', (300, 200))

        # Test the _is_larger method
        assert reshaper._is_larger(img) is False

    def test_exact_size_image(self):
        """Test detection of image with exact target size."""
        # Create a reshaper with target size (400, 300)
        reshaper = ImgReshaper((400, 300))

        # Create an image with exact target size (400, 300)
        img = Image.new('RGB', (400, 300))

        # Test the _is_larger method
        assert reshaper._is_larger(img) is False
