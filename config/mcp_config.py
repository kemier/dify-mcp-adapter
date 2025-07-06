"""
MCP Configuration Management
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import aiohttp
import asyncio
from .logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)


@dataclass
class MCPServer:
    """MCP Server configuration."""
    name: str
    url: str
    enabled: bool = True
    description: str = ""
    tags: List[str] = None
    last_updated: str = ""
    available_tools: List[Dict[str, Any]] = None
    enabled_tools: List[str] = None  # Track enabled tools for this server

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.available_tools is None:
            self.available_tools = []
        if self.enabled_tools is None:
            self.enabled_tools = []
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()
        # If enabled_tools is empty but we have available_tools, enable all by default
        if not self.enabled_tools and self.available_tools:
            self.enabled_tools = [tool['name'] for tool in self.available_tools]
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.available_tools is None:
            self.available_tools = []
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()


class MCPConfig:
    """MCP Configuration Manager."""
    
    def __init__(self, config_file: str = "config/mcp_servers.json"):
        self.config_file = config_file
        self.servers: Dict[str, MCPServer] = {}
        self.registry_url = os.getenv("MCP_REGISTRY_URL", "http://localhost:8080/api/mcp-servers")  # Configurable registry endpoint
        self._load_config()
        self._load_registry_config()

    def _load_registry_config(self):
        """Load registry configuration from environment or config file"""
        # Load from config file if available
        if hasattr(self, 'config_data') and 'registry' in self.config_data:
            self.registry_url = self.config_data['registry'].get('url', self.registry_url)
            self.auto_refresh = self.config_data['registry'].get('auto_refresh', False)
            self.refresh_interval = self.config_data['registry'].get('refresh_interval', 3600)
        else:
            self.auto_refresh = os.getenv("MCP_REGISTRY_AUTO_REFRESH", "false").lower() == "true"
            self.refresh_interval = int(os.getenv("MCP_REGISTRY_REFRESH_INTERVAL", "3600"))

    def set_registry_url(self, url: str):
        """Set the registry URL and save configuration"""
        self.registry_url = url
        # Save to config file
        config_data = {
            'servers': {name: asdict(server) for name, server in self.servers.items()},
            'registry': {
                'url': url,
                'auto_refresh': self.auto_refresh,
                'refresh_interval': self.refresh_interval
            },
            'last_updated': datetime.now().isoformat()
        }
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        logger.info(f"Updated registry URL to: {url}")
        return True
    
    def _load_config(self):
        """Load configuration from file."""
        logger.debug(f"Loading configuration from {self.config_file}")
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    server_count = len(data.get('servers', {}))
                    logger.info(f"Loading {server_count} servers from configuration file")
                    
                    for name, server_data in data.get('servers', {}).items():
                        self.servers[name] = MCPServer(**server_data)
                        logger.debug(f"Loaded server configuration: {name}")
                        
                logger.info(f"Successfully loaded configuration with {len(self.servers)} servers")
            except Exception as e:
                logger.error(f"Error loading config from {self.config_file}: {e}")
        else:
            logger.info(f"Configuration file {self.config_file} not found, starting with empty configuration")
    
    def _save_config(self):
        """Save configuration to file."""
        logger.debug(f"Saving configuration to {self.config_file}")
        
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            config_data = {
                'servers': {name: asdict(server) for name, server in self.servers.items()},
                'last_updated': datetime.now().isoformat()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info(f"Configuration saved successfully with {len(self.servers)} servers")
        except Exception as e:
            logger.error(f"Failed to save configuration to {self.config_file}: {e}")
            raise
    
    async def fetch_registry_servers(self) -> List[Dict[str, Any]]:
        """Fetch MCP servers from the registry."""
        logger.info(f"Fetching MCP servers from registry: {self.registry_url}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.registry_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        servers = data.get('servers', [])
                        logger.registry_operation("fetch_servers", servers_count=len(servers), success=True)
                        return servers
                    else:
                        logger.warning(f"Failed to fetch from registry: HTTP {response.status}, falling back to mock data")
                        mock_servers = self._get_mock_registry_data()
                        logger.registry_operation("fetch_servers", servers_count=len(mock_servers), 
                                                success=False, error=f"HTTP {response.status}")
                        return mock_servers
        except Exception as e:
            logger.warning(f"Error fetching registry: {e}, falling back to mock data")
            mock_servers = self._get_mock_registry_data()
            logger.registry_operation("fetch_servers", servers_count=len(mock_servers), 
                                    success=False, error=str(e))
            return mock_servers
    
    def _get_mock_registry_data(self) -> List[Dict[str, Any]]:
        """Mock registry data for development."""
        return [
            {
                "name": "github-mcp",
                "url": "https://github.com/modelcontextprotocol/servers/github",
                "description": "GitHub integration for MCP",
                "tags": ["version-control", "collaboration"],
                "tools": ["create_issue", "get_repository", "search_code"]
            },
            {
                "name": "slack-mcp",
                "url": "https://github.com/modelcontextprotocol/servers/slack",
                "description": "Slack integration for MCP",
                "tags": ["communication", "collaboration"],
                "tools": ["send_message", "create_channel", "get_users"]
            },
            {
                "name": "database-mcp",
                "url": "https://github.com/modelcontextprotocol/servers/database",
                "description": "Database operations for MCP",
                "tags": ["database", "sql"],
                "tools": ["execute_query", "get_schema", "backup_database"]
            }
        ]
    
    async def refresh_servers_from_registry(self) -> List[MCPServer]:
        """Refresh server list from registry."""
        logger.info("Refreshing servers from registry")
        
        try:
            registry_servers = await self.fetch_registry_servers()
            servers_updated = 0
            servers_created = 0
            
            for server_data in registry_servers:
                name = server_data.get('name')
                if name:
                    is_new = name not in self.servers
                    if is_new:
                        servers_created += 1
                    else:
                        servers_updated += 1
                    
                    # Create or update server
                    server = MCPServer(
                        name=name,
                        url=server_data.get('url', ''),
                        description=server_data.get('description', ''),
                        tags=server_data.get('tags', []),
                        enabled=self.servers.get(name, MCPServer(name, '')).enabled,
                        last_updated=datetime.now().isoformat()
                    )
                    
                    # Mock available tools from registry data
                    if 'tools' in server_data:
                        server.available_tools = [
                            {
                                "name": tool_name,
                                "description": f"Tool: {tool_name}",
                                "parameters": {"type": "object", "properties": {}}
                            }
                            for tool_name in server_data['tools']
                        ]
                    
                    self.servers[name] = server
                    logger.debug(f"{'Created' if is_new else 'Updated'} server: {name}")
            
            self._save_config()
            
            logger.info(f"Registry refresh completed - Created: {servers_created}, Updated: {servers_updated}, Total: {len(self.servers)}")
            logger.registry_operation("refresh_servers", servers_count=len(self.servers), success=True)
            
            return list(self.servers.values())
            
        except Exception as e:
            logger.error(f"Failed to refresh servers from registry: {e}")
            logger.registry_operation("refresh_servers", success=False, error=str(e))
            raise
    
    def get_server(self, name: str) -> Optional[MCPServer]:
        """Get server by name."""
        return self.servers.get(name)
    
    def get_all_servers(self) -> List[MCPServer]:
        """Get all servers."""
        return list(self.servers.values())
    
    def get_enabled_servers(self) -> List[MCPServer]:
        """Get all enabled servers."""
        return [server for server in self.servers.values() if server.enabled]

    def update_server_tools(self, server_name: str, enabled_tools: List[str]) -> bool:
        """Update enabled tools for a specific server"""
        if server_name not in self.servers:
            logger.error(f"Server {server_name} not found")
            return False

        server = self.servers[server_name]
        # Validate tools exist
        available_tool_names = [tool['name'] for tool in server.available_tools]
        for tool_name in enabled_tools:
            if tool_name not in available_tool_names:
                logger.warning(f"Tool {tool_name} not available for server {server_name}")
                return False

        server.enabled_tools = enabled_tools
        server.last_updated = datetime.now().isoformat()
        self._save_config()
        logger.info(f"Updated enabled tools for {server_name}: {enabled_tools}")
        return True

    def add_server(self, server_data: Dict[str, Any]) -> bool:
        """Manually add a new MCP server"""
        name = server_data.get('name')
        if not name:
            logger.error("Server name is required")
            return False

        if name in self.servers:
            logger.error(f"Server {name} already exists")
            return False

        server = MCPServer(
            name=name,
            url=server_data.get('url', ''),
            description=server_data.get('description', ''),
            tags=server_data.get('tags', []),
            enabled=server_data.get('enabled', True),
            available_tools=server_data.get('available_tools', [])
        )
        self.servers[name] = server
        self._save_config()
        logger.info(f"Added new server: {name}")
        return True

    def remove_server(self, server_name: str) -> bool:
        """Remove an MCP server"""
        if server_name not in self.servers:
            logger.error(f"Server {server_name} not found")
            return False

        del self.servers[server_name]
        self._save_config()
        logger.info(f"Removed server: {server_name}")
        return True

    def get_server_enabled_tools(self, server_name: str) -> List[str]:
        """Get enabled tools for a specific server"""
        server = self.get_server(server_name)
        if not server:
            return []
        return server.enabled_tools or []
    
    def enable_server(self, name: str) -> bool:
        """Enable a server."""
        logger.info(f"Enabling server: {name}")
        
        if name in self.servers:
            self.servers[name].enabled = True
            self._save_config()
            logger.server_operation("enable", name, success=True)
            return True
        else:
            logger.warning(f"Cannot enable server '{name}' - server not found")
            logger.server_operation("enable", name, success=False, details="Server not found")
            return False
    
    def disable_server(self, name: str) -> bool:
        """Disable a server."""
        logger.info(f"Disabling server: {name}")
        
        if name in self.servers:
            self.servers[name].enabled = False
            self._save_config()
            logger.server_operation("disable", name, success=True)
            return True
        else:
            logger.warning(f"Cannot disable server '{name}' - server not found")
            logger.server_operation("disable", name, success=False, details="Server not found")
            return False
    
    def get_server_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """Get tools for a specific server."""
        server = self.servers.get(server_name)
        if server:
            return server.available_tools
        return []
    
    def get_all_available_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all available tools from all enabled servers."""
        result = {}
        for server in self.get_enabled_servers():
            result[server.name] = server.available_tools
        return result