def clear_entries(entries):
    for entry in entries:
        entry.delete(0, "end")
    return


def get_latest_cid(session):
    rows = session.execute('SELECT * from parking_lot')
    if not rows:
        print('no matched record')
        return 0
    else:
        rows = list(rows)
        return len(rows)


def add_car(name_entry, position_entry, car_make_entry, car_model_entry, session):
    entries = [name_entry, position_entry, car_make_entry, car_model_entry]
    name = name_entry.get()
    position = position_entry.get()
    car_make = car_make_entry.get()
    car_model = car_model_entry.get()

    # check for mis-info
    if any(elem == "" for elem in [name, position, car_make, car_model]):
        print("you missed some information; plz try again")
        clear_entries(entries)
        return
    car_id = get_latest_cid(session) + 1
    cql = f"INSERT INTO parking_lot (employee_name, cid, car_make, car_model, position) \
            VALUES ('{name}', {car_id}, '{car_make}', '{car_model}', '{position}') \
            if not exists"
    session.execute(cql)
    print("a new car cid:", car_id, "is added to the parking lot management system")
    clear_entries(entries)
    return

# def del
