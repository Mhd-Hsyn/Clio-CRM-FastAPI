from passlib.hash import pbkdf2_sha256
from sqlalchemy.orm import validates
from app.core.constants.choices import UserRoleChoices, UserAccountStatusChoices

class PasswordMixin:
    @validates("password")
    def hash_password(self, key, value):
        if value:
            return pbkdf2_sha256.hash(value)
        return value

    def check_password(self, raw_password: str) -> bool:
        return pbkdf2_sha256.verify(raw_password, self.password)

class UserModelMixin:
    @property
    def full_name(self):
        return " ".join(filter(None, [self.first_name, self.middle_name, self.last_name]))

    @property
    def role_name(self):
        return UserRoleChoices(self.role).name

    @property
    def account_status_name(self):
        return UserAccountStatusChoices(self.account_status).name

