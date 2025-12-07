import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()


class BaseDataCollectorAgent:
    def __init__(self, prompt_file_path, data_model_class):
        self.llm = AzureChatOpenAI(
            azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
            openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        )

        self.collected_data = data_model_class()

        tools = self._create_tools()

        with open(prompt_file_path, "r", encoding="utf-8") as file:
            prompt_template = file.read()
        
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    prompt_template
                ),
                ("placeholder", "{chat_history}"),
                ("user", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        
        self.agent = create_tool_calling_agent(self.llm, tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=tools, verbose=True)

    def _create_tools(self):
        """Override this method in subclasses to define specific tools"""
        raise NotImplementedError("Subclass must implement _create_tools()")

    def collect_data(self, user_input, chat_history=None):
        """Collect accident data through a conversation"""
        if chat_history is None:
            chat_history = []
            
        result = self.agent_executor.invoke({
            "input": user_input,
            "chat_history": chat_history
        })
        return result["output"]
    
    def get_collected_data(self):
        """Returns collected accident data"""
        return self.collected_data




if __name__ == "__main__":
    agent = AccidentDataCollectorAgent()
    response = agent.collect_data("Miałam wypadek")
    print(response)
    