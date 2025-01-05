""" Horizontal (=default) or vertical bar with radiobuttons
    for Tkinter Py3
    Author: jean-claude.feltes@education.lu
    
    Usage:
    txts=["CH0", "CH1", "All channels"]
    c=Radiobar(parent, txts, side=tk.LEFT, selected=2)
    
        parent = parent window
        txts = array containing the labels
        side and selected are optional
        side = tk.LEFT / tk.TOP  -> horizontal / vertical
        By setting selected = 0,1,2... a button can be preselected
    t = c.getstate() returns the text of the activated button
    """

import tkinter as tk


class Radiobar(tk.Frame):
    """Realizes a horizontal (=default) or vertical bar with radiobuttons
    
    side = tk.LEFT / tk.TOP  -> horizontal / vertical
    texts[] contains the button texts
    
    The state of the buttons can be fetched by calling self.getstate 
    -> returns the text of the activated button
    
    By setting selected = 0,1,2... a button can be selected
    """
    def __init__(self, parent, texts=[], side=tk.LEFT, anchor=tk.W, selected=0):
        tk.Frame.__init__(self, parent)
        self.var=tk.StringVar()
        self.var.set(texts[selected])
        
        for txt in texts:
            r = tk.Radiobutton(self, text=txt, value=txt, variable=self.var)
            r.pack(side=side, anchor=anchor, expand=tk.YES)
                        
    def getstate(self):
        v = self.var.get()
        return v
                  
    
#-----------------------------------------------------------------
# Test

if __name__ == '__main__':
    def printstate():
        print (c.getstate())
    
    root=tk.Tk()
    txts=["CH0", "CH1", "All channels"]
    c=Radiobar(root, txts, side=tk.LEFT, selected=2)
    c.config(relief=tk.RIDGE, bd=3)
    c.pack()
    
    b=tk.Button(root, text="Print", command=printstate)
    b.pack()
    
    root.mainloop()

