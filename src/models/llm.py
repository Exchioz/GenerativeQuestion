from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

class LLM:
    def __init__(self, model_name: str, api_key: str) -> None:
        self.client = ChatOpenAI(
            model_name=model_name, 
            api_key=api_key
        )

    def generate_question(self, query: str, parser: JsonOutputParser) -> dict:
        prompt = PromptTemplate(
            template="Jawab pertanyaan pengguna.\n{format_instructions}\n{query}\n",
            input_variables=["query"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | self.client | parser
        return chain.invoke({"query": query})
    
