# week11 : 11주차 과제
## 1. 백엔드 - DB 연결
- 기존 프로젝트에서 Model 코드의 JSON 반환 대신에 데이터베이스 적용해서 데이터 반환하기
- Postman 테스트 필수 (예외처리 확실히!)

> commit : week11 (과제1) ~

> 이외 설명은 week11_1의 DB_
> pyproject.toml 참고
> 
> ❗실행 전 아래를 따라주세요❗


### 1. MySQL에 DB 만들기
> 로컬 DB를 만들어서 진행했기 때문에, 테스트 시 별도의 데이터베이스 및 테이블 생성 과정이 필요합니다.
>
> **week11_1** 폴더의 **commuinty_DB.sql** 파일을 개인 MySQL 워크벤치에서 오픈, 파일 내의 모든 쿼리를 실행해주세요.


### 2. config.py 수정하기
> 프로젝트의 config.py에서 테스트하려는 MySQL 환경에 맞게 아래의 정보를 수정해주세요.

- MYSQL_HOST 
- MYSQL_USER 
- MYSQL_PASSWORD

### 3. uvicorn으로 실행
> uvicorn으로 main.py를 실행합니다.


---
# week10 : 10주차 과제
## 1. FastAPI로 모델 서빙

- 모델 종류는 자신이 선택
- Postman 테스트 필수

> commit : week10 (과제1) ~

> pyproject.toml 참고
> 
> 모델 : YOLO 8
> 
> uvicorn으로 main.py로 실행

---
# week9 : 9주차 과제
## 1. HTTP 내용 정리

- 내용 공부 후, 키워드 리스팅 + 키워드마다 한줄정리.
- 한줄정리 시 참고자료 보지 않고 내 생각으로만 쓰기.

> commit : (과제1) ~

>  [바로가기(week9_1)](https://github.com/Resfebel/ktb_community-project-be/blob/main/week9_1)


---
## 2. FastAPI: Route, controller로 커뮤니티 백엔드 구현
- Route, Controller만 이용해서 커뮤니티 백엔드 FastAPI 구현하기
- Postman 테스트 필수

> commit : (과제2) ~

> ~~requirements.txt 설치 필수~~
> pyproject.toml 참고
> 
> uvicorn으로 main.py로 실행

---
## 3. 커뮤니티 서비스 HTTP REST API 사전 설계
- 커뮤니티 서비스를 위한 HTTP REST API 설계 및 작성
- 구글 스프레드시트를 활용

> commit : (과제3) ~

> [바로가기(week9_3)](https://github.com/Resfebel/ktb_community-project-be/tree/main/week9_3)

---
## 4. FastAPI: Route-Controller-Model 패턴 커뮤니티 백엔드 구현
- 과제 2에서 Model을 추가해 MVC 패턴을 적용한 커뮤니티 백엔드 구현
- Postman 테스트 필수 + 예외처리 열심히 할 것!

> commit : (과제4) ~

> ~~requirements.txt 설치 필수~~
> pyproject.toml 참고
> 
> uvicorn으로 main.py로 실행