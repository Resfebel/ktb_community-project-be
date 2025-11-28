from fastapi import APIRouter, status
from fastapi.params import Depends

from controllers import post_controller
from models.post_model import PostCreate, PostUpdate, CommentInput
from utils.deps import get_current_user
from database import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)

# post
# 게시글 작성
@router.post("/",
             status_code = status.HTTP_201_CREATED, summary = "게시글 작성")
def post(post_info: PostCreate, current_user: dict = Depends(get_current_user),
         db:Session = Depends(get_db)):
    return post_controller.create_post(current_user, db, post_info)

# 게시글 목록 조회
@router.get("/",
             status_code = status.HTTP_200_OK, summary = "게시글 목록조회")
def list_posts(db: Session = Depends(get_db)):
    return post_controller.get_post_list(db)

# 게시글 상세 조회 (click)
@router.get("/{post_id}",
             status_code = status.HTTP_200_OK, summary = "게시글 상세조회")
def get_post(post_id: int, db: Session = Depends(get_db)):
    print(f"Post ID received: {post_id}, Type: {type(post_id)}")
    return post_controller.get_post(post_id, db)

# 게시글 수정
@router.patch("/{post_id}",
             status_code = status.HTTP_200_OK, summary = "게시글 수정")
def update_post(post_id: int, new_post: PostUpdate,
                current_user: dict = Depends(get_current_user),
                db: Session = Depends(get_db)):
    return post_controller.update_post(post_id, current_user, db, new_post)

# 게시글 삭제
@router.delete("/{post_id}",
             status_code = status.HTTP_200_OK, summary = "게시글 삭제")
def remove_post(post_id: int, current_user: dict = Depends(get_current_user),
                db: Session = Depends(get_db)):
    return post_controller.remove_post(post_id, current_user, db)


# likes
# 좋아요
@router.post("/{post_id}/likes",
              status_code= status.HTTP_201_CREATED, summary = "게시글 좋아요")
def post_like(post_id: int, current_user: dict = Depends(get_current_user),
              db: Session = Depends(get_db)):
    return post_controller.post_like(post_id, current_user, db)

# 사용자 좋아요 반영 확인
@router.get("/{post_id}/likes",
            status_code= status.HTTP_200_OK, summary = "현재 유저가 좋아요 눌렀는지 확인")
def check_like(post_id: int, current_user: dict = Depends(get_current_user),
               db: Session = Depends(get_db)):
    return post_controller.check_like(post_id, current_user, db)

# 좋아요 취소
@router.delete("/{post_id}/likes",
               status_code= status.HTTP_200_OK, summary = "좋아요 취소")
def remove_like(post_id: int, current_user: dict = Depends(get_current_user),
                db: Session = Depends(get_db)):
    return post_controller.remove_like(post_id, current_user, db)


# comment
# 댓글 작성
@router.post("/{post_id}/comments",
             status_code = status.HTTP_201_CREATED, summary = "댓글 작성")
def post_comment(post_id: int, comment_info: CommentInput,
                 current_user: dict = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    return post_controller.create_comment(post_id, current_user, db, comment_info)

# 포스트 댓글 조회
@router.get("/{post_id}/comments",
            status_code = status.HTTP_200_OK, summary = "댓글 조회")
def get_comment(post_id: int, db: Session = Depends(get_db)):
    return post_controller.get_comment(post_id, db)

# 댓글 수정
@router.patch("/{post_id}/comments/{comment_id}",
              status_code = status.HTTP_200_OK, summary = "댓글 수정")
def update_comment(post_id: int, comment_id: int, comment_info: CommentInput,
                   current_user: dict = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    return post_controller.update_comment(post_id, comment_id,
                                          current_user, db, comment_info)

# 댓글 삭제
@router.delete("/{post_id}/comments/{comment_id}",
               status_code = status.HTTP_200_OK, summary = "댓글 삭제")
def remove_comment(post_id: int, comment_id: int,
                   current_user: dict = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    return post_controller.delete_comment(post_id, comment_id, current_user, db)