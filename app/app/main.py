import os
from dotenv import find_dotenv, load_dotenv

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from .database import sql_query_raw


load_dotenv(find_dotenv())

DATABASE_URL = os.getenv("DATABASE_URL", None)
URL_PREFIX = os.getenv("URL_PREFIX", "/api/v0")

app = FastAPI(docs_url=URL_PREFIX)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
def get_api_status():
    return {"status": f"running via automated deployment at {URL_PREFIX}"}


@app.get(URL_PREFIX + "/foo/")
async def test_function():
    return {"foo": "bar"}
