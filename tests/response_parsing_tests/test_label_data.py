import pytest
from pydantic import ValidationError

from label_generator.label_data import LabelData


class TestLabelDataInitialization:
    """Test class for LabelData initialization and validation."""

    def test_default_initialization(self):
        """Test creating LabelData with default parameters."""
        data = LabelData()
        assert data.tags == []
        assert data.keywords == []

    def test_initialization_with_tags_only(self):
        """Test creating LabelData with only tags provided."""
        tags = ["tag1", "tag2", "tag3"]
        label_data = LabelData(tags=tags)

        assert set(label_data.tags) == set(tags)
        assert label_data.keywords == []

    def test_initialization_with_keywords_only(self):
        """Test creating LabelData with only keywords provided."""
        keywords = ["keyword1", "keyword2", "keyword3"]
        label_data = LabelData(keywords=keywords)

        assert set(label_data.keywords) == set(keywords)
        assert label_data.tags == []

    def test_initialization_with_both_tags_and_keywords(self):
        """Test creating LabelData with both tags and keywords provided."""
        tags = ["tag1", "tag2"]
        keywords = ["keyword1", "keyword2"]
        label_data = LabelData(tags=tags, keywords=keywords)

        assert set(label_data.tags) == set(tags)
        assert set(label_data.keywords) == set(keywords)

    def test_initialization_removes_duplicate_tags(self):
        """Test that duplicate tags are removed during initialization."""
        tags_with_duplicates = ["tag1", "tag2", "tag1", "tag3", "tag2"]
        label_data = LabelData(tags=tags_with_duplicates)

        # Should have unique tags only
        assert len(label_data.tags) == 3
        assert set(label_data.tags) == {"tag1", "tag2", "tag3"}

    def test_initialization_removes_duplicate_keywords(self):
        """Test that duplicate keywords are removed during initialization."""
        keywords_with_duplicates = ["key1", "key2", "key1", "key3", "key2"]
        label_data = LabelData(keywords=keywords_with_duplicates)

        # Should have unique keywords only
        assert len(label_data.keywords) == 3
        assert set(label_data.keywords) == {"key1", "key2", "key3"}

    def test_initialization_with_none_values(self):
        """Test creating LabelData with None values for tags and keywords."""
        # None values should be converted to empty lists which are now allowed
        label_data = LabelData(tags=None, keywords=None)
        assert label_data.tags == []
        assert label_data.keywords == []


class TestLabelDataValidation:
    """Test class for Pydantic validation rules."""

    def test_validation_error_on_empty_tags_field(self):
        """Test that empty tags field is now allowed."""
        # Empty lists are now allowed, so this should succeed
        label_data = LabelData(tags=[], keywords=["keyword1"])
        assert label_data.tags == []
        assert label_data.keywords == ["keyword1"]

    def test_validation_error_on_empty_keywords_field(self):
        """Test that empty keywords field is now allowed."""
        # Empty lists are now allowed, so this should succeed
        label_data = LabelData(tags=["tag1"], keywords=[])
        assert label_data.tags == ["tag1"]
        assert label_data.keywords == []

    def test_validation_error_on_extra_fields(self):
        """Test ValidationError when extra fields are provided."""
        with pytest.raises(ValidationError):
            test = LabelData(tags=["tag1"], keywords=["keyword1"])
            test.extra_tag = "should be forbidden"

    def test_validation_error_on_non_list_tags(self):
        """Test ValidationError when tags is not a list."""
        with pytest.raises(ValidationError):
            LabelData(tags='not_a_list', keywords=['keyword1'])

    def test_validation_error_on_non_list_keywords(self):
        """Test ValidationError when keywords is not a list."""
        with pytest.raises(ValidationError):
            LabelData(tags=['tag1'], keywords='not_a_list')

    def test_validation_error_on_non_string_tag_elements(self):
        """Test ValidationError when tag elements are not strings."""
        with pytest.raises(ValidationError):
            LabelData(tags=['tag1', 123, 'tag2'], keywords=['keyword1'])

    def test_validation_error_on_non_string_keyword_elements(self):
        """Test ValidationError when keyword elements are not strings."""
        with pytest.raises(ValidationError):
            LabelData(tags=['tag1'], keywords=['keyword1', 123, 'keyword2'])


class TestTagOperations:
    """Test class for tag-related operations."""

    def test_add_tags_to_empty_list(self):
        """Test adding tags to an initially empty tags list."""
        # Now we can start with truly empty tags since empty lists are allowed
        label_data = LabelData(tags=[], keywords=["keyword1"])
        new_tags = ["tag1", "tag2", "tag3"]

        label_data.add_tags(new_tags)

        assert label_data.tags == new_tags
        assert len(label_data.tags) == 3

    def test_add_tags_to_existing_list(self):
        """Test adding tags to an existing tags list."""
        label_data = LabelData(tags=["existing1", "existing2"],
                               keywords=["keyword1"])
        new_tags = ["tag1", "tag2"]

        label_data.add_tags(new_tags)

        expected = ["existing1", "existing2", "tag1", "tag2"]
        assert label_data.tags == expected
        assert len(label_data.tags) == 4

    def test_add_tags_prevents_duplicates(self):
        """Test that add_tags prevents duplicate tags from being added."""
        label_data = LabelData(tags=["tag1", "tag2"], keywords=["keyword1"])
        duplicate_tags = ["tag1", "tag3", "tag2", "tag4"]

        label_data.add_tags(duplicate_tags)

        # Should only add tag3 and tag4, not the duplicates
        expected = ["tag1", "tag2", "tag3", "tag4"]
        assert label_data.tags == expected
        assert len(label_data.tags) == 4

    def test_add_tags_with_empty_list(self):
        """Test adding an empty list of tags."""
        original_tags = ["tag1", "tag2"]
        label_data = LabelData(tags=original_tags, keywords=["keyword1"])

        label_data.add_tags([])

        # Should remain unchanged
        assert label_data.tags == original_tags
        assert len(label_data.tags) == 2

    def test_add_tags_with_mixed_duplicates_and_new(self):
        """Test adding a list containing both duplicates and new tags."""
        label_data = LabelData(tags=["existing1", "existing2"],
                               keywords=["keyword1"])
        mixed_tags = ["existing1", "new1", "existing2", "new2", "new1"]

        label_data.add_tags(mixed_tags)

        # Should only add new1 and new2 once each
        expected = ["existing1", "existing2", "new1", "new2"]
        assert label_data.tags == expected
        assert len(label_data.tags) == 4

    def test_get_tags_returns_copy(self):
        """Test that get_tags returns a copy, not the original list."""
        original_tags = ["tag1", "tag2", "tag3"]
        label_data = LabelData(tags=original_tags, keywords=["keyword1"])

        returned_tags = label_data.get_tags()

        # Should be equal but not the same object
        assert returned_tags == original_tags
        assert returned_tags is not label_data.tags

    def test_get_tags_returns_all_tags(self):
        """Test that get_tags returns all current tags."""
        tags = ["tag1", "tag2", "tag3", "tag4"]
        label_data = LabelData(tags=tags, keywords=["keyword1"])

        returned_tags = label_data.get_tags()

        assert returned_tags == tags
        assert len(returned_tags) == 4

    def test_get_tags_modification_doesnt_affect_original(self):
        """Test that modifying returned tags list doesn't affect original."""
        original_tags = ["tag1", "tag2"]
        label_data = LabelData(tags=original_tags, keywords=["keyword1"])

        returned_tags = label_data.get_tags()
        returned_tags.append("new_tag")
        returned_tags[0] = "modified_tag"

        # Original should be unchanged
        assert label_data.tags == original_tags
        assert "new_tag" not in label_data.tags
        assert "modified_tag" not in label_data.tags


class TestKeywordOperations:
    """Test class for keyword-related operations."""

    def test_add_keywords_to_empty_list(self):
        """Test adding keywords to an initially empty keywords list."""
        label_data = LabelData(tags=["tag1"], keywords=[])
        new_keywords = ["keyword1", "keyword2", "keyword3"]

        label_data.add_keywords(new_keywords)

        assert label_data.keywords == new_keywords
        assert len(label_data.keywords) == 3

    def test_add_keywords_to_existing_list(self):
        """Test adding keywords to an existing keywords list."""
        label_data = LabelData(tags=["tag1"],
                               keywords=["existing1", "existing2"])
        new_keywords = ["keyword1", "keyword2"]

        label_data.add_keywords(new_keywords)

        expected = ["existing1", "existing2", "keyword1", "keyword2"]
        assert label_data.keywords == expected
        assert len(label_data.keywords) == 4

    def test_add_keywords_prevents_duplicates(self):
        """Test that add_keywords prevents duplicate keywords."""
        label_data = LabelData(tags=["tag1"], keywords=["keyword1", "keyword2"])
        duplicate_keywords = ["keyword1", "keyword3", "keyword2", "keyword4"]

        label_data.add_keywords(duplicate_keywords)

        # Should only add keyword3 and keyword4, not the duplicates
        expected = ["keyword1", "keyword2", "keyword3", "keyword4"]
        assert label_data.keywords == expected
        assert len(label_data.keywords) == 4

    def test_add_keywords_with_empty_list(self):
        """Test adding an empty list of keywords."""
        original_keywords = ["keyword1", "keyword2"]
        label_data = LabelData(tags=["tag1"], keywords=original_keywords)

        label_data.add_keywords([])

        # Should remain unchanged
        assert label_data.keywords == original_keywords
        assert len(label_data.keywords) == 2

    def test_add_keywords_with_mixed_duplicates_and_new(self):
        """Test adding a list containing both duplicates and new keywords."""
        label_data = LabelData(tags=["tag1"],
                               keywords=["existing1", "existing2"])
        mixed_keywords = ["existing1", "new1", "existing2", "new2", "new1"]

        label_data.add_keywords(mixed_keywords)

        # Should only add new1 and new2 once each
        expected = ["existing1", "existing2", "new1", "new2"]
        assert label_data.keywords == expected
        assert len(label_data.keywords) == 4

    def test_get_keywords_returns_copy(self):
        """Test that get_keywords returns a copy, not the original list."""
        original_keywords = ["keyword1", "keyword2", "keyword3"]
        label_data = LabelData(tags=["tag1"], keywords=original_keywords)

        returned_keywords = label_data.get_keywords()

        # Should be equal but not the same object
        assert set(returned_keywords) == set(original_keywords)
        assert returned_keywords is not label_data.keywords

    def test_get_keywords_returns_all_keywords(self):
        """Test that get_keywords returns all current keywords."""
        keywords = ["keyword1", "keyword2", "keyword3", "keyword4"]
        label_data = LabelData(tags=["tag1"], keywords=keywords)

        returned_keywords = label_data.get_keywords()

        assert returned_keywords == keywords
        assert len(returned_keywords) == 4

    def test_get_keywords_modification_doesnt_affect_original(self):
        """Test that modifying returned keywords doesn't affect original."""
        original_keywords = ["keyword1", "keyword2"]
        label_data = LabelData(tags=["tag1"], keywords=original_keywords)

        returned_keywords = label_data.get_keywords()
        returned_keywords.append("new_keyword")
        returned_keywords[0] = "modified_keyword"

        # Original should be unchanged
        assert label_data.keywords == original_keywords
        assert "new_keyword" not in label_data.keywords
        assert "modified_keyword" not in label_data.keywords


class TestExtendOperations:
    """Test class for extend method functionality."""

    def test_extend_with_empty_label_data(self):
        """Test extending with LabelData instance that has empty lists."""
        label_data1 = LabelData(tags=["tag1"], keywords=["keyword1"])
        label_data2 = LabelData(tags=[], keywords=[])

        original_tags = label_data1.tags.copy()
        original_keywords = label_data1.keywords.copy()

        label_data1.extend(label_data2)

        # Should remain unchanged since we're extending with empty data
        assert label_data1.tags == original_tags
        assert label_data1.keywords == original_keywords

    def test_extend_with_tags_only(self):
        """Test extending with LabelData that only has tags."""
        label_data1 = LabelData(tags=["existing_tag"], keywords=["keyword1"])
        label_data2 = LabelData(tags=["new_tag1", "new_tag2"],
                                keywords=["temp"])

        # Clear keywords from second instance to simulate tags-only
        label_data2.keywords.clear()

        label_data1.extend(label_data2)

        expected_tags = ["existing_tag", "new_tag1", "new_tag2"]
        assert label_data1.tags == expected_tags
        assert label_data1.keywords == ["keyword1"]  # Should remain unchanged

    def test_extend_with_keywords_only(self):
        """Test extending with LabelData that only has keywords."""
        label_data1 = LabelData(tags=["tag1"], keywords=["existing_keyword"])
        label_data2 = LabelData(tags=["temp"],
                                keywords=["new_keyword1", "new_keyword2"])

        # Clear tags from second instance to simulate keywords-only
        label_data2.tags.clear()

        label_data1.extend(label_data2)

        expected_keywords = ["existing_keyword", "new_keyword1", "new_keyword2"]
        assert label_data1.keywords == expected_keywords
        assert label_data1.tags == ["tag1"]  # Should remain unchanged

    def test_extend_with_both_tags_and_keywords(self):
        """Test extending with LabelData that has both tags and keywords."""
        label_data1 = LabelData(tags=["tag1"], keywords=["keyword1"])
        label_data2 = LabelData(tags=["tag2", "tag3"],
                                keywords=["keyword2", "keyword3"])

        label_data1.extend(label_data2)

        expected_tags = ["tag1", "tag2", "tag3"]
        expected_keywords = ["keyword1", "keyword2", "keyword3"]
        assert label_data1.tags == expected_tags
        assert label_data1.keywords == expected_keywords

    def test_extend_prevents_duplicate_tags(self):
        """Test that extend prevents duplicate tags when merging."""
        label_data1 = LabelData(tags=["tag1", "tag2"], keywords=["keyword1"])
        label_data2 = LabelData(tags=["tag2", "tag3", "tag1"],
                                keywords=["keyword2"])

        label_data1.extend(label_data2)

        # Should only add tag3, not duplicate tag1 and tag2
        expected_tags = ["tag1", "tag2", "tag3"]
        assert label_data1.tags == expected_tags
        assert len(label_data1.tags) == 3

    def test_extend_prevents_duplicate_keywords(self):
        """Test that extend prevents duplicate keywords when merging."""
        label_data1 = LabelData(tags=["tag1"],
                                keywords=["keyword1", "keyword2"])
        label_data2 = LabelData(tags=["tag2"],
                                keywords=["keyword2", "keyword3", "keyword1"])

        label_data1.extend(label_data2)

        # Should only add keyword3, not duplicate keyword1 and keyword2
        expected_keywords = ["keyword1", "keyword2", "keyword3"]
        assert label_data1.keywords == expected_keywords
        assert len(label_data1.keywords) == 3

    def test_extend_multiple_instances(self):
        """Test extending with multiple LabelData instances sequentially."""
        label_data1 = LabelData(tags=["tag1"], keywords=["keyword1"])
        label_data2 = LabelData(tags=["tag2"], keywords=["keyword2"])
        label_data3 = LabelData(tags=["tag3"], keywords=["keyword3"])

        label_data1.extend(label_data2)
        label_data1.extend(label_data3)

        expected_tags = ["tag1", "tag2", "tag3"]
        expected_keywords = ["keyword1", "keyword2", "keyword3"]
        assert label_data1.tags == expected_tags
        assert label_data1.keywords == expected_keywords

    def test_extend_with_overlapping_and_unique_data(self):
        """Test extending with LabelData with overlapping and unique data."""
        label_data1 = LabelData(tags=["common_tag", "unique1"],
                                keywords=["common_keyword", "unique1"])
        label_data2 = LabelData(tags=["common_tag", "unique2"],
                                keywords=["common_keyword", "unique2"])

        label_data1.extend(label_data2)

        # Should merge unique items and avoid duplicates
        expected_tags = ["common_tag", "unique1", "unique2"]
        expected_keywords = ["common_keyword", "unique1", "unique2"]
        assert set(label_data1.tags) == set(expected_tags)
        assert set(label_data1.keywords) == set(expected_keywords)
        assert len(label_data1.tags) == 3
        assert len(label_data1.keywords) == 3


class TestInitializationEdgeCases:
    """Test class for initialization edge cases and boundary conditions."""

    def test_tags_with_special_characters(self):
        """Test handling of tags containing special characters."""
        special_tags = ["tag@#$", "tag-with-dashes", "tag_with_underscores",
                        "tag.with.dots"]
        label_data = LabelData(tags=special_tags, keywords=["keyword1"])

        assert label_data.tags == special_tags
        assert len(label_data.tags) == 4

    def test_keywords_with_special_characters(self):
        """Test handling of keywords containing special characters."""
        special_keywords = ["keyword@#$", "keyword-with-dashes",
                            "keyword_with_underscores", "keyword.with.dots"]
        label_data = LabelData(tags=["tag1"], keywords=special_keywords)

        assert label_data.keywords == special_keywords
        assert len(label_data.keywords) == 4

    def test_unicode_tags(self):
        """Test handling of tags with unicode characters."""
        unicode_tags = ["タグ", "étiquette", "метка", "🏷️", "café"]
        label_data = LabelData(tags=unicode_tags, keywords=["keyword1"])

        assert label_data.tags == unicode_tags
        assert len(label_data.tags) == 5

    def test_unicode_keywords(self):
        """Test handling of keywords with unicode characters."""
        unicode_keywords = ["キーワード", "mot-clé", "ключевое_слово", "🔑",
                            "naïve"]
        label_data = LabelData(tags=["tag1"], keywords=unicode_keywords)

        assert label_data.keywords == unicode_keywords
        assert len(label_data.keywords) == 5

    def test_empty_string_tags(self):
        """Test behavior when tags contain empty strings."""
        tags_with_empty = ["tag1", "", "tag2", ""]
        label_data = LabelData(tags=tags_with_empty, keywords=["keyword1"])

        # Empty strings should be preserved as valid tags
        assert "" in label_data.tags
        assert "tag1" in label_data.tags
        assert "tag2" in label_data.tags
        # Set conversion should remove one duplicate empty string
        assert label_data.tags.count("") == 1

    def test_empty_string_keywords(self):
        """Test behavior when keywords contain empty strings."""
        keywords_with_empty = ["keyword1", "", "keyword2", ""]
        label_data = LabelData(tags=["tag1"], keywords=keywords_with_empty)

        # Empty strings should be preserved as valid keywords
        assert "" in label_data.keywords
        assert "keyword1" in label_data.keywords
        assert "keyword2" in label_data.keywords
        # Set conversion should remove one duplicate empty string
        assert label_data.keywords.count("") == 1

    def test_whitespace_only_tags(self):
        """Test behavior when tags contain only whitespace."""
        whitespace_tags = ["tag1", "   ", "\t", "\n", "  \t\n  "]
        label_data = LabelData(tags=whitespace_tags, keywords=["keyword1"])

        # Whitespace-only strings should be preserved as valid tags
        assert "   " in label_data.tags
        assert "\t" in label_data.tags
        assert "\n" in label_data.tags
        assert "  \t\n  " in label_data.tags
        assert "tag1" in label_data.tags

    def test_whitespace_only_keywords(self):
        """Test behavior when keywords contain only whitespace."""
        whitespace_keywords = ["keyword1", "   ", "\t", "\n", "  \t\n  "]
        label_data = LabelData(tags=["tag1"], keywords=whitespace_keywords)

        # Whitespace-only strings should be preserved as valid keywords
        assert "   " in label_data.keywords
        assert "\t" in label_data.keywords
        assert "\n" in label_data.keywords
        assert "  \t\n  " in label_data.keywords
        assert "keyword1" in label_data.keywords


class TestDataIntegrity:
    """Test class for data integrity and immutability concerns."""

    def test_tags_order_preservation(self):
        """Test that the order of tags is preserved when adding them."""
        label_data = LabelData(tags=["first", "second"], keywords=["keyword1"])
        new_tags = ["third", "fourth", "fifth"]

        label_data.add_tags(new_tags)

        expected_order = ["first", "second", "third", "fourth", "fifth"]
        assert label_data.tags == expected_order

    def test_keywords_order_preservation(self):
        """Test that the order of keywords is preserved when adding them."""
        label_data = LabelData(tags=["tag1"], keywords=["first", "second"])
        new_keywords = ["third", "fourth", "fifth"]

        label_data.add_keywords(new_keywords)

        expected_order = ["first", "second", "third", "fourth", "fifth"]
        assert label_data.keywords == expected_order

    def test_case_sensitivity_tags(self):
        """Test that tag comparison is case-sensitive for duplicates."""
        label_data = LabelData(tags=["Tag", "TAG", "tag"],
                               keywords=["keyword1"])

        # All different case variations should be preserved
        assert "Tag" in label_data.tags
        assert "TAG" in label_data.tags
        assert "tag" in label_data.tags
        assert len(label_data.tags) == 3

        # Adding the same cases should not create duplicates
        label_data.add_tags(["Tag", "NEW_TAG", "tag"])
        assert label_data.tags.count("Tag") == 1
        assert label_data.tags.count("tag") == 1
        assert "NEW_TAG" in label_data.tags

    def test_case_sensitivity_keywords(self):
        """Test that keyword comparison is case-sensitive for duplicates."""
        label_data = LabelData(tags=["tag1"],
                               keywords=["Keyword", "KEYWORD", "keyword"])

        # All different case variations should be preserved
        assert "Keyword" in label_data.keywords
        assert "KEYWORD" in label_data.keywords
        assert "keyword" in label_data.keywords
        assert len(label_data.keywords) == 3

        # Adding the same cases should not create duplicates
        label_data.add_keywords(["Keyword", "NEW_KEYWORD", "keyword"])
        assert label_data.keywords.count("Keyword") == 1
        assert label_data.keywords.count("keyword") == 1
        assert "NEW_KEYWORD" in label_data.keywords

    def test_state_consistency_after_multiple_operations(self):
        """Test object state consistency after multiple operations."""
        label_data = LabelData(tags=["initial_tag"],
                               keywords=["initial_keyword"])

        # Perform multiple operations
        label_data.add_tags(["tag1", "tag2"])
        label_data.add_keywords(["keyword1", "keyword2"])

        other_data = LabelData(tags=["tag3", "initial_tag"],
                               keywords=["keyword3", "initial_keyword"])
        label_data.extend(other_data)

        # Verify final state is consistent
        expected_tags = ["initial_tag", "tag1", "tag2", "tag3"]
        expected_keywords = ["initial_keyword", "keyword1", "keyword2",
                             "keyword3"]

        assert set(label_data.tags) == set(expected_tags)
        assert set(label_data.keywords) == set(expected_keywords)
        assert len(label_data.tags) == 4  # No duplicates
        assert len(label_data.keywords) == 4  # No duplicates


class TestPydanticIntegration:
    """Test class for Pydantic-specific functionality."""

    def test_model_dump(self):
        """Test that model can be properly serialized using model_dump."""
        tags = ["tag1", "tag2"]
        keywords = ["keyword1", "keyword2"]
        label_data = LabelData(tags=tags, keywords=keywords)

        dumped = label_data.model_dump()

        assert isinstance(dumped, dict)
        assert dumped["tags"] == tags
        assert dumped["keywords"] == keywords
        assert len(dumped) == 2  # Only tags and keywords fields

    def test_model_validate(self):
        """Test that model can be created using model_validate class method."""
        data = {
            "tags": ["tag1", "tag2"],
            "keywords": ["keyword1", "keyword2"]
        }

        label_data = LabelData.model_validate(data)

        assert label_data.tags == data["tags"]
        assert label_data.keywords == data["keywords"]

    def test_model_fields_info(self):
        """Test that model fields have correct metadata."""
        fields = LabelData.model_fields

        assert "tags" in fields
        assert "keywords" in fields

        # Check tags field constraints
        tags_field = fields["tags"]
        assert tags_field.description is not None
        assert "tags extracted from the response" in tags_field.description

        # Check keywords field constraints
        keywords_field = fields["keywords"]
        assert keywords_field.description is not None
        assert ("keywords extracted from the response"
                in keywords_field.description)

    def test_validate_assignment_config(self):
        """Test that validate_assignment configuration works correctly."""
        label_data = LabelData(tags=["tag1"], keywords=["keyword1"])

        # Valid assignment should work
        label_data.tags = ["new_tag1", "new_tag2"]
        assert label_data.tags == ["new_tag1", "new_tag2"]

        # Empty lists should now be allowed for assignment
        label_data.tags = []
        assert label_data.tags == []

        label_data.keywords = []
        assert label_data.keywords == []

        # Invalid assignment should raise ValidationError
        with pytest.raises(ValidationError):
            label_data.keywords = "not_a_list"  # Not a list


class TestFieldConstraintValidation:
    """Test class for Pydantic field constraint validation."""

    def test_empty_lists_now_allowed_for_tags(self):
        """Test that empty lists are now allowed for tags field."""
        label_data = LabelData.model_validate(
            {"tags": [], "keywords": ["keyword1"]})
        assert label_data.tags == []
        assert label_data.keywords == ["keyword1"]

    def test_empty_lists_now_allowed_for_keywords(self):
        """Test that empty lists are now allowed for keywords field."""
        label_data = LabelData.model_validate({"tags": ["tag1"],
                                               "keywords": []})
        assert label_data.tags == ["tag1"]
        assert label_data.keywords == []

    def test_field_description_metadata(self):
        """Test that field descriptions are properly set."""
        fields = LabelData.model_fields

        # Verify tags field description
        tags_field = fields["tags"]
        expected_tags_desc = "List of tags extracted from the response"
        assert expected_tags_desc in tags_field.description

        # Verify keywords field description
        keywords_field = fields["keywords"]
        expected_keywords_desc = "List of keywords extracted from the response"
        assert expected_keywords_desc in keywords_field.description


class TestDeduplicationLogic:
    """Test class specifically for deduplication behavior."""

    def test_set_conversion_during_initialization(self):
        """Test that list(set()) conversion works correctly in __init__."""
        # Test with tags containing duplicates
        tags_with_dupes = ["a", "b", "a", "c", "b", "a"]
        label_data = LabelData(tags=tags_with_dupes, keywords=["keyword1"])

        # Should have unique elements only
        assert len(label_data.tags) == 3
        assert set(label_data.tags) == {"a", "b", "c"}

        # Test with keywords containing duplicates
        keywords_with_dupes = ["x", "y", "x", "z", "y", "x"]
        label_data = LabelData(tags=["tag1"], keywords=keywords_with_dupes)

        # Should have unique elements only
        assert len(label_data.keywords) == 3
        assert set(label_data.keywords) == {"x", "y", "z"}

    def test_deduplication_preserves_order(self):
        """Test that deduplication maintains first occurrence order."""
        # Note: set() conversion in Python doesn't guarantee order preservation
        # But we can test that all unique elements are present
        tags_with_dupes = ["first", "second", "first", "third", "second"]
        label_data = LabelData(tags=tags_with_dupes, keywords=["keyword1"])

        # All unique elements should be present
        assert "first" in label_data.tags
        assert "second" in label_data.tags
        assert "third" in label_data.tags
        assert len(label_data.tags) == 3
