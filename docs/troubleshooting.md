# Troubleshooting

Common issues and solutions for the LinkDing MCP Server.

## Quick Diagnostics

### Health Check Script

Create a simple diagnostic script to test your setup:

```python
#!/usr/bin/env python3
"""
LinkDing MCP Server Health Check
"""
import os
import httpx
from dotenv import load_dotenv

def main():
    print("🔍 LinkDing MCP Server Health Check")
    print("=" * 40)
    
    # Load environment
    load_dotenv()
    
    # Check environment variables
    print("\n1. Environment Variables:")
    linkding_url = os.getenv("LINKDING_URL")
    linkding_token = os.getenv("LINKDING_API_TOKEN")
    debug = os.getenv("DEBUG", "false")
    
    print(f"   LINKDING_URL: {'✅' if linkding_url else '❌'} {linkding_url or 'Not set'}")
    print(f"   LINKDING_API_TOKEN: {'✅' if linkding_token else '❌'} {'Set' if linkding_token else 'Not set'}")
    print(f"   DEBUG: {debug}")
    
    if not linkding_url or not linkding_token:
        print("\n❌ Missing required environment variables")
        return False
    
    # Test LinkDing connectivity
    print("\n2. LinkDing Connectivity:")
    try:
        response = httpx.get(f"{linkding_url.rstrip('/')}/api/bookmarks/", 
                           headers={"Authorization": f"Token {linkding_token}"},
                           params={"limit": 1},
                           timeout=10.0)
        
        if response.status_code == 200:
            print("   ✅ Successfully connected to LinkDing")
            data = response.json()
            print(f"   📊 Total bookmarks: {data.get('count', 'Unknown')}")
            return True
        else:
            print(f"   ❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except httpx.ConnectError:
        print(f"   ❌ Cannot connect to {linkding_url}")
        print("   💡 Check if LinkDing is running and URL is correct")
        return False
    except httpx.TimeoutException:
        print("   ❌ Connection timeout")
        print("   💡 LinkDing may be slow to respond")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
```

Save as `health_check.py` and run:

```bash
python health_check.py
```

## Common Issues

### 1. Environment Variable Issues

#### "LINKDING_API_TOKEN environment variable is required"

**Cause:** Missing or empty API token

**Solutions:**

1. **Check .env file exists:**
   ```bash
   ls -la .env
   ```

2. **Verify .env content:**
   ```bash
   cat .env
   ```

3. **Create .env from sample:**
   ```bash
   cp .env.sample .env
   # Edit .env with your values
   ```

4. **Check environment loading:**
   ```python
   from dotenv import load_dotenv
   import os
   
   load_dotenv()
   print("Token:", os.getenv("LINKDING_API_TOKEN"))
   ```

#### Environment Variables Not Loading

**Cause:** .env file not in correct location or not loaded

**Solutions:**

1. **Verify file location:**
   ```bash
   pwd  # Should be in linkding-mcp-server directory
   ls .env
   ```

2. **Check file permissions:**
   ```bash
   ls -la .env
   chmod 644 .env
   ```

3. **Load explicitly:**
   ```python
   from dotenv import load_dotenv
   load_dotenv("/absolute/path/to/.env")
   ```

### 2. Connection Issues

#### "Connection refused" or "Cannot connect"

**Cause:** LinkDing instance not running or URL incorrect

**Solutions:**

1. **Verify LinkDing is running:**
   ```bash
   # If using Docker
   docker ps | grep linkding
   
   # If using systemd
   systemctl status linkding
   
   # Check process
   ps aux | grep linkding
   ```

2. **Test URL directly:**
   ```bash
   curl http://127.0.0.1:9090
   # Should return LinkDing web interface
   ```

3. **Check port and host:**
   ```bash
   # Common LinkDing ports: 9090, 8000, 80, 443
   netstat -tlnp | grep :9090
   ```

4. **Test API endpoint:**
   ```bash
   curl -H "Authorization: Token YOUR_TOKEN" \
        http://127.0.0.1:9090/api/bookmarks/?limit=1
   ```

#### "HTTP 401: Unauthorized"

**Cause:** Invalid or expired API token

**Solutions:**

1. **Generate new token:**
   - Open LinkDing web interface
   - Go to Settings → API
   - Copy the API token
   - Update .env file

2. **Verify token format:**
   ```bash
   # Token should be a long string like:
   # abcd1234efgh5678ijkl9012mnop3456qrst7890
   echo $LINKDING_API_TOKEN | wc -c  # Should be ~40 characters
   ```

3. **Test token manually:**
   ```bash
   curl -H "Authorization: Token YOUR_ACTUAL_TOKEN" \
        http://127.0.0.1:9090/api/bookmarks/?limit=1
   ```

#### "HTTP 404: Not Found"

**Cause:** Incorrect API endpoint or LinkDing version mismatch

**Solutions:**

1. **Check LinkDing version:**
   ```bash
   curl http://127.0.0.1:9090/api/
   # Should return API information
   ```

2. **Verify API endpoints:**
   ```bash
   # Test different endpoints
   curl -H "Authorization: Token YOUR_TOKEN" \
        http://127.0.0.1:9090/api/bookmarks/
   ```

3. **Check URL format:**
   ```bash
   # Ensure no trailing slashes in LINKDING_URL
   LINKDING_URL=http://127.0.0.1:9090  # Good
   LINKDING_URL=http://127.0.0.1:9090/ # May cause issues
   ```

### 3. Python and Dependency Issues

#### "Module not found" errors

**Cause:** Missing dependencies

**Solutions:**

1. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Check Python version:**
   ```bash
   python --version  # Should be 3.12+
   ```

3. **Use virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

4. **Verify installation:**
   ```bash
   pip list | grep -E "(fastmcp|httpx|pydantic|python-dotenv)"
   ```

#### "Permission denied" errors

**Cause:** Script not executable or permission issues

**Solutions:**

1. **Make script executable:**
   ```bash
   chmod +x linkding_server.py
   ```

2. **Check file ownership:**
   ```bash
   ls -la linkding_server.py
   chown $USER:$USER linkding_server.py
   ```

3. **Run with python explicitly:**
   ```bash
   python linkding_server.py
   ```

### 4. MCP Client Integration Issues

#### Claude Desktop: "No MCP servers found"

**Cause:** Configuration file issues

**Solutions:**

1. **Check config file location:**
   ```bash
   # macOS
   ls -la ~/Library/Application\ Support/Claude/claude_desktop_config.json
   
   # Windows
   dir %APPDATA%\Claude\claude_desktop_config.json
   ```

2. **Validate JSON syntax:**
   ```bash
   python -m json.tool claude_desktop_config.json
   ```

3. **Use absolute paths:**
   ```json
   {
     "mcpServers": {
       "linkding": {
         "command": "/usr/bin/python3",
         "args": ["/absolute/path/to/linkding_server.py"]
       }
     }
   }
   ```

4. **Check Python path:**
   ```bash
   which python
   which python3
   ```

#### "Server failed to start"

**Cause:** Incorrect paths or environment issues

**Solutions:**

1. **Test command manually:**
   ```bash
   # Copy the exact command from config
   /usr/bin/python3 /path/to/linkding_server.py
   ```

2. **Check environment variables in config:**
   ```json
   {
     "mcpServers": {
       "linkding": {
         "command": "python",
         "args": ["/path/to/linkding_server.py"],
         "env": {
           "LINKDING_URL": "http://127.0.0.1:9090",
           "LINKDING_API_TOKEN": "your_token_here"
         }
       }
     }
   }
   ```

3. **Use virtual environment path:**
   ```json
   {
     "mcpServers": {
       "linkding": {
         "command": "/path/to/venv/bin/python",
         "args": ["/path/to/linkding_server.py"]
       }
     }
   }
   ```

### 5. Performance Issues

#### Slow response times

**Cause:** Network latency or large datasets

**Solutions:**

1. **Use smaller limits:**
   ```python
   search_bookmarks(query="python", limit=20)  # Instead of 100
   ```

2. **Enable connection pooling:**
   ```python
   # In linkding_server.py
   client = httpx.AsyncClient(
       limits=httpx.Limits(max_connections=10)
   )
   ```

3. **Check LinkDing performance:**
   ```bash
   curl -w "@curl-format.txt" -H "Authorization: Token YOUR_TOKEN" \
        http://127.0.0.1:9090/api/bookmarks/?limit=100
   ```

#### Memory usage issues

**Cause:** Large result sets or memory leaks

**Solutions:**

1. **Use pagination:**
   ```python
   # Instead of getting all bookmarks
   search_bookmarks(limit=50, offset=0)
   search_bookmarks(limit=50, offset=50)
   ```

2. **Monitor memory:**
   ```bash
   # Linux/Mac
   ps aux | grep python
   top -p $(pgrep -f linkding_server)
   ```

### 6. Data Issues

#### "Bookmark not found" errors

**Cause:** Bookmark ID doesn't exist or was deleted

**Solutions:**

1. **Verify bookmark exists:**
   ```python
   # Search for bookmark first
   results = search_bookmarks(query="", limit=1000)
   bookmark_ids = [b['id'] for b in results]
   print(f"Available IDs: {bookmark_ids}")
   ```

2. **Handle missing bookmarks:**
   ```python
   try:
       bookmark = get_bookmark(bookmark_id=123)
   except Exception as e:
       if "not found" in str(e).lower():
           print("Bookmark was deleted or doesn't exist")
       else:
           raise
   ```

#### Duplicate bookmarks

**Cause:** Not checking for existing URLs

**Solutions:**

1. **Always check before adding:**
   ```python
   result = check_url(url="https://example.com")
   if not result['is_bookmarked']:
       add_bookmark(url="https://example.com")
   ```

2. **Find duplicates:**
   ```python
   bookmarks = search_bookmarks(limit=1000)
   urls = {}
   for bookmark in bookmarks:
       url = bookmark['url']
       if url in urls:
           print(f"Duplicate: {url}")
           print(f"  ID {urls[url]}: {bookmark['title']}")
           print(f"  ID {bookmark['id']}: {bookmark['title']}")
       else:
           urls[url] = bookmark['id']
   ```

## Debug Mode

### Enable Debug Logging

1. **Set environment variable:**
   ```bash
   export DEBUG=true
   ```

2. **Or in .env file:**
   ```env
   DEBUG=true
   ```

3. **Run server:**
   ```bash
   python linkding_server.py
   ```

### Debug Output

With debug mode enabled, you'll see:

```
2024-01-15 10:30:00 - linkding_server - DEBUG - Making request: GET http://127.0.0.1:9090/api/bookmarks/
2024-01-15 10:30:00 - linkding_server - DEBUG - Request params: {'q': 'python', 'limit': 10}
2024-01-15 10:30:00 - linkding_server - DEBUG - Response status: 200
2024-01-15 10:30:00 - linkding_server - DEBUG - Response data: {"count": 25, "results": [...]}
```

### Log Files

Debug mode creates log files:

```bash
# Check log file
tail -f linkding-mcp.log

# Search for errors
grep -i error linkding-mcp.log

# Search for specific requests
grep "search_bookmarks" linkding-mcp.log
```

## Advanced Troubleshooting

### Network Analysis

1. **Monitor HTTP traffic:**
   ```bash
   # Using tcpdump
   sudo tcpdump -i lo port 9090
   
   # Using Wireshark
   wireshark -i lo -f "port 9090"
   ```

2. **Check DNS resolution:**
   ```bash
   nslookup your-linkding-domain.com
   dig your-linkding-domain.com
   ```

3. **Test with curl:**
   ```bash
   # Verbose output
   curl -v -H "Authorization: Token YOUR_TOKEN" \
        http://127.0.0.1:9090/api/bookmarks/?limit=1
   ```

### Database Issues

If LinkDing has database problems:

1. **Check LinkDing logs:**
   ```bash
   # Docker
   docker logs linkding-container
   
   # Systemd
   journalctl -u linkding
   
   # Direct logs
   tail -f /path/to/linkding/logs/linkding.log
   ```

2. **Database connectivity:**
   ```bash
   # If using PostgreSQL
   psql -h localhost -U linkding_user -d linkding_db
   
   # If using SQLite
   sqlite3 /path/to/linkding/db.sqlite3 ".tables"
   ```

### Performance Profiling

1. **Profile Python code:**
   ```python
   import cProfile
   import pstats
   
   # Profile a function
   cProfile.run('search_bookmarks("python")', 'profile_stats')
   stats = pstats.Stats('profile_stats')
   stats.sort_stats('cumulative').print_stats(10)
   ```

2. **Monitor system resources:**
   ```bash
   # CPU and memory usage
   htop
   
   # Network connections
   netstat -an | grep :9090
   
   # Disk I/O
   iotop
   ```

## Getting Help

### Information to Gather

When seeking help, provide:

1. **Environment details:**
   ```bash
   python --version
   pip list | grep -E "(fastmcp|httpx|pydantic)"
   uname -a  # Linux/Mac
   ```

2. **Configuration (sanitized):**
   ```bash
   # Remove sensitive tokens
   cat .env | sed 's/LINKDING_API_TOKEN=.*/LINKDING_API_TOKEN=[REDACTED]/'
   ```

3. **Error messages:**
   ```bash
   # Full error output
   python linkding_server.py 2>&1 | tee error.log
   ```

4. **Health check results:**
   ```bash
   python health_check.py
   ```

### Support Channels

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check this documentation for solutions
- **Community**: LinkDing and MCP community forums
- **Debug Mode**: Enable for detailed troubleshooting information

### Creating Bug Reports

Include in your bug report:

1. **Steps to reproduce**
2. **Expected behavior**
3. **Actual behavior**
4. **Environment information**
5. **Configuration (sanitized)**
6. **Error logs**
7. **Health check output**

## Prevention

### Regular Maintenance

1. **Update dependencies:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Rotate API tokens:**
   - Generate new token monthly
   - Update all configurations
   - Test connectivity

3. **Monitor logs:**
   ```bash
   # Set up log rotation
   logrotate /etc/logrotate.d/linkding-mcp
   ```

4. **Backup configuration:**
   ```bash
   cp .env .env.backup
   cp claude_desktop_config.json claude_desktop_config.json.backup
   ```

### Health Monitoring

Set up automated health checks:

```bash
#!/bin/bash
# health_monitor.sh
if ! python health_check.py; then
    echo "LinkDing MCP Server health check failed" | mail -s "Alert" admin@example.com
fi
```

Add to crontab:
```bash
# Check every 15 minutes
*/15 * * * * /path/to/health_monitor.sh
```

## Next Steps

- **[FAQ](faq.md)** - Frequently asked questions
- **[Development Guide](development/contributing.md)** - Contribute fixes
- **[API Reference](api/reference.md)** - Technical details