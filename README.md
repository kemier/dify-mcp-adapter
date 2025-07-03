# Dify MCP Adapter Plugin

A comprehensive Dify plugin for managing MCP (Model Context Protocol) servers, enabling dynamic tool discovery and execution from registry endpoints.

## Features

- 🔌 **MCP Server Discovery**: Automatically fetch MCP servers from registry endpoints
- 🛠️ **Dynamic Tool Management**: Discover and manage tools from multiple MCP servers
- 🎯 **LLM Integration**: Allow LLMs to query tool schemas and execute tools with validation
- 📊 **Management Dashboard**: Web-based dashboard for server management and analytics
- ⚡ **Real-time Updates**: Refresh server configurations and tool availability
- 🔒 **Argument Validation**: Validate tool arguments against schemas before execution

## Installation

### Using UV (Recommended)

1. **Install UV** if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Clone the repository**:
```bash
git clone https://github.com/kemier/dify-mcp-adapter.git
cd dify-mcp-adapter
```

3. **Set up Python environment with UV**:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

4. **Install dependencies**:
```bash
uv pip install -r requirements.txt
```

### Using pip

1. **Clone the repository**:
```bash
git clone https://github.com/kemier/dify-mcp-adapter.git
cd dify-mcp-adapter
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

### Configuration

Configure environment variables (create `.env` file):
```env
PLUGIN_HOST=0.0.0.0
PLUGIN_PORT=5000
PLUGIN_DEBUG=false
MCP_REGISTRY_URL=https://registry.com/api/mcp-servers
USE_MOCK_DATA=true
```

## Usage

### Running the Plugin

```bash
python -m main
```

The plugin will start on `http://localhost:5000` by default.

### Available Tools

#### 1. Fetch MCP Servers
Retrieves available MCP servers from the registry.

**Parameters:**
- `refresh_from_registry` (boolean): Whether to fetch fresh data from registry
- `filter_enabled_only` (boolean): Only return enabled servers

**Usage:**
```json
{
  "refresh_from_registry": true,
  "filter_enabled_only": false
}
```

#### 2. Fetch Tools Schema
Gets schema information for tools from MCP servers.

**Parameters:**
- `server_name` (string): Specific server to get tools from
- `tool_name` (string): Specific tool to get schema for
- `include_examples` (boolean): Include usage examples

**Usage:**
```json
{
  "server_name": "github-mcp",
  "include_examples": true
}
```

#### 3. Call MCP Tool
Executes a tool on an MCP server with provided arguments.

**Parameters:**
- `server_name` (string, required): MCP server name
- `tool_name` (string, required): Tool name to execute
- `arguments` (string): JSON string of tool arguments
- `validate_args` (boolean): Whether to validate arguments

**Usage:**
```json
{
  "server_name": "github-mcp",
  "tool_name": "create_issue",
  "arguments": "{\"repository\": \"owner/repo\", \"title\": \"Bug report\", \"body\": \"Description of the bug\"}",
  "validate_args": true
}
```

#### 4. Manage MCP Dashboard
Provides dashboard management operations.

**Actions:**
- `get_status`: Get overall server status
- `enable_server`: Enable a specific server
- `disable_server`: Disable a specific server
- `refresh_registry`: Refresh from registry
- `get_server_details`: Get detailed server information
- `get_analytics`: Get analytics data

### Web Dashboard

Access the management dashboard at `http://localhost:5000/dashboard`

The dashboard provides:
- Server overview and statistics
- Enable/disable server controls
- Registry refresh functionality
- Server details and tool listings
- Analytics and usage metrics

## Configuration

### MCP Server Configuration

Servers are automatically discovered from the registry endpoint configured in `MCP_REGISTRY_URL`. The configuration is stored in `config/mcp_servers.json`.

### Mock Data for Development

When `USE_MOCK_DATA=true`, the plugin uses mock MCP servers for development:

- **github-mcp**: GitHub integration with tools like `create_issue`, `get_repository`, `search_code`
- **slack-mcp**: Slack integration with tools like `send_message`, `create_channel`, `get_users`
- **database-mcp**: Database operations with tools like `execute_query`, `get_schema`, `backup_database`

## Architecture

```
dify-mcp-adapter/
├── main.py                 # Plugin entry point
├── manifest.yaml          # Plugin manifest
├── requirements.txt       # Dependencies
├── config/
│   ├── __init__.py
│   └── mcp_config.py      # MCP configuration management
├── tools/
│   ├── __init__.py
│   ├── fetch_mcp_servers.py      # Fetch servers tool
│   ├── fetch_tools_schema.py     # Fetch tools schema tool
│   ├── call_mcp_tool.py          # Call MCP tool
│   └── manage_mcp_dashboard.py   # Dashboard management tool
└── endpoints/
    ├── __init__.py
    └── dashboard.py        # Web dashboard endpoint
```

## Development

### Adding New MCP Servers

1. Add server configuration to the registry or manually to `config/mcp_servers.json`
2. Implement server-specific tool execution logic in `call_mcp_tool.py`
3. Update mock data if needed for development

### Extending Tool Functionality

1. Create new tool classes in the `tools/` directory
2. Register tools in `main.py`
3. Update the manifest file with new tool definitions

### Testing

```bash
# Run tests (when implemented)
pytest tests/

# Format code
black .

# Lint code
flake8 .
```

## API Reference

### REST API Endpoints

- `GET /dashboard` - Main dashboard interface
- `POST /dashboard/api/manage` - Dashboard management API

### Tool Responses

All tools return a standardized response format:

```json
{
  "success": true,
  "data": { /* tool-specific data */ },
  "message": "Operation completed successfully",
  "error": null  // Only present when success is false
}
```

## Integration with Dify

### As LLM Tools

The plugin tools can be used by LLMs in Dify agents:

1. **Discovery Phase**: Use `fetch_mcp_servers` to discover available servers
2. **Schema Phase**: Use `fetch_tools_schema` to understand available tools
3. **Execution Phase**: Use `call_mcp_tool` to execute specific tools
4. **Management**: Use `manage_mcp_dashboard` for administrative tasks

### Agent Configuration

When building agents in Dify:

1. Enable the MCP adapter plugin
2. Configure which MCP servers to use
3. Allow the agent to discover and use tools dynamically
4. Set up appropriate permissions and validation

## Environment Variables

Configure the plugin behavior with these environment variables:

- `MCP_REGISTRY_URL`: URL of the MCP registry endpoint
- `USE_MOCK_DATA`: Use mock data for development (true/false) - default: false
- `PLUGIN_HOST`: Host to bind the plugin server - default: 0.0.0.0
- `PLUGIN_PORT`: Port for the plugin server - default: 5000  
- `PLUGIN_DEBUG`: Enable debug mode (true/false) - default: false

## Troubleshooting

### Common Issues

1. **Registry Connection Failed**: Check `MCP_REGISTRY_URL` and network connectivity
2. **Tool Execution Failed**: Verify server is enabled and arguments are correct
3. **Dashboard Not Loading**: Ensure plugin is running and port is accessible

### Debug Mode

Set `PLUGIN_DEBUG=true` in environment to enable debug mode.

### Mock Data

Use mock data for development without external dependencies (automatically used when registry fails).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Open an issue on the repository
- Check the Dify plugin documentation
- Review the MCP specification 