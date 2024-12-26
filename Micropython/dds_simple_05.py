# DDS modified
# DDS generator
# DAC on Pins GP8...GP15
# Inspired by Rolf Oldeman, 13/2/2021. CC BY-NC-SA 4.0 licence
# This is a simplified (very simple) version with fixed number of samples
# Advantage: Practically no delay when changing frequency
# Disadvantage: smaller frequency range (could be extended however)
# Range OK for audio

from machine import Pin,mem32
from rp2 import PIO, StateMachine, asm_pio, DMA
from array import array
from math import pi,sin, exp, cos
from uctypes import addressof
import time

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

#------------------------------------------------------------------

# Only needed for switching off output at the end
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

#------------------------------------------------------------
    
def test():
    #demo()
    sine()
    #saw()
    #triangle()
    #abssine()
    
    f = 440
    start(f)


    while(True):
        f = ask_f()
        if not f:
            stop()
            break
        #secure_start(f)
        start(f) 
    stop()

if __name__ == "__main__":
    test()

