from datetime import timedelta
from typing import Dict
from fastapi import HTTPException
from starlette import status

from utils.jwt_handler import create_access_token
from utils.password_handler import hash_password, verify_password
from utils.token_data import TOKEN_BLACKLIST
from config import ACCESS_TOKEN_EXPIRE_MINUTES

from sqlalchemy.orm import Session
from database import User

from models.user_model import (UserResponse, UserSignup, UserLogin,
                               TokenResponse, UserUpdate, PasswordUpdate, UserInfo)

# Function
def signup_user(user: UserSignup, db: Session) -> UserResponse:
    # 이메일 미입력
    if not user.email:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {"message": "이메일을 입력해주세요."}
        )

    # 비밀번호 미입력
    if not user.password:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {"message": "비밀번호를 입력해주세요."}
        )

    # 비밀번호 확인 미입력
    if not user.password_check:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {"message": "비밀번호 확인을 입력해주세요."}
        )

    # 비밀번호-확인 불일치
    if user.password != user.password_check:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {"message": "비밀번호가 다릅니다."}
        )

    # 닉네임 미입력
    if not user.nickname:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {"message": "닉네임을 입력해주세요."}
        )

    # 이미 가입된 이메일
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {"message": "이미 가입된 이메일입니다."}
        )

    # 중복된 닉네임
    existing_nickname = db.query(User).filter(User.nickname == user.nickname).first()
    if existing_nickname:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "중복된 닉네임입니다."}
        )

    # 비밀번호는 해시함수로 암호화해서 넣기!
    hashed_password = hash_password(user.password)

    new_user = User(
        email = user.email,
        password = hashed_password,
        nickname = user.nickname,
        profile_image = user.profile_image
    )

    # DB 저장
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return UserResponse(
            message=f"{user.nickname}님 성공적으로 가입되었습니다.",
            data={"user_id": new_user.user_id}
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = {"message" : f"데이터베이스 갱신 중 오류 : {e}"}
        )

def login_user(user: UserLogin, db: Session) -> TokenResponse:

    # 존재하지 않는 사용자
    existing_user = db.query(User).filter(User.email == user.email).first()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "아이디 또는 비밀번호를 확인해 주세요."}
        )

    # 이메일-비밀번호 불일치
    if not verify_password(user.password, existing_user.password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = {"message": "아이디 또는 비밀번호를 확인해 주세요."}
        )

    # JWT 토큰 생성
    access_token = create_access_token(
        data = {"user_id": existing_user.user_id},
        expires_delta = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES))

    # 토큰 반환 -> 로그인 성공!
    return TokenResponse(
        access_token = access_token,
        token_type = "bearer",
        message = f"{existing_user.nickname}님 로그인 되었습니다."
    )

def logout_user(current_user: Dict, token: str) -> UserResponse:
    # 토큰 무효화
    TOKEN_BLACKLIST.add(token)
    return UserResponse(
        message = "로그아웃 성공"
    )

def get_user(current_user: Dict, db: Session) :
    auth_user_id = current_user.get("user_id")
    user_info = db.query(User).filter(User.user_id == auth_user_id).first()

    return_user_info = UserInfo(
        email = user_info.email,
        nickname = user_info.nickname,
        profile_image = user_info.profile_image
    )

    return UserResponse(
        message = f"{user_info.nickname} 회원님의 정보",
        data = return_user_info
    )

def update_user(current_user: dict, db: Session, update_user_data: UserUpdate) -> UserResponse:

    # 예외. 닉네임 입력x
    new_nickname = update_user_data.nickname
    if not new_nickname:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {"message": "닉네임을 입력해주세요."}
        )

    auth_user_id = current_user.get("user_id")
    auth_user = db.query(User).filter(User.user_id == auth_user_id).first()

    # 예외. 중복 닉네임 (본인은 제외)
    existing_nickname = db.query(User).filter(
        (User.nickname == new_nickname) & (User.user_id != auth_user_id)).first()
    if existing_nickname:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "중복된 닉네임입니다."}
        )

    # 닉네임 변경
    auth_user.nickname = new_nickname
    # 프로필 사진 변경
    if update_user_data.profile_image :
        auth_user.profile_image = update_user_data.profile_image

    # DB 갱신
    try:
        db.commit()
        return UserResponse(
            message = "수정 완료",
            data = {"nickname": auth_user.nickname,
                    "profile_image": auth_user.profile_image})
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = {"message" : f"데이터베이스 갱신 중 오류 : {e}"}
    )

def update_password(current_user: dict, db: Session, update_password_data: PasswordUpdate) -> UserResponse:
    new_pw = update_password_data.new_password
    check_pw = update_password_data.new_password_check
    # 예외. 새 비밀번호 입력x -> 유효성 검사로 해결.
    # 예외. 비밀번호 확인 입력x
    if not check_pw:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {"message": "비밀번호 확인을 입력해주세요."}
        )
    # 예외. 비밀번호-확인 불일치
    if new_pw != check_pw:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {"message": "비밀번호가 다릅니다."}
        )

    auth_user_id = current_user.get("user_id")
    auth_user = db.query(User).filter(User.user_id == auth_user_id).first()

    # 비밀번호 변경
    hashed_pw = hash_password(new_pw)
    auth_user.password = hashed_pw

    # DB 갱신
    try:
        db.commit()
        return UserResponse(
            message="수정 완료"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"데이터베이스 갱신 중 오류 : {e}"}
        )

def remove_user(current_user: Dict, db: Session) -> UserResponse:
    auth_user_id = current_user.get("user_id")
    auth_user = db.query(User).filter(User.user_id == auth_user_id).first()

    # 유저 삭제
    db.delete(auth_user)

    # DB 갱신
    try:
        db.commit()
        return UserResponse(message = "사용자 탈퇴 완료")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"데이터베이스 갱신 중 오류 : {e}"}
        )