"""
CAUTION: Please modify ARDUINO_COM below so that it matches the correct serial port of the Arduino.

CURRENT LIMITATION:
1. When reading serial input, the GUI freezes until a serial input is received, because
   readline() is a blocking function.
        - Tried other non-blocking read. Somehow didn't work.
        - Can solve using "multithreading" (will do that sometime later...).

2. There's a need to match timing setting in this script and in the Arduino sketch (i.e.
   TIME_LIMIT, INITIAL_WAIT, WAIT).
        - Can be solved by sending timing data over serial.
"""
import simpleaudio as sa
from tkinter import *
import serial
from tkinter import messagebox
from tkinter import font
# GUI settings.
SCORE_SIZE = 160
FONT_SIZE = 60
# Comm and timing settings, must match with Arduino code!
ARDUINO_COM = 'COM7'
BAUD = 9600
TIME_LIMIT = 5000    # in milliseconds.
INITIAL_WAIT = 4000  # in milliseconds.
WAIT = 6000          # in milliseconds.
UPDATE_RATE = 100    # in milliseconds. Hardcoded in the Arduino program (for now).
def helloCallBack():
   global var_score_1
   global var_score_2
   score="Your Score is {fname},\nHighest Score is {age}".format(fname = var_score_2, age = var_score_1)
   msg = messagebox.showwarning( "Game OVER", score)
    
# Create Tk object (GUI window).
display = Tk()

display.attributes('-fullscreen', True)   # Uncomment this for full screen!
display.geometry('1000x600')
display.title("Memory Test!")

arduino = serial.Serial(ARDUINO_COM, BAUD)   # Open serial port.

var_score_1 = 0
var_score_2 = 0
time = TIME_LIMIT
arduino.write(65)
###################### User defined functions ######################
def reset_time():
    #global time
    #time = TIME_LIMIT
   # time_left.config(text = "Time: {:.2f} seconds".format(time/1000))

    arduino.reset_input_buffer()     # Flush buffer.

    reset_button.config(state=DISABLED)
    quit_button.config(state=DISABLED)
    display.after(10, update_score)    # Check serial immediately (start polling).


def reset_score():
    global var_score_1
    global var_score_2
    
    var_score_1 = 0
    var_score_2 = 0
    score_1.config(text = var_score_1)
    score_2.config(text = var_score_2)


# Update the score & time.
def update_score():
    global var_score_1
    global var_score_2
    global time
    
    score_update = arduino.readline()[0:-2]   # Remove the last 2 chars (CR and LF).
    print(score_update)
    if(str(score_update).count("Game over")):
        filename = './Super.wav'
        wave_obj = sa.WaveObject.from_wave_file(filename)
        play_obj = wave_obj.play()
        play_obj.wait_done()
        helloCallBack()
        var_score_2 = 0
        
        
    else:    
        score_update = str(score_update)[2:-1].split(" ")
        # Remove b'' by slicing, then split into a list of 2 indices (1st score and 2nd score update).
        print(score_update)
        var_score_1 = int( score_update[1] )
        var_score_2 = int( score_update[0] )
        time -= UPDATE_RATE    # The arduino sends score update data every <UPDATE_RATE> secs.
        display.after(UPDATE_RATE - 10, update_score)
    score_1.config(text = var_score_1)
    score_2.config(text = var_score_2)
        
    '''if time < 0:
            #time_left.config(text = "Time's out! Next please!")
            display.after(WAIT - 100, reset_time)   # Reset the time display.
            reset_button.config(state = NORMAL)
            quit_button.config(state = NORMAL) 
        else:'''
           # time_left.config(text = "Time: {:.2f} seconds".format(time/1000))
    
            # Check serial again shortly (for continuous score update).
    #update_score()         
# Quit game (kill the GUI).
def quit():
    arduino.write(bytes('s', 'utf-8'))
    display.destroy()

def start():
    arduino.write(bytes('a', 'utf-8'))
    update_score()

###################### GUI Setup ######################

# TKinter color chart: http://www.science.smith.edu/dftwiki/00000000000000000000000000000000000000000  l/index.php/Color_Charts_for_TKinter

# Title.
title = Label(text = "    Memory Test !", fg = "orange red", font=("Segoe Script", 65))
title.grid(row = 0, columnspan = 3, sticky=W+E+S, pady = 20)

# Display time.
'''time_left = Label(text = 'Welcome! Starting soon...', fg = "black", font=("Calibri", 30))
time_left.grid(row = 1, columnspan = 2, sticky=W+E+N, pady = 20)'''

# Display score of team 1.

score_1 = Label(text = 0, fg = "blue", bg = 'white', font=("Calibri", SCORE_SIZE),width=4)
score_1.grid(row = 2, column = 0)
#score_1.place(x = 300, y = 180)
score_1_label = Label(text = "           Highest Score           ",\
                      fg = "blue", font=("Calibri", FONT_SIZE))
score_1_label.grid(row = 3, column = 0)

# Display score of team 2.
score_2 = Label(text = 0, fg = "red", bg = 'white', font=("Calibri", SCORE_SIZE),width=4)
score_2.grid(row = 2, column = 1)
score_2_label = Label(text = " Current Score ",\
                      fg = "red", font=("Calibri", FONT_SIZE))
score_2_label.grid(row = 3, column = 1)

# Button to reset score and quit window.
reset_button = Button(text = 'Reset Game', command = reset_score, width = 20,height=1, state = NORMAL,font=("Calibri", 20,"bold"),fg="white",bg="black")
reset_button.place(x = 950, y = 600)

quit_button = Button(text = 'Quit Game', command = quit, width = 20,height=1, state = NORMAL,font=("Calibri", 20,"bold"),fg="white",bg="black")
quit_button.place(x = 260, y = 600)
# quit_button.grid(row = 4, column = 1, sticky=N+S+W, padx = 20)

start_button = Button(text = 'Start Game', command = start, width = 40, state = NORMAL,font=("Calibri", 50,"bold"),fg="white",bg="gray")
start_button.place(x = 100, y = 700)

#############################################################################

# Initial call for score_update().

display.mainloop()   # Launch GUI.