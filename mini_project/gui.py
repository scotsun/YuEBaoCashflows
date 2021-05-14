import tkinter
from tkinter import ttk
from cassandra.cluster import Cluster
from ssh import *
from employee_features import *


def main():
    # connect to cassandra
    tunnel.start()
    cluster = Cluster(['34.67.124.229'])
    session = cluster.connect('test_keyspace')

    root = tkinter.Tk()
    root.title("Parking lot System")
    make_employees_frame(root, session)
    root.mainloop()


def make_employees_frame(root, session):
    employees_frame = ttk.Frame(root, padding=20)
    employees_frame.grid(row=0)
    v = tkinter.StringVar()

    # input entries
    name_label = ttk.Label(employees_frame, text="Name")
    name_entry = ttk.Entry(employees_frame, width=8)
    position_label = ttk.Label(employees_frame, text="Position")
    position_entry = ttk.Entry(employees_frame, width=8)
    car_make_label = ttk.Label(employees_frame, text="Car Make")
    car_make_entry = ttk.Entry(employees_frame, width=8)
    car_model_label = ttk.Label(employees_frame, text="Car Model")
    car_model_entry = ttk.Entry(employees_frame, width=8)

    name_label.grid(row=0, column=0)
    name_entry.grid(row=0, column=1)
    position_label.grid(row=0, column=2)
    position_entry.grid(row=0, column=3)
    car_make_label.grid(row=1, column=0)
    car_make_entry.grid(row=1, column=1)
    car_model_label.grid(row=1, column=2)
    car_model_entry.grid(row=1, column=3)

    # add buttons
    add_employee_button = ttk.Button(employees_frame, text="add car")
    del_employee_button = ttk.Button(employees_frame, text="delete car")
    edit_employee_button = ttk.Button(employees_frame, text="edit car")
    search_employee_button = ttk.Button(employees_frame, text="search car")
    list_all_employees_button = ttk.Button(employees_frame, text="all employees' cars")

    add_employee_button.grid(row=3, column=0)
    del_employee_button.grid(row=3, column=1)
    edit_employee_button.grid(row=3, column=2)
    search_employee_button.grid(row=3, column=3)
    list_all_employees_button.grid(row=4, column=0)

    add_employee_button['command'] = lambda: add_car(name_entry, position_entry, car_make_entry,
                                                     car_model_entry, session)
    # add_employee_button['command'] = lambda: del_employee(car_make_entry, session)
    # add_employee_button['command'] = lambda: edit_employee(name_entry, id_entry, car_make_entry,
    #                                                        car_model_entry, session)
    # add_employee_button['command'] = lambda: search_employee(name_entry, id_entry, car_make_entry, session)
    return


main()
