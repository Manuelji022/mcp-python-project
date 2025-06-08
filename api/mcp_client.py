import traceback
from contextlib import AsyncExitStack
from typing import Optional

import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from ollama import ChatResponse
from utils import logger

MODEL = "qwen3:1.7b"


class MCPClient:
    def __init__(self):
        # Initialize the MCP client with a session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack: AsyncExitStack()
        self.tools = []
        self.messages = []
        self.ollama_client = ollama.AsyncClient()
        self.logger = logger

    # Connect to the MCP server
    async def connect_to_server(self, server_script_path: str):
        try:
            server_params = StdioServerParameters(
                command="python",
                args=[server_script_path],
                env=None,
            )
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            self.stdio, self.write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(self.stdio, self.write)
            )

            await self.session.initialize()

            self.logger.info(" ✅ Connected to MCP server successfully.")

            mcp_tools = await self.get_mcp_tools()
            self.tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                }
                for tool in mcp_tools
            ]

            self.logger.info(f" 🛠️ MCP Tools: {self.tools}")

        except Exception as e:
            self.logger.error(f" ❌ Failed to connect to MCP server: {str(e)}")
            traceback.print_exc()  # Ensure traceback is printed for debugging. Traceback means the error stack trace.
            raise

    # Call a tool
    # async def call_tool(self, tool_name: str, tool_args: dict):
    #     """Cal a tool with the given name and arguments."""
    #     try:
    #         result = await self.session.call_tool(
    #             tool_name=tool_name,
    #             tool_args=tool_args,
    #         )
    #         return result
    #     except Exception as e:
    #         self.logger.error(f" ❌ Failed to call tool {tool_name}: {str(e)}")
    #         self.logger.debug(f"Error details: {traceback.format_exc()}")
    #         raise Exception(f"Failed to call tool {tool_name}: {str(e)}")

    # Get MCP tool list
    async def get_mcp_tools(self):
        try:
            self.logger.info(" 🔍 Fetching MCP tools...")
            response = await self.session.list_tools()
            return response.tools
        except Exception as e:
            self.logger.error(f" ❌ Failed to fetch MCP tools: {str(e)}")
            self.logger.debug(f"Error details: {traceback.format_exc()}")
            raise Exception(f"Failed to fetch MCP tools: {str(e)}")

    # Call LLM
    async def call_llm_with_tools(self):
        try:
            response: ChatResponse = await self.ollama_client.chat(
                model=MODEL,
                messages=self.messages,
                tools=self.tools,
            )
            return response
        except Exception as e:
            self.logger.error(f" ❌ Failed to call LLM: {str(e)}")
            raise Exception(f"Failed to call LLM: {str(e)}")

    # Call simple LLM
    async def call_llm(self):
        try:
            response: ChatResponse = await self.ollama_client.chat(
                model=MODEL,
                messages=self.messages,
            )
            return response
        except Exception as e:
            self.logger.error(f" ❌ Failed to call simple LLM: {str(e)}")
            raise Exception(f"Failed to call simple LLM: {str(e)}")

    # Process query
    async def process_query(self, query: str):
        try:
            self.logger.info(f" 📝 Processing query: {query}")
            user_message = {
                "role": "user",
                "content": query,
            }
            self.messages.append(user_message)
            self.messages = [user_message]

            while True:
                response = await self.call_llm_with_tools()

                if response.message.tool_calls:
                    for tool in response.message.tool_calls:
                        self.logger.info(f" 🛠️ Calling tool: {tool.name}")
                        if function_to_call := self.tools.get(tool.name):
                            self.logger.info(f"Calling function: {tool.function.name}")
                            self.logger.info(
                                f"Function parameters: {tool.function.arguments}"
                            )
                            output = function_to_call(**tool.function.arguments)
                            self.logger.info(f" ✅ Tool call output: {output}")

                if response.message.tool_calls:
                    self.logger.info(
                        "Generate the final response based on tool outputs."
                    )
                    self.messages.append(response.message)
                    self.messages.append(
                        {
                            "role": "tool",
                            "content": str(output),
                            "name": tool.function.name,
                        }
                    )
                    final_response = await self.call_llm()
                    text_message = {
                        "role": "assistant",
                        "content": final_response.message.content,
                    }
                    self.messages.append(text_message)

        except Exception as e:
            self.logger.error(f" ❌ Failed to process query: {str(e)}")
            self.logger.debug(f"Error details: {traceback.format_exc()}")
            raise Exception(f"Failed to process query: {str(e)}")

    # Cleanup
    async def cleanup(self):
        try:
            self.logger.info(" 🧹 Cleaning up MCP client resources...")
            await self.exit_stack.aclose()
        except Exception as e:
            self.logger.error(f" ❌ Failed to clean up MCP client: {str(e)}")

    # Log conversation
