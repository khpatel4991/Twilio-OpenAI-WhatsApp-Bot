import os
from datetime import datetime
from dotenv import load_dotenv

from fastapi import Form, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from twilio.rest import Client

from app.prompts import SYSTEM_PROMPT
from app.xai_utils import gpt_without_functions, summarise_conversation
from app.logger_utils import logger

# Load environment variables from a .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

app = FastAPI(
    title="WhatsApp-Bot",
    description="WhatsApp Bot",
    version="0.0.2",
    contact={
        "name": "Kashyap Patel",
        "url": "https://vyas.guru/",
        "email": "kashyap@vyas.guru",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def home():
    return {"message": "Twilio WhatsApp Bot API", "status": "running"}


def respond(to_number, message) -> None:
    """Send a message via Twilio WhatsApp"""
    TWILIO_WHATSAPP_PHONE_NUMBER = "whatsapp:" + TWILIO_WHATSAPP_NUMBER  # type: ignore
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    from_whatsapp_number = TWILIO_WHATSAPP_PHONE_NUMBER
    twilio_client.messages.create(
        body=message, from_=from_whatsapp_number, to=to_number
    )


@app.post("/whatsapp-endpoint")
async def whatsapp_endpoint(
    request: Request, From: str = Form(...), Body: str = Form(...)
):
    logger.info(f"WhatsApp endpoint triggered...")
    logger.info(f"Request: {request}")
    logger.info(f"Body: {Body}")
    logger.info(f"From: {From}")

    query = Body
    phone_no = From.replace("whatsapp:+", "")
    chat_session_id = phone_no

    # Initialize chat history (no persistence without Redis)
    history = []

    # Append the user's query to the chat history
    history.append({"role": "user", "content": query})

    # Summarize the conversation history
    history_summary = summarise_conversation(history)

    # Format the system prompt with the conversation summary and current date
    system_prompt = SYSTEM_PROMPT.format(
        history_summary=history_summary, today=datetime.now().date()
    )

    # Get a response from xAI's GPT model
    model_response = gpt_without_functions(
        model="grok-4-1-fast-non-reasoning",
        stream=False,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": "Hi there, how can I help you?"},
        ]
        + history,
    )
    chatbot_response = model_response

    # Append the assistant's response to the chat history
    history.append(
        {"role": "assistant", "content": chatbot_response},
    )

    logger.info(f"Response: {chatbot_response}")

    # Send the assistant's response back to the user via WhatsApp
    respond(From, chatbot_response)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=3002, reload=True)
