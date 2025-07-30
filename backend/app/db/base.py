"""Import all models to ensure they are registered with SQLAlchemy."""

from app.db.database import Base  # noqa
from app.models.user import User  # noqa
from app.models.category import Category  # noqa
from app.models.tag import Tag  # noqa
from app.models.event import Event  # noqa
from app.models.review import Review  # noqa
from app.models.event_tag import event_tags  # noqa