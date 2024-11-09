import requests
from groq import *
import json
import gradio as gr
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
import dotenv
import os

from deep_translator import GoogleTranslator

dotenv.load_dotenv()

MODEL = 'llama-3.1-70b-versatile'
llm = ChatGroq(model=MODEL) # MAKE SURE GROQ API IS IN VENV, RUN: export GROQ_API_KEY='[YOUR_API_KEY]'

SYSTEM_PROMPT = """
    You're an API for a water resource conservation system. You'll need to write reports, simulations, and action proposals in a JSON format when asked.
    Each of the things you write MUST follow a specific format.

    The format for a REPORT is:
    {
        "text": REPORT TEXT (string, 2 - 3 paragraphs),
        "pH": pH VALUE (float, 0 - 14),
        "indiceBiodiversidade": BIODIVERSITY INDEX (int, 0 - 100)
    }

    The format for a SIMULATION is:
    {
        "text": SIMULATION TEXT (string, 2 - 3 paragraphs),
        "severity": SEVERITY LEVEL (string, enum('leve','medio','grave'))
    }

    The format for an ACTION PROPOSAL is:
    {
        "text": ACTION PROPOSAL TEXT (string, 2 - 3 paragraphs),
        "budget": BUDGET (float, 0 - 1000000)
    }
"""

def run_conversation(user_prompt):
    # Based off of this example (https://github.com/groq/groq-api-cookbook/blob/main/tutorials/function-calling-101-ecommerce/Function-Calling-101-Ecommerce.ipynb) on tool calling with Groq.
    # Changes allow for multiple tool calls that depend on each other (non-parallel) to be made at once.
    messages = [SystemMessage(SYSTEM_PROMPT), HumanMessage(user_prompt)]
    ai_msg = llm.invoke(messages)
    
    return ai_msg.content

def get_report(river_name):
    result = run_conversation(f"Generate a REPORT for the {river_name}")
    result = result[result.find("{"):result.rfind("}")+1]
    result = ''.join(c for c in result if c.isprintable())
    
    return json.loads(result)

def get_simulation(river_name, situation):
    result = run_conversation(f"Generate a SIMULATION with regarding what would happen to {river_name} if the following situation took place: {situation}")
    result = result[result.find("{"):result.rfind("}")+1]
    result = ''.join(c for c in result if c.isprintable())

    return json.loads(result)

def get_action_proposal(river_name):
    result = run_conversation(f"Generate an ACTION PROPOSAL for the {river_name}")
    result = result[result.find("{"):result.rfind("}")+1]
    result = ''.join(c for c in result if c.isprintable())

    return json.loads(result)

if __name__ == "__main__":
    result = get_report("Amazon River")
    print(result)

    result = get_simulation("Amazon River", "a severe drought")
    print(result)

    result = get_action_proposal("Amazon River")
    print(result)


