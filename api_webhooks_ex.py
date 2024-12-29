from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import httpx

app = FastAPI()

# Simulated API Example
def get_weather_data(location: str):
    """Simulate an API call to fetch weather data."""
    mock_weather_data = {
        "New York": {"temperature": "5°C", "condition": "Cloudy"},
        "London": {"temperature": "7°C", "condition": "Rainy"},
        "Tokyo": {"temperature": "10°C", "condition": "Sunny"},
    }
    return mock_weather_data.get(location, {"error": "Location not found"})

@app.get("/api/weather")
async def weather_api(location: str):
    """API endpoint to get weather information."""
    data = get_weather_data(location)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data

# Webhook Models and Logic
class Subscription(BaseModel):
    url: str

class EventData(BaseModel):
    event: str
    details: dict

subscribers = []  # List of subscriber URLs

@app.post("/webhook/subscribe")
async def subscribe_webhook(subscription: Subscription):
    """Endpoint to subscribe to webhook notifications."""
    subscribers.append(subscription.url)
    return {"message": "Subscription successful", "url": subscription.url}

async def notify_subscriber(subscriber_url: str, event_data: dict):
    """Send a POST request to a subscriber with the event data."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(subscriber_url, json=event_data)
            response.raise_for_status()
            print(f"Notification sent to {subscriber_url}, status code: {response.status_code}")
        except Exception as e:
            print(f"Failed to notify {subscriber_url}: {e}")

@app.post("/webhook/event")
async def trigger_event(event_data: EventData, background_tasks: BackgroundTasks):
    """Trigger an event and notify subscribers."""
    for subscriber_url in subscribers:
        background_tasks.add_task(notify_subscriber, subscriber_url, event_data.dict())
    return {"message": "Event notifications are being sent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
