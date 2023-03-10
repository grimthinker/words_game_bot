import typing

from hashlib import sha256
from sqlalchemy import select

from app.admin.models import Admin, AdminModel
from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        admin = await self.get_by_email(email=app.config.admin.email)
        if not admin:
            await self.create_admin(
                email=app.config.admin.email, password=app.config.admin.password
            )

    async def get_by_email(self, email: str) -> typing.Optional[Admin]:
        async with self.app.database.session.begin() as db_session:
            stmt = select(AdminModel).where(AdminModel.email == email)
            result = await db_session.execute(stmt)
            curr = result.scalars()
            for admin in curr:
                return Admin(admin.id, admin.email, admin.password)

    async def create_admin(self, email: str, password: str):
        async with self.app.database.session.begin() as db_session:
            password = sha256(password.encode()).hexdigest()
            admin = AdminModel(email=email, password=password)
            db_session.add(admin)
