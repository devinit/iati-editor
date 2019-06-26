import sys
from utils import csv_to_xml
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
        self.input = None
        self.output = None
        Label(root, text="Input directory").grid(row=1, column=0, sticky=W)
        Label(root, text="Output XML (optional)").grid(row=2, column=0, sticky=W)
        self.bari = Entry(master, state='disabled')
        self.bari.grid(row=1, column=1, sticky=W + E)
        self.baro = Entry(master, state='disabled')
        self.baro.grid(row=2, column=1, sticky=W + E)

        # Buttons
        self.cbutton = Button(root, text="Generate XML", command=self.process)
        self.cbutton.grid(row=3, column=3, sticky=E)
        self.ibutton = Button(root, text="Browse", command=self.browseinput)
        self.ibutton.grid(row=1, column=3, sticky=E)
        self.obutton = Button(root, text="Browse", command=self.browseoutput)
        self.obutton.grid(row=2, column=3, sticky=E)

        self.text_box = Text(root, wrap='word', height=10, state='disabled')
        self.text_box.grid(column=0, row=4, padx=5, pady=5, columnspan=4, sticky=W + E + N + S)
        sys.stdout = StdoutRedirector(self.text_box)
        sys.stderr = StdoutRedirector(self.text_box)

    def browseinput(self):
        Tk().withdraw()
        self.input = filedialog.askdirectory()
        self.bari.configure(state='normal')
        self.bari.delete(0, END)
        self.bari.insert(0, self.input)
        self.bari.configure(state='disabled')

    def browseoutput(self):
        Tk().withdraw()
        self.output = filedialog.asksaveasfilename(filetypes=[('XML files', '.xml'), ('All files', '.*')])
        self.baro.configure(state='normal')
        self.baro.delete(0, END)
        self.baro.insert(0, self.output)
        self.baro.configure(state='disabled')

    def process(self):
        if self.input:
            csv_to_xml(self.input, self.output)
        else:
            print("Error: Please select one input directory.")


def on_closing():
    root.destroy()
    sys.exit(0)


root = Tk()
root.title("DevInit IATI CSV to XML tool")
root.protocol("WM_DELETE_WINDOW", on_closing)
window = Window(root)
root.mainloop()
