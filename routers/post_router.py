from fastapi import APIRouter, status
from fastapi.params import Depends

from controllers import post_controller
from controllers.post_controller import PostCreate, PostUpdate, Comment
from utils.deps import get_current_user

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)

@router.post("/",
             status_code = status.HTTP_201_CREATED, summary = "게시글 작성")
def post(post_info: PostCreate, current_user: dict = Depends(get_current_user)):
    return post_controller.create_post(current_user, post_info)

@router.get("/",
             status_code = status.HTTP_200_OK, summary = "게시글 목록조회")
def list_posts():
    return post_controller.get_post_list()

@router.get("/{post_id}",
             status_code = status.HTTP_200_OK, summary = "게시글 상세조회")
def get_post(post_id: int):
    print(f"Post ID received: {post_id}, Type: {type(post_id)}")
    return post_controller.get_post(post_id)

@router.patch("/{post_id}",
             status_code = status.HTTP_200_OK, summary = "게시글 수정")
def update_post(post_id: int, new_post: PostUpdate,
                current_user: dict = Depends(get_current_user)):
    return post_controller.update_post(post_id, current_user, new_post)

@router.delete("/{post_id}",
             status_code = status.HTTP_200_OK, summary = "게시글 삭제")
def remove_post(post_id: int, current_user: dict = Depends(get_current_user)):
    return post_controller.remove_post(post_id, current_user)

# comment
@router.post("/{post_id}/comments",
             status_code = status.HTTP_201_CREATED, summary = "댓글 작성")
def post_comment(post_id: int, comment_info: Comment,
                 current_user: dict = Depends(get_current_user)):
    return post_controller.create_comment(post_id, current_user, comment_info)

@router.patch("/{post_id}/comments/{comment_id}",
              status_code = status.HTTP_200_OK, summary = "댓글 수정")
def update_comment(post_id: int, comment_id: int, comment_info: Comment,
                   current_user: dict = Depends(get_current_user)):
    return post_controller.update_comment(post_id, comment_id,
                                          current_user, comment_info)

@router.delete("/{post_id}/comments/{comment_id}",
               status_code = status.HTTP_200_OK, summary = "댓글 삭제")
def remove_comment(post_id: int, comment_id: int,
                   current_user: dict = Depends(get_current_user)):
    return post_controller.delete_comment(post_id, comment_id, current_user)