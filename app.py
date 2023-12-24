from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

from authlib.integrations.starlette_client import OAuth, OAuthError
from celery.schedules import schedule
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from redbeat import RedBeatSchedulerEntry
from starlette import status
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware

from model import crud, models, schemas
from model.database import SessionLocal, engine
from tasks import celery_app


if TYPE_CHECKING:
    from sqlalchemy.orm import Session

BASE_DIR = Path(__file__).parent
STATIC_DIR = Path(BASE_DIR, "static")
TEMPALTES_DIR = Path(BASE_DIR, "templates")


models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="some-random-string")  # noqa:S106


# Dependency
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


oauth = OAuth(Config())
oauth.register("github", access_token_params=None, authorize_params=None, client_kwargs={"scope": "read:user"})

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPALTES_DIR)


@dataclass
class UserData:
    login: str
    name: str


def get_login_and_name(request: Request) -> UserData | None:
    userinfo = request.session.get("userinfo")
    if not userinfo:
        return None

    login, name = userinfo.get("login", ""), userinfo.get("name", "")
    if not login or not name:
        return None
    return UserData(login=login, name=name)


def get_user_from_session(request: Request, db: Session) -> models.User | None:
    data = get_login_and_name(request)
    if not data:
        return None

    return crud.get_user_by_login_and_name(db=db, login=data.login, name=data.name)


def get_user_id_from_session(request: Request, db: Session) -> int | None:
    user = get_user_from_session(request, db)
    if not user:
        return None

    return user.id


def celery_task_from_stream(stream: models.Stream) -> RedBeatSchedulerEntry:
    return RedBeatSchedulerEntry(
        name=f"task-{stream.name}-{stream.user_id}",
        task="tasks.stream_with_notificators",
        schedule=schedule(run_every=60),
        kwargs={"stream_params": jsonable_encoder(stream)},
        app=celery_app,
    )


@app.get("/", response_class=HTMLResponse)
def homepage(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:  # noqa:B008
    user = get_user_from_session(request, db)

    values: dict[str, Any] = {"request": request}
    if user:
        values |= {
            "userinfo": {"name": user.name, "login": login},
            "streams": user.streams,
            "notificators": user.notificators,
            "predictors": models.Predictor,
            "notificator_types": models.NotificatorType,
            "video_parsers": models.VideoParser,
        }

    return templates.TemplateResponse("index.html", values)  # type:ignore[return-value]


@app.post("/streams")
def create_stream(
    request: Request,
    stream: schemas.StreamCreate = Depends(schemas.StreamCreate.as_form),  # noqa:B008
    db: Session = Depends(get_db),  # noqa:B008
) -> RedirectResponse:
    user_id = get_user_id_from_session(request, db)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Login please")

    celery_task_from_stream(
        crud.create_user_stream(
            db=db,
            stream=stream,
            user_id=user_id,
        ),
    ).save()

    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


@app.get("/streams/delete")
def delete_stream(
    request: Request,
    name: str = Query(),
    db: Session = Depends(get_db),  # noqa:B008
) -> RedirectResponse:
    user_id = get_user_id_from_session(request, db)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Login please")

    stream = crud.delete_user_stream(db=db, name=name, user_id=user_id)
    if stream:
        celery_task_from_stream(stream).delete()

    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


@app.post("/notificators")
def create_notificator(
    request: Request,
    notificator: schemas.NotificatorCreate = Depends(schemas.NotificatorCreate.as_form),  # noqa:B008
    db: Session = Depends(get_db),  # noqa:B008
) -> RedirectResponse:
    user_id = get_user_id_from_session(request, db)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Login please")

    crud.create_user_notificator(
        db=db,
        notificator=notificator,
        user_id=user_id,
    )

    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


@app.get("/notificators/delete")
def delete_notificator(
    request: Request,
    name: str = Query(),
    db: Session = Depends(get_db),  # noqa:B008
) -> RedirectResponse:
    user_id = get_user_id_from_session(request, db)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Login please")

    crud.delete_user_notificator(db=db, name=name, user_id=user_id)
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


@app.get("/login")
async def login(request: Request) -> RedirectResponse:
    redirect_uri = request.url_for("auth")
    return await oauth.github.authorize_redirect(request, redirect_uri)


@app.get("/authorize")
async def auth(request: Request, db: Session = Depends(get_db)) -> RedirectResponse:  # noqa:B008
    try:
        token = await oauth.github.authorize_access_token(request)
    except OAuthError as error:
        request.session["userinfo"] = {"error": f"can't login {error}"}
    else:
        resp = await oauth.github.get("user", token=token)
        request.session["userinfo"] = resp.json()
        data = get_login_and_name(request)
        if data:
            crud.create_user(db, schemas.UserCreate(name=data.name, login=data.login))
        else:
            request.session["userinfo"] = {"error": "no login or name in oauth response"}
    return RedirectResponse(url="/")


@app.get("/logout")
def logout(request: Request) -> RedirectResponse:
    request.session.pop("userinfo", None)
    return RedirectResponse(url="/")
