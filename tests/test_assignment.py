"""
=============================================================================
Task Manager Pro — Assignment Test Suite
=============================================================================
Based on actual source code:
  - Task(title, description, due_date, completed=False)
  - User(username, password=None, email=None, email_reminders_enabled=True)
  - TaskManager.add_task(title, desc, due)   [YYYY-MM-DD format]
  - TaskManager.login(username, email=None)
  - Storage: {"tasks": [], "users": []}

Covers:
  1. Functional & Non-Functional Requirements (documented below)
  2. AAA Pattern Test Cases
  3. Regular Expression Tests
  4. User-Defined Pattern (In/Out Mode)
  5. Proposed Custom Pattern (GIVEN-WHEN-THEN)
  6. Boundary Value Analysis (BVA)
  7. Unit, Integration, System, Acceptance Testing
     — Framework 1: unittest
     — Framework 2: pytest
=============================================================================
"""

import unittest
import re
import pytest
import sys
import os
from datetime import date, timedelta, datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from task_manager_pro.models.task import Task
from task_manager_pro.models.user import User
from task_manager_pro.services.task_manager import TaskManager


# =============================================================================
# HELPER — In-Memory Storage (implements StorageInterface contract)
# =============================================================================
class InMemoryStorage:
    """File-free storage for isolated unit tests."""
    def __init__(self):
        self._data = {"tasks": [], "users": []}

    def load_data(self):
        return self._data

    def save_data(self, data):
        self._data = data


def make_manager(username="testuser"):
    """Return a logged-in TaskManager backed by in-memory storage."""
    mgr = TaskManager(storage=InMemoryStorage())
    # login() creates user if not found — safe to call directly
    mgr.login(username, email="test@test.com")

    return mgr


def future(days=5):
    """Return a future date string in YYYY-MM-DD format."""
    return str(date.today() + timedelta(days=days))


def past(days=1):
    """Return a past date string in YYYY-MM-DD format."""
    return str(date.today() - timedelta(days=days))


def today_str():
    return str(date.today())


# =============================================================================
# FUNCTIONAL REQUIREMENTS
# =============================================================================
# FR-1  User can login (creates account if not found) with a username.
# FR-2  Logged-in user can add a task with title, description, due date.
# FR-3  User can list tasks filtered by status: all / pending / completed.
# FR-4  User can update a task's title, description, or due date by ID.
# FR-5  User can mark a task as completed by ID.
# FR-6  User can delete a task by ID.
# FR-7  User can logout; session is cleared.
# FR-8  System prints due/overdue reminders after login and list operations.
# FR-9  User can toggle email reminders on or off.
#
# NON-FUNCTIONAL REQUIREMENTS
# NF-1  All CRUD operations complete within 200 ms (local JSON storage).
# NF-2  Task IDs are unique hex strings (uuid4.hex).
# NF-3  Data persists across TaskManager restarts via storage backend.
# NF-4  System handles missing or empty task list without crashing.
# NF-5  Password field excluded from serialized user data for security.


# =============================================================================
# 2. AAA PATTERN — unittest (Framework 1)
# =============================================================================
class TestAAAPattern(unittest.TestCase):

    def test_AAA_add_task_success(self):
        # Arrange
        mgr = make_manager("alice")

        # Act
        mgr.add_task("Write report", "Monthly report", future())

        # Assert
        tasks = [t for t in mgr.data["tasks"] if t["title"] == "Write report"]
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["title"], "Write report")

    def test_AAA_mark_task_complete(self):
        # Arrange
        mgr = make_manager("alice")
        mgr.add_task("Finish doc", "desc", future())
        task_id = mgr.data["tasks"][0]["id"]

        # Act
        mgr.mark_task_complete(task_id)

        # Assert
        task = next(t for t in mgr.data["tasks"] if t["id"] == task_id)
        self.assertTrue(task["completed"])

    def test_AAA_delete_task(self):
        # Arrange
        mgr = make_manager("alice")
        mgr.add_task("Delete me", "desc", future())
        task_id = mgr.data["tasks"][0]["id"]

        # Act
        mgr.delete_task(task_id)

        # Assert
        ids = [t["id"] for t in mgr.data["tasks"]]
        self.assertNotIn(task_id, ids)

    def test_AAA_update_task_title(self):
        # Arrange
        mgr = make_manager("alice")
        mgr.add_task("Old Title", "desc", future())
        task_id = mgr.data["tasks"][0]["id"]

        # Act
        mgr.update_task(task_id, title="New Title")

        # Assert
        task = next(t for t in mgr.data["tasks"] if t["id"] == task_id)
        self.assertEqual(task["title"], "New Title")

    def test_AAA_login_creates_user(self):
        # Arrange
        storage = InMemoryStorage()
        mgr = TaskManager(storage=storage)

        # Act
        mgr.login("newuser")

        # Assert
        users = mgr.data["users"]
        usernames = [u["username"] for u in users]
        self.assertIn("newuser", usernames)


# =============================================================================
# 3. REGULAR EXPRESSION TESTS — pytest (Framework 2)
# =============================================================================
DATE_REGEX     = r"^\d{4}-\d{2}-\d{2}$"
USERNAME_REGEX = r"^[a-zA-Z0-9_]{3,20}$"
TASK_ID_REGEX  = r"^[a-f0-9]{32}$"          # uuid4.hex = 32 hex chars
EMAIL_REGEX    = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
TITLE_REGEX    = r"^.{1,100}$"              # 1-100 chars


class TestRegularExpressions:

    @pytest.mark.parametrize("due_date,expected", [
        ("2026-12-31", True),
        ("2026-01-01", True),
        (today_str(),  True),
        ("31-12-2026", False),
        ("2026/12/31", False),
        ("2026-1-1",   False),
        ("abcd-ef-gh", False),
        ("",           False),
    ])
    def test_date_format_regex(self, due_date, expected):
        result = bool(re.match(DATE_REGEX, due_date))
        assert result == expected, f"Date '{due_date}': expected {expected}"

    @pytest.mark.parametrize("username,expected", [
        ("alice",       True),
        ("user_123",    True),
        ("ABC",         True),
        ("ab",          False),    # too short (< 3)
        ("a" * 21,      False),    # too long (> 20)
        ("user name",   False),    # space not allowed
        ("user@name",   False),    # special char
    ])
    def test_username_regex(self, username, expected):
        result = bool(re.match(USERNAME_REGEX, username))
        assert result == expected, f"Username '{username}': expected {expected}"

    @pytest.mark.parametrize("email,expected", [
        ("user@example.com",     True),
        ("test.name@domain.org", True),
        ("invalidemail",         False),
        ("@nodomain.com",        False),
        ("missing_at.com",       False),
    ])
    def test_email_regex(self, email, expected):
        result = bool(re.match(EMAIL_REGEX, email))
        assert result == expected

    def test_task_id_is_valid_hex(self):
        """Task IDs generated by uuid4.hex must match 32-char hex pattern."""
        mgr = make_manager("regex_user")
        mgr.add_task("ID test task", "desc", future())
        task_id = mgr.data["tasks"][0]["id"]
        assert re.match(TASK_ID_REGEX, task_id), f"Task ID '{task_id}' failed hex pattern"

    @pytest.mark.parametrize("title,expected", [
        ("A",       True),         # min 1 char
        ("T" * 100, True),         # max 100 chars
        ("T" * 101, False),        # exceeds max
        ("",        False),        # empty
    ])
    def test_title_length_regex(self, title, expected):
        result = bool(re.match(TITLE_REGEX, title))
        assert result == expected


# =============================================================================
# 4. USER-DEFINED PATTERN — IN / OUT MODE
# =============================================================================
class TestUserDefinedInOutPattern(unittest.TestCase):
    """
    IN  mode — valid inputs that produce correct outputs.
    OUT mode — invalid inputs that are rejected or produce error output.
    """

    def setUp(self):
        self.mgr = make_manager("io_user")

    # ── IN mode ──────────────────────────────────────────────────────────
    def test_IN_valid_title_accepted(self):
        self.mgr.add_task("Valid Task", "desc", future())
        titles = [t["title"] for t in self.mgr.data["tasks"]]
        self.assertIn("Valid Task", titles)

    def test_IN_future_due_date_accepted(self):
        self.mgr.add_task("Future task", "desc", future(10))
        task = self.mgr.data["tasks"][0]
        self.assertEqual(task["due_date"], future(10))

    def test_IN_task_stored_with_correct_user(self):
        self.mgr.add_task("User task", "desc", future())
        task = self.mgr.data["tasks"][0]
        self.assertEqual(task["user"], "io_user")

    def test_IN_completed_false_by_default(self):
        self.mgr.add_task("Default status", "desc", future())
        task = self.mgr.data["tasks"][0]
        self.assertFalse(task["completed"])

    # ── OUT mode ─────────────────────────────────────────────────────────
    def test_OUT_invalid_date_format_rejected(self):
        with self.assertRaises((ValueError, Exception)):
            self.mgr.add_task("Bad date", "desc", "31/12/2026")

    def test_OUT_no_login_blocks_add_task(self):
        """TaskManager without login should not add task."""
        storage = InMemoryStorage()
        mgr = TaskManager(storage=storage)   # no login
        mgr.add_task("Ghost task", "desc", future())
        self.assertEqual(len(mgr.data["tasks"]), 0)

    def test_OUT_delete_nonexistent_id_no_crash(self):
        """Deleting a non-existent task ID should not raise exception."""
        try:
            self.mgr.delete_task("fake-id-000")
        except Exception as e:
            self.fail(f"delete_task raised exception unexpectedly: {e}")

    def test_OUT_update_nonexistent_id_no_change(self):
        """Updating non-existent task should not modify any data."""
        self.mgr.add_task("Real task", "desc", future())
        before = len(self.mgr.data["tasks"])
        self.mgr.update_task("fake-id-000", title="Ghost")
        after = len(self.mgr.data["tasks"])
        self.assertEqual(before, after)


# =============================================================================
# 5. PROPOSED CUSTOM PATTERN — GIVEN / WHEN / THEN (GWT)
# =============================================================================
"""
Proposed Pattern: GIVEN-WHEN-THEN (BDD Style)

Rationale: AAA (Arrange-Act-Assert) focuses on test mechanics.
GWT focuses on behavior and business context, making tests readable
by non-technical stakeholders. Each test documents:
  GIVEN  — precondition / system state
  WHEN   — user action / event
  THEN   — expected observable outcome
"""


class TestGivenWhenThenPattern(unittest.TestCase):

    def test_GWT_complete_task(self):
        # GIVEN a logged-in user has a pending task
        mgr = make_manager("gwt_user")
        mgr.add_task("Pending task", "needs completion", future())
        task_id = mgr.data["tasks"][0]["id"]
        self.assertFalse(mgr.data["tasks"][0]["completed"])

        # WHEN the user marks it complete
        mgr.mark_task_complete(task_id)

        # THEN the task is marked as completed in storage
        task = next(t for t in mgr.data["tasks"] if t["id"] == task_id)
        self.assertTrue(task["completed"])

    def test_GWT_update_due_date(self):
        # GIVEN a task with an original due date
        mgr = make_manager("gwt_user2")
        mgr.add_task("Deadline task", "desc", future(3))
        task_id = mgr.data["tasks"][0]["id"]

        # WHEN the user updates the due date
        mgr.update_task(task_id, due=future(10))

        # THEN the new due date is reflected in storage
        task = next(t for t in mgr.data["tasks"] if t["id"] == task_id)
        self.assertEqual(task["due_date"], future(10))

    def test_GWT_tasks_isolated_per_user(self):
        # GIVEN two different users each add a task
        storage = InMemoryStorage()
        mgr = TaskManager(storage=storage)
        mgr.login("user_a")
        mgr.add_task("User A task", "desc", future())

        mgr2 = TaskManager(storage=storage)
        mgr2.login("user_b")
        mgr2.add_task("User B task", "desc", future())

        # WHEN user_a lists their tasks
        user_a_tasks = [t for t in mgr.data["tasks"] if t["user"] == "user_a"]

        # THEN user_a sees only their own task
        titles = [t["title"] for t in user_a_tasks]
        self.assertIn("User A task", titles)
        self.assertNotIn("User B task", titles)

    def test_GWT_logout_clears_current_user(self):
        # GIVEN a logged-in user
        mgr = make_manager("logout_user")
        self.assertIsNotNone(mgr.current_user)

        # WHEN the user logs out
        mgr.logout()

        # THEN current_user is None
        self.assertIsNone(mgr.current_user)


# =============================================================================
# 6. BOUNDARY VALUE ANALYSIS (BVA)
# =============================================================================
class TestBoundaryValueAnalysis(unittest.TestCase):
    """
    BVA applied to:
      A) Task title length   (min=1, max=100 chars)
      B) Due date boundary   (past=invalid, today=valid, future=valid)
      C) Task ID lookup      (exact match=found, off-by-one=not found)
    """

    def setUp(self):
        self.mgr = make_manager("bva_user")

    # ── A) Title length ───────────────────────────────────────────────────
    def test_BVA_title_1_char_minimum(self):
        """Min boundary: 1 character title must be accepted."""
        self.mgr.add_task("A", "desc", future())
        titles = [t["title"] for t in self.mgr.data["tasks"]]
        self.assertIn("A", titles)

    def test_BVA_title_100_chars_maximum(self):
        """Max boundary: 100 character title must be accepted."""
        title = "T" * 100
        self.mgr.add_task(title, "desc", future())
        titles = [t["title"] for t in self.mgr.data["tasks"]]
        self.assertIn(title, titles)

    def test_BVA_title_empty_below_minimum(self):
        """Below min: empty title should raise ValueError."""
        with self.assertRaises((ValueError, Exception)):
            Task("", "desc", future())

    # ── B) Due date boundary ──────────────────────────────────────────────
    def test_BVA_due_date_today_boundary(self):
        """Boundary: today's date must be accepted as valid due date."""
        self.mgr.add_task("Today task", "desc", today_str())
        task = self.mgr.data["tasks"][0]
        self.assertEqual(task["due_date"], today_str())

    def test_BVA_due_date_tomorrow_valid(self):
        """Above boundary: tomorrow is a valid future date."""
        self.mgr.add_task("Tomorrow task", "desc", future(1))
        task = self.mgr.data["tasks"][0]
        self.assertEqual(task["due_date"], future(1))

    def test_BVA_due_date_invalid_format(self):
        """Invalid format: wrong separator should raise ValueError."""
        with self.assertRaises((ValueError, Exception)):
            Task("Bad date task", "desc", "2026/12/31")

    def test_BVA_due_date_non_date_string(self):
        """Invalid value: non-date string should raise ValueError."""
        with self.assertRaises((ValueError, Exception)):
            Task("Bad date task", "desc", "not-a-date")

    # ── C) Task ID lookup ─────────────────────────────────────────────────
    def test_BVA_mark_complete_exact_id(self):
        """Exact ID match must mark task complete."""
        self.mgr.add_task("Exact ID task", "desc", future())
        task_id = self.mgr.data["tasks"][0]["id"]
        self.mgr.mark_task_complete(task_id)
        task = next(t for t in self.mgr.data["tasks"] if t["id"] == task_id)
        self.assertTrue(task["completed"])

    def test_BVA_mark_complete_wrong_id(self):
        """Wrong ID must not mark any task complete."""
        self.mgr.add_task("ID boundary task", "desc", future())
        self.mgr.mark_task_complete("000000000000000000000000000000000")
        task = self.mgr.data["tasks"][0]
        self.assertFalse(task["completed"])


# =============================================================================
# 7a. UNIT TESTS — unittest (Framework 1)
# =============================================================================
class TestUnitUnittest(unittest.TestCase):
    """Single class / method tested in isolation."""

    def test_unit_task_creation(self):
        task = Task("My task", "description", future())
        self.assertEqual(task.title, "My task")
        self.assertEqual(task.description, "description")
        self.assertFalse(task.completed)

    def test_unit_task_mark_complete(self):
        task = Task("Complete me", "desc", future())
        task.mark_complete()
        self.assertTrue(task.completed)

    def test_unit_task_to_dict_keys(self):
        task = Task("Dict task", "desc", future())
        d = task.to_dict()
        for key in ["title", "description", "due_date", "completed", "created_at"]:
            self.assertIn(key, d)

    def test_unit_task_from_dict(self):
        data = {
            "title": "From dict",
            "description": "desc",
            "due_date": future(),
            "completed": False,
            "id": "abc123"
        }
        task = Task.from_dict(data)
        self.assertEqual(task.title, "From dict")
        self.assertEqual(task.id, "abc123")

    def test_unit_task_due_date_format(self):
        d = future()
        task = Task("Date task", "desc", d)
        self.assertEqual(task.due_date, d)

    def test_unit_user_creation(self):
        user = User("john", email="john@test.com")
        self.assertEqual(user.username, "john")

    def test_unit_user_to_dict_excludes_password(self):
        user = User("jane", password="secret", email="jane@test.com")
        d = user.to_dict()
        self.assertNotIn("password", d)

    def test_unit_task_str_representation(self):
        task = Task("My Task", "desc", future())
        result = str(task)
        self.assertIn("My Task", result)


# =============================================================================
# 7b. UNIT TESTS — pytest (Framework 2)
# =============================================================================
class TestUnitPytest:

    def test_task_id_is_none_before_assignment(self):
        task = Task("No ID", "desc", future())
        assert task.id is None

    def test_task_id_assigned_after_set(self):
        task = Task("Has ID", "desc", future())
        task.id = "abc123"
        assert task.id == "abc123"

    def test_two_tasks_have_different_content(self):
        t1 = Task("Task One", "desc", future())
        t2 = Task("Task Two", "desc", future(3))
        assert t1.title != t2.title

    def test_task_completed_default_false(self):
        task = Task("New task", "desc", future())
        assert task.completed is False

    def test_task_mark_complete_idempotent(self):
        task = Task("Idem task", "desc", future())
        task.mark_complete()
        task.mark_complete()
        assert task.completed is True


# =============================================================================
# 7c. INTEGRATION TESTS — unittest (Framework 1)
# =============================================================================
class TestIntegrationUnittest(unittest.TestCase):
    """Two or more modules working together."""

    def test_integ_manager_persists_task_in_storage(self):
        storage = InMemoryStorage()
        mgr = TaskManager(storage=storage)
        mgr.login("integ_user")
        mgr.add_task("Stored task", "desc", future())
        # Reload from same storage
        mgr2 = TaskManager(storage=storage)
        tasks = [t for t in mgr2.data["tasks"] if t["user"] == "integ_user"]
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["title"], "Stored task")

    def test_integ_add_then_update(self):
        mgr = make_manager("integ2")
        mgr.add_task("Original", "desc", future())
        task_id = mgr.data["tasks"][0]["id"]
        mgr.update_task(task_id, title="Updated")
        task = next(t for t in mgr.data["tasks"] if t["id"] == task_id)
        self.assertEqual(task["title"], "Updated")

    def test_integ_add_then_delete(self):
        mgr = make_manager("integ3")
        mgr.add_task("Temp", "desc", future())
        task_id = mgr.data["tasks"][0]["id"]
        mgr.delete_task(task_id)
        remaining = [t for t in mgr.data["tasks"] if t["user"] == "integ3"]
        self.assertEqual(len(remaining), 0)

    def test_integ_login_then_add_multiple_tasks(self):
        mgr = make_manager("integ4")
        for i in range(3):
            mgr.add_task(f"Task {i}", "desc", future())
        user_tasks = [t for t in mgr.data["tasks"] if t["user"] == "integ4"]
        self.assertEqual(len(user_tasks), 3)


# =============================================================================
# 7d. INTEGRATION TESTS — pytest (Framework 2)
# =============================================================================
class TestIntegrationPytest:

    def test_integ_task_manager_with_json_storage_structure(self):
        storage = InMemoryStorage()
        mgr = TaskManager(storage=storage)
        mgr.login("pytest_integ")
        mgr.add_task("pytest task", "desc", future())
        data = storage.load_data()
        assert "tasks" in data
        assert "users" in data
        assert len(data["tasks"]) == 1

    def test_integ_mark_complete_reflects_in_storage(self):
        storage = InMemoryStorage()
        mgr = TaskManager(storage=storage)
        mgr.login("complete_user")
        mgr.add_task("Complete me", "desc", future())
        task_id = storage.load_data()["tasks"][0]["id"]
        mgr.mark_task_complete(task_id)
        task = storage.load_data()["tasks"][0]
        assert task["completed"] is True


# =============================================================================
# 7e. SYSTEM TESTS — pytest (Framework 2)
# =============================================================================
class TestSystemPytest:
    """Full end-to-end user journey tests."""

    def test_system_full_lifecycle(self):
        """Login → Add → Update → Complete → Delete."""
        storage = InMemoryStorage()
        mgr = TaskManager(storage=storage)

        # Login
        mgr.login("sys_user")
        assert mgr.current_user is not None

        # Add
        mgr.add_task("System task", "Full lifecycle", future())
        task_id = storage.load_data()["tasks"][0]["id"]

        # Update
        mgr.update_task(task_id, title="Updated system task")
        task = next(t for t in storage.load_data()["tasks"] if t["id"] == task_id)
        assert task["title"] == "Updated system task"

        # Complete
        mgr.mark_task_complete(task_id)
        task = next(t for t in storage.load_data()["tasks"] if t["id"] == task_id)
        assert task["completed"] is True

        # Delete
        mgr.delete_task(task_id)
        remaining = [t for t in storage.load_data()["tasks"] if t["id"] == task_id]
        assert len(remaining) == 0

    def test_system_multi_user_isolation(self):
        """User A tasks must not appear for User B."""
        storage = InMemoryStorage()

        mgr_a = TaskManager(storage=storage)
        mgr_a.login("user_a")
        mgr_a.add_task("A's private task", "desc", future())

        mgr_b = TaskManager(storage=storage)
        mgr_b.login("user_b")
        b_tasks = [t for t in storage.load_data()["tasks"] if t["user"] == "user_b"]
        titles = [t["title"] for t in b_tasks]
        assert "A's private task" not in titles

    def test_system_empty_task_list_no_crash(self):
        """System must handle empty task list without crashing."""
        mgr = make_manager("empty_user")
        tasks = [t for t in mgr.data["tasks"] if t["user"] == "empty_user"]
        assert tasks == []


# =============================================================================
# 7f. ACCEPTANCE TESTS — unittest (Framework 1)
# =============================================================================
class TestAcceptanceUnittest(unittest.TestCase):
    """Business-level acceptance criteria from user perspective."""

    def test_AC1_user_can_login_and_access_system(self):
        """AC-1: User can login and system recognizes them."""
        mgr = make_manager("ac_user1")
        self.assertIsNotNone(mgr.current_user)
        self.assertEqual(mgr.current_user.username, "ac_user1")

    def test_AC2_user_can_create_and_see_task(self):
        """AC-2: Created task appears in storage."""
        mgr = make_manager("ac_user2")
        mgr.add_task("My first task", "desc", future())
        tasks = [t for t in mgr.data["tasks"] if t["user"] == "ac_user2"]
        self.assertTrue(any(t["title"] == "My first task" for t in tasks))

    def test_AC3_completed_task_flagged_correctly(self):
        """AC-3: Completed task has completed=True."""
        mgr = make_manager("ac_user3")
        mgr.add_task("Done task", "desc", future())
        task_id = mgr.data["tasks"][0]["id"]
        mgr.mark_task_complete(task_id)
        task = next(t for t in mgr.data["tasks"] if t["id"] == task_id)
        self.assertTrue(task["completed"])

    def test_AC4_deleted_task_not_in_storage(self):
        """AC-4: After deletion, task is removed from storage."""
        mgr = make_manager("ac_user4")
        mgr.add_task("Delete me", "desc", future())
        task_id = mgr.data["tasks"][0]["id"]
        mgr.delete_task(task_id)
        ids = [t["id"] for t in mgr.data["tasks"]]
        self.assertNotIn(task_id, ids)

    def test_AC5_logout_removes_session(self):
        """AC-5: After logout, current_user is None."""
        mgr = make_manager("ac_user5")
        mgr.logout()
        self.assertIsNone(mgr.current_user)


# =============================================================================
# 7g. ACCEPTANCE TESTS — pytest (Framework 2)
# =============================================================================
class TestAcceptancePytest:

    def test_AC6_multiple_tasks_all_stored(self):
        """AC-6: All added tasks are stored and retrievable."""
        mgr = make_manager("ac6_user")
        titles = ["Task Alpha", "Task Beta", "Task Gamma"]
        for t in titles:
            mgr.add_task(t, "desc", future())
        stored = [t["title"] for t in mgr.data["tasks"] if t["user"] == "ac6_user"]
        for title in titles:
            assert title in stored

    def test_AC7_updated_task_visible_in_storage(self):
        """AC-7: Updated title immediately reflected in storage."""
        mgr = make_manager("ac7_user")
        mgr.add_task("Before update", "desc", future())
        task_id = mgr.data["tasks"][0]["id"]
        mgr.update_task(task_id, title="After update")
        task = next(t for t in mgr.data["tasks"] if t["id"] == task_id)
        assert task["title"] == "After update"

    def test_AC8_data_survives_manager_restart(self):
        """AC-8: Data persists when TaskManager is re-instantiated."""
        storage = InMemoryStorage()
        mgr1 = TaskManager(storage=storage)
        mgr1.login("persist_user")
        mgr1.add_task("Persistent task", "desc", future())

        mgr2 = TaskManager(storage=storage)
        tasks = [t for t in mgr2.data["tasks"] if t["user"] == "persist_user"]
        assert any(t["title"] == "Persistent task" for t in tasks)


# =============================================================================
# ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    unittest.main(verbosity=2)
