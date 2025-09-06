
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from core.prompt_manager import get_system_prompt
from tools.knowledge_base import search_knowledge_base
from tools.file_io import write_file

class ResearchAgent:
    """
    The core of the research agent, now powered by LangChain's Agent Executor.
    """
    def __init__(self, model: str, api_key: str, api_base: str, temperature: float = 0.1):
        self.llm = ChatOpenAI(
            model=model,
            openai_api_key=api_key,
            openai_api_base=api_base,
            temperature=temperature
        )
        self.tools = [search_knowledge_base, write_file]
        self.chat_history = []

        # This prompt template is designed for tool-using agents
        prompt = ChatPromptTemplate.from_messages([
            ("system", get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=False) # verbose=True lets us see the agent's thoughts

    def chat(self, user_input: str) -> str:
        """
        Invokes the agent executor to get a response.
        """
        try:
            response = self.agent_executor.invoke({
                "input": user_input,
                "chat_history": self.chat_history
            })
            
            # Save history
            self.chat_history.append(HumanMessage(content=user_input))
            self.chat_history.append(AIMessage(content=response['output']))

            return response['output']
        except Exception as e:
            return f"An error occurred: {e}"

