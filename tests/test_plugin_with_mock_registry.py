#!/usr/bin/env python3
"""
Test script for Dify MCP Adapter Plugin with Mocked Registry
"""

import json
import asyncio
import sys
from pathlib import Path
from aiohttp import web
from unittest.mock import patch

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from demo import get_mock_registry_data, setup_mock_registry
from test_plugin import test_plugin

def test_with_mock_registry():
    # Create a new event loop just for server setup
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def async_setup():
        # Setup mock registry server
        app = setup_mock_registry()
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "localhost", 8080)
        await site.start()
        return runner
    
    try:
        # Run async setup
        runner = loop.run_until_complete(async_setup())
        
        # Patch registry URL to point to our mock server
        with patch('config.mcp_config.MCPConfig.set_registry_url', return_value="http://localhost:8080/api/mcp-servers"):
            # Run the test plugin with mock registry
            test_plugin(use_mock_registry=True)
    finally:
        # Clean up
        loop.run_until_complete(runner.cleanup())
        loop.close()

if __name__ == "__main__":
    test_with_mock_registry()