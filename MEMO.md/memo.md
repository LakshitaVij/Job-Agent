What you built 

I built an autonomous job application agent with 55 tools across 5 namespaces, namely search, evaluate, email, apply and document.
It is a Claude-powered execution loop that selects tools dynamically from a registry, and uses integrations of JSearch, Serper, Hunter.io, Gmail, and Notion. To make sure that outputs survive across 45+ tool calls, I have created a mechanism for external state persistence via JSON. To make sure that there is sufficient production scaffolding, I have created a retry mechanism for exponential backoff, rate limiting and observability logging.  The subagent for this job application agent is called suggest_build_opportunities which has isolated context and scoped toolset with the job of finding job descriptions, and evaluating which of my experiences match with said role, and synthesizing the information to draft in one paragraph what I can do for the role which would make me stand out.

What you cut 

I cut real browser automation for the apply namespace, and instead mocked Greenhouse/Workday form filling. Instead of having multiple subagents I implemented only one end to end. There is also no frontend or dashboard and the real Gmail OAuth flow has not been fully tested end to end.

What additional time would have addressed

If I had more time, I would have used real playwrite implementation for the apply namespace, written more evaluation scenarios with actual API calls, and fine tuned prompts in evaluate namespace based on real outputs,and I would have done better context summarization for very long sessions.

One design decision you would defend

I chose Raw Anthropic SDK over LangGraph because I wanted to force myself to understand every part of the architecture involved to make myself a better engineer, make the codebase more readable,  and avoid framework magic hiding critical decisions like context management and tool routing