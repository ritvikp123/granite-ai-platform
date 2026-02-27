from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.role import Role
from app.models.user import User


DEFAULT_ROLES = ["admin", "manager", "operations", "procurement"]


def seed_defaults(db: Session) -> None:
    roles_by_name: dict[str, Role] = {}
    for role_name in DEFAULT_ROLES:
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            role = Role(name=role_name)
            db.add(role)
            db.flush()
        roles_by_name[role_name] = role

    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123!"),
            is_active=True,
            roles=[roles_by_name["admin"]],
        )
        db.add(admin_user)

    db.commit()
