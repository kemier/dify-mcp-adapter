"""
Mock Dify Plugin Framework for Development
This is a simplified mock implementation for development purposes.
In production, this would be provided by the actual Dify plugin framework.
"""

from typing import Any, Dict, List


class Tool:
    """Base class for Dify plugin tools."""
    
    def get_name(self) -> str:
        """Get the tool name."""
        raise NotImplementedError("Subclasses must implement get_name()")
    
    def get_description(self) -> str:
        """Get the tool description."""
        raise NotImplementedError("Subclasses must implement get_description()")
    
    def get_summary(self) -> str:
        """Get the tool summary."""
        return self.get_description()
    
    def get_runtime_parameters(self) -> List[Dict[str, Any]]:
        """Get the runtime parameters for the tool."""
        return []
    
    def _invoke(self, user_id: str, tool_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _invoke()")


class Endpoint:
    """Base class for Dify plugin endpoints."""
    
    def get_name(self) -> str:
        """Get the endpoint name."""
        raise NotImplementedError("Subclasses must implement get_name()")
    
    def get_path(self) -> str:
        """Get the endpoint path."""
        raise NotImplementedError("Subclasses must implement get_path()")
    
    def get_description(self) -> str:
        """Get the endpoint description."""
        return f"Endpoint: {self.get_name()}"
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming requests. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement handle_request()")


class DifyPlugin:
    """Main Dify plugin class."""
    
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.tools = []
        self.endpoints = []
    
    def register_tool(self, tool: Tool):
        """Register a tool with the plugin."""
        self.tools.append(tool)
        print(f"📝 Registered tool: {tool.get_name()}")
    
    def register_endpoint(self, endpoint: Endpoint):
        """Register an endpoint with the plugin."""
        self.endpoints.append(endpoint)
        print(f"🌐 Registered endpoint: {endpoint.get_name()} at {endpoint.get_path()}")
    
    def run(self, host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
        """Run the plugin server (mock implementation)."""
        print(f"🚀 Starting {self.name} v{self.version}")
        print(f"🔧 Registered {len(self.tools)} tools:")
        for tool in self.tools:
            print(f"   - {tool.get_name()}: {tool.get_description()}")
        
        print(f"🌐 Registered {len(self.endpoints)} endpoints:")
        for endpoint in self.endpoints:
            print(f"   - {endpoint.get_name()}: http://{host}:{port}{endpoint.get_path()}")
        
        print(f"🎯 Plugin would be running on http://{host}:{port}")
        print("💡 This is a mock implementation for development purposes.")
        print("   In production, the actual Dify plugin framework would handle the server.")
        
        # In a real implementation, this would start an actual web server
        # For development purposes, we just print the information
        return True 