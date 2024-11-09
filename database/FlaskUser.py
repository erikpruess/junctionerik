from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email, role):
        self.id = id
        self.email = email
        self.role = role

    @staticmethod
    def get(db, user_id: int):
        user_row = db._fetch_one('SELECT * FROM users WHERE id = ?', user_id)
        if user_row:
            return User(user_row['id'], user_row['email'], user_row['role'])
        return None
