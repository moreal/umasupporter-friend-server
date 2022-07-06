from databases import Database

from app.env import DATABASE_URL

__all__ = ("database",)


database = Database(DATABASE_URL)
