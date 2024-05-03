import tkinter as tk
import json
import threading
import time
from ctypes import windll, byref, c_ulong
import sounddevice as sd
import soundfile as sf
import pytchat

def play_audio(file_path):
    data, fs = sf.read(file_path, dtype='float32')
    sd.play(data, fs)
    sd.wait()

def make_overlay(window):
    hwnd = windll.user32.GetParent(window.winfo_id())
    windll.user32.SetWindowLongW(hwnd, -20, c_ulong(0x800000))
    windll.user32.SetLayeredWindowAttributes(hwnd, 0, 0, 0x1)

def write_data(time , user , message):
    current = {
        "time": time,
        "user": user,
        "message": message
    }

    with open('data.json', 'r') as file:
        data = json.load(file)

    array = data['chats']
    array.insert(0 , current)

    data['chats'] = array

    with open('data.json', 'w') as file:
        json.dump(data , file , indent=4, sort_keys=True)
    
def on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

app = tk.Tk()
app.title("Live Chat")
app.geometry("540x80-100-100")
app.attributes("-topmost", True)
app.attributes("-transparent", "white")
app.configure(background='white')

gwidth = 500 

frame = tk.Frame(app, bg="white", width=gwidth, height=200)
frame.place(relx=0, rely=0,relwidth=1, relheight=1)

canvas = tk.Canvas(frame, bg="white", width=gwidth, height=200, highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

canvas.configure(yscrollcommand=scrollbar.set)

scrollable_frame = tk.Frame(canvas, bg="white")
scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

initial_length = 0

def update_chats():
    global initial_length
    while True:
        time.sleep(2)
        with open('data.json', 'r') as file:
            data = json.load(file)
        chats = data['chats']

        if len(chats) == initial_length: 
            print("no new chat")
            continue 

        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        for e in chats:
            label = tk.Label(
                scrollable_frame,
                text=f"{e['time'].split(' ')[1]} : {e['user']}: {e['message']}",
                font=("Arial", 12),
                foreground="lightgreen",
                background="black",
                padx=10,  
                pady=3,   
                wraplength=gwidth
            )
            label.pack(fill=tk.X, padx=10, pady=5)
        play_audio('./notii.mp3')
        initial_length = len(chats)
        print('chat updated')

update_thread = threading.Thread(target=update_chats)
update_thread.daemon = True
update_thread.start()

chat = pytchat.create(video_id="44IqCS9XB2c")

def update_file():
    print("Getting chats")
    while chat.is_alive():
        for c in chat.get().sync_items():
            print(f"{c.datetime} {c.author.name}: {c.message}")
            write_data(c.datetime , c.author.name , c.message)

update_chat = threading.Thread(target=update_file)
update_chat.daemon = True
update_chat.start()

canvas.bind_all("<MouseWheel>", on_mousewheel)

make_overlay(app)

app.mainloop()

print("Thank you :)")