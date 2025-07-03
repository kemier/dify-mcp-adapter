#!/usr/bin/env python3
"""
Dify MCP Adapter Plugin - Main Entry Point
"""

import os
import sys
from pathlib import Path

# Add the current directory to the Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Initialize logging first
from config.logging_config import initialize_logging, get_logger

# Initialize the logging system
log_config = initialize_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_dir=os.getenv("LOG_DIR", "logs"),
    enable_console=os.getenv("ENABLE_CONSOLE_LOGGING", "true").lower() == "true"
)

# Get logger for main module
logger = get_logger(__name__)

from dify_plugin import DifyPlugin
from tools.fetch_mcp_servers import FetchMCPServersTool
from tools.fetch_tools_schema import FetchToolsSchemaTool
from tools.call_mcp_tool import CallMCPTool
from tools.manage_mcp_dashboard import ManageMCPDashboardTool
from endpoints.dashboard import DashboardEndpoint


def create_plugin():
    """Create and configure the MCP adapter plugin."""
    logger.info("Initializing MCP Adapter Plugin")
    
    try:
        plugin = DifyPlugin(
            name="mcp-adapter",
            version="0.0.1"
        )
        
        logger.info("Plugin instance created successfully")
        
        # Register tools
        logger.info("Registering plugin tools")
        plugin.register_tool(FetchMCPServersTool())
        plugin.register_tool(FetchToolsSchemaTool())
        plugin.register_tool(CallMCPTool())
        plugin.register_tool(ManageMCPDashboardTool())
        logger.info("All tools registered successfully")
        
        # Register endpoints
        logger.info("Registering plugin endpoints")
        plugin.register_endpoint(DashboardEndpoint())
        logger.info("All endpoints registered successfully")
        
        logger.info("MCP Adapter Plugin initialization completed")
        return plugin
        
    except Exception as e:
        logger.error(f"Failed to create plugin: {str(e)}")
        raise


def main():
    """Main entry point for the plugin."""
    logger.info("Starting MCP Adapter Plugin")
    
    try:
        # Configuration
        host = os.getenv("PLUGIN_HOST", "0.0.0.0")
        port = int(os.getenv("PLUGIN_PORT", "5000"))
        debug = os.getenv("PLUGIN_DEBUG", "false").lower() == "true"
        
        logger.info(f"Plugin configuration - Host: {host}, Port: {port}, Debug: {debug}")
        
        # Create plugin
        plugin = create_plugin()
        
        # Start the plugin server
        logger.info(f"Starting plugin server on {host}:{port}")
        plugin.run(host=host, port=port, debug=debug)
        
    except KeyboardInterrupt:
        logger.info("Plugin shutdown requested by user")
    except Exception as e:
        logger.error(f"Plugin failed to start: {str(e)}")
        raise
    finally:
        logger.info("Plugin shutdown completed")


if __name__ == "__main__":
    main() 