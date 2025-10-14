from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.PredictionBuilder import PredictionBuilder
from fastapi.encoders import jsonable_encoder


app = FastAPI()

prediction_builder = PredictionBuilder()

origins = [
    "http://localhost:3000",  # React dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/backtest/daily-returns")
def get_daily_returns():
    return prediction_builder.get_portfolio_performance()

@app.get("/backtest/performance-per-stock")
def get_stock_performance():
    return prediction_builder.get_stock_performance()

@app.get("/backtest/global-stats")
def get_global_stats():
    return prediction_builder.get_stats()