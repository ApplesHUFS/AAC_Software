class AACUserManager:
    def __init__(self):
        self.users = {}  # {user_id: user_data 딕셔너리 구조 예시}

    def add_user(self, user_id: str, name: str, age: int):
        """새 사용자 등록"""
        self.users[user_id] = {
            "name": name,
            "age": age
        }
        print(f"[UserManager] 사용자 {name} 추가 완료")

    def get_user(self, user_id: str):
        """사용자 정보 불러오기"""
        return self.users.get(user_id, None)

    def delete_user(self, user_id: str):
        """사용자 삭제"""
        if user_id in self.users:
            del self.users[user_id]
            print(f"[UserManager] 사용자 {user_id} 삭제 완료")
