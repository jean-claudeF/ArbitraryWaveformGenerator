import tkinter as tk
from tkinter import ttk
from numpy import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from buttonbar import Buttonbar

# Global constants
dpi = 100
figsize = (7, 6)
N = 4096  # Number of points for calculations


#-----------------------------------------------------------------------

# Utility functions for calculations
def calculate_y(x, n, function):
    y = empty(n, dtype=float)
    s = f"y[:] = {function}"
    exec(s)
    return y

def normalize(y):
    maxy = max(max(y), abs(min(y)))
    return y / maxy

def normalize_to_bytes(y):
    return ((y * 127) + 127).astype(int)

def calc_xy(n, function):
    x = linspace(0.0, 1.0, n)
    y = calculate_y(x, n, function)
    return x, y
"""
def calc_awg(N, function):
    x, y = calc_xy(N, function)
    y_normalized = normalize(y)
    y_bytes = normalize_to_bytes(y_normalized)
    values = y_bytes.tolist()
    return x, y_bytes
"""
    
def calc_awg(n, function):
    # returns py string s 
    # contains function = ..., N=... and y=[....] (byte values), 
    # and x, y values
    x, y = calc_xy(n, function)
    y1 = normalize(y)
    yb = normalize_to_bytes(y1)
    yv = array(yb, dtype = uint8)
    #yn = yn.toint()
    yv = yv.tolist()
    x = x.tolist()
    s = "function = '" + function + "'\n"
    s += "N = " + str(n) + "\nvalues = " + str(yv)

    return s, x, yv    


#-----------------------------------------------------------------------

class FormulaPlotter(tk.Toplevel):
    def __init__(self, master, on_plot_callback=None, n = 2048):
        super().__init__(master)
        self.title("Formula Plotter")
        self.master = master
        
        self.on_plot_callback = on_plot_callback
        self.function = "sin(2*pi*x) + cos(3*pi*x)"
        self.x = []
        self.y = []
        self.description = ""
        self.filename = "plotvalues.py"
        self.N = n
        
        # Layout
        self.frm_left = tk.Frame(self)
        self.frm_left.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        

        # Canvas for plotting
        self.canvas, self.figure, self.plot = self.prepare_canvas(figsize, dpi)
        
        # Formula entry
        self.lbl_formula = tk.Label(self.frm_left, text="Formula (Use x = t/T)")
        self.lbl_formula.pack()
        self.txt_formula = tk.Entry(self.frm_left, width=100)
        self.txt_formula.insert(0, self.function)
        self.txt_formula.pack(padx=10, pady=5)
        self.txt_formula.bind('<Return>', lambda event: self.plot_curve())
        
        self.plot_curve()
        

        # Button bar
        cmds = {
            "Plot formula": self.plot_curve,
            "Example1": self.example1,
            "Example2": self.example2,
            "OK":self.ok,
            "QUIT": self._quit,
        }
        
        self.buttonbar = Buttonbar(cmds, parent=self.frm_left, side=tk.LEFT)
        self.buttonbar.pack(side=tk.TOP, pady = 10)

        # Close behavior
        self.protocol("WM_DELETE_WINDOW", self._quit)

    def prepare_canvas(self, figsize, dpi):
        figure = Figure(figsize=figsize, dpi=dpi)
        plot = figure.add_subplot(111)
        canvas = FigureCanvasTkAgg(figure, master=self.frm_left)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        return canvas, figure, plot

    def example1(self):
        self.function = "sin(4*2*pi*x)*exp(-x)"
        self.set_formula(self.function)
        self.plot_curve()

    def example2(self):
        self.function = "sin(2*pi*x) + sin(6*pi*x)"
        self.set_formula(self.function)
        self.plot_curve()

    def plot_curve(self):
        # plots function defined by formula in text field
        # automatically scales to byte values
        self.function = self.txt_formula.get()
        ### s, x, y = calc_awg(N, self.function)
        s, x, y = calc_awg(self.N, self.function)
        self.x = x
        self.y = y
        self.description = s
        self.plot.clear()
        self.plot.plot(x, y)
        self.plot.set_xlabel("t/T")
        self.canvas.draw()
        
        
    """    
    def write_plotfile(self):
        # writes function, N, y values (list) to file
        # as Python file
        try:
            with open(self.filename, "w") as f:
                f.write(self.description)
            print(f"Values written to {self.filename}")
        except IOError:
            print("FILE ERROR!")
    """
    
    
    def ok(self):
        # calls callback function in main app
        # (callback only if callback function is defined)
        if self.on_plot_callback:
           ##self.write_plotfile() 
           self.on_plot_callback(self.x, self.y, self.function)    

    def set_formula(self, formula):
        # sets formula to text field
        self.txt_formula.delete(0, tk.END)
        self.txt_formula.insert(0, formula)

    def _quit(self):
        # closes window and maximizes calling app again
        self.destroy()
        self.master.deiconify()
#----------------------------------------------------------------------
def handle_plot_data( x, y, function):
   
    print("Received plot data from FormulaPlotter.")
    print(function)
    N = len(y)
    print ("N = ", N)
    print("x = ", x[:8], "...")
    print("y = ", y[:30], "...")
    
    

#-----------------------------------------------------------------------
# Main Application class
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Main Application")
        self.geometry("400x300")

        self.label = ttk.Label(self, text="Main Application Window")
        self.label.pack(pady=20)

        self.open_button = ttk.Button(self, text="Open Formula Plotter", 
            command=self.open_plotter)
        self.open_button.pack(pady=10)

    def open_plotter(self):
        self.withdraw()
        fp = FormulaPlotter(self, on_plot_callback=handle_plot_data, n = 4096)

    
# Run the application
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
