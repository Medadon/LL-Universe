
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from API.database import (
    create_tables,
    register_player,
    save_score,
    get_leaderboard
)

app = FastAPI(title="LL Universe API")


@app.on_event("startup")
def startup():
    create_tables()


class PlayerRegistration(BaseModel):
    nickname: str = Field(min_length=1, max_length=20)


class ScoreSubmission(BaseModel):
    player_id: int
    score: int = Field(ge=0)


@app.get("/")
def home():
    return {"message": "LL Universe API is running!"}


@app.post("/players/register")
def register(data: PlayerRegistration):
    nickname = data.nickname.strip()

    if not nickname:
        raise HTTPException(
            status_code=400,
            detail="Nickname cannot be empty."
        )

    player_id = register_player(nickname)

    return {
        "message": "Player registered successfully.",
        "player_id": player_id
    }


@app.post("/scores")
def submit_score(data: ScoreSubmission):
    save_score(data.player_id, data.score)

    return {"message": "Score saved successfully."}


@app.get("/leaderboard")
def leaderboard():
    return {
        "leaderboard": get_leaderboard()
    }
