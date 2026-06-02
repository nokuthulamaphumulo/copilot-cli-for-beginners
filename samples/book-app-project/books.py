"""Book collection data model and persistence layer.

This module defines :class:`Book` (a dataclass representing a single book)
and :class:`BookCollection` (which loads, mutates, and saves the collection
to a local JSON file).

Error-handling strategy
-----------------------
- *Validation errors* (empty title/author) are raised as ``ValueError`` so
  callers can surface them to the user immediately.
- *I/O and format errors* in :meth:`BookCollection.load_books` are caught
  and reported as warnings; the collection starts empty rather than crashing.
- *I/O errors* in :meth:`BookCollection.save_books` propagate as ``OSError``
  — callers should catch this at the UI layer and notify the user.

.. note::
    ``DATA_FILE`` is resolved relative to this module's location so the app
    works correctly regardless of the current working directory.
"""

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional

#: Absolute path to the JSON file that persists the book collection.
DATA_FILE = Path(__file__).parent / "data.json"


@dataclass
class Book:
    """Represents a single book in the collection.

    Attributes
    ----------
    title : str
        The title of the book.
    author : str
        The name of the book's author.
    year : int
        The publication year. Defaults to 0 when unknown.
    read : bool
        Whether the book has been marked as read. Defaults to False.
    """

    title: str
    author: str
    year: int
    read: bool = False


class BookCollection:
    """Manages a persistent collection of books backed by a local JSON file.

    Books are loaded from ``data.json`` on instantiation and saved back
    whenever the collection is modified.
    """

    def __init__(self) -> None:
        """Initialise the collection and load any previously saved books."""
        self.books: List[Book] = []
        self.load_books()

    def load_books(self) -> None:
        """Load books from the JSON data file into memory.

        Reads ``DATA_FILE`` from the same directory as this module and
        deserialises each entry into a :class:`Book` instance.

        The following error conditions are handled gracefully — in each case
        a warning is printed and the collection starts empty:

        - ``FileNotFoundError`` — ``data.json`` does not exist yet (first run).
        - ``json.JSONDecodeError`` — the file contains invalid JSON.
        - ``KeyError`` / ``TypeError`` — a record has missing or wrongly-typed
          fields that cannot be mapped onto :class:`Book`.

        .. note::
            This method is called automatically by :meth:`__init__`.
        """
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                self.books = [Book(**b) for b in data]
        except FileNotFoundError:
            self.books = []
        except json.JSONDecodeError:
            print("Warning: data.json is corrupted. Starting with empty collection.")
            self.books = []
        except (KeyError, TypeError):
            print("Warning: data.json has unexpected format. Starting with empty collection.")
            self.books = []

    def save_books(self) -> None:
        """Persist the current collection to ``data.json``.

        Serialises every :class:`Book` to a plain dictionary and writes the
        resulting list to ``data.json`` with two-space indentation. Creates
        the file if it does not already exist.

        Raises
        ------
        OSError
            If the file cannot be written (e.g. permission denied, disk full).
            The caller — typically the UI layer — is responsible for catching
            this and notifying the user.

        .. note::
            The write is **not** atomic in this implementation. A future
            improvement is to write to a temporary file and use
            ``os.replace()`` to swap it in, preventing data loss on
            interrupted writes.
        """
        with open(DATA_FILE, "w") as f:
            json.dump([asdict(b) for b in self.books], f, indent=2)

    def add_book(self, title: str, author: str, year: int) -> Book:
        """Add a new book to the collection and save.

        Parameters
        ----------
        title : str
            Title of the book. Must be a non-empty string.
        author : str
            Author of the book. Must be a non-empty string.
        year : int
            Publication year. Pass ``0`` when the year is unknown.

        Returns
        -------
        Book
            The newly created :class:`Book` instance.

        Raises
        ------
        ValueError
            If *title* or *author* is empty or contains only whitespace.
        """
        if not title or not title.strip():
            raise ValueError("Book title cannot be empty.")
        if not author or not author.strip():
            raise ValueError("Author name cannot be empty.")
        book = Book(title=title.strip(), author=author.strip(), year=year)
        self.books.append(book)
        self.save_books()
        return book

    def list_books(self) -> List[Book]:
        """Return all books in the collection.

        Returns
        -------
        List[Book]
            A list of every :class:`Book` currently held in memory. The list
            may be empty if no books have been added yet.
        """
        return self.books

    def find_book_by_title(self, title: str) -> Optional[Book]:
        """Find a book by its title using a case-insensitive match.

        Parameters
        ----------
        title : str
            The title to search for.

        Returns
        -------
        Book or None
            The first :class:`Book` whose title matches *title* (ignoring
            case), or ``None`` if no match is found.
        """
        for book in self.books:
            if book.title.lower() == title.lower():
                return book
        return None

    def mark_as_read(self, title: str) -> bool:
        """Mark a book as read by title.

        Performs a case-insensitive title lookup. If the book is found its
        ``read`` flag is set to ``True`` and the collection is saved.

        Parameters
        ----------
        title : str
            Title of the book to mark as read.

        Returns
        -------
        bool
            ``True`` if the book was found and updated, ``False`` otherwise.
        """
        book = self.find_book_by_title(title)
        if book:
            book.read = True
            self.save_books()
            return True
        return False

    def remove_book(self, title: str) -> bool:
        """Remove a book from the collection by title and save.

        Performs a case-insensitive title lookup. If the book is found it is
        removed from the in-memory list and the collection is saved.

        Parameters
        ----------
        title : str
            Title of the book to remove.

        Returns
        -------
        bool
            ``True`` if the book was found and removed, ``False`` otherwise.
        """
        book = self.find_book_by_title(title)
        if book:
            self.books.remove(book)
            self.save_books()
            return True
        return False

    def get_unread_books(self) -> List[Book]:
        """Return all books that have not been marked as read.

        Returns
        -------
        List[Book]
            A list of :class:`Book` instances where ``read`` is ``False``.
            Returns an empty list if all books have been read or the
            collection is empty.
        """
        return [b for b in self.books if not b.read]

    def find_by_year(self, year: int) -> List[Book]:
        """Return all books published in the given year.

        Parameters
        ----------
        year : int
            The exact publication year to search for.

        Returns
        -------
        List[Book]
            A list of :class:`Book` instances whose ``year`` field equals
            *year*. Returns an empty list if no matches are found.
        """
        return [b for b in self.books if b.year == year]

    def find_by_year_range(self, start: int, end: int) -> List[Book]:
        """Return all books published within an inclusive year range.

        Parameters
        ----------
        start : int
            The earliest publication year (inclusive).
        end : int
            The latest publication year (inclusive).

        Returns
        -------
        List[Book]
            A list of :class:`Book` instances whose ``year`` falls between
            *start* and *end* (both inclusive). Returns an empty list if no
            matches are found.

        Raises
        ------
        ValueError
            If *start* is greater than *end*.
        """
        if start > end:
            raise ValueError(f"Start year ({start}) cannot be greater than end year ({end}).")
        return [b for b in self.books if start <= b.year <= end]

    def find_by_author(self, author: str) -> List[Book]:
        """Return all books whose author name contains the search string.

        Performs a case-insensitive substring match so partial names such as
        ``"Herbert"`` will match ``"Frank Herbert"``.

        Parameters
        ----------
        author : str
            The author name or partial name to search for.

        Returns
        -------
        List[Book]
            A list of :class:`Book` instances whose ``author`` field contains
            *author* (ignoring case). Returns an empty list if no matches
            are found or if *author* is empty.
        """
        if not author or not author.strip():
            return []
        return [b for b in self.books if author.lower() in b.author.lower()]
