from fastapi import FastAPI

from app.routers import pins, users

app = FastAPI(title="SoundPins API", version="0.1.0")
app.include_router(users.router)
app.include_router(pins.router)
