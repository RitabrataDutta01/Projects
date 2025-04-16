import tkinter as tk
import threading
import sqlite3
from tkinter import ttk


connection = sqlite3.connect("to-do-list.db")
cursor = connection.cursor()

def createTable():
    cursor.execute("DROP TABLE IF EXISTS todo")  # Drops the existing table if it exists
    cursor.execute('''CREATE TABLE todo(
                    Sl_No INTEGER PRIMARY KEY AUTOINCREMENT,
                    ITEM TEXT,
                    STATUS TEXT DEFAULT 'incomplete')''')  # Create with STATUS column
    connection.commit()


createTable()

def on_Enter(event=None):
    userInput = entryBar.get()
    add_item(userInput)
    entryBar.delete(0, tk.END)
    showData()

def add_item(userInput):

    cursor.execute('INSERT INTO todo (ITEM, STATUS) VALUES (?,?)', (userInput,'incomplete'))
    connection.commit()

def fetch_data():
    cursor.execute('SELECT * FROM todo')
    data = cursor.fetchall()
    return data

def toggleStatus(event):
    selected = outputTable.focus()

    if not selected:
        return

    values = outputTable.item(selected, 'values')
    sl_no = values[0]
    currentStatus = values[2]
    newStatus = 'complete' if currentStatus == 'Incomplete' else 'Incomplete'

    cursor.execute('UPDATE todo SET STATUS=? WHERE Sl_No=?', (newStatus, sl_no))

    connection.commit()
    showData()

def showData():

    data = fetch_data()

    for row in outputTable.get_children():
        outputTable.delete(row)

    for i, row in enumerate(data):
        if i % 2 == 0:
            outputTable.insert("", tk.END, values=row, tags="even")
        else:
            outputTable.insert("", tk.END, values=row, tags="odd")

    outputTable.tag_configure("even", background="#f9f9f9")
    outputTable.tag_configure("odd", background="#e9e9e9")


root = tk.Tk()
root.geometry("500x500")
root.title("To-Do List")

#GUI elements

inputFrame = tk.Frame(root)
inputFrame.grid(row=1, column=0, sticky='nsew')
inputFrame.rowconfigure(1, weight=1)

entryLabel = tk.Label(inputFrame, text="Enter task:")
entryLabel.grid(row=1, column=0)

entryBar = tk.Entry(inputFrame)
entryBar.grid(row=1, column=1)
entryBar.bind("<Return>", on_Enter)

outputFrame = tk.Frame(root)
outputFrame.grid(row=2, column=0)

outputTable = ttk.Treeview(outputFrame, columns=("Sl_No", "Item", "Status"), show="headings")
outputTable.heading("Sl_No", text="Sl No.")
outputTable.heading("Item", text="Task")
outputTable.heading("Status", text="Status")

outputTable.column("Sl_No", width=100, anchor=tk.CENTER)
outputTable.column("Item", width=100, anchor=tk.CENTER)
outputTable.column("Status", width=100, anchor=tk.CENTER)

outputTable.grid(row=2, column=0, sticky='nsew')

outputTable.bind("<Double-1>", toggleStatus)

header = tk.Label(root, text="Expense Tracker", font=("Arial", 24, "bold"))
header.grid(row=0, column=0, pady=10)

tableScroll = ttk.Scrollbar(outputFrame, orient='vertical', command=outputTable.yview)
tableScroll.grid(row=2, column=1, sticky='ns')

if __name__ == '__main__':
    root.mainloop()