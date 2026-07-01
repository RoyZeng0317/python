# tkinter
import tkinter as tk

# Tk() is a create a window
window = tk.Tk()

# set the window title(font color is blue at the top)
window.title('NFU')

# set the window size, fomat: 'width x height', pay attention the center is English latter x not *
window.geometry('400x300')

# mainloop() let the window still open it, the window will be show a second then close at the not this line
window.mainloop()