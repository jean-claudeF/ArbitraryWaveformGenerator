# music
# https://en.wikipedia.org/wiki/Music_and_mathematics

def get_frequency(halftone, octave):
    # octave = -2 ... 5,    1 for octave containing A = 440Hz
    # halftone = 0...11     C...H
    f = 440 * (2**((halftone - 9)/12)) * 2**(octave-1)
    return f

def format_nb (x, n):
    '''return x as string with n significant digits'''
    return '{:g}'.format(float('{:.{p}g}'.format(x, p=n)))
    

def print_musical_frequencies():   
    print("Musical frequencies:")
     
    tones = ['C', 'Cis', 'D', 'Dis', 'E', 'F', 'Fis', 'G', 'Gis', 'A', 'B', 'H'] 
    t = 0
    o = -2
    print('Octave', end = '\t') 
    for octave in range(-2, 6):
        print(o, end = '\t')
        o += 1
    print()
    
    for halftone in range(0, 12):
        print(tones[t], end = '\t')
        
        
        for octave in range(-2, 6):
            f = get_frequency(halftone, octave)  
            
            s =  format_nb(f, 5)
    
            print(s, end = '\t')
        print()    
        t += 1
    
    print()
    
#----------------------------------------------------------------------    

def MIDInote_to_f(notenbr):
    frequency = 2 ** ((notenbr - 69) / 12) * 440
    return frequency

#----------------------------------------------------------------------
    
nb_semitones = { "semitone": 1, "second": 2, "min_third": 3, "third": 4 ,
        "fourth": 5, "diat_tritone": 6, "fifth": 7,  "min_sixth": 8,
        "maj_sixth": 9, "min_seventh": 10, "maj_seventh": 11, "octave": 12}
           
ratios_pure = [ 1, 16/15, 9/8, 6/5, 5/4, 4/3, 45/32, 3/2, 8/5, 5/3, 9/5, 15/8, 2]

def list_intervals():
    intervals = list(nb_semitones.keys()) 
    return intervals
 
def semitones_to_factor(semitones, temperated = True):
    if temperated:
        k = 2 ** ( semitones / 12)
    else:    
        k = ratios_pure[semitones]  
    return k       
    
def interval_to_factor(interval , temperated = True):
    semitones = nb_semitones[interval]
    k = semitones_to_factor(semitones, temperated = temperated)
    return k
    
    
#----------------------------------------------------------------------    
    
if __name__ == "__main__":
    
    print("Intervals:")
    intervals =list_intervals()    
    print(intervals)
    print()
    
    print_musical_frequencies()
    
    print("Intervals")
      
    for interval in nb_semitones:
        semitones = nb_semitones[interval]
        k_pure = interval_to_factor(interval, temperated = False)
        kpure = format_nb(k_pure, 4)
        k_temperated = interval_to_factor(interval, temperated = True)
        ktemp = format_nb(k_temperated, 4)
        print(semitones, '\t',  kpure, '\t',  ktemp, '\t\t',  interval)           
            
    #-----------------------------------------------------------------
    import tkinter as tk
    
    from functools import partial
    
    def handle_interval(semitones):
        print(semitones, " semitones")
        kt = semitones_to_factor(semitones, temperated = True)
        kn = semitones_to_factor(semitones, temperated = False)
        print("Temperated:  k = ", kt)
        print("Natural: k = ", kn)

    
    root = tk.Tk()
    root.title("Button Bar")

    
    frm_interval = tk.Frame(root)
    frm_interval.pack(pady=10)
        
    for label, value in nb_semitones.items():
        btn = tk.Button(frm_interval, text=label, command=partial(handle_interval, value))
        btn.pack(side=tk.TOP, padx=5, fill = tk.X)

    
    root.mainloop()

    
