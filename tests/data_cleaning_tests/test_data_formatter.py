import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
from pydantic import ValidationError

from data_formatting.data_formatter import (DataFormatter, DataFormat,
                                            MIN_IMG_SIZE)
from entities.question_bank import QuestionBank
from entities.question import Question


# Test constants
DEFAULT_IMAGE_SHAPE = (256, 256)
DUMMY_IMAGE = Image.new('RGB', DEFAULT_IMAGE_SHAPE, color='blue')
VALID_EXTENSIONS = ["jpg", "jpeg", "webp", "png", "bmp", "gif"]
INVALID_EXTENSIONS = ["tiff", "svg", "pdf", "txt", "xyz"]


# Fixtures for reusable test data
@pytest.fixture
def sample_data_format():
    """Create a sample DataFormat for testing."""
    return DataFormat(
        input_image_extension="jpg",
        output_image_extension="png"
    )


@pytest.fixture
def temp_directories():
    """Create temporary directories for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = os.path.join(temp_dir, "input")
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        yield input_dir, output_dir


@pytest.fixture
def sample_question_with_image(temp_directories):
    """Create a sample Question with an image path."""
    input_dir, _ = temp_directories
    test_img_name = "test_q1"
    test_img_path = os.path.join(input_dir, f"{test_img_name}.jpg")
    DUMMY_IMAGE.save(test_img_path)
    return Question(
        qid=test_img_name,
        question="Sample question?",
        answers={"A", "B", "C", "D"},
        correct_answer="A",
        img_path=test_img_path
    )

@pytest.fixture
def sample_question_without_image():
    """Create a sample Question without an image."""
    return Question(
        qid="test_q2",
        question="Sample question without image?",
        answers={"A", "B", "C", "D"},
        correct_answer="B"
    )

@pytest.fixture
def sample_question_bank(temp_directories, sample_question_with_image,
                         sample_question_without_image):
    """Create a sample QuestionBank for testing."""
    input_dir, _ = temp_directories

    # Create the question bank
    qb = QuestionBank(img_dir=input_dir)
    qb.add_chapter(1, "Test Chapter")
    qb.add_question(sample_question_with_image, 1)
    qb.add_question(sample_question_without_image, 1)

    return qb

def _create_mock_reshaper(temp_directories,
                          qid: str = "test_q1",
                          extension: str = "png"):
    """Helper function to create a mock ImgReshaper."""
    _, output_dir = temp_directories
    mock_reshaper = Mock()
    img_path = os.path.join(output_dir, f"{qid}.{extension}")
    DUMMY_IMAGE.save(img_path)
    mock_reshaper.reshape.return_value = img_path
    return mock_reshaper


class TestDataFormat:
    def setup_method(self):
        self._image_shape_error = "Image shape values must be" \
                                  " integers greater than or equal " \
                                  "to"

    def test_data_format_valid_creation(self):
        """
        Test that DataFormat can be created with valid parameters.
        Should create a DataFormat instance with default image shape (256, 256)
        and provided valid extensions.
        """
        # Test with default image shape
        data_format = DataFormat(
            input_image_extension="jpg",
            output_image_extension="png"
        )
        assert data_format.image_shape == (256, 256)
        assert data_format.input_image_extension == "jpg"
        assert data_format.output_image_extension == "png"

    def test_data_format_custom_image_shape(self):
        """
        Test that DataFormat accepts custom image shapes.
        Should allow creation with different valid image dimensions.
        """
        # Test with custom valid dimensions
        data_format = DataFormat(
            image_shape=(128, 128),
            input_image_extension="jpeg",
            output_image_extension="webp"
        )
        assert data_format.image_shape == (128, 128)
        assert data_format.input_image_extension == "jpeg"
        assert data_format.output_image_extension == "webp"

        # Test with different valid dimensions
        data_format2 = DataFormat(
            image_shape=(512, 384),
            input_image_extension="png",
            output_image_extension="bmp"
        )
        assert data_format2.image_shape == (512, 384)

    def test_data_format_invalid_image_shape_length(self):
        """
        Test that DataFormat rejects image shapes that are not tuples of length 2.
        Should raise ValueError for tuples with length != 2.
        """
        # Test with single value
        with pytest.raises(ValidationError):
            DataFormat(
                image_shape=(256,),
                input_image_extension="jpg",
                output_image_extension="png"
            )

        # Test with three values
        with pytest.raises(ValidationError):
            DataFormat(
                image_shape=(256, 256, 256),
                input_image_extension="jpg",
                output_image_extension="png"
            )

        # Test with empty tuple
        with pytest.raises(ValidationError):
            DataFormat(
                image_shape=(),
                input_image_extension="jpg",
                output_image_extension="png"
            )

    def test_data_format_invalid_image_shape_negative(self):
        """
        Test that DataFormat rejects negative dimensions in image shape.
        Should raise ValueError for negative integers in the tuple.
        """
        # Test with negative width
        with pytest.raises(ValueError, match=self._image_shape_error):
            DataFormat(
                image_shape=(-100, 256),
                input_image_extension="jpg",
                output_image_extension="png"
            )

        # Test with negative height
        with pytest.raises(ValueError, match=self._image_shape_error):
            DataFormat(
                image_shape=(256, -100),
                input_image_extension="jpg",
                output_image_extension="png"
            )

        # Test with both negative
        with pytest.raises(ValueError, match=self._image_shape_error):
            DataFormat(
                image_shape=(-256, -256),
                input_image_extension="jpg",
                output_image_extension="png"
            )

    def test_data_format_invalid_image_shape_too_small(self):
        """
        Test that DataFormat rejects image dimensions smaller than
        MIN_IMG_SIZE.
        Should raise ValueError for dimensions < MIN_IMG_SIZE.
        """
        # Test with width too small
        with pytest.raises(ValueError, match=self._image_shape_error):
            DataFormat(
                image_shape=(MIN_IMG_SIZE-1, 256),
                input_image_extension="jpg",
                output_image_extension="png"
            )

        # Test with height too small
        with pytest.raises(ValueError, match=self._image_shape_error):
            DataFormat(
                image_shape=(256, MIN_IMG_SIZE-1),
                input_image_extension="jpg",
                output_image_extension="png"
            )

        # Test with both too small
        with pytest.raises(ValueError, match=self._image_shape_error):
            DataFormat(
                image_shape=(10, MIN_IMG_SIZE-1),
                input_image_extension="jpg",
                output_image_extension="png"
            )

    def test_data_format_invalid_image_shape_non_integer(self):
        """
        Test that DataFormat rejects non-integer values in image shape.
        Should raise ValueError for float or string values in the tuple.
        """
        # Test with float values
        with pytest.raises(ValidationError):
            DataFormat(
                image_shape=(256.5, 256),
                input_image_extension="jpg",
                output_image_extension="png"
            )

        # Test with string values
        with pytest.raises(ValidationError):
            DataFormat(
                image_shape=("256", 256),
                input_image_extension="jpg",
                output_image_extension="png"
            )

    def test_data_format_valid_extensions(self):
        """
        Test that DataFormat accepts all valid image extensions.
        Should accept jpg, jpeg, webp, png, bmp, gif extensions.
        """
        for ext in VALID_EXTENSIONS:
            data_format = DataFormat(
                input_image_extension=ext,
                output_image_extension=ext
            )
            assert data_format.input_image_extension == ext.lower()
            assert data_format.output_image_extension == ext.lower()

    def test_data_format_invalid_input_extension(self):
        """
        Test that DataFormat rejects invalid input image extensions.
        Should raise ValueError for unsupported extensions like 'tiff', 'svg'.
        """
        for ext in INVALID_EXTENSIONS:
            with pytest.raises(ValueError, match=f"Invalid image extension: {ext}"):
                DataFormat(
                    input_image_extension=ext,
                    output_image_extension="jpg"
                )

    def test_data_format_invalid_output_extension(self):
        """
        Test that DataFormat rejects invalid output image extensions.
        Should raise ValueError for unsupported extensions.
        """
        for ext in INVALID_EXTENSIONS:
            with pytest.raises(ValueError, match=f"Invalid image extension: {ext}"):
                DataFormat(
                    input_image_extension="jpg",
                    output_image_extension=ext
                )

    def test_data_format_extension_case_insensitive(self):
        """
        Test that DataFormat handles extensions in a case-insensitive manner.
        Should accept 'JPG', 'PNG', etc. and convert them to lowercase.
        """
        # Test uppercase extensions
        data_format = DataFormat(
            input_image_extension="JPG",
            output_image_extension="PNG"
        )
        assert data_format.input_image_extension == "jpg"
        assert data_format.output_image_extension == "png"

        # Test mixed case extensions
        data_format2 = DataFormat(
            input_image_extension="JpEg",
            output_image_extension="WebP"
        )
        assert data_format2.input_image_extension == "jpeg"
        assert data_format2.output_image_extension == "webp"

    def test_data_format_edge_case_minimum_dimensions(self):
        """
        Test DataFormat with minimum allowed dimensions.
        Should successfully create instance with the boundary values.
        """
        # Test exactly at the minimum boundary
        data_format = DataFormat(
            image_shape=(MIN_IMG_SIZE, MIN_IMG_SIZE),
            input_image_extension="jpg",
            output_image_extension="png"
        )
        assert data_format.image_shape == (MIN_IMG_SIZE, MIN_IMG_SIZE)

        # Test slightly above minimum
        data_format2 = DataFormat(
            image_shape=(MIN_IMG_SIZE+1, MIN_IMG_SIZE),
            input_image_extension="jpg",
            output_image_extension="png"
        )
        assert data_format2.image_shape == (MIN_IMG_SIZE+1, MIN_IMG_SIZE)


class TestDataFormatter:
    """Test cases for the DataFormatter class."""

    def test_data_formatter_initialization(self, sample_data_format):
        """
        Test that DataFormatter initializes correctly with a DataFormat instance.
        Should store the provided DataFormat and be ready for formatting operations.
        """
        formatter = DataFormatter(sample_data_format)
        assert formatter._data_format == sample_data_format
        assert formatter._data_format.image_shape == DEFAULT_IMAGE_SHAPE
        assert formatter._data_format.input_image_extension == "jpg"
        assert formatter._data_format.output_image_extension == "png"

    @patch('data_formatting.data_formatter.ImgReshaper')
    def test_format_data_with_images(self, mock_reshaper_class,
                                     sample_data_format, sample_question_bank,
                                     temp_directories):
        """
        Test the format_data method with a QuestionBank containing images.
        Should resize images and update their paths in the question bank.
        """
        _, output_dir = temp_directories
        mock_reshaper = _create_mock_reshaper(temp_directories)
        mock_reshaper_class.return_value = mock_reshaper

        formatter = DataFormatter(sample_data_format)
        result = formatter.format_data(sample_question_bank, output_dir)

        # Verify ImgReshaper was created with correct target size
        mock_reshaper_class.assert_called_once_with(
            target_size=DEFAULT_IMAGE_SHAPE)

        # Verify reshape was called for questions with images
        mock_reshaper.reshape.assert_called_once()

        # Verify question bank img_dir was updated
        assert result.get_img_dir() == output_dir

    @patch('data_formatting.data_formatter.ImgReshaper')
    def test_format_data_without_images(self, mock_reshaper_class, sample_data_format, temp_directories):
        """
        Test the format_data method with a QuestionBank containing no images.
        Should return the question bank unchanged when no questions have images.
        """
        input_dir, output_dir = temp_directories

        # Create question bank with no image questions
        qb = QuestionBank(img_dir=input_dir)
        qb.add_chapter(1, "Test Chapter")
        question_no_img = Question(
            qid="no_img_q",
            question="Question without image?",
            answers={"A", "B"},
            correct_answer="A"
        )
        qb.add_question(question_no_img, 1)

        mock_reshaper = _create_mock_reshaper(temp_directories)
        mock_reshaper_class.return_value = mock_reshaper

        formatter = DataFormatter(sample_data_format)
        result = formatter.format_data(qb, output_dir)

        # Verify reshape was never called
        mock_reshaper.reshape.assert_not_called()

        # Verify question bank img_dir was still updated
        assert result.get_img_dir() == output_dir

    @patch('data_formatting.data_formatter.ImgReshaper')
    def test_format_data_mixed_image_questions(self, mock_reshaper_class, sample_data_format, sample_question_bank, temp_directories):
        """
        Test format_data with a QuestionBank containing both image and non-image questions.
        Should only process questions that have images and leave others unchanged.
        """
        _, output_dir = temp_directories
        mock_reshaper = _create_mock_reshaper(temp_directories)
        mock_reshaper_class.return_value = mock_reshaper

        formatter = DataFormatter(sample_data_format)
        result = formatter.format_data(sample_question_bank, output_dir)

        # Should call reshape only once (for the question with image)
        assert mock_reshaper.reshape.call_count == 1

        # Verify the correct question was processed
        call_args = mock_reshaper.reshape.call_args[1]  # Get keyword arguments
        assert call_args['img_name'] == "test_q1"  # The question with image

    @patch('data_formatting.data_formatter.ImgReshaper')
    def test_format_data_updates_image_directory(self, mock_reshaper_class, sample_data_format, sample_question_bank, temp_directories):
        """
        Test that format_data correctly updates the QuestionBank's image directory.
        Should call set_img_dir with the new directory path after processing.
        """
        _, output_dir = temp_directories
        mock_reshaper = _create_mock_reshaper(temp_directories)
        mock_reshaper_class.return_value = mock_reshaper

        formatter = DataFormatter(sample_data_format)
        result = formatter.format_data(sample_question_bank, output_dir)

        assert result.get_img_dir() == output_dir

    @patch('data_formatting.data_formatter.ImgReshaper')
    def test_resize_images_calls_reshaper_correctly(self, mock_reshaper_class, sample_data_format, sample_question_bank, temp_directories):
        """
        Test that _resize_images calls the ImgReshaper with correct parameters.
        Should pass the right image name, directories, and extensions to reshape method.
        """
        input_dir, output_dir = temp_directories
        mock_reshaper = _create_mock_reshaper(temp_directories)
        mock_reshaper_class.return_value = mock_reshaper

        formatter = DataFormatter(sample_data_format)
        formatter.format_data(sample_question_bank, output_dir)

        # Verify reshape was called with correct parameters
        mock_reshaper.reshape.assert_called_once_with(
            img_name="test_q1",
            input_directory=input_dir,
            output_directory=output_dir,
            input_extension="jpg",
            output_extension="png"
        )

    @patch('data_formatting.data_formatter.ImgReshaper')
    def test_resize_images_updates_question_paths(self, mock_reshaper_class,
                                                  sample_data_format,
                                                  sample_question_bank,
                                                  temp_directories):
        """
        Test that _resize_images updates question image paths after reshaping.
        Should call set_img_path on questions with the new path returned by
        reshaper.
        """
        _, output_dir = temp_directories
        new_path = os.path.join(output_dir, "test_q1.png")

        mock_reshaper = _create_mock_reshaper(temp_directories)
        mock_reshaper.reshape.return_value = new_path
        mock_reshaper_class.return_value = mock_reshaper

        formatter = DataFormatter(sample_data_format)
        formatter.format_data(sample_question_bank, output_dir)

        # Get the question and verify its image path was updated
        question = sample_question_bank.get_question("test_q1")
        assert question.img_path == new_path

    @patch('data_formatting.data_formatter.ImgReshaper')
    def test_resize_images_handles_reshaper_errors(self, mock_reshaper_class, sample_data_format, sample_question_bank, temp_directories):
        """
        Test that _resize_images handles errors from the ImgReshaper gracefully.
        Should propagate or handle exceptions from the reshape method appropriately.
        """
        _, output_dir = temp_directories
        mock_reshaper = Mock()
        mock_reshaper.reshape.side_effect = Exception("Reshape error")
        mock_reshaper_class.return_value = mock_reshaper

        formatter = DataFormatter(sample_data_format)

        # The error should propagate
        with pytest.raises(Exception, match="Reshape error"):
            formatter.format_data(sample_question_bank, output_dir)

    @patch('data_formatting.data_formatter.ImgReshaper')
    def test_format_data_preserves_question_bank_structure(self, mock_reshaper_class, sample_data_format, sample_question_bank, temp_directories):
        """
        Test that format_data preserves the overall structure of the QuestionBank.
        Should maintain all questions, chapters, and relationships except image paths.
        """
        _, output_dir = temp_directories
        mock_reshaper = _create_mock_reshaper(temp_directories)
        mock_reshaper_class.return_value = mock_reshaper

        # Store original structure
        original_qids = sample_question_bank.get_qid_list()
        original_chapters = sample_question_bank.list_chapters()

        formatter = DataFormatter(sample_data_format)
        result = formatter.format_data(sample_question_bank, output_dir)

        # Verify structure is preserved
        assert result.get_qid_list() == original_qids
        assert result.list_chapters() == original_chapters

        # Verify questions are still accessible
        for qid in original_qids:
            question = result.get_question(qid)
            assert question.qid == qid

    @patch('data_formatting.data_formatter.ImgReshaper')
    def test_format_data_with_empty_question_bank(self, mock_reshaper_class, sample_data_format, temp_directories):
        """
        Test format_data with an empty QuestionBank.
        Should handle empty question banks without errors.
        """
        input_dir, output_dir = temp_directories

        # Create empty question bank
        empty_qb = QuestionBank(img_dir=input_dir)

        mock_reshaper = _create_mock_reshaper(temp_directories)
        mock_reshaper_class.return_value = mock_reshaper

        formatter = DataFormatter(sample_data_format)
        result = formatter.format_data(empty_qb, output_dir)

        # Should not call reshape for empty question bank
        mock_reshaper.reshape.assert_not_called()

        # Should still update image directory
        assert result.get_img_dir() == output_dir


class TestDataFormatterIntegration:
    """Integration tests for DataFormatter with real file operations."""
    # TODO: Implement these tests to verify end-to-end functionality

    def test_end_to_end_image_processing(self):
        """
        Test complete image processing workflow from input to output.
        Should create actual image files, process them, and verify results.
        """
        pass

    def test_different_input_output_extensions(self):
        """
        Test processing with different input and output image extensions.
        Should correctly convert between different image formats.
        """
        pass

    def test_image_quality_preservation(self):
        """
        Test that image processing preserves reasonable quality.
        """
        pass


class TestDataFormatterErrorHandling:
    """Test error handling scenarios for DataFormatter."""

    def test_invalid_data_format_initialization(self):
        """
        Test DataFormatter initialization with invalid DataFormat.
        Should raise appropriate errors for malformed DataFormat instances.
        """
        # Test with None
        with pytest.raises(TypeError):
            DataFormatter(None)

        # Test with wrong type
        with pytest.raises(TypeError):
            DataFormatter("not_a_data_format")

    @patch('data_formatting.data_formatter.ImgReshaper')
    def test_format_data_with_invalid_question_bank(self, mock_reshaper_class,
                                                    sample_data_format,
                                                    temp_directories):
        """
        Test format_data with invalid QuestionBank instances.
        Should handle None, malformed, or corrupted QuestionBank objects.
        """
        mock_reshaper = _create_mock_reshaper(temp_directories)
        mock_reshaper_class.return_value = mock_reshaper

        formatter = DataFormatter(sample_data_format)

        # Test with None
        with pytest.raises(AttributeError):
            formatter.format_data(None,
                                  "/some/dir")

        # Test with wrong type
        with pytest.raises(AttributeError):
            formatter.format_data("not_a_question_bank",
                                  "/some/dir")

    @patch('data_formatting.data_formatter.ImgReshaper')
    def test_format_data_with_invalid_output_directory(self,
                                                       mock_reshaper_class,
                                                       sample_data_format,
                                                       sample_question_bank):
        """
        Test format_data with invalid or inaccessible output directories.
        Should handle permission errors and invalid paths appropriately.
        """
        mock_reshaper = Mock()
        mock_reshaper.reshape.side_effect = IOError("Permission denied")
        mock_reshaper_class.return_value = mock_reshaper

        formatter = DataFormatter(sample_data_format)

        # The error should propagate from ImgReshaper
        with pytest.raises(IOError, match="Permission denied"):
            formatter.format_data(sample_question_bank, "/invalid/path")

    @patch('data_formatting.data_formatter.ImgReshaper')
    def test_corrupted_image_files(self, mock_reshaper_class, sample_data_format, temp_directories):
        """
        Test behavior with corrupted or invalid image files.
        Should handle PIL Image loading errors appropriately.
        """
        input_dir, output_dir = temp_directories

        # Create a "corrupted" image file (just text)
        corrupted_path = os.path.join(input_dir, "corrupted.jpg")
        with open(corrupted_path, 'w') as f:
            f.write("This is not an image")

        # Create question bank with corrupted image
        qb = QuestionBank(img_dir=input_dir)
        qb.add_chapter(1, "Test Chapter")
        question = Question(
            qid="corrupted",
            question="Question with corrupted image?",
            answers={"A", "B"},
            correct_answer="A",
            img_path=corrupted_path
        )
        qb.add_question(question, 1)

        mock_reshaper = Mock()
        mock_reshaper.reshape.side_effect = Exception("Image corruption error")
        mock_reshaper_class.return_value = mock_reshaper

        formatter = DataFormatter(sample_data_format)

        # The error should propagate from ImgReshaper
        with pytest.raises(Exception, match="Image corruption error"):
            formatter.format_data(qb, output_dir)
