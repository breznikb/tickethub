from tickethub.services.transform import transform_todo_to_ticket


def test_status_open_when_not_completed():
    todo = {"id": 1, "todo": "Do X", "completed": False, "userId": 1}
    result = transform_todo_to_ticket(todo, {})
    assert result["status"] == "open"


def test_status_closed_when_completed():
    todo = {"id": 1, "todo": "Do X", "completed": True, "userId": 1}
    result = transform_todo_to_ticket(todo, {})
    assert result["status"] == "closed"


def test_priority_derived_from_id_modulo_3():
    cases = {1: "medium", 2: "high", 3: "low", 4: "medium"}
    for ticket_id, expected in cases.items():
        todo = {"id": ticket_id, "todo": "x", "completed": False, "userId": 1}
        result = transform_todo_to_ticket(todo, {})
        assert result["priority"] == expected


def test_assignee_resolved_from_users():
    todo = {"id": 1, "todo": "x", "completed": False, "userId": 5}
    users_by_id = {5: {"id": 5, "username": "johnd"}}
    result = transform_todo_to_ticket(todo, users_by_id)
    assert result["assignee"] == "johnd"


def test_assignee_defaults_to_unknown_when_missing():
    todo = {"id": 1, "todo": "x", "completed": False, "userId": 999}
    result = transform_todo_to_ticket(todo, {})
    assert result["assignee"] == "unknown"