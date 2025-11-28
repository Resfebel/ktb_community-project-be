from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from database import get_db

from controllers import user_controller
from models.user_model import UserSignup, UserLogin, UserUpdate, PasswordUpdate
from typing import Dict, Any
from utils.deps import get_current_user, oauth2_scheme


router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# 회원가입
@router.post("/signup",
             status_code = status.HTTP_201_CREATED, summary = "회원가입")
def signup(user: UserSignup, db: Session = Depends(get_db)):
    return user_controller.signup_user(user, db)

# 로그인
@router.post("/login",
             status_code = status.HTTP_200_OK, summary = "로그인")
def login(user: UserLogin, db: Session = Depends(get_db)):
    return user_controller.login_user(user, db)

# 로그아웃
@router.post("/logout",
             status_code=status.HTTP_200_OK, summary = "로그아웃")
def logout(current_user: Dict[str, Any] = Depends(get_current_user),
           token: str = Depends(oauth2_scheme)):
    return user_controller.logout_user(current_user, token)

# 회원정보 불러오기
@router.get("/me",
            status_code = status.HTTP_200_OK, summary = "현재 인증된 사용자 정보")
def get_user(current_user: Dict[str, Any] = Depends(get_current_user),
             db: Session = Depends(get_db)):
    return user_controller.get_user(current_user, db)

# 회원정보 수정
@router.patch("/me",
              status_code = status.HTTP_200_OK, summary = "회원정보 수정")
def update_user(update_data: UserUpdate, current_user: dict = Depends(get_current_user),
                db = Depends(get_db)):
    return user_controller.update_user(current_user, db, update_data)

# 비밀번호 수정
@router.patch("/password",
              status_code = status.HTTP_200_OK, summary = "비밀번호 변경")
def password(update_password: PasswordUpdate, current_user: dict = Depends(get_current_user),
             db = Depends(get_db)):
    return user_controller.update_password(current_user, db, update_password)

# 회원 탈퇴
@router.delete("/me",
               status_code = status.HTTP_200_OK, summary = "회원 탈퇴")
def remove(current_user: dict = Depends(get_current_user), db = Depends(get_db)):
    return user_controller.remove_user(current_user, db)