import json
from app.auth.models import UserWhitelistTokenModel
from app.core.utils.helpers import generate_fingerprint
from app.core.exceptions.base import UnauthorizedException
from app.auth.services.jwt_handler import JWTHandler
from sqlalchemy.orm import Session
from fastapi.concurrency import run_in_threadpool

class AuthService:
    def __init__(self, jwt_key: str):
        self.jwt_handler = JWTHandler(jwt_key)

    async def generate_jwt_payload(
        self,
        user,
        request,
        db: Session,
        access_token_duration={"days": 1},
        refresh_token_duration={"days": 7}
    ):
        access_token = self.jwt_handler.generate_token(
            user.id, user.email, user.role, access_token_duration
        )
        refresh_token = self.jwt_handler.generate_token(
            user.id, user.email, user.role, refresh_token_duration
        )

        user_agent_info = {
            "browser_agent": request.headers.get("user-agent", "Unknown"),
            "ip": request.client.host,
        }

        token_entry = UserWhitelistTokenModel(
            user_id=user.id,
            access_token_fingerprint=generate_fingerprint(access_token),
            refresh_token_fingerprint=generate_fingerprint(refresh_token),
            useragent=json.dumps(user_agent_info),
        )

        # Use threadpool to run sync DB commit in async context
        def commit_token():
            db.add(token_entry)
            db.commit()
            db.refresh(token_entry)

        await run_in_threadpool(commit_token)

        return {
            "status": True,
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    async def verify_jwt(self, token: str, db: Session):
        payload = self.jwt_handler.decode_token(token)
        fingerprint = generate_fingerprint(token)

        def get_token():
            return db.query(UserWhitelistTokenModel).filter(
                UserWhitelistTokenModel.access_token_fingerprint == fingerprint
            ).first()

        token_instance = await run_in_threadpool(get_token)

        if not token_instance:
            raise UnauthorizedException("Token is not whitelisted")

        # Return associated user (SQLAlchemy relationship)
        return token_instance.user

