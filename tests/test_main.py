import logging
import random
import os
import requests
import json
import re
import pytest
from dotenv import load_dotenv

load_dotenv() # load environment variables from .env file

host = os.environ.get("MCP_HOST", "127.0.0.1")
port = os.environ.get("MCP_PORT", "8080")
path = os.environ.get("MCP_PATH", "mcp")

# ensure an __init__.py file exists in the tests and src directories to make them packages
from src.main import add, get_secret_word, get_current_weather

import subprocess
import sys
import time

logger = logging.getLogger(__name__)

@pytest.fixture
def server():
    """Start the MCP server in a separate Python process so the tests can continue.

    The original ``start_server()`` helper called ``mcp.run`` directly, which blocks
    the current thread.  When you invoke it from within pytest the fixture never
    returns and the suite hangs.

    Instead we launch ``src.main`` as a subprocess, wait briefly for it to come up,
    and then terminate it after the tests complete.
    """
    # spawn a fresh interpreter running the module as a script
    proc = subprocess.Popen([sys.executable, "-m", "src.main"],
                            env=os.environ.copy())
    # give the server a moment to bind to the port; in real code you could poll
    time.sleep(0.5)
    yield # provide the server fixture whilst the tests run
    proc.terminate()
    proc.wait(timeout=5)

@pytest.mark.parametrize("a, b, expected", [
    (2,3,5),
    (-1,1,0),
    (0,0,0)
])
def test_add(a, b, expected):
    assert add(a, b) == expected, f"Expected add({a}, {b}) to be {expected}"

def test_get_secret_word():
    random.seed(0) # set seed for reproducibility
    word = get_secret_word()
    logger.info(f"Secret word obtained: {word}")
    assert word in ["apple", "banana", "cherry"], f"Secret word should be one of 'apple', 'banana', or 'cherry', got '{word}'"

def test_get_current_weather():
    city = "London"
    weather = get_current_weather(city)
    logger.info(f"Weather data obtained for {city}")
    assert f"Weather report: {city}" in weather, f"Weather report should contain the city name '{city}'"

def test_server(server):
    """Test the MCP server by starting it, making a request, and then shutting it down."""

    headers = {
        "Content-Type": "application/json",
        # FastMCP requires the client to accept both JSON and SSE when negotiating
        # a streamable session. Include both mime types to avoid 406 responses.
        "Accept": "application/json, text/event-stream"
    }

    # necessary payload format for calling a tool hosted on the MCP server
    payload = {
        "jsonrpc": "2.0", 
        "id": 1, 
        "method": "tools/call", # method for calling a tool
        "params": {
            "name": "get_secret_word", # name of the tool to call
            "arguments": {} # parameters for the tool, if any, leave empty if tool takes no parameters
        }
    }
    
    # POST request to the MCP server endpoint
    logger.info(f"Attempting to call the MCP server at http://{host}:{port}/{path}...")
    r = requests.post(f"http://{host}:{port}/{path}", headers=headers, json=payload, stream=True)
    response_text = r.content.decode('utf-8')
    logger.info(f"Raw response from MCP server: {response_text}")
    # extract the tool result from the streamed response
    result = json.loads(re.findall(r"data: (.+)", response_text)[0])['result']['content'][0]['text']
    # stream or print the initial content for debugging
    logger.info(f"MCP server response: {result}")
    assert result in ["banana", "apple", "cherry"], f"Expected one of 'banana', 'apple', or 'cherry', got '{result}'"