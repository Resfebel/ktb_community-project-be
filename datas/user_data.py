from typing import Dict, Any


### TEST JSON DATA
USER_DATA: Dict[str, Dict[str, Any]] = {
    "test1@ktbai.kr": {
        "user_id": 1,
        "email": "test1@ktbai.kr",
        # 해싱값 변경 필요
        "password": "Test123!",
        "nickname": "tester_1",
        "profile_image": None
    },
    "test2@ktbai.kr": {
        "user_id": 2,
        "email": "test2@ktbai.kr",
        # 해싱값 변경 필요
        "password": "Test123!",
        "nickname": "tester_2",
        "profile_image": None
    }
}

user_id_counter = 3