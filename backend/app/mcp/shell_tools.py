import subprocess
import shlex
from mcp.server.fastmcp import FastMCP
from pydantic import Field
from typing import Annotated
mcp = FastMCP()

@mcp.tool(name="run_shell", description="Run a shell command")
def run_shell_cmd(cmd:Annotated[str, Field(description="shell command will be executed",examples="ls -al")]) -> str:
    try:
        shell_cmd=shlex.split(cmd)
        if "rm" in shell_cmd:
            raise Exception("rm is not allowed")
        res = subprocess.run(cmd, shell=True,capture_output=True, text=True) 
        if res.returncode != 0:
            return res.stderr
        else:
            return res.stdout
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    mcp.run(transport="stdio")