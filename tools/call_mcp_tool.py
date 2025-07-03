"""
Call MCP Tool - Executes tools on MCP servers with LLM-provided arguments
"""

import json
import asyncio
import time
from typing import Any, Dict, List
from dify_plugin import Tool
from config.mcp_config import MCPConfig
from config.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)


class MCPToolExecutor:
    """Handles execution of MCP server tools."""
    
    def __init__(self):
        self.mcp_config = MCPConfig()
    
    async def execute_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool on an MCP server."""
        logger.debug(f"Executing tool '{tool_name}' on server '{server_name}' with arguments: {arguments}")
        
        try:
            # Get server info
            server = self.mcp_config.get_server(server_name)
            if not server:
                error_msg = f"Server '{server_name}' not found"
                logger.warning(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
            
            if not server.enabled:
                error_msg = f"Server '{server_name}' is disabled"
                logger.warning(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
            
            # Check if tool exists
            tool_exists = any(tool["name"] == tool_name for tool in server.available_tools)
            if not tool_exists:
                error_msg = f"Tool '{tool_name}' not found on server '{server_name}'"
                logger.warning(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
            
            logger.info(f"Executing tool '{tool_name}' on server '{server_name}'")
            
            # Mock execution for development - in production this would call the actual MCP server
            result = await self._mock_tool_execution(server_name, tool_name, arguments)
            
            logger.debug(f"Tool execution successful: {tool_name} on {server_name}")
            
            return {
                "success": True,
                "result": result,
                "server": server_name,
                "tool": tool_name,
                "arguments_used": arguments
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Tool execution failed: {tool_name} on {server_name} - {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "server": server_name,
                "tool": tool_name
            }
    
    async def _mock_tool_execution(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Mock tool execution for development purposes."""
        # Simulate different types of tool responses based on tool names
        
        if tool_name == "create_issue":
            return {
                "issue_id": 12345,
                "issue_url": f"https://github.com/{arguments.get('repository', 'owner/repo')}/issues/12345",
                "title": arguments.get("title", ""),
                "status": "open",
                "created_at": "2024-01-15T10:30:00Z"
            }
        
        elif tool_name == "send_message":
            return {
                "message_id": "1234567890.123456",
                "channel": arguments.get("channel", "#general"),
                "timestamp": "2024-01-15T10:30:00Z",
                "status": "sent"
            }
        
        elif tool_name == "execute_query":
            return {
                "rows_affected": 3,
                "execution_time": "0.045s",
                "result": [
                    {"id": 1, "name": "John Doe", "active": True},
                    {"id": 2, "name": "Jane Smith", "active": True},
                    {"id": 3, "name": "Bob Johnson", "active": True}
                ]
            }
        
        elif tool_name == "get_repository":
            return {
                "name": arguments.get("repository", "example-repo"),
                "full_name": f"owner/{arguments.get('repository', 'example-repo')}",
                "description": "Example repository",
                "stars": 42,
                "forks": 7,
                "language": "Python"
            }
        
        elif tool_name == "search_code":
            return {
                "total_count": 15,
                "results": [
                    {"file": "src/main.py", "line": 25, "match": "def main():"},
                    {"file": "src/utils.py", "line": 12, "match": "import main"},
                    {"file": "tests/test_main.py", "line": 5, "match": "from main import"}
                ]
            }
        
        else:
            # Generic response for unknown tools
            return {
                "status": "executed",
                "tool": tool_name,
                "server": server_name,
                "arguments": arguments,
                "execution_time": "0.123s",
                "message": f"Tool '{tool_name}' executed successfully on '{server_name}'"
            }


class CallMCPTool(Tool):
    """Tool to call MCP server tools with LLM-provided arguments."""
    
    def __init__(self):
        super().__init__()
        self.executor = MCPToolExecutor()
    
    def get_runtime_parameters(self) -> List[Dict[str, Any]]:
        """Define the tool parameters."""
        return [
            {
                "name": "server_name",
                "type": "string",
                "required": True,
                "label": {
                    "en_US": "Server Name",
                    "zh_Hans": "服务器名称"
                },
                "human_description": {
                    "en_US": "Name of the MCP server to call the tool on",
                    "zh_Hans": "要调用工具的MCP服务器名称"
                },
                "form": "form"
            },
            {
                "name": "tool_name",
                "type": "string",
                "required": True,
                "label": {
                    "en_US": "Tool Name",
                    "zh_Hans": "工具名称"
                },
                "human_description": {
                    "en_US": "Name of the tool to execute on the MCP server",
                    "zh_Hans": "要在MCP服务器上执行的工具名称"
                },
                "form": "form"
            },
            {
                "name": "arguments",
                "type": "string",
                "required": False,
                "label": {
                    "en_US": "Tool Arguments",
                    "zh_Hans": "工具参数"
                },
                "human_description": {
                    "en_US": "JSON string of arguments to pass to the tool. Must match the tool's schema.",
                    "zh_Hans": "传递给工具的参数的JSON字符串。必须符合工具的架构。"
                },
                "form": "form"
            },
            {
                "name": "validate_args",
                "type": "boolean",
                "required": False,
                "label": {
                    "en_US": "Validate Arguments",
                    "zh_Hans": "验证参数"
                },
                "human_description": {
                    "en_US": "Whether to validate arguments against tool schema before execution",
                    "zh_Hans": "是否在执行前根据工具架构验证参数"
                },
                "form": "form"
            }
        ]
    
    def get_name(self) -> str:
        return "call_mcp_tool"
    
    def get_description(self) -> str:
        return "Execute a tool on an MCP server with provided arguments. LLMs can use this to interact with external services through MCP servers."
    
    def get_summary(self) -> str:
        return "Calls a specific tool on an MCP server with the provided arguments and returns the execution result."
    
    def _validate_arguments(self, arguments: Dict[str, Any], tool_schema: Dict[str, Any]) -> tuple[bool, str]:
        """Validate arguments against tool schema."""
        try:
            # Basic validation - in production this would be more comprehensive
            parameters = tool_schema.get("parameters", {})
            properties = parameters.get("properties", {})
            required = parameters.get("required", [])
            
            # Check required parameters
            for req_param in required:
                if req_param not in arguments:
                    return False, f"Missing required parameter: {req_param}"
            
            # Basic type checking
            for param_name, param_value in arguments.items():
                if param_name in properties:
                    expected_type = properties[param_name].get("type")
                    if expected_type == "string" and not isinstance(param_value, str):
                        return False, f"Parameter '{param_name}' must be a string"
                    elif expected_type == "number" and not isinstance(param_value, (int, float)):
                        return False, f"Parameter '{param_name}' must be a number"
                    elif expected_type == "boolean" and not isinstance(param_value, bool):
                        return False, f"Parameter '{param_name}' must be a boolean"
                    elif expected_type == "array" and not isinstance(param_value, list):
                        return False, f"Parameter '{param_name}' must be an array"
                    elif expected_type == "object" and not isinstance(param_value, dict):
                        return False, f"Parameter '{param_name}' must be an object"
            
            return True, ""
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def _invoke(self, user_id: str, tool_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool."""
        start_time = time.time()
        
        # Get parameters
        server_name = tool_parameters.get("server_name")
        tool_name = tool_parameters.get("tool_name")
        arguments_str = tool_parameters.get("arguments", "{}")
        validate_args = tool_parameters.get("validate_args", True)
        
        logger.info(f"Calling MCP tool - User: {user_id}, Server: {server_name}, Tool: {tool_name}, Validate: {validate_args}")
        
        try:
            if not server_name or not tool_name:
                error_msg = "server_name and tool_name are required"
                logger.warning(f"Tool call failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "message": "Both server_name and tool_name must be provided"
                }
            
            # Parse arguments
            try:
                arguments = json.loads(arguments_str) if arguments_str else {}
                logger.debug(f"Parsed arguments: {arguments}")
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON in arguments: {str(e)}"
                logger.warning(f"JSON parsing failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "message": "Arguments must be valid JSON"
                }
            
            # Validate arguments if requested
            if validate_args:
                logger.debug("Validating arguments against tool schema")
                mcp_config = MCPConfig()
                server = mcp_config.get_server(server_name)
                if server:
                    tool_schema = None
                    for tool in server.available_tools:
                        if tool["name"] == tool_name:
                            tool_schema = tool
                            break
                    
                    if tool_schema:
                        is_valid, error_msg = self._validate_arguments(arguments, tool_schema)
                        if not is_valid:
                            logger.warning(f"Argument validation failed: {error_msg}")
                            return {
                                "success": False,
                                "error": f"Argument validation failed: {error_msg}",
                                "message": "Please check your arguments against the tool schema"
                            }
                        else:
                            logger.debug("Arguments validated successfully")
                    else:
                        logger.warning(f"Tool schema not found for '{tool_name}' on server '{server_name}'")
            
            # Execute the tool
            logger.info(f"Executing tool '{tool_name}' on server '{server_name}'")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.executor.execute_tool(server_name, tool_name, arguments)
                )
                
                execution_time = time.time() - start_time
                
                if result["success"]:
                    logger.tool_execution(
                        tool_name=tool_name,
                        server_name=server_name,
                        user_id=user_id,
                        parameters=tool_parameters,
                        success=True,
                        execution_time=execution_time
                    )
                    
                    logger.info(f"Tool execution successful: {tool_name} on {server_name} in {execution_time:.3f}s")
                    
                    return {
                        "success": True,
                        "execution_result": result["result"],
                        "server": server_name,
                        "tool": tool_name,
                        "arguments_used": arguments,
                        "message": f"Successfully executed {tool_name} on {server_name}"
                    }
                else:
                    logger.tool_execution(
                        tool_name=tool_name,
                        server_name=server_name,
                        user_id=user_id,
                        parameters=tool_parameters,
                        success=False,
                        execution_time=execution_time,
                        error=result["error"]
                    )
                    
                    logger.error(f"Tool execution failed: {tool_name} on {server_name} - {result['error']}")
                    
                    return {
                        "success": False,
                        "error": result["error"],
                        "server": server_name,
                        "tool": tool_name,
                        "message": f"Failed to execute {tool_name} on {server_name}"
                    }
                    
            finally:
                loop.close()
                
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            logger.tool_execution(
                tool_name=tool_name or "unknown",
                server_name=server_name or "unknown",
                user_id=user_id,
                parameters=tool_parameters,
                success=False,
                execution_time=execution_time,
                error=error_msg
            )
            
            logger.error(f"Unexpected error while executing tool: {error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "message": f"Unexpected error while executing tool: {error_msg}"
            } 