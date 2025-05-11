from composio_gemini import ComposioToolSet, App, Action, action
from dotenv import load_dotenv

load_dotenv()

toolset = ComposioToolSet()

github_tools = toolset.get_tools(
    actions=[
        Action.GITHUB_CREATE_A_COMMIT,
        Action.SHELLTOOL_CREATE_SHELL, 
        Action.SHELLTOOL_EXEC_COMMAND,
        Action.GITHUB_CREATE_A_PULL_REQUEST
        ],
    skip_default=True
)

slack_tools = toolset.get_tools(
    apps=[App.SLACK],
    skip_default=True
)

twitter_tools = toolset.get_tools(
    apps=[App.TYPEFULLY, App.TWITTER],
    skip_default=True
)

file_tools = toolset.get_tools(
    apps=[App.FILETOOL, App.SHELLTOOL],
    skip_default=True
)

twitter_scroll_tools = toolset.get_tools(
    actions=[Action.TWITTER_LIST_POSTS_TIMELINE_BY_LIST_ID, Action.TWITTER_USER_HOME_TIMELINE_BY_USER_ID, Action.TWITTER_GET_A_USER_S_OWNED_LISTS, Action.TWITTER_USER_LOOKUP_ME],
    skip_default=True,
)
code_tools = toolset.get_tools(
    apps=[App.CODEINTERPRETER, App.FILETOOL, App.SHELLTOOL],
    skip_default=True

)

web_tools = toolset.get_tools(
    actions=[Action.COMPOSIO_SEARCH_SEARCH],
    skip_default=True

)

@action(toolname="relevant_tools_for_a_usecase")
def tools_for_usecase(usecase: str)->list[str]:
    """
    Get the tools to use based on usecase
    :param usecase: what are the core apps you need to finish the task in one concise line of description
    :returns tools list 
    """
    tools = toolset.find_actions_by_use_case(use_case=usecase, advanced=True)
    return tools