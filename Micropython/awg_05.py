# Arbitrary Wave Generator by jean-claude.feltes@education.lu
# https://github.com/jean-claudeF/ArbitraryWaveformGenerator
# DAC on Pins GP8...GP15
# Inspired by Rolf Oldeman, 13/2/2021. CC BY-NC-SA 4.0 licence
# This is a simplified  version with fixed number of samples
# Advantage: Practically no delay when changing frequency
# Disadvantage: smaller frequency range
# by putting more than 1 period into the buffer(could be extended however)
# Range OK for audio
# MODES:
# modes = ["sine", "saw", "triangle", "rect", "demo", "abssine", "awg","awg_new", "awg_last"]
# For the mode "awg" the Pico must have a file awgvalues.py that defines the curve in Python format
# like this:
# function = 'sin(2*pi*x) + cos(3*pi*x)'
# N = 4096
# values = [231, 231, 231, 231, 232, 232, 232, ...]
# There is a Python software for the PC to easily generate and transfer this
# For an explanation of the fundamental algorithm see here:
# https://staff.ltam.lu/feljc/electronics/uPython/PIO_DDS.pdf

from machine import Pin,mem32
from rp2 import PIO, StateMachine, asm_pio, DMA
from array import array
from math import pi,sin, exp, cos
from uctypes import addressof
import time
import sys

PIO0_TXF0       = 0x50200010
PIO0_SM0_CLKDIV = 0x502000c8

DMA0_Read  = 0x50000000; DMA1_Read  = 0x50000040
DMA0_Write = 0x50000004; DMA1_Write = 0x50000044
DMA0_Count = 0x50000008; DMA1_Count = 0x50000048
DMA0_Trig  = 0x5000000C; DMA1_Trig  = 0x5000004C
DMA0_Ctrl  = 0x50000010; DMA1_Ctrl  = 0x50000050

BASEPIN = 8
N=4096

buffer = bytearray(N)
FREQUENCY = 440           # global, used by stop()

# Get free memory
import gc
def get_free_memory():
    return gc.mem_free()
    
print(str(get_free_memory()) + " bytes free")

#------------------------------------------------------------------

# This is needed for switching off output at the end
# Set output to 0 or 127 for bipolar
# After using state machine outputs must be reinitialised
# as Pin.OUT and desired value

def out_zero(bipolar = 1):
    outs = []
    for i in range(BASEPIN, BASEPIN + 8):
        outs.append(Pin(i, Pin.OUT))

    for i in range(0,8):
        outs[i].value(0)
    if bipolar:
        outs[7].value(1)

#------------------------------------------------------------------
#define PIO.OUT_HIGH 3, PIO.SHIFT_RIGHT 1
@asm_pio(out_init=(PIO.OUT_LOW,)*8, out_shiftdir=PIO.SHIFT_RIGHT,
         autopull=True, pull_thresh=32)
def parallel():
    out(pins,8)

sm=StateMachine(0, parallel, freq= 100_000_000, out_base=Pin(BASEPIN))

#------------------------------------------------------------------

dma0 = DMA()
dma1 = DMA()

def DMA_Stop():
    dma1.ctrl = 0
    dma0.ctrl = 0
    
def DMA_Start(words):
    # dma0: From buffer to port (to state machine)
    # size = 2 -> 32 bit transfer   (1 -> B2 signal)
    control0 = dma0.pack_ctrl(inc_read=True,
                              inc_write=False,
                              size=2,
                              treq_sel=0,
                              enable = 1,
                              high_pri= 1,
                              chain_to = 1)
    dma0.config(read=buffer,
                write=PIO0_TXF0,
                count=words,
                ctrl=control0)

    # dma1: chain dma0 for next package of data
    control1 = dma1.pack_ctrl(inc_read=False,
                              inc_write=False,
                              size=2,
                              treq_sel=63,
                              high_pri= 1,
                              enable = 1,
                              chain_to = 0)
    dma1.config(read=addressof(array('i',[addressof(buffer)])),
                write=DMA0_Read,
                count=1,
                ctrl=control1,
                trigger = 1)

#------------------------------------------------------------------
def set_N(n):
    global N, buffer
    N = n
    buffer = bytearray(N)
    
def set_buffer(yvalues):
    global buffer
    n = len(yvalues)
    #if len(yvalues) != N:
    #    set_N(n)
    i = 0
    for y in yvalues:
        buffer[i] = y
        i+=1

# For awg() and awg_new(), data are imported in Python format.
# This is elegant, but leads to failure if the import is done more than once.
# To avoid this, the module awgvalues is deleted if it was already in memory.


def awg():
    global N, buffer
    try:
        del sys.modules['awgvalues']
    except:
        print("Importing awgvalues.py")
        
    import awgvalues as a
    set_N(a.N)
    values = a.values
    print(a.function)
        
    #buffer = bytearray(N)
    for i in range(0, N):
        buffer[i] = values[i]

    print(str(get_free_memory()) + " bytes free")
    
def awg_new():
    """
    global N, buffer
    try:
        del sys.modules['awgvalues']
    except:
        print("Importing awgvalues.py")
       
    
    import awgvalues as a
    set_N(a.N)
    values = a.values
        
    #buffer = bytearray(N)
    for i in range(0, N):
        buffer[i] = values[i]
        
    print(a.function)
    print(str(get_free_memory()) + " bytes free")
    """
    awg()

def awg_last():
    awg_new()
    
def sine():
    global buffer
    for i in range(N):
        buffer[i]=int(127+127*sin(2*pi*i/N))
        
def saw():
    global buffer
    for i in range(N):
        buffer[i] = int(255 * i/N) 	 

def triangle():
    global buffer
    for i in range(N):
        c=(i/N)
        if i<= N/2:
            buffer[i] = int(510 * c) 
        else:
            buffer[i] = 510 - int(510 * c)

def rect():
    global buffer
    for i in range(N):
        if i<= N/2:
            buffer[i] = 0 
        else:
            buffer[i] = 255

def abssine():
    global buffer
    for i in range(N):
        
        buffer[i]=int(abs(255*sin(2*pi*i/N)))

def demo():
    global buffer
    for i in range(N):
        #buffer[i]=int(127+127*sin(2*pi*i/N)*sin(8*pi*i/N))
        buffer[i]=int(127+127*sin(8*pi*i/N)*exp(-2*i/N))
#-----------------------------------------------------------------------    

def start(f):
    global sm, FREQUENCY
    FREQUENCY = f
    stop()    
    sm=StateMachine(0, parallel, freq= int(f*N), out_base=Pin(8))
    DMA_Start(int(N/4))
    sm.active(1)
    print("f = ", int(f*N)/N)

def stop():
    global sm
    DMA_Stop()
    if FREQUENCY < 40:
        time.sleep(0.1)      # for very low frequencies allow DMA transfer to terminate
    sm.active(0)
    time.sleep(0.1)
    out_zero(bipolar = True)

def gen_stop():
    stop()

def secure_start(f):
    #if True:
    if f <= 30500 and f >= 32:
        start(f)
    else:    
        start(440)
        print("Illegal value!")
        print("Range: 32Hz ... 30.5kHz")
        print("f set to 440Hz")

def ask_f():
    s = input("Frequency/Hz: (empty to stop): ")
    if not s:
        f = 0
        stop()
    else:
        f = float(s)
    return f

def ask_f_and_mode():
    modes = ["sine", "saw", "triangle", "rect", "demo", "abssine", "awg","awg_new", "awg_last"]
    f = FREQUENCY
    print("Input f/Hz or mode")
    print("Modes: ", modes)
    print("Empty to stop")
    s = input("f/Hz or mode: ")
    if not s:
        f = 0
        stop()
    elif s.isdigit():
        f = float(s)
    else:
        if s in modes:
            exec(s + "()")
    
    return f

#------------------------------------------------------------
    
def test():
    #demo()
    #sine()
    #saw()
    #triangle()
    #abssine()
    #rect()
    #read_bufferfile()
    print("N = ", N)
    print(buffer)
    sine()
    
    f = 440
    start(f)
    print(str(get_free_memory()) + " bytes free")

    while(True):
        f = ask_f()
        if not f:
            stop()
            break
        #secure_start(f)
        start(f) 
    stop()

def mainloop():
    sine()
    start(440)
    
    while(True):
        f = ask_f_and_mode()
        if not f:
            stop()
            break
        #secure_start(f)
        start(f) 
    stop()
    

def test_buffer():
    yvalues = []
    for i in range(N):
        yvalues.append(int(127+127*sin(6*pi*i/N)) )
    #print(y)
    set_buffer(yvalues)
    start(500)
    

if __name__ == "__main__":
    #set_N(4096)
    #set_N(512)
    #test2()
    #test_buffer()
    mainloop()
    
    

