
# copied partly from tk_connect_06.py

import time
import tkinter as tk

from buttonbar import Buttonbar
from listbox_dialog import MyListbox

#---------------------------------------------------------------------- 
# GLOBAL VARIABLES:

baud = 115200
FREQUENCY = 440
MODE = "sine()"
OLDMODE = MODE


#---------------------------------------------------------------------- 

from picoconnect_pa01 import create_pico_dictionary, Pico, CMD_TEST

keyword = "SWISS"

create_pico_dictionary()
mypico = Pico(keyword)
mypico.connect()
mypico.execute("from awg_01 import *")
mypico.execute("stop()")
mypico.execute("sine()")
#mypico.execute("start(440)")

def disconnect():
    mypico.close()
    
   
#---------------------------------------------------- 


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
            
#--------------------------------------------------------------

if __name__ == "__main__":  
    
    cmds = {'SINE': sine,
            'RECT': rectangle,
            'SAWTOOTH': sawtooth,
            'TRIANGLE': triangle,
            'ABS SINÊ': abssine,
            'AWG DEMO': awg_demo,
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
    
    
    lbl_f = tk.Label(frm_left, text = "Frequency/Hz:\n(1...30_000)")
    lbl_f.pack() 
    txt_f = tk.Entry(master = frm_left)
    txt_f.insert(0, "440")
    txt_f.config(width = 10)
    txt_f.pack()
    txt_f.bind('<Return>', (lambda event: get_f()))
    l = tk.Label(frm_left, text = "")
    l.pack()
   
    root.mainloop()
    
