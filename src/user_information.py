class AACUserManager:
    def __init__(self):
        self.users = {}

    def add_user(self, user_id: str, name: str, age: int, gender: str,
                 disability_type: str, communication_characteristics: str, password: str):
        """
        새 사용자 등록
        gender: '남', '여' 또는 기타 표기
        disability_type: 장애 종류 (예: 시각, 청각, 지적, 지체 등)
        communication_characteristics: 의사소통 특성 (예: 구어, 보완대체의사소통, 점자 등)
        password: 비밀번호 (문자열)
        """
        self.users[user_id] = {
            "name": name,
            "age": age,
            "gender": gender,
            "disability_type": disability_type,
            "communication_characteristics": communication_characteristics,
            "password": password
        }
        print(f"[UserManager] 사용자 {name}({user_id}) 등록 완료")

    def get_user(self, user_id: str):
        """사용자 정보 반환 (비밀번호 제외)"""
        user = self.users.get(user_id)
        if user:
            return {k: v for k, v in user.items() if k != "password"}
        return None

    def check_password(self, user_id: str, password: str) -> bool:
        """비밀번호 확인"""
        user = self.users.get(user_id)
        return user and user["password"] == password

    def delete_user(self, user_id: str):
        """사용자 삭제"""
        if user_id in self.users:
            del self.users[user_id]
            print(f"[UserManager] 사용자 {user_id} 삭제 완료")
