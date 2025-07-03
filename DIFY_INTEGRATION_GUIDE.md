# Dify MCP Adapter Plugin - Integration Guide

## Overview
This guide helps you integrate the MCP Adapter Plugin with your running Dify instance on macOS.

## Current Status
✅ Plugin is tested and working in standalone mode
✅ All tools are functional:
- **fetch_mcp_servers**: Discovers available MCP servers
- **fetch_tools_schema**: Gets tool schemas from MCP servers
- **call_mcp_tool**: Executes tools on MCP servers
- **manage_mcp_dashboard**: Manages server configuration

## Integration Steps

### 1. Prepare the Plugin Package

Since Dify uses a different plugin framework in production, you'll need to:

1. **Package the plugin**:
   ```bash
   # Create a plugin package
   zip -r mcp-adapter-plugin.zip . -x "*.pyc" -x "__pycache__/*" -x ".venv/*" -x "logs/*"
   ```

2. **Verify manifest.yaml** is correctly formatted for your Dify version

### 2. Install in Dify

1. **Locate Dify's plugin directory**:
   - Usually at `~/dify/plugins/` or similar
   - Check Dify's configuration for the exact path

2. **Copy plugin files**:
   ```bash
   cp -r /Users/zaedinzeng/projects/dify-mcp-adapter ~/dify/plugins/mcp-adapter
   ```

3. **Restart Dify** to load the new plugin

### 3. Configure in Dify

1. **Access Dify Admin Panel**:
   - Go to Settings → Plugins
   - Find "MCP Server Adapter" in the list
   - Enable the plugin

2. **Configure MCP Registry**:
   - Set `MCP_REGISTRY_URL` to your MCP registry endpoint
   - Or use the mock data for testing

### 4. Use in Dify Workflows

1. **Create a new Agent or Workflow**

2. **Add MCP tools**:
   ```yaml
   tools:
     - fetch_mcp_servers:
         refresh_from_registry: true
         filter_enabled_only: true
     
     - fetch_tools_schema:
         server_name: "github-mcp"
         include_examples: true
     
     - call_mcp_tool:
         server_name: "github-mcp"
         tool_name: "create_issue"
         arguments: '{"repository": "org/repo", "title": "Issue Title"}'
   ```

3. **Example Agent Prompt**:
   ```
   You are an assistant with access to MCP (Model Context Protocol) servers.
   
   First, use fetch_mcp_servers to see what servers are available.
   Then, use fetch_tools_schema to understand what tools each server provides.
   Finally, use call_mcp_tool to execute specific actions.
   
   Always validate arguments before calling tools.
   ```

## Testing the Integration

### Quick Test
1. Create a simple workflow that:
   - Fetches available MCP servers
   - Gets schema for github-mcp
   - Lists the available tools

### Full Test
Run the test script to verify all functionality:
```bash
python test_plugin.py
```

## Dashboard Access

Once integrated, access the MCP Dashboard at:
```
http://[your-dify-host]:[port]/plugins/mcp-adapter/dashboard
```

Features:
- View all MCP servers and their status
- Enable/disable servers
- View tool schemas
- Monitor usage analytics

## Troubleshooting

### Plugin Not Showing in Dify
1. Check the manifest.yaml format matches Dify's requirements
2. Verify file permissions
3. Check Dify logs for plugin loading errors

### Tools Not Working
1. Check logs in `logs/mcp_adapter.log`
2. Verify MCP server connectivity
3. Ensure proper authentication is configured

### Dashboard Not Loading
1. Check if the endpoint is registered correctly
2. Verify port is not blocked
3. Check browser console for errors

## Next Steps

1. **Production Setup**:
   - Configure real MCP registry URL
   - Set up authentication for MCP servers
   - Configure logging levels

2. **Advanced Usage**:
   - Create custom MCP servers
   - Extend tool functionality
   - Build complex workflows

3. **Monitoring**:
   - Set up log aggregation
   - Monitor tool usage
   - Track performance metrics

## Support

For issues or questions:
1. Check the logs in `logs/` directory
2. Run the demo script for debugging
3. Verify MCP server connectivity

---

**Note**: This plugin is currently using mock data for development. In production, configure real MCP server endpoints and authentication. 