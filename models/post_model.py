from pydantic import BaseModel, Field
from typing import Optional, Any

# 응답
class Response(BaseModel):
    message: str
    data: Optional[Any] = None

# 게시글 작성
class PostCreate(BaseModel):
    title: str = Field(..., max_length=26)
    content: str
    post_image: Optional[str] = None

# 게시글 상세 형태
class PostDetail(BaseModel):
    title: str
    content: str
    post_image: Optional[str] = None
    create_at: str
    likes: int
    views: int
    comments: int
    nickname: str

# 게시글 요약 형태
class PostSummary(BaseModel):
    title: str
    likes: int
    views: int
    comments: int
    timestamp: str
    nickname: str


# 게시글 수정
class PostUpdate(BaseModel):
    title: str = Field(..., max_length=26)
    content: str
    post_image: Optional[str] = None

# 댓글 작성
class CommentInput(BaseModel):
    comment_text: str

class CommentDetail(BaseModel):
    commenter_nickname: str
    create_at: str
    comment_text: str

# 좋아요
class PostlikeInput(BaseModel):
    post_id: int
    user_id: int