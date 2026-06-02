import sys
from books import BookCollection
from utils import print_books


# Global collection instance
collection = BookCollection()


def handle_list():
    books = collection.list_books()
    print_books(books)


def handle_add():
    print("\nAdd a New Book\n")

    title = input("Title: ").strip()
    author = input("Author: ").strip()
    year_str = input("Year: ").strip()

    try:
        year = int(year_str) if year_str else 0
        collection.add_book(title, author, year)
        print("\nBook added successfully.\n")
    except ValueError as e:
        print(f"\nError: {e}\n")


def handle_remove():
    print("\nRemove a Book\n")

    title = input("Enter the title of the book to remove: ").strip()
    collection.remove_book(title)

    print("\nBook removed if it existed.\n")


def handle_find():
    print("\nFind Books by Author\n")

    author = input("Author name: ").strip()
    books = collection.find_by_author(author)

    print_books(books)


def handle_year():
    print("\nSearch Books by Year\n")

    raw = input("Enter year or range (e.g. 1965 or 1940-1960): ").strip()

    try:
        if "-" in raw.lstrip("-"):
            # Range input: "1940-1960"
            parts = raw.split("-")
            start, end = int(parts[0]), int(parts[1])
            books = collection.find_by_year_range(start, end)
        else:
            # Exact year input: "1965"
            year = int(raw)
            books = collection.find_by_year(year)
    except ValueError as e:
        print(f"\nError: {e}\n")
        return

    if not books:
        print("\nNo books found for that year.\n")
    else:
        print_books(books)


def handle_unread():
    books = collection.get_unread_books()
    if not books:
        print("\nNo unread books in your collection.\n")
    else:
        print_books(books)


def show_help():
    print("""
Book Collection Helper

Commands:
  list     - Show all books
  year     - Search books by year or year range
  unread   - Show only unread books
  add      - Add a new book
  remove   - Remove a book by title
  find     - Find books by author
  help     - Show this help message
""")


COMMANDS = {
    "list": handle_list,
    "year": handle_year,
    "unread": handle_unread,
    "add": handle_add,
    "remove": handle_remove,
    "find": handle_find,
    "help": show_help,
}


def main():
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()
    handler = COMMANDS.get(command)

    if handler:
        handler()
    else:
        print("Unknown command.\n")
        show_help()


if __name__ == "__main__":
    main()
