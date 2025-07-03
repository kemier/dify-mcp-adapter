"""
Fetch MCP Servers Tool - Retrieves available MCP servers from the registry
"""

import asyncio
import time
from typing import Any, Dict, List
from dify_plugin import Tool
from config.mcp_config import MCPConfig
from config.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)


class FetchMCPServersTool(Tool):
    """Tool to fetch MCP servers from the registry."""
    
    def get_runtime_parameters(self) -> List[Dict[str, Any]]:
        """Define the tool parameters."""
        return [
            {
                "name": "refresh_from_registry",
                "type": "boolean",
                "required": False,
                "label": {
                    "en_US": "Refresh from Registry",
                    "zh_Hans": "从注册表刷新"
                },
                "human_description": {
                    "en_US": "Whether to fetch fresh data from the registry or use cached data",
                    "zh_Hans": "是否从注册表获取新数据或使用缓存数据"
                },
                "form": "form"
            },
            {
                "name": "filter_enabled_only",
                "type": "boolean",
                "required": False,
                "label": {
                    "en_US": "Filter Enabled Only",
                    "zh_Hans": "仅筛选已启用"
                },
                "human_description": {
                    "en_US": "Only return enabled MCP servers",
                    "zh_Hans": "仅返回已启用的MCP服务器"
                },
                "form": "form"
            }
        ]
    
    def get_name(self) -> str:
        return "fetch_mcp_servers"
    
    def get_description(self) -> str:
        return "Fetch available MCP servers from the registry, with options to refresh from registry and filter by enabled status."
    
    def get_summary(self) -> str:
        return "Retrieves a list of available MCP servers from the registry with their details and available tools."
    
    def _invoke(self, user_id: str, tool_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool."""
        start_time = time.time()
        
        # Get parameters
        refresh_from_registry = tool_parameters.get("refresh_from_registry", False)
        filter_enabled_only = tool_parameters.get("filter_enabled_only", False)
        
        logger.info(f"Fetching MCP servers - User: {user_id}, Refresh: {refresh_from_registry}, Filter enabled: {filter_enabled_only}")
        
        try:
            # Initialize MCP config
            mcp_config = MCPConfig()
            
            # Run async operations
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                if refresh_from_registry:
                    # Refresh from registry
                    servers = loop.run_until_complete(mcp_config.refresh_servers_from_registry())
                else:
                    # Use cached data
                    servers = mcp_config.get_all_servers()
                
                # Filter if requested
                if filter_enabled_only:
                    servers = [s for s in servers if s.enabled]
                
                # Format response
                server_list = []
                for server in servers:
                    server_info = {
                        "name": server.name,
                        "url": server.url,
                        "description": server.description,
                        "enabled": server.enabled,
                        "tags": server.tags,
                        "last_updated": server.last_updated,
                        "available_tools": len(server.available_tools),
                        "tools_preview": [tool["name"] for tool in server.available_tools[:5]]  # First 5 tools
                    }
                    server_list.append(server_info)
                
                execution_time = time.time() - start_time
                enabled_count = len([s for s in servers if s.enabled])
                
                logger.tool_execution(
                    tool_name="fetch_mcp_servers",
                    server_name="registry",
                    user_id=user_id,
                    parameters=tool_parameters,
                    success=True,
                    execution_time=execution_time
                )
                
                logger.info(f"Successfully fetched {len(server_list)} servers ({enabled_count} enabled) in {execution_time:.3f}s")
                
                return {
                    "success": True,
                    "servers": server_list,
                    "total_servers": len(server_list),
                    "enabled_servers": enabled_count,
                    "refreshed_from_registry": refresh_from_registry,
                    "message": f"Successfully retrieved {len(server_list)} MCP servers"
                }
                
            finally:
                loop.close()
                
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            logger.tool_execution(
                tool_name="fetch_mcp_servers",
                server_name="registry",
                user_id=user_id,
                parameters=tool_parameters,
                success=False,
                execution_time=execution_time,
                error=error_msg
            )
            
            logger.error(f"Failed to fetch MCP servers: {error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "message": f"Failed to fetch MCP servers: {error_msg}"
            } 