import os

# 환경 변수에서 'JWT_SECRET_KEY'를 로드하고, 없으면 빈 문자열을 사용 (실행 시 오류 방지)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-key-for-test")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#--------------------
# MySQL 연동 관련 정보 (로컬 DB에 맞게 HOST, USER, PASSWORD를 수정해주세요!)
MYSQL_HOST = '127.0.0.1'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'your_password'
MYSQL_DATABASE = 'ktb_community_db'

# SQLAlchemy URI
SQLALCHEMY_DATABASE_URI = (
    f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:3306/{MYSQL_DATABASE}"
)