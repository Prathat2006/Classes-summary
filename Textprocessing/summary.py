import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from Textprocessing.llminit import LLMManager

# Load environment variables from .env
# load_dotenv()

# Lecture Summary Agent
class LectureSummaryAgent:
    def __init__(self, llm_manager, fallback_order):
        self.llm_manager = llm_manager
        self.fallback_order = fallback_order
        self.prompt = PromptTemplate(
            input_variables=["transcription"],
            template="""You are an AI assistant tasked with summarizing a lecture transcript. Given the following transcription, provide:
            1. A full summary of what happened in the lecture.
            2. A list of topics covered in the lecture.
            3. A brief explanation of key points discussed.

            Transcription: {transcription}
            
            Format your response in clear sections:
            - Full Summary
            - Topics Covered
            - Brief Explanation
            """
        )

    def generate_summary(self, transcription):
        chain_input = self.prompt.format(transcription=transcription.strip())
        summary = self.llm_manager.invoke_with_fallback(self.llm_manager.setup_llm_with_fallback(self.fallback_order), self.fallback_order, chain_input)
        if not summary.strip():
            return "Error: Summary could not be generated."
        return summary

# Main Function to Generate Lecture Summaries
def lecture_summary_agent(transcription, fallback_order=None):
    try:
        llm_manager = LLMManager()
        llm_instances = llm_manager.setup_llm_with_fallback(fallback_order)
        if not llm_instances:
            raise Exception("No LLMs available for processing.")

        agent = LectureSummaryAgent(llm_manager, fallback_order or llm_manager.DEFAULT_FALLBACK_ORDER)
        
        print("\n--- Input Transcription ---")
        print(transcription)
        
        print("\nGenerating summary...")
        summary = agent.generate_summary(transcription)
        
        if summary:
            print("\n--- Lecture Summary ---")
            print(summary)
            return summary
        else:
            print("Failed to generate summary.")
            return None
            
    except Exception as e:
        print(f"Error in lecture summary agent: {e}")
        return None

# #