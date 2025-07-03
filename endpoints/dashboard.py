"""
Dashboard Endpoint - Web interface for MCP server management
"""

import json
import asyncio
import time
from typing import Any, Dict
from dify_plugin import Endpoint
from config.mcp_config import MCPConfig
from config.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)


class DashboardEndpoint(Endpoint):
    """Web dashboard endpoint for MCP server management."""
    
    def get_name(self) -> str:
        return "dashboard"
    
    def get_path(self) -> str:
        return "/dashboard"
    
    def get_description(self) -> str:
        return "Web dashboard for managing MCP servers, viewing analytics, and configuring tools."
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle dashboard requests."""
        start_time = time.time()
        method = request.get("method", "GET")
        path = request.get("path", "")
        user_agent = request.get("headers", {}).get("User-Agent", "Unknown")
        
        logger.info(f"Dashboard request - Method: {method}, Path: {path}, User-Agent: {user_agent}")
        
        mcp_config = MCPConfig()
        
        if method == "GET" and path == "/dashboard":
            # Return simple dashboard HTML
            all_servers = mcp_config.get_all_servers()
            enabled_servers = mcp_config.get_enabled_servers()
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>MCP Server Dashboard</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    .header {{ background: white; padding: 30px; border-radius: 8px; margin-bottom: 20px; }}
                    .stats {{ display: flex; gap: 20px; margin-bottom: 20px; }}
                    .stat-card {{ background: white; padding: 20px; border-radius: 8px; text-align: center; flex: 1; }}
                    .stat-number {{ font-size: 2em; font-weight: bold; color: #3498db; }}
                    .servers-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
                    .server-card {{ background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #ddd; }}
                    .server-card.enabled {{ border-left-color: #27ae60; }}
                    .server-card.disabled {{ border-left-color: #e74c3c; opacity: 0.7; }}
                    .status-badge {{ padding: 5px 10px; border-radius: 15px; font-size: 0.8em; font-weight: bold; }}
                    .status-badge.enabled {{ background: #d5f4e6; color: #27ae60; }}
                    .status-badge.disabled {{ background: #fce4ec; color: #e74c3c; }}
                    .btn {{ padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }}
                    .btn-primary {{ background: #3498db; color: white; }}
                    .btn-success {{ background: #27ae60; color: white; }}
                    .btn-danger {{ background: #e74c3c; color: white; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔌 MCP Server Dashboard</h1>
                        <p>Manage your Model Context Protocol servers and tools</p>
                    </div>
                    
                    <div class="stats">
                        <div class="stat-card">
                            <div class="stat-number">{len(all_servers)}</div>
                            <div>Total Servers</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{len(enabled_servers)}</div>
                            <div>Enabled</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{len(all_servers) - len(enabled_servers)}</div>
                            <div>Disabled</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{sum(len(server.available_tools) for server in enabled_servers)}</div>
                            <div>Available Tools</div>
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <button class="btn btn-primary" onclick="refreshRegistry()">🔄 Refresh Registry</button>
                        <button class="btn btn-primary" onclick="viewAnalytics()">📊 Analytics</button>
                    </div>
                    
                    <div class="servers-grid">
            """
            
            # Add server cards
            for server in all_servers:
                status_class = "enabled" if server.enabled else "disabled"
                status_text = "Enabled" if server.enabled else "Disabled"
                
                html_content += f"""
                        <div class="server-card {status_class}">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                <h3>{server.name}</h3>
                                <span class="status-badge {status_class}">{status_text}</span>
                            </div>
                            <p style="color: #666; margin-bottom: 15px;">{server.description}</p>
                            <div style="margin-bottom: 15px;">
                                <span style="margin-right: 15px;">🔧 {len(server.available_tools)} tools</span>
                                <span>🏷️ {len(server.tags)} tags</span>
                            </div>
                            <div>
                                <button class="btn {'btn-danger' if server.enabled else 'btn-success'}" 
                                        onclick="toggleServer('{server.name}', {str(server.enabled).lower()})">
                                    {'Disable' if server.enabled else 'Enable'}
                                </button>
                                <button class="btn btn-primary" onclick="viewDetails('{server.name}')">
                                    Details
                                </button>
                            </div>
                        </div>
                """
            
            html_content += """
                    </div>
                </div>
                
                <script>
                    async function toggleServer(serverName, isEnabled) {
                        const action = isEnabled ? 'disable_server' : 'enable_server';
                        
                        try {
                            const response = await fetch('/dashboard/api/manage', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({action: action, server_name: serverName})
                            });
                            
                            const result = await response.json();
                            if (result.success) {
                                location.reload();
                            } else {
                                alert('Error: ' + result.error);
                            }
                        } catch (error) {
                            alert('Network error: ' + error.message);
                        }
                    }
                    
                    async function refreshRegistry() {
                        if (!confirm('Refresh from registry?')) return;
                        
                        try {
                            const response = await fetch('/dashboard/api/manage', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({action: 'refresh_registry'})
                            });
                            
                            const result = await response.json();
                            if (result.success) {
                                alert('Registry refreshed successfully!');
                                location.reload();
                            } else {
                                alert('Error: ' + result.error);
                            }
                        } catch (error) {
                            alert('Network error: ' + error.message);
                        }
                    }
                    
                    function viewDetails(serverName) {
                        alert('Server details for ' + serverName + ' - implement as needed');
                    }
                    
                    function viewAnalytics() {
                        alert('Analytics view - implement as needed');
                    }
                </script>
            </body>
            </html>
            """
            
            execution_time = time.time() - start_time
            logger.info(f"Dashboard served successfully in {execution_time:.3f}s - Servers: {len(all_servers)} ({len(enabled_servers)} enabled)")
            
            return {
                "status": 200,
                "headers": {"Content-Type": "text/html"},
                "body": html_content
            }
        
        elif method == "POST" and path == "/dashboard/api/manage":
            # Handle API requests
            try:
                body = request.get("body", {})
                if isinstance(body, str):
                    body = json.loads(body)
                
                action = body.get("action")
                server_name = body.get("server_name")
                
                logger.info(f"Dashboard API request - Action: {action}, Server: {server_name}")
                
                if action == "enable_server" and server_name:
                    success = mcp_config.enable_server(server_name)
                    logger.info(f"Server enable request: {server_name} - {'Success' if success else 'Failed'}")
                    return {
                        "status": 200,
                        "headers": {"Content-Type": "application/json"},
                        "body": json.dumps({"success": success})
                    }
                
                elif action == "disable_server" and server_name:
                    success = mcp_config.disable_server(server_name)
                    logger.info(f"Server disable request: {server_name} - {'Success' if success else 'Failed'}")
                    return {
                        "status": 200,
                        "headers": {"Content-Type": "application/json"},
                        "body": json.dumps({"success": success})
                    }
                
                elif action == "refresh_registry":
                    logger.info("Registry refresh requested via dashboard")
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        servers = loop.run_until_complete(mcp_config.refresh_servers_from_registry())
                        logger.info(f"Registry refresh completed - {len(servers)} servers updated")
                        return {
                            "status": 200,
                            "headers": {"Content-Type": "application/json"},
                            "body": json.dumps({"success": True, "servers_updated": len(servers)})
                        }
                    finally:
                        loop.close()
                
                else:
                    logger.warning(f"Invalid dashboard API action: {action}")
                    return {
                        "status": 400,
                        "headers": {"Content-Type": "application/json"},
                        "body": json.dumps({"success": False, "error": "Invalid action"})
                    }
                    
            except Exception as e:
                execution_time = time.time() - start_time
                error_msg = str(e)
                logger.error(f"Dashboard API error: {error_msg} (execution time: {execution_time:.3f}s)")
                return {
                    "status": 500,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"success": False, "error": error_msg})
                }
        
        execution_time = time.time() - start_time
        logger.warning(f"Dashboard 404 - Method: {method}, Path: {path} (execution time: {execution_time:.3f}s)")
        
        return {
            "status": 404,
            "headers": {"Content-Type": "text/plain"},
            "body": "Not Found"
        } 