import logging
import os
import random
import sys
import requests
from fastmcp import FastMCP

from dotenv import load_dotenv

load_dotenv() # load environment variables from .env file

host = os.environ.get("MCP_HOST", "127.0.0.1")
port = os.environ.get("MCP_PORT", 8080)
path = os.environ.get("MCP_PATH", "mcp")

name = "mcp-server"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)',
    filename='src/main.log'
)
logger = logging.getLogger(__name__)

mcp = FastMCP(name)

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    logger.info(f"Tool called: add({a}, {b})")
    return a + b

@mcp.tool()
def get_secret_word() -> str:
    """Get a random secret word"""
    logger.info("Tool called: get_secret_word()")
    return random.choice(["apple", "banana", "cherry"])

@mcp.tool()
def get_current_weather(city: str) -> str:
    """Get current weather for a city"""
    logger.info(f"Tool called: get_current_weather({city})")

    try:
        endpoint = "https://wttr.in"
        response = requests.get(f"{endpoint}/{city}", timeout=20)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Error fetching weather data: {str(e)}")
        return f"Error fetching weather data: {str(e)}"

if __name__ == "__main__":
    logger.info(f"Starting MCP Server on port {port}...")
    try:
        mcp.run(transport="streamable-http", path=f"/{path}", host=host, port=int(port), stateless=True) # run in stateless mode (no session)
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)
    finally:
        logger.info("Server terminated")