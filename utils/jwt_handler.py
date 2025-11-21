from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional
from fastapi import HTTPException, status
from config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    # 이메일 복사
    to_encode = data.copy()
    if expires_delta:
        # 토큰 만료시간 제공되면 그거대로
        expire = datetime.utcnow() + expires_delta
    else:
        # 아니면 기존에 지정해둔 대로 (30m)
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # 페이로드 업데이트
    to_encode.update({"exp": expire, "sub": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # payload -> email 추출
        email: str = payload.get("email")

        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid token payload")
        return {"email": email}

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid token signature or expired token")
