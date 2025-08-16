from beanie import Document


class Sudo(Document):
    user_id: int

    class Settings:
        name = "sudoers"
        indexes = ["user_id"]
