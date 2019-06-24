import sys
from utils import xml_differencer
from tkinter import Label, Entry, Button, Tk, filedialog, END, Text, W, E, N, S


class StdoutRedirector(object):
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.configure(state='normal')
        self.text_space.insert('end', string)
        self.text_space.see('end')
        self.text_space.configure(state='disabled')

    def flush(self):
        pass


class Window:
    def __init__(self, master):
        self.input1 = None
        self.input2 = None
        self.output = None
        Label(root, text="Past XML file").grid(row=1, column=0, sticky=W)
        Label(root, text="Current XML file").grid(row=2, column=0, sticky=W)
        Label(root, text="Output XML file").grid(row=3, column=0, sticky=W)
        self.bari1 = Entry(master, state='disabled')
        self.bari1.grid(row=1, column=1, sticky=W + E)
        self.bari2 = Entry(master, state='disabled')
        self.bari2.grid(row=2, column=1, sticky=W + E)
        self.baro = Entry(master, state='disabled')
        self.baro.grid(row=3, column=1, sticky=W + E)

        # Buttons
        self.cbutton = Button(root, text="Generate difference", command=self.process)
        self.cbutton.grid(row=4, column=3, sticky=E)
        self.i1button = Button(root, text="Browse", command=self.browseinput1)
        self.i1button.grid(row=1, column=3, sticky=E)
        self.i2button = Button(root, text="Browse", command=self.browseinput2)
        self.i2button.grid(row=2, column=3, sticky=E)
        self.obutton = Button(root, text="Browse", command=self.browseoutput)
        self.obutton.grid(row=3, column=3, sticky=E)

        self.text_box = Text(root, wrap='word', height=10, state='disabled')
        self.text_box.grid(column=0, row=5, padx=5, pady=5, columnspan=4, sticky=W + E + N + S)
        sys.stdout = StdoutRedirector(self.text_box)
        sys.stderr = StdoutRedirector(self.text_box)

    def browseinput1(self):
        Tk().withdraw()
        self.input1 = filedialog.askopenfilename(filetypes=[('XML files', '.xml'), ('All files', '.*')])
        self.bari1.configure(state='normal')
        self.bari1.delete(0, END)
        self.bari1.insert(0, self.input1)
        self.bari1.configure(state='disabled')

    def browseinput2(self):
        Tk().withdraw()
        self.input2 = filedialog.askopenfilename(filetypes=[('XML files', '.xml'), ('All files', '.*')])
        self.bari2.configure(state='normal')
        self.bari2.delete(0, END)
        self.bari2.insert(0, self.input2)
        self.bari2.configure(state='disabled')

    def browseoutput(self):
        Tk().withdraw()
        self.output = filedialog.asksaveasfilename(filetypes=[('XML files', '.xml'), ('All files', '.*')])
        self.baro.configure(state='normal')
        self.baro.delete(0, END)
        self.baro.insert(0, self.output)
        self.baro.configure(state='disabled')

    def process(self):
        if self.input1 and self.input2 and self.output:
            xml_differencer(self.input1, self.input2, self.output)
        else:
            print("Error: Please select one past XML file, one current XML file, and an output filename.")


def on_closing():
    root.destroy()
    sys.exit(0)


root = Tk()
root.title("DevInit IATI XML Differencer")
root.protocol("WM_DELETE_WINDOW", on_closing)
window = Window(root)
root.mainloop()
