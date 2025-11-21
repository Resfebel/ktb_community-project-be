from datetime import timedelta

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any, Dict
from fastapi import HTTPException
from starlette import status
import re

from datas.user_data import USER_DATA, user_id_counter
from utils.jwt_handler import create_access_token
from utils.password_handler import hash_password, verify_password
from utils.token_data import TOKEN_BLACKLIST
from config import ACCESS_TOKEN_EXPIRE_MINUTES

### 틀
ID_COMPLEXITY = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+$'
ID_FAILURE_MESSAGE= "올바른 이메일 주소 형식을 입력해주세요. (예:example@example.com)"
PASSWORD_COMPLEXITY = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,20}$'
PASSWORD_FAILURE_MESSAGE= "비밀번호는 8자 이상, 20자 이하이며, 대문자, 소문자, 숫자, 특수문자를 각각 최소 1개 포함해야 합니다."

# 응답
class UserResponse(BaseModel):
    message: str
    data: Optional[Any] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    data: Optional[Any] = None
    message: Optional[str] = None

# JWT
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# JWT 토큰 들어갈 정보
class TokenData(BaseModel):
    # 토큰에 email을 담아 사용자 식별에 사용합니다.
    email: Optional[str] = None

# 회원가입
class UserSignup(BaseModel):
    email: str
    password: str
    password_check: str
    nickname: str = Field(..., max_length=10)
    profile_image: Optional[str] = None

    # 예외 1. 유효성 검사
    # 이메일
    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if not re.fullmatch(ID_COMPLEXITY, value):
            raise ValueError(ID_FAILURE_MESSAGE)
        return value

    # 비밀번호
    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if not re.fullmatch(PASSWORD_COMPLEXITY, value):
            raise ValueError(PASSWORD_FAILURE_MESSAGE)
        return value

    # 닉네임
    @field_validator("nickname")
    @classmethod
    def validate_nickname(cls, value):
        if ' ' in value:
            raise ValueError("띄어쓰기를 없애주세요")
        return value

# 로그인
class UserLogin(BaseModel):
    email: str
    password: str

    # 예외 1. 유효성 검사
    # 이메일
    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if not re.fullmatch(ID_COMPLEXITY, value):
            raise ValueError(ID_FAILURE_MESSAGE)
        return value

    # 비밀번호
    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if not re.fullmatch(PASSWORD_COMPLEXITY, value):
            raise ValueError(PASSWORD_FAILURE_MESSAGE)
        return value

# 정보 수정
class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(None, max_length=10)
    profile_image: Optional[str] = None

# 비밀번호 수정
class PasswordUpdate(BaseModel):
    new_password: str
    new_password_check: str

    # 예외 1. 비밀번호 유효성 검사
    @field_validator("new_password")
    @classmethod
    def validate_password(cls, value):
        if not re.fullmatch(PASSWORD_COMPLEXITY, value):
            raise ValueError(PASSWORD_FAILURE_MESSAGE)
        return value

# Function
def signup_user(user: UserSignup) -> UserResponse:
    # 예외 2. 이메일 예외처리
    # 입력 x
    if not user.email:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {"message": "이메일을 입력해주세요."}
        )
    # 이미 가입된 이메일
    elif user.email in USER_DATA:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {"message": "이미 가입된 이메일입니다."}
        )
    # 예외 3. 비밀번호 예외처리
    # 비밀번호 입력x
    if not user.password:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {"message": "비밀번호를 입력해주세요."}
        )
    # 비밀번호 확인 입력x
    elif not user.password_check:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {"message": "비밀번호 확인을 입력해주세요."}
        )
    # 비밀번호-확인 불일치
    elif user.password != user.password_check:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {"message": "비밀번호가 다릅니다."}
        )
    # 예외 4: 닉네임 예외처리
    # 닉네임 입력 x
    if not user.nickname:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {"message": "닉네임을 입력해주세요."}
        )

    # 중복 닉네임
    for _, data in USER_DATA.items():
        if data.get("nickname") == user.nickname:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"message": "중복된 닉네임입니다."}
            )

    user_id = globals()["user_id_counter"]
    # 비밀번호는 해시함수로 암호화해서 넣기!
    hashed_password = hash_password(user.password)

    new_user = {
        "user_id": user_id,
        "email": user.email,
        "password": hashed_password,
        "nickname": user.nickname,
        "profile_image": user.profile_image
    }

    USER_DATA[user.email] = new_user
    globals()["user_id_counter"] += 1

    # 회원 가입
    return UserResponse(
        message = f"{user.nickname}님 성공적으로 가입되었습니다.",
        data = { "user_id": user_id }
    )

def login_user(user: UserLogin) -> TokenResponse:
    # 예외 2. 비밀번호 입력 x
    if not user.password:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {"message": "비밀번호를 입력해주세요."}
        )

    user_info = USER_DATA.get(user.email)
    # 예외 3. 존재하지 않는 사용자
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "아이디 또는 비밀번호를 확인해 주세요."}
        )

    # 예외 4. 이메일-비밀번호 불일치
    if not verify_password(user.password, user_info["password"]):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = {"message": "아이디 또는 비밀번호를 확인해 주세요."}
        )

    ###
    # JWT 토큰 생성
    access_token = create_access_token(
        data = {"email": user.email},
        expires_delta = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES))

    # 토큰 반환 -> 로그인 성공!
    return TokenResponse(
        access_token = access_token,
        token_type = "bearer",
        data = { "email": user.email},
        message = f"{user_info['nickname']}님 로그인 되었습니다."
    )

def logout_user(current_user: Dict, token: str) -> UserResponse:
    auth_email = current_user.get("email")
    user_info = USER_DATA.get(auth_email)
    if user_info is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail={"message": "존재하지 않는 사용자입니다."}
        )
    # 토큰 무효화
    TOKEN_BLACKLIST.add(token)

    user_name = user_info.get("nickname")
    return UserResponse(
        message = f"{user_name}로그아웃 성공"
    )


def update_user(current_user: dict, update_user_data: UserUpdate) -> UserResponse:
    auth_email = current_user.get("email")
    user_info = USER_DATA.get(auth_email)

    # 예외 2. 사용자 x (희박하지만...)
    if user_info is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = {"인증된 사용자를 찾을 수 없습니다."}
        )

    new_nickname = update_user_data.nickname
    # 예외 3. 닉네임 입력x
    if not new_nickname:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {"message": "닉네임을 입력해주세요."}
        )
    # 예외 3. 중복 닉네임
    for email, data in USER_DATA.items():
        if email == auth_email:
            continue
        if data["nickname"] == new_nickname:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = {"message": "중복된 닉네임입니다."}
            )

    # 닉네임 변경
    user_info["nickname"] = new_nickname
    # 프로필 사진 변경
    if update_user_data.profile_image is not None:
        user_info["profile_image"] = update_user_data.profile_image

    return UserResponse(
        message = "수정 완료",
        data = {"nickname": user_info["nickname"],
                "profile_image": user_info["profile_image"]
                }
    )

def update_password(current_user: dict, update_password_data: PasswordUpdate) -> UserResponse:
    auth_email = current_user.get("email")
    if auth_email not in USER_DATA:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"인증된 사용자를 찾을 수 없습니다."}
        )
    new_pw = update_password_data.new_password
    check_pw = update_password_data.new_password_check
    # 예외 2. 새 비밀번호 입력x -> 유효성 검사로 해결.
    if not new_pw:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {"message": "비밀번호를 입력해주세요."}
        )
    # 예외 3. 비밀번호 확인 입력x
    elif not check_pw:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {"message": "비밀번호 확인을 입력해주세요."}
        )
    # 예외 4. 비밀번호-확인 불일치
    elif new_pw != check_pw:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {"message": "비밀번호가 다릅니다."}
        )

    # 비밀번호 변경'
    user_info = USER_DATA.get(auth_email)
    hashed_pw = hash_password(new_pw)
    user_info["password"] = hashed_pw
    return UserResponse(
        message = "수정 완료"
    )

def remove_user(current_user: Dict) -> UserResponse:
    auth_email = current_user.get("email")

    if auth_email not in USER_DATA:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = {"message": "탈퇴한 사용자를 찾을 수 없습니다."}
        )

    # 유저 삭제
    del USER_DATA[auth_email]
    return UserResponse(
        message = f"{auth_email} 사용자 탈퇴 완료"
    )