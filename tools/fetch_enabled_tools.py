"""
Fetch Tools Schema Tool - Retrieves schema information for tools from MCP servers
"""

import time
from typing import Any, Dict, List
from dify_plugin import Tool
from config.mcp_config import MCPConfig
from config.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)


class FetchEnabledToolsTool(Tool):
    """Tool to fetch available tools schema from MCP servers."""
    
    def get_runtime_parameters(self) -> List[Dict[str, Any]]:
        """Define the tool parameters."""
        return [
            {
                "name": "server_name",
                "type": "string",
                "required": False,
                "label": {
                    "en_US": "Server Name",
                    "zh_Hans": "服务器名称"
                },
                "human_description": {
                    "en_US": "Name of specific MCP server to get tools from. If not provided, returns tools from all enabled servers.",
                    "zh_Hans": "要获取工具的特定MCP服务器名称。如果未提供，则返回所有已启用服务器的工具。"
                },
                "form": "form"
            },
            {
                "name": "include_disabled",
                "type": "boolean",
                "required": False,
                "default": False,
                "label": {
                    "en_US": "Include Disabled",
                    "zh_Hans": "包含已禁用"
                },
                "human_description": {
                    "en_US": "Whether to include disabled tools in the response",
                    "zh_Hans": "是否在响应中包含已禁用的工具"
                },
                "form": "form"
            }
        ]
    
    def get_name(self) -> str:
        return "fetch_enabled_tools"
    
    def get_description(self) -> str:
        return "Fetch schema information for user-enabled tools across all MCP servers. Used by LLMs to understand available tools."
    
    def get_summary(self) -> str:
        return "Retrieve the JSON schema for enabled tools on MCP servers, including parameters and descriptions."
    
    def _generate_tool_examples(self, tool_name: str, server_name: str) -> Dict[str, Any]:
        """Generate usage examples for tools."""
        examples = {
            "create_issue": {
                "description": "Create a new issue in a GitHub repository",
                "example_parameters": {
                    "repository": "owner/repo-name",
                    "title": "Bug: Application crashes on startup",
                    "body": "The application crashes when starting up with the following error...",
                    "labels": ["bug", "high-priority"]
                }
            },
            "send_message": {
                "description": "Send a message to a Slack channel",
                "example_parameters": {
                    "channel": "#general",
                    "message": "Hello team! The deployment was successful.",
                    "thread_ts": None
                }
            },
            "execute_query": {
                "description": "Execute a SQL query on the database",
                "example_parameters": {
                    "query": "SELECT * FROM users WHERE active = true LIMIT 10",
                    "database": "production"
                }
            }
        }
        
        return examples.get(tool_name, {
            "description": f"Execute {tool_name} on {server_name}",
            "example_parameters": {}
        })
    
    def _invoke(self, user_id: str, tool_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool."""
        start_time = time.time()
        
        # Get parameters
        server_name = tool_parameters.get("server_name")
        include_disabled = tool_parameters.get("include_disabled", False)
        
        logger.info(f"Fetching tools schema - User: {user_id}, Server: {server_name}, Tool: {tool_name}, Examples: {include_examples}")
        
        try:
            # Initialize MCP config
            mcp_config = MCPConfig()
            
            # Get tools data
            if server_name:
                # Get tools from specific server
                if server_name not in [s.name for s in mcp_config.get_all_servers()]:
                    return {
                        "success": False,
                        "error": f"Server '{server_name}' not found",
                        "message": f"MCP server '{server_name}' is not available"
                    }
                
                tools_data = {server_name: mcp_config.get_server_tools(server_name)}
            else:
                # Get tools from all enabled servers
                tools_data = mcp_config.get_all_available_tools()

        except Exception as e:
            logger.error(f"Error filtering tools: {str(e)}")
            return {"success": False, "error": str(e)}
                    
            # Filter by specific tool if requested
            # Filter out disabled tools unless requested
        try:
            filtered_tools_data = {}
            for server_name, tools in tools_data.items():
                server = mcp_config.get_server(server_name)
                if not server and not include_disabled:
                    continue
                 
                enabled_tools = [tool for tool in tools if tool["name"] in server.enabled_tools]
                if include_disabled:
                    # Add disabled tools with flag
                    for tool in tools:
                        if tool["name"] not in server.enabled_tools:
                            tool["enabled"] = False
                            enabled_tools.append(tool)
                filtered_tools_data[server_name] = enabled_tools
            tools_data = filtered_tools_data
            
            # Format schema response
            schema_response = {
                "servers": {},
                "total_tools": 0,
                "available_servers": list(tools_data.keys())
            }
            
            for server, tools in tools_data.items():
                server_info = mcp_config.get_server(server)
                schema_response["servers"][server] = {
                    "server_info": {
                        "name": server,
                        "description": server_info.description if server_info else "",
                        "enabled": server_info.enabled if server_info else False,
                        "url": server_info.url if server_info else ""
                    },
                    "tools": []
                }
                
                for tool in tools:
                    tool_schema = {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters", {}),
                        "server": server,
                        "full_name": f"{server}.{tool['name']}"  # For unique identification
                    }
                    
                    # Add enabled status
                    tool_schema["enabled"] = tool["name"] in server.enabled_tools
                    
                    schema_response["servers"][server]["tools"].append(tool_schema)
                    schema_response["total_tools"] += 1
            
            execution_time = time.time() - start_time
            
            logger.tool_execution(
                tool_name="fetch_tools_schema",
                server_name=server_name or "all",
                user_id=user_id,
                parameters=tool_parameters,
                success=True,
                execution_time=execution_time
            )
            
            logger.info(f"Successfully fetched schema for {schema_response['total_tools']} tools from {len(schema_response['available_servers'])} servers in {execution_time:.3f}s")
            
            return {
                "success": True,
                "schema": schema_response,
                "query_params": {
                    "server_name": server_name,
                    "tool_name": tool_name,
                    "include_examples": include_examples
                },
                "message": f"Successfully retrieved schema for {schema_response['total_tools']} tools from {len(schema_response['available_servers'])} servers"
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            logger.tool_execution(
                tool_name="fetch_tools_schema",
                server_name=server_name or "all",
                user_id=user_id,
                parameters=tool_parameters,
                success=False,
                execution_time=execution_time,
                error=error_msg
            )
            
            logger.error(f"Failed to fetch tools schema: {error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "message": f"Failed to fetch tools schema: {error_msg}"
            }