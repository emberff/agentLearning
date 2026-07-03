import os

from tavily import TavilyClient


def search(query: str) -> str:
    """
    一个基于 Tavily 的网页搜索工具。
    优先返回 AI 总结，没有则返回搜索结果摘要。
    """
    print(f"🔍 正在执行 [Tavily] 网页搜索: {query}")

    try:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return "错误：TAVILY_API_KEY 未在 .env 文件中配置。"

        client = TavilyClient(api_key=api_key)

        results = client.search(
            query=query,
            search_depth="advanced",     # basic / advanced
            topic="general",             # general / news
            max_results=3,
            include_answer=True,
            include_raw_content=False,
        )

        # 优先返回 AI 总结
        answer = results.get("answer")
        if answer:
            return answer

        # 如果没有 AI 总结，则返回搜索结果
        search_results = results.get("results", [])
        if search_results:
            snippets = [
                f"[{i+1}] {item.get('title', '')}\n"
                f"{item.get('content', '')}\n"
                f"{item.get('url', '')}"
                for i, item in enumerate(search_results)
            ]
            return "\n\n".join(snippets)

        return f"对不起，没有找到关于 '{query}' 的信息。"

    except Exception as e:
        return f"搜索时发生错误：{e}"