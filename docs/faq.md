# Frequently Asked Questions

Common questions and answers about the LinkDing MCP Server.

## General Questions

### What is the LinkDing MCP Server?

The LinkDing MCP Server is a Model Context Protocol (MCP) server that enables LLMs like Claude to interact with your LinkDing bookmark manager. It provides tools for searching, adding, updating, and organizing bookmarks through natural language conversations.

### What is LinkDing?

[LinkDing](https://github.com/sissbruecker/linkding) is a self-hosted bookmark manager that provides a clean web interface and REST API for managing your bookmarks. It's privacy-focused and runs on your own infrastructure.

### What is MCP?

The Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to LLMs. It enables communication between LLMs and external tools, databases, and services.

### Do I need to run LinkDing locally?

No, the LinkDing MCP Server can connect to any LinkDing instance that's accessible over HTTP/HTTPS, whether it's running locally, on your network, or hosted remotely.

## Installation and Setup

### What Python version do I need?

Python 3.12 or higher is required. The server uses modern Python features and type hints that require this minimum version.

### Can I use this with other bookmark managers?

No, this server is specifically designed for LinkDing's API. However, the architecture could be adapted for other bookmark managers with similar APIs.

### Do I need Docker to run this?

No, Docker is not required. The server runs as a standard Python application. However, you can use Docker if you prefer containerized deployments.

### How do I get a LinkDing API token?

1. Open your LinkDing web interface
2. Go to Settings (usually in the user menu)
3. Find the API or Integrations section
4. Copy the API Token
5. Add it to your `.env` file as `LINKDING_API_TOKEN`

## Usage and Features

### What can I do with this server?

You can:
- Search your bookmarks by text, tags, or status
- Add new bookmarks with automatic metadata scraping
- Update existing bookmarks (title, description, notes, tags)
- Delete bookmarks
- Archive and unarchive bookmarks
- Check if URLs are already bookmarked
- List and manage tags
- Filter bookmarks by specific tags

### Can I use this with Claude Desktop?

Yes! Claude Desktop is the primary integration target. See the [Claude Desktop Integration](integration/claude.md) guide for setup instructions.

### Can I use this with other AI assistants?

Yes, any application that supports the Model Context Protocol can use this server. This includes Continue.dev, Cursor, Zed Editor, and custom applications.

### How do I prevent duplicate bookmarks?

Use the `check_url` tool before adding bookmarks:

```python
result = check_url(url="https://example.com")
if not result['is_bookmarked']:
    add_bookmark(url="https://example.com")
```

### Can I bulk import bookmarks?

Yes, you can write scripts that use the MCP tools to bulk import bookmarks. The `check_url` tool helps prevent duplicates during bulk operations.

### How do I organize bookmarks with tags?

Use consistent tagging strategies:
- **Hierarchical**: `lang-python`, `framework-django`
- **Multi-dimensional**: `python`, `tutorial`, `beginner`
- **Project-based**: `project-alpha`, `documentation`

See the [Tag Management](tools/tags.md) guide for detailed strategies.

## Performance and Limits

### How many bookmarks can I search?

There's no hard limit, but for performance reasons:
- Default search limit is 100 results
- Use pagination for larger datasets
- Consider using more specific search terms
- Filter by tags to narrow results

### Is there rate limiting?

The server respects LinkDing's built-in rate limiting. For high-volume usage, consider:
- Using reasonable request limits
- Implementing client-side delays
- Batching operations when possible

### Can I cache results?

The server doesn't implement caching, but you can:
- Cache tag lists (they change infrequently)
- Implement client-side caching for repeated searches
- Use LinkDing's built-in caching mechanisms

## Security and Privacy

### Is my data secure?

Yes, the server:
- Never logs API tokens
- Connects directly to your LinkDing instance
- Doesn't store or cache bookmark data
- Uses secure HTTPS connections (when configured)

### Should I use HTTPS?

Yes, especially for remote LinkDing instances:
- Use HTTPS URLs in `LINKDING_URL`
- Ensure your LinkDing instance has valid SSL certificates
- Consider VPN for internal network access

### How do I rotate API tokens?

1. Generate a new token in LinkDing Settings
2. Update your `.env` file with the new token
3. Restart the MCP server
4. Update any client configurations (like Claude Desktop)
5. Test connectivity

### Can I limit what the server can do?

The server has the same permissions as your LinkDing API token. LinkDing doesn't currently support scoped tokens, so the server has full access to your bookmarks.

## Troubleshooting

### The server won't start

Common causes and solutions:

1. **Missing API token**: Check your `.env` file
2. **Python version**: Ensure Python 3.12+
3. **Missing dependencies**: Run `pip install -r requirements.txt`
4. **Permission issues**: Make the script executable with `chmod +x linkding_server.py`

### I get "Connection refused" errors

This usually means:

1. **LinkDing isn't running**: Check if your LinkDing instance is accessible
2. **Wrong URL**: Verify `LINKDING_URL` in your `.env` file
3. **Network issues**: Test connectivity with `curl`
4. **Firewall**: Ensure the port is accessible

### Claude Desktop doesn't see the server

Check:

1. **Configuration file location**: Ensure it's in the right place for your OS
2. **JSON syntax**: Validate your configuration file
3. **Absolute paths**: Use full paths in the configuration
4. **Restart**: Completely quit and restart Claude Desktop

### I get "Unauthorized" errors

This means:

1. **Invalid token**: Generate a new API token in LinkDing
2. **Expired token**: Some LinkDing configurations may expire tokens
3. **Wrong format**: Ensure the token is correctly formatted in your `.env` file

## Development and Customization

### Can I modify the server?

Yes! The server is open source. See the [Development Guide](development/contributing.md) for information about:
- Code structure
- Adding new tools
- Testing
- Contributing back to the project

### Can I add custom tools?

Yes, you can extend the server with additional tools. The FastMCP framework makes it easy to add new functionality.

### How do I report bugs?

1. Check the [Troubleshooting](troubleshooting.md) guide first
2. Run the health check script to gather diagnostic information
3. Create an issue on GitHub with:
   - Steps to reproduce
   - Error messages
   - Environment information
   - Configuration (with tokens redacted)

### Can I contribute to the project?

Absolutely! Contributions are welcome:
- Bug fixes
- New features
- Documentation improvements
- Testing
- Examples and tutorials

See the [Contributing Guide](development/contributing.md) for details.

## Integration Specific

### How do I use this with VS Code?

Use the Continue.dev extension with MCP support. See the [Other MCP Clients](integration/clients.md) guide for configuration details.

### Can I use this in web applications?

Yes, run the server with HTTP transport:

```bash
fastmcp run linkding_server.py --transport http --port 8000
```

Then make HTTP requests to the server endpoints.

### How do I integrate with custom applications?

You can:
- Use the MCP SDK for your language
- Make HTTP requests to the server (with HTTP transport)
- Run the server as a subprocess
- Use the FastMCP CLI for scripting

## Comparison with Alternatives

### How does this compare to browser bookmarks?

Advantages:
- **Centralized**: Access from any device/application
- **AI Integration**: Natural language search and organization
- **Rich metadata**: Notes, descriptions, tags
- **API access**: Programmatic management
- **Self-hosted**: Full control over your data

### How does this compare to cloud bookmark services?

Advantages:
- **Privacy**: Your data stays on your infrastructure
- **Customization**: Full control over features and data
- **No vendor lock-in**: Open source and self-hosted
- **AI integration**: Direct LLM access to your bookmarks

### Why not just use LinkDing directly?

The MCP server adds:
- **AI integration**: Natural language bookmark management
- **Conversational interface**: Manage bookmarks through chat
- **Automated workflows**: Let AI help organize and discover content
- **Cross-application access**: Use bookmarks in various tools

## Future Plans

### What features are planned?

Potential future features:
- **Bookmark collections**: Group related bookmarks
- **Smart tagging**: AI-powered tag suggestions
- **Content analysis**: Extract and index bookmark content
- **Sync capabilities**: Multi-instance synchronization
- **Advanced search**: Full-text search within bookmark content

### Will this work with LinkDing v2?

The server will be updated to support new LinkDing versions as they're released. The API is generally stable, so most features should continue working.

### Can I request features?

Yes! Feature requests are welcome:
1. Check existing GitHub issues first
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Implementation suggestions (if any)

## Getting Help

### Where can I get support?

- **Documentation**: Start with this documentation
- **GitHub Issues**: For bugs and feature requests
- **Health Check**: Run the diagnostic script first
- **Community**: LinkDing and MCP community forums

### What information should I provide when asking for help?

Include:
- Python version and OS
- LinkDing version
- Error messages (full output)
- Configuration (with tokens redacted)
- Steps to reproduce the issue
- Health check results

### How do I stay updated?

- **Watch the GitHub repository** for updates
- **Check the changelog** for new releases
- **Follow LinkDing updates** for compatibility information
- **Monitor MCP protocol changes** for new features

## Best Practices

### How should I organize my bookmarks?

Recommended strategies:
- **Consistent tagging**: Use standardized tag formats
- **Hierarchical organization**: Create tag hierarchies
- **Regular maintenance**: Clean up and reorganize periodically
- **Descriptive titles**: Use clear, searchable titles
- **Rich notes**: Add context and insights

### How often should I backup my data?

- **LinkDing data**: Follow LinkDing's backup recommendations
- **Configuration**: Backup your `.env` and client configurations
- **Regular exports**: Consider periodic bookmark exports
- **Test restores**: Verify your backups work

### What's the best way to learn the tools?

1. **Start simple**: Begin with basic search and add operations
2. **Use Claude Desktop**: Interactive learning through conversation
3. **Read examples**: Check the documentation examples
4. **Experiment**: Try different search patterns and workflows
5. **Build workflows**: Create repeatable bookmark management processes

---

*Don't see your question here? Check the [Troubleshooting](troubleshooting.md) guide or create an issue on GitHub.*