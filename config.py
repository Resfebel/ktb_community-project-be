import os
#SECRET_KEY = "YOUR_SUPER_KEY_NEVER_EVER_SHARE"
# 환경 변수에서 'JWT_SECRET_KEY'를 로드하고, 없으면 빈 문자열을 사용 (실행 시 오류 방지)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-key-for-test")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30