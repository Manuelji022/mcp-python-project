from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("weather")


@mcp.tool()
async def get_weather(city: str) -> str:
    """Get the current weather for a specified city
    Args:
        city (str): The name of the city to get the weather for.

    Returns:
        str: A string containing the current weather information for the city.
    """
    return f""""
    The weather in {city} is currently sunny with a temperature of 22°C.
    """


if __name__ == "__main__":
    mcp.run(transport="stdio")
