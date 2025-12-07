from .web import tool_definitions as web_tools
from .memory import tool_definitions as memory_tools
from .automation.ui import tool_definitions as ui_automation_tools
from .automation.browser import tool_definitions as browser_tools
from .automation.droidrun import tool_definitions as droidrun_tools
from .database import tool_definitions as database_tools
from .git import tool_definitions as git_tools
from .file_ops import tool_definitions as file_ops_tools
from .nlp import tool_definitions as nlp_tools
from .cm import tool_definitions as cm_tools
from .core import tool_definitions as core_tools

tool_definitions = {
    **web_tools,
    **memory_tools,
    **ui_automation_tools,
    **browser_tools,
    **droidrun_tools,
    **database_tools,
    **git_tools,
    **file_ops_tools,
    **nlp_tools,
    **cm_tools,
    **core_tools,
}

__all__ = ["tool_definitions"]
