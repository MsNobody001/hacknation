import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()

PROMPT_FILE_PATH = "prompts/document_advisor.txt"

class DocumentAdvisorAgent:
    def __init__(self, prompt_file_path=PROMPT_FILE_PATH):
        self.llm = AzureChatOpenAI(
            azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
            openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        )

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
        
        self.agent = create_tool_calling_agent(self.llm, [], self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools = [], verbose=True)

    def generate_document_checklist(self, accident_data, chat_history=None):
        """Generate a document checklist based on accident data"""
        if chat_history is None:
            chat_history = []
            
        result = self.agent_executor.invoke({
            "input": accident_data,
            "chat_history": chat_history
        })
        return result["output"]
    

if __name__ == "__main__":
    agent = DocumentAdvisorAgent()
    response = agent.generate_document_checklist("Miałam wypadek")
    print(response)
    