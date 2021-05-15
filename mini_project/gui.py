import tkinter
from tkinter import ttk
from cassandra.cluster import Cluster
from cassandra.query import dict_factory
from ssh import *
from employee_features import *


def main():
    # connect to cassandra
    tunnel.start()
    cluster = Cluster(['34.67.124.229'])
    session = cluster.connect('test_keyspace')
    session.row_factory = dict_factory
    root = tkinter.Tk()
    root.title("Parking lot System")
    make_employees_frame(root, session)
    root.mainloop()


def make_employees_frame(root, session):
    employees_frame = ttk.Frame(root, padding=20)
    employees_frame.grid(row=0)
    v = tkinter.StringVar()

    # input entries
    uname_label = ttk.Label(employees_frame, text="UName")
    uname_entry = ttk.Entry(employees_frame, width=8)
    position_label = ttk.Label(employees_frame, text="Position")
    position_entry = ttk.Entry(employees_frame, width=8)
    car_make_label = ttk.Label(employees_frame, text="Car Make")
    car_make_entry = ttk.Entry(employees_frame, width=8)
    car_model_label = ttk.Label(employees_frame, text="Car Model")
    car_model_entry = ttk.Entry(employees_frame, width=8)
    cid_label = ttk.Label(employees_frame, text="Car ID")
    cid_entry = ttk.Entry(employees_frame, width=8)

    uname_label.grid(row=0, column=0)
    uname_entry.grid(row=0, column=1)
    position_label.grid(row=0, column=2)
    position_entry.grid(row=0, column=3)
    car_make_label.grid(row=1, column=0)
    car_make_entry.grid(row=1, column=1)
    car_model_label.grid(row=1, column=2)
    car_model_entry.grid(row=1, column=3)
    cid_label.grid(row=2, column=0)
    cid_entry.grid(row=2, column=1)

    # add buttons
    add_employee_button = ttk.Button(employees_frame, text="add car")
    del_employee_button = ttk.Button(employees_frame, text="delete car")
    edit_employee_button = ttk.Button(employees_frame, text="edit car")
    list_all_employees_button = ttk.Button(employees_frame, text="all cars")

    add_employee_button.grid(row=3, column=0)
    del_employee_button.grid(row=3, column=1)
    edit_employee_button.grid(row=3, column=2)
    list_all_employees_button.grid(row=3, column=3)

    add_employee_button['command'] = lambda: add_car(uname_entry, position_entry, car_make_entry, car_model_entry,
                                                     session)
    del_employee_button['command'] = lambda: del_car(uname_entry, cid_entry, session)
    edit_employee_button['command'] = lambda: edit_car(uname_entry, cid_entry, position_entry, car_make_entry,
                                                       car_model_entry, session)
    list_all_employees_button['command'] = lambda: list_all_cars(session)
    return


main()
