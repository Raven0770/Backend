class MessageRepository:
    """
    Repository Layer:
    Responsible ONLY for data access (e.g., querying a database).
    For now, instead of a real DB, it uses simple dummy messages.
    """

    def get_welcome_message(self) -> str:
        # Later, this could be: db.query(Message).first()
        return "Hello from the Repository layer! (No database connected yet)"

    def save_message(self, username: str, text: str) -> str:
        # Later, this could be: db.add(Message(...)); db.commit()
        return f"Saved dummy message from '{username}': {text}"
