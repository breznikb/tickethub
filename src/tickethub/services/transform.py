PRIORITY_LEVELS = ["low", "medium", "high"]


def transform_todo_to_ticket(todo: dict, users_by_id: dict[int, dict]) -> dict:
    user = users_by_id.get(todo["userId"])
    assignee = user["username"] if user else "unknown"

    return {
        "id": todo["id"],
        "title": todo["todo"],
        "status": "closed" if todo["completed"] else "open",
        "priority": PRIORITY_LEVELS[todo["id"] % 3],
        "assignee": assignee,
        "source_data": todo
    }
