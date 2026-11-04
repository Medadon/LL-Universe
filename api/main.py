from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from api.db import (
    create_tables,
    get_leaderboard,
    register_player,
    save_score,
)


API_DIR = Path(__file__).resolve().parent
app = FastAPI(title="LL Universe API")
app.mount(
    "/static",
    StaticFiles(directory=API_DIR / "static"),
    name="static",
)
templates = Jinja2Templates(directory=API_DIR / "templates")


@app.on_event("startup")
def startup():
    create_tables()


class PlayerRegistration(BaseModel):
    nickname: str = Field(min_length=1, max_length=20)


class ScoreSubmission(BaseModel):
    player_id: int
    score: int = Field(ge=0)
    ship_name: str | None = Field(default=None, max_length=30)


@app.get("/")
def home():
    return {"message": "LL Universe API is running!"}


@app.post("/players/register")
def register(data: PlayerRegistration):
    nickname = data.nickname.strip()

    if not nickname:
        raise HTTPException(
            status_code=400,
            detail="Nickname cannot be empty.",
        )

    player_id = register_player(nickname)
    return {
        "message": "Player registered successfully.",
        "player_id": player_id,
    }


@app.post("/scores")
def submit_score(data: ScoreSubmission):
    save_score(data.player_id, data.score, data.ship_name)
    return {"message": "Score saved successfully."}


@app.get("/leaderboard")
def leaderboard():
    return {"leaderboard": get_leaderboard()}


@app.get("/leaderboard/view", response_class=HTMLResponse)
def leaderboard_view(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="leaderboard.html",
        context={"players": get_leaderboard()},
    )
