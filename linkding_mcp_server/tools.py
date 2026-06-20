"""MCP tools for LinkDing server"""

import structlog
from fastmcp import FastMCP

from .client import LinkDingClient, LinkDingError
from .config import get_settings
from .models import BookmarkCreate, BookmarkUpdate, SearchParams

# Configure structured logging
logger = structlog.get_logger()


# Security check helper
def check_destructive_actions_enabled(settings) -> str | None:
    """Check if destructive actions are enabled"""
    if not settings.enable_destructive_actions:
        return (
            "Error: Destructive actions are disabled for security. "
            "To enable bookmark modifications, set LINKDING_ENABLE_DESTRUCTIVE_ACTIONS=true "
            "in your environment variables or .env file. "
            "This includes: add, update, delete, archive, and unarchive operations."
        )
    return None


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server with all tools"""
    # Get settings lazily when server is created
    settings = get_settings()

    mcp = FastMCP(
        name="LinkDing MCP Server",
        instructions="""
        This server provides tools for interacting with a LinkDing bookmark manager.
        You can search for bookmarks, add new ones, manage tags, and perform various
        bookmark operations. All operations require a valid LinkDing API token.

        Security Note: Write operations (add, update, delete) are disabled by default.
        Enable them by setting LINKDING_ENABLE_DESTRUCTIVE_ACTIONS=true.
        """,
    )

    @mcp.tool
    async def search_bookmarks(
        query: str | None = None,
        tag: str | None = None,
        limit: int = 100,
        offset: int = 0,
        archived: bool = False,
        unread_only: bool = False,
    ) -> str:
        """
        Search for bookmarks with various filters.

        Args:
            query: Search phrase to filter bookmarks (searches title, description, notes, URL)
            tag: Filter by specific tag name
            limit: Maximum number of results to return (1-1000, default: 100)
            offset: Number of results to skip for pagination (default: 0)
            archived: Search in archived bookmarks instead of active ones
            unread_only: Only return unread bookmarks

        Returns:
            JSON string containing the search results
        """
        log = logger.bind(tool="search_bookmarks", query=query, tag=tag, limit=limit, archived=archived)
        log.info("searching_bookmarks")

        try:
            # Validate parameters
            params = SearchParams(
                query=query, tag=tag, limit=limit, offset=offset, archived=archived, unread_only=unread_only
            )

            async with LinkDingClient(settings) as client:
                # Get bookmarks
                bookmark_list = await client.get_bookmarks(
                    archived=params.archived, q=params.query, limit=params.limit, offset=params.offset
                )

                # Apply additional filters
                filtered_results = bookmark_list.results

                if params.tag:
                    filtered_results = [b for b in filtered_results if params.tag in [t.lower() for t in b.tag_names]]

                if params.unread_only:
                    filtered_results = [b for b in filtered_results if b.unread]

                # Update the results
                bookmark_list.results = filtered_results
                bookmark_list.count = len(filtered_results)

                log.info("search_successful", count=bookmark_list.count)
                return bookmark_list.model_dump_json(indent=2)

        except LinkDingError as e:
            log.error("search_failed", error=str(e))
            return f"Error: {str(e)}"
        except Exception as e:
            log.error("unexpected_error", error=str(e))
            return f"Error searching bookmarks: {str(e)}"

    @mcp.tool
    async def add_bookmark(
        url: str,
        title: str | None = None,
        description: str | None = None,
        notes: str | None = None,
        tags: list[str] | None = None,
        is_archived: bool = False,
        unread: bool = False,
        shared: bool = False,
    ) -> str:
        """
        Add a new bookmark to LinkDing.

        Args:
            url: The URL to bookmark (required)
            title: Custom title for the bookmark (auto-scraped if not provided)
            description: Custom description (auto-scraped if not provided)
            notes: Personal notes for the bookmark
            tags: List of tag names to assign to the bookmark
            is_archived: Whether to save the bookmark directly to archive
            unread: Mark the bookmark as unread
            shared: Make the bookmark shared with other users

        Returns:
            JSON string containing the created bookmark data
        """
        # Security check
        error = check_destructive_actions_enabled(settings)
        if error:
            return error

        log = logger.bind(tool="add_bookmark", url=url, tags=tags)
        log.info("adding_bookmark")

        try:
            # Create validated bookmark
            bookmark = BookmarkCreate(
                url=url,
                title=title,
                description=description,
                notes=notes,
                tags=tags or [],
                is_archived=is_archived,
                unread=unread,
                shared=shared,
            )

            async with LinkDingClient(settings) as client:
                result = await client.create_bookmark(bookmark)
                log.info("bookmark_added", bookmark_id=result.id)
                return result.model_dump_json(indent=2)

        except LinkDingError as e:
            log.error("add_failed", error=str(e))
            return f"Error: {str(e)}"
        except Exception as e:
            log.error("unexpected_error", error=str(e))
            return f"Error adding bookmark: {str(e)}"

    @mcp.tool
    async def get_bookmark(bookmark_id: int) -> str:
        """
        Retrieve a specific bookmark by its ID.

        Args:
            bookmark_id: The ID of the bookmark to retrieve

        Returns:
            JSON string containing the bookmark data
        """
        log = logger.bind(tool="get_bookmark", bookmark_id=bookmark_id)
        log.info("getting_bookmark")

        try:
            async with LinkDingClient(settings) as client:
                bookmark = await client.get_bookmark(bookmark_id)
                log.info("bookmark_retrieved")
                return bookmark.model_dump_json(indent=2)

        except LinkDingError as e:
            log.error("get_failed", error=str(e))
            return f"Error: {str(e)}"
        except Exception as e:
            log.error("unexpected_error", error=str(e))
            return f"Error retrieving bookmark: {str(e)}"

    @mcp.tool
    async def update_bookmark(
        bookmark_id: int,
        url: str | None = None,
        title: str | None = None,
        description: str | None = None,
        notes: str | None = None,
        tags: list[str] | None = None,
        is_archived: bool | None = None,
        unread: bool | None = None,
        shared: bool | None = None,
    ) -> str:
        """
        Update an existing bookmark.

        Args:
            bookmark_id: The ID of the bookmark to update
            url: New URL for the bookmark
            title: New title for the bookmark
            description: New description for the bookmark
            notes: New notes for the bookmark
            tags: New list of tag names (replaces existing tags)
            is_archived: Update archived status
            unread: Update unread status
            shared: Update shared status

        Returns:
            JSON string containing the updated bookmark data
        """
        # Security check
        error = check_destructive_actions_enabled(settings)
        if error:
            return error

        log = logger.bind(tool="update_bookmark", bookmark_id=bookmark_id)
        log.info("updating_bookmark")

        try:
            # Create update model
            update = BookmarkUpdate(
                url=url,
                title=title,
                description=description,
                notes=notes,
                tags=tags,
                is_archived=is_archived,
                unread=unread,
                shared=shared,
            )

            async with LinkDingClient(settings) as client:
                result = await client.update_bookmark(bookmark_id, update)
                log.info("bookmark_updated")
                return result.model_dump_json(indent=2)

        except LinkDingError as e:
            log.error("update_failed", error=str(e))
            return f"Error: {str(e)}"
        except Exception as e:
            log.error("unexpected_error", error=str(e))
            return f"Error updating bookmark: {str(e)}"

    @mcp.tool
    async def delete_bookmark(bookmark_id: int) -> str:
        """
        Delete a bookmark by its ID.

        Args:
            bookmark_id: The ID of the bookmark to delete

        Returns:
            Success or error message
        """
        # Security check
        error = check_destructive_actions_enabled(settings)
        if error:
            return error

        log = logger.bind(tool="delete_bookmark", bookmark_id=bookmark_id)
        log.info("deleting_bookmark")

        try:
            async with LinkDingClient(settings) as client:
                await client.delete_bookmark(bookmark_id)
                log.info("bookmark_deleted")
                return f"Bookmark {bookmark_id} deleted successfully"

        except LinkDingError as e:
            log.error("delete_failed", error=str(e))
            return f"Error: {str(e)}"
        except Exception as e:
            log.error("unexpected_error", error=str(e))
            return f"Error deleting bookmark: {str(e)}"

    @mcp.tool
    async def archive_bookmark(bookmark_id: int) -> str:
        """
        Archive a bookmark by its ID.

        Args:
            bookmark_id: The ID of the bookmark to archive

        Returns:
            Success or error message
        """
        # Security check
        error = check_destructive_actions_enabled(settings)
        if error:
            return error

        log = logger.bind(tool="archive_bookmark", bookmark_id=bookmark_id)
        log.info("archiving_bookmark")

        try:
            async with LinkDingClient(settings) as client:
                await client.archive_bookmark(bookmark_id)
                log.info("bookmark_archived")
                return f"Bookmark {bookmark_id} archived successfully"

        except LinkDingError as e:
            log.error("archive_failed", error=str(e))
            return f"Error: {str(e)}"
        except Exception as e:
            log.error("unexpected_error", error=str(e))
            return f"Error archiving bookmark: {str(e)}"

    @mcp.tool
    async def unarchive_bookmark(bookmark_id: int) -> str:
        """
        Unarchive a bookmark by its ID.

        Args:
            bookmark_id: The ID of the bookmark to unarchive

        Returns:
            Success or error message
        """
        # Security check
        error = check_destructive_actions_enabled(settings)
        if error:
            return error

        log = logger.bind(tool="unarchive_bookmark", bookmark_id=bookmark_id)
        log.info("unarchiving_bookmark")

        try:
            async with LinkDingClient(settings) as client:
                await client.unarchive_bookmark(bookmark_id)
                log.info("bookmark_unarchived")
                return f"Bookmark {bookmark_id} unarchived successfully"

        except LinkDingError as e:
            log.error("unarchive_failed", error=str(e))
            return f"Error: {str(e)}"
        except Exception as e:
            log.error("unexpected_error", error=str(e))
            return f"Error unarchiving bookmark: {str(e)}"

    @mcp.tool
    async def check_url(url: str) -> str:
        """
        Check if a URL is already bookmarked and get metadata.

        Args:
            url: The URL to check

        Returns:
            JSON string containing bookmark status, metadata, and auto-tags
        """
        log = logger.bind(tool="check_url", url=url)
        log.info("checking_url")

        try:
            # Validate URL format
            from pydantic import HttpUrl

            HttpUrl(url)  # This will raise if invalid

            async with LinkDingClient(settings) as client:
                result = await client.check_url(url)
                log.info("url_checked", is_bookmarked=result.bookmark is not None)
                return result.model_dump_json(indent=2)

        except LinkDingError as e:
            log.error("check_failed", error=str(e))
            return f"Error: {str(e)}"
        except Exception as e:
            log.error("unexpected_error", error=str(e))
            return f"Error checking URL: {str(e)}"

    @mcp.tool
    async def list_tags(limit: int = 100, offset: int = 0) -> str:
        """
        List all available tags.

        Args:
            limit: Maximum number of tags to return (1-1000, default: 100)
            offset: Number of tags to skip for pagination (default: 0)

        Returns:
            JSON string containing the list of tags
        """
        log = logger.bind(tool="list_tags", limit=limit, offset=offset)
        log.info("listing_tags")

        try:
            # Validate parameters
            if limit < 1 or limit > 1000:
                return "Error: limit must be between 1 and 1000"
            if offset < 0:
                return "Error: offset must be non-negative"

            async with LinkDingClient(settings) as client:
                tag_list = await client.get_tags(limit=limit, offset=offset)
                log.info("tags_listed", count=tag_list.count)
                return tag_list.model_dump_json(indent=2)

        except LinkDingError as e:
            log.error("list_failed", error=str(e))
            return f"Error: {str(e)}"
        except Exception as e:
            log.error("unexpected_error", error=str(e))
            return f"Error listing tags: {str(e)}"

    @mcp.tool
    async def list_bookmarks_by_tag(tag_name: str, limit: int = 100, offset: int = 0) -> str:
        """
        List bookmarks filtered by a specific tag.

        Args:
            tag_name: Name of the tag to filter by
            limit: Maximum number of bookmarks to return (1-1000, default: 100)
            offset: Number of bookmarks to skip for pagination (default: 0)

        Returns:
            JSON string containing bookmarks with the specified tag
        """
        log = logger.bind(tool="list_bookmarks_by_tag", tag_name=tag_name, limit=limit, offset=offset)
        log.info("listing_bookmarks_by_tag")

        try:
            # Use search_bookmarks with tag filter
            return await search_bookmarks(tag=tag_name, limit=limit, offset=offset)

        except Exception as e:
            log.error("unexpected_error", error=str(e))
            return f"Error listing bookmarks by tag: {str(e)}"

    return mcp
