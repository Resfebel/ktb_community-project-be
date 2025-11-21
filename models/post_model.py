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

# 게시글 수정
class PostUpdate(BaseModel):
    title: str = Field(..., max_length=26)
    content: str
    post_image: Optional[str] = None

# 댓글 작성
class Comment(BaseModel):
    comment_content: str
