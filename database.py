from datetime import datetime

from sqlalchemy import create_engine, text, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base

from config import SQLALCHEMY_DATABASE_URI

# 엔진
engine = create_engine(SQLALCHEMY_DATABASE_URI)


# 세션
Session = sessionmaker(bind = engine)
session = Session() #테스트용세션

# DB 세션을 생성하고 종료하는 의존성 함수
def get_db():
    db = Session() # 새 세션 생성
    try:
        yield db       # 라우터 함수로 세션 전달
    finally:
        db.close()     # 요청 처리 후 세션 닫기 (필수)

# 연동 테스트
try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM user LIMIT 1;")).fetchone()
    print("DB 연결 테스트: ", result)
except Exception as e:
    print(f"DB 연결 실패: {e}")
finally:
    # 끝나면 세션 닫아주기
    session.close()


# 기본 클래스
Base = declarative_base()

# 테이블 클래스
class User(Base):
    # table
    __tablename__ = "user"
    # attribute
    user_id = Column(Integer, primary_key = True, autoincrement = True)
    email = Column(String(50), unique = True, nullable = False)
    password = Column(String(255), nullable = False)
    nickname = Column(String(10), nullable = False)
    profile_image = Column(String(255), default = None)

    # tuple check
    def __repr__(self):
        return f"user(id: {self.user_id}, email: {self.email})"


class Post(Base):
    __tablename__ = "post"

    post_id = Column(Integer, primary_key = True, autoincrement = True)
    user_id = Column(Integer, ForeignKey('user.user_id', ondelete = 'CASCADE'),
                     nullable = False)
    title = Column(String(26), nullable = False)
    content = Column(Text, nullable = False)
    post_image = Column(String(255), default = None)
    create_at = Column(DateTime, default = datetime.now)
    likes= Column(Integer, default = 0)
    views = Column(Integer, default = 0)
    comments = Column(Integer, default = 0)

    def __repr__(self):
        return f"post(id: {self.post_id}, title: {self.title})"


class Comment(Base):
    __tablename__ = "comment"

    comment_id = Column(Integer, primary_key = True, autoincrement = True)
    post_id = Column(Integer, ForeignKey('post.post_id', ondelete = 'CASCADE'),
                     nullable = False)
    commenter_id = Column(Integer, ForeignKey('user.user_id', ondelete = 'CASCADE'),
                          nullable = False)
    comment_text = Column(Text, nullable = False)
    create_at = Column(DateTime, default = datetime.now)

    def __repr__(self):
        return f"comment(id: {self.comment_id}, commenter: {self.commenter_id})"

class Postlike(Base):
    __tablename__ = "postlike"

    post_id = Column(Integer, ForeignKey('post.post_id', ondelete = 'CASCADE'),
                     primary_key = True, nullable = False)
    user_id = Column(Integer, ForeignKey('user.user_id', ondelete = 'CASCADE'),
                     primary_key = True, nullable = False)

    def __repr__(self):
        return f"postlike(post id: {self.post_id}, liker: {self.useR_id})"