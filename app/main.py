from fastapi import FastAPI
from app.ai_api import app as ai_app      # or include_router if same FastAPI instance
from app.tickets_api import router as tickets_router

app = FastAPI()
app.include_router(tickets_router)
app.mount("", ai_app)  # or merge routes in one app if you prefer
