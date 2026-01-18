# Twilio-OpenAI-WhatsApp-Bot/app/xai_utils.py

import os
from dotenv import load_dotenv
from xai_sdk import Client
from xai_sdk.chat import system, user, assistant
from app.prompts import SUMMARY_PROMPT

load_dotenv()

XAI_API_KEY = os.getenv("XAI_API_KEY")

# Constants
TEMPERATURE = 0.1
MAX_TOKENS = 350
STOP_SEQUENCES = ["==="]
TOP_P = 1
TOP_K = 1
BEST_OF = 1
FREQUENCY_PENALTY = 0
PRESENCE_PENALTY = 0

SUPPORTED_MODELS = {
    "grok-4-1-fast-reasoning",
    "grok-4-1-fast-non-reasoning",
    "grok-3",
    "grok-2-vision",
    "grok-2",
    "grok-1",
}


def _convert_messages(messages):
    """Convert OpenAI-style messages to xAI chat messages"""
    converted = []
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        if role == "system":
            converted.append(system(content))
        elif role == "user":
            converted.append(user(content))
        elif role == "assistant":
            converted.append(assistant(content))
    return converted


class MockChoice:
    def __init__(self, message):
        self.message = message


class MockMessage:
    def __init__(self, content):
        self.content = content


class MockResponse:
    def __init__(self, content):
        self.choices = [MockChoice(MockMessage(content))]


def gpt_without_functions(model, stream=False, messages=[]):
    """xAI model without function call."""
    if model not in SUPPORTED_MODELS:
        return False

    client = Client(api_key=XAI_API_KEY)
    chat = client.chat.create(model=model, messages=_convert_messages(messages))

    if stream:
        # For streaming, return the stream generator
        return chat.stream()
    else:
        response = chat.sample()
        # Wrap in mock response to match OpenAI API
        return response.content


def summarise_conversation(history):
    """Summarise conversation history in one sentence"""

    conversation = ""
    for item in history[-70:]:
        if "user_input" in item:
            conversation += f"User: {item['user_input']}\n"
        if "bot_response" in item:
            conversation += f"Bot: {item['bot_response']}\n"

    xai_response = gpt_without_functions(
        model="grok-4-1-fast-non-reasoning",
        stream=False,
        messages=[
            {"role": "system", "content": SUMMARY_PROMPT},
            {"role": "user", "content": conversation},
        ],
    )

    return xai_response
