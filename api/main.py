from contextlib import AsyncExitStack
from typing import Optional

from mcp import ClientSession


class MCPClient:
    def __init__(self):
        # Initialize the MCP client with a session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack: AsyncExitStack()
        self.tools = []
        self.messages = []
