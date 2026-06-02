import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import books
from books import Book, BookCollection


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def use_temp_data_file(tmp_path, monkeypatch):
    """Redirect DATA_FILE to a fresh temp file for every test."""
    temp_file = tmp_path / "data.json"
    temp_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", temp_file)


@pytest.fixture
def collection():
    """Return an empty BookCollection."""
    return BookCollection()


@pytest.fixture
def populated_collection():
    """Return a BookCollection pre-loaded with three books."""
    col = BookCollection()
    col.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    col.add_book("Dune", "Frank Herbert", 1965)
    col.add_book("1984", "George Orwell", 1949)
    return col


# ---------------------------------------------------------------------------
# TestAddBook
# ---------------------------------------------------------------------------

class TestAddBook:
    """Tests for BookCollection.add_book."""

    def test_returns_book_instance(self, collection):
        book = collection.add_book("1984", "George Orwell", 1949)
        assert isinstance(book, Book)

    def test_book_stored_in_collection(self, collection):
        collection.add_book("1984", "George Orwell", 1949)
        assert len(collection.books) == 1

    def test_book_fields_are_correct(self, collection):
        book = collection.add_book("1984", "George Orwell", 1949)
        assert book.title == "1984"
        assert book.author == "George Orwell"
        assert book.year == 1949
        assert book.read is False

    def test_multiple_books_accumulate(self, collection):
        collection.add_book("Dune", "Frank Herbert", 1965)
        collection.add_book("1984", "George Orwell", 1949)
        assert len(collection.books) == 2

    def test_strips_leading_trailing_whitespace(self, collection):
        book = collection.add_book("  Dune  ", "  Frank Herbert  ", 1965)
        assert book.title == "Dune"
        assert book.author == "Frank Herbert"

    def test_year_zero_allowed(self, collection):
        book = collection.add_book("Unknown Year Book", "Some Author", 0)
        assert book.year == 0

    def test_persisted_to_disk(self, collection):
        collection.add_book("Dune", "Frank Herbert", 1965)
        reloaded = BookCollection()
        assert len(reloaded.books) == 1
        assert reloaded.books[0].title == "Dune"

    @pytest.mark.parametrize("bad_title", ["", "   ", "\t", "\n"])
    def test_empty_or_whitespace_title_raises(self, collection, bad_title):
        with pytest.raises(ValueError, match="[Tt]itle"):
            collection.add_book(bad_title, "Some Author", 2024)

    @pytest.mark.parametrize("bad_author", ["", "   ", "\t", "\n"])
    def test_empty_or_whitespace_author_raises(self, collection, bad_author):
        with pytest.raises(ValueError, match="[Aa]uthor"):
            collection.add_book("Some Title", bad_author, 2024)


# ---------------------------------------------------------------------------
# TestRemoveBook
# ---------------------------------------------------------------------------

class TestRemoveBook:
    """Tests for BookCollection.remove_book."""

    def test_removes_existing_book(self, populated_collection):
        result = populated_collection.remove_book("The Hobbit")
        assert result is True
        assert populated_collection.find_book_by_title("The Hobbit") is None

    def test_decreases_collection_size(self, populated_collection):
        before = len(populated_collection.books)
        populated_collection.remove_book("Dune")
        assert len(populated_collection.books) == before - 1

    def test_returns_false_for_nonexistent_book(self, collection):
        result = collection.remove_book("Ghost Book")
        assert result is False

    def test_returns_false_on_empty_collection(self, collection):
        assert collection.remove_book("Anything") is False

    def test_case_insensitive_removal(self, populated_collection):
        result = populated_collection.remove_book("the hobbit")
        assert result is True
        assert populated_collection.find_book_by_title("The Hobbit") is None

    def test_only_removes_exact_title_not_partial(self, collection):
        collection.add_book("Dune", "Frank Herbert", 1965)
        collection.add_book("Dune Messiah", "Frank Herbert", 1969)
        collection.remove_book("Dune")
        assert collection.find_book_by_title("Dune Messiah") is not None

    def test_other_books_unaffected(self, populated_collection):
        populated_collection.remove_book("Dune")
        assert populated_collection.find_book_by_title("The Hobbit") is not None
        assert populated_collection.find_book_by_title("1984") is not None

    def test_persists_removal_to_disk(self, populated_collection):
        populated_collection.remove_book("Dune")
        reloaded = BookCollection()
        assert reloaded.find_book_by_title("Dune") is None


# ---------------------------------------------------------------------------
# TestFindBookByTitle
# ---------------------------------------------------------------------------

class TestFindBookByTitle:
    """Tests for BookCollection.find_book_by_title."""

    def test_finds_existing_book(self, populated_collection):
        book = populated_collection.find_book_by_title("Dune")
        assert book is not None
        assert book.title == "Dune"

    def test_returns_none_when_not_found(self, populated_collection):
        assert populated_collection.find_book_by_title("Invisible Man") is None

    def test_returns_none_on_empty_collection(self, collection):
        assert collection.find_book_by_title("Dune") is None

    @pytest.mark.parametrize("query", ["The Hobbit", "the hobbit", "THE HOBBIT", "tHe HoBbIt"])
    def test_case_insensitive(self, populated_collection, query):
        book = populated_collection.find_book_by_title(query)
        assert book is not None
        assert book.title == "The Hobbit"

    def test_does_not_match_partial_title(self, populated_collection):
        assert populated_collection.find_book_by_title("Hobb") is None

    def test_returns_correct_book_among_many(self, populated_collection):
        book = populated_collection.find_book_by_title("1984")
        assert book.author == "George Orwell"
        assert book.year == 1949


# ---------------------------------------------------------------------------
# TestFindByAuthor
# ---------------------------------------------------------------------------

class TestFindByAuthor:
    """Tests for BookCollection.find_by_author."""

    def test_returns_matching_books(self, populated_collection):
        results = populated_collection.find_by_author("Frank Herbert")
        assert len(results) == 1
        assert results[0].title == "Dune"

    def test_returns_multiple_books_same_author(self, collection):
        collection.add_book("Dune", "Frank Herbert", 1965)
        collection.add_book("Dune Messiah", "Frank Herbert", 1969)
        results = collection.find_by_author("Frank Herbert")
        assert len(results) == 2

    def test_returns_empty_list_when_not_found(self, populated_collection):
        results = populated_collection.find_by_author("Unknown Author")
        assert results == []

    def test_returns_empty_list_on_empty_collection(self, collection):
        assert collection.find_by_author("Anyone") == []

    @pytest.mark.parametrize("query", ["George Orwell", "george orwell", "GEORGE ORWELL"])
    def test_case_insensitive(self, populated_collection, query):
        results = populated_collection.find_by_author(query)
        assert len(results) == 1
        assert results[0].title == "1984"

    def test_does_not_return_other_authors(self, populated_collection):
        results = populated_collection.find_by_author("Frank Herbert")
        titles = [b.title for b in results]
        assert "1984" not in titles
        assert "The Hobbit" not in titles

    # --- Partial match tests (fix for issue #1) ---

    def test_partial_last_name_matches(self, populated_collection):
        results = populated_collection.find_by_author("Herbert")
        assert len(results) == 1
        assert results[0].title == "Dune"

    def test_partial_first_name_matches(self, populated_collection):
        results = populated_collection.find_by_author("Frank")
        assert len(results) == 1
        assert results[0].title == "Dune"

    def test_partial_name_case_insensitive(self, populated_collection):
        results = populated_collection.find_by_author("ORWELL")
        assert len(results) == 1
        assert results[0].title == "1984"

    def test_partial_name_matches_multiple_authors(self, collection):
        collection.add_book("Dune", "Frank Herbert", 1965)
        collection.add_book("Foundation", "Isaac Asimov", 1951)
        collection.add_book("Childhood's End", "Arthur C. Clarke", 1953)
        # "a" appears in all three authors — sanity check on broad partial
        results = collection.find_by_author("a")
        assert len(results) == 3

    def test_empty_string_returns_empty_list(self, populated_collection):
        assert populated_collection.find_by_author("") == []

    def test_whitespace_only_returns_empty_list(self, populated_collection):
        assert populated_collection.find_by_author("   ") == []

    @pytest.mark.parametrize("query", ["Herbert", "frank", "FRANK HERBERT", "rank Her"])
    def test_various_partial_queries_find_dune(self, populated_collection, query):
        results = populated_collection.find_by_author(query)
        titles = [b.title for b in results]
        assert "Dune" in titles


# ---------------------------------------------------------------------------
# TestMarkAsRead
# ---------------------------------------------------------------------------

class TestMarkAsRead:
    """Tests for BookCollection.mark_as_read."""

    def test_marks_book_as_read(self, populated_collection):
        result = populated_collection.mark_as_read("Dune")
        assert result is True
        assert populated_collection.find_book_by_title("Dune").read is True

    def test_returns_false_for_nonexistent_book(self, collection):
        assert collection.mark_as_read("Ghost Book") is False

    def test_returns_false_on_empty_collection(self, collection):
        assert collection.mark_as_read("Dune") is False

    def test_case_insensitive(self, populated_collection):
        result = populated_collection.mark_as_read("the hobbit")
        assert result is True
        assert populated_collection.find_book_by_title("The Hobbit").read is True

    def test_only_marks_target_book(self, populated_collection):
        populated_collection.mark_as_read("Dune")
        assert populated_collection.find_book_by_title("The Hobbit").read is False
        assert populated_collection.find_book_by_title("1984").read is False

    def test_persists_read_status_to_disk(self, populated_collection):
        populated_collection.mark_as_read("1984")
        reloaded = BookCollection()
        assert reloaded.find_book_by_title("1984").read is True

    def test_already_read_book_stays_read(self, populated_collection):
        populated_collection.mark_as_read("Dune")
        result = populated_collection.mark_as_read("Dune")
        assert result is True
        assert populated_collection.find_book_by_title("Dune").read is True


# ---------------------------------------------------------------------------
# TestEdgeCasesEmptyData
# ---------------------------------------------------------------------------

class TestEdgeCasesEmptyData:
    """Edge cases, especially around an empty or minimal collection."""

    def test_list_books_empty(self, collection):
        assert collection.list_books() == []

    def test_load_books_missing_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(books, "DATA_FILE", tmp_path / "nonexistent.json")
        col = BookCollection()
        assert col.books == []

    def test_load_books_corrupted_json(self, tmp_path, monkeypatch, capsys):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{not valid json}")
        monkeypatch.setattr(books, "DATA_FILE", bad_file)
        col = BookCollection()
        assert col.books == []
        captured = capsys.readouterr()
        assert "corrupted" in captured.out.lower() or "warning" in captured.out.lower()

    def test_add_then_remove_leaves_empty(self, collection):
        collection.add_book("Dune", "Frank Herbert", 1965)
        collection.remove_book("Dune")
        assert collection.list_books() == []

    def test_remove_from_empty_collection(self, collection):
        assert collection.remove_book("Dune") is False

    def test_find_by_title_empty_collection(self, collection):
        assert collection.find_book_by_title("Anything") is None

    def test_find_by_author_empty_collection(self, collection):
        assert collection.find_by_author("Anyone") == []

    def test_mark_as_read_empty_collection(self, collection):
        assert collection.mark_as_read("Anything") is False

    def test_collection_survives_reload_cycle(self, collection):
        collection.add_book("Dune", "Frank Herbert", 1965)
        collection.add_book("1984", "George Orwell", 1949)
        reloaded = BookCollection()
        assert len(reloaded.books) == 2
        titles = {b.title for b in reloaded.books}
        assert titles == {"Dune", "1984"}

    def test_load_books_wrong_field_names(self, tmp_path, monkeypatch, capsys):
        """load_books handles records with unexpected field names (KeyError path)."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text('[{"name": "Dune", "writer": "Herbert", "year": 1965, "read": false}]')
        monkeypatch.setattr(books, "DATA_FILE", bad_file)
        col = BookCollection()
        assert col.books == []
        captured = capsys.readouterr()
        assert "warning" in captured.out.lower()

    def test_load_books_wrong_field_types(self, tmp_path, monkeypatch, capsys):
        """load_books handles records where field types are wrong (TypeError path)."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text('[{"title": 123, "author": null, "year": "not-a-year", "read": false}]')
        monkeypatch.setattr(books, "DATA_FILE", bad_file)
        col = BookCollection()
        # collection starts empty rather than crashing
        assert isinstance(col.books, list)

    def test_load_books_missing_required_field(self, tmp_path, monkeypatch, capsys):
        """load_books handles records missing a required field like 'author' (KeyError path)."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text('[{"title": "Dune", "year": 1965, "read": false}]')
        monkeypatch.setattr(books, "DATA_FILE", bad_file)
        col = BookCollection()
        assert col.books == []
        captured = capsys.readouterr()
        assert "warning" in captured.out.lower()


# ---------------------------------------------------------------------------
# TestGetUnreadBooks
# ---------------------------------------------------------------------------

class TestGetUnreadBooks:
    """Tests for BookCollection.get_unread_books."""

    def test_returns_only_unread_books(self, populated_collection):
        populated_collection.mark_as_read("Dune")
        unread = populated_collection.get_unread_books()
        titles = [b.title for b in unread]
        assert "Dune" not in titles
        assert "The Hobbit" in titles
        assert "1984" in titles

    def test_returns_all_when_none_read(self, populated_collection):
        unread = populated_collection.get_unread_books()
        assert len(unread) == 3

    def test_returns_empty_when_all_read(self, populated_collection):
        for title in ["The Hobbit", "Dune", "1984"]:
            populated_collection.mark_as_read(title)
        assert populated_collection.get_unread_books() == []

    def test_returns_empty_on_empty_collection(self, collection):
        assert collection.get_unread_books() == []

    def test_returns_single_unread_book(self, collection):
        collection.add_book("Dune", "Frank Herbert", 1965)
        unread = collection.get_unread_books()
        assert len(unread) == 1
        assert unread[0].title == "Dune"

    def test_does_not_include_read_books(self, collection):
        collection.add_book("Dune", "Frank Herbert", 1965)
        collection.add_book("1984", "George Orwell", 1949)
        collection.mark_as_read("Dune")
        unread = collection.get_unread_books()
        assert all(not b.read for b in unread)

    @pytest.mark.parametrize("n_read,n_unread", [
        (0, 3),
        (1, 2),
        (2, 1),
        (3, 0),
    ])
    def test_count_matches_unread_ratio(self, collection, n_read, n_unread):
        titles = ["Book A", "Book B", "Book C"]
        for title in titles:
            collection.add_book(title, "Author", 2000)
        for title in titles[:n_read]:
            collection.mark_as_read(title)
        assert len(collection.get_unread_books()) == n_unread

    def test_unaffected_by_remove_book(self, populated_collection):
        populated_collection.remove_book("Dune")
        unread = populated_collection.get_unread_books()
        titles = [b.title for b in unread]
        assert "Dune" not in titles
        assert len(unread) == 2

    def test_newly_added_book_appears_in_unread(self, populated_collection):
        populated_collection.add_book("Brave New World", "Aldous Huxley", 1932)
        unread = populated_collection.get_unread_books()
        titles = [b.title for b in unread]
        assert "Brave New World" in titles

    def test_marking_as_read_removes_from_unread(self, populated_collection):
        populated_collection.mark_as_read("The Hobbit")
        unread = populated_collection.get_unread_books()
        assert all(b.title != "The Hobbit" for b in unread)

# NOTE: These tests define the *expected* behaviour for year validation.
#       They will fail until validation is added to add_book().
# ---------------------------------------------------------------------------

class TestFindByYear:
    """Tests for BookCollection.find_by_year and find_by_year_range."""

    # --- find_by_year ---

    def test_exact_year_returns_matching_books(self, populated_collection):
        results = populated_collection.find_by_year(1965)
        assert len(results) == 1
        assert results[0].title == "Dune"

    def test_exact_year_no_match_returns_empty(self, populated_collection):
        assert populated_collection.find_by_year(2000) == []

    def test_exact_year_empty_collection(self, collection):
        assert collection.find_by_year(1965) == []

    def test_exact_year_multiple_books_same_year(self, collection):
        collection.add_book("Book A", "Author One", 1965)
        collection.add_book("Book B", "Author Two", 1965)
        collection.add_book("Book C", "Author Three", 1999)
        results = collection.find_by_year(1965)
        assert len(results) == 2

    def test_year_zero_sentinel_is_searchable(self, collection):
        collection.add_book("Unknown Year Book", "Some Author", 0)
        results = collection.find_by_year(0)
        assert len(results) == 1
        assert results[0].title == "Unknown Year Book"

    # --- find_by_year_range ---

    def test_range_returns_books_in_range(self, populated_collection):
        # 1937 (Hobbit), 1949 (1984), 1965 (Dune)
        results = populated_collection.find_by_year_range(1940, 1970)
        titles = {b.title for b in results}
        assert titles == {"1984", "Dune"}

    def test_range_inclusive_lower_boundary(self, populated_collection):
        results = populated_collection.find_by_year_range(1937, 1940)
        titles = {b.title for b in results}
        assert "The Hobbit" in titles

    def test_range_inclusive_upper_boundary(self, populated_collection):
        results = populated_collection.find_by_year_range(1960, 1965)
        titles = {b.title for b in results}
        assert "Dune" in titles

    def test_range_single_year_equals_exact(self, populated_collection):
        assert populated_collection.find_by_year_range(1965, 1965) == \
               populated_collection.find_by_year(1965)

    def test_range_no_match_returns_empty(self, populated_collection):
        assert populated_collection.find_by_year_range(2000, 2024) == []

    def test_range_empty_collection_returns_empty(self, collection):
        assert collection.find_by_year_range(1900, 2000) == []

    def test_range_invalid_raises_value_error(self, collection):
        with pytest.raises(ValueError):
            collection.find_by_year_range(2000, 1900)

    def test_range_all_books(self, populated_collection):
        results = populated_collection.find_by_year_range(1900, 2000)
        assert len(results) == 3


# NOTE: These tests define the *expected* behaviour for year validation.
#       They will fail until validation is added to add_book().
# ---------------------------------------------------------------------------

class TestYearValidation:
    """Tests for year validation in BookCollection.add_book.

    These are specification tests — they document the required behaviour
    and will fail until `add_book` validates the `year` parameter.
    """

    @pytest.mark.xfail(reason="Year validation not yet implemented in add_book()", strict=True)
    @pytest.mark.parametrize("bad_year", [-1, -100, -9999])
    def test_negative_year_raises(self, collection, bad_year):
        """Negative years should be rejected with ValueError."""
        with pytest.raises(ValueError, match="[Yy]ear"):
            collection.add_book("Dune", "Frank Herbert", bad_year)

    def test_year_zero_is_accepted(self, collection):
        """Year 0 is the sentinel for 'unknown year' and must be allowed."""
        book = collection.add_book("Unknown Year Book", "Some Author", 0)
        assert book.year == 0

    @pytest.mark.parametrize("valid_year", [1, 1000, 1965, 2024, 2100])
    def test_valid_years_accepted(self, collection, valid_year):
        book = collection.add_book("Some Book", "Some Author", valid_year)
        assert book.year == valid_year

    @pytest.mark.xfail(reason="Year validation not yet implemented in add_book()", strict=True)
    def test_non_integer_year_raises(self, collection):
        """A string passed as year should raise TypeError or ValueError."""
        with pytest.raises((TypeError, ValueError)):
            collection.add_book("Dune", "Frank Herbert", "nineteen-sixty-five")  # type: ignore
