from pydantic import BaseModel, Field
from typing import Optional, Any
from fastapi import HTTPException
from starlette import status
from datetime import datetime

from datas.post_data import POST_DATA, post_id_counter
from datas.user_data import USER_DATA


# 틀
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


# 게시글 작성
def create_post(current_user: dict, post: PostCreate) -> Response:
    # 예외 1. 제목 입력x
    if not post.title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = {"message": "제목, 내용을 모두 작성해주세요"}
        )
    # 예외 2. 내용 입력x
    if not post.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = {"message": "제목, 내용을 모두 작성해주세요"}
        )

    post_id = globals()["post_id_counter"]
    # 게시글 추가

    auth_email = current_user.get("email")
    user_info = USER_DATA.get(auth_email)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = {"message": "사용자를 찾을 수 없습니다."}
        )
    user_id = user_info.get("user_id")

    new_post = {
        "user_id": user_id,
        "title": post.title,
        "content": post.content,
        "post_image": post.post_image,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "like": 0,
        "views": 0,
        "comments": {},
        "next_comment_id": 1
    }

    POST_DATA[post_id] = new_post
    globals()["post_id_counter"] += 1

    return Response(
        message = "게시글이 작성되었습니다.",
        data = { "title": post.title,
                 "post_id": post_id }
    )


# 게시글 목록 조회
def get_post_list() :
    post_list = []
    for target_post in POST_DATA.values():
        post_summary = {
            "title": target_post["title"],
            "like": target_post["like"],
            "comments count": len(target_post["comments"]),
            "views": target_post["views"],
            "date": target_post["date"]
        }
        post_list.append(post_summary)

    return post_list


# 게시글 상세조회
def get_post(post_id: int) -> Response:
    post_info = POST_DATA.get(post_id)
    # 예외 1: 잘못된 게시글 아이디 (삭제했거나...)
    if post_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = {"message": "존재하지 않는 게시글입니다."}
        )
    return Response(
        message = "200 OK",
        data = post_info
    )

# 게시글 수정
def update_post(post_id: int, current_user: dict, post: PostUpdate) -> Response:
    # 예외 1: 잘못된 게시글 아이디
    post_info = POST_DATA.get(post_id)
    if post_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = {"message": "존재하지 않는 게시글입니다."}
        )

    auth_email = current_user.get("email")
    user_info = USER_DATA.get(auth_email)

    # 예외 2: 사용자 없음
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = {"message": "인증된 사용자를 찾을 수 없습니다."}
        )

    # 예외 3: 현재 사용자 - 작성자 불일치
    user_id = user_info["user_id"]
    if user_id != post_info.get("user_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = {"message": "해당 게시글을 수정할 권한이 없습니다."}
        )

    # 예외 4. 제목 미입력
    if not post.title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = {"message": "제목, 내용을 모두 작성해주세요"}
        )

    # 예외 5: 게시글 수정 내용 미입력
    if not post.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = {"message": "제목, 내용을 모두 작성해주세요"}
        )

    post_info["title"] = post.title
    post_info["content"] = post.content
    if post.post_image:
        post_info["post_image"] = post.post_image

    return Response(
        message = "게시글 수정 완료",
        data = f"title : {post.title}"
    )

# 게시글 삭제
def remove_post(post_id: int, current_user: dict) -> Response:
    # 예외 1: 잘못된 게시글 아이디
    post_info = POST_DATA.get(post_id)
    if post_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "존재하지 않는 게시글입니다."}
        )

    auth_email = current_user.get("email")
    user_info = USER_DATA.get(auth_email)
    # 예외 2: 사용자 없음
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = {"message": "인증된 사용자를 찾을 수 없습니다."}
        )

    # 예외 3: 현재 사용자 - 작성자 불일치
    user_id = user_info["user_id"]
    if user_id != post_info.get("user_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = {"message": "해당 게시글을 삭제할 권한이 없습니다."}
        )

    POST_DATA.pop(post_id)
    return Response(
        message = "게시글 삭제 완료"
    )


# 댓글 작성
def create_comment(post_id: int, current_user: dict, comment_info: Comment) -> Response:
    post = POST_DATA.get(post_id)
    # 예외 1: 유효하지 않은 게시글 (ex: 댓글 작성할 때 게시글 삭제)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "존재하지 않는 게시글입니다."}
        )

    # 예외 2: 댓글 내용 미입력
    content = comment_info.comment_content
    if content == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = { "message": "댓글 내용을 입력해주세요." }
        )
    auth_email = current_user.get("email")
    user_info = USER_DATA.get(auth_email)
    comment_id = post.get("next_comment_id", 1)
    comment_dict = post.get("comments")
    comment_dict[comment_id] = {
            "comment_id": comment_id,
            "commenter_id": user_info.get("user_id"),
            "author": user_info.get("nickname"),
            "comment_content": content,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    post["next_comment_id"] = comment_id + 1

    return Response(
        message = "댓글이 작성되었습니다.",
        data = { "comment_id" : comment_id,
                 "content" : content }
    )

# 댓글 수정
def update_comment(post_id: int, comment_id: int, current_user: dict, new_comment: Comment):
    post_info = POST_DATA.get(post_id)
    # 예외 1. 잘못된 게시글 아이디
    if post_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={ "message": "존재하지 않는 게시글입니다." }
        )
    # 예외 2. 잘못된 댓글 아이디
    comment_list = post_info.get("comments")
    comment_info = comment_list.get(comment_id)
    if comment_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = { "message": "댓글을 찾을 수 없습니다." }
        )

    # 예외 3: 댓글 내용 미입력
    new_comment_content = new_comment.comment_content
    if new_comment_content == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = { "message": "댓글 내용을 입력해주세요." }
        )

    # 예외 4: 사용자 - 댓글 작성자 불일치
    auth_email = current_user.get("email")
    user_info = USER_DATA.get(auth_email)
    if user_info.get("user_id") != comment_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = { "message": "댓글을 수정할 권한이 없습니다." }
        )

    comment_info["comment_content"] = new_comment_content
    return Response(
        message = "댓글이 수정되었습니다.",
        data = {"message": f"{comment_info}"}
    )

def delete_comment(post_id: int, comment_id: int, current_user: dict) -> Response:
    post_info = POST_DATA.get(post_id)
    # 예외 1. 잘못된 게시글 아이디
    if post_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={ "message": "존재하지 않는 게시글입니다." }
        )

    # 예외 2. 잘못된 댓글 아이디
    comment_dict = post_info.get("comments")
    comment_info = comment_dict.get(comment_id)
    if comment_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = { "message": "댓글을 찾을 수 없습니다." }
        )

    # 예외 3: 사용자 - 댓글 작성자 불일치
    auth_email = current_user.get("email")
    user_info = USER_DATA.get(auth_email)
    if user_info.get("user_id") != comment_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = { "message": "댓글을 삭제할 권한이 없습니다." }
        )

    del comment_dict[comment_id]
    return Response(
        message = "게시글 삭제 완료"
    )