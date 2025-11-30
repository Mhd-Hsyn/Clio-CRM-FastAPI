from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.models.base import BaseModel
from app.core.constants.choices import UserRoleChoices, UserAccountStatusChoices
from app.core.models.mixins import FileHandlerMixin
from .mixins import (
    PasswordMixin, 
    UserModelMixin,
)
from app.config.storage.factory import storage


class UserModel(BaseModel, PasswordMixin, UserModelMixin, FileHandlerMixin):
    __tablename__ = "users"

    first_name = Column(String, nullable=False)
    middle_name = Column(String)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    mobile_number = Column(String)
    role = Column(Integer, default=UserRoleChoices.CLIENT)
    account_status = Column(Integer, default=UserAccountStatusChoices.PENDING)
    is_active = Column(Boolean, default=True)
    is_staff = Column(Boolean, default=False)
    is_email_verified = Column(Boolean, default=False)
    password = Column(String, nullable=False)
    profile_image: str = Column(
        String, 
        default="dummy/user.png", 
        info={"upload_to": "users/profile"}
    )

    whitelist_tokens = relationship("UserWhitelistTokenModel", back_populates="user")

    __file_fields__ = {
        "profile_image": "users/profile",
    }

    async def profile_image_url(self) -> str:
        return await storage.url(self.profile_image)



class UserWhitelistTokenModel(BaseModel):
    __tablename__ = "user_whitelist_tokens"

    user_id = Column(ForeignKey("users.id"), nullable=False)
    access_token_fingerprint = Column(String(64), unique=True)
    refresh_token_fingerprint = Column(String(64), unique=True)
    useragent = Column(String)

    user = relationship("UserModel", back_populates="whitelist_tokens")

