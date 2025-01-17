# Arbitrary Waveform Generator
Simple sine / triangle /rect / sawtooth / arbitrary (formula defined) generator with Raspi Pico ca. 1Hz ...30kHz

![Picture](awg_04.png)

This started as an educational project (me learning about PIO and DMA) and ended as a quite usable AWG generator that is computer controlled.
A document describing my efforts is found here:

https://staff.ltam.lu/feljc/electronics/uPython/PIO_DDS.pdf

There is a small PC software now to control the generator:

https://github.com/jean-claudeF/ArbitraryWaveformGenerator/blob/main/awg_v.mp4

Again I find the small Pico programmed in Micropython is a very useful piece of hardware.
It has some big advantages over Arduino, for example:
- one controller can have more programs on it that can easily be exchanged or edited
- functions can be called from the exterior, via UART terminal or via Picoconnect

## Micropython

MODES:
modes = ["sine", "saw", "triangle", "rect", "demo", "abssine", "awg","awg_new", "awg_last"]

For the mode "awg" the Pico must have a file awgvalues.py that defines the curve in Python format
like this:

``` python
function = 'sin(2*pi*x) + cos(3*pi*x)'
N = 4096
values = [231, 231, 231, 231, 232, 232, 232, ...]
```

There is a Python software for the PC to easily generate and transfer this.

For an explanation of the fundamental algorithm see here:

https://staff.ltam.lu/feljc/electronics/uPython/PIO_DDS.pdf


### Some explanations to the code

#### Modes sine, saw, triangle, rect

The waveform is calculated and the buffer filled with the calculated values.

N is the number of samples


#### awg modes

- the modes awg, awg_new and awg_last essentially do the same, the different names are for compatibility with the PC software only


- For awg() and awg_new(), data are imported in Python format.
This is elegant, but leads to failure if the import is done more than once.
To avoid this, the module awgvalues is deleted if it was already in memory.

``` python
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
   
    for i in range(0, N):
        buffer[i] = values[i]
```        

#### Setting modes and frequency via terminal

When awg_05.py is started, a loop that asks for frequency or mode is started.

Thus the generator can be simply controlled via serial terminal.

``` python
def mainloop():
    sine()
    start(440)
    
    while(True):
        f = ask_f_and_mode()
        if not f:
            stop()
            break
        start(f) 
    stop()
```

The function ask_f_and_mode is used to input frequency or mode, or stop on empty input:

``` python
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
```












