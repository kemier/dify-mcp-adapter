"""
Manage MCP Dashboard Tool - Provides dashboard management functionality for MCP servers
"""

import asyncio
import time
from typing import Any, Dict, List
from dify_plugin import Tool
from config.mcp_config import MCPConfig
from config.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)


class ManageMCPDashboardTool(Tool):
    """Tool to manage MCP server dashboard operations."""
    
    def get_runtime_parameters(self) -> List[Dict[str, Any]]:
        """Define the tool parameters."""
        return [
            {
                "name": "action",
                "type": "select",
                "required": True,
                "options": [
                    {"label": {"en_US": "Get Status", "zh_Hans": "获取状态"}, "value": "get_status"},
                    {"label": {"en_US": "Enable Server", "zh_Hans": "启用服务器"}, "value": "enable_server"},
                    {"label": {"en_US": "Disable Server", "zh_Hans": "禁用服务器"}, "value": "disable_server"},
                    {"label": {"en_US": "Refresh Registry", "zh_Hans": "刷新注册表"}, "value": "refresh_registry"},
                    {"label": {"en_US": "Get Server Details", "zh_Hans": "获取服务器详情"}, "value": "get_server_details"},
                    {"label": {"en_US": "Get Analytics", "zh_Hans": "获取分析"}, "value": "get_analytics"}
                ],
                "label": {
                    "en_US": "Dashboard Action",
                    "zh_Hans": "仪表板操作"
                },
                "human_description": {
                    "en_US": "Select the dashboard management action to perform",
                    "zh_Hans": "选择要执行的仪表板管理操作"
                },
                "form": "form"
            },
            {
                "name": "server_name",
                "type": "string",
                "required": False,
                "label": {
                    "en_US": "Server Name",
                    "zh_Hans": "服务器名称"
                },
                "human_description": {
                    "en_US": "Name of the MCP server (required for server-specific actions)",
                    "zh_Hans": "MCP服务器名称（特定服务器操作需要）"
                },
                "form": "form"
            },
            {
                "name": "include_disabled",
                "type": "boolean",
                "required": False,
                "label": {
                    "en_US": "Include Disabled",
                    "zh_Hans": "包含已禁用"
                },
                "human_description": {
                    "en_US": "Include disabled servers in status and analytics",
                    "zh_Hans": "在状态和分析中包含已禁用的服务器"
                },
                "form": "form"
            }
        ]
    
    def get_name(self) -> str:
        return "manage_mcp_dashboard"
    
    def get_description(self) -> str:
        return "Manage MCP server dashboard operations including status monitoring, server management, and analytics."
    
    def get_summary(self) -> str:
        return "Provides comprehensive dashboard management for MCP servers with status monitoring and administration capabilities."
    
    def _get_status(self, mcp_config: MCPConfig, include_disabled: bool = False) -> Dict[str, Any]:
        """Get overall status of MCP servers."""
        all_servers = mcp_config.get_all_servers()
        enabled_servers = mcp_config.get_enabled_servers()
        
        servers_data = enabled_servers if not include_disabled else all_servers
        
        # Calculate statistics
        total_tools = sum(len(server.available_tools) for server in servers_data)
        server_stats = {}
        
        for server in servers_data:
            server_stats[server.name] = {
                "name": server.name,
                "enabled": server.enabled,
                "description": server.description,
                "tools_count": len(server.available_tools),
                "tags": server.tags,
                "last_updated": server.last_updated,
                "url": server.url
            }
        
        return {
            "total_servers": len(all_servers),
            "enabled_servers": len(enabled_servers),
            "disabled_servers": len(all_servers) - len(enabled_servers),
            "total_tools": total_tools,
            "servers": server_stats,
            "system_status": "healthy" if enabled_servers else "no_servers_enabled"
        }
    
    def _get_server_details(self, mcp_config: MCPConfig, server_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific server."""
        server = mcp_config.get_server(server_name)
        if not server:
            return {"error": f"Server '{server_name}' not found"}
        
        return {
            "name": server.name,
            "url": server.url,
            "enabled": server.enabled,
            "description": server.description,
            "tags": server.tags,
            "last_updated": server.last_updated,
            "tools": [
                {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {}),
                    "parameter_count": len(tool.get("parameters", {}).get("properties", {}))
                }
                for tool in server.available_tools
            ],
            "tools_count": len(server.available_tools),
            "status": "active" if server.enabled else "disabled"
        }
    
    def _get_analytics(self, mcp_config: MCPConfig, include_disabled: bool = False) -> Dict[str, Any]:
        """Get analytics data for MCP servers."""
        all_servers = mcp_config.get_all_servers()
        enabled_servers = mcp_config.get_enabled_servers()
        
        servers_data = enabled_servers if not include_disabled else all_servers
        
        # Tool analytics
        tool_categories = {}
        tools_by_server = {}
        most_common_tools = {}
        
        for server in servers_data:
            tools_by_server[server.name] = len(server.available_tools)
            
            for tool in server.available_tools:
                tool_name = tool["name"]
                if tool_name in most_common_tools:
                    most_common_tools[tool_name] += 1
                else:
                    most_common_tools[tool_name] = 1
        
        # Tag analytics
        tag_counts = {}
        for server in servers_data:
            for tag in server.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Sort by frequency
        top_tools = sorted(most_common_tools.items(), key=lambda x: x[1], reverse=True)[:10]
        popular_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "overview": {
                "total_servers": len(all_servers),
                "enabled_servers": len(enabled_servers),
                "total_tools": sum(len(server.available_tools) for server in servers_data),
                "unique_tools": len(most_common_tools),
                "total_tags": len(tag_counts)
            },
            "tools_by_server": tools_by_server,
            "top_tools": [{"name": tool, "server_count": count} for tool, count in top_tools],
            "popular_tags": [{"tag": tag, "server_count": count} for tag, count in popular_tags],
            "server_distribution": {
                "enabled": len(enabled_servers),
                "disabled": len(all_servers) - len(enabled_servers)
            }
        }
    
    def _invoke(self, user_id: str, tool_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the dashboard management tool."""
        start_time = time.time()
        
        # Get parameters
        action = tool_parameters.get("action")
        server_name = tool_parameters.get("server_name")
        include_disabled = tool_parameters.get("include_disabled", False)
        
        logger.info(f"Dashboard management - User: {user_id}, Action: {action}, Server: {server_name}, Include disabled: {include_disabled}")
        
        try:
            # Initialize MCP config
            mcp_config = MCPConfig()
            
            if not action:
                error_msg = "Action parameter is required"
                logger.warning(f"Dashboard management failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "message": "Please specify an action to perform"
                }
            
            # Execute action
            if action == "get_status":
                result = self._get_status(mcp_config, include_disabled)
                return {
                    "success": True,
                    "action": action,
                    "data": result,
                    "message": f"Retrieved status for {result['total_servers']} servers"
                }
            
            elif action == "enable_server":
                if not server_name:
                    return {
                        "success": False,
                        "error": "server_name is required for enable_server action",
                        "message": "Please specify a server name to enable"
                    }
                
                success = mcp_config.enable_server(server_name)
                if success:
                    return {
                        "success": True,
                        "action": action,
                        "server_name": server_name,
                        "message": f"Successfully enabled server '{server_name}'"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to enable server '{server_name}'",
                        "message": "Server not found or already enabled"
                    }
            
            elif action == "disable_server":
                if not server_name:
                    return {
                        "success": False,
                        "error": "server_name is required for disable_server action",
                        "message": "Please specify a server name to disable"
                    }
                
                success = mcp_config.disable_server(server_name)
                if success:
                    return {
                        "success": True,
                        "action": action,
                        "server_name": server_name,
                        "message": f"Successfully disabled server '{server_name}'"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to disable server '{server_name}'",
                        "message": "Server not found or already disabled"
                    }
            
            elif action == "refresh_registry":
                # Run async operation
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    servers = loop.run_until_complete(mcp_config.refresh_servers_from_registry())
                    return {
                        "success": True,
                        "action": action,
                        "servers_updated": len(servers),
                        "message": f"Successfully refreshed registry with {len(servers)} servers"
                    }
                finally:
                    loop.close()
            
            elif action == "get_server_details":
                if not server_name:
                    return {
                        "success": False,
                        "error": "server_name is required for get_server_details action",
                        "message": "Please specify a server name to get details for"
                    }
                
                details = self._get_server_details(mcp_config, server_name)
                if "error" in details:
                    return {
                        "success": False,
                        "error": details["error"],
                        "message": f"Could not get details for server '{server_name}'"
                    }
                
                return {
                    "success": True,
                    "action": action,
                    "server_name": server_name,
                    "data": details,
                    "message": f"Retrieved details for server '{server_name}'"
                }
            
            elif action == "get_analytics":
                analytics = self._get_analytics(mcp_config, include_disabled)
                return {
                    "success": True,
                    "action": action,
                    "data": analytics,
                    "message": f"Retrieved analytics for {analytics['overview']['total_servers']} servers"
                }
            
            else:
                error_msg = f"Unknown action: {action}"
                logger.warning(f"Dashboard management failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "message": "Please specify a valid action"
                }
                
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            logger.tool_execution(
                tool_name="manage_mcp_dashboard",
                server_name=server_name or "system",
                user_id=user_id,
                parameters=tool_parameters,
                success=False,
                execution_time=execution_time,
                error=error_msg
            )
            
            logger.error(f"Dashboard management failed: {error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "message": f"Dashboard management failed: {error_msg}"
            } 