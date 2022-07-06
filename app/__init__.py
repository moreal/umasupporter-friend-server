import requests
import sqlalchemy
from app.database import database
from app.models import metadata
from app.schema import schema

from app.env import CLIENT_ID, DATABASE_URL, HOST
from fastapi import Depends, FastAPI, Request, Response
from pydantic import BaseModel
from strawberry.fastapi import GraphQLRouter

from uuid import uuid4
from app.cookie import SessionData, cookie, verifier, backend


class OAuthTokenRequest(BaseModel):
    token_type: str
    access_token: str
    expires_in: int
    refresh_token: str
    refresh_token_expires_in: int
    scope: str


engine = sqlalchemy.create_engine(DATABASE_URL)

metadata.create_all(engine)
app = FastAPI(debug=True)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/callback")
async def oauth(code: str, response: Response):
    resp = requests.post(
        "https://kauth.kakao.com/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "code": code,
            "redirect_uri": f"https://{HOST}/callback",
        },
    )

    access_token = resp.json()["access_token"]
    resp = requests.get(
        "https://kapi.kakao.com/v1/user/access_token_info",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    session = uuid4()
    kakao_id = resp.json()["id"]
    data = SessionData(kakao_id=kakao_id)

    await backend.create(session, data)
    cookie.attach_to_response(response, session)

    return "Give me SSR"


@app.get("/whoami", dependencies=[Depends(cookie)])
async def whoami(request: Request, session_data: SessionData = Depends(verifier)):
    return session_data
