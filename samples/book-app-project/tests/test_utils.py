import pytest
from unittest.mock import Mock
from books import Book
from utils import get_user_choice, get_book_details, print_books, print_menu


# ---------------------------------------------------------------------------
# TestPrintMenu
# ---------------------------------------------------------------------------

class TestPrintMenu:
    """Tests for print_menu."""

    def test_prints_app_title(self, capsys):
        print_menu()
        assert "Book Collection App" in capsys.readouterr().out

    def test_prints_all_five_options(self, capsys):
        print_menu()
        out = capsys.readouterr().out
        for option in ["1.", "2.", "3.", "4.", "5."]:
            assert option in out


# ---------------------------------------------------------------------------
# TestGetUserChoice
# ---------------------------------------------------------------------------

class TestGetUserChoice:
    """Tests for get_user_choice."""

    @pytest.mark.parametrize("valid", ["1", "2", "3", "4", "5"])
    def test_valid_choice_returned(self, monkeypatch, valid):
        monkeypatch.setattr("builtins.input", lambda _: valid)
        assert get_user_choice() == valid

    def test_empty_input_returns_empty_string(self, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", lambda _: "")
        assert get_user_choice() == ""
        assert "No input" in capsys.readouterr().out

    def test_non_digit_returns_empty_string(self, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", lambda _: "abc")
        assert get_user_choice() == ""
        assert "not a number" in capsys.readouterr().out

    @pytest.mark.parametrize("out_of_range", ["0", "6", "9", "99"])
    def test_out_of_range_returns_empty_string(self, monkeypatch, capsys, out_of_range):
        monkeypatch.setattr("builtins.input", lambda _: out_of_range)
        assert get_user_choice() == ""
        assert "out of range" in capsys.readouterr().out

    def test_whitespace_only_returns_empty_string(self, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", lambda _: "   ")
        assert get_user_choice() == ""


# ---------------------------------------------------------------------------
# TestGetBookDetails
# ---------------------------------------------------------------------------

class TestGetBookDetails:
    """Tests for get_book_details."""

    def test_returns_title_author_year(self, monkeypatch):
        inputs = Mock(side_effect=["Dune", "Frank Herbert", "1965"])
        monkeypatch.setattr("builtins.input", inputs)
        title, author, year = get_book_details()
        assert title == "Dune"
        assert author == "Frank Herbert"
        assert year == 1965

    def test_empty_year_defaults_to_zero(self, monkeypatch, capsys):
        inputs = Mock(side_effect=["Dune", "Frank Herbert", ""])
        monkeypatch.setattr("builtins.input", inputs)
        _, _, year = get_book_details()
        assert year == 0

    def test_invalid_year_defaults_to_zero(self, monkeypatch, capsys):
        inputs = Mock(side_effect=["Dune", "Frank Herbert", "bad"])
        monkeypatch.setattr("builtins.input", inputs)
        _, _, year = get_book_details()
        assert year == 0
        assert "Invalid year" in capsys.readouterr().out

    def test_out_of_range_year_warns_but_accepts(self, monkeypatch, capsys):
        inputs = Mock(side_effect=["Dune", "Frank Herbert", "500"])
        monkeypatch.setattr("builtins.input", inputs)
        _, _, year = get_book_details()
        assert year == 500
        assert "Warning" in capsys.readouterr().out

    def test_retries_on_empty_title(self, monkeypatch, capsys):
        inputs = Mock(side_effect=["", "Dune", "Frank Herbert", "1965"])
        monkeypatch.setattr("builtins.input", inputs)
        title, _, _ = get_book_details()
        assert title == "Dune"
        assert "cannot be empty" in capsys.readouterr().out

    def test_retries_on_empty_author(self, monkeypatch, capsys):
        inputs = Mock(side_effect=["Dune", "", "Frank Herbert", "1965"])
        monkeypatch.setattr("builtins.input", inputs)
        _, author, _ = get_book_details()
        assert author == "Frank Herbert"
        assert "cannot be empty" in capsys.readouterr().out

    def test_strips_whitespace_from_title_and_author(self, monkeypatch):
        inputs = Mock(side_effect=["  Dune  ", "  Frank Herbert  ", "1965"])
        monkeypatch.setattr("builtins.input", inputs)
        title, author, _ = get_book_details()
        assert title == "Dune"
        assert author == "Frank Herbert"


# ---------------------------------------------------------------------------
# TestPrintBooks
# ---------------------------------------------------------------------------

class TestPrintBooks:
    """Tests for print_books."""

    def test_empty_list_prints_message(self, capsys):
        print_books([])
        assert "No books" in capsys.readouterr().out

    def test_prints_book_title_and_author(self, capsys):
        print_books([Book("Dune", "Frank Herbert", 1965)])
        out = capsys.readouterr().out
        assert "Dune" in out
        assert "Frank Herbert" in out

    def test_prints_year(self, capsys):
        print_books([Book("Dune", "Frank Herbert", 1965)])
        assert "1965" in capsys.readouterr().out

    def test_read_book_shows_checkmark(self, capsys):
        print_books([Book("1984", "George Orwell", 1949, read=True)])
        assert "✅" in capsys.readouterr().out

    def test_unread_book_shows_open_book(self, capsys):
        print_books([Book("Dune", "Frank Herbert", 1965, read=False)])
        assert "📖" in capsys.readouterr().out

    def test_prints_index_numbers(self, capsys):
        books = [
            Book("Dune", "Frank Herbert", 1965),
            Book("1984", "George Orwell", 1949),
        ]
        print_books(books)
        out = capsys.readouterr().out
        assert "1." in out
        assert "2." in out

    def test_mixed_read_status(self, capsys):
        books = [
            Book("Dune", "Frank Herbert", 1965, read=False),
            Book("1984", "George Orwell", 1949, read=True),
        ]
        print_books(books)
        out = capsys.readouterr().out
        assert "✅" in out
        assert "📖" in out
