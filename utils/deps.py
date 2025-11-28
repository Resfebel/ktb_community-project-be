from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from typing import Dict, Any

from utils.jwt_handler import decode_access_token
from .token_data import TOKEN_BLACKLIST

# 토큰 소유자
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "/users/login")

# Depends 이용한 의존성 주입
def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    # 토큰 무효화 -> 로그아웃
    if token in TOKEN_BLACKLIST:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 유효하지 않습니다. 다시 로그인해주세요",
        )

    # 현재 토큰으로 디코딩
    try:
        payload = decode_access_token(token)
    except HTTPException:
        raise

    # 디코딩 -> 페이로드에 유저 아이디 딕셔너리가 담겨서 옴!
    return payload
