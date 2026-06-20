"""Tests for data models"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from linkding_mcp_server.models import BookmarkBase, BookmarkCreate, BookmarkUpdate, SearchParams, Tag


class TestBookmarkBase:
    """Tests for BookmarkBase model"""

    def test_valid_bookmark_base(self):
        """Test creating a valid bookmark base"""
        bookmark = BookmarkBase(
            url="https://example.com",
            title="Example",
            description="Test description",
            notes="Test notes",
            tags=["test", "example"],
            is_archived=False,
            unread=True,
            shared=False
        )
        assert str(bookmark.url) == "https://example.com/"
        assert bookmark.title == "Example"
        assert bookmark.tags == ["test", "example"]

    def test_invalid_url(self):
        """Test that invalid URLs are rejected"""
        with pytest.raises(ValidationError) as exc_info:
            BookmarkBase(url="not-a-url")
        assert "URL" in str(exc_info.value)

    def test_tag_validation(self):
        """Test tag name validation"""
        # Valid tags
        bookmark = BookmarkBase(
            url="https://example.com",
            tags=["valid-tag", "another_tag", "tag.with.dots"]
        )
        assert bookmark.tags == ["valid-tag", "another_tag", "tag.with.dots"]

        # Invalid tags
        with pytest.raises(ValidationError) as exc_info:
            BookmarkBase(
                url="https://example.com",
                tags=["invalid tag with spaces"]
            )
        assert "can only contain" in str(exc_info.value)

    def test_tag_normalization(self):
        """Test that tags are normalized to lowercase"""
        bookmark = BookmarkBase(
            url="https://example.com",
            tags=["TestTag", "ANOTHER"]
        )
        assert bookmark.tags == ["testtag", "another"]

    def test_text_field_cleaning(self):
        """Test that text fields are cleaned"""
        bookmark = BookmarkBase(
            url="https://example.com",
            title="  Title  with   spaces  ",
            description="  Description\n\nwith\n\nnewlines  ",
            notes="  Notes  "
        )
        assert bookmark.title == "Title with spaces"
        assert bookmark.description == "Description with newlines"
        assert bookmark.notes == "Notes"

    def test_field_length_limits(self):
        """Test field length validation"""
        # Title too long
        with pytest.raises(ValidationError):
            BookmarkBase(
                url="https://example.com",
                title="x" * 501  # Max is 500
            )

        # Description too long
        with pytest.raises(ValidationError):
            BookmarkBase(
                url="https://example.com",
                description="x" * 2001  # Max is 2000
            )

        # Too many tags
        with pytest.raises(ValidationError):
            BookmarkBase(
                url="https://example.com",
                tags=[f"tag{i}" for i in range(51)]  # Max is 50
            )


class TestBookmarkCreate:
    """Tests for BookmarkCreate model"""

    def test_url_required(self):
        """Test that URL is required for creation"""
        with pytest.raises(ValidationError) as exc_info:
            BookmarkCreate()
        assert "url" in str(exc_info.value).lower()

    def test_empty_url_rejected(self):
        """Test that empty URL is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            BookmarkCreate(url="")
        assert "cannot be empty" in str(exc_info.value)

    def test_valid_creation(self):
        """Test valid bookmark creation"""
        bookmark = BookmarkCreate(
            url="https://example.com",
            title="Example",
            tags=["test"]
        )
        assert str(bookmark.url) == "https://example.com/"
        assert bookmark.title == "Example"
        assert bookmark.tags == ["test"]


class TestBookmarkUpdate:
    """Tests for BookmarkUpdate model"""

    def test_all_fields_optional(self):
        """Test that all fields are optional for updates"""
        update = BookmarkUpdate()
        assert update.url is None
        assert update.title is None
        assert update.tags is None

    def test_partial_update(self):
        """Test partial update with only some fields"""
        update = BookmarkUpdate(
            title="New Title",
            tags=["updated"]
        )
        assert update.title == "New Title"
        assert update.tags == ["updated"]
        assert update.url is None

    def test_tag_validation_in_update(self):
        """Test tag validation in updates"""
        update = BookmarkUpdate(tags=["Valid", "Tags"])
        assert update.tags == ["valid", "tags"]

        with pytest.raises(ValidationError):
            BookmarkUpdate(tags=["invalid tag with spaces"])


class TestSearchParams:
    """Tests for SearchParams model"""

    def test_default_values(self):
        """Test default search parameter values"""
        params = SearchParams()
        assert params.query is None
        assert params.tag is None
        assert params.limit == 100
        assert params.offset == 0
        assert params.archived is False
        assert params.unread_only is False

    def test_limit_validation(self):
        """Test limit parameter validation"""
        # Valid limits
        params = SearchParams(limit=1)
        assert params.limit == 1

        params = SearchParams(limit=1000)
        assert params.limit == 1000

        # Invalid limits
        with pytest.raises(ValidationError):
            SearchParams(limit=0)

        with pytest.raises(ValidationError):
            SearchParams(limit=1001)

    def test_offset_validation(self):
        """Test offset parameter validation"""
        # Valid offset
        params = SearchParams(offset=100)
        assert params.offset == 100

        # Invalid offset
        with pytest.raises(ValidationError):
            SearchParams(offset=-1)

    def test_tag_normalization(self):
        """Test that search tags are normalized"""
        params = SearchParams(tag="TestTag")
        assert params.tag == "testtag"

    def test_query_length_limit(self):
        """Test query length limit"""
        # Valid query
        params = SearchParams(query="test search")
        assert params.query == "test search"

        # Query too long
        with pytest.raises(ValidationError):
            SearchParams(query="x" * 501)  # Max is 500


class TestTag:
    """Tests for Tag model"""

    def test_valid_tag(self):
        """Test creating a valid tag"""
        tag = Tag(
            id=1,
            name="test-tag",
            date_added=datetime.now()
        )
        assert tag.id == 1
        assert tag.name == "test-tag"

    def test_tag_name_normalization(self):
        """Test that tag names are normalized"""
        tag = Tag(
            id=1,
            name="TestTag",
            date_added=datetime.now()
        )
        assert tag.name == "testtag"

    def test_empty_tag_name_rejected(self):
        """Test that empty tag names are rejected"""
        with pytest.raises(ValidationError):
            Tag(
                id=1,
                name="",
                date_added=datetime.now()
            )