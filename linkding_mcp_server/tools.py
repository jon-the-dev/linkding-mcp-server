"""MCP server factory — registers all LinkDing tools with FastMCP.

Cyclomatic complexity here is intentionally high; issue #2 will extract
individual tools into separate modules.
"""

from typing import List, Optional

import httpx
from fastmcp import FastMCP

from linkding_mcp_server.client import LinkDingClient, handle_api_error
from linkding_mcp_server.config import Settings
from linkding_mcp_server.models import Bookmark, BookmarkCheck, BookmarkList, TagList


def create_mcp_server(settings: Settings) -> FastMCP:
    """Build and return a configured FastMCP instance with all tools registered.

    Args:
        settings: Runtime configuration for the LinkDing connection.

    Returns:
        A FastMCP server with all 11 bookmark tools registered.
    """
    client = LinkDingClient(settings)

    mcp = FastMCP(
        name="LinkDing MCP Server",
        instructions="""
        This server provides tools for interacting with a LinkDing bookmark manager.
        You can search for bookmarks, add new ones, manage tags, and perform various
        bookmark operations. All operations require a valid LinkDing API token.
        """,
    )

    def check_destructive_actions_enabled() -> str:
        """Return an error string if destructive actions are disabled, else empty string."""
        if not settings.enable_destructive_actions:
            return (
                "Error: Destructive actions are disabled for security. "
                "To enable bookmark modifications, set LINKDING_ENABLE_DESTRUCTIVE_ACTIONS=true "
                "in your environment variables or .env file. "
                "This includes: add, update, delete, archive, and unarchive operations."
            )
        return ""

    @mcp.tool
    async def search_bookmarks(
        query: Optional[str] = None,
        tag: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        archived: bool = False,
        unread_only: bool = False,
    ) -> str:
        """Search for bookmarks with various filters.

        Args:
            query: Search phrase to filter bookmarks (searches title, description, notes, URL)
            tag: Filter by specific tag name
            limit: Maximum number of results to return (default: 100)
            offset: Number of results to skip for pagination (default: 0)
            archived: Search in archived bookmarks instead of active ones
            unread_only: Only return unread bookmarks

        Returns:
            JSON string containing the search results
        """
        try:
            params = {"limit": limit, "offset": offset}
            if query:
                params["q"] = query

            endpoint = "/bookmarks/archived/" if archived else "/bookmarks/"
            response = await client.get(endpoint, params=params)

            if response.status_code != 200:
                return await handle_api_error(response)

            data = response.json()
            bookmark_list = BookmarkList(**data)

            filtered_results = bookmark_list.results
            if tag:
                filtered_results = [b for b in filtered_results if tag in b.tag_names]
            if unread_only:
                filtered_results = [b for b in filtered_results if b.unread]

            bookmark_list.results = filtered_results
            bookmark_list.count = len(filtered_results)

            return bookmark_list.model_dump_json(indent=2)

        except httpx.RequestError as e:
            return f"Connection error: {str(e)}"
        except Exception as e:
            return f"Error searching bookmarks: {str(e)}"

    @mcp.tool
    async def add_bookmark(
        url: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        notes: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_archived: bool = False,
        unread: bool = False,
        shared: bool = False,
    ) -> str:
        """Add a new bookmark to LinkDing.

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
        security_error = check_destructive_actions_enabled()
        if security_error:
            return security_error

        try:
            payload = {"url": url, "is_archived": is_archived, "unread": unread, "shared": shared}
            if title:
                payload["title"] = title
            if description:
                payload["description"] = description
            if notes:
                payload["notes"] = notes
            if tags:
                payload["tag_names"] = tags

            response = await client.post("/bookmarks/", json=payload)

            if response.status_code not in [200, 201]:
                return await handle_api_error(response)

            bookmark = Bookmark(**response.json())
            return bookmark.model_dump_json(indent=2)

        except httpx.RequestError as e:
            return f"Connection error: {str(e)}"
        except Exception as e:
            return f"Error adding bookmark: {str(e)}"

    @mcp.tool
    async def get_bookmark(bookmark_id: int) -> str:
        """Retrieve a specific bookmark by its ID.

        Args:
            bookmark_id: The ID of the bookmark to retrieve

        Returns:
            JSON string containing the bookmark data
        """
        try:
            response = await client.get(f"/bookmarks/{bookmark_id}/")

            if response.status_code == 404:
                return f"Bookmark with ID {bookmark_id} not found"
            elif response.status_code != 200:
                return await handle_api_error(response)

            bookmark = Bookmark(**response.json())
            return bookmark.model_dump_json(indent=2)

        except httpx.RequestError as e:
            return f"Connection error: {str(e)}"
        except Exception as e:
            return f"Error retrieving bookmark: {str(e)}"

    @mcp.tool
    async def update_bookmark(
        bookmark_id: int,
        url: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        notes: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_archived: Optional[bool] = None,
        unread: Optional[bool] = None,
        shared: Optional[bool] = None,
    ) -> str:
        """Update an existing bookmark.

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
        security_error = check_destructive_actions_enabled()
        if security_error:
            return security_error

        try:
            payload = {}
            if url is not None:
                payload["url"] = url
            if title is not None:
                payload["title"] = title
            if description is not None:
                payload["description"] = description
            if notes is not None:
                payload["notes"] = notes
            if tags is not None:
                payload["tag_names"] = tags
            if is_archived is not None:
                payload["is_archived"] = is_archived
            if unread is not None:
                payload["unread"] = unread
            if shared is not None:
                payload["shared"] = shared

            if not payload:
                return "No fields provided to update"

            response = await client.patch(f"/bookmarks/{bookmark_id}/", json=payload)

            if response.status_code == 404:
                return f"Bookmark with ID {bookmark_id} not found"
            elif response.status_code != 200:
                return await handle_api_error(response)

            bookmark = Bookmark(**response.json())
            return bookmark.model_dump_json(indent=2)

        except httpx.RequestError as e:
            return f"Connection error: {str(e)}"
        except Exception as e:
            return f"Error updating bookmark: {str(e)}"

    @mcp.tool
    async def delete_bookmark(bookmark_id: int) -> str:
        """Delete a bookmark by its ID.

        Args:
            bookmark_id: The ID of the bookmark to delete

        Returns:
            Success or error message
        """
        security_error = check_destructive_actions_enabled()
        if security_error:
            return security_error

        try:
            response = await client.delete(f"/bookmarks/{bookmark_id}/")

            if response.status_code == 404:
                return f"Bookmark with ID {bookmark_id} not found"
            elif response.status_code != 204:
                return await handle_api_error(response)

            return f"Bookmark {bookmark_id} deleted successfully"

        except httpx.RequestError as e:
            return f"Connection error: {str(e)}"
        except Exception as e:
            return f"Error deleting bookmark: {str(e)}"

    @mcp.tool
    async def archive_bookmark(bookmark_id: int) -> str:
        """Archive a bookmark by its ID.

        Args:
            bookmark_id: The ID of the bookmark to archive

        Returns:
            Success or error message
        """
        security_error = check_destructive_actions_enabled()
        if security_error:
            return security_error

        try:
            response = await client.post(f"/bookmarks/{bookmark_id}/archive/")

            if response.status_code == 404:
                return f"Bookmark with ID {bookmark_id} not found"
            elif response.status_code != 204:
                return await handle_api_error(response)

            return f"Bookmark {bookmark_id} archived successfully"

        except httpx.RequestError as e:
            return f"Connection error: {str(e)}"
        except Exception as e:
            return f"Error archiving bookmark: {str(e)}"

    @mcp.tool
    async def unarchive_bookmark(bookmark_id: int) -> str:
        """Unarchive a bookmark by its ID.

        Args:
            bookmark_id: The ID of the bookmark to unarchive

        Returns:
            Success or error message
        """
        security_error = check_destructive_actions_enabled()
        if security_error:
            return security_error

        try:
            response = await client.post(f"/bookmarks/{bookmark_id}/unarchive/")

            if response.status_code == 404:
                return f"Bookmark with ID {bookmark_id} not found"
            elif response.status_code != 204:
                return await handle_api_error(response)

            return f"Bookmark {bookmark_id} unarchived successfully"

        except httpx.RequestError as e:
            return f"Connection error: {str(e)}"
        except Exception as e:
            return f"Error unarchiving bookmark: {str(e)}"

    @mcp.tool
    async def check_url(url: str) -> str:
        """Check if a URL is already bookmarked and get metadata.

        Args:
            url: The URL to check

        Returns:
            JSON string containing bookmark status, metadata, and auto-tags
        """
        try:
            response = await client.get("/bookmarks/check/", params={"url": url})

            if response.status_code != 200:
                return await handle_api_error(response)

            check_result = BookmarkCheck(**response.json())
            return check_result.model_dump_json(indent=2)

        except httpx.RequestError as e:
            return f"Connection error: {str(e)}"
        except Exception as e:
            return f"Error checking URL: {str(e)}"

    @mcp.tool
    async def list_tags(limit: int = 100, offset: int = 0) -> str:
        """List all available tags.

        Args:
            limit: Maximum number of tags to return (default: 100)
            offset: Number of tags to skip for pagination (default: 0)

        Returns:
            JSON string containing the list of tags
        """
        try:
            response = await client.get("/tags/", params={"limit": limit, "offset": offset})

            if response.status_code != 200:
                return await handle_api_error(response)

            tag_list = TagList(**response.json())
            return tag_list.model_dump_json(indent=2)

        except httpx.RequestError as e:
            return f"Connection error: {str(e)}"
        except Exception as e:
            return f"Error listing tags: {str(e)}"

    @mcp.tool
    async def list_bookmarks_by_tag(tag_name: str, limit: int = 100, offset: int = 0) -> str:
        """List bookmarks filtered by a specific tag.

        Args:
            tag_name: Name of the tag to filter by
            limit: Maximum number of bookmarks to return (default: 100)
            offset: Number of bookmarks to skip for pagination (default: 0)

        Returns:
            JSON string containing bookmarks with the specified tag
        """
        try:
            return await search_bookmarks(tag=tag_name, limit=limit, offset=offset)
        except Exception as e:
            return f"Error listing bookmarks by tag: {str(e)}"

    return mcp
