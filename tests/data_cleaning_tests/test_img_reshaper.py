# Tests for the ImgReshaper class
# Library Imports
import PIL
from PIL import Image
import pytest
import os
import tempfile

# Local Imports
from data_formatting.img_reshaper import ImgReshaper, ImgSquarer

PADDING_COLOR = (127, 127, 127)

TEST_SOURCE_DIR = "test_db/raw_db"
TEST_SOURCE_FILE = "test_db/raw_db/data.json"
TEST_SOURCE_IMG_DIR = "test_db/raw_db/images"

TEST_OUTPUT_DIR = "test_db/formatted_db"
TEST_OUTPUT_FILE = "test_db/formatted_db/data.json"
TEST_NEW_IMG_DIR = "test_db/formatted_db/images"

IMG_DIM_TO_ID = {(900,450) : "0a1e1",
                 (900, 448) : "0b5ae",
                 (900, 900) : "0b15e",
                 (500, 249) : "0bb47",
                 (500, 250) : "0beac",
                 (331, 653) : "0c80a",
                 (663,399) : "0c708"}


class TestImgReshaperInitialization:
    """Tests for ImgReshaper initialization and setup."""

    @pytest.fixture
    def valid_target_sizes(self):
        """Fixture providing various valid target size tuples."""
        return [
            (224, 224),  # Square
            (512, 256),  # Rectangular horizontal
            (256, 512),  # Rectangular vertical
            (1024, 768), # Large resolution
            (1, 1),      # Minimum valid size
        ]

    @pytest.fixture
    def expected_buffer_color(self):
        """Fixture providing the expected buffer color."""
        return PADDING_COLOR

    def test_init_valid_target_size(self, valid_target_sizes):
        """Test initialization with valid target size tuple."""
        for target_size in valid_target_sizes:
            # Should not raise any exception
            reshaper = ImgReshaper(target_size)
            assert reshaper is not None

    def test_init_sets_correct_size_attribute(self, valid_target_sizes):
        """Test that initialization correctly sets the _size attribute."""
        for target_size in valid_target_sizes:
            reshaper = ImgReshaper(target_size)
            assert reshaper._size == target_size
            assert isinstance(reshaper._size, tuple)
            assert len(reshaper._size) == 2

    def test_init_creates_buffer_image_with_correct_dimensions(self, valid_target_sizes):
        """Test that buffer image is created with target dimensions."""
        for target_size in valid_target_sizes:
            reshaper = ImgReshaper(target_size)
            assert hasattr(reshaper, '_buffer_image')
            assert isinstance(reshaper._buffer_image, PIL.Image.Image)
            assert reshaper._buffer_image.size == target_size

    def test_init_creates_buffer_image_with_correct_color(self, valid_target_sizes, expected_buffer_color):
        """Test that buffer image uses the correct background color."""
        for target_size in valid_target_sizes:
            reshaper = ImgReshaper(target_size)

            # Get a pixel from the buffer image to check the color
            pixel_color = reshaper._buffer_image.getpixel((0, 0))
            assert pixel_color == expected_buffer_color

            # Check that the image mode is RGB
            assert reshaper._buffer_image.mode == 'RGB'


class TestImgReshaperFetchImage:
    """Tests for the _fetch_img private method."""

    @pytest.fixture
    def reshaper(self):
        """Fixture providing a basic ImgReshaper instance for testing."""
        return ImgReshaper((224, 224))

    @pytest.fixture
    def valid_image_files(self):
        """Fixture providing valid image files that exist in test database."""
        # These are actual image IDs from the IMG_DIM_TO_ID mapping
        return [
            ("0a1e1", "webp"),
            ("0b5ae", "webp"),
            ("0b15e", "webp"),
            ("0bb47", "webp"),
            ("0beac", "webp")
        ]

    @pytest.fixture
    def test_image_directory(self):
        """Fixture providing the test image directory path."""
        return TEST_SOURCE_IMG_DIR

    @pytest.fixture
    def temp_test_files(self):
        """Fixture that creates temporary test files for testing."""
        temp_dir = tempfile.mkdtemp()

        # Create a valid test image
        valid_img = Image.new('RGB', (100, 100), color='red')
        valid_path = os.path.join(temp_dir, "valid_test.jpg")
        valid_img.save(valid_path)

        # Create a corrupted file (not a valid image)
        corrupted_path = os.path.join(temp_dir, "corrupted_test.jpg")
        with open(corrupted_path, 'wb') as f:
            f.write(b"This is not an image file")

        # Create test files with different extensions
        png_img = Image.new('RGB', (50, 50), color='blue')
        png_path = os.path.join(temp_dir, "test_png.png")
        png_img.save(png_path)

        webp_img = Image.new('RGB', (75, 75), color='green')
        webp_path = os.path.join(temp_dir, "test_webp.webp")
        webp_img.save(webp_path)

        yield {
            'directory': temp_dir,
            'valid': ('valid_test', 'jpg'),
            'corrupted': ('corrupted_test', 'jpg'),
            'png': ('test_png', 'png'),
            'webp': ('test_webp', 'webp')
        }

        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)

    def test_fetch_img_valid_file_returns_image(self, reshaper,
                                                valid_image_files,
                                                test_image_directory):
        """Test fetching a valid image file returns PIL Image object."""
        for img_name, extension in valid_image_files:
            result = reshaper._fetch_img(img_name, test_image_directory,
                                         extension)
            assert isinstance(result, PIL.Image.Image)
            assert result.size[0] > 0  # Width should be positive
            assert result.size[1] > 0  # Height should be positive

    def test_fetch_img_nonexistent_file_raises_file_not_found_error(self, reshaper, test_image_directory):
        """Test that fetching non-existent file raises FileNotFoundError."""
        nonexistent_files = [
            ("nonexistent_image", "jpg"),
            ("missing_file", "webp"),
            ("does_not_exist", "png")
        ]

        for img_name, extension in nonexistent_files:
            with pytest.raises(FileNotFoundError) as exc_info:
                reshaper._fetch_img(img_name, test_image_directory, extension)

            # Verify the error message contains relevant information
            assert img_name in str(exc_info.value)
            assert "Error loading image" in str(exc_info.value)

    def test_fetch_img_invalid_directory_raises_file_not_found_error(self, reshaper, valid_image_files):
        """Test that invalid directory path raises FileNotFoundError."""
        invalid_directories = [
            "/path/that/does/not/exist",
            "nonexistent_directory",
            "/invalid/directory/path"
        ]

        img_name, extension = valid_image_files[0]  # Use any valid image name

        for invalid_dir in invalid_directories:
            with pytest.raises(FileNotFoundError) as exc_info:
                reshaper._fetch_img(img_name, invalid_dir, extension)

            # Verify the error message contains relevant information
            assert "Error loading image" in str(exc_info.value)

    def test_fetch_img_corrupted_file_raises_exception(self, reshaper, temp_test_files):
        """Test that corrupted image file raises appropriate exception."""
        img_name, extension = temp_test_files['corrupted']
        directory = temp_test_files['directory']

        with pytest.raises(FileNotFoundError) as exc_info:
            reshaper._fetch_img(img_name, directory, extension)

        # Verify the error contains information about the failure
        error_msg = str(exc_info.value)
        assert "Error loading image" in error_msg
        assert img_name in error_msg

    def test_fetch_img_different_extensions(self, reshaper, temp_test_files):
        """Test fetching images with different file extensions (jpg, png, webp, etc.)."""
        test_cases = [
            temp_test_files['valid'],   # JPG
            temp_test_files['png'],     # PNG
            temp_test_files['webp']     # WebP
        ]

        directory = temp_test_files['directory']

        for img_name, extension in test_cases:
            # Should successfully fetch the image
            result = reshaper._fetch_img(img_name, directory, extension)

            # Verify it's a valid PIL Image
            assert isinstance(result, Image.Image)
            assert result.size[0] > 0
            assert result.size[1] > 0

    def test_fetch_img_preserves_image_properties(self, reshaper, temp_test_files):
        """Test that fetched images preserve their original properties."""
        # Test with the created valid image
        img_name, extension = temp_test_files['valid']
        directory = temp_test_files['directory']

        result = reshaper._fetch_img(img_name, directory, extension)

        # The original image was created as 100x100 RGB
        assert result.size == (100, 100)
        assert result.mode in ['RGB', 'RGBA']  # PIL might convert mode during loading

    def test_fetch_img_handles_case_sensitivity(self, reshaper, temp_test_files):
        """Test that file extension handling works correctly."""
        # Test with uppercase extension
        img_name, _ = temp_test_files['valid']
        directory = temp_test_files['directory']

        # This should work with lowercase extension
        result = reshaper._fetch_img(img_name, directory, 'jpg')
        assert isinstance(result, Image.Image)

        # Test that wrong extension fails appropriately
        with pytest.raises(FileNotFoundError):
            reshaper._fetch_img(img_name, directory, 'png')  # Wrong extension


class TestImgReshaperSaveImage:
    """Tests for the _save_img private method."""

    @pytest.fixture
    def reshaper(self):
        """Fixture providing a basic ImgReshaper instance for testing."""
        return ImgReshaper((224, 224))

    @pytest.fixture
    def temp_directory(self):
        """Fixture that creates a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def test_images(self):
        """Fixture providing test images with different modes."""
        # RGB image
        rgb_img = Image.new('RGB', (100, 100), color='red')

        # RGBA image with transparency
        rgba_img = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))

        # PNG with transparency
        png_img = Image.new('RGBA', (100, 100), color=(0, 255, 0, 200))

        return {
            'rgb': rgb_img,
            'rgba': rgba_img,
            'png_transparent': png_img
        }

    def test_save_img_creates_output_directory_if_not_exists(self, reshaper,
                                                             temp_directory,
                                                             test_images):
        """Test that output directory is created if it doesn't exist."""
        # Create a subdirectory path that doesn't exist yet
        non_existent_dir = os.path.join(temp_directory, "new_directory",
                                        "subdirectory")

        # Ensure the directory doesn't exist
        assert not os.path.exists(non_existent_dir)

        # Save an image to the non-existent directory
        test_img = test_images['rgb']
        saved_path = reshaper._save_img(test_img, "test_image",
                                        non_existent_dir, "jpeg")

        # Verify the directory was created
        assert os.path.exists(non_existent_dir)
        assert os.path.isdir(non_existent_dir)

        # Verify the image was saved
        assert os.path.exists(saved_path)
        assert saved_path == os.path.join(non_existent_dir, "test_image.jpeg")

    def test_save_img_saves_with_correct_filename(self, reshaper, temp_directory, test_images):
        """Test that image is saved with the correct filename and extension."""
        test_cases = [
            ("test_image", "jpg"),
            ("another_image", "png"),
            ("webp_image", "webp"),
            ("image_with_numbers_123", "jpeg")
        ]

        test_img = test_images['rgb']

        for image_name, extension in test_cases:
            saved_path = reshaper._save_img(test_img, image_name, temp_directory, extension)

            expected_filename = f"{image_name}.{extension}"
            expected_path = os.path.join(temp_directory, expected_filename)

            # Verify the returned path is correct
            assert saved_path == expected_path

            # Verify the file exists
            assert os.path.exists(saved_path)

            # Verify it's a valid image file
            saved_img = Image.open(saved_path)
            assert isinstance(saved_img, Image.Image)
            saved_img.close()

    def test_save_img_converts_rgba_to_rgb_for_jpg(self, reshaper, temp_directory, test_images):
        """Test that RGBA images are converted to RGB when saving as JPG."""
        rgba_img = test_images['rgba']

        # Verify the original image is RGBA
        assert rgba_img.mode == 'RGBA'

        # Save as JPG (which doesn't support transparency)
        saved_path = reshaper._save_img(rgba_img, "rgba_test", temp_directory, "jpg")

        # Load the saved image and verify it's RGB
        saved_img = Image.open(saved_path)
        assert saved_img.mode == 'RGB'

        # Verify the image dimensions are preserved
        assert saved_img.size == rgba_img.size

        saved_img.close()

        # Test with other formats that don't support transparency
        for extension in ['jpeg', 'bmp']:
            saved_path = reshaper._save_img(rgba_img, f"rgba_test_{extension}", temp_directory, extension)
            saved_img = Image.open(saved_path)
            assert saved_img.mode == 'RGB'
            saved_img.close()

    def test_save_img_preserves_transparency_for_png(self, reshaper, temp_directory, test_images):
        """Test that transparency is preserved when saving as PNG."""
        rgba_img = test_images['png_transparent']

        # Verify the original image has transparency
        assert rgba_img.mode == 'RGBA'

        # Save as PNG (which supports transparency)
        saved_path = reshaper._save_img(rgba_img, "transparent_test", temp_directory, "png")

        # Load the saved image and verify transparency is preserved
        saved_img = Image.open(saved_path)
        assert saved_img.mode in ['RGBA', 'P']  # PNG can be RGBA or palette with transparency

        # Verify the image dimensions are preserved
        assert saved_img.size == rgba_img.size

        saved_img.close()

        # Test with GIF which also supports transparency
        saved_path = reshaper._save_img(rgba_img, "transparent_gif", temp_directory, "gif")
        saved_img = Image.open(saved_path)
        # GIF might convert to P mode with transparency
        assert saved_img.mode in ['RGBA', 'P']
        saved_img.close()


class TestImgReshaperImageSizeChecks:
    """Tests for image size comparison methods."""

    @pytest.fixture
    def reshaper(self):
        """Fixture providing a basic ImgReshaper instance with a standard target size."""
        return ImgReshaper((224, 224))

    @pytest.fixture
    def rectangular_reshaper(self):
        """Fixture providing a reshaper with rectangular target size."""
        return ImgReshaper((400, 300))

    @pytest.fixture
    def test_images(self):
        """Fixture providing test images with various dimensions."""
        return {
            # Images larger in width only
            'wider': Image.new('RGB', (300, 200), color='red'),
            'much_wider': Image.new('RGB', (500, 100), color='blue'),

            # Images larger in height only
            'taller': Image.new('RGB', (200, 300), color='green'),
            'much_taller': Image.new('RGB', (100, 500), color='yellow'),

            # Images larger in both dimensions
            'larger_both': Image.new('RGB', (300, 300), color='purple'),
            'much_larger_both': Image.new('RGB', (500, 400), color='orange'),

            # Images smaller in both dimensions
            'smaller_both': Image.new('RGB', (100, 100), color='cyan'),
            'much_smaller_both': Image.new('RGB', (50, 80), color='magenta'),

            # Images with exact dimensions
            'exact_match': Image.new('RGB', (224, 224), color='white'),

            # Mixed cases
            'wider_shorter': Image.new('RGB', (300, 150), color='black'),
            'narrower_taller': Image.new('RGB', (150, 300), color='gray'),
        }

    def test_is_larger_returns_true_when_width_exceeds_target(self, reshaper, test_images):
        """Test _is_larger returns True when image width exceeds target."""
        # Test with images that have width > target width
        wider_images = ['wider', 'much_wider', 'larger_both', 'much_larger_both', 'wider_shorter']

        for img_key in wider_images:
            img = test_images[img_key]
            result = reshaper._is_larger(img)
            assert result is True, f"Expected True for {img_key} with size {img.size}, target {reshaper._size}"

    def test_is_larger_returns_true_when_height_exceeds_target(self, reshaper, test_images):
        """Test _is_larger returns True when image height exceeds target."""
        # Test with images that have height > target height
        taller_images = ['taller', 'much_taller', 'larger_both', 'much_larger_both', 'narrower_taller']

        for img_key in taller_images:
            img = test_images[img_key]
            result = reshaper._is_larger(img)
            assert result is True, f"Expected True for {img_key} with size {img.size}, target {reshaper._size}"

    def test_is_larger_returns_true_when_both_dimensions_exceed_target(self, reshaper, test_images):
        """Test _is_larger returns True when both dimensions exceed target."""
        # Test with images that have both width > target width AND height > target height
        larger_both_images = ['larger_both', 'much_larger_both']

        for img_key in larger_both_images:
            img = test_images[img_key]
            result = reshaper._is_larger(img)
            assert result is True, f"Expected True for {img_key} with size {img.size}, target {reshaper._size}"

            # Verify both dimensions are indeed larger
            assert img.size[0] > reshaper._size[0], f"Width should be larger: {img.size[0]} > {reshaper._size[0]}"
            assert img.size[1] > reshaper._size[1], f"Height should be larger: {img.size[1]} > {reshaper._size[1]}"

    def test_is_larger_returns_false_when_image_fits_within_target(self, reshaper, test_images):
        """Test _is_larger returns False when image fits within target size."""
        # Test with images that have both dimensions <= target dimensions
        fitting_images = ['smaller_both', 'much_smaller_both', 'exact_match']

        for img_key in fitting_images:
            img = test_images[img_key]
            result = reshaper._is_larger(img)
            assert result is False, f"Expected False for {img_key} with size {img.size}, target {reshaper._size}"

            # Verify both dimensions are indeed within target
            assert img.size[0] <= reshaper._size[0], f"Width should be <= target: {img.size[0]} <= {reshaper._size[0]}"
            assert img.size[1] <= reshaper._size[1], f"Height should be <= target: {img.size[1]} <= {reshaper._size[1]}"

    def test_is_smaller_returns_true_when_both_dimensions_below_target(self, reshaper, test_images):
        """Test _is_smaller returns True when both dimensions are below target."""
        # Test with images that have both width < target width AND height < target height
        smaller_images = ['smaller_both', 'much_smaller_both']

        for img_key in smaller_images:
            img = test_images[img_key]
            result = reshaper._is_smaller(img)
            assert result is True, f"Expected True for {img_key} with size {img.size}, target {reshaper._size}"

            # Verify both dimensions are indeed smaller
            assert img.size[0] < reshaper._size[0], f"Width should be smaller: {img.size[0]} < {reshaper._size[0]}"
            assert img.size[1] < reshaper._size[1], f"Height should be smaller: {img.size[1]} < {reshaper._size[1]}"

    def test_is_smaller_returns_false_when_width_equals_target(self, reshaper):
        """Test _is_smaller returns False when width equals target."""
        # Create image with width = target width but height < target height
        img = Image.new('RGB', (reshaper._size[0], reshaper._size[1] - 50), color='red')

        result = reshaper._is_smaller(img)
        assert result is False, f"Expected False when width equals target: {img.size} vs {reshaper._size}"

        # Verify the condition: width equals, height is smaller
        assert img.size[0] == reshaper._size[0], "Width should equal target"
        assert img.size[1] < reshaper._size[1], "Height should be smaller than target"

    def test_is_smaller_returns_false_when_height_equals_target(self, reshaper):
        """Test _is_smaller returns False when height equals target."""
        # Create image with height = target height but width < target width
        img = Image.new('RGB', (reshaper._size[0] - 50, reshaper._size[1]), color='blue')

        result = reshaper._is_smaller(img)
        assert result is False, f"Expected False when height equals target: {img.size} vs {reshaper._size}"

        # Verify the condition: height equals, width is smaller
        assert img.size[0] < reshaper._size[0], "Width should be smaller than target"
        assert img.size[1] == reshaper._size[1], "Height should equal target"

    def test_is_smaller_returns_false_when_any_dimension_exceeds_target(self, reshaper, test_images):
        """Test _is_smaller returns False when any dimension exceeds target."""
        # Test with images that have at least one dimension >= target dimension
        non_smaller_images = [
            'wider', 'much_wider', 'taller', 'much_taller',
            'larger_both', 'much_larger_both', 'exact_match',
            'wider_shorter', 'narrower_taller'
        ]

        for img_key in non_smaller_images:
            img = test_images[img_key]
            result = reshaper._is_smaller(img)
            assert result is False, f"Expected False for {img_key} with size {img.size}, target {reshaper._size}"

            # Verify that at least one dimension is >= target
            width_condition = img.size[0] >= reshaper._size[0]
            height_condition = img.size[1] >= reshaper._size[1]
            assert width_condition or height_condition, f"At least one dimension should be >= target for {img_key}"

    def test_size_checks_with_rectangular_target(self, rectangular_reshaper):
        """Test size check methods work correctly with non-square target dimensions."""
        target_width, target_height = rectangular_reshaper._size  # (400, 300)

        # Test cases for rectangular target
        test_cases = [
            # (width, height, expected_is_larger, expected_is_smaller, description)
            (450, 250, True, False, "wider but shorter"),
            (350, 350, True, False, "narrower but taller"),
            (450, 350, True, False, "both dimensions larger"),
            (350, 250, False, True, "both dimensions smaller"),
            (400, 300, False, False, "exact match"),
            (400, 250, False, False, "exact width, smaller height"),
            (350, 300, False, False, "smaller width, exact height"),
        ]

        for width, height, expected_larger, expected_smaller, description in test_cases:
            img = Image.new('RGB', (width, height), color='white')

            is_larger_result = rectangular_reshaper._is_larger(img)
            is_smaller_result = rectangular_reshaper._is_smaller(img)

            assert is_larger_result == expected_larger, \
                f"_is_larger failed for {description}: {(width, height)} vs {(target_width, target_height)}"
            assert is_smaller_result == expected_smaller, \
                f"_is_smaller failed for {description}: {(width, height)} vs {(target_width, target_height)}"

    def test_edge_cases_size_checks(self):
        """Test edge cases for size checking methods."""
        # Test with very small target size
        small_reshaper = ImgReshaper((1, 1))

        # Any image larger than 1x1 should be considered larger
        larger_img = Image.new('RGB', (2, 1), color='red')
        assert small_reshaper._is_larger(larger_img) is True
        assert small_reshaper._is_smaller(larger_img) is False

        # 1x1 image should not be larger or smaller
        exact_img = Image.new('RGB', (1, 1), color='blue')
        assert small_reshaper._is_larger(exact_img) is False
        assert small_reshaper._is_smaller(exact_img) is False

        # Test with large target size
        large_reshaper = ImgReshaper((1000, 1000))

        # Most normal images should be smaller
        normal_img = Image.new('RGB', (500, 500), color='green')
        assert large_reshaper._is_larger(normal_img) is False
        assert large_reshaper._is_smaller(normal_img) is True


class TestImgReshaperImageScaling:
    """Tests for image scaling operations."""

    @pytest.fixture
    def reshaper(self):
        """Fixture providing a basic ImgReshaper instance for testing."""
        return ImgReshaper((224, 224))

    @pytest.fixture
    def rectangular_reshaper(self):
        """Fixture providing a reshaper with rectangular target size."""
        return ImgReshaper((400, 300))

    @pytest.fixture
    def test_images(self):
        """Fixture providing test images for scaling operations."""
        return {
            # Large images that need downscaling
            'large_square': Image.new('RGB', (500, 500), color='red'),
            'large_wide': Image.new('RGB', (800, 400), color='blue'),
            'large_tall': Image.new('RGB', (300, 600), color='green'),

            # Small images that need upscaling
            'small_square': Image.new('RGB', (100, 100), color='yellow'),
            'small_wide': Image.new('RGB', (150, 75), color='purple'),
            'small_tall': Image.new('RGB', (80, 160), color='orange'),

            # Exact size images
            'exact_match': Image.new('RGB', (224, 224), color='white'),
        }

    def test_downscale_img_maintains_aspect_ratio(self, reshaper, test_images):
        """Test that downscaling maintains the original aspect ratio."""
        test_cases = ['large_square', 'large_wide', 'large_tall']

        for img_key in test_cases:
            original_img = test_images[img_key]
            original_ratio = original_img.size[0] / original_img.size[1]

            downscaled_img = reshaper._downscale_img(original_img)
            downscaled_ratio = downscaled_img.size[0] / downscaled_img.size[1]

            # Check that aspect ratio is preserved (within floating point tolerance)
            assert abs(original_ratio - downscaled_ratio) < 0.01, \
                f"Aspect ratio not preserved for {img_key}: {original_ratio} vs {downscaled_ratio}"

    def test_downscale_img_fits_within_target_size(self, reshaper, test_images):
        """Test that downscaled image fits within target dimensions."""
        test_cases = ['large_square', 'large_wide', 'large_tall']

        for img_key in test_cases:
            original_img = test_images[img_key]
            downscaled_img = reshaper._downscale_img(original_img)

            # Check that both dimensions fit within target size
            assert downscaled_img.size[0] <= reshaper._size[0], \
                f"Width exceeds target for {img_key}: {downscaled_img.size[0]} > {reshaper._size[0]}"
            assert downscaled_img.size[1] <= reshaper._size[1], \
                f"Height exceeds target for {img_key}: {downscaled_img.size[1]} > {reshaper._size[1]}"

            # Check that at least one dimension matches the target (for proper scaling)
            width_matches = downscaled_img.size[0] == reshaper._size[0]
            height_matches = downscaled_img.size[1] == reshaper._size[1]
            assert width_matches or height_matches, \
                f"No dimension matches target for {img_key}: {downscaled_img.size} vs {reshaper._size}"

    def test_upscale_img_maintains_aspect_ratio(self, reshaper, test_images):
        """Test that upscaling maintains the original aspect ratio."""
        test_cases = ['small_square', 'small_wide', 'small_tall']

        for img_key in test_cases:
            original_img = test_images[img_key]
            original_ratio = original_img.size[0] / original_img.size[1]

            upscaled_img = reshaper._upscale_img(original_img)
            upscaled_ratio = upscaled_img.size[0] / upscaled_img.size[1]

            # Check that aspect ratio is preserved (within floating point tolerance)
            assert abs(original_ratio - upscaled_ratio) < 0.01, \
                f"Aspect ratio not preserved for {img_key}: {original_ratio} vs {upscaled_ratio}"

    def test_upscale_img_at_least_one_dimension_matches_target(self, reshaper, test_images):
        """Test that upscaled image has at least one dimension matching target."""
        test_cases = ['small_square', 'small_wide', 'small_tall']

        for img_key in test_cases:
            original_img = test_images[img_key]
            upscaled_img = reshaper._upscale_img(original_img)

            # Check that at least one dimension matches or exceeds the target
            width_condition = upscaled_img.size[0] >= reshaper._size[0]
            height_condition = upscaled_img.size[1] >= reshaper._size[1]
            assert width_condition or height_condition, \
                f"No dimension reaches target for {img_key}: {upscaled_img.size} vs {reshaper._size}"

            # For proper upscaling, at least one dimension should match exactly
            width_matches = abs(upscaled_img.size[0] - reshaper._size[0]) <= 1  # Allow for rounding
            height_matches = abs(upscaled_img.size[1] - reshaper._size[1]) <= 1
            assert width_matches or height_matches, \
                f"No dimension matches target exactly for {img_key}: {upscaled_img.size} vs {reshaper._size}"

    def test_rescale_image_calls_downscale_for_larger_images(self, reshaper, test_images):
        """Test that _rescale_image calls downscale for images larger than target."""
        test_cases = ['large_square', 'large_wide', 'large_tall']

        for img_key in test_cases:
            original_img = test_images[img_key]

            # Verify the image is indeed larger than target
            assert reshaper._is_larger(original_img), f"{img_key} should be larger than target"

            rescaled_img = reshaper._rescale_image(original_img)

            # Check that the image was downscaled (both dimensions should be <= target)
            assert rescaled_img.size[0] <= reshaper._size[0], \
                f"Width not downscaled for {img_key}: {rescaled_img.size[0]} > {reshaper._size[0]}"
            assert rescaled_img.size[1] <= reshaper._size[1], \
                f"Height not downscaled for {img_key}: {rescaled_img.size[1]} > {reshaper._size[1]}"

    def test_rescale_image_calls_upscale_for_smaller_images(self, reshaper, test_images):
        """Test that _rescale_image calls upscale for images smaller than target."""
        test_cases = ['small_square', 'small_wide', 'small_tall']

        for img_key in test_cases:
            original_img = test_images[img_key]

            # Verify the image is indeed smaller than target
            assert reshaper._is_smaller(original_img), f"{img_key} should be smaller than target"

            rescaled_img = reshaper._rescale_image(original_img)

            # Check that the image was upscaled (at least one dimension should match target)
            width_condition = rescaled_img.size[0] >= reshaper._size[0]
            height_condition = rescaled_img.size[1] >= reshaper._size[1]
            assert width_condition or height_condition, \
                f"Image not properly upscaled for {img_key}: {rescaled_img.size} vs {reshaper._size}"

    def test_rescale_image_no_change_for_exact_size_match(self, reshaper, test_images):
        """Test that images matching target size are not rescaled."""
        exact_img = test_images['exact_match']

        # Verify the image exactly matches target size
        assert exact_img.size == reshaper._size, "Test image should exactly match target size"
        assert not reshaper._is_larger(exact_img), "Exact match should not be larger"
        assert not reshaper._is_smaller(exact_img), "Exact match should not be smaller"

        rescaled_img = reshaper._rescale_image(exact_img)

        # Check that the image dimensions remain unchanged
        assert rescaled_img.size == exact_img.size, \
            f"Exact match image was modified: {rescaled_img.size} vs {exact_img.size}"

