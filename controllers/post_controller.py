from fastapi import HTTPException
from starlette import status

from models.post_model import (Response, PostCreate, PostUpdate, CommentInput, PostSummary, PostDetail, CommentDetail)

from sqlalchemy.orm import Session
from database import User, Post, Comment, Postlike

# 게시글 작성
def create_post(current_user: dict, db: Session, post: PostCreate) -> Response:
    # 예외. 제목 or 내용 미입력
    if not post.title or not post.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = {"message": "제목, 내용을 모두 작성해주세요"}
        )


    auth_user_id = current_user.get("user_id")
    new_post = Post(
        user_id = auth_user_id,
        title = post.title,
        content = post.content,
        post_image = post.post_image if post.post_image else None
    )

    # DB 저장
    try:
        db.add(new_post)
        db.commit()
        db.refresh(new_post)

        return Response(
            message = "게시글이 작성되었습니다.",
            data = { "title": post.title }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = {"message" : f"데이터베이스 갱신 중 오류 : {e}"}
        )


# 게시글 목록 조회
def get_post_list(db: Session) -> Response:
    post_list = db.query(Post.title, Post.likes, Post.views,
                         Post.comments, Post.create_at, User.nickname
                         ).join(User, Post.user_id == User.user_id).all()

    post_summary_list = []
    for title, likes, views, comments, create_at, nickname in post_list:
        post_summary = PostSummary(
            title = title,
            likes = likes,
            views = views,
            comments = comments,
            timestamp = create_at.strftime("%Y-%m-%d %H:%M:%S"),
            nickname = nickname
        )
        post_summary_list.append(post_summary)

    return Response(
        message = "게시글 목록 조회",
        data = post_summary_list
    )

# 게시글 상세조회
def get_post(post_id: int, db: Session) -> Response:
    search_query = db.query(Post, User.nickname).join(User, Post.user_id == User.user_id
                                ).filter(Post.post_id == post_id).first()

    # 예외. : 잘못된 게시글 아이디 (삭제했거나...)
    if not search_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = {"message": "존재하지 않는 게시글입니다."}
        )

    # 언패킹
    post_info, nickname = search_query
    # 조회수 증가
    post_info.views += 1

    # DB 갱신
    try:
        db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"데이터베이스 오류 : {e}"}
        )

    post_detail_data = PostDetail(
        title = post_info.title,
        content = post_info.content,
        post_image = post_info.post_image,
        create_at = post_info.create_at.strftime("%Y-%m-%d %H:%M:%S"),
        likes = post_info.likes,
        views = post_info.views,
        comments = post_info.comments,
        nickname = nickname
    )

    return Response(
        message="200 OK",
        data = post_detail_data
    )

# 게시글 수정
def update_post(post_id: int, current_user: dict, db: Session, post: PostUpdate) -> Response:

    # 예외. 제목 or 내용 미입력
    if not post.title or not post.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = {"message": "제목, 내용을 모두 작성해주세요"}
        )

    post_info = db.query(Post).filter(Post.post_id == post_id).first()
    # 예외. : 잘못된 게시글 아이디
    if not post_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = {"message": "존재하지 않는 게시글입니다."}
        )

    auth_user_id = current_user.get("user_id")
    # 예외. : 현재 사용자 - 작성자 불일치
    if auth_user_id != post_info.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = {"message": "해당 게시글을 수정할 권한이 없습니다."}
        )

    post_info.title = post.title
    post_info.content = post.content
    post_info.post_image = post.post_image if post.post_image else None

    # DB 갱신
    try:
        db.commit()
        db.refresh(post_info)
        return Response(
            message="게시글 수정 완료",
            data=f"title : {post.title}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = {"message" : f"데이터베이스 갱신 중 오류 : {e}"}
        )

# 게시글 삭제
def remove_post(post_id: int, current_user: dict, db: Session) -> Response:
    # 예외 1: 잘못된 게시글 아이디
    post_info = db.query(Post).filter(Post.post_id == post_id).first()
    if not post_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "존재하지 않는 게시글입니다."}
        )

    auth_user_id = current_user.get("user_id")
    # 예외. 현재 사용자 - 작성자 불일치
    if post_info.user_id != auth_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = {"message": "해당 게시글을 삭제할 권한이 없습니다."}
        )

    db.delete(post_info)
    # DB 갱신
    try:
        db.commit()
        return Response(message = "게시글 삭제 완료")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"데이터베이스 갱신 중 오류 : {e}"}
        )


# 좋아요 추가
def post_like(post_id: int, current_user: dict, db: Session) -> Response:
    # 본인 글에 좋아요를 누를 수 있는가? -> 가능하다고본다...

    post_info = db.query(Post).filter(Post.post_id == post_id).first()
    # 예외. 존재하지 않는 게시글
    if not post_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = {"message": "존재하지 않는 게시글입니다."}
        )

    auth_user_id = current_user.get("user_id")
    is_exist = db.query(Postlike).filter((Postlike.post_id == post_id) & (
            Postlike.user_id == auth_user_id)).first()

    # 예외. 이미 좋아요 누름
    if is_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail = {"message" : "이미 좋아요를 눌렀습니다."}
        )

    # 좋아요 정보
    like_info = Postlike(
        post_id = post_id,
        user_id = auth_user_id
    )
    # DB 갱신
    try:
        db.add(like_info)
        # 좋아요 수 증가
        post_info.likes += 1
        db.commit()
        return Response(message = "좋아요를 눌렀습니다.")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"데이터베이스 갱신 중 오류 : {e}"}
        )

# 좋아요 눌렀는지 안눌렀는지 확인
def check_like(post_id: int, current_user: dict, db: Session) -> Response:
    post_info = db.query(Post).filter(Post.post_id == post_id).first()
    # 예외. 존재하지 않는 게시글
    if not post_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "존재하지 않는 게시글입니다."}
        )

    auth_user_id = current_user.get("user_id")
    is_exist = db.query(Postlike).filter((Postlike.post_id == post_id) & (
            Postlike.user_id == auth_user_id)).first()
    message_text = ""
    if is_exist:
        message_text = f"이미 {post_info.title} 게시글에 좋아요를 눌렀습니다."
    else:
        message_text = f"{post_info.title} 게시글에 좋아요를 누르지 않았습니다."

    return Response(message = message_text)

# 좋아요 취소
def remove_like(post_id: int, current_user: dict, db: Session) -> Response:
    post_info = db.query(Post).filter(Post.post_id == post_id).first()
    # 예외. 존재하지 않는 게시글
    if not post_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = {"message": "존재하지 않는 게시글입니다."}
        )

    auth_user_id = current_user.get("user_id")
    is_exist = db.query(Postlike).filter((Postlike.post_id == post_id) & (
            Postlike.user_id == auth_user_id)).first()

    # 예외. 좋아요 안누름
    if not is_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail = {"message" : "좋아요를 누르지 않았습니다."}
        )

    # 좋아요 취소
    db.delete(is_exist)

    # DB 갱신
    try:
        post_info.likes -= 1
        db.commit()
        return Response(message = "좋아요가 취소되었습니다.")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"데이터베이스 갱신 중 오류 : {e}"}
        )


# 댓글 작성
def create_comment(post_id: int, current_user: dict,
                   db: Session, comment_info: CommentInput) -> Response:
    # 예외. 댓글 내용 미입력
    content = comment_info.comment_text
    if content == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = { "message": "댓글 내용을 입력해주세요." }
        )

    post_info = db.query(Post).filter(Post.post_id == post_id).first()
    # 예외 1: 유효하지 않은 게시글 (ex: 댓글 작성할 때 게시글 삭제)
    if not post_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "존재하지 않는 게시글입니다."}
        )

    new_comment = Comment(
        post_id = post_id,
        commenter_id = current_user.get("user_id"),
        comment_text = content,
    )

    # DB 갱신
    try:
        db.add(new_comment)
        post_info.comments += 1
        db.commit()
        db.refresh(new_comment)
        return Response(message = "댓글이 작성되었습니다.")

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"데이터베이스 갱신 중 오류 : {e}"}
        )

# 댓글 조회
def get_comment(post_id: int, db: Session) -> Response:
    post_info = db.query(Post).filter(Post.post_id == post_id).first()
    # 예외. 잘못된 게시글 아이디
    if not post_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "존재하지 않는 게시글입니다."}
        )

    comment_list = db.query(
        User.nickname, Comment.create_at, Comment.comment_text
    ).join(User, Comment.commenter_id == User.user_id
           ).filter(Comment.post_id == post_id).all()

    return_comment_list = []
    for nickname, create_at, comment_text in comment_list:
        comment_info = CommentDetail(
            commenter_nickname = nickname,
            create_at = create_at.strftime("%Y-%m-%d %H:%M:%S"),
            comment_text = comment_text
        )
        return_comment_list.append(comment_info)

    return Response(
        message = "댓글 목록",
        data = return_comment_list
    )



# 댓글 수정
def update_comment(post_id: int, comment_id: int, current_user: dict,
                   db:Session, new_comment: CommentInput) -> Response:
    # 예외. 댓글 내용 미입력
    new_comment_text = new_comment.comment_text
    if new_comment_text == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = { "message": "댓글 내용을 입력해주세요." }
        )

    post_info = db.query(Post).filter(Post.post_id == post_id).first()
    # 예외. 잘못된 게시글 아이디
    if not post_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={ "message": "존재하지 않는 게시글입니다." }
        )

    # 예외. 잘못된 댓글 아이디
    comment_info = db.query(Comment).filter(Comment.comment_id == comment_id).first()
    if not comment_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = { "message": "댓글을 찾을 수 없습니다." }
        )

    # 예외. 사용자 - 댓글 작성자 불일치
    auth_user_id = current_user.get("user_id")
    if comment_info.commenter_id != auth_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = { "message": "댓글을 수정할 권한이 없습니다." }
        )

    comment_info.comment_text = new_comment_text

    # DB 갱신
    try:
        db.commit()
        db.refresh(comment_info)
        return Response(
            message = "댓글이 수정되었습니다.",
            data = {"message": f"{comment_info}"}
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"데이터베이스 갱신 중 오류 : {e}"}
        )

# 댓글 삭제
def delete_comment(post_id: int, comment_id: int, current_user: dict,
                   db: Session) -> Response:

    post_info = db.query(Post).filter(Post.post_id == post_id).first()
    # 예외. 잘못된 게시글 아이디
    if not post_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "존재하지 않는 게시글입니다."}
        )

    # 예외. 잘못된 댓글 아이디
    comment_info = db.query(Comment).filter(Comment.comment_id == comment_id).first()
    if not comment_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "댓글을 찾을 수 없습니다."}
        )

    # 예외. 사용자 - 댓글 작성자 불일치
    auth_user_id = current_user.get("user_id")
    if comment_info.commenter_id != auth_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "댓글을 삭제할 권한이 없습니다."}
        )

    # 댓글 삭제
    db.delete(comment_info)

    # DB 갱신
    try:
        post_info.comments -= 1
        db.commit()
        return Response(message = "댓글 삭제 완료")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"데이터베이스 갱신 중 오류 : {e}"}
        )