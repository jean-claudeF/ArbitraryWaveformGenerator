

import time
import tkinter as tk

from buttonbar import Buttonbar
#from listbox_dialog import MyListbox

from formula_plotter_05 import FormulaPlotter
from picoconnect_pa03 import create_pico_dictionary, Pico, CMD_TEST


from music_02 import *
from functools import partial
from radiobar import Radiobar

#---------------------------------------------------------------------- 
# GLOBAL VARIABLES:

baud = 115200
FREQUENCY = 440
MODE = "sine()"
OLDMODE = MODE
NSAMPLES = 2048
AWGFILE = "awgvalues.py"

#---------------------------------------------------------------------- 

# keyword is the keyword set in the info.txt file on the Pico
keyword = "SWISS"

create_pico_dictionary()
mypico = Pico(keyword)
mypico.connect()
mypico.execute("from awg_05 import *")
mypico.execute("stop()")
mypico.execute("sine()")
#mypico.execute("start(440)")

def disconnect():
    mypico.close()
    

# --------------------------------------
def set_mode(mode):
    global MODE, OLDMODE
    MODE = mode
    get_f()
    if MODE != OLDMODE:
        mypico.execute("stop()")
        mypico.execute(mode)
        OLDMODE = MODE
    mypico.execute("start(" + str(FREQUENCY) + ")" ) 

def sine():
    set_mode("sine()")
    
def rectangle():
    set_mode("rect()")
    
def sawtooth():
    set_mode("saw()")

def triangle():
    set_mode("triangle()")
   
def abssine():
    set_mode("abssine()")
    
def awg_demo():
    set_mode("demo()")
    
def awg():
    set_mode("awg()")
       
    
def gen_stop():
    print("STOP")
    mypico.execute("gen_stop()")
        
def reset():
    mypico.soft_reset()
    mypico.execute("from awg_01 import *")
    
def get_f():
    global FREQUENCY
    FREQUENCY = float(txt_f.get()) 
    mypico.execute("start(" + str(FREQUENCY) + ")" )      

def get_N():
    global NSAMPLES, MODE
    NSAMPLES = int(txt_n.get())
    set_N()
    
def set_N():     
    mypico.execute("set_N(" + str(NSAMPLES) + ")" ) 
    get_f()
    mypico.execute("stop()")
    mypico.execute(MODE)
    mypico.execute("start(" + str(FREQUENCY) + ")" )    
    
def send_cmd():
    cmd = txt_c.get()
    mypico.execute(cmd)

#----------------------------------------------------------------

def awg_last():
    set_mode("awg()")     # without transferring data


def awg_new():
    # switch over to formula plotter window
    # after this is closed, handle_pot_data() is called
    root.withdraw()
    fp = FormulaPlotter(root, on_plot_callback=handle_plot_data)
    
    
def handle_plot_data( x, y, function):
   
    print("Received plot data from FormulaPlotter.")
    print(function)
    N = len(y)
    print ("N = ", N)
    print("y = ", y[:30], "...")
    
    s = "function = '" + function + "'"
    s += "\nN = " + str(N)
    s += "\nvalues = " + str(y) + '\n'
    
    
    print("awgfile: " + AWGFILE +":")
    print(s[:200] + "...")    
    mypico.write_big_file(AWGFILE, s,1000)
    set_N()
    set_mode("awg_new()")
    
    

def read_awg():
    s = mypico.read_file(AWGFILE)
    print('\n\n')
    print(AWGFILE)
    print(s[:200])
       
    
#-------------------------------------------------------------
# Musical intervals
    
def handle_interval(semitones):
    print(semitones, " semitones")
    k = semitones_to_factor(semitones, temperated = True)
    #kn = semitones_to_factor(semitones, temperated = False)
    print("Temperated:  k = ", k)
    #print("Natural: k = ", kn)
    ### TODO button to choose
    
    upd = updown.getstate()
    print(upd)
    if upd == "UP":
        new_f = float(txt_f.get()) * k
    else:
        new_f = float(txt_f.get()) / k   
        
    txt_f.delete(0, tk.END)
    txt_f.insert(0, str(new_f))
    get_f()
    

def set_440():
    txt_f.delete(0, tk.END)
    txt_f.insert(0, "440")
    get_f()    

def set_1000():
    txt_f.delete(0, tk.END)
    txt_f.insert(0, "1000")
    get_f()   
             
#--------------------------------------------------------------

if __name__ == "__main__":  
    
    
    
    cmds = {'SINE': sine,
            'RECT': rectangle,
            'SAWTOOTH': sawtooth,
            'TRIANGLE': triangle,
            'ABS SINE': abssine,
            'AWG DEMO': awg_demo,
            'AWG LAST': awg,
            'AWG NEW': awg_new,
            'Read_AWG': read_awg,
            'STOP':gen_stop,
            #'RESET': reset,
            
    }     
    
   
    root = tk.Tk()
    root.title("AWG")
    comport = None
    
    # LEFT SIDE
    frm_left = tk.Frame()
    frm_left.pack(side = tk.LEFT, expand = tk.YES, fill = tk.BOTH)
    
    b2=Buttonbar(cmds, parent = frm_left, side=tk.TOP)
    b2.config(relief=tk.RIDGE, bd=3)
    b2.pack(side = tk.TOP)
    
    # Parameters
    frm_right = tk.Frame()
    frm_right.pack(side = tk.LEFT, expand = tk.YES, fill = tk.BOTH)
    
    lbl_f = tk.Label(frm_right, text = "Frequency/Hz:\n(1...30_000)")
    lbl_f.pack() 
    txt_f = tk.Entry(master = frm_right)
    txt_f.insert(0, "440")
    txt_f.config(width = 10)
    txt_f.pack()
    txt_f.bind('<Return>', (lambda event: get_f()))
    
    b = tk.Button(frm_right, text="440Hz", command = set_440)
    b.pack(pady = 10)
    
    b = tk.Button(frm_right, text="1kHz", command = set_1000)
    b.pack(pady = 10)
    
    
    lbl_n = tk.Label(frm_right, text = "Number of samples:\n(64...4096)\n(dividable by 4)")
    lbl_n.pack() 
    txt_n = tk.Entry(master = frm_right)
    txt_n.insert(0, "4096")
    txt_n.config(width = 10)
    txt_n.pack()
    txt_n.bind('<Return>', (lambda event: get_N()))
    
    lbl_c = tk.Label(frm_right, text = "Send command:")
    lbl_c.pack() 
    txt_c = tk.Entry(master = frm_right)
    txt_c.insert(0, "")
    txt_c.config(width = 10)
    txt_c.pack()
    txt_c.bind('<Return>', (lambda event: send_cmd()))
    
       
    # Intervals
    frm_interval = tk.Frame(root)
    frm_interval.pack(side = tk.LEFT, expand = tk.YES, fill = tk.BOTH)
        
    for label, value in nb_semitones.items():
        btn = tk.Button(frm_interval, text=label, command=partial(handle_interval, value))
        btn.pack(side=tk.TOP, padx=5, fill = tk.X)
    
    txts = ["UP", "DOWN"]
    updown = Radiobar(frm_interval, txts, side=tk.LEFT, selected=0)
    updown.config(relief=tk.RIDGE, bd=3)
    updown.pack(side = tk.TOP, pady = 5)
    
   
    root.mainloop()
    
