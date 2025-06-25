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

# Test fixtures
@pytest.fixture
def setup_test_dirs():
    """
    Setup test directories and ensure they exist.
    """
    os.makedirs(TEST_IMG_DIR, exist_ok=True)
    os.makedirs(TEST_NEW_IMG_DIR, exist_ok=True)
    yield
    # Any cleanup if needed

class TestImgReshaperInit:
    """Tests for the ImgReshaper constructor."""

    def test_valid_initialization(self):
        """Test that ImgReshaper initializes correctly with valid parameters."""
        pass


class TestReshape:
    """Tests for the reshape method."""

    def test_reshape_larger_image(self, setup_test_dirs):
        """Test reshaping an image larger than target size."""
        pass

    def test_reshape_smaller_image(self, setup_test_dirs):
        """Test reshaping an image smaller than target size."""
        pass

    def test_reshape_exact_size_image(self, setup_test_dirs):
        """Test reshaping an image with exact target size."""
        pass

    def test_reshape_different_aspect_ratio(self, setup_test_dirs):
        """Test reshaping an image with different aspect ratio."""
        pass


class TestFetchImg:
    """Tests for the _fetch_img method."""

    def test_fetch_existing_image(self, setup_test_dirs):
        """Test fetching an existing image."""
        pass


class TestSaveImg:
    """Tests for the _save_img method."""

    def test_save_rgb_image(self, setup_test_dirs):
        """Test saving an RGB image."""
        pass

    def test_save_rgba_image(self, setup_test_dirs):
        """Test saving an RGBA image (should convert to RGB)."""
        pass


class TestDownscaleImg:
    """Tests for the _downscale_img method."""

    def test_downscale_larger_width_height(self):
        """Test downscaling an image larger in both dimensions."""
        pass

    def test_downscale_larger_width_only(self):
        """Test downscaling an image larger in width only."""
        pass

    def test_downscale_larger_height_only(self):
        """Test downscaling an image larger in height only."""
        pass

    def test_downscale_maintains_aspect_ratio(self):
        """Test that downscaling maintains the aspect ratio."""
        pass

class TestFillImg:
    """Tests for the _fill_img method."""

    def test_fill_smaller_image(self):
        """Test filling a smaller image with white pixels."""
        pass

    def test_fill_exact_size_image(self):
        """Test filling an image that already matches target size."""
        pass


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
