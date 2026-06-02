import sys
import pytest
from unittest.mock import MagicMock, Mock

import books
import book_app
from book_app import (
    handle_list,
    handle_add,
    handle_remove,
    handle_find,
    handle_unread,
    show_help,
    main,
)
from books import Book, BookCollection


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def patch_data_file(tmp_path, monkeypatch):
    """Prevent import-time BookCollection from touching real data.json."""
    temp_file = tmp_path / "data.json"
    temp_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", temp_file)


@pytest.fixture(autouse=True)
def mock_collection(monkeypatch):
    """Replace the module-level collection with a MagicMock for every test."""
    mock = MagicMock(spec=BookCollection)
    monkeypatch.setattr(book_app, "collection", mock)
    return mock


# ---------------------------------------------------------------------------
# TestHandleList
# ---------------------------------------------------------------------------

class TestHandleList:
    """Tests for handle_list."""

    def test_calls_list_books(self, mock_collection):
        mock_collection.list_books.return_value = []
        handle_list()
        mock_collection.list_books.assert_called_once()

    def test_prints_books_when_present(self, mock_collection, capsys):
        mock_collection.list_books.return_value = [Book("Dune", "Frank Herbert", 1965)]
        handle_list()
        assert "Dune" in capsys.readouterr().out

    def test_empty_collection_prints_message(self, mock_collection, capsys):
        mock_collection.list_books.return_value = []
        handle_list()
        assert "No books" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# TestHandleUnread
# ---------------------------------------------------------------------------

class TestHandleUnread:
    """Tests for handle_unread."""

    def test_calls_get_unread_books(self, mock_collection):
        mock_collection.get_unread_books.return_value = []
        handle_unread()
        mock_collection.get_unread_books.assert_called_once()

    def test_prints_unread_books(self, mock_collection, capsys):
        mock_collection.get_unread_books.return_value = [Book("Dune", "Frank Herbert", 1965)]
        handle_unread()
        assert "Dune" in capsys.readouterr().out

    def test_no_unread_books_prints_message(self, mock_collection, capsys):
        mock_collection.get_unread_books.return_value = []
        handle_unread()
        assert "No unread books" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# TestHandleAdd
# ---------------------------------------------------------------------------

class TestHandleAdd:
    """Tests for handle_add."""

    def test_calls_add_book_with_correct_args(self, mock_collection, monkeypatch):
        monkeypatch.setattr("builtins.input", Mock(side_effect=["Dune", "Frank Herbert", "1965"]))
        handle_add()
        mock_collection.add_book.assert_called_once_with("Dune", "Frank Herbert", 1965)

    def test_prints_success_message(self, mock_collection, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", Mock(side_effect=["Dune", "Frank Herbert", "1965"]))
        handle_add()
        assert "successfully" in capsys.readouterr().out.lower()

    def test_empty_year_defaults_to_zero(self, mock_collection, monkeypatch):
        monkeypatch.setattr("builtins.input", Mock(side_effect=["Dune", "Frank Herbert", ""]))
        handle_add()
        mock_collection.add_book.assert_called_once_with("Dune", "Frank Herbert", 0)

    def test_prints_error_on_value_error_from_add_book(self, mock_collection, monkeypatch, capsys):
        mock_collection.add_book.side_effect = ValueError("Book title cannot be empty.")
        monkeypatch.setattr("builtins.input", Mock(side_effect=["", "Frank Herbert", "1965"]))
        handle_add()
        assert "Error" in capsys.readouterr().out

    def test_non_numeric_year_caught_prints_error(self, mock_collection, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", Mock(side_effect=["Dune", "Frank Herbert", "bad"]))
        handle_add()
        # ValueError from int("bad") is caught; error message printed, add_book not called
        assert "Error" in capsys.readouterr().out
        mock_collection.add_book.assert_not_called()


# ---------------------------------------------------------------------------
# TestHandleRemove
# ---------------------------------------------------------------------------

class TestHandleRemove:
    """Tests for handle_remove."""

    def test_calls_remove_book_with_title(self, mock_collection, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "Dune")
        handle_remove()
        mock_collection.remove_book.assert_called_once_with("Dune")

    def test_prints_output(self, mock_collection, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", lambda _: "Dune")
        handle_remove()
        assert capsys.readouterr().out.strip()


# ---------------------------------------------------------------------------
# TestHandleFind
# ---------------------------------------------------------------------------

class TestHandleFind:
    """Tests for handle_find."""

    def test_calls_find_by_author_with_name(self, mock_collection, monkeypatch):
        mock_collection.find_by_author.return_value = []
        monkeypatch.setattr("builtins.input", lambda _: "Frank Herbert")
        handle_find()
        mock_collection.find_by_author.assert_called_once_with("Frank Herbert")

    def test_prints_found_books(self, mock_collection, monkeypatch, capsys):
        mock_collection.find_by_author.return_value = [Book("Dune", "Frank Herbert", 1965)]
        monkeypatch.setattr("builtins.input", lambda _: "Frank Herbert")
        handle_find()
        assert "Dune" in capsys.readouterr().out

    def test_no_results_prints_message(self, mock_collection, monkeypatch, capsys):
        mock_collection.find_by_author.return_value = []
        monkeypatch.setattr("builtins.input", lambda _: "Unknown")
        handle_find()
        assert "No books" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# TestShowHelp
# ---------------------------------------------------------------------------

class TestShowHelp:
    """Tests for show_help."""

    def test_prints_all_commands(self, capsys):
        show_help()
        out = capsys.readouterr().out
        for cmd in ["list", "unread", "add", "remove", "find", "help"]:
            assert cmd in out


# ---------------------------------------------------------------------------
# TestMain
# ---------------------------------------------------------------------------

class TestMain:
    """Tests for main."""

    def test_no_args_shows_help(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["book_app.py"])
        main()
        assert "Commands" in capsys.readouterr().out

    def test_list_command_calls_list_books(self, mock_collection, monkeypatch):
        mock_collection.list_books.return_value = []
        monkeypatch.setattr(sys, "argv", ["book_app.py", "list"])
        main()
        mock_collection.list_books.assert_called_once()

    def test_unread_command_calls_get_unread_books(self, mock_collection, monkeypatch):
        mock_collection.get_unread_books.return_value = []
        monkeypatch.setattr(sys, "argv", ["book_app.py", "unread"])
        main()
        mock_collection.get_unread_books.assert_called_once()

    def test_help_command_prints_commands(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["book_app.py", "help"])
        main()
        assert "Commands" in capsys.readouterr().out

    def test_unknown_command_prints_error(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["book_app.py", "unknown"])
        main()
        assert "Unknown command" in capsys.readouterr().out

    def test_command_is_case_insensitive(self, mock_collection, monkeypatch):
        mock_collection.list_books.return_value = []
        monkeypatch.setattr(sys, "argv", ["book_app.py", "LIST"])
        main()
        mock_collection.list_books.assert_called_once()
