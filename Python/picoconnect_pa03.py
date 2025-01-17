'''Module for connecting to named Picos

by jean-claude.feltes@education.lu

The name (or keyword) must be the first line of a file info.txt on the Pico

# Usage:

from picoconnect_pa01 import create_pico_dictionary, Pico, CMD_TEST

create_pico_dictionary()

keyword = "SWISS"
mypico = Pico(keyword)
mypico.connect()
mypico.execute(CMD_TEST)
mypico.execute("x = 5; print (2* 3.14 * x)")
mypico.list_files()
mypico.write_file("test.txt", "HELLO\nTEST\n")
mypico.append_file("test.txt", "This is appended!")
mypico.read_file("test.txt")
mypico.close()

# First create a dictionary of Picos before calling other functions!
(If you don't, it is created automatically at first definition of Pico(keyword).
Why is it better to do this at the beginning? 
Because to read the info file the running program on the pico must be
stopped, and this can be a problem when using more than one Pico.
Don't bother, if you use create_pico_dictionary() at the beginning,
everything is fine

Example see main section
'''

import serial
import time
from serial.tools import list_ports

RESPONSE_TIMEOUT = 5        # This could be chosen greater 
                            # in case of problems

#-----------------------------------------------------------------------
# Do not edit this!

CMD_GETINFO ="""
try:
    f = open("info.txt", "r")
    t = f.readline()
    f.close()
except:
    t = ""
print("KEY=",t,"=ENDKEY")
"""

CMD_LISTFILES = """import os
files = os.listdir()
for f in files:
    print(f)
"""

CMD_TEST = """x = 56
y = 123
print("Hello from Pico")
print(x+y)
for i in range(0,10):
    print(i ** 2)
print("Good bye from Pico")   
"""

CMD_READFILE1 ="""
try:
    f = open('"""
CMD_READFILE2 = """', "r")
    t = f.read()
    f.close()
except:
    t = ""
print(t)
""" 


CMD_WRITEFILE1 ="""
try:
    f = open('"""
CMD_WRITEFILE2 = """', "w")
    f.write('''"""
CMD_WRITEFILE3 ="""''')
    f.close()
    print("OK")
except:
    print("FILE ERROR")
""" 

CMD_WRITEFILE2A = """', "a")
    f.write('''"""

PICO_DICTIONARY = {}

#-----------------------------------------------------------------------

# High level functions:

def create_pico_dictionary():
    # returns dictionary in the form {keyword1:port1, keyword2:port2....}  
    # This should be called only once at the beginning 
    # as it stops running programs to access the info file
    global PICO_DICTIONARY
    dict = {}
    for port in scan_for_picoports():
        info = get_info_pico(port)
        dict[info] = port
        PICO_DICTIONARY[info] = port
        
    return dict


def find_pico(keyword):
    '''returns name of the port where a Pico with the right keyword is connected'''
    # if dictionary is not yet created, create it now
    if PICO_DICTIONARY == {}:
        create_pico_dictionary()
    port = PICO_DICTIONARY[keyword]       
    return port


def scan_for_picoports(verbose = True):
    '''returns list of USB portnames with Raspi Picos connected '''
        
    picoports = []
    for port in list_ports.comports():
        if port.manufacturer != None:
            if "MicroPython" in port.manufacturer:
                picoports.append(port.device)
    if verbose:
        print("Pico found on port:")
        for p in picoports:
            print(p) 
        print()               
    return picoports

def scan_picoinfo():
    # returns list of tuples (port, info)
    # if dictionary is not yet created, create it now
    if PICO_DICTIONARY == {}:
        create_pico_dictionary()
    
    picoinfo = []
    for key in PICO_DICTIONARY.keys():
        info = key
        port = PICO_DICTIONARY[key] 
        picoinfo.append([port,info])
    """
    for port in scan_for_picoports():
        info = get_info_pico(port)
        print(port, ":   ", info)
        picoinfo.append([port,info])
    """    
    return picoinfo
    
#---------------------------------------------------------------------    
    
# port related    

def open_picoport(port):
    ser = serial.Serial(port, baudrate=115200)
    if ser.isOpen()==False:
        ser.open()
    flush_input_buffer(ser)
    return ser



def get_info_pico(port):
    # get info on Pico on port port
    ser = open_picoport(port)
    r = pico_get_info(ser)
    ser.close()
    return r

#----------------------------------------------------------------------

# Functions that operate on a Serial object already opened:

def flush_input_buffer(ser):
    n = ser.in_waiting
    ser.read(n) 


def rawREPL(ser):
    # Ctrl - A
    ser.write(b'\x01')     
    
def normalREPL(ser):
    # Ctrl - B
    ser.write(b'\x02') 
    
def interrupt_program(ser):
    # Ctrl - C
    ser.write(b'\x03\x03')
    time.sleep(0.1)
    
    
def soft_reset(ser):
    interrupt_program(ser)
    # Ctrl - D
    ser.write(b'\x04\x04')                          
   
    
def paste_mode(ser):
    # Ctrl - E
    ser.write(b'\x05')  
    
def end_paste_mode(ser):
    # Ctrl - D
    ser.write(b'\x04')        
    
def send_commands(ser,cmds):
    ser.write(cmds.encode("utf8"))
    ser.write(b'\x0D\x0A')

def debug_get_response(ser, timeout = 10):
    # for debugging purposes only, interrupt with Ctrl-C 
    t1 = time.time()
    while True:
        if ser.inWaiting():
            c = ser.read()
            try:
                cc = c.decode("utf-8")
            except:
                cc = "_DECODE ERROR_"    
            print(cc, end = "")
        if time.time() - t1 > timeout:
            print("TIMEOUT!")
            break    

def get_response(ser, timeout = RESPONSE_TIMEOUT):
    # get everything that is printed from the Pico (in paste mode)
    t1 = time.time()
    response = ""
    while True:
        
        # add to response
        if ser.inWaiting():
            c = ser.read()
            try:
                cc = c.decode("utf-8")
            except:
                cc = "_DECODE ERROR_"    
            
            response += cc
        
        # check for end of paste mode:
        if ">>>" in response[10:]:
            # at the end, not at the beginning: return to normal REPL,
            response= response[:-3]     # cut off ">>>"
            break
                
        # break if timeout
        if time.time() - t1 > timeout:
            print("TIMEOUT!")
            break    
    
    # cut off beginning 
    p1 = response.find("===")   # begin paste mode
    p2 = response.find("===", p1 + 1)
    response = response[p2+3+4:]
    return response

def pico_execute(ser, cmds, debug = False):
    # execute commands in paste mode and return response
    # response = everything that is printed from Pico
    flush_input_buffer(ser)
    paste_mode(ser)
    #time.sleep(0.1)
    send_commands(ser, cmds)
    end_paste_mode(ser)
    normalREPL(ser)
    time.sleep(0.1)
    if debug == False:
        r = get_response(ser)
    else:
        r = debug_get_response(ser)    
    return r

    
def pico_get_info(ser):
    '''
    Get info stored on the pico in a file info.txt
    This must contain a keyword in the first line:
    The keyword is returned  
    '''
    interrupt_program(ser)
    r = pico_execute(ser, CMD_GETINFO)
    pos1 = r.find("KEY=")   # This is the response 
    pos2 = r.find("=ENDKEY")         
    info = r[pos1+len("KEY=")+1:pos2]
    info = info.strip()
    
    return info   

def pico_listfiles(ser):
    ''' Return list of files as '\n' separated string
    if needed change to array: r1 = r.splitlines()
    '''
    interrupt_program(ser)
    r = pico_execute(ser, CMD_LISTFILES)
    return r

def pico_readfile(ser, filename):
    '''Return file contents'''
    CMD_READFILE = CMD_READFILE1 + filename + CMD_READFILE2 
    interrupt_program(ser)
    r = pico_execute(ser, CMD_READFILE)
    return r


def pico_write_file(ser, filename, s):
    ''' Write s to file (s may be multi line)
        Returns "OK" or "FILE ERROR"
    '''
    CMD_WRITEFILE = CMD_WRITEFILE1 + filename + CMD_WRITEFILE2 + s + CMD_WRITEFILE3
    print(CMD_WRITEFILE)
    interrupt_program(ser)
    r = pico_execute(ser, CMD_WRITEFILE)
    return r

def pico_append_file(ser, filename, s):
    ''' Append s to file (s may be multi line)
        Returns "OK" or "FILE ERROR"
    '''
    CMD_WRITEFILE = CMD_WRITEFILE1 + filename + CMD_WRITEFILE2A + s + CMD_WRITEFILE3
    print(CMD_WRITEFILE)
    interrupt_program(ser)
    r = pico_execute(ser, CMD_WRITEFILE)
    return r

def split_string_into_chunks(s, size):
    return [s[i:i + size] for i in range(0, len(s), size)]
    
def pico_write_big_file(ser, filename, s, chunksize):
    slist = split_string_into_chunks(s, chunksize)
    print("Writing chunk 1")
    pico_write_file(ser, filename, slist[0])  
    i = 0
    for item in slist[1:]:
        print("Writing chunk " + str(i+1))
        pico_append_file(ser, filename, item)
        i+=1
          
    
#------------------------------------------------------------------------

class Pico():
    def __init__(self, keyword):
        self.keyword = keyword
        self.port = None
        self.portname = ""
        self.connected = False
        
    def connect(self, verbose = True):
        '''Connect to Pico with the right keyword
           (keyword in first line of file INFO.TXT on Pico'''
        self.portname = find_pico(self.keyword)
        
        
        if self.portname:
            if verbose:
                print('Found ', self.keyword, ' on port',  self.portname)   

            self.port = serial.Serial(self.portname, baudrate = 115200)
            if self.port.open == False:
                self.port.open()
        else:
            if verbose:
                print(self.keyword + " not found")
            self.port = None        
               
        if self.port:
            self.connected = True
            if verbose:
                print ( "Connected to ", self.keyword)
                print()
    
    def disconnect(self, verbose = True):
        self.port.close()
        if verbose:
            print(self.keyword, "on port ", self.portname, " disconnected")
        self.port = None
        self.keyword = ""
        
    def close(self):
        self.disconnect()
    
                    
    def interrupt_prog(self):
        if self.port:
            print("Interrupting running program\n")
            self.port.write(b'\x03\x03')
      
        
    def soft_reset(self):
        soft_reset(self.port)
        time.sleep(0.5)
                             
    
    def list_files(self,  printflag = True):
        r = pico_listfiles(self.port)
        if printflag:
            print(r)
        return r
        

    def read_file(self, filename,  printflag = True):
        r = pico_readfile(self.port, filename)
        if printflag:
            print(r)
        return r
        
    def write_file(self, filename,  text, printflag = True):
        r = pico_write_file(self.port, filename, text)
        if printflag:
            print(r)
        return r    
        
    def write_big_file(self, filename,  text, chunksize):
        r = pico_write_big_file(self.port, filename, text, chunksize)
    
    def append_file(self, filename,  text, printflag = True):
        r = pico_append_file(self.port, filename, text)
        if printflag:
            print(r)
        return r     
        
    def execute(self, cmds, debug = False, printflag = True):
        r = pico_execute(self.port, cmds, debug = debug)
        if printflag:
            print(r)
        return r

#----------------------------------------------------------------------------------
if __name__ == "__main__":
    
    # Always first create Picos dictionatry:
    dict = create_pico_dictionary()
    print(dict)
        
    # print info on all Picos connected to this PC:
    for k in dict.keys():
        print(k, "\t\t", dict[k])
    
    
    # use Picos by keyword (stored in info.txt on Pico)
    pico1 = Pico("SWISS")
    pico1.connect()
    #LA = Pico("LOGICANALYSER")
    #LA.connect()

    # do something on one or the other Pico:
    pico1.execute(CMD_TEST)
    #LA.execute("x = 5; print (2* 3.14 * x)")
        
    pico1.list_files()
    
    # write file:
    pico1.write_file("test.txt", "HELLO\nTEST\n")
    
    # append to file:
    pico1.append_file("test.txt", "This is appended!\nFINE!")
    
    # read file:
    pico1.read_file("test.txt")
    
    from loremipsum import lorem
    pico1.write_big_file( "big.txt", lorem, 100)
    
    pico1.read_file("big.txt")
    
    
    # disconnect Picos:
    #for p in [LA, swiss]:
    pico1.close()
        
    

    
    
    
    
 
    





