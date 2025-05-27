import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
from passlib.hash import pbkdf2_sha256
from tkcalendar import DateEntry
from ttkthemes import ThemedTk
import threading


root = ThemedTk(theme="Elegance")

root.title('Logbook')

root.geometry("900x600")
root.minsize(700,500)


#SQL DATABASE
connection = sqlite3.connect('logbook.db')
cursor = connection.cursor()

def create_table():
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS entries(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        heading TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        date TEXT NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    connection.commit()

def create_users_table():
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')
    connection.commit()

create_users_table()
create_table()

current_user_id = None

def register_window():
    reg_win = tk.Toplevel()
    reg_win.title("Register")
    reg_win.geometry("350x300")
    reg_win.grab_set()
    
    def on_register_close():
        root.destroy()
        
    reg_win.protocol("WM_DELETE_WINDOW", on_register_close)
    
    tk.Label(reg_win, text="Choose Username").pack(pady=5)
    username_entry = tk.Entry(reg_win)
    username_entry.pack(pady=5)
    
    tk.Label(reg_win, text="Choose Password").pack(pady=5)
    password_entry = tk.Entry(reg_win, show="*")
    password_entry.pack(pady=5)
    
    tk.Label(reg_win, text="Confirm Password").pack(pady=5)
    confirm_entry = tk.Entry(reg_win, show="*")
    confirm_entry.pack(pady=5)
    
    def attempt_register():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        confirm = confirm_entry.get().strip()
        
        if not username or not password or not confirm:
            messagebox.showwarning("Input Error", "All fields are required.")
            return
        
        if password != confirm:
            messagebox.showerror("Mismatch", "Passwords do not match.")
            return
        
        hashed = pbkdf2_sha256.hash(password)
        
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
            connection.commit()
            messagebox.showinfo("Success", "Registration successful! Please log in.")
            reg_win.destroy()
            login_window()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")
    
    tk.Button(reg_win, text="Register", command=attempt_register).pack(pady=10)
    tk.Button(reg_win, text="Back to Login", command=lambda: [reg_win.destroy(), login_window()]).pack()



def login_window():
    login_win = tk.Toplevel()
    login_win.title("Login")
    login_win.geometry("350x250")
    login_win.grab_set()  # Make modal so user must interact here first
    
    def on_login_close():
        root.destroy()
    
    login_win.protocol("WM_DELETE_WINDOW", on_login_close)

    
    tk.Label(login_win, text="Username").pack(pady=5)
    username_entry = tk.Entry(login_win)
    username_entry.pack(pady=5)
    
    tk.Label(login_win, text="Password").pack(pady=5)
    password_entry = tk.Entry(login_win, show="*")
    password_entry.pack(pady=5)
    
    def attempt_login():
        
        global current_user_id
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter username and password")
            return
        
        cursor.execute("SELECT id,password FROM users WHERE username=?", (username,))
        row = cursor.fetchone()
        if row and pbkdf2_sha256.verify(password, row[1]):
            current_user_id = row[0]
            root.title(f'Logbook - {username}')
            messagebox.showinfo("Success", f"Welcome {username}!")
            login_win.destroy()
            root.deiconify()  # Show main window after login
            loadEntries()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    tk.Button(login_win, text="Login", command=attempt_login).pack(pady=10)
    
    tk.Button(login_win, text="Register", command=lambda: [login_win.destroy(), register_window()]).pack()
    
    root.withdraw()  # Hide main window until login succeeds




def loadEntries_thread():
    
    con = sqlite3.connect("logbook.db")
    cur = con.cursor()
    
    date = dateEntry.get_date().strftime("%d-%m-%Y")
    cur.execute("SELECT timestamp, heading FROM entries WHERE date = ? AND user_id = ? ORDER BY timestamp DESC",(date, current_user_id))
    rows = cur.fetchall()
    con.close()
    
    
    def update_gui():
        previousEntry.delete(*previousEntry.get_children())
        for row in rows:
            previousEntry.insert("", "end", values=row)
    
    root.after(0, update_gui)
    

def loadEntries():
    
    threading.Thread(target = loadEntries_thread, daemon= True).start()



    
def search():
    text = textEntry.get()
    if not text:
        messagebox.showwarning("Empty Search", "Please enter a search term.")
        return
    
    date = dateEntry.get_date().strftime("%d-%m-%Y")
    cursor.execute("""SELECT timestamp, heading FROM entries WHERE date=? AND user_id=? AND (heading LIKE ? OR content LIKE ?) ORDER BY timestamp DESC""",
               (date, current_user_id, f"%{text}%", f"%{text}%"))
    rows = cursor.fetchall()
    
    previousEntry.delete(*previousEntry.get_children())
    for row in rows:
        previousEntry.insert("", "end", values=row)
    
    
def on2click(event):
    item_id = previousEntry.focus()
    
    if not item_id:
        return
    
    item = previousEntry.item(item_id)
    time, content_summary = item['values']
    
    details = tk.Toplevel(root)
    details.title(f"Log details - {time}")
    details.geometry("600x400")
    
    date = dateEntry.get_date().strftime("%d-%m-%Y")
    
    cursor.execute("SELECT heading, content FROM entries WHERE timestamp=? AND date= ? AND user_id= ?", (time, date,current_user_id))
    
    result = cursor.fetchone()
    
    if result:
        heading, content =result
        tk.Label(details, text=f"Time: {time}", font=('Arial', 12)).pack(pady=5)
        tk.Label(details, text=f"Heading: {heading}", font=('Arial', 14, 'bold')).pack(pady=10)
        tk.Label(details, text="Details:").pack()
        tk.Message(details, text=content, width=500).pack()
    else:
        messagebox.showerror("Not found", "Log entry could not be found.")
    
#opens a new window where the user can enter their log details
def entry():
    
    debrief = tk.Toplevel()
    debrief.title("Logs")
    debrief.geometry("600x400")
    
    head = tk.Label(debrief, text = "Log Heading")
    head.grid(row=0, column=0)
    
    entry = tk.Entry(debrief)
    entry.grid(row=1, column=0, columnspan= 3)
    
    body = tk.Label(debrief, text = "Log details")
    body.grid(row=2, column=0)
    
    details = tk.Text(debrief, height=10, width=50)
    details.grid(row=3, column=0, columnspan=3, sticky='nsew')
    
    debrief.grid_columnconfigure(0, weight=1)
    debrief.grid_columnconfigure(1, weight=1)
    debrief.grid_columnconfigure(2, weight=1)
    
    #Saves the entered details
    def saved_thread(logHead, logDetails):
        
        timestamp = datetime.now().strftime("%H:%M")
        logDate = datetime.now().strftime("%d-%m-%Y")
        
        con = sqlite3.connect("logbook.db")
        cur = con.cursor()
    
        
        cur.execute("INSERT INTO entries (user_id, heading, content, timestamp, date) VALUES (?, ?, ?, ?, ?)", (current_user_id, logHead, logDetails, timestamp, logDate))
        con.commit()
        con.close()
        
        def after_save():
            messagebox.showinfo("Saved", "Log Entry saved successfully", parent = debrief)
            debrief.destroy()
            loadEntries()

        root.after(0, after_save)    

    def saved():
        
        logHead = entry.get()
        logDetails = details.get("1.0", tk.END).strip()
        
        if not logDetails or not logHead:
            messagebox.showwarning("Incomplete!!", "Please enter both the heading and the details")
            return
        
        threading.Thread(target = saved_thread, args=(logHead, logDetails), daemon= True).start()
    
    save = tk.Button(debrief, text= "Save", command= saved)
    save.grid(row=4, column=0)
    
    
    
    
#GUI

f1 = tk.Frame(root)
f1.grid(row= 0, column= 0, columnspan= 2, sticky='ew', padx=10, pady=10)
root.grid_columnconfigure(0, weight=1)

dateEntry = DateEntry(f1, width=12, background = "darkblue", foreground = "white", borderwidth=2, year = datetime.now().year)
dateEntry.grid(row=0, column=0, sticky='w')
dateEntry.bind("<<DateEntrySelected>>", lambda e: loadEntries())


searchBtn = tk.Button(f1, text="Search", command= search)
searchBtn.grid(row=0, column=3, sticky='e')

textEntry = tk.Entry(f1)
textEntry.grid(row =0, column=1, columnspan=2, sticky='ew', padx=5)
f1.grid_columnconfigure(1, weight=1)

f2 = tk.Frame(root)
f2.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0,10))
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

columns = ('time', 'content')
previousEntry = ttk.Treeview(f2, columns= columns, show='headings', height= 15)

previousEntry.heading('time', text='Time')
previousEntry.heading('content', text='Content')

previousEntry.column('time', width=100, anchor='center')
previousEntry.column('content', width=600)

scroll = ttk.Scrollbar(f2, orient="vertical", command=previousEntry.yview)
previousEntry.configure(yscrollcommand= scroll.set)
scroll.pack(side='right', fill='y')

previousEntry.pack(side='left', fill='both',expand=True)

previousEntry.bind("<Double-1>", on2click)


f3 = tk.Frame(root)
f3.grid(row=2, column=0, sticky='e', padx=10, pady=5)

addEntry = tk.Button(f3, text = 'Add Entry', command= entry)
addEntry.pack()


def on_closing():
    connection.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)


if __name__ == '__main__':
    login_window()
    root.mainloop()