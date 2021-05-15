from random import randint


def clear_entries(entries):
    for entry in entries:
        entry.delete(0, "end")
    return


def get_cid():
    return randint(1, 1000)


def add_car(uname_entry, position_entry, car_make_entry, car_model_entry, session):
    entries = [uname_entry, position_entry, car_make_entry, car_model_entry]
    uname = uname_entry.get()
    position = position_entry.get()
    car_make = car_make_entry.get()
    car_model = car_model_entry.get()

    # check for mis-info
    if any(elem == "" for elem in [uname, position, car_make, car_model]):
        print("you missed some information; plz try again")
        clear_entries(entries)
        return

    car_id = get_cid()
    cql = f"INSERT INTO parking_lot (employee_uname, cid, car_make, car_model, position) \
            VALUES ('{uname}', {car_id}, '{car_make}', '{car_model}', '{position}') \
            if not exists"
    session.execute(cql)
    print("a new car cid:", car_id, "is added to the parking lot management system")
    clear_entries(entries)
    return


def del_car(uname_entry, car_id_entry, session):
    entries = [uname_entry, car_id_entry]
    uname = uname_entry.get()
    cid = car_id_entry.get()

    # check for mis-info
    if any(elem == "" for elem in [uname, cid]):
        print("you missed some information; plz try again")
        clear_entries(entries)
        return
    try:
        cid = int(cid)
    except ValueError:
        print("incorrect form of car id")
        clear_entries(entries)
        return
    # check if exist
    cid_row = session.execute(f"SELECT * from parking_lot where uname='{uname}' and cid={cid}")
    if not cid_row:
        clear_entries(entries)
        print("this book does not exist")
        return

    cql = f"DELETE from parking_lot where employee_uname='{uname}' and cid={cid}"
    session.execute(cql)
    print(f"car: {cid} deleted")
    clear_entries(entries)
    return


def edit_car(uname_entry, car_id_entry, position_entry, car_make_entry, car_model_entry, session):
    entries = [uname_entry, car_id_entry, position_entry, car_make_entry, car_model_entry]
    uname = uname_entry.get()
    cid = car_id_entry.get()
    position = position_entry.get()
    car_make = car_make_entry.get()
    car_model = car_model_entry.get()

    # check for mis-info
    if any(elem == "" for elem in [uname, cid, position, car_make, car_model]):
        print("you missed some information; plz try again")
        clear_entries(entries)
        return
    try:
        cid = int(cid)
    except ValueError:
        print("incorrect form of car id")
        clear_entries(entries)
        return
    # check if exist
    cid_row = session.execute(f"SELECT * from parking_lot where employee_uname='{uname}' and cid={cid}")
    if not cid_row:
        clear_entries(entries)
        print("this book does not exist")
        return

    cql = f"update parking_lot set position = '{position}', car_make = '{car_make}',  \
            car_model = '{car_model}' where employee_uname = '{uname}' and cid = {cid};"
    session.execute(cql)
    print(f"car: {cid} updated")
    clear_entries(entries)
    return


def search_car(uname_entry, car_id_entry, position_entry, car_make_entry, car_model_entry, session):
    entries = [uname_entry, car_id_entry, position_entry, car_make_entry, car_model_entry]
    uname = uname_entry.get()
    cid = car_id_entry.get()
    position = position_entry.get()
    car_make = car_make_entry.get()
    car_model = car_model_entry.get()

    try:
        if cid == "":
            cid = -1
        else:
            cid = int(cid)
    except ValueError:
        print("incorrect form of car id")
        clear_entries(entries)
        return
    inputs = [uname, cid, position, car_make, car_model]
    input_names = ['employee_name', 'cid', 'position', 'car_make', 'car_model']
    # check for mis-info
    if all(elem == "" for elem in inputs):
        print("you missed some information; plz try again")
        clear_entries(entries)
        return

    values = []
    where = input_names.copy()
    for i in range(len(inputs)):
        if inputs[i] == "":
            where.remove(input_names[i])
        else:
            values.append(inputs[i])
    cql = "select * from parking_lot "
    cql = cql + "where "
    for i in range(len(where) - 1):
        if where[i] != 'cid':
            add = f"{where[i]} = '{values[i]}' and "
        else:
            add = f"{where[i]} = {values[i]} and "
        cql = cql + add
    n = len(where) - 1
    if where[n] != 'cid':
        add = f"{where[n]} = '{values[n]}'"
    else:
        add = f"{where[n]} = {values[n]}"
    cql = cql + add
    print(cql)
    rows = session.execute(cql)
    if not rows:
        print("no matched record")
    for row in rows:
        print(row)
    clear_entries(entries)
    return


def list_all_cars(session):
    cql = f"select * from parking_lot"
    rows = session.execute(cql)
    if not rows:
        print("no car is registered yet")
    print("registered cars:")
    for row in rows:
        print(row)
