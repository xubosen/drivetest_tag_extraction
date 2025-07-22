import pytest
from entities.question import Question
from pydantic import ValidationError
import json

SAMPLE_IMG_PATH = "test_db/raw_db/images/0a1e1.webp"
SAMPLE_IMG_PATH2 = "test_db/raw_db/images/0b5ae.webp"

class TestQuestionCreation:
    """Test class for Question model creation and validation."""

    def test_valid_question_creation(self):
        """Test creating a Question with valid minimum required fields."""
        question = Question(
            qid="q1",
            question="What is the speed limit?",
            answers={"50 km/h", "60 km/h"},
            correct_answer="50 km/h"
        )
        assert question.qid == "q1"
        assert question.question == "What is the speed limit?"
        assert question.answers == {"50 km/h", "60 km/h"}
        assert question.correct_answer == "50 km/h"
        assert question.chapter is None
        assert question.img_path is None
        assert question.tags == []
        assert question.keywords == []

    def test_valid_question_creation_with_all_fields(self):
        """Test creating a Question with all fields provided."""
        question = Question(
            qid="q2",
            chapter=(3, "Traffic Rules"),
            question="When should you stop at a red light?",
            img_path=SAMPLE_IMG_PATH,
            answers={"Immediately", "After 3 seconds", "Never"},
            correct_answer="Immediately",
            tags=["traffic", "signals"],
            keywords=["red light", "stop"]
        )
        assert question.qid == "q2"
        assert question.chapter == (3, "Traffic Rules")
        assert question.question == "When should you stop at a red light?"
        assert question.img_path == SAMPLE_IMG_PATH
        assert question.answers == {"Immediately", "After 3 seconds", "Never"}
        assert question.correct_answer == "Immediately"
        assert question.tags == ["traffic", "signals"]
        assert question.keywords == ["red light", "stop"]

    def test_invalid_qid_empty_string(self):
        """Test that creating Question with empty qid raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Question(
                qid="",
                question="What is the speed limit?",
                answers={"50 km/h", "60 km/h"},
                correct_answer="50 km/h",
                img_path=SAMPLE_IMG_PATH
            )
        assert "qid" in str(exc_info.value)

    def test_invalid_question_empty_string(self):
        """Test that creating Question with empty question text raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Question(
                qid="q1",
                question="",
                answers={"50 km/h", "60 km/h"},
                correct_answer="50 km/h",
                img_path=SAMPLE_IMG_PATH
            )
        assert "question" in str(exc_info.value)

    def test_invalid_answers_too_few(self):
        """Test that creating Question with less than 2 answers raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Question(
                qid="q1",
                question="What is the speed limit?",
                answers={"50 km/h"},
                correct_answer="50 km/h"
            )
        assert "answers" in str(exc_info.value)

    def test_invalid_correct_answer_empty(self):
        """Test that creating Question with empty correct_answer raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Question(
                qid="q1",
                question="What is the speed limit?",
                answers={"50 km/h", "60 km/h"},
                correct_answer=""
            )
        assert "correct_answer" in str(exc_info.value)

    def test_invalid_tags_non_string(self):
        """Test that providing non-string items in tags raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Question(
                qid="q1",
                question="What is the speed limit?",
                answers={"50 km/h", "60 km/h"},
                correct_answer="50 km/h",
                tags=["valid_tag", 123, "another_tag"]
            )
        assert "Input should be a valid string" in str(exc_info.value)

    def test_invalid_keywords_non_string(self):
        """Test that providing non-string items in keywords raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Question(
                qid="q1",
                question="What is the speed limit?",
                answers={"50 km/h", "60 km/h"},
                correct_answer="50 km/h",
                keywords=["valid_keyword", None, "another_keyword"]
            )
        assert "Input should be a valid string" in str(exc_info.value)

    def test_invalid_tags_empty_string(self):
        """Test that providing empty strings in tags raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Question(
                qid="q1",
                question="What is the speed limit?",
                answers={"50 km/h", "60 km/h"},
                correct_answer="50 km/h",
                tags=["valid_tag", "", "another_tag"]
            )
        assert "non-empty strings" in str(exc_info.value)

    def test_invalid_keywords_empty_string(self):
        """Test that providing empty strings in keywords raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Question(
                qid="q1",
                question="What is the speed limit?",
                answers={"50 km/h", "60 km/h"},
                correct_answer="50 km/h",
                keywords=["valid_keyword", "", "another_keyword"]
            )
        assert "non-empty strings" in str(exc_info.value)

    def test_tags_whitespace_trimming(self):
        """Test that whitespace is trimmed from tags during validation."""
        question = Question(
            qid="q1",
            question="What is the speed limit?",
            answers={"50 km/h", "60 km/h"},
            correct_answer="50 km/h",
            tags=["  traffic  ", "\tspeed\t", "\nrules\n"]
        )
        assert question.tags == ["traffic", "speed", "rules"]

    def test_keywords_whitespace_trimming(self):
        """Test that whitespace is trimmed from keywords during validation."""
        question = Question(
            qid="q1",
            question="What is the speed limit?",
            answers={"50 km/h", "60 km/h"},
            correct_answer="50 km/h",
            keywords=["  speed limit  ", "\tdriving\t", "\nsafety\n"]
        )
        assert question.keywords == ["speed limit", "driving", "safety"]


class TestQuestionGetters:
    """Test class for Question getter methods."""

    def test_get_qid(self):
        """Test that get_qid returns the correct question ID."""
        question = Question(
            qid="test_id_123",
            question="What is the speed limit?",
            answers={"50 km/h", "60 km/h"},
            correct_answer="50 km/h"
        )
        assert question.get_qid() == "test_id_123"

    def test_get_question(self):
        """Test that get_question returns the correct question text."""
        question_text = "When should you use your turn signal?"
        question = Question(
            qid="q1",
            question=question_text,
            answers={"Always", "Sometimes", "Never"},
            correct_answer="Always"
        )
        assert question.get_question() == question_text

    def test_get_answers(self):
        """Test that get_answers returns the correct set of answers."""
        answers = {"Option A", "Option B", "Option C", "Option D"}
        question = Question(
            qid="q1",
            question="Test question?",
            answers=answers,
            correct_answer="Option A"
        )
        assert question.get_answers() == answers

    def test_get_answers_returns_copy(self):
        """Test that get_answers returns a copy, not the original set."""
        original_answers = {"Answer 1", "Answer 2", "Answer 3"}
        question = Question(
            qid="q1",
            question="Test question?",
            answers=original_answers,
            correct_answer="Answer 1"
        )
        returned_answers = question.get_answers()

        # Modify the returned set
        returned_answers.add("New Answer")

        # Original should remain unchanged
        assert question.get_answers() == original_answers
        assert "New Answer" not in question.get_answers()

    def test_get_correct_answer(self):
        """Test that get_correct_answer returns the correct answer."""
        correct_answer = "The correct option"
        question = Question(
            qid="q1",
            question="Test question?",
            answers={correct_answer, "Wrong option"},
            correct_answer=correct_answer
        )
        assert question.get_correct_answer() == correct_answer

    def test_get_chapter(self):
        """Test that get_chapter returns the correct chapter tuple."""
        chapter_info = (5, "Traffic Signs")
        question = Question(
            qid="q1",
            chapter=chapter_info,
            question="What does this sign mean?",
            answers={"Stop", "Yield", "Go"},
            correct_answer="Stop"
        )
        assert question.get_chapter() == chapter_info

    def test_get_chapter_default(self):
        """Test that get_chapter returns default (0, '') when not set."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        assert question.get_chapter() is None

    def test_get_tags(self):
        """Test that get_tags returns the correct list of tags."""
        tags = ["safety", "traffic", "rules"]
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A",
            tags=tags
        )
        assert question.get_tags() == tags

    def test_get_tags_returns_copy(self):
        """Test that get_tags returns a copy, not the original list."""
        original_tags = ["tag1", "tag2", "tag3"]
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A",
            tags=original_tags
        )
        returned_tags = question.get_tags()

        # Modify the returned list
        returned_tags.append("new_tag")

        # Original should remain unchanged
        assert question.get_tags() == original_tags
        assert "new_tag" not in question.get_tags()

    def test_get_tags_empty_list(self):
        """Test that get_tags returns empty list when no tags are set."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        assert question.get_tags() == []

    def test_get_keywords(self):
        """Test that get_keywords returns the correct list of keywords."""
        keywords = ["speed", "limit", "highway"]
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A",
            keywords=keywords
        )
        assert question.get_keywords() == keywords

    def test_get_keywords_returns_copy(self):
        """Test that get_keywords returns a copy, not the original list."""
        original_keywords = ["keyword1", "keyword2", "keyword3"]
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A",
            keywords=original_keywords
        )
        returned_keywords = question.get_keywords()

        # Modify the returned list
        returned_keywords.append("new_keyword")

        # Original should remain unchanged
        assert question.get_keywords() == original_keywords
        assert "new_keyword" not in question.get_keywords()

    def test_get_keywords_empty_list(self):
        """Test that get_keywords returns empty list when no keywords are set."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        assert question.get_keywords() == []


class TestImageMethods:
    """Test class for image-related methods."""

    def test_has_img_true(self):
        """Test that has_img returns True when img_path is set."""
        question = Question(
            qid="q1",
            question="What does this sign mean?",
            answers={"Stop", "Go", "Yield"},
            correct_answer="Stop",
            img_path=SAMPLE_IMG_PATH
        )
        assert question.has_img() is True

    def test_has_img_false_none(self):
        """Test that has_img returns False when img_path is None."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A",
            img_path=None
        )
        assert question.has_img() is False

    def test_has_img_false_default(self):
        """Test that has_img returns False when img_path is not provided."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        assert question.has_img() is False

    def test_get_img_path_with_path(self):
        """Test that get_img_path returns the correct path when set."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A",
            img_path=SAMPLE_IMG_PATH
        )
        assert question.get_img_path() == SAMPLE_IMG_PATH

    def test_get_img_path_none(self):
        """Test that get_img_path returns None when not set."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        assert question.get_img_path() is None

    def test_set_img_path_valid_string(self):
        """Test setting img_path with a valid string path."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        question.set_img_path(SAMPLE_IMG_PATH2)
        assert question.get_img_path() == SAMPLE_IMG_PATH2
        assert question.has_img() is True

    def test_set_img_path_none(self):
        """Test setting img_path to None."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A",
            img_path=SAMPLE_IMG_PATH
        )
        question.set_img_path(None)
        assert question.get_img_path() is None
        assert question.has_img() is False

    def test_set_img_path_empty_string(self):
        """Test setting img_path to empty string."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        # Test that setting img_path to an empty string raises Validation Error
        with pytest.raises(ValidationError) as exc_info:
            question.set_img_path("")
        assert "Image path does not exist" in str(exc_info.value)

    def test_set_img_path_invalid_path(self):
        """Test setting img_path with an invalid path raises ValueError."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        with pytest.raises(ValueError) as exc_info:
            question.set_img_path("invalid/path/to/image.jpg")
        assert "Image path does not exist" in str(exc_info.value)


class TestChapterMethods:
    """Test class for chapter-related methods."""

    def test_set_chapter_valid_tuple(self):
        """Test setting chapter with a valid (int, str) tuple."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        new_chapter = (5, "Traffic Signs")
        question.set_chapter(new_chapter)
        assert question.get_chapter() == new_chapter

    def test_set_chapter_zero_number(self):
        """Test setting chapter with zero as chapter number."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        zero_chapter = (0, "Introduction")
        with pytest.raises(ValidationError) as exc_info:
            question.set_chapter(zero_chapter)
        assert ("Chapter number must be a positive integer" in
                str(exc_info.value))

    def test_set_chapter_negative_number(self):
        """Test setting chapter with negative chapter number."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        negative_chapter = (-1, "Review")
        with pytest.raises(ValidationError) as exc_info:
            question.set_chapter(negative_chapter)
        assert ("Chapter number must be a positive integer" in
                str(exc_info.value))

    def test_set_chapter_empty_name(self):
        """Test setting chapter with empty string as name."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        empty_name_chapter = (3, "")
        with pytest.raises(ValidationError) as exc_info:
            question.set_chapter(empty_name_chapter)
        assert "Chapter name must be a non-empty string" in str(exc_info.value)

    def test_set_chapter_name_spaces(self):
        """ Test setting chapter with name that has only spaces."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        new_chapter = (1, "   ")
        with pytest.raises(ValidationError) as exc_info:
            question.set_chapter(new_chapter)
        assert "Chapter name must be a non-empty string" in str(exc_info.value)


class TestTagMethods:
    """Test class for tag-related methods."""

    def test_set_tags_valid_list(self):
        """Test setting tags with a valid list of strings."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        tags = ["safety", "traffic", "rules"]
        question.set_tags(tags)
        assert question.get_tags() == tags

    def test_set_tags_empty_list(self):
        """Test setting tags with an empty list."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A",
            tags=["existing", "tags"]
        )
        question.set_tags([])
        assert question.get_tags() == []

    def test_set_tags_single_item(self):
        """Test setting tags with a list containing one item."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        single_tag = ["single_tag"]
        question.set_tags(single_tag)
        assert question.get_tags() == single_tag

    def test_set_tags_creates_copy(self):
        """Test that set_tags creates a copy of the input list."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        original_tags = ["tag1", "tag2", "tag3"]
        question.set_tags(original_tags)

        # Modify the original list
        original_tags.append("new_tag")

        # Question's tags should not be affected
        assert question.get_tags() == ["tag1", "tag2", "tag3"]
        assert "new_tag" not in question.get_tags()

    def test_set_tags_invalid_empty_string(self):
        """Test that set_tags raises ValueError for empty string tags."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        with pytest.raises(ValidationError) as exc_info:
            question.set_tags(["valid_tag", "", "another_tag"])
        assert "non-empty strings" in str(exc_info.value)

    def test_set_tags_invalid_whitespace_only(self):
        """Test that set_tags handles whitespace-only strings."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        with pytest.raises(ValidationError) as exc_info:
            question.set_tags(["valid_tag", "   ", "another_tag"])
        assert "non-empty strings" in str(exc_info.value)

    def test_add_tag_valid(self):
        """Test adding a valid tag to existing tags."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A",
            tags=["existing_tag"]
        )
        question.add_tag("new_tag")
        assert "new_tag" in question.get_tags()
        assert "existing_tag" in question.get_tags()
        assert len(question.get_tags()) == 2

    def test_add_tag_to_empty_list(self):
        """Test adding a tag when tags list is initially empty."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        question.add_tag("first_tag")
        assert question.get_tags() == ["first_tag"]

    def test_add_tag_multiple_times(self):
        """Test that add_tag handles duplicate tags."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        question.add_tag("tag1")
        question.add_tag("tag2")
        question.add_tag("tag3")
        assert question.get_tags() == ["tag1", "tag2", "tag3"]

    def test_add_tag_invalid_empty_string(self):
        """Test that add_tag raises ValueError for empty string."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        with pytest.raises(ValueError) as exc_info:
            question.add_tag("")
        assert "non-empty strings" in str(exc_info.value)

    def test_add_tag_invalid_whitespace_only(self):
        """Test that add_tag raises ValueError for whitespace-only string."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        with pytest.raises(ValueError) as exc_info:
            question.add_tag("      ")
        assert "non-empty strings" in str(exc_info.value)

    def test_add_tag_duplicates(self):
        """Test that add_tag handles duplicate tags correctly."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A",
            tags=["existing_tag"]
        )
        question.add_tag("existing_tag")
        # Since add_tag checks if tag not in self.tags, it shouldn't add duplicates
        assert question.get_tags().count("existing_tag") == 1
        assert len(question.get_tags()) == 1


class TestKeywordMethods:
    """Test class for keyword-related methods."""

    def test_set_keywords_valid_list(self):
        """Test setting keywords with a valid list of strings."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        keywords = ["speed", "limit", "highway"]
        question.set_keywords(keywords)
        assert question.get_keywords() == keywords

    def test_set_keywords_empty_list(self):
        """Test setting keywords with an empty list."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A",
            keywords=["existing", "keywords"]
        )
        question.set_keywords([])
        assert question.get_keywords() == []

    def test_set_keywords_single_item(self):
        """Test setting keywords with a list containing one item."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        single_keyword = ["single_keyword"]
        question.set_keywords(single_keyword)
        assert question.get_keywords() == single_keyword

    def test_set_keywords_creates_copy(self):
        """Test that set_keywords creates a copy of the input list."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        original_keywords = ["keyword1", "keyword2", "keyword3"]
        question.set_keywords(original_keywords)

        # Modify the original list
        original_keywords.append("new_keyword")

        # Question's keywords should not be affected
        assert question.get_keywords() == ["keyword1", "keyword2", "keyword3"]
        assert "new_keyword" not in question.get_keywords()

    def test_set_keywords_invalid_empty_string(self):
        """Test that set_keywords raises ValueError for empty string keywords."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        with pytest.raises(ValidationError) as exc_info:
            question.set_keywords(["valid_keyword", "", "another_keyword"])
        assert "non-empty strings" in str(exc_info.value)

    def test_set_keywords_invalid_whitespace_only(self):
        """Test that set_keywords handles whitespace-only strings."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        with pytest.raises(ValidationError) as exc_info:
            question.set_keywords(["valid_keyword", "   ", "another_keyword"])
        assert "non-empty strings" in str(exc_info.value)

    def test_add_keyword_valid(self):
        """Test adding a valid keyword to existing keywords."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A",
            keywords=["existing_keyword"]
        )
        question.add_keyword("new_keyword")
        assert "new_keyword" in question.get_keywords()
        assert "existing_keyword" in question.get_keywords()
        assert len(question.get_keywords()) == 2

    def test_add_keyword_to_empty_list(self):
        """Test adding a keyword when keywords list is initially empty."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        question.add_keyword("first_keyword")
        assert question.get_keywords() == ["first_keyword"]

    def test_add_keyword_multiple_times(self):
        """Test adding multiple keywords sequentially."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        question.add_keyword("keyword1")
        question.add_keyword("keyword2")
        question.add_keyword("keyword3")
        assert question.get_keywords() == ["keyword1", "keyword2", "keyword3"]

    def test_add_keyword_invalid_empty_string(self):
        """Test that add_keyword raises ValueError for empty string."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        with pytest.raises(ValueError) as exc_info:
            question.add_keyword("")
        assert "non-empty strings" in str(exc_info.value)

    def test_add_keyword_invalid_whitespace_only(self):
        """Test that add_keyword raises ValueError for whitespace-only string."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )
        with pytest.raises(ValueError) as exc_info:
            question.add_keyword("      ")
        assert "non-empty strings" in str(exc_info.value)

    def test_add_keyword_allows_duplicates(self):
        """Test that add_keyword allows duplicate keywords."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A",
            keywords=["existing_keyword"]
        )
        question.add_keyword("existing_keyword")
        # Since add_keyword checks if keyword not in self.keywords, it shouldn't add duplicates
        assert question.get_keywords().count("existing_keyword") == 1
        assert len(question.get_keywords()) == 1


class TestQuestionValidation:
    """Test class for Pydantic validation and configuration."""

    def test_validate_assignment_enabled(self):
        """Test that validate_assignment=True works for field updates."""
        question = Question(
            qid="q1",
            question="Test question?",
            answers={"A", "B"},
            correct_answer="A"
        )

        # Test that validation occurs when updating fields after creation
        with pytest.raises(ValidationError) as exc_info:
            question.qid = ""  # Should trigger validation
        assert "qid" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            question.question = ""  # Should trigger validation
        assert "question" in str(exc_info.value)

    def test_extra_fields_forbidden(self):
        """Test that extra='forbid' prevents adding unexpected fields."""
        # Test that creating Question with extra fields raises ValidationError
        with pytest.raises(ValidationError) as exc_info:
            Question(
                qid="q1",
                question="Test question?",
                answers={"A", "B"},
                correct_answer="A",
                extra_field="this should not be allowed"  # Extra field
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_field_type_validation(self):
        """Test that field types are validated correctly."""
        # Test wrong type for qid (should be string)
        with pytest.raises(ValidationError) as exc_info:
            Question(
                qid=123,  # Wrong type
                question="Test question?",
                answers={"A", "B"},
                correct_answer="A"
            )
        assert "Input should be a valid string" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            Question(
                qid="q1",
                question="Test question?",
                answers="invalid",  # Wrong type
                correct_answer="A"
            )
        assert "Input should be a valid set" in str(exc_info.value)


class TestQuestionEdgeCases:
    """Test class for edge cases and boundary conditions."""

    def test_unicode_characters(self):
        """Test Question creation with unicode characters in strings."""
        # Test unicode characters in various string fields
        question = Question(
            qid="q1_测试",
            chapter=(1, "Тест章节"),
            question="What is the meaning of life? 人生の意味は何ですか？",
            answers={"答案A", "Ответ Б", "Answer C", "回答D"},
            correct_answer="答案A",
            tags=["测试", "тест", "テスト"],
            keywords=["生活", "жизнь", "life"]
        )

        assert question.qid == "q1_测试"
        assert question.chapter == (1, "Тест章节")
        assert "人生の意味は何ですか？" in question.question
        assert "答案A" in question.answers
        assert question.correct_answer == "答案A"
        assert "测试" in question.tags
        assert "生活" in question.keywords

    def test_special_characters_in_answers(self):
        """Test Question creation with special characters in answers set."""
        special_answers = {
            "Option with spaces and punctuation!",
            "Option-with-dashes_and_underscores",
            "Option/with\\slashes",
            "Option@#$%^&*()symbols",
            "Option\"with'quotes",
            "Option\nwith\ttabs\rand\rcarriages",
            "Option with emoji 🚗🚦"
        }

        question = Question(
            qid="special_chars_test",
            question="Which option contains special characters?",
            answers=special_answers,
            correct_answer="Option with spaces and punctuation!"
        )

        assert question.answers == special_answers
        assert question.correct_answer == "Option with spaces and punctuation!"

        # Test that all special characters are preserved
        for answer in special_answers:
            assert answer in question.get_answers()


class TestQuestionSerialization:
    """Test class for Pydantic serialization and deserialization."""

    def test_model_dump_minimal_question(self):
        """Test dumping a Question with minimal required fields to dictionary."""
        question = Question(
            qid="q1",
            question="What is the speed limit?",
            answers={"50 km/h", "60 km/h"},
            correct_answer="50 km/h"
        )

        dumped = question.model_dump()

        assert dumped["qid"] == "q1"
        assert dumped["question"] == "What is the speed limit?"
        assert set(dumped["answers"]) == {"50 km/h", "60 km/h"}
        assert dumped["correct_answer"] == "50 km/h"
        assert dumped["chapter"] is None
        assert dumped["img_path"] is None
        assert dumped["tags"] == []
        assert dumped["keywords"] == []

    def test_model_dump_full_question(self):
        """Test dumping a Question with all fields to dictionary."""
        question = Question(
            qid="q2",
            chapter=(3, "Traffic Rules"),
            question="When should you stop at a red light?",
            img_path=SAMPLE_IMG_PATH,
            answers={"Immediately", "After 3 seconds", "Never"},
            correct_answer="Immediately",
            tags=["traffic", "signals"],
            keywords=["red light", "stop"]
        )

        dumped = question.model_dump()

        assert dumped["qid"] == "q2"
        assert dumped["chapter"] == (3, "Traffic Rules")
        assert dumped["question"] == "When should you stop at a red light?"
        assert dumped["img_path"] == SAMPLE_IMG_PATH
        assert set(dumped["answers"]) == {"Immediately", "After 3 seconds", "Never"}
        assert dumped["correct_answer"] == "Immediately"
        assert dumped["tags"] == ["traffic", "signals"]
        assert dumped["keywords"] == ["red light", "stop"]

    def test_model_validate_from_dict_minimal(self):
        """Test loading a Question from dictionary with minimal fields."""
        data = {
            "qid": "q1",
            "question": "What is the speed limit?",
            "answers": ["50 km/h", "60 km/h"],
            "correct_answer": "50 km/h"
        }

        question = Question.model_validate(data)

        assert question.qid == "q1"
        assert question.question == "What is the speed limit?"
        assert question.answers == {"50 km/h", "60 km/h"}
        assert question.correct_answer == "50 km/h"
        assert question.chapter is None
        assert question.img_path is None
        assert question.tags == []
        assert question.keywords == []

    def test_model_validate_from_dict_full(self):
        """Test loading a Question from dictionary with all fields."""
        data = {
            "qid": "q2",
            "chapter": [3, "Traffic Rules"],
            "question": "When should you stop at a red light?",
            "img_path": SAMPLE_IMG_PATH,
            "answers": ["Immediately", "After 3 seconds", "Never"],
            "correct_answer": "Immediately",
            "tags": ["traffic", "signals"],
            "keywords": ["red light", "stop"]
        }

        question = Question.model_validate(data)

        assert question.qid == "q2"
        assert question.chapter == (3, "Traffic Rules")
        assert question.question == "When should you stop at a red light?"
        assert question.img_path == SAMPLE_IMG_PATH
        assert question.answers == {"Immediately", "After 3 seconds", "Never"}
        assert question.correct_answer == "Immediately"
        assert question.tags == ["traffic", "signals"]
        assert question.keywords == ["red light", "stop"]

    def test_round_trip_serialization_minimal(self):
        """Test that a Question can be dumped and loaded without data loss (minimal)."""
        original = Question(
            qid="q1",
            question="What is the speed limit?",
            answers={"50 km/h", "60 km/h"},
            correct_answer="50 km/h"
        )

        # Dump to dict and load back
        dumped = original.model_dump()
        loaded = Question.model_validate(dumped)

        assert loaded.qid == original.qid
        assert loaded.question == original.question
        assert loaded.answers == original.answers
        assert loaded.correct_answer == original.correct_answer
        assert loaded.chapter == original.chapter
        assert loaded.img_path == original.img_path
        assert loaded.tags == original.tags
        assert loaded.keywords == original.keywords

    def test_round_trip_serialization_full(self):
        """Test that a Question can be dumped and loaded without data loss (full)."""
        original = Question(
            qid="q2",
            chapter=(3, "Traffic Rules"),
            question="When should you stop at a red light?",
            img_path=SAMPLE_IMG_PATH,
            answers={"Immediately", "After 3 seconds", "Never"},
            correct_answer="Immediately",
            tags=["traffic", "signals"],
            keywords=["red light", "stop"]
        )

        # Dump to dict and load back
        dumped = original.model_dump()
        loaded = Question.model_validate(dumped)

        assert loaded.qid == original.qid
        assert loaded.chapter == original.chapter
        assert loaded.question == original.question
        assert loaded.img_path == original.img_path
        assert loaded.answers == original.answers
        assert loaded.correct_answer == original.correct_answer
        assert loaded.tags == original.tags
        assert loaded.keywords == original.keywords

    def test_json_serialization_minimal(self):
        """Test JSON serialization and deserialization for minimal Question."""
        question = Question(
            qid="q1",
            question="What is the speed limit?",
            answers={"50 km/h", "60 km/h"},
            correct_answer="50 km/h"
        )

        # Serialize to JSON
        json_str = question.model_dump_json()
        assert isinstance(json_str, str)

        # Deserialize from JSON
        data = json.loads(json_str)
        loaded = Question.model_validate(data)

        assert loaded.qid == question.qid
        assert loaded.question == question.question
        assert loaded.answers == question.answers
        assert loaded.correct_answer == question.correct_answer

    def test_json_serialization_full(self):
        """Test JSON serialization and deserialization for full Question."""
        question = Question(
            qid="q2",
            chapter=(3, "Traffic Rules"),
            question="When should you stop at a red light?",
            img_path=SAMPLE_IMG_PATH,
            answers={"Immediately", "After 3 seconds", "Never"},
            correct_answer="Immediately",
            tags=["traffic", "signals"],
            keywords=["red light", "stop"]
        )

        # Serialize to JSON
        json_str = question.model_dump_json()
        assert isinstance(json_str, str)

        # Deserialize from JSON
        data = json.loads(json_str)
        loaded = Question.model_validate(data)

        assert loaded.qid == question.qid
        assert loaded.chapter == question.chapter
        assert loaded.question == question.question
        assert loaded.img_path == question.img_path
        assert loaded.answers == question.answers
        assert loaded.correct_answer == question.correct_answer
        assert loaded.tags == question.tags
        assert loaded.keywords == question.keywords

    def test_model_validate_with_invalid_data(self):
        """Test that model_validate raises ValidationError for invalid data."""
        invalid_data = {
            "qid": "",  # Invalid: empty string
            "question": "What is the speed limit?",
            "answers": ["50 km/h"],  # Invalid: only one answer
            "correct_answer": "50 km/h"
        }

        with pytest.raises(ValidationError) as exc_info:
            Question.model_validate(invalid_data)
        assert "qid" in str(exc_info.value) or "answers" in str(exc_info.value)

    def test_model_dump_exclude_fields(self):
        """Test dumping Question while excluding specific fields."""
        question = Question(
            qid="q1",
            chapter=(3, "Traffic Rules"),
            question="What is the speed limit?",
            img_path=SAMPLE_IMG_PATH,
            answers={"50 km/h", "60 km/h"},
            correct_answer="50 km/h",
            tags=["traffic"],
            keywords=["speed"]
        )

        # Exclude sensitive or unwanted fields
        dumped = question.model_dump(exclude={"img_path", "keywords"})

        assert "img_path" not in dumped
        assert "keywords" not in dumped
        assert "qid" in dumped
        assert "question" in dumped
        assert "tags" in dumped

    def test_model_dump_include_fields(self):
        """Test dumping Question while including only specific fields."""
        question = Question(
            qid="q1",
            question="What is the speed limit?",
            answers={"50 km/h", "60 km/h"},
            correct_answer="50 km/h"
        )

        # Include only essential fields
        dumped = question.model_dump(include={"qid", "question", "correct_answer"})

        assert len(dumped) == 3
        assert dumped["qid"] == "q1"
        assert dumped["question"] == "What is the speed limit?"
        assert dumped["correct_answer"] == "50 km/h"
        assert "answers" not in dumped
        assert "tags" not in dumped

    def test_model_validate_with_extra_fields_ignored(self):
        """Test that model_validate handles unknown fields according to config."""
        data = {
            "qid": "q1",
            "question": "What is the speed limit?",
            "answers": ["50 km/h", "60 km/h"],
            "correct_answer": "50 km/h",
            "unknown_field": "this should be rejected"
        }

        # Should raise ValidationError due to extra='forbid'
        with pytest.raises(ValidationError) as exc_info:
            Question.model_validate(data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_serialization_preserves_data_types(self):
        """Test that serialization preserves complex data types correctly."""
        question = Question(
            qid="q1",
            chapter=(5, "Advanced Rules"),
            question="Complex question with unicode: 测试",
            answers={"答案A", "Answer B", "Réponse C"},
            correct_answer="答案A",
            tags=["unicode", "测试"],
            keywords=["complex", "特殊字符"]
        )

        # Test round-trip preservation
        dumped = question.model_dump()
        loaded = Question.model_validate(dumped)

        # Verify unicode characters are preserved
        assert "测试" in loaded.question
        assert "答案A" in loaded.answers
        assert "测试" in loaded.tags
        assert "特殊字符" in loaded.keywords

        # Verify tuple/list conversion works correctly
        assert isinstance(loaded.chapter, tuple)
        assert loaded.chapter == (5, "Advanced Rules")

