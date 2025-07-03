#!/usr/bin/env python3
"""
Demo script for the Dify MCP Adapter Plugin
This demonstrates how the plugin would be used with LLMs and agents.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from tools.fetch_mcp_servers import FetchMCPServersTool
from tools.fetch_tools_schema import FetchToolsSchemaTool
from tools.call_mcp_tool import CallMCPTool
from tools.manage_mcp_dashboard import ManageMCPDashboardTool


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🔧 {title}")
    print(f"{'='*60}")


def print_json(data, title: str = "Response"):
    """Pretty print JSON data."""
    print(f"\n📄 {title}:")
    print(json.dumps(data, indent=2))


async def demo_agent_workflow():
    """Demonstrate a typical agent workflow using the MCP adapter."""
    
    print("🤖 MCP Adapter Plugin - Agent Workflow Demo")
    print("This demonstrates how an LLM agent would use the MCP adapter.")
    
    # Initialize tools
    fetch_servers_tool = FetchMCPServersTool()
    fetch_schema_tool = FetchToolsSchemaTool()
    call_tool = CallMCPTool()
    dashboard_tool = ManageMCPDashboardTool()
    
    # Step 1: Agent discovers available MCP servers
    print_header("Step 1: Discover Available MCP Servers")
    print("🤖 Agent: I need to see what MCP servers are available.")
    
    servers_result = fetch_servers_tool._invoke("agent_user", {
        "refresh_from_registry": True,
        "filter_enabled_only": True
    })
    
    print_json(servers_result, "Available MCP Servers")
    
    if not servers_result["success"]:
        print("❌ Failed to fetch servers. Stopping demo.")
        return
    
    # Step 2: Agent gets schema for specific tools
    print_header("Step 2: Get Tools Schema")
    print("🤖 Agent: Let me see what tools are available on the GitHub MCP server.")
    
    schema_result = fetch_schema_tool._invoke("agent_user", {
        "server_name": "github-mcp",
        "include_examples": True
    })
    
    print_json(schema_result, "GitHub MCP Tools Schema")
    
    # Step 3: Agent uses a tool to accomplish a task
    print_header("Step 3: Execute a Tool")
    print("🤖 Agent: I'll create a GitHub issue using the create_issue tool.")
    
    tool_args = {
        "repository": "myorg/myproject",
        "title": "Implement new feature: AI-powered code review",
        "body": "We should implement an AI-powered code review system to help developers...",
        "labels": ["enhancement", "ai"]
    }
    
    execution_result = call_tool._invoke("agent_user", {
        "server_name": "github-mcp",
        "tool_name": "create_issue",
        "arguments": json.dumps(tool_args),
        "validate_args": True
    })
    
    print_json(execution_result, "Tool Execution Result")
    
    # Step 4: Agent checks dashboard status
    print_header("Step 4: Check System Status")
    print("🤖 Agent: Let me check the overall status of MCP servers.")
    
    status_result = dashboard_tool._invoke("agent_user", {
        "action": "get_status",
        "include_disabled": False
    })
    
    print_json(status_result, "System Status")
    
    # Step 5: Demonstrate analytics
    print_header("Step 5: Get Analytics")
    print("🤖 Agent: I'll get analytics about tool usage.")
    
    analytics_result = dashboard_tool._invoke("agent_user", {
        "action": "get_analytics"
    })
    
    print_json(analytics_result, "Analytics Data")
    
    print_header("Demo Complete")
    print("✅ Successfully demonstrated MCP adapter workflow!")
    print("\n🔍 Key Features Demonstrated:")
    print("  - Dynamic server discovery from registry")
    print("  - Tool schema retrieval for LLM understanding")
    print("  - Validated tool execution with real arguments")
    print("  - Dashboard management and analytics")
    print("  - Error handling and response formatting")


def demo_user_scenarios():
    """Demonstrate specific user scenarios."""
    
    print_header("User Scenario Demonstrations")
    
    # Scenario 1: Developer wants to integrate GitHub
    print("\n📋 Scenario 1: Developer Setting Up GitHub Integration")
    print("A developer wants to enable their agent to create GitHub issues.")
    
    dashboard_tool = ManageMCPDashboardTool()
    
    # Check if github-mcp is enabled
    details_result = dashboard_tool._invoke("dev_user", {
        "action": "get_server_details",
        "server_name": "github-mcp"
    })
    
    if details_result["success"]:
        print("✅ GitHub MCP server is available!")
        print(f"   - {details_result['data']['tools_count']} tools available")
        print(f"   - Status: {'Enabled' if details_result['data']['enabled'] else 'Disabled'}")
    
    # Scenario 2: Data analyst wants to query databases
    print("\n📊 Scenario 2: Data Analyst Database Access")
    print("A data analyst wants to query production databases safely.")
    
    schema_tool = FetchToolsSchemaTool()
    db_schema = schema_tool._invoke("analyst_user", {
        "server_name": "database-mcp",
        "tool_name": "execute_query",
        "include_examples": True
    })
    
    if db_schema["success"]:
        tools = db_schema["schema"]["servers"]["database-mcp"]["tools"]
        print(f"✅ Found {len(tools)} database tools available")
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description']}")
    
    # Scenario 3: Team lead managing server configuration
    print("\n👥 Scenario 3: Team Lead Server Management")
    print("A team lead wants to see overall system health and configure servers.")
    
    analytics_result = dashboard_tool._invoke("team_lead", {
        "action": "get_analytics"
    })
    
    if analytics_result["success"]:
        overview = analytics_result["data"]["overview"]
        print(f"✅ System Overview:")
        print(f"   - Total Servers: {overview['total_servers']}")
        print(f"   - Enabled Servers: {overview['enabled_servers']}")
        print(f"   - Total Tools: {overview['total_tools']}")
        print(f"   - Unique Tools: {overview['unique_tools']}")


def main():
    """Run the complete demo."""
    print("🎯 Starting Dify MCP Adapter Plugin Demo")
    print("This demo shows how the plugin enables dynamic MCP server management.")
    
    try:
        # Run the async demo
        asyncio.run(demo_agent_workflow())
        
        # Run user scenarios
        demo_user_scenarios()
        
        print_header("Dashboard Information")
        print("🌐 Web Dashboard: http://localhost:5000/dashboard")
        print("📚 Features:")
        print("  - Visual server management interface")
        print("  - Real-time server status monitoring")
        print("  - Tool discovery and configuration")
        print("  - Analytics and usage metrics")
        print("  - Server enable/disable controls")
        print("  - Registry refresh functionality")
        
        print_header("Integration with Dify")
        print("🔌 Plugin Integration:")
        print("  1. Install plugin in Dify platform")
        print("  2. Configure MCP registry endpoint")
        print("  3. Enable desired MCP servers")
        print("  4. Agents can now discover and use tools dynamically")
        print("  5. Monitor usage through the dashboard")
        
        print("\n🎉 Demo completed successfully!")
        print("The MCP adapter plugin is ready for production use.")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 