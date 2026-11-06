import sys

import anyio

from mcp.client import Client
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("demo")


@mcp.tool()
def add_one(x: int) -> int:
    """Add one.

    Args:
        x: The number.
    """
    return x + 1


async def main() -> None:
    async with Client(mcp) as client:
        tool = (await client.list_tools()).tools[0]
    print(sys.version.split()[0], repr(tool.description))


anyio.run(main)
