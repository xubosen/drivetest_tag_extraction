import pytest
import tempfile
import os
import json
import shutil

from src.data_access.local_json_db import LocalJsonDB
from src.entities.question_bank import QuestionBank
from src.entities.question import Question

EMPTY_JSON_PATH = "data_access_test/empty_json.json"

DB_IMAGES = "test_db/raw_db/images"


# =============================================================================
# FIXTURE SETUP
# =============================================================================

@pytest.fixture
def temp_dirs():
    """
    Create temporary directories for testing database files and images.

    Returns:
        tuple: (temp_db_dir, temp_img_dir, db_file_path)
    """
    temp_db_dir = tempfile.mkdtemp()
    temp_img_dir = tempfile.mkdtemp()
    db_file_path = os.path.join(temp_db_dir, "test_db.json")

    yield temp_db_dir, temp_img_dir, db_file_path

    # Cleanup temporary directories after test
    shutil.rmtree(temp_db_dir, ignore_errors=True)
    shutil.rmtree(temp_img_dir, ignore_errors=True)


@pytest.fixture
def sample_question_bank(temp_dirs):
    """
    Create a sample QuestionBank with test data for testing.

    Returns:
        QuestionBank: A populated QuestionBank instance with multiple chapters and questions
    """
    _, temp_img_dir, _ = temp_dirs
    qb = QuestionBank(img_dir=temp_img_dir)
    qb.add_chapter(1, "Description of Chapter 1")
    qb.add_chapter(2, "Description of Chapter 2")

    # Create temporary image files for testing
    img1_path = os.path.join(temp_img_dir, "1.jpg")
    img2_path = os.path.join(temp_img_dir, "2.jpg")
    open(img1_path, 'a').close()
    open(img2_path, 'a').close()

    q1 = Question(
        qid="q1",
        question="What is 2 + 2?",
        answers={"2", "3", "4", "5"},
        correct_answer="4",
        img_path=img1_path
    )
    q2 = Question(
        qid="q2",
        question="What is the capital of France?",
        answers={"London", "Paris", "Berlin", "Madrid"},
        correct_answer="Paris",
        img_path=img2_path
    )
    q3 = Question(
        qid="q3",
        question="Explain photosynthesis.",
        answers={"Process by which plants make food", "Animal breathing",
                 "Water cycle", "Soil formation"},
        correct_answer="Process by which plants make food"
    )

    qb.add_question(q1, 1)
    qb.add_question(q2, 1)
    qb.add_question(q3, 2)

    return qb


@pytest.fixture
def sample_question(temp_dirs):
    """
    Create a sample Question instance for testing.

    Returns:
        Question: A Question instance with all fields populated
    """
    _, temp_img_dir, _ = temp_dirs
    img_path = os.path.join(temp_img_dir, "sample.jpg")
    open(img_path, 'a').close()

    return Question(
        qid="sample_q",
        question="Sample question?",
        answers={"Answer A", "Answer B", "Sample answer", "Answer D"},
        correct_answer="Sample answer",
        img_path=img_path
    )


@pytest.fixture
def local_json_db(temp_dirs):
    """
    Create a LocalJsonDB instance with temporary directories.

    Args:
        temp_dirs: Fixture providing temporary directory paths

    Returns:
        LocalJsonDB: An instance configured with test directories
    """
    temp_db_dir, temp_img_dir, db_file_path = temp_dirs
    return LocalJsonDB(db_file_path, temp_img_dir)


# =============================================================================
# CONSTRUCTOR TESTS
# =============================================================================

class TestLocalJsonDBConstructor:
    """Test class for LocalJsonDB constructor functionality."""

    def test_init_valid_paths(self):
        """
        Test LocalJsonDB constructor with valid file and directory paths.

        Should successfully create an instance with the provided paths.
        """
        db = LocalJsonDB("valid_path.json", "valid_dir/")
        assert db is not None
        assert isinstance(db, LocalJsonDB)

    def test_init_stores_paths_correctly(self):
        """
        Test that constructor correctly stores the provided file and image directory paths.

        Should verify that internal path attributes match the provided arguments.
        """
        db_file_path = "test_db.json"
        img_dir = "test_images/"
        db = LocalJsonDB(db_file_path, img_dir)

        assert db._db_file_path == db_file_path
        assert db._img_dir == img_dir


# =============================================================================
# SAVE METHOD TESTS
# =============================================================================

class TestLocalJsonDBSave:
    """Test class for LocalJsonDB save method functionality."""

    def test_save_empty_question_bank(self, local_json_db):
        """
        Test saving an empty QuestionBank to JSON file.

        Should create a valid JSON file with empty collections but proper structure.
        """
        empty_qb = QuestionBank(img_dir=local_json_db._img_dir)
        result = local_json_db.save(empty_qb)

        assert result is True
        assert os.path.exists(local_json_db._db_file_path)

        with open(local_json_db._db_file_path, 'r') as f:
            data = json.load(f)

        assert data["chapters"] == {}
        assert data["chap_to_qids"] == {}
        assert data["questions"] == {}
        assert data["img_dir"] == local_json_db._img_dir

    def test_save_question_bank_with_single_chapter(self, local_json_db, sample_question_bank):
        """
        Test saving a QuestionBank containing a single chapter with questions.

        Should create a JSON file with proper chapter and question data structure.
        """
        # Create a QB with only chapter 1
        qb = QuestionBank(img_dir=sample_question_bank.get_img_dir())
        qb.add_chapter(1, "Test Chapter")

        q1 = Question(
            qid="test_q1",
            question="Test question?",
            answers={"A", "B", "C", "D"},
            correct_answer="A"
        )
        qb.add_question(q1, 1)

        result = local_json_db.save(qb)

        assert result is True
        assert os.path.exists(local_json_db._db_file_path)

        with open(local_json_db._db_file_path, 'r') as f:
            data = json.load(f)

        assert len(data["chapters"]) == 1
        assert "1" in data["chapters"]
        assert data["chapters"]["1"] == "Test Chapter"
        assert len(data["questions"]) == 1
        assert "test_q1" in data["questions"]

    def test_save_question_bank_with_multiple_chapters(self, local_json_db, sample_question_bank):
        """
        Test saving a QuestionBank with multiple chapters and questions.

        Should properly serialize all chapters and their associated questions.
        """
        result = local_json_db.save(sample_question_bank)

        assert result is True
        assert os.path.exists(local_json_db._db_file_path)

        with open(local_json_db._db_file_path, 'r') as f:
            data = json.load(f)

        assert len(data["chapters"]) == 2
        assert "1" in data["chapters"]
        assert "2" in data["chapters"]
        assert len(data["questions"]) == 3

    def test_save_question_bank_with_images(self, local_json_db, sample_question_bank):
        """
        Test saving a QuestionBank where questions have associated images.

        Should copy image files to the target directory and update paths in JSON.
        """
        result = local_json_db.save(sample_question_bank)

        assert result is True

        # Check that images were copied
        for qid in sample_question_bank.get_qid_list():
            question = sample_question_bank.get_question(qid)
            if question.has_img():
                expected_path = f"{local_json_db._img_dir}/{qid}.jpg"
                assert os.path.exists(expected_path)

    def test_save_creates_json_file(self, local_json_db):
        """
        Test that save method creates a JSON file at the specified path.

        Should verify file existence and basic JSON structure after save.
        """
        empty_qb = QuestionBank(img_dir=local_json_db._img_dir)

        assert not os.path.exists(local_json_db._db_file_path)

        result = local_json_db.save(empty_qb)

        assert result is True
        assert os.path.exists(local_json_db._db_file_path)

        # Verify it's valid JSON
        with open(local_json_db._db_file_path, 'r') as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_save_overwrites_existing_file(self, local_json_db, sample_question_bank):
        """
        Test saving over an existing JSON file.

        Should replace the existing file with new data completely.
        """
        # Create initial file
        initial_data = {"test": "data"}
        with open(local_json_db._db_file_path, 'w') as f:
            json.dump(initial_data, f)

        result = local_json_db.save(sample_question_bank)

        assert result is True

        # Verify file was overwritten
        with open(local_json_db._db_file_path, 'r') as f:
            data = json.load(f)

        assert "test" not in data
        assert "chapters" in data

    def test_save_returns_true_on_success(self, local_json_db):
        """
        Test that save method returns True when operation succeeds.

        Should return True for successful save operations.
        """
        empty_qb = QuestionBank(img_dir=local_json_db._img_dir)
        result = local_json_db.save(empty_qb)
        assert result is True

    def test_save_raises_connection_error_on_file_write_failure(self, local_json_db, monkeypatch):
        """
        Test save method behavior when file writing fails.

        Should raise ConnectionError when unable to write to the specified file path.
        """
        empty_qb = QuestionBank(img_dir=local_json_db._img_dir)

        # Mock open to raise an exception
        def mock_open(*args, **kwargs):
            raise PermissionError("Permission denied")

        monkeypatch.setattr("builtins.open", mock_open)

        with pytest.raises(ConnectionError, match="Error saving question bank"):
            local_json_db.save(empty_qb)

    def test_save_raises_connection_error_on_image_copy_failure(self, local_json_db, sample_question_bank, monkeypatch):
        """
        Test save method behavior when image copying fails.

        Should raise ConnectionError when unable to copy image files.
        """
        # Mock shutil.copy2 to raise an exception
        def mock_copy2(*args, **kwargs):
            raise PermissionError("Permission denied")

        monkeypatch.setattr("shutil.copy2", mock_copy2)

        with pytest.raises(ConnectionError, match="Error saving question bank"):
            local_json_db.save(sample_question_bank)

    def test_save_creates_image_directory_if_not_exists(self, local_json_db, sample_question_bank):
        """
        Test that save method creates the image directory if it doesn't exist.

        Should automatically create the image directory before copying images.
        """
        # Remove the image directory
        if os.path.exists(local_json_db._img_dir):
            shutil.rmtree(local_json_db._img_dir)

        assert not os.path.exists(local_json_db._img_dir)

        result = local_json_db.save(sample_question_bank)

        assert result is True
        assert os.path.exists(local_json_db._img_dir)


# =============================================================================
# LOAD METHOD TESTS
# =============================================================================

class TestLocalJsonDBLoad:
    """Test class for LocalJsonDB load method functionality."""

    def test_load_empty_database(self):
        """
        Test loading from a JSON file containing an empty QuestionBank.

        Should return a valid but empty QuestionBank instance.
        """
        test_db = LocalJsonDB(EMPTY_JSON_PATH, DB_IMAGES)
        qb = test_db.load()

        assert len(qb.list_chapters()) == 0
        assert qb.question_count() == 0

    def test_load_single_chapter_database(self):
        """
        Test loading a database with one chapter and its questions.

        Should correctly reconstruct the QuestionBank with all chapter data.
        """
        test_db = LocalJsonDB(EMPTY_JSON_PATH, DB_IMAGES)
        test_qb = QuestionBank(img_dir=DB_IMAGES)
        test_qb.add_chapter(1, "description of chapter 1")
        test_db.save(test_qb)
        loaded_qb = test_db.load()

        assert len(loaded_qb.list_chapters()) == 1

        # Clean up by setting EMPTY_JSON_PATH to an empty file
        with open(EMPTY_JSON_PATH, 'w') as f:
            json.dump({}, f)

    def test_load_multiple_chapters_database(self, local_json_db, sample_question_bank):
        """
        Test loading a database with multiple chapters and questions.

        Should properly reconstruct all chapters and their question associations.
        """
        # Save and load sample data
        local_json_db.save(sample_question_bank)
        loaded_qb = local_json_db.load()

        assert len(loaded_qb.list_chapters()) == 2
        assert loaded_qb.question_count() == 3

        # Verify chapters exist
        assert 1 in loaded_qb.list_chapters()
        assert 2 in loaded_qb.list_chapters()

    def test_load_database_with_images(self, local_json_db, sample_question_bank):
        """
        Test loading a database where questions have associated images.

        Should correctly set image paths for questions with existing image files.
        """
        # Save with images
        local_json_db.save(sample_question_bank)

        loaded_qb = local_json_db.load()

        # Check that questions with images have correct paths
        for qid in loaded_qb.get_qid_list():
            question = loaded_qb.get_question(qid)
            if question.has_img():
                assert question.get_img_path() is not None
                assert os.path.exists(question.get_img_path())

    def test_load_database_with_missing_images(self, local_json_db, temp_dirs):
        """
        Test loading a database where some referenced images don't exist.

        Should set image paths to None for questions with missing image files.
        """
        # Create data with image references
        data = {
            "chapters": {"1": "Test Chapter"},
            "chap_to_qids": {"1": ["q1"]},
            "questions": {
                "q1": {
                    "qid": "q1",
                    "question": "Test?",
                    "answers": ["A", "B"],
                    "correct_answer": "A",
                    "img_path": "/non/existent/image.jpg",
                    "chapter": 1,
                    "tags": [],
                    "keywords": []
                }
            },
            "img_dir": local_json_db._img_dir
        }

        with open(local_json_db._db_file_path, 'w') as f:
            json.dump(data, f)

        loaded_qb = local_json_db.load()
        question = loaded_qb.get_question("q1")

        assert question.get_img_path() is None

    def test_load_nonexistent_file(self, local_json_db):
        """
        Test loading from a file path that doesn't exist.

        Should raise FileNotFoundError with appropriate error message.
        """
        with pytest.raises(FileNotFoundError, match="Database file not found"):
            local_json_db.load()

    def test_load_invalid_json_file(self, local_json_db, monkeypatch):
        """
        Test loading from a file containing invalid JSON.

        Should raise ConnectionError when JSON parsing fails.
        """
        # Create invalid JSON file
        with open(local_json_db._db_file_path, 'w') as f:
            f.write("invalid json content {")

        with pytest.raises(ConnectionError, match="Error loading question bank"):
            local_json_db.load()

    def test_load_json_with_missing_required_fields(self, local_json_db, monkeypatch):
        """
        Test loading from JSON missing required fields (chapters, questions, etc.).

        Should handle missing fields gracefully or raise appropriate errors.
        """
        # Create JSON with missing fields
        incomplete_data = {"chapters": {}}

        with open(local_json_db._db_file_path, 'w') as f:
            json.dump(incomplete_data, f)

        with pytest.raises(ConnectionError, match="Error loading question bank"):
            local_json_db.load()

    def test_load_json_with_invalid_data_types(self, local_json_db, monkeypatch):
        """
        Test loading from JSON with incorrect data types for fields.

        Should raise ConnectionError when data types don't match expectations.
        """
        # Create JSON with wrong data types
        invalid_data = {
            "chapters": "not_a_dict",
            "chap_to_qids": {},
            "questions": {},
            "img_dir": local_json_db._img_dir
        }

        with open(local_json_db._db_file_path, 'w') as f:
            json.dump(invalid_data, f)

        with pytest.raises(ConnectionError, match="Error loading question bank"):
            local_json_db.load()

    def test_load_preserves_question_order(self, local_json_db, sample_question_bank):
        """
        Test that questions maintain consistent ordering after save/load cycle.

        Should verify that question order is preserved or follows expected sorting.
        """
        original_qids = sorted(sample_question_bank.get_qid_list())

        local_json_db.save(sample_question_bank)
        loaded_qb = local_json_db.load()

        loaded_qids = sorted(loaded_qb.get_qid_list())

        assert original_qids == loaded_qids


# =============================================================================
# SERIALIZATION HELPER METHOD TESTS
# =============================================================================

class TestLocalJsonDBSerialization:
    """Test class for LocalJsonDB serialization helper methods."""

    def test_serialize_question_bank_structure(self, local_json_db, sample_question_bank):
        """
        Test that _serialize_question_bank creates correct JSON structure.

        Should verify all required top-level keys and their data types.
        """
        data = local_json_db._serialize_question_bank(sample_question_bank)

        required_keys = ["chapters", "chap_to_qids", "questions", "img_dir"]
        for key in required_keys:
            assert key in data

        assert isinstance(data["chapters"], dict)
        assert isinstance(data["chap_to_qids"], dict)
        assert isinstance(data["questions"], dict)
        assert isinstance(data["img_dir"], str)

    def test_serialize_question_bank_chapter_data(self, local_json_db, sample_question_bank):
        """
        Test serialization of chapter information.

        Should correctly serialize chapter numbers, descriptions, and question mappings.
        """
        data = local_json_db._serialize_question_bank(sample_question_bank)

        # Check chapters are serialized correctly
        for chap_num in sample_question_bank.list_chapters():
            assert chap_num in data["chapters"].keys()
            assert (data["chapters"][chap_num] ==
                    sample_question_bank.describe_chapter(chap_num))
            assert chap_num in data["chap_to_qids"].keys()
            assert isinstance(data["chap_to_qids"][chap_num], list)

    def test_serialize_question_bank_question_data(self, local_json_db, sample_question_bank):
        """
        Test serialization of individual question data.

        Should include all question fields with proper data types and structure.
        """
        data = local_json_db._serialize_question_bank(sample_question_bank)

        for qid in sample_question_bank.get_qid_list():
            assert qid in data["questions"]
            q_data = data["questions"][qid]

            required_fields = ["qid", "question", "answers", "correct_answer", "img_path", "chapter", "tags", "keywords"]
            for field in required_fields:
                assert field in q_data

    def test_make_img_path_with_valid_image(self, local_json_db, sample_question):
        """
        Test _make_img_path method with a question that has an image.

        Should generate correct image path based on question ID and file extension.
        """
        result = local_json_db._make_img_path(sample_question)

        expected_path = f"{local_json_db._img_dir}/{sample_question.get_qid()}.jpg"
        assert result == expected_path

    def test_make_img_path_with_no_image(self, local_json_db, temp_dirs):
        """
        Test _make_img_path method with a question that has no image.

        Should return empty string when question has no associated image.
        """
        question_no_img = Question(
            qid="no_img_q",
            question="No image question?",
            answers={"A", "B"},
            correct_answer="A"
        )

        result = local_json_db._make_img_path(question_no_img)
        assert result == ""


# =============================================================================
# DESERIALIZATION HELPER METHOD TESTS
# =============================================================================

class TestLocalJsonDBDeserialization:
    """Test class for LocalJsonDB deserialization helper methods."""

    def test_deserialize_question_bank_empty_data(self, local_json_db):
        """
        Test _deserialize_question_bank with empty/minimal data.

        Should create valid QuestionBank even with empty data structure.
        """
        empty_data = {
            "chapters": {},
            "chap_to_qids": {},
            "questions": {},
            "img_dir": local_json_db._img_dir
        }

        qb = local_json_db._deserialize_question_bank(empty_data)

        assert qb.question_count() == 0
        assert len(qb.list_chapters()) == 0

    def test_deserialize_question_bank_full_data(self, local_json_db, sample_question_bank):
        """
        Test deserialization of complete QuestionBank data.

        Should correctly reconstruct all chapters, questions, and relationships.
        """
        # Serialize then deserialize
        data = local_json_db._serialize_question_bank(sample_question_bank)
        reconstructed_qb = local_json_db._deserialize_question_bank(data)

        assert reconstructed_qb.question_count() == sample_question_bank.question_count()
        assert reconstructed_qb.list_chapters() == sample_question_bank.list_chapters()

    def test_get_chapter_num_valid_question(self, local_json_db):
        """
        Test _get_chapter_num method with a question that belongs to a chapter.

        Should return correct chapter number for valid question ID.
        """
        data = {
            "chap_to_qids": {"1": ["q1", "q2"], "2": ["q3"]}
        }

        chapter_num = local_json_db._get_chapter_num(data, "q1")
        assert chapter_num == 1

        chapter_num = local_json_db._get_chapter_num(data, "q3")
        assert chapter_num == 2

    def test_get_chapter_num_invalid_question(self, local_json_db):
        """
        Test _get_chapter_num method with question ID not in any chapter.

        Should raise ValueError when question doesn't belong to any chapter.
        """
        data = {
            "chap_to_qids": {"1": ["q1", "q2"]}
        }

        with pytest.raises(ValueError, match="Question ID q99 does not belong to any chapter"):
            local_json_db._get_chapter_num(data, "q99")

    def test_get_img_path_existing_image(self, local_json_db, temp_dirs):
        """
        Test _get_img_path method when image file exists.

        Should return the image path when file exists on disk.
        """
        _, temp_img_dir, _ = temp_dirs
        img_path = os.path.join(temp_img_dir, "test.jpg")

        # Create the image file
        open(img_path, 'a').close()

        q_data = {"img_path": img_path}
        result = local_json_db._get_img_path(q_data)

        assert result == img_path

    def test_get_img_path_missing_image(self, local_json_db):
        """
        Test _get_img_path method when image file doesn't exist.

        Should return None when referenced image file is missing.
        """
        q_data = {"img_path": "/non/existent/path.jpg"}
        result = local_json_db._get_img_path(q_data)

        assert result is None


# =============================================================================
# IMAGE HANDLING TESTS
# =============================================================================

class TestLocalJsonDBImageHandling:
    """Test class for LocalJsonDB image handling functionality."""

    def test_copy_images_single_image(self, local_json_db, temp_dirs):
        """
        Test _copy_images method with a single image file.

        Should successfully copy one image to the target directory.
        """
        _, temp_img_dir, _ = temp_dirs
        qb = QuestionBank(img_dir=temp_img_dir)
        qb.add_chapter(1, "Test")

        # Create source image
        src_img = os.path.join(temp_img_dir, "source.jpg")
        open(src_img, 'a').close()

        question = Question(
            qid="test_q",
            question="Test?",
            answers={"A", "B"},
            correct_answer="A",
            img_path=src_img
        )
        qb.add_question(question, 1)

        # Ensure target directory exists
        os.makedirs(local_json_db._img_dir, exist_ok=True)

        local_json_db._copy_images(qb)

        expected_path = f"{local_json_db._img_dir}/test_q.jpg"
        assert os.path.exists(expected_path)

    def test_copy_images_multiple_images(self, local_json_db, sample_question_bank):
        """
        Test _copy_images method with multiple image files.

        Should copy all images and preserve file extensions.
        """
        # Ensure target directory exists
        os.makedirs(local_json_db._img_dir, exist_ok=True)

        local_json_db._copy_images(sample_question_bank)

        # Check that images with valid paths were copied
        for qid in sample_question_bank.get_qid_list():
            question = sample_question_bank.get_question(qid)
            if question.has_img() and os.path.exists(question.get_img_path()):
                expected_path = f"{local_json_db._img_dir}/{qid}.jpg"
                assert os.path.exists(expected_path)

    def test_copy_images_destination_permission_error(self, local_json_db, sample_question_bank, monkeypatch):
        """
        Test image copying when destination directory has permission issues.

        Should raise appropriate error when unable to write to destination.
        """
        def mock_copy2(*args, **kwargs):
            raise PermissionError("Permission denied")

        monkeypatch.setattr("shutil.copy2", mock_copy2)

        with pytest.raises(PermissionError):
            local_json_db._copy_images(sample_question_bank)


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestLocalJsonDBIntegration:
    """Test class for LocalJsonDB integration and end-to-end functionality."""

    def test_save_load_roundtrip_empty(self, local_json_db):
        """
        Test complete save/load cycle with empty QuestionBank.

        Should maintain data integrity through save and load operations.
        """
        empty_qb = QuestionBank(img_dir=local_json_db._img_dir)

        # Save
        result = local_json_db.save(empty_qb)
        assert result is True

        # Load
        loaded_qb = local_json_db.load()

        # Verify
        assert loaded_qb.question_count() == 0
        assert len(loaded_qb.list_chapters()) == 0

    def test_save_load_roundtrip_full_data(self, local_json_db, sample_question_bank):
        """
        Test complete save/load cycle with fully populated QuestionBank.

        Should preserve all data exactly through save/load roundtrip.
        """
        original_count = sample_question_bank.question_count()
        original_chapters = sample_question_bank.list_chapters()

        # Save
        result = local_json_db.save(sample_question_bank)
        assert result is True

        # Load
        loaded_qb = local_json_db.load()

        # Verify
        assert loaded_qb.question_count() == original_count
        assert loaded_qb.list_chapters() == original_chapters

    def test_save_load_roundtrip_with_images(self, local_json_db, sample_question_bank):
        """
        Test save/load cycle including image file operations.

        Should properly handle image copying and path management.
        """
        # Save
        local_json_db.save(sample_question_bank)

        # Load
        loaded_qb = local_json_db.load()

        # Verify images
        for qid in loaded_qb.get_qid_list():
            original_q = sample_question_bank.get_question(qid)
            loaded_q = loaded_qb.get_question(qid)

            if original_q.has_img():
                assert loaded_q.has_img()
                assert os.path.exists(loaded_q.get_img_path())

    def test_multiple_save_operations(self, local_json_db, sample_question_bank):
        """
        Test multiple consecutive save operations to same file.

        Should handle multiple saves without data corruption or conflicts.
        """
        # Save multiple times
        for _ in range(3):
            result = local_json_db.save(sample_question_bank)
            assert result is True

        # Verify final state is correct
        loaded_qb = local_json_db.load()
        assert loaded_qb.question_count() == sample_question_bank.question_count()

    def test_multiple_load_operations(self, local_json_db, sample_question_bank):
        """
        Test multiple consecutive load operations from same file.

        Should return consistent results across multiple load calls.
        """
        # Save first
        local_json_db.save(sample_question_bank)

        # Load multiple times
        results = []
        for _ in range(3):
            loaded_qb = local_json_db.load()
            results.append(loaded_qb.question_count())

        # All results should be the same
        assert all(count == results[0] for count in results)
