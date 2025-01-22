from fastapi import FastAPI
from transformers import pipeline
import json

app = FastAPI()

# Load the DeepSeek model
chatbot = pipeline("text-generation", model="deepseek-model")

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

@app.post("/chat")
def chat(user_input: str):
    # Extract event name from user query
    event_name = extract_event_name(user_input)

    if event_name:
        # Get event details
        event_detail = get_event_detail(event_name)

        if event_detail:
            # Pass event details to the model
            prompt = f"Event Details: {event_detail}\nUser Query: {user_input}"
            response = chatbot(prompt, max_length=50)[0]['generated_text']
        else:
            response = "Sorry, I couldn't find details for that event."
    else:
        # If no event is found, respond generically
        response = chatbot(user_input, max_length=50)[0]['generated_text']

    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)