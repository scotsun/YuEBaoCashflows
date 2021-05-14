def clear_entries(entries):
    for entry in entries:
        entry.delete(0, "end")
    return


def add_book(title_entry, author_entry, isbn_entry, page_number_entry, session):
    entries = [title_entry, author_entry, isbn_entry, page_number_entry]
    title = title_entry.get()
    author = author_entry.get()
    page_number = page_number_entry.get()
    isbn = isbn_entry.get()

    author_set = set(author.split(sep=", "))

    # check for mis-info
    if any(elem == "" for elem in [title, author, page_number, isbn]):
        print("you missed some information; plz try again")
        clear_entries(entries)
        return
    try:
        int(page_number)
    except ValueError:
        print("incorrect value for page number; plz try again")
        clear_entries(entries)
        return
    if int(page_number) <= 0:
        print("incorrect value for page number; it should be positive")
        clear_entries(entries)
        return
    book_rows = session.execute(f"SELECT * from books where isbn = '{isbn}'")
    if not book_rows:
        cql = f"INSERT INTO books (isbn, author, title, numpage) \
                VALUES ('{isbn}', {author_set}, '{title}', {page_number})"
        session.execute(cql)
    cql = f"UPDATE books SET numbook = numbook + 1 where isbn = '{isbn}'"
    session.execute(cql)

    print("a new book is added, isbn:", isbn)
    clear_entries(entries)
    return


def search_book(title_entry, author_entry, isbn_entry, session):
    entries = [title_entry, author_entry, isbn_entry]

    title = title_entry.get()
    author = author_entry.get()
    isbn = isbn_entry.get()

    if all(elem == "" for elem in [title, author, isbn]):
        print("you should provide information for search")
        return 0

    if isbn != "":
        cql = f"select * from books where isbn = '{isbn}'"
    elif author != "":
        cql = f"select * from books where author contains '{author}'"
    else:
        cql = f"select * from books where title = '{title}'"

    book_rows = session.execute(cql)
    for r in book_rows:
        print(r)
    clear_entries(entries)
    return 1


def del_book(isbn_entry, session):
    entries = [isbn_entry]
    isbn = isbn_entry.get()
    book_row = session.execute(f"SELECT * from books where isbn='{isbn}'")
    if not book_row:
        clear_entries(entries)
        print("this book does not exist")
        return
    session.execute(f"DELETE from books where isbn='{isbn}'")
    print("book: " + isbn + " deleted")
    clear_entries(entries)
    return


def edit_book(title_entry, author_entry, isbn_entry, page_number_entry, session):
    entries = [title_entry, author_entry, isbn_entry, page_number_entry]
    isbn = isbn_entry.get()
    book_row = session.execute(f"SELECT * from books where isbn='{isbn}'")
    if not book_row:
        clear_entries(entries)
        print("this book does not exist")
        return
    new_title = title_entry.get()
    new_author = author_entry.get()
    new_author_set = set(new_author.split(sep=", "))
    new_page_number = page_number_entry.get()
    # check for mis-info
    if any(elem == "" for elem in [new_title, new_author, new_page_number]):
        print("some information is missed for the update; plz try again")
        clear_entries(entries)
        return
    if new_page_number != "":
        try:
            int(new_page_number)
        except ValueError:
            print("incorrect value for page number; plz try again")
            clear_entries(entries)
            return
        if int(new_page_number) <= 0:
            print("incorrect value for page number; it should be positive")
            clear_entries(entries)
            return

    cql = f"UPDATE books set author = {new_author_set}, title = '{new_title}', numpage = {new_page_number} \
           where isbn = 'B100'"
    session.execute(cql)
    print("book: " + isbn + " is edited")
    clear_entries(entries)
    return

