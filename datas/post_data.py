from typing import Dict, Any
from datetime import datetime

### TEST JSON DATA
# [post_id, [post_info]]
POST_DATA: Dict[int, Dict[str, Any]] = {
    1: {
        "user_id": 1,
        "title": "Test Post 1 by tester_1",
        "content": "Hello world!!",
        "post_image": None,
        "date": datetime(2025, 11, 17, 10, 10, 50).strftime("%Y-%m-%d %H:%M:%S"),
        "like": 10,
        "views": 35,
        "comments": {
            1: {
                "comment_id": 1,
                "commenter_id": 1,
                "author": "tester_1",
                "comment_content": "nice",
                "date": datetime(2025, 11, 17, 11, 40, 29).strftime("%Y-%m-%d %H:%M:%S")
            },
            2: {
                "comment_id": 2,
                "commenter_id": 2,
                "author": "tester_2",
                "comment_content": "good good",
                "date": datetime(2025, 11, 17, 17, 30, 20).strftime("%Y-%m-%d %H:%M:%S")
            }
        },
        "next_comment_id": 3
    },
    2: {
        "user_id": 1,
        "title": "Test Post 2 by tester_1",
        "content": "test test test test",
        "post_image": None,
        "date": datetime(2025, 11, 17, 13, 29, 45).strftime("%Y-%m-%d %H:%M:%S"),
        "like": 10,
        "views": 35,
        "comments": {
            1: {
                "comment_id": 1,
                "commenter_id": 2,
                "author": "tester_2",
                "comment_content": "test comment by tester_2",
                "date": datetime(2025, 11, 17, 20, 30, 20).strftime("%Y-%m-%d %H:%M:%S")
            }
        },
        "next_comment_id": 2
    },
    3: {
        "user_id": 2,
        "title": "Test Post 3 by tester_2",
        "content": "new test content",
        "post_image": None,
        "date": datetime(2025, 11, 17, 22, 30, 39).strftime("%Y-%m-%d %H:%M:%S"),
        "like": 0,
        "views": 0,
        "comments": {
            1: {
                "comment_id": 1,
                "commenter_id": 1,
                "author": "tester_1",
                "comment_content": "test comment by tester_2",
                "date": datetime(2025, 11, 17, 23, 30, 20).strftime("%Y-%m-%d %H:%M:%S")
            }
        },
        "next_comment_id": 2
    }
}

post_id_counter = 4