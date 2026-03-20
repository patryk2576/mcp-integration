import requests
import logging
import json
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)',
    filename='src/mcp_server_test.log'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Attempting to call the MCP server...")

    headers = {
        "Content-Type": "application/json",
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
    try:
        # POST request to the MCP server endpoint
        r = requests.post("http://127.0.0.1:8080/mcp", headers=headers, json=payload, stream=True)
        response_text = r.content.decode('utf-8')
        logger.info(f"Raw response from MCP server: {response_text}")
        # extract the tool result from the streamed response
        result = json.loads(re.findall(r"data: (.+)", response_text)[0])['result']['content'][0]['text']
        # stream or print the initial content for debugging
        logger.info(f"MCP server response: {result}")
    except Exception as e:
        logger.error(f"Error calling MCP server: {str(e)}")
    