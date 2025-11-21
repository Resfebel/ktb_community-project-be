from fastapi import FastAPI
from dotenv import load_dotenv
import uvicorn

from routers import user_router, post_router

# dev.env 파일의 환경 변수를 시스템에 로드
load_dotenv(dotenv_path='dev.env')

app = FastAPI()

app.include_router(user_router.router)
app.include_router(post_router.router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
