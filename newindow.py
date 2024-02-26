import customtkinter
import customtkinter as ctk
import tkinter as tk
from tkinter import *
import tkinter.messagebox as mb
from tkinter import ttk
import datetime
from tkcalendar import DateEntry
import sqlite3

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

    for var in [first_name_strvar, last_name_strvar, email_strvar, contact_strvar, gender_strvar, stream_strvar,
                rollNumber_strvar]:
        var.set('')

    dobEntry.set_date(datetime.datetime.now().date())


def reset_form():
    global tree
    tree.delete(*tree.get_children())
    reset_fields()


def display_records():
    tree.delete(*tree.get_children())
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
    DOB = dobEntry.get_date()
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
    DOB = dobEntry.get_date()
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
    global first_name_strvar, last_name_strvar, email_strvar, contact_strvar, gender_strvar, dob, stream_strvar, rollNumber_strvar

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
            dobEntry.set_date(datetime.date(int(record[6][:4]), int(record[6][5:7]), int(record[6][8:])))
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
    dobEntry.set_date(date)
    stream_strvar.set(selection[7])
    rollNumber_strvar.set(selection[8])

customtkinter.set_appearance_mode("light")

new_window = ctk.CTk()
new_window.geometry('300x300')
new_window.title("School Management System")
FirstFrame = ctk.CTkFrame(new_window,width=1150,height=350,corner_radius=20)
FirstFrame.grid(row=0, column=0,padx=55,pady=15)

first_name_strvar = StringVar()
last_name_strvar = StringVar()
email_strvar = StringVar()
contact_strvar = StringVar()
gender_strvar = StringVar()
stream_strvar = StringVar()
rollNumber_strvar = StringVar()
search_var = StringVar()


firstName=ctk.CTkLabel(FirstFrame,text="First Name:",font=("Helvetica",20))
fnameEntry=ctk.CTkEntry(FirstFrame,textvariable=first_name_strvar,width=135,font=("Helvetica",16),corner_radius=10)

lastName=ctk.CTkLabel(FirstFrame,text="Last Name:",font=("Helvetica",20))
lnameEntry=ctk.CTkEntry(FirstFrame,textvariable=last_name_strvar,width=135,font=("Helvetica",16),corner_radius=10)

roll=ctk.CTkLabel(FirstFrame,text="Roll No.:",font=("Helvetica",20))
rollEntry=ctk.CTkEntry(FirstFrame, textvariable=rollNumber_strvar, width=135,font=("Helvetica",16),corner_radius=10)

email=ctk.CTkLabel(FirstFrame,text="Email:",font=("Helvetica",20))
emailEntry=ctk.CTkEntry(FirstFrame,textvariable=email_strvar, width=210,font=("Helvetica",16),corner_radius=10)

contactNo=ctk.CTkLabel(FirstFrame,text="Conatct No.:",font=("Helvetica",20))
contactEntry=ctk.CTkEntry(FirstFrame, textvariable=contact_strvar , width=135,font=("Helvetica",16),corner_radius=10)

gender=ctk.CTkLabel(FirstFrame,text="Gender:",font=("Helvetica",20))
gender_strvar = customtkinter.StringVar(value="Gender")  # set initial value
def optionmenu_callback(choice):
    print("optionmenu dropdown clicked:", choice)

genOption = ctk.CTkOptionMenu(FirstFrame,values=["Male", "Female"], command=optionmenu_callback,
            variable=gender_strvar,dropdown_font=("Helvetica",16),font=("Helvetica",16),corner_radius=20)

dob=ctk.CTkLabel(FirstFrame,text="Date of Birth:",font=("Helvetica",20))
dobEntry=DateEntry(FirstFrame,font=("Helvetica",16),width=15)

stream=ctk.CTkLabel(FirstFrame,text="Stream:",font=("Helvetica",20))
stream_strvar = customtkinter.StringVar(value="Science/Comm")  # set initial value
def optionmenu_callback(choice):
    print("optionmenu dropdown clicked:", choice)

streamOption = ctk.CTkOptionMenu(FirstFrame,values=["Science", "Commerce"], command=optionmenu_callback,
            variable=stream_strvar,dropdown_font=("Helvetica",16),font=("Helvetica",16),corner_radius=20)


firstName.grid(row=0,column=0,padx=20,pady=35)
fnameEntry.grid(row=0,column=1,padx=10,pady=35)
lastName.grid(row=0,column=2,padx=20,pady=35)
lnameEntry.grid(row=0,column=3,padx=10,pady=35)
roll.grid(row=0,column=4,pady=35)
rollEntry.grid(row=0,column=5,padx=10,pady=35)
email.grid(row=0,column=6,padx=20,pady=35)
emailEntry.grid(row=0,column=7,padx=10,pady=35)

contactNo.grid(row=1,column=0,padx=20,pady=20)
contactEntry.grid(row=1,column=1,padx=10,pady=20)
gender.grid(row=1,column=2,padx=20,pady=20)
genOption.grid(row=1,column=3,padx=10,pady=20)
dob.grid(row=1,column=4,padx=20,pady=20)
dobEntry.grid(row=1,column=5,padx=10,pady=20)
stream.grid(row=1,column=6,padx=20,pady=20)
streamOption.grid(row=1,column=7,padx=40,pady=20)


SecondFrame = ctk.CTkFrame(new_window,width=1150,height=350,corner_radius=20)
SecondFrame.grid(row=2,padx=55,pady=5)

submit=ctk.CTkButton(SecondFrame,text="Submit Record", command=add_record,corner_radius=9,width=180,height=50,font=("Helvetica",20))
update=ctk.CTkButton(SecondFrame,text="Update Record", command=update_record ,corner_radius=9,width=180,height=50,font=("Helvetica",20))
delete=ctk.CTkButton(SecondFrame,text="Delete Record", command=remove_record ,corner_radius=9,width=180,height=50,font=("Helvetica",20))
view=ctk.CTkButton(SecondFrame,text="View Record", command=view_record, corner_radius=9,width=180,height=50,font=("Helvetica",20))
reset=ctk.CTkButton(SecondFrame,text="Reset Fields", command=reset_fields ,corner_radius=9,width=180,height=50,font=("Helvetica",20))
deldatabase=ctk.CTkButton(SecondFrame,text="Delete Database", command=reset_form ,corner_radius=9,width=180,height=50,font=("Helvetica",20))

submit.grid(row=2,column=0,padx=20,pady=20)
update.grid(row=2,column=1,padx=10,pady=20)
delete.grid(row=2,column=2,padx=20,pady=20)
view.grid(row=2,column=3,padx=10,pady=20)
reset.grid(row=2,column=4,padx=20,pady=20)
deldatabase.grid(row=2,column=5,padx=10,pady=20)


SearchFrame = ctk.CTkFrame(new_window,width=1150,height=40,corner_radius=20)
SearchFrame.grid(row=3,padx=55,pady=5)
search_entry = ctk.CTkEntry(SearchFrame, textvariable=search_var, font=("Helvetica", 20))
search_entry.pack(side=RIGHT, padx=10, pady=10)
search=ctk.CTkButton(SearchFrame, text="Search Record", font=("Helvetica", 20), text_color="White",command=search_record)
search.pack( padx=20, pady=8)

'''search_var = StringVar()
search_label = ctk.CTkLabel(search_window, text="Enter Roll Number to Search:", font=("Helvetica",16))
search_label.pack(padx=10, pady=10)
search_entry = ctk.CTkEntry(search_window, textvariable=search_var, font=("Helvetica",16))
search_entry.pack(padx=10, pady=10)
search_button = ctk.CTkButton(search_window, text="Search", font=("Helvetica",16), command=search_record)
search_button.pack(padx=10, pady=10)'''


ThirdFrame = ctk.CTkFrame(new_window,width=1150,height=40,corner_radius=20,fg_color="DarkGrey")
ThirdFrame.grid(row=4,padx=55,pady=5)
studentRec=ctk.CTkLabel(ThirdFrame,text="STUDENT RECORDS",font=("Helvetica",32),text_color="White")
studentRec.grid(row=4,column=0,padx=475,pady=10)





# Set a fixed size for bottom_frame
bottom_frame = tk.Frame(new_window, bg="GRAY", width=1400, height=400)
bottom_frame.grid(row=5,column=0)

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
tree.column('#5', width=100, stretch=NO,anchor=CENTER)
tree.column('#6', width=80, stretch=NO,anchor=CENTER)
tree.column('#7', width=150, stretch=NO,anchor=CENTER)
tree.column('#8', width=150, stretch=NO)
tree.column('#9', width=150, stretch=NO,anchor=CENTER)

# Use place to set an absolute size for the Treeview
tree.place(relwidth=40, relheight=20, width=1200, height=400)

display_records()
new_window.geometry("1200x700")
new_window.mainloop()