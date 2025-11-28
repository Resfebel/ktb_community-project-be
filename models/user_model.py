from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any
import re


### 틀
ID_COMPLEXITY = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+$'
ID_FAILURE_MESSAGE= "올바른 이메일 주소 형식을 입력해주세요. (예:example@example.com)"

PASSWORD_COMPLEXITY = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,20}$'
PASSWORD_FAILURE_MESSAGE= "비밀번호는 8자 이상, 20자 이하이며, 대문자, 소문자, 숫자, 특수문자를 각각 최소 1개 포함해야 합니다."


# 응답
class UserResponse(BaseModel):
    message: str
    data: Optional[Any] = None

# 토큰 응답
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    data: Optional[Any] = None
    message: Optional[str] = None

# JWT 반환용
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# JWT 토큰 들어갈 정보
class TokenData(BaseModel):
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

# 정보 조회
class UserInfo(BaseModel):
    email: str
    nickname: str
    profile_image: Optional[str] = None


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
