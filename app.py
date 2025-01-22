from fastapi import FastAPI
from pydantic import BaseModel
import requests
import json

app = FastAPI()

# Define the request body schema
class ChatRequest(BaseModel):
    user_input: str

# LM Studio API endpoint
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

# Load event details
with open('event_details.json', 'r') as file:
    event_data = json.load(file)

def get_event_detail(event_name):
    for event in event_data['events']:
        if event['name'].lower() == event_name.lower():
            return event
    return None

def extract_event_name(query):
    # Simple keyword matching
    for event in event_data['events']:
        if event['name'].lower() in query.lower():
            return event['name']
    return None

def ask_lm_studio(prompt):
    # Send a request to the LM Studio API
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 50
    }
    response = requests.post(LM_STUDIO_URL, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "Sorry, I couldn't generate a response."

@app.post("/chat")
def chat(request: ChatRequest):
    # Extract event name from user query
    event_name = extract_event_name(request.user_input)

    if event_name:
        # Get event details
        event_detail = get_event_detail(event_name)

        if event_detail:
            # Pass event details to the model
            prompt = f"Event Details: {event_detail}\nUser Query: {request.user_input}\nProvide a short and direct response."
            response = ask_lm_studio(prompt)
        else:
            response = "Sorry, I couldn't find details for that event."
    else:
        # If no event is found, respond generically
        response = ask_lm_studio(request.user_input)

    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)