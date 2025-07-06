import asyncio
from aiohttp import web

# Mock MCP server registry data
def get_mock_registry_data():
    return [
        {
            "name": "MockServer1",
            "url": "http://localhost:8001",
            "enabled": True,
            "description": "Mock Server for Testing",
            "tags": ["test", "mock"],
            "last_updated": "2023-11-15T10:30:00Z",
            "available_tools": [
                {
                    "name": "weather",
                    "description": "Get current weather information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "City name"
                            }
                        },
                        "required": ["city"]
                    }
                },
                {
                    "name": "calculator",
                    "description": "Simple arithmetic calculations",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "operation": {
                                "type": "string",
                                "enum": ["add", "subtract", "multiply", "divide"]
                            },
                            "num1": {
                                "type": "number"
                            },
                            "num2": {
                                "type": "number"
                            }
                        },
                        "required": ["operation", "num1", "num2"]
                    }
                }
            ]
        },
        {
            "name": "MockServer2",
            "url": "http://localhost:8002",
            "enabled": False,
            "description": "Disabled Mock Server",
            "tags": ["test", "disabled"],
            "last_updated": "2023-11-15T11:45:00Z",
            "available_tools": [
                {
                    "name": "translator",
                    "description": "Translate text between languages",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string"
                            },
                            "source_lang": {
                                "type": "string"
                            },
                            "target_lang": {
                                "type": "string"
                            }
                        },
                        "required": ["text", "target_lang"]
                    }
                }
            ]
        }
    ]

# Request handler for registry endpoint
async def handle_registry_request(request):
    data = get_mock_registry_data()
    return web.json_response(data)

# Setup mock server
def setup_mock_registry():
    app = web.Application()
    app.router.add_get('/api/mcp-servers', handle_registry_request)
    return app

if __name__ == '__main__':
    print("Starting mock MCP registry server on http://localhost:8080")
    print("Registry endpoint: http://localhost:8080/api/mcp-servers")
    web.run_app(setup_mock_registry(), port=8080)