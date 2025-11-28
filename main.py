from fastapi import FastAPI
from dotenv import load_dotenv
import uvicorn

from routers import user_router, post_router, yolo_router
from database import engine, Base, User, Post, Comment

# dev.env 파일의 환경 변수를 시스템에 로드
load_dotenv(dotenv_path='dev.env')

# 과제 확인 위한 DB Table Create
#Base.metadata.create_all(bind = engine)

app = FastAPI()

app.include_router(user_router.router)
app.include_router(post_router.router)
app.include_router(yolo_router.router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
