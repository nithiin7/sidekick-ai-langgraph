"""
External API tools for search, Wikipedia, and notifications.
Provides integration with various external services.
"""

import os
import requests
from typing import List
from langchain.agents import Tool
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_experimental.tools import PythonREPLTool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from src.utils.config import config


def push(text: str) -> str:
    """
    Send a push notification to the user via Pushover.
    
    Args:
        text: Message text to send
        
    Returns:
        Success status string
    """
    if not config.PUSHOVER_TOKEN or not config.PUSHOVER_USER:
        return "Push notifications not configured"
    
    try:
        response = requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": config.PUSHOVER_TOKEN,
                "user": config.PUSHOVER_USER,
                "message": text
            },
            timeout=10
        )
        response.raise_for_status()
        return "Push notification sent successfully"
    except requests.RequestException as e:
        return f"Failed to send push notification: {e}"


def get_file_tools() -> List[Tool]:
    """
    Get file management tools.
    
    Returns:
        List of file management tools
    """
    try:
        # Ensure sandbox directory exists
        os.makedirs("sandbox", exist_ok=True)
        toolkit = FileManagementToolkit(root_dir="sandbox")
        return toolkit.get_tools()
    except Exception as e:
        print(f"Warning: Failed to initialize file tools: {e}")
        return []


async def other_tools() -> List[Tool]:
    """
    Get all external tools.
    
    Returns:
        List of external tools
    """
    tools = []
    
    # Push notification tool
    push_tool = Tool(
        name="send_push_notification",
        func=push,
        description="Use this tool when you want to send a push notification"
    )
    tools.append(push_tool)
    
    # File management tools
    file_tools = get_file_tools()
    tools.extend(file_tools)
    
    # Search tool
    if config.SERPER_API_KEY:
        serper = GoogleSerperAPIWrapper()
        search_tool = Tool(
            name="search",
            func=serper.run,
            description="Use this tool when you want to get the results of an online web search"
        )
        tools.append(search_tool)
    
    # Wikipedia tool
    try:
        wikipedia = WikipediaAPIWrapper()
        wiki_tool = WikipediaQueryRun(api_wrapper=wikipedia)
        tools.append(wiki_tool)
    except Exception as e:
        print(f"Warning: Failed to initialize Wikipedia tool: {e}")
    
    # Python REPL tool
    try:
        python_repl = PythonREPLTool()
        tools.append(python_repl)
    except Exception as e:
        print(f"Warning: Failed to initialize Python REPL tool: {e}")
    
    return tools
