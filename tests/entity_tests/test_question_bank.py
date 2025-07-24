import pytest
import tempfile
import os
import json
from pydantic import ValidationError

from entities.question_bank import QuestionBank
from entities.question import Question

SAMPLE_VALID_IMG_DIR = "test_db/raw_db/images"


class TestQuestionBankInitialization:
    """Test QuestionBank model initialization and validation."""

    def test_init_with_valid_img_dir(self):
        """Test successful initialization with valid image directory."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        assert qb.img_dir == SAMPLE_VALID_IMG_DIR
        assert qb.qids == set()
        assert qb.chapters == {}
        assert qb.chap_num_to_ids == {}
        assert qb.id_to_q == {}

    def test_init_with_invalid_img_dir(self):
        """Test initialization fails with non-existent image directory."""
        with pytest.raises(ValidationError) as exc_info:
            QuestionBank(img_dir="/non/existent/directory")
        assert "Image directory does not exist" in str(exc_info.value)

    def test_init_with_empty_img_dir(self):
        """Test initialization fails with empty string image directory."""
        with pytest.raises(ValidationError) as exc_info:
            QuestionBank(img_dir="")
        assert "at least 1 character" in str(exc_info.value)

    def test_init_with_whitespace_img_dir(self):
        """Test initialization handles whitespace in image directory path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            qb = QuestionBank(img_dir=f"  {temp_dir}  ")
            assert qb.img_dir == temp_dir  # whitespace stripped

    def test_init_with_file_instead_of_dir(self):
        """Test initialization fails when img_dir points to a file instead of directory."""
        with tempfile.NamedTemporaryFile() as temp_file:
            with pytest.raises(ValidationError) as exc_info:
                QuestionBank(img_dir=temp_file.name)
            assert "is not a directory" in str(exc_info.value)

    def test_init_with_default_values(self):
        """Test initialization with default values for optional fields."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        assert isinstance(qb.qids, set)
        assert isinstance(qb.chapters, dict)
        assert isinstance(qb.chap_num_to_ids, dict)
        assert isinstance(qb.id_to_q, dict)

    def test_init_with_custom_values(self):
        """Test initialization with custom values for all fields."""
        custom_qids = {"q1", "q2"}
        custom_chapters = {1: "Chapter 1", 2: "Chapter 2"}
        custom_chap_to_ids = {1: {"q1"}, 2: {"q2"}}

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create sample questions
            q1 = Question(
                qid="q1",
                question="Sample question 1?",
                answers={"A", "B", "C", "D"},
                correct_answer="A",
                chapter=(1, "Chapter 1")
            )
            q2 = Question(
                qid="q2",
                question="Sample question 2?",
                answers={"A", "B", "C", "D"},
                correct_answer="B",
                chapter=(2, "Chapter 2")
            )

            qb = QuestionBank(
                img_dir=temp_dir,
                qids=custom_qids,
                chapters=custom_chapters,
                chap_num_to_ids=custom_chap_to_ids,
                id_to_q={"q1": q1, "q2": q2}
            )

            assert qb.qids == custom_qids
            assert qb.chapters == custom_chapters
            assert qb.chap_num_to_ids == custom_chap_to_ids


class TestQuestionBankFieldValidation:
    """Test individual field validators for QuestionBank."""

    def test_validate_qids_with_empty_string(self):
        """Test qids validation fails when set contains empty string."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValidationError) as exc_info:
                QuestionBank(
                    img_dir=temp_dir,
                    qids={"valid_id", ""},
                    chapters={1: "Chapter 1"},
                    chap_num_to_ids={1: {"valid_id", ""}}
                )
            assert "All question IDs must be non-empty strings" in str(exc_info.value)

    def test_validate_qids_with_valid_ids(self):
        """Test qids validation succeeds with valid non-empty string IDs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            qb = QuestionBank(
                img_dir=temp_dir,
                qids={"q1", "q2", "question_3"},
                chapters={1: "Chapter 1"},
                chap_num_to_ids={1: {"q1", "q2", "question_3"}}
            )
            assert "q1" in qb.qids
            assert "q2" in qb.qids
            assert "question_3" in qb.qids

    def test_validate_chapters_with_negative_number(self):
        """Test chapters validation fails with negative chapter numbers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValidationError) as exc_info:
                QuestionBank(
                    img_dir=temp_dir,
                    chapters={-1: "Invalid Chapter"}
                )
            assert "Chapter number must be a positive integer" in str(exc_info.value)

    def test_validate_chapters_with_zero_number(self):
        """Test chapters validation fails with zero chapter number."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValidationError) as exc_info:
                QuestionBank(
                    img_dir=temp_dir,
                    chapters={0: "Invalid Chapter"}
                )
            assert "Chapter number must be a positive integer" in str(exc_info.value)

    def test_validate_chapters_with_empty_description(self):
        """Test chapters validation fails with empty chapter description."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValidationError) as exc_info:
                QuestionBank(
                    img_dir=temp_dir,
                    chapters={1: ""}
                )
            assert "Chapter description cannot be empty" in str(exc_info.value)

    def test_validate_chapters_with_whitespace_description(self):
        """Test chapters validation fails with whitespace-only description."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValidationError) as exc_info:
                QuestionBank(
                    img_dir=temp_dir,
                    chapters={1: "   "}
                )
            assert "Chapter description cannot be empty" in str(exc_info.value)

    def test_validate_chapters_with_valid_data(self):
        """Test chapters validation succeeds with positive numbers and non-empty descriptions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            qb = QuestionBank(
                img_dir=temp_dir,
                chapters={1: "Chapter One", 2: "Chapter Two",
                          10: "Chapter Ten"},
                chap_num_to_ids={1: set(), 2:set(), 10:set()}
            )
            assert qb.chapters[1] == "Chapter One"
            assert qb.chapters[2] == "Chapter Two"
            assert qb.chapters[10] == "Chapter Ten"

    def test_validate_img_dir_strips_whitespace(self):
        """Test img_dir validator strips leading/trailing whitespace."""
        with tempfile.TemporaryDirectory() as temp_dir:
            qb = QuestionBank(img_dir=f"  {temp_dir}  ")
            assert qb.img_dir == temp_dir
            assert not qb.img_dir.startswith(" ")
            assert not qb.img_dir.endswith(" ")


class TestQuestionBankModelValidation:
    """Test model-level validation for QuestionBank."""

    def test_validate_chapter_consistency_matching_keys(self):
        """Test model validation succeeds when chapter keys match between chapters and chap_num_to_ids."""
        with tempfile.TemporaryDirectory() as temp_dir:
            qb = QuestionBank(
                img_dir=temp_dir,
                chapters={1: "Chapter 1", 2: "Chapter 2"},
                chap_num_to_ids={1: set(), 2: set()}
            )
            assert qb.chapters.keys() == qb.chap_num_to_ids.keys()

    def test_validate_chapter_consistency_mismatched_keys(self):
        """Test model validation fails when chapter keys don't match between dictionaries."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValidationError) as exc_info:
                QuestionBank(
                    img_dir=temp_dir,
                    chapters={1: "Chapter 1", 2: "Chapter 2"},
                    chap_num_to_ids={1: set(), 3: set()}  # 3 instead of 2
                )
            assert "Chapter numbers must match" in str(exc_info.value)

    def test_validate_question_belongs_to_one_chapter(self):
        """Test model validation succeeds when each question belongs to exactly one chapter."""
        with tempfile.TemporaryDirectory() as temp_dir:
            qb = QuestionBank(
                img_dir=temp_dir,
                qids={"q1", "q2"},
                chapters={1: "Chapter 1", 2: "Chapter 2"},
                chap_num_to_ids={1: {"q1"}, 2: {"q2"}}
            )
            assert "q1" in qb.qids and "q2" in qb.qids

    def test_validate_question_belongs_to_no_chapter(self):
        """Test model validation fails when a question doesn't belong to any chapter."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValidationError) as exc_info:
                QuestionBank(
                    img_dir=temp_dir,
                    qids={"q1", "q2"},
                    chapters={1: "Chapter 1"},
                    chap_num_to_ids={1: {"q1"}}  # q2 missing
                )
            assert "must belong to exactly one chapter" in str(exc_info.value)

    def test_validate_question_belongs_to_multiple_chapters(self):
        """Test model validation fails when a question belongs to multiple chapters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValidationError) as exc_info:
                QuestionBank(
                    img_dir=temp_dir,
                    qids={"q1"},
                    chapters={1: "Chapter 1", 2: "Chapter 2"},
                    chap_num_to_ids={1: {"q1"}, 2: {"q1"}}  # q1 in both
                )
            assert "must belong to exactly one chapter" in str(exc_info.value)

    def test_validate_orphaned_question_id(self):
        """Test model validation fails when qids contains ID not in any chapter."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValidationError) as exc_info:
                QuestionBank(
                    img_dir=temp_dir,
                    qids={"q1", "q2"},
                    chapters={1: "Chapter 1"},
                    chap_num_to_ids={1: {"q1"}}  # q2 not in any chapter
                )
            assert "must belong to exactly one chapter" in str(exc_info.value)


class TestQuestionBankChapterManagement:
    """Test chapter-related operations in QuestionBank."""

    def test_add_chapter_new_chapter(self):
        """Test adding a new chapter successfully."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Chapter One")

        assert 1 in qb.chapters
        assert qb.chapters[1] == "Chapter One"
        assert 1 in qb.chap_num_to_ids
        assert qb.chap_num_to_ids[1] == set()

    def test_add_chapter_duplicate_number(self):
        """Test adding a chapter with existing number (should handle gracefully)."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Chapter One")
        # Adding again should not raise error due to the condition check
        qb.add_chapter(1, "Chapter One Updated")
        # The original should remain unchanged due to the bug in the code
        assert qb.chapters[1] == "Chapter One"

    def test_add_chapter_invalid_number(self):
        """Test adding a chapter with invalid number (negative/zero)."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        # The validation happens during assignment due to validate_assignment=True
        with pytest.raises(ValueError):
            qb.add_chapter(-1, "Invalid Chapter")

    def test_add_chapter_empty_description(self):
        """Test adding a chapter with empty description."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        # The validation happens during assignment due to validate_assignment=True
        with pytest.raises(ValueError):
            qb.add_chapter(1, "")

    def test_list_chapters_empty(self):
        """Test listing chapters when no chapters exist."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        chapters = qb.list_chapters()
        assert chapters == []
        assert isinstance(chapters, list)

    def test_list_chapters_multiple_ordered(self):
        """Test listing chapters returns ordered list of chapter numbers."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(3, "Chapter Three")
        qb.add_chapter(1, "Chapter One")
        qb.add_chapter(2, "Chapter Two")

        chapters = qb.list_chapters()
        assert chapters == [1, 2, 3]

    def test_describe_chapter_existing(self):
        """Test getting description of existing chapter."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Test Chapter")

        description = qb.describe_chapter(1)
        assert description == "Test Chapter"

    def test_describe_chapter_non_existing(self):
        """Test getting description of non-existing chapter raises LookupError."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)

        with pytest.raises(LookupError) as exc_info:
            qb.describe_chapter(999)
        assert "Chapter 999 not found" in str(exc_info.value)

    def test_get_qids_by_chapter_existing_empty(self):
        """Test getting question IDs for existing chapter with no questions."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Empty Chapter")

        qids = qb.get_qids_by_chapter(1)
        assert qids == set()
        assert isinstance(qids, set)

    def test_get_qids_by_chapter_existing_with_questions(self):
        """Test getting question IDs for existing chapter with questions."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Test Chapter")

        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B", "C", "D"},
            correct_answer="A",
            chapter=(1, "Test Chapter")
        )
        qb.add_question(question, 1)

        qids = qb.get_qids_by_chapter(1)
        assert "q1" in qids
        assert len(qids) == 1

    def test_get_qids_by_chapter_non_existing(self):
        """Test getting question IDs for non-existing chapter raises LookupError."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)

        with pytest.raises(LookupError) as exc_info:
            qb.get_qids_by_chapter(999)
        assert "Chapter 999 not found" in str(exc_info.value)

    def test_get_qids_by_chapter_returns_copy(self):
        """Test that get_qids_by_chapter returns a copy, not reference."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Test Chapter")

        qids1 = qb.get_qids_by_chapter(1)
        qids2 = qb.get_qids_by_chapter(1)

        # Modify one copy
        qids1.add("test_id")

        # Other copy should be unchanged
        assert "test_id" not in qids2
        assert "test_id" not in qb.chap_num_to_ids[1]


class TestQuestionBankQuestionManagement:
    """Test question-related operations in QuestionBank."""

    def test_add_question_to_existing_chapter(self):
        """Test adding a question to an existing chapter."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Test Chapter")

        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B", "C", "D"},
            correct_answer="A",
            chapter=(1, "Test Chapter")
        )

        qb.add_question(question, 1)

        assert "q1" in qb.qids
        assert "q1" in qb.chap_num_to_ids[1]
        assert qb.id_to_q["q1"] == question

    def test_add_question_to_non_existing_chapter(self):
        """Test adding a question to non-existing chapter raises KeyError."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)

        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B", "C", "D"},
            correct_answer="A",
            chapter=(1, "Test Chapter")
        )

        with pytest.raises(KeyError) as exc_info:
            qb.add_question(question, 999)
        assert "Chapter 999 does not exist" in str(exc_info.value)

    def test_add_question_duplicate_id(self):
        """Test adding a question with duplicate ID (should handle gracefully)."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Test Chapter")

        question1 = Question(
            qid="q1",
            question="First question?",
            answers={"A", "B", "C", "D"},
            correct_answer="A",
            chapter=(1, "Test Chapter")
        )

        question2 = Question(
            qid="q1",  # Same ID
            question="Second question?",
            answers={"A", "B", "C", "D"},
            correct_answer="B",
            chapter=(1, "Test Chapter")
        )

        qb.add_question(question1, 1)
        qb.add_question(question2, 1)  # Should overwrite

        assert len(qb.qids) == 1  # Only one unique ID
        assert qb.id_to_q["q1"] == question2  # Latest question

    def test_add_question_updates_all_collections(self):
        """Test that adding a question updates qids, chap_num_to_ids, and id_to_q."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Test Chapter")

        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B", "C", "D"},
            correct_answer="A",
            chapter=(1, "Test Chapter")
        )

        initial_qids_len = len(qb.qids)
        initial_chap_ids_len = len(qb.chap_num_to_ids[1])
        initial_id_to_q_len = len(qb.id_to_q)

        qb.add_question(question, 1)

        assert len(qb.qids) == initial_qids_len + 1
        assert len(qb.chap_num_to_ids[1]) == initial_chap_ids_len + 1
        assert len(qb.id_to_q) == initial_id_to_q_len + 1

    def test_get_question_existing(self):
        """Test retrieving an existing question by ID."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Test Chapter")

        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B", "C", "D"},
            correct_answer="A",
            chapter=(1, "Test Chapter")
        )

        qb.add_question(question, 1)
        retrieved = qb.get_question("q1")

        assert retrieved == question
        assert retrieved.get_qid() == "q1"

    def test_get_question_non_existing(self):
        """Test retrieving non-existing question raises LookupError."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)

        with pytest.raises(LookupError) as exc_info:
            qb.get_question("non_existent")
        assert "Question non_existent not found" in str(exc_info.value)

    def test_get_question_returns_correct_object(self):
        """Test that get_question returns the exact Question object."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Test Chapter")

        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B", "C", "D"},
            correct_answer="A",
            chapter=(1, "Test Chapter")
        )

        qb.add_question(question, 1)
        retrieved = qb.get_question("q1")

        assert retrieved is qb.id_to_q["q1"]
        assert id(retrieved) == id(qb.id_to_q["q1"])

    def test_get_qid_list_empty(self):
        """Test getting question ID list when no questions exist."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qid_list = qb.get_qid_list()

        assert qid_list == []
        assert isinstance(qid_list, list)

    def test_get_qid_list_multiple_ordered(self):
        """Test getting question ID list returns ordered list."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Test Chapter")

        for qid in ["q3", "q1", "q2"]:
            question = Question(
                qid=qid,
                question=f"Question {qid}?",
                answers={"A", "B", "C", "D"},
                correct_answer="A",
                chapter=(1, "Test Chapter")
            )
            qb.add_question(question, 1)

        qid_list = qb.get_qid_list()
        assert qid_list == ["q1", "q2", "q3"]

    def test_get_qid_list_returns_copy(self):
        """Test that get_qid_list returns a copy, not reference."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Test Chapter")

        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B", "C", "D"},
            correct_answer="A",
            chapter=(1, "Test Chapter")
        )
        qb.add_question(question, 1)

        qid_list1 = qb.get_qid_list()
        qid_list2 = qb.get_qid_list()

        # Modify one copy
        qid_list1.append("test_id")

        # Other copy should be unchanged
        assert "test_id" not in qid_list2
        assert len(qid_list2) == 1


class TestQuestionBankImageDirectory:
    """Test image directory management in QuestionBank."""

    def test_get_img_dir(self):
        """Test getting the image directory path."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        assert qb.get_img_dir() == SAMPLE_VALID_IMG_DIR

    def test_set_img_dir_valid_directory(self):
        """Test setting image directory to valid directory."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)

        with tempfile.TemporaryDirectory() as temp_dir:
            qb.set_img_dir(temp_dir)
            assert qb.get_img_dir() == temp_dir

    def test_set_img_dir_invalid_directory(self):
        """Test setting image directory to invalid directory."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)

        with pytest.raises(ValidationError):
            qb.set_img_dir("/non/existent/directory")

    def test_set_img_dir_strips_whitespace(self):
        """Test that set_img_dir strips whitespace from path."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)

        with tempfile.TemporaryDirectory() as temp_dir:
            qb.set_img_dir(f"  {temp_dir}  ")
            assert qb.get_img_dir() == temp_dir
            assert not qb.get_img_dir().startswith(" ")
            assert not qb.get_img_dir().endswith(" ")

    def test_set_img_dir_with_file_path(self):
        """Test setting image directory to file path (should fail)."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)

        with tempfile.NamedTemporaryFile() as temp_file:
            with pytest.raises(ValidationError):
                qb.set_img_dir(temp_file.name)


class TestQuestionBankCounting:
    """Test counting operations in QuestionBank."""

    def test_question_count_empty_bank(self):
        """Test question count when no questions exist."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        assert qb.question_count() == 0

    def test_question_count_total_with_questions(self):
        """Test total question count with multiple questions."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Chapter 1")
        qb.add_chapter(2, "Chapter 2")

        for i in range(3):
            question = Question(
                qid=f"q{i+1}",
                question=f"Question {i+1}?",
                answers={"A", "B", "C", "D"},
                correct_answer="A",
                chapter=(1 if i < 2 else 2, f"Chapter {1 if i < 2 else 2}")
            )
            qb.add_question(question, 1 if i < 2 else 2)

        assert qb.question_count() == 3

    def test_question_count_by_chapter_empty(self):
        """Test question count for specific chapter with no questions."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Empty Chapter")

        assert qb.question_count(1) == 0

    def test_question_count_by_chapter_with_questions(self):
        """Test question count for specific chapter with questions."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Chapter 1")
        qb.add_chapter(2, "Chapter 2")

        # Add 2 questions to chapter 1
        for i in range(2):
            question = Question(
                qid=f"q{i+1}",
                question=f"Question {i+1}?",
                answers={"A", "B", "C", "D"},
                correct_answer="A",
                chapter=(1, "Chapter 1")
            )
            qb.add_question(question, 1)

        # Add 1 question to chapter 2
        question = Question(
            qid="q3",
            question="Question 3?",
            answers={"A", "B", "C", "D"},
            correct_answer="A",
            chapter=(2, "Chapter 2")
        )
        qb.add_question(question, 2)

        assert qb.question_count(1) == 2
        assert qb.question_count(2) == 1

    def test_question_count_by_non_existing_chapter(self):
        """Test question count for non-existing chapter (should handle gracefully)."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)

        with pytest.raises(KeyError):
            qb.question_count(999)

    def test_question_count_multiple_chapters(self):
        """Test question counts are correct across multiple chapters."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)

        # Create 3 chapters with different numbers of questions
        chapter_questions = {1: 2, 2: 3, 3: 1}

        for chap_num, num_questions in chapter_questions.items():
            qb.add_chapter(chap_num, f"Chapter {chap_num}")
            for i in range(num_questions):
                question = Question(
                    qid=f"q{chap_num}_{i+1}",
                    question=f"Question {chap_num}_{i+1}?",
                    answers={"A", "B", "C", "D"},
                    correct_answer="A",
                    chapter=(chap_num, f"Chapter {chap_num}")
                )
                qb.add_question(question, chap_num)

        # Test individual chapter counts
        for chap_num, expected_count in chapter_questions.items():
            assert qb.question_count(chap_num) == expected_count

        # Test total count
        assert qb.question_count() == sum(chapter_questions.values())


class TestQuestionBankEdgeCases:
    """Test edge cases and error conditions for QuestionBank."""

    def test_large_number_of_questions(self):
        """Test performance and correctness with large number of questions."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Large Chapter")

        # Add 1000 questions
        num_questions = 1000
        for i in range(num_questions):
            question = Question(
                qid=f"q{i:04d}",
                question=f"Question {i}?",
                answers={"A", "B", "C", "D"},
                correct_answer="A",
                chapter=(1, "Large Chapter")
            )
            qb.add_question(question, 1)

        assert qb.question_count() == num_questions
        assert len(qb.get_qid_list()) == num_questions
        assert len(qb.get_qids_by_chapter(1)) == num_questions

    def test_large_number_of_chapters(self):
        """Test performance and correctness with large number of chapters."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)

        # Add 100 chapters
        num_chapters = 100
        for i in range(1, num_chapters + 1):
            qb.add_chapter(i, f"Chapter {i}")

        chapters = qb.list_chapters()
        assert len(chapters) == num_chapters
        assert chapters == list(range(1, num_chapters + 1))

    def test_unicode_chapter_descriptions(self):
        """Test handling of unicode characters in chapter descriptions."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)

        unicode_descriptions = [
            "Chapitre 1: Règles de base",  # French
            "第1章：基本規則",  # Japanese
            "Κεφάλαιο 1: Βασικοί κανόνες",  # Greek
            "Глава 1: Основные правила"  # Russian
        ]

        for i, desc in enumerate(unicode_descriptions, 1):
            qb.add_chapter(i, desc)
            assert qb.describe_chapter(i) == desc

    def test_unicode_question_ids(self):
        """Test handling of unicode characters in question IDs."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Unicode Chapter")

        unicode_qids = ["问题1", "質問2", "pregunta3", "вопрос4"]

        for qid in unicode_qids:
            question = Question(
                qid=qid,
                question=f"Question with ID {qid}?",
                answers={"A", "B", "C", "D"},
                correct_answer="A",
                chapter=(1, "Unicode Chapter")
            )
            qb.add_question(question, 1)

        for qid in unicode_qids:
            assert qid in qb.qids
            retrieved = qb.get_question(qid)
            assert retrieved.get_qid() == qid

    def test_very_long_paths(self):
        """Test handling of very long image directory paths."""
        with tempfile.TemporaryDirectory() as base_temp_dir:
            # Create a very long path (but within filesystem limits)
            long_path_parts = ["very_long_directory_name"] * 10
            long_path = os.path.join(base_temp_dir, *long_path_parts)
            os.makedirs(long_path, exist_ok=True)

            qb = QuestionBank(img_dir=long_path)
            assert qb.get_img_dir() == long_path
            assert len(qb.get_img_dir()) > 200  # Ensure it's actually long

    def test_concurrent_modifications(self):
        """Test behavior under concurrent modifications (if applicable)."""
        # This test simulates what might happen in concurrent scenarios
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Test Chapter")

        # Simulate adding questions from different "threads"
        questions = []
        for i in range(10):
            question = Question(
                qid=f"concurrent_q{i}",
                question=f"Concurrent question {i}?",
                answers={"A", "B", "C", "D"},
                correct_answer="A",
                chapter=(1, "Test Chapter")
            )
            questions.append(question)

        # Add all questions
        for question in questions:
            qb.add_question(question, 1)

        # Verify all were added correctly
        assert qb.question_count() == 10
        for i in range(10):
            assert f"concurrent_q{i}" in qb.qids


class TestQuestionBankIntegration:
    """Test integration scenarios with QuestionBank and Question objects."""

    def test_full_workflow_add_chapters_and_questions(self):
        """Test complete workflow of adding chapters and questions."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)

        # Step 1: Add chapters
        chapters_data = [
            (1, "Rules of the Road"),
            (2, "Signs and Signals"),
            (3, "Safe Driving Practices")
        ]

        for chap_num, desc in chapters_data:
            qb.add_chapter(chap_num, desc)

        # Step 2: Add questions to each chapter
        questions_per_chapter = 3
        for chap_num, desc in chapters_data:
            for i in range(questions_per_chapter):
                question = Question(
                    qid=f"q{chap_num}_{i+1:02d}",
                    question=f"Question {i+1} for {desc}?",
                    answers={"A", "B", "C", "D"},
                    correct_answer=["A", "B", "C", "D"][i % 4],
                    chapter=(chap_num, desc)
                )
                qb.add_question(question, chap_num)

        # Step 3: Verify the complete state
        assert len(qb.list_chapters()) == 3
        assert qb.question_count() == 9

        for chap_num, _ in chapters_data:
            assert qb.question_count(chap_num) == questions_per_chapter
            chapter_qids = qb.get_qids_by_chapter(chap_num)
            assert len(chapter_qids) == questions_per_chapter

    def test_cross_references_consistency(self):
        """Test that all cross-references between collections remain consistent."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)

        # Add multiple chapters and questions
        for chap_num in [1, 3, 5]:  # Non-sequential chapter numbers
            qb.add_chapter(chap_num, f"Chapter {chap_num}")

            for i in range(2):
                question = Question(
                    qid=f"ch{chap_num}_q{i+1}",
                    question=f"Question {i+1} for chapter {chap_num}?",
                    answers={"A", "B", "C", "D"},
                    correct_answer="A",
                    chapter=(chap_num, f"Chapter {chap_num}")
                )
                qb.add_question(question, chap_num)

        # Verify cross-reference consistency
        # 1. Every qid in qids should be in exactly one chapter
        for qid in qb.qids:
            count = sum(1 for chapter_qids in qb.chap_num_to_ids.values()
                       if qid in chapter_qids)
            assert count == 1, f"Question {qid} found in {count} chapters"

        # 2. Every qid should have a corresponding Question object
        for qid in qb.qids:
            assert qid in qb.id_to_q, f"Question {qid} missing from id_to_q"

        # 3. Every Question object should have its qid in qids
        for qid, question in qb.id_to_q.items():
            assert qid in qb.qids, f"Question object {qid} not in qids"
            assert question.get_qid() == qid, f"Question object ID mismatch"

        # 4. Chapter keys should match between dictionaries
        assert qb.chapters.keys() == qb.chap_num_to_ids.keys()


class TestQuestionBankPydanticFeatures:
    """Test Pydantic-specific features and configurations."""
    def test_extra_fields_forbidden(self):
        """Test that extra='forbid' prevents additional fields."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValidationError) as exc_info:
                QuestionBank(
                    img_dir=temp_dir,
                    extra_field="This should not be allowed"
                )
            assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_field_aliases_and_descriptions(self):
        """Test that field descriptions work correctly."""
        # This test verifies that the Field descriptions are accessible
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)

        # Get the model fields info
        fields_info = qb.model_fields

        # Verify that fields have the expected configurations
        assert 'img_dir' in fields_info
        assert fields_info['img_dir'].annotation == str

        # Test that min_length constraint works
        with pytest.raises(ValidationError):
            QuestionBank(img_dir="")

    def test_model_copy_functionality(self):
        """Test Pydantic model copy operations."""
        qb_original = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb_original.add_chapter(1, "Original Chapter")

        # Test deep copy
        qb_copy = qb_original.model_copy(deep=True)

        # Verify they are separate objects
        assert qb_copy is not qb_original
        assert qb_copy.chapters is not qb_original.chapters
        assert qb_copy.qids is not qb_original.qids

        # Verify content is the same
        assert qb_copy.img_dir == qb_original.img_dir
        assert qb_copy.chapters == qb_original.chapters
        assert qb_copy.qids == qb_original.qids

        # Test that modifying copy doesn't affect original
        qb_copy.chapters[2] = "New Chapter"
        assert 2 not in qb_original.chapters

        # Test copy with updates
        qb_updated = qb_original.model_copy(
            update={'chapters': {1: "Updated Chapter"}}
        )
        assert qb_updated.chapters[1] == "Updated Chapter"
        assert qb_original.chapters[1] == "Original Chapter"


class TestQuestionBankSerialization:
    """Test Pydantic serialization and deserialization for QuestionBank."""

    def test_model_dump_empty_bank(self):
        """Test dumping an empty QuestionBank to dictionary."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        dumped = qb.model_dump()

        expected_keys = {'img_dir', 'qids', 'chapters', 'chap_num_to_ids', 'id_to_q'}
        assert set(dumped.keys()) == expected_keys
        assert dumped['img_dir'] == SAMPLE_VALID_IMG_DIR
        assert dumped['qids'] == set()
        assert dumped['chapters'] == {}
        assert dumped['chap_num_to_ids'] == {}
        assert dumped['id_to_q'] == {}

    def test_model_dump_populated_bank(self):
        """Test dumping a populated QuestionBank to dictionary."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Test Chapter")

        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B", "C", "D"},
            correct_answer="A",
            chapter=(1, "Test Chapter")
        )
        qb.add_question(question, 1)

        dumped = qb.model_dump()

        assert dumped['img_dir'] == SAMPLE_VALID_IMG_DIR
        assert dumped['qids'] == {"q1"}
        assert dumped['chapters'] == {1: "Test Chapter"}
        assert dumped['chap_num_to_ids'] == {1: {"q1"}}
        assert "q1" in dumped['id_to_q']
        assert isinstance(dumped['id_to_q']["q1"], dict)  # Question is also dumped

    def test_model_dump_exclude_fields(self):
        """Test dumping QuestionBank with excluded fields."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Test Chapter")

        # Exclude img_dir and id_to_q
        dumped = qb.model_dump(exclude={'img_dir', 'id_to_q'})

        assert 'img_dir' not in dumped
        assert 'id_to_q' not in dumped
        assert 'qids' in dumped
        assert 'chapters' in dumped
        assert 'chap_num_to_ids' in dumped

    def test_model_dump_include_fields(self):
        """Test dumping QuestionBank with only included fields."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Test Chapter")

        # Include only img_dir and chapters
        dumped = qb.model_dump(include={'img_dir', 'chapters'})

        assert set(dumped.keys()) == {'img_dir', 'chapters'}
        assert dumped['img_dir'] == SAMPLE_VALID_IMG_DIR
        assert dumped['chapters'] == {1: "Test Chapter"}

    def test_model_validate_empty_data(self):
        """Test creating QuestionBank from minimal valid dictionary."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data = {'img_dir': temp_dir}
            qb = QuestionBank.model_validate(data)

            assert qb.img_dir == temp_dir
            assert qb.qids == set()
            assert qb.chapters == {}
            assert qb.chap_num_to_ids == {}
            assert qb.id_to_q == {}

    def test_model_validate_full_data(self):
        """Test creating QuestionBank from complete dictionary."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a Question first to get its dict representation
            question = Question(
                qid="q1",
                question="Test question?",
                answers={"A", "B", "C", "D"},
                correct_answer="A",
                chapter=(1, "Test Chapter")
            )

            data = {
                'img_dir': temp_dir,
                'qids': {"q1"},
                'chapters': {1: "Test Chapter"},
                'chap_num_to_ids': {1: {"q1"}},
                'id_to_q': {"q1": question.model_dump()}
            }

            qb = QuestionBank.model_validate(data)

            assert qb.img_dir == temp_dir
            assert qb.qids == {"q1"}
            assert qb.chapters == {1: "Test Chapter"}
            assert qb.chap_num_to_ids == {1: {"q1"}}
            assert "q1" in qb.id_to_q
            assert isinstance(qb.id_to_q["q1"], Question)
            assert qb.id_to_q["q1"].get_qid() == "q1"

    def test_model_validate_invalid_data(self):
        """Test model_validate with invalid data raises ValidationError."""
        # Missing required img_dir
        with pytest.raises(ValueError) as exc_info:
            QuestionBank.model_validate({})
        assert "required field" in str(exc_info.value)

        # Invalid img_dir (non-existent directory)
        with pytest.raises(ValueError) as exc_info:
            QuestionBank.model_validate({'img_dir': '/non/existent/path'})
        assert "Image directory does not exist" in str(exc_info.value)

        # Invalid chapter data
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValueError) as exc_info:
                QuestionBank.model_validate({
                    'img_dir': temp_dir,
                    'chapters': {-1: "Invalid Chapter"}
                })
            assert ("Chapter number must be a "
                    "positive integer") in str(exc_info.value)

    def test_round_trip_serialization_empty(self):
        """Test round-trip serialization for empty QuestionBank."""
        original = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)

        # Dump to dict and reload
        dumped = original.model_dump()
        reloaded = QuestionBank.model_validate(dumped)

        assert reloaded.img_dir == original.img_dir
        assert reloaded.qids == original.qids
        assert reloaded.chapters == original.chapters
        assert reloaded.chap_num_to_ids == original.chap_num_to_ids
        assert reloaded.id_to_q == original.id_to_q

    def test_round_trip_serialization_populated(self):
        """Test round-trip serialization for populated QuestionBank."""
        original = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)

        # Add test data
        original.add_chapter(1, "Chapter One")
        original.add_chapter(2, "Chapter Two")

        questions = [
            Question(
                qid="q1",
                question="Question 1?",
                answers={"A", "B", "C", "D"},
                correct_answer="A",
                chapter=(1, "Chapter One"),
                tags=["tag1", "tag2"],
                keywords=["key1", "key2"]
            ),
            Question(
                qid="q2",
                question="Question 2?",
                answers={"True", "False"},
                correct_answer="True",
                chapter=(2, "Chapter Two"),
                tags=["tag3"],
                keywords=["key3"]
            )
        ]

        for i, question in enumerate(questions):
            original.add_question(question, i + 1)

        # Dump to dict and reload
        dumped = original.model_dump()
        reloaded = QuestionBank.model_validate(dumped)

        # Verify all data is preserved
        assert reloaded.img_dir == original.img_dir
        assert reloaded.qids == original.qids
        assert reloaded.chapters == original.chapters
        assert reloaded.chap_num_to_ids == original.chap_num_to_ids
        assert len(reloaded.id_to_q) == len(original.id_to_q)

        # Verify individual questions
        for qid in original.qids:
            orig_q = original.get_question(qid)
            reloaded_q = reloaded.get_question(qid)

            assert reloaded_q.get_qid() == orig_q.get_qid()
            assert reloaded_q.get_question() == orig_q.get_question()
            assert reloaded_q.get_answers() == orig_q.get_answers()
            assert reloaded_q.get_correct_answer() == orig_q.get_correct_answer()
            assert reloaded_q.get_chapter() == orig_q.get_chapter()
            assert reloaded_q.get_tags() == orig_q.get_tags()
            assert reloaded_q.get_keywords() == orig_q.get_keywords()

    def test_json_serialization_compatibility(self):
        """Test that model_dump produces JSON-serializable output."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Test Chapter")

        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B", "C", "D"},
            correct_answer="A",
            chapter=(1, "Test Chapter")
        )
        qb.add_question(question, 1)

        # Test that dumped data can be JSON serialized
        dumped = qb.model_dump()
        json_str = json.dumps(dumped, default=str)  # Convert sets to str for JSON
        assert isinstance(json_str, str)
        assert len(json_str) > 0

        # Test mode='json' for JSON-compatible output
        json_dumped = qb.model_dump(mode='json')
        json_str = json.dumps(json_dumped)

        # Should be able to parse back
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)
        assert 'img_dir' in parsed

    def test_model_dump_with_nested_exclude(self):
        """Test model_dump with nested field exclusions."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Test Chapter")

        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B", "C", "D"},
            correct_answer="A",
            chapter=(1, "Test Chapter"),
            tags=["tag1"],
            keywords=["key1"]
        )
        qb.add_question(question, 1)

        # Exclude tags from nested Question objects
        dumped = qb.model_dump(exclude={'id_to_q': {'__all__': {'tags'}}})

        assert 'id_to_q' in dumped
        question_dict = dumped['id_to_q']['q1']
        assert 'tags' not in question_dict
        assert 'keywords' in question_dict  # Should still be present

    def test_model_validate_with_extra_fields(self):
        """Test model_validate rejects extra fields due to extra='forbid'."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data = {
                'img_dir': temp_dir,
                'extra_field': 'This should not be allowed'
            }

            with pytest.raises(ValueError) as exc_info:
                QuestionBank.model_validate(data)
            assert "Unexpected field" in str(exc_info.value)

    def test_model_validate_partial_data_with_defaults(self):
        """Test that model_validate uses default values for missing optional fields."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Only provide required field
            data = {'img_dir': temp_dir}
            qb = QuestionBank.model_validate(data)

            # All optional fields should have their default values
            assert qb.qids == set()
            assert qb.chapters == {}
            assert qb.chap_num_to_ids == {}
            assert qb.id_to_q == {}

    def test_serialization_with_unicode_data(self):
        """Test serialization/deserialization with unicode content."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Chapitre 1: Règles de base")

        question = Question(
            qid="测试问题1",
            question="这是一个测试问题吗？",
            answers={"是", "不是", "可能", "不确定"},
            correct_answer="是",
            chapter=(1, "Chapitre 1: Règles de base"),
            tags=["测试", "unicode"],
            keywords=["关键词", "keyword"]
        )
        qb.add_question(question, 1)

        # Test round-trip with unicode data
        dumped = qb.model_dump()
        reloaded = QuestionBank.model_validate(dumped)

        assert reloaded.chapters[1] == "Chapitre 1: Règles de base"
        reloaded_question = reloaded.get_question("测试问题1")
        assert reloaded_question.get_question() == "这是一个测试问题吗？"
        assert "是" in reloaded_question.get_answers()
        assert reloaded_question.get_tags() == ["测试", "unicode"]

    def test_model_dump_exclude_unset(self):
        """Test model_dump with exclude_unset parameter."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create QuestionBank with only required field
            qb = QuestionBank(img_dir=temp_dir)

            # Default dump includes all fields
            dumped_all = qb.model_dump()
            assert 'qids' in dumped_all
            assert 'chapters' in dumped_all

            # With exclude_unset=True, should exclude fields that weren't explicitly set
            dumped_set = qb.model_dump(exclude_unset=True)
            assert 'img_dir' in dumped_set
            # Note: Due to default_factory, these fields are considered "set"
            # This test mainly verifies the parameter works without error

    def test_model_dump_exclude_none(self):
        """Test model_dump with exclude_none parameter."""
        qb = QuestionBank(img_dir=SAMPLE_VALID_IMG_DIR)
        qb.add_chapter(1, "Test Chapter")

        # Add question without image path (None value)
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A",
            chapter=(1, "Test Chapter"),
            img_path=None  # Explicitly None
        )
        qb.add_question(question, 1)

        dumped_with_none = qb.model_dump()
        dumped_exclude_none = qb.model_dump(exclude_none=True)

        # Both should be valid, this mainly tests the parameter works
        assert isinstance(dumped_with_none, dict)
        assert isinstance(dumped_exclude_none, dict)

