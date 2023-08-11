import time
from typing import Annotated

import uvicorn
from fastapi import FastAPI, Query, Path, Body
from pydantic import BaseModel, Field, validator, field_validator, field_serializer
import aiofiles
import asyncio


app = FastAPI()


class User(BaseModel):
    name: str
    age: int
    address: str
    friends: list[str]


@app.get("/")
async def hello() -> dict[str, int]:
    return {"meesage": "Hello World"}


@app.get("/hello/{name}")
async def custom_hello(name: str, nickname: Annotated[str, None]) -> dict[str, str]:
    match nickname:
        case "" | None:
            message = f"Hello {name}"
        case _:
            message = f"Hello {name} ({nickname})"
    return {"message": message}


@app.get("/add/{x}/{y}")
async def add(x: Annotated[int, Path(ge=0, lt=100)], y: Annotated[int, Path(ge=0, lt=100)]) -> dict[str, int]:
    return {"message": x+y}


@app.get("/multiply")
async def multiply(x: int, y: int) -> dict[str, int]:
    return {"message": x*y}


@app.get("/multiply/{x}/{y}")
async def multiply_from_path(x: int, y: int) -> dict[str, int]:
    return {"message": x*y}


@app.post("/users")
async def add_user(user: Annotated[User, Body()]) -> dict[str, str | list[str]]:
    return dict(name=user.name, friends=user.friends)


class IdSheet(BaseModel):
    filename: str = Field(min_length=1, max_length=10)
    ids: list[int]

    @validator("ids", each_item=True)
    def greater_or_equal_zero(cls, value: int) -> int:
        if value < 0:
            raise ValueError("id가 0보다 작습니다.")
        return value


@app.post("/sheets", status_code=201)
async def add_file(sheet: IdSheet) -> dict[str, str]:
    start = time.time()
    async with aiofiles.open(sheet.filename, "w") as f:
        asyncio.sleep(5)
        await f.write(f"id\n" + "\n".join(map(str, sheet.ids)))
    end = time.time() - start
    return dict(message=f"elapsed time: {end}s")


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
