# Book Collection App

*(This README is intentionally rough so you can improve it with GitHub Copilot CLI)*

A Python app for managing books you have or want to read.
It can add, remove, and list books. Also mark them as read.

---

## Current Features

* Reads and writes books from a JSON file (`data.json`)
* Add, remove, and list books
* Mark books as read/unread
* Find books by author name (partial match supported)
* Search books by exact year or year range (e.g. `1940-1960`)
* Show only unread books
* Input checking is weak in some areas
* Some tests exist but probably not enough

---

## Files

* `book_app.py` - Main CLI entry point
* `books.py` - BookCollection class with data logic
* `utils.py` - Helper functions for UI and input
* `data.json` - Sample book data
* `tests/test_books.py` - Starter pytest tests

---

## Running the App

```bash
python book_app.py list     # Show all books
python book_app.py unread   # Show only unread books
python book_app.py year     # Search by year or year range (e.g. 1965 or 1940-1960)
python book_app.py add      # Add a new book
python book_app.py remove   # Remove a book by title
python book_app.py find     # Find books by author name
python book_app.py help     # Show available commands
```

## Running Tests

```bash
python -m pytest tests/
```

---

## Notes

* Not production-ready (obviously)
* Some code could be improved
* Could add more commands later
