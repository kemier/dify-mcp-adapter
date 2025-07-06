#!/usr/bin/env python3
"""
Test script for Dify MCP Adapter Plugin
"""

import json
import asyncio
from tools.fetch_mcp_servers import FetchMCPServersTool
from tools.fetch_tools_schema import FetchToolsSchemaTool
from tools.call_mcp_tool import CallMCPTool
from tools.manage_mcp_dashboard import ManageMCPDashboardTool


def test_plugin(use_mock_registry: bool = False):
    """Test the plugin tools individually.
    
    Args:
        use_mock_registry: If True, uses mock registry data instead of real one
    """
    
    print("🧪 Testing Dify MCP Adapter Plugin\n")
    
    if use_mock_registry:
        print("🔧 Using mock registry data\n")
    
    # Test 1: Fetch MCP Servers
    print("1️⃣ Testing Fetch MCP Servers Tool")
    fetch_tool = FetchMCPServersTool()
    
    # Use mock registry if requested
    refresh_from_registry = not use_mock_registry
    
    servers = fetch_tool._invoke("test_user", {
        "refresh_from_registry": refresh_from_registry,
        "filter_enabled_only": True
    })
    print(f"   Result: {servers['success']}")
    if servers['success'] and 'servers' in servers:
        print(f"   Found {len(servers['servers'])} servers")
        for server in servers['servers']:
            print(f"   - {server['name']}: {server['description']}")
    print()
    
    # Test 2: Get Tools Schema
    print("2️⃣ Testing Fetch Tools Schema")
    schema_tool = FetchToolsSchemaTool()
    schema = schema_tool._invoke("test_user", {
        "server_name": "github-mcp",
        "include_examples": True
    })
    print(f"   Result: {schema['success']}")
    if schema['success']:
        tools = schema['schema']['servers']['github-mcp']['tools']
        print(f"   Found {len(tools)} tools for github-mcp:")
        for tool in tools[:3]:  # Show first 3 tools
            print(f"   - {tool['name']}: {tool['description']}")
    print()
    
    # Test 3: Dashboard Analytics
    print("3️⃣ Testing Dashboard Analytics")
    dashboard_tool = ManageMCPDashboardTool()
    analytics = dashboard_tool._invoke("test_user", {
        "action": "get_analytics"
    })
    print(f"   Result: {analytics['success']}")
    if analytics['success'] and 'data' in analytics:
        overview = analytics['data']['overview']
        print(f"   System Overview:")
        print(f"   - Total Servers: {overview['total_servers']}")
        print(f"   - Enabled Servers: {overview['enabled_servers']}")
        print(f"   - Total Tools: {overview['total_tools']}")
    print()
    
    # Test 4: Simulate Tool Call
    print("4️⃣ Testing Tool Execution (Mock)")
    call_tool = CallMCPTool()
    
    # Example: Create GitHub issue
    tool_args = {
        "repository": "test-org/test-repo",
        "title": "Test Issue from MCP Adapter",
        "body": "This is a test issue created via MCP adapter",
        "labels": ["test", "mcp-adapter"]
    }
    
    # Run tool execution synchronously
    result = call_tool._invoke("test_user", {
        "server_name": "github-mcp",
        "tool_name": "create_issue",
        "arguments": json.dumps(tool_args),
        "validate_args": True
    })
    print(f"   Result: {result['success']}")
    if result['success']:
        print(f"   Response: {result.get('data', 'Success')}")
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")
    
    print("\n✅ Plugin testing completed!")
    print("\n📝 Next Steps:")
    print("1. Install this plugin in your Dify instance")
    print("2. Configure MCP registry URL in Dify settings")
    print("3. Create an agent that uses these tools")
    print("4. Test with real MCP servers")


if __name__ == "__main__":
    test_plugin()