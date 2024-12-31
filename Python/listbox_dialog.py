''' 
    MyListbox = Toplevel window with listbox and OK button
    Author: jean-claude.feltes@education.lu
    Usage:
    selected = MyListbox(title, texts)
    selected = MyListbox(title, texts, width = w, height = h)
    texts is an array containing the list items
    width and height are optional:
       if not set, optimal values are calculated
    selected is the selected item
    The Toplevel window is automatically closed after selection.
'''    

from tkinter import *

def get_maxlength(texts):
    '''get maximal length of texts elements'''
    l = 0
    for text in texts:
        if len(text) > l:
            l = len(text)
    return l
            
    

def MyListbox (title, texts = [], width = 0, height = 0):
    """function MyListbox(title, texts, width = w, height = h)
       texts is an array containing the listbox elements
       width and height are optional:
       if not set, optimal values are calculated
    """
    if width == 0:
        width = get_maxlength(texts) 
        
    if height == 0:
        height = len(texts)
            
    d = _MyListbox(title,  texts, width = width, height = height)
    d. wait()
    return d.get()
        

class _MyListbox:
    """internal class for MyListbox"""

    def __init__(self, title,  texts=[], width = 100, height = 10):

        top = self.top = Toplevel()
        top.title(title)
        top.grab_set()
        top.attributes("-topmost", True)
               
        self.listbox = Listbox(top, width = width, height = height)
        
        for item in texts:
            self.listbox.insert(END, item)
        self.listbox.pack(padx=5)
        
        self.listbox.focus_set()
        self.listbox.bind('<Return>', self.on_Return)          # normal Return / Enter   
        self.listbox.bind('<KP_Enter>', self.on_Return)        # Enter on numeric keypad   
        self.listbox.bind('<Escape>', self.on_Escape)
        self.listbox.bind('<Double-1>', self.on_Return)
                

        b = Button(top, text="OK", command=self.on_ok)
        b.pack(pady=5)
        
        self.text=""
        
    def on_Return(self, event):
        # reaction to <Enter> / <Return>
        self.on_ready()
        
    def on_Escape(self, event):
        # reaction to <Escape>  -> clear
        self.text = ""
        self.top.destroy()  
      
               
    def on_ok(self):
        # reaction to OK button
        self.on_ready()
        
    def get(self):
        # get entered text
        return self.text
        
        
    def on_ready(self):
        # when ready: get selected text and destroy window
        
        try:
           i = int(self.listbox.curselection()[0])
        except:
            i = 0
        
        self.text = self.listbox.get(i)  
        self.top.destroy()  
        
    def wait(self):
        # wait for user input
        self.top.wait_window()  

#---------------------------------------------------
if __name__ == "__main__":  

    text = '''first option
second option
blah text
--------------------------
looooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong text
ghghjghjghj
jhjkjklj
4456456456
iuiuiouio
iuzuzuzuiz
zuzuizuzuiz'''
    
    listitems = text.splitlines()
    #t = MyListbox("TEST", listitems, width = 200, height = 50)
    t = MyListbox("TEST", listitems)
    print(t)    
    
    def showlist():
        listitems = text.splitlines()
        #t = MyListbox("TEST", listitems, width = 200, height = 50)
        t = MyListbox("TEST", listitems)
        print(t)
    
    root = Tk()
    
    b = Button(root, text = "show list", command = showlist)
    b.pack()
   
    
    root.mainloop()
    
    
