import time
from tkinter import *
from tkinter import messagebox
import threading

class Timer():
    def __init__(self, parent):
        self.parent = parent
        
        # Timer 1
        self.hour = StringVar()
        self.minute = StringVar()
        self.second = StringVar()
        self.hour.set("00")
        self.minute.set("00")
        self.second.set("00")
        
        self.hourEntry = Entry(parent, width=3, font=("Arial", 18, ""), textvariable=self.hour)
        self.hourEntry.place(x=80, y=20)
        self.minuteEntry = Entry(parent, width=3, font=("Arial", 18, ""), textvariable=self.minute)
        self.minuteEntry.place(x=130, y=20)
        self.secondEntry = Entry(parent, width=3, font=("Arial", 18, ""), textvariable=self.second)
        self.secondEntry.place(x=180, y=20)
        self.start_button = Button(parent, text='Set Time Countdown',
                                    command=lambda: self.proc_start(self.hour, self.minute, self.second), bd='5')
        self.start_button.place(x=70, y=120)

        # Timer 2
        self.hour2 = StringVar()
        self.minute2 = StringVar()
        self.second2 = StringVar()
        self.hour2.set("00")
        self.minute2.set("00")
        self.second2.set("00")

        self.hourEntry2 = Entry(parent, width=3, font=("Arial", 18, ""), textvariable=self.hour2)
        self.hourEntry2.place(x=80, y=60)  # Adjusted y-coordinate for separation
        self.minuteEntry2 = Entry(parent, width=3, font=("Arial", 18, ""), textvariable=self.minute2)
        self.minuteEntry2.place(x=130, y=60)  # Adjusted y-coordinate for separation
        self.secondEntry2 = Entry(parent, width=3, font=("Arial", 18, ""), textvariable=self.second2)
        self.secondEntry2.place(x=180, y=60)  # Adjusted y-coordinate for separation
        self.start_button2 = Button(parent, text='Set Time Countdown',
                                     command=lambda: self.proc_start(self.hour2, self.minute2, self.second2), bd='5')
        self.start_button2.place(x=70, y=160)  # Adjusted y-coordinate for separation

    def start(self, hour, minute, second):
        try:
            # Get the total time in seconds
            temp = int(hour.get()) * 3600 + int(minute.get()) * 60 + int(second.get())
        except:
            print("Please input the right value")
            return

        while temp >= 0:
            # Calculate hours, minutes, and seconds
            mins, secs = divmod(temp, 60)
            hours = 0
            if mins > 60:
                hours, mins = divmod(mins, 60)

            # Update the respective timer variables
            hour.set("{0:02d}".format(hours))
            minute.set("{0:02d}".format(mins))
            second.set("{0:02d}".format(secs))

            # Update the GUI
            self.parent.update()
            time.sleep(1)

            # Check if time is up
            if temp == 0:
                messagebox.showinfo("Time Countdown", "Time's up")

            temp -= 1
    
    def proc_start(self, hour, minute, second):
        process = threading.Thread(target=lambda: self.start(hour, minute, second))
        process.daemon = True
        process.start()

# Run the app
root = Tk()
app = Timer(root)
root.geometry("300x200")
root.mainloop()