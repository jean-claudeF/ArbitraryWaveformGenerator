"""Buttonbar for Py3
    Author: jean-claude.feltes@education.lu
    Realizes a horizontal (=default) or vertical bar with buttons
    
    Example:
    b1=MultiButton(root, cmds, side=tk.TOP)
    
    side = tk.LEFT / tk.TOP  -> horizontal / vertical
    cmds is a dictionary containing button text and callback functions
    in the form { 'cmd1': callback1, ....}
        
"""
import tkinter as tk
        
class Buttonbar(tk.Frame):

    def __init__(self, cmds, parent=None, side=tk.LEFT, anchor=tk.W ):
    
        tk.Frame.__init__(self, parent)    
                       
        # create buttons
        for btntext in cmds:
            btn = tk.Button(self, text=btntext,command=cmds[btntext])
            btn.pack(side=side, expand=1, fill=tk.BOTH)
            
class LabeledButtonbar(tk.Frame):

    def __init__(self, cmds,lbltxt, parent=None,  buttonside=tk.LEFT, labelside=tk.LEFT, anchor=tk.W ):
    
        tk.Frame.__init__(self, parent)    
        
   
        self.label=tk.Label(self, text=lbltxt)
        self.label.pack(side=labelside)
                   
        # create buttons
        for btntext in cmds:
            btn = tk.Button(self, text=btntext,command=cmds[btntext])
            btn.pack(side=buttonside, expand=1, fill=tk.BOTH)            
            
#-----------------------------------------------------------------------
if __name__ == '__main__':
    def on_cmd1():
        print ("HELLO")
        
    def on_cmd2():
        print ("BONJOUR")
        
    def on_cmd3():
        print ("GOOD BYE")
        
            
    cmds = {
            'cmd1': on_cmd1,
            'cmd2___long': on_cmd2,
            'cmd3': on_cmd3
    }     
    
    root = tk.Tk()
    mf = tk.Frame()
    mf.pack()
    
    
    #f1 = ButtonFrame(cmds, 'V', side=LEFT)
    b1=LabeledButtonbar( cmds, "Labeled\nbuttonbar", labelside=tk.TOP, buttonside=tk.LEFT)
    b1.label.config(fg='blue')
    b1.config(relief=tk.RIDGE, bd=3)
    b1.pack(side = tk.TOP)
    
    b2=Buttonbar(cmds, side=tk.LEFT)
    b2.config(relief=tk.RIDGE, bd=3)
    b2.pack(side = tk.TOP)
    
    b3=LabeledButtonbar( cmds, "Labeled\nbuttonbar", buttonside=tk.TOP)
    b3.label.config(fg='blue')
    b3.config(relief=tk.RIDGE, bd=3)
    b3.pack(side = tk.TOP)
    
    b3=LabeledButtonbar( cmds, "Labeled\nbuttonbar", labelside=tk.TOP, buttonside=tk.TOP)
    b3.label.config(fg='blue')
    b3.config(relief=tk.RIDGE, bd=3)
    b3.pack(side = tk.TOP)
    
    root.mainloop()

