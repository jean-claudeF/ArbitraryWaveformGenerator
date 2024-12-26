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
from math import pi,sin
from uctypes import addressof
import time

PIO0_TXF0       = 0x50200010
PIO0_SM0_CLKDIV = 0x502000c8

DMA0_Read  = 0x50000000; DMA1_Read  = 0x50000040
DMA0_Write = 0x50000004; DMA1_Write = 0x50000044
DMA0_Count = 0x50000008; DMA1_Count = 0x50000048
DMA0_Trig  = 0x5000000C; DMA1_Trig  = 0x5000004C
DMA0_Ctrl  = 0x50000010; DMA1_Ctrl  = 0x50000050


N=4096
buffer = bytearray(N)

#------------------------------------------------------------------
#define PIO.OUT_HIGH 3, PIO.SHIFT_RIGHT 1
@asm_pio(out_init=(PIO.OUT_HIGH,)*8, out_shiftdir=PIO.SHIFT_RIGHT,
         autopull=True, pull_thresh=32)
def parallel():
    out(pins,8)

sm=StateMachine(0, parallel, freq= 100_000_000, out_base=Pin(8))

#------------------------------------------------------------------

dma0 = DMA()
dma1 = DMA()

def DMA_Stop():
    dma0.ctrl = 0
    dma1.ctrl = 0
    
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
        
#-----------------------------------------------------------------------    

def start(f):
    global sm
    stop()    
    sm=StateMachine(0, parallel, freq= int(f*N), out_base=Pin(8))
    DMA_Start(int(N/4))
    sm.active(1)
    print("f = ", int(f*N)/N)
    
def stop():
    global sm
    DMA_Stop()
    sm.active(0)

#------------------------------------------------------------
    
def test():
    sine()
    #saw()
    #triangle()
    #abssine()
    start(440)
    time.sleep(100)
    stop()

if __name__ == "__main__":
    test()

