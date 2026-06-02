from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from books import Book


def print_menu() -> None:
    print("\n📚 Book Collection App")
    print("1. Add a book")
    print("2. List books")
    print("3. Mark book as read")
    print("4. Remove a book")
    print("5. Exit")



def get_user_choice() -> str:
    choice = input("Choose an option (1-5): ").strip()
    if not choice:
        print("No input provided. Please enter a number between 1 and 5.")
        return ""
    if not choice.isdigit():
        print(f"'{choice}' is not a number. Please enter a number between 1 and 5.")
        return ""
    if choice not in {"1", "2", "3", "4", "5"}:
        print(f"'{choice}' is out of range. Please enter a number between 1 and 5.")
        return ""
    return choice


def get_book_details() -> tuple[str, str, int]:
    """Interactively prompt the user for book details via the terminal.

    Prompts for three fields in order: title, author, and publication year.
    Title and author are required — the user is re-prompted until a non-empty
    value is provided. Year is optional; non-numeric input or an empty string
    defaults to 0, and an out-of-range year (outside 1000–2100) triggers a
    warning but is still accepted.

    Parameters
    ----------
    None
        This function takes no parameters; all input is read interactively
        from stdin via ``input()``.

    Returns
    -------
    tuple[str, str, int]
        A three-element tuple of ``(title, author, year)`` where:

        - ``title``  (str) — the book's title; guaranteed non-empty.
        - ``author`` (str) — the book's author; guaranteed non-empty.
        - ``year``   (int) — the publication year, or ``0`` if not provided
          or invalid.
    """
    title = ""
    while not title:
        title = input("Enter book title: ").strip()
        if not title:
            print("Book title cannot be empty. Please try again.")

    author = ""
    while not author:
        author = input("Enter author: ").strip()
        if not author:
            print("Author name cannot be empty. Please try again.")

    year_input = input("Enter publication year: ").strip()
    try:
        year = int(year_input)
        if not (1000 <= year <= 2100):
            print(f"Warning: year {year} seems unusual. Using it anyway.")
    except ValueError:
        print(f"Invalid year '{year_input}'. Defaulting to 0.")
        year = 0

    return title, author, year


def print_books(books: list[Book]) -> None:
    if not books:
        print("No books in your collection.")
        return

    print("\nYour Books:")
    for index, book in enumerate(books, start=1):
        status = "✅ Read" if book.read else "📖 Unread"
        print(f"{index}. {book.title} by {book.author} ({book.year}) - {status}")
