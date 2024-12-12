import threading 
import pickle
import select
from tkinter import *
from tkinter import font 
import tkinter.messagebox as msgb
from tkinter import ttk
from chat_utils import * 
import os
import json

# Initialization for Pickle File 
pickle_file_path = "ChatSystem/simple_gui/all_users.pickle"

# Make sure the pickle file exists
os.makedirs(os.path.dirname(pickle_file_path), exist_ok=True)

if not os.path.exists(pickle_file_path) or os.path.getsize(pickle_file_path) == 0: 
    with open(pickle_file_path, "wb") as f:
        pickle.dump({}, f)
        print("Initialized all_users.pickle with an empty dictionary.")
else:
    print("all_users.pickle already exists.")

class GUI:
    # constructor method
    def __init__(self, send=None, recv=None, sm=None, s=None):
        self.Window = Tk()
        self.Window.withdraw()
        self.send = send
        self.recv = recv
        self.sm = sm
        self.socket = s
        self.my_msg = ""
        self.system_msg = ""
        self.game_started = False  # Flag to prevent multiple game windows

    def login(self):
        # login window
        self.login = Toplevel()
        self.login.title("Login")
        self.login.resizable(width=False, 
                             height=False)
        self.login.configure(width=800,
                             height=600,
                             bg="#ABB2B9")

        self.pls = Label(self.login, 
                         text="Welcome to Evans Chatbox",
                         justify=CENTER, 
                         font="Helvetica 30 bold")
        self.pls.place(relheight=0.15,
                       relx=0.27, 
                       rely=0.07)

        self.username = StringVar()
        self.label_username = Label(self.login,
                                    text="Name: ",
                                    font="Helvetica 12 bold")
        self.label_username.place(relheight=0.15,
                                  relx=0.15, 
                                  rely=0.25)

        self.password = StringVar()
        self.label_password = Label(self.login,
                                    text="Password: ",
                                    font="Helvetica 12 bold",
                                    bg="#EAECEE") 
        self.label_password.place(relheight=0.15,
                                  relx=0.15,
                                  rely=0.38)

        self.entry_username = Entry(self.login, 
                                    font="Helvetica 14",
                                    textvariable=self.username)
        self.entry_username.place(relwidth=0.4, 
                                  relheight=0.1,
                                  relx=0.3,
                                  rely=0.28)

        self.entry_password = Entry(self.login, 
                                    font="Helvetica 14",
                                    textvariable=self.password)
        self.entry_password.place(relwidth=0.4, 
                                  relheight=0.1,
                                  relx=0.3,
                                  rely=0.48)

        self.entry_username.focus()

        self.login_button = Button(self.login,
                                   text="Log In", 
                                   font="Helvetica 14 bold", 
                                   command=self.log_in)
        self.login_button.place(relwidth=0.2,
                                relheight=0.1,
                                relx=0.25,
                                rely=0.7)

        self.sign_up_button = Button(self.login,
                                     text="Create Account",
                                     font="Helvetica 12",
                                     command=self.sign_up)
        self.sign_up_button.place(relwidth=0.2,
                                  relheight=0.1,
                                  relx=0.55,
                                  rely=0.7)

        self.Window.mainloop()

    def sign_up(self):
        def sign_up_action():
            new_user = self.new_username.get().strip()
            new_pass = self.new_password.get().strip()
            confirm_pass = self.confirm_password.get().strip()

            if not new_user or not new_pass:
                msgb.showerror(message="Username and Password cannot be empty")
                return

            try:
                with open("ChatSystem/simple_gui/all_users.pickle", "rb") as user_file:
                    all_users = pickle.load(user_file)
            except (FileNotFoundError, EOFError):      
                all_users = {}

            if new_user in all_users:
                msgb.showerror(message="Username already exists")
                return
            else:
                if new_pass == confirm_pass:
                    msgb.showinfo(message="Account Successfully Created, Start Chatting!")
                    all_users[new_user] = new_pass
                    with open("ChatSystem/simple_gui/all_users.pickle", "wb") as user_file:
                        pickle.dump(all_users, user_file)
                    self.window_sign_up.destroy()
                    self.goAhead(new_user)
                else:
                    msgb.showerror(message="Passwords do not match. Please try again")

        self.window_sign_up = Toplevel(self.login)
        self.window_sign_up.title("Sign Up")
        self.window_sign_up.configure(width=400,
                                      height=300,
                                      bg="#17202A")

        self.new_username = StringVar()
        self.label_new_username = Label(self.window_sign_up,
                                        text="Username: ",
                                        font="Arial 12 bold",
                                        bg="#EAECEE")
        self.label_new_username.place(relheight=0.15,
                                      relx=0.075,
                                      rely=0.08)
        self.entry_username = Entry(self.window_sign_up,
                                    font="Arial 12",
                                    textvariable=self.new_username)
        self.entry_username.place(relwidth=0.4,
                                  relheight=0.1,
                                  relx=0.52,
                                  rely=0.1)

        self.new_password = StringVar()
        self.label_new_password = Label(self.window_sign_up,
                                        text="Password: ",
                                        font="Arial 12 bold",
                                        bg="#EAECEE")
        self.label_new_password.place(relheight=0.15,
                                      relx=0.075,
                                      rely=0.23)

        self.entry_new_password = Entry(self.window_sign_up,
                                        font="Arial 12",
                                        show="*",
                                        textvariable=self.new_password)
        self.entry_new_password.place(relwidth=0.4,
                                      relheight=0.1,
                                      relx=0.52,
                                      rely=0.25)

        self.confirm_password = StringVar()
        self.label_confirm_password = Label(self.window_sign_up,
                                            text="Confirm Password: ",
                                            font="Arial 12 bold",
                                            bg="#EAECEE")
        self.label_confirm_password.place(relheight=0.15,
                                          relx=0.07,
                                          rely=0.38)

        self.entry_password = Entry(self.window_sign_up,
                                    font="Arial 12",
                                    show="*",
                                    textvariable=self.confirm_password)
        self.entry_password.place(relwidth=0.4,
                                  relheight=0.1,
                                  relx=0.52,
                                  rely=0.4)

        self.sign_up_button = Button(self.window_sign_up,
                                     text="Sign Up",
                                     font="Arial 12 bold",
                                     command=sign_up_action)
        self.sign_up_button.place(relx=0.4,
                                  rely=0.65)
        self.window_sign_up.bind('<Return>', lambda event: sign_up_action())

    def log_in(self):
        self.log_in_username = self.username.get().strip()
        self.log_in_password = self.password.get().strip()

        file_path = "ChatSystem/simple_gui/all_users.pickle"
        try:
            with open(file_path, "rb") as user_file:
                self.all_users = pickle.load(user_file)
        except (FileNotFoundError, EOFError):
            msgb.showerror(message="No users found, please create an account")
            return

        if self.log_in_username in self.all_users:
            if self.log_in_password == self.all_users[self.log_in_username]:
                msgb.showinfo(message="Welcome Back, " + self.log_in_username)
                self.goAhead(self.log_in_username)
            else:
                msgb.showerror(message="Incorrect Password, Try Again!")
        else:
            msgb.showerror(message="Username not found, Try Again!")

    def goAhead(self, name):
        if len(name) > 0:
            msg = json.dumps({"action": "login", "name": name})
            self.send(msg)
            response = json.loads(self.recv())
            if response["status"] == 'ok':
                self.login.destroy()
                self.sm.set_state(S_LOGGEDIN)
                self.sm.set_myname(name)
                self.layout(name)
                self.textCons.config(state=NORMAL)
                self.textCons.insert(END, menu + "\n\n")
                self.textCons.config(state=DISABLED)
                self.textCons.see(END)

                # Start the thread to process incoming/outgoing messages
                process = threading.Thread(target=self.proc)
                process.daemon = True
                process.start()

    def layout(self, name):
        self.name = name
        self.Window.deiconify()
        self.Window.title("CHATROOM")
        self.Window.resizable(width=False, height=False)
        self.Window.configure(width=940, height=800, bg="#17202A")

        self.labelHead = Label(self.Window,
                               bg="#17202A",
                               fg="#EAECEE",
                               text="Logged into: " + self.name,
                               font="Helvetica 13 bold",
                               pady=10)
        self.labelHead.place(relwidth=1)

        self.line = Label(self.Window,
                          width=450,
                          bg="#ABB2B9")
        self.line.place(relwidth=1,
                        rely=0.07,
                        relheight=0.012)

        self.textCons = Text(self.Window,
                             width=20,
                             height=2,
                             bg="#17202A",
                             fg="#EAECEE",
                             font="Helvetica 14",
                             padx=5,
                             pady=5)
        self.textCons.place(relheight=0.745,
                            relwidth=1,
                            rely=0.08)

        self.labelBottom = Label(self.Window, bg="#ABB2B9", height=80)
        self.labelBottom.place(relwidth=1, rely=0.825)

        self.entryMsg = Entry(self.labelBottom,
                              bg="#2C3E50",
                              fg="#EAECEE",
                              font="Helvetica 13")
        self.entryMsg.place(relwidth=0.74,
                            relheight=0.06,
                            rely=0.008,
                            relx=0.011)
        self.entryMsg.focus()

        self.buttonMsg = Button(self.labelBottom,
                                text="Send",
                                font="Helvetica 10 bold",
                                width=20,
                                bg="#ABB2B9",
                                command=lambda: self.sendButton(self.entryMsg.get()))
        self.buttonMsg.place(relx=0.77,
                             rely=0.008,
                             relheight=0.06,
                             relwidth=0.22)

        self.buttonG = Button(self.labelBottom, 
                              text="Game",
                              font="Arial 10 bold",
                              width=20,
                              bg="#ABB2B9",
                              command=lambda: self.sendButton("game"))
        self.buttonG.place(relx=0.88,
                           rely=0.008,
                           relheight=0.06,
                           relwidth=0.11)

        self.buttonTime = Button(self.labelBottom,
                                 text="Time",
                                 font="Helvetica 10 bold",
                                 width=20,
                                 bg="#ABB2B9",
                                 command=lambda: self.sendButton("time"))
        self.buttonTime.place(relx=0.77, rely=0.075, relheight=0.06, relwidth=0.22)

        self.textCons.config(cursor="arrow")

        scrollbar = Scrollbar(self.textCons)
        scrollbar.place(relheight=1, relx=0.974)
        scrollbar.config(command=self.textCons.yview)

        self.textCons.config(state=DISABLED)

    def sendButton(self, msg):
        self.textCons.config(state=DISABLED)
        self.my_msg = msg
        self.entryMsg.delete(0, END)

    def game_layout(self):
        if self.game_started:
            return  # Prevent multiple game windows
        self.game_started = True

        self.gameWindow = Toplevel(self.Window)
        self.gameWindow.title("Evan's Tic Tac Toe")
        self.gameWindow.protocol("WM_DELETE_WINDOW", self.on_game_close)

        Label(self.gameWindow, text="Player 1: X", font="times 15").grid(row=0, column=1)
        Label(self.gameWindow, text="Player 2: O", font="times 15").grid(row=0, column=2)
        self.buttons = []
        for i in range(3):
            for j in range(1, 4):
                btn = Button(self.gameWindow, width=15, height=7, font=('Times 16 bold'), 
                             command=lambda pos=i*3 + j-1: self.checker(pos))
                btn.grid(row=i+1, column=j)
                self.buttons.append(btn)

    def checker(self, position):
        # Send move to the server
        self.sm.send_move(position)

    def on_game_close(self):
        if self.gameWindow:
            self.gameWindow.destroy()
            self.game_started = False

    def proc(self):
        while True:
            try:
                read, write, error = select.select([self.socket], [], [], 0)
                peer_msg = ""
                if self.socket in read:
                    peer_msg = self.recv()

                if len(self.my_msg) > 0 or len(peer_msg) > 0:
                    self.system_msg = self.sm.proc(self.my_msg, peer_msg)
                    self.my_msg = ""  # Reset my_msg after processing

                    # Handle system messages
                    if "[Server]: Enjoy Evans Tic Tac Toe!" in self.system_msg and not self.game_started:
                        self.Window.after(0, self.game_layout)  # Schedule on main thread
                        self.textCons.config(state=NORMAL)
                        self.textCons.insert(END, self.system_msg + "\n\n")
                        self.textCons.config(state=DISABLED)
                        self.textCons.see(END)

                    elif self.system_msg.startswith("update_board:"):
                        _, board_str, current_player = self.system_msg.split(":")
                        board = board_str.split(",")
                        self.update_game_board(board)
                        self.update_turn_indicator(current_player)

                    elif self.system_msg.startswith("game_result:"):
                        _, winner = self.system_msg.split(":")
                        if winner == "Draw":
                            msgb.showinfo(title="Result", message="It's a draw!")
                        else:
                            msgb.showinfo(title="Result", message=f"{winner} wins!")
                        if self.gameWindow:
                            self.gameWindow.destroy()
                            self.game_started = False

                    else:
                        # Normal message
                        if self.system_msg.strip():
                            self.textCons.config(state=NORMAL)
                            self.textCons.insert(END, self.system_msg + '\n\n')
                            self.textCons.config(state=DISABLED)
                            self.textCons.see(END)
            except Exception as e:
                print(f"Error in proc thread: {e}")
                break

    def update_game_board(self, board):
        # Update the GUI buttons based on the board state
        for idx, mark in enumerate(board):
            if mark == "X":
                self.buttons[idx].config(text="X", state=DISABLED, bg="lightblue")
            elif mark == "O":
                self.buttons[idx].config(text="O", state=DISABLED, bg="lightgreen")
            else:
                self.buttons[idx].config(text="", state=NORMAL, bg="SystemButtonFace")

    def update_turn_indicator(self, current_player):
        # Corrected reference to self.sm.get_myname()
        if self.sm.get_myname() == current_player:
            self.labelHead.config(text=f"Logged into: {self.name} (Your turn)")
        else:
            self.labelHead.config(text=f"Logged into: {self.name} (Opponent's turn)")

    def run(self):
        self.login()
