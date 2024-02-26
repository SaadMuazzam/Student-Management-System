import customtkinter
import customtkinter as ctk
import tkinter as tk
from tkinter import *
import tkinter.messagebox as mb
from tkinter import ttk
import datetime
from tkcalendar import DateEntry
import sqlite3



# Creating the global variable for tree
tree = None

# Creating the universal font variables
headlabelfont = ("Segoe", 15, 'bold')
labelfont = ('Arial', 14)
entryfont = ('Arial', 12)

# Connecting to the Database where all information will be stored
connector = sqlite3.connect('SchoolManagement.db')
cursor = connector.cursor()

connector.execute(
    "CREATE TABLE IF NOT EXISTS SCHOOL_MANAGEMENT \
    (STUDENT_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
    FIRST_NAME TEXT, LAST_NAME TEXT, EMAIL TEXT, PHONE_NO TEXT, \
    GENDER TEXT, DOB TEXT, STREAM TEXT, ROLL TEXT)"
)

# Creating the functions
def reset_fields():
    global first_name_strvar, last_name_strvar, email_strvar, contact_strvar, gender_strvar, dob, stream_strvar, rollNumber_strvar

    for var in [first_name_strvar, last_name_strvar, email_strvar, contact_strvar, gender_strvar, stream_strvar, rollNumber_strvar]:
        var.set('')

    dob.set_date(datetime.datetime.now().date())

def reset_form():
    global tree
    tree.delete(*tree.get_children())
    reset_fields()

def display_records():
    global tree

    if tree:
        tree.delete(*tree.get_children())
    else:
        mb.showerror('Tree Not Defined', 'Tree widget is not defined.')

    curr = connector.execute('SELECT * FROM SCHOOL_MANAGEMENT')
    data = curr.fetchall()
    for records in data:
        tree.insert('', END, values=records)

def update_record():
    global first_name_strvar, last_name_strvar, email_strvar, contact_strvar, gender_strvar, dob, stream_strvar, rollNumber_strvar

    first_name = first_name_strvar.get()
    last_name = last_name_strvar.get()
    email = email_strvar.get()
    contact = contact_strvar.get()
    gender = gender_strvar.get()
    DOB = dob.get_date()
    stream = stream_strvar.get()
    roll = rollNumber_strvar.get()
    
    current_item = tree.focus()
    values = tree.item(current_item)
    selection = values["values"]
    student_id = selection[0]

    cursor.execute("SELECT COUNT(*) FROM SCHOOL_MANAGEMENT WHERE ROLL=? AND STUDENT_ID <> ?", (roll, student_id))
    count = cursor.fetchone()[0]
    if count > 0:
        mb.showerror('Roll Number Exists', 'Roll Number already exists!')
        return

    if not contact.isdigit():
        mb.showerror('Invalid Contact', 'The contact field can only contain numeric characters.')
        return

    if len(contact) < 10:
        mb.showerror('Invalid Contact', 'The contact number should be at least 10 digits long.')
        return

    # Check if the email is valid using the is_valid_email function
    if not is_valid_email(email):
        mb.showerror('Invalid Email', 'Please enter a valid email address.')
        return

    if not all([first_name, last_name, email, contact, gender, DOB, stream]):
        mb.showerror('Error!', "Please fill all the missing fields!!")
    else:
        try:
            connector.execute(
                'UPDATE SCHOOL_MANAGEMENT \
                SET FIRST_NAME=?, LAST_NAME=?, EMAIL=?, PHONE_NO=?, GENDER=?, DOB=?, STREAM=?, ROLL=? \
                WHERE STUDENT_ID=?',
                (first_name, last_name, email, contact, gender, DOB, stream, roll, student_id)
            )
            connector.commit()
            mb.showinfo('Record Updated', f"Record of {first_name} {last_name} was successfully updated")
            reset_fields()
            display_records()
        except sqlite3.Error as e:
            mb.showerror('Error', 'An error occurred while updating the record: ' + str(e))
            
            
def is_valid_email(email):
    # Split the email into parts
    parts = email.split('@')

    # Check if there are exactly two parts (username and domain)
    if len(parts) != 2:
        return False

    username, domain = parts

    # Check if the username and domain have at least one character
    if len(username) == 0 or len(domain) == 0:
        return False

    # Check if there is a period (.) in the domain part
    if '.' not in domain:
        return False

    # Check if the last part of the domain contains only letters and has at least two characters
    domain_parts = domain.split('.')
    if not all(part.isalpha() for part in domain_parts) or len(domain_parts[-1]) < 2:
        return False

    return True

def add_record():
    global first_name_strvar, last_name_strvar, email_strvar, contact_strvar, gender_strvar, dob, stream_strvar, rollNumber_strvar

    first_name = first_name_strvar.get()
    last_name = last_name_strvar.get()
    email = email_strvar.get()
    contact = contact_strvar.get()
    gender = gender_strvar.get()
    DOB = dob.get_date()
    stream = stream_strvar.get()
    roll = rollNumber_strvar.get().upper()  # Convert to uppercase

    cursor.execute("SELECT COUNT(*) FROM SCHOOL_MANAGEMENT WHERE ROLL=?", (roll,))
    count = cursor.fetchone()[0]
    if count > 0:
        mb.showerror('Roll Number Exists', 'Roll Number already exists!')
        return

    if not contact.isdigit():
        mb.showerror('Invalid Contact', 'The contact field can only contain numeric characters.')
        return

    if len(contact) < 10:
        mb.showerror('Invalid Contact', 'The contact number should be at least 10 digits long.')
        return

    # Check if the email is valid using the is_valid_email function
    if not is_valid_email(email):
        mb.showerror('Invalid Email', 'Please enter a valid email address.')
        return

    if not all([first_name, last_name, email, contact, gender, DOB, stream]):
        mb.showerror('Error!', "Please fill all the missing fields!!")
    else:
        try:
            connector.execute(
                'INSERT INTO SCHOOL_MANAGEMENT \
                (FIRST_NAME, LAST_NAME, EMAIL, PHONE_NO, GENDER, DOB, STREAM,ROLL) \
                VALUES (?,?,?,?,?,?,?,?)', (first_name, last_name, email, contact, gender, DOB, stream, roll)
            )
            connector.commit()
            mb.showinfo('Record added', f"Record of {first_name} {last_name} was successfully added")
            reset_fields()
            display_records()
        except sqlite3.Error as e:
            mb.showerror('Database Error', f'An error occurred while adding the record: {e}')


def remove_record():
    if not tree.selection():
        mb.showerror('Error!', 'Please select an item from the database')
    else:
        current_item = tree.focus()
        values = tree.item(current_item)
        selection = values["values"]

        tree.delete(current_item)

        connector.execute('DELETE FROM SCHOOL_MANAGEMENT \
            WHERE STUDENT_ID=%d' % selection[0])
        connector.commit()

        mb.showinfo('Done', 'The record you wanted deleted was successfully deleted.')

        display_records()

def search_record():
    global search_var

    roll_to_search = search_var.get().strip().upper()  # Remove leading/trailing spaces and convert to uppercase

    if not roll_to_search:
        mb.showerror('Empty Search', 'Please enter a roll number to search.')
    else:
        cursor.execute("SELECT * FROM SCHOOL_MANAGEMENT WHERE UPPER(ROLL)=?", (roll_to_search,))
        record = cursor.fetchone()
        if record:
            first_name_strvar.set(record[1])
            last_name_strvar.set(record[2])
            email_strvar.set(record[3])
            contact_strvar.set(record[4])
            gender_strvar.set(record[5])
            dob.set_date(datetime.date(int(record[6][:4]), int(record[6][5:7]), int(record[6][8:])))
            stream_strvar.set(record[7])
            rollNumber_strvar.set(record[8])

            # Create formatted details with line breaks
            details = f"First Name: {record[1]}\n\n"
            details += f"Last Name: {record[2]}\n\n"
            details += f"Email: {record[3]}\n\n"
            details += f"Contact: {record[4]}\n\n"
            details += f"Gender: {record[5]}\n\n"
            details += f"DOB: {record[6]}\n\n"
            details += f"Stream: {record[7]}\n\n"
            details += f"Roll Number: {record[8]}\n"

            # Create a larger message box with word wrap
            msg_box = mb.showinfo('Student Details', details, icon=mb.INFO)
            msg_box.geometry("1000x600")  # Adjust the size of the message box
            msg_box.configure(wraplength=480)  # Set word wrap to avoid horizontal scroll

        else:
            mb.showerror('Not Found', 'No records found for the given roll number.')

            
            
def view_record():
    global first_name_strvar, last_name_strvar, email_strvar, contact_strvar, gender_strvar, dob, stream_strvar, rollNumber_strvar

    current_item = tree.focus()
    values = tree.item(current_item)
    selection = values["values"]

    details = f"First Name: {selection[1]}\n\n"
    details += f"Last Name: {selection[2]}\n\n"
    details += f"Email: {selection[3]}\n\n"
    details += f"Contact: {selection[4]}\n\n"
    details += f"Gender: {selection[5]}\n\n"
    details += f"DOB: {selection[6]}\n\n"
    details += f"Stream: {selection[7]}\n\n"
    details += f"Roll Number: {selection[8]}\n\n"

    mb.showinfo('Student Details', details)
    date = datetime.date(int(selection[6][:4]),
                int(selection[6][5:7]), int(selection[6][8:]))

    first_name_strvar.set(selection[1])
    last_name_strvar.set(selection[2])
    email_strvar.set(selection[3])
    contact_strvar.set(selection[4])
    gender_strvar.set(selection[5])
    dob.set_date(date)
    stream_strvar.set(selection[7])
    rollNumber_strvar.set(selection[8])

def open_main_window():
    global main, search_var, first_name_strvar, last_name_strvar, email_strvar, contact_strvar, gender_strvar, stream_strvar, rollNumber_strvar, tree

    main = Tk()
    main.title('School Management System')
    #main.geometry('1050x600')
    #main.resizable(0, 0)

    # Creating the StringVar or IntVar variables
    search_var = StringVar()
    first_name_strvar = StringVar()
    last_name_strvar = StringVar()
    email_strvar = StringVar()
    contact_strvar = StringVar()
    gender_strvar = StringVar()
    stream_strvar = StringVar()
    rollNumber_strvar = StringVar()

        # Creating fonts
    verdana_font = ("Verdana", 12)
    labelfont = ("Verdana", 14)
    entryfont = ("Verdana", 12)
    headlabelfont = ("Verdana", 18)

    # Creating the background and foreground color variables
    lf_bg = 'SteelBlue4'  # bg color for the left_frame
    cf_bg = 'DarkBlue'  # bg color for the center_frame

    # Placing the components in the main window
    Label(main, text="SCHOOL MANAGEMENT SYSTEM",
        font=headlabelfont, bg='SteelBlue').pack(side=TOP, fill=X)

    # Creating horizontal frames
    top_frame = Frame(main, bg="SteelBlue4")
    top_frame.pack(fill=X, padx=10, pady=6)

    middle_frame = Frame(main, bg="SteelBlue")
    middle_frame.pack(fill=X, padx=10, pady=10)

    bottom_frame = Frame(main, bg="GRAY")
    bottom_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

    # Placing components in the top frame
    Label(top_frame, text="First Name", font=labelfont, bg=lf_bg, fg="white").grid(row=0, column=0, padx=10, pady=5)
    Label(top_frame, text="Last Name", font=labelfont, bg=lf_bg, fg="white").grid(row=0, column=2, padx=10, pady=5)
    Label(top_frame, text="Contact Number", font=labelfont, bg=lf_bg, fg="white").grid(row=0, column=4, padx=10, pady=5)
    Label(top_frame, text="Email", font=labelfont, bg=lf_bg, fg="white").grid(row=3, column=0, padx=10, pady=5)
    Label(top_frame, text="Gender", font=labelfont, bg=lf_bg, fg="white").grid(row=3, column=2, padx=10, pady=5)
    Label(top_frame, text="Date of Birth (DOB)", font=labelfont, bg=lf_bg, fg="white").grid(row=3, column=4, padx=10, pady=5)
    Label(top_frame, text="Stream", font=labelfont, bg=lf_bg, fg="white").grid(row=6, column=0, padx=10, pady=5)
    Label(top_frame, text="Roll No.", font=labelfont, bg=lf_bg, fg="white").grid(row=6, column=2, padx=10, pady=5)

    Entry(top_frame, textvariable=first_name_strvar, font=entryfont).grid(row=0, column=1, padx=10, pady=5)
    Entry(top_frame, textvariable=last_name_strvar, font=entryfont).grid(row=0, column=3, padx=10, pady=5)
    Entry(top_frame, textvariable=contact_strvar, font=entryfont).grid(row=0, column=5, padx=10, pady=5)
    Entry(top_frame, textvariable=email_strvar, font=entryfont).grid(row=3, column=1, padx=10, pady=5)
    Entry(top_frame, textvariable=rollNumber_strvar, font=entryfont).grid(row=6, column=3, padx=10, pady=5)

    stream_options = ['Science', 'Commerce']  # List of available options
    stream_strvar.set(stream_options[0])
    OptionMenu(top_frame, stream_strvar, *stream_options).grid(row=6, column=1, padx=10, pady=5)

    OptionMenu(top_frame, gender_strvar, 'Male', 'Female').grid(row=3, column=3, padx=5, pady=5)
    dob = DateEntry(top_frame, font=("Arial", 12), width=15)
    dob.grid(row=3, column=5, padx=10, pady=5)

    # Placing components in the middle frame
    Button(middle_frame, text='Submit Record', font=labelfont, command=add_record, width=15).grid(row=0, column=3, padx=10, pady=5)
    Button(middle_frame, text='Update Record', font=labelfont, command=update_record, width=15).grid(row=0, column=4, padx=10, pady=5)
    Button(middle_frame, text='Delete Record', font=labelfont, command=remove_record, width=15).grid(row=0, column=5, padx=10, pady=5)
    Button(middle_frame, text='View Record', font=labelfont, command=view_record, width=15).grid(row=0, column=6, padx=10, pady=5)
    Button(middle_frame, text='Reset Fields', font=labelfont, command=reset_fields, width=15).grid(row=0, column=7, padx=10, pady=5)
    Button(middle_frame, text='Delete database', font=labelfont, command=reset_form, width=15).grid(row=1, column=5, padx=10, pady=5)

    # Placing components in the bottom frame
    Label(bottom_frame, text='Students Records', font=headlabelfont, bg='DeepSkyBlue4', fg='White').pack(side=TOP, fill=X)

    tree = ttk.Treeview(bottom_frame, height=100,
                        selectmode=BROWSE,
                        columns=("Student ID", "First Name", "Last Name",
                                "Email Address", "Contact Number", "Gender", "Date of Birth", "Stream", "Roll Number"))

    X_scroller = Scrollbar(tree, orient=HORIZONTAL, command=tree.xview)
    Y_scroller = Scrollbar(tree, orient=VERTICAL, command=tree.yview)

    X_scroller.pack(side=BOTTOM, fill=X)
    Y_scroller.pack(side=RIGHT, fill=Y)

    tree.config(yscrollcommand=Y_scroller.set, xscrollcommand=X_scroller.set)

    tree.heading('#1', text='ID', anchor=CENTER)
    tree.heading('#2', text='First Name', anchor=CENTER)
    tree.heading('#3', text='Last Name', anchor=CENTER)
    tree.heading('#4', text='Email ID', anchor=CENTER)
    tree.heading('#5', text='Phone No', anchor=CENTER)
    tree.heading('#6', text='Gender', anchor=CENTER)
    tree.heading('#7', text='DOB', anchor=CENTER)
    tree.heading('#8', text='Stream', anchor=CENTER)
    tree.heading('#9', text='Roll Number', anchor=CENTER)

    # Adjust the column widths to fit within the Treeview's width
    tree.column('#0', width=0, stretch=NO)
    tree.column('#1', width=40, stretch=NO)
    tree.column('#2', width=100, stretch=NO)
    tree.column('#3', width=100, stretch=NO)
    tree.column('#4', width=180, stretch=NO)
    tree.column('#5', width=100, stretch=NO)
    tree.column('#6', width=50, stretch=NO)
    tree.column('#7', width=80, stretch=NO)
    tree.column('#8', width=70, stretch=NO)
    tree.column('#9', width=90, stretch=NO)

    tree.pack(fill=BOTH, expand=YES)

    # Create an entry field for searching
    search_var = StringVar()
    #search_var.set("")
    search_entry = Entry(bottom_frame, textvariable=search_var, font=entryfont)
    search_entry.pack(side=LEFT, padx=10, pady=10)
    search_button = Button(bottom_frame, text="Search", font=labelfont, command=search_record)
    search_button.pack(side=LEFT, padx=10, pady=10)

    # Populate the Treeview with existing records
    display_records()
    # Finalizing the GUI window
    main.update()
    main.geometry("1100x600")
    main.attributes('-fullscreen', True)


    main.mainloop()

def login_window():
    login = ctk.CTk()
    login.title('Login')
    login.geometry('300x400')
    
    # Load the image
    frame = ctk.CTkFrame(login, width=700, height=600, border_color="red", fg_color="grey")
    frame.grid(padx=40,pady=45)

    username = ctk.CTkLabel(frame, text="Username",font=("Helvetica",20),text_color="white")
    username.grid(row=0, column=0, padx=40, pady=20)
    username_entry = ctk.CTkEntry(frame)
    username_entry.grid(row=1, column=0, padx=40, pady=5)

    password = ctk.CTkLabel(frame, text="Password",font=("Helvetica",20),text_color="white")
    password_entry = ctk.CTkEntry(frame, show="*")

    password_entry.grid(row=3, column=0, padx=40, pady=5)

    def validate_login():
        username = username_entry.get()
        password = password_entry.get()

        # Check the username and password (You can replace this with your own logic)
        if username == "admin" and password == "123":
            login.destroy()
            open_main_window()
        else:
            mb.showerror('Invalid Login', 'Invalid username or password')

    mybutton = ctk.CTkButton(frame, text="Login", command=validate_login) # Assign check_credentials function to the button click
    mybutton.grid(row=4, column=0, columnspan=2, padx=40, pady=40)

    login.resizable(False, False)
    login.mainloop()

# Test the login window

login_window()