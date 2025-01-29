from tkinter import filedialog, messagebox
import tkinter as tk
import keyboard
from tkinter import font
import threading
import sys
import time

cache=["\n"]
stacking=[False,False]
pointer=0
pasttext="\n"
currenttext="\n"
endthreads=False
carets=["1.0"]

def initialize(content=''):
    global cache, stacking
    cache=[f"{content}\n"]
    stacking=[False,False]

def start_drag(event):
    if keyboard.is_pressed("alt"):
        root.start_x = event.x
        root.start_y = event.y
        root.is_dragging = True

def drag(event):
    if getattr(root, "is_dragging", False):
        x = root.winfo_x() + event.x - root.start_x
        y = root.winfo_y() + event.y - root.start_y
        root.geometry(f"+{x}+{y}")

def stop_drag(event):
    root.is_dragging = False

def save_file():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if file_path:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(textbox.get("1.0", tk.END))
        except Exception as e:
            print(f"Error saving file: {e}")

def import_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            response = messagebox.askyesno("Textbox", "Do you want to overwrite the current text?")
            if response:
                textbox.delete("1.0", tk.END)
                textbox.insert(tk.END, file_content)
                initialize(file_content)
            else:
                file_content=''
        except Exception as e:
            print(f"Error reading file: {e}")

def new_file():
    try:
        response = messagebox.askyesno("Textbox", "Do you want to discard the current text?")
        if response:
            textbox.delete("1.0", tk.END)
            initialize()
        else:
            pass
    except Exception as e:
        print(f"Error reading file: {e}")

def handle_key(event):
    if keyboard.is_pressed("alt") or (keyboard.is_pressed("ctrl") and
                                      (keyboard.is_pressed("Z") or
                                       keyboard.is_pressed("Y") or
                                       keyboard.is_pressed("N") or
                                       keyboard.is_pressed("=") or
                                       keyboard.is_pressed("-") or
                                       keyboard.is_pressed("S") or
                                       keyboard.is_pressed("O"))):
        return "break"

def start_resize(event):
    root.start_width = root.winfo_width()
    root.start_height = root.winfo_height()
    root.start_x = event.x_root
    root.start_y = event.y_root
    root.is_resizing = True

def resize(event):
    if getattr(root, "is_resizing", False):
        delta_x = event.x_root - root.start_x
        delta_y = event.y_root - root.start_y
        new_width = max(root.start_width + delta_x, 100)
        new_height = max(root.start_height + delta_y, 100)
        root.geometry(f"{new_width}x{new_height}")

def stop_resize(event):
    root.is_resizing = False

def npos(position):
    line_number = int(position.split('.')[0])
    total_lines = int(textbox.index("end-1c").split('.')[0])
    if total_lines > 1:
        fraction = (line_number - 1) / (total_lines - 1)
    else:
        fraction = 0
    return fraction

def undo():
    global pasttext, currenttext, stacking, pointer, cache, endthreads, tt, carets
    pointer=pointer-1
    stacking[0]=True
    currenttext=cache[pointer]
    caret=carets[pointer]
    pasttext=currenttext
    ins=currenttext
    tt[0]=time.time()
    if ins.endswith("\n"):
        ins=ins[:-1]
    textbox.delete("1.0", tk.END)
    textbox.insert(tk.END, ins)
    textbox.mark_set("insert", caret)
    textbox.yview_moveto(npos(caret))

def redo():
    global pasttext, currenttext, stacking, pointer, cache, endthreads, tt, carets
    pointer+=1
    stacking[1]=True
    currenttext=cache[pointer]
    caret=carets[pointer]
    pasttext=currenttext
    ins=currenttext
    tt[1]=time.time()
    if ins.endswith("\n"):
        ins=ins[:-1]
    textbox.delete("1.0", tk.END)
    textbox.insert(tk.END, ins)
    textbox.mark_set("insert", caret)
    textbox.yview_moveto(npos(caret))

def check_func():
    global pasttext, currenttext, stacking, pointer, cache, endthreads, tt, carets
    textresizing = [False, False]
    tt=[0,0,0,0]
    fileio=[0,0,0]
    while True:
        if endthreads:
            break
        if keyboard.is_pressed("ctrl") and keyboard.is_pressed("Z") and root.focus_get() == textbox and pointer>=1 and not stacking[0]:
            undo()
        else:
            if keyboard.is_pressed("ctrl") and keyboard.is_pressed("Z") and time.time()-tt[0]>=0.5 and pointer>=1 and stacking[0]:
                undo()
                tt[0]=time.time()-0.46
            if not (keyboard.is_pressed("ctrl") and keyboard.is_pressed("Z")) and stacking[0]:
                stacking[0]=False
        if keyboard.is_pressed("ctrl") and keyboard.is_pressed("Y") and root.focus_get() == textbox and pointer<len(cache)-1 and not stacking[1]:
            redo()
        else:
            if keyboard.is_pressed("ctrl") and keyboard.is_pressed("Y") and time.time()-tt[1]>=0.5 and pointer<len(cache)-1 and stacking[1]:
                redo()
                tt[1]=time.time()-0.46
            if not (keyboard.is_pressed("ctrl") and keyboard.is_pressed("Y")) and stacking[1]:
                stacking[1]=False
        if keyboard.is_pressed("ctrl") and keyboard.is_pressed("=") and root.focus_get() == textbox and not textresizing[0]:
            textresizing[0]=True
            text_resize(2)
            tt[2]=time.time()
        else:
            if keyboard.is_pressed("ctrl") and keyboard.is_pressed("=") and time.time()-tt[2]>=0.5 and textresizing[0]:
                textresizing[0]=True
                text_resize(2)
                tt[2]=time.time()-0.46
            if not (keyboard.is_pressed("ctrl") and keyboard.is_pressed("=")) and textresizing[0]:
                textresizing[0]=False
        if keyboard.is_pressed("ctrl") and keyboard.is_pressed("-") and root.focus_get() == textbox and not textresizing[1]:
            textresizing[1]=True
            text_resize(-2)
            tt[3]=time.time()
        else:
            if keyboard.is_pressed("ctrl") and keyboard.is_pressed("-") and time.time()-tt[3]>=0.5 and textresizing[1]:
                textresizing[1]=True
                text_resize(-2)
                tt[3]=time.time()-0.46
            if not (keyboard.is_pressed("ctrl") and keyboard.is_pressed("-")) and textresizing[1]:
                textresizing[1]=False
        if keyboard.is_pressed("ctrl") and keyboard.is_pressed("S") and root.focus_get() == textbox and not fileio[1]:
            fileio[1]=1
            save_file()
        else:
            if not (keyboard.is_pressed("ctrl") and keyboard.is_pressed("S")) and fileio[1]:
                fileio[1]=0
        if keyboard.is_pressed("ctrl") and keyboard.is_pressed("O") and root.focus_get() == textbox and not fileio[0]:
            fileio[0]=1
            import_file()
        else:
            if not (keyboard.is_pressed("ctrl") and keyboard.is_pressed("O")) and fileio[0]:
                fileio[0]=0
        if keyboard.is_pressed("ctrl") and keyboard.is_pressed("N") and root.focus_get() == textbox and not fileio[2]:
            fileio[2]=1
            new_file()
        else:
            if not (keyboard.is_pressed("ctrl") and keyboard.is_pressed("N")) and fileio[2]:
                fileio[2]=0
        if keyboard.is_pressed("alt") and keyboard.is_pressed("f4") and root.focus_get() == textbox:
            endthreads=True
            root.destroy()
            root.quit()
        time.sleep(0.01)

def diff():
    global cache, pointer, pasttext, endthreads, carets
    while True:
        if endthreads:
            break
        currenttext=textbox.get("1.0", tk.END)
        if pasttext!=currenttext and not (stacking[0] or stacking[1]):
            cache=cache[:pointer+1]
            cache.append(currenttext)
            carets=carets[:pointer+1]
            carets.append(textbox.index("insert"))
            pointer = len(cache)-1
        pasttext=currenttext
        time.sleep(0.1)

def is_font_available(font_name):
    available_fonts = font.families()
    return font_name in available_fonts

def text_resize(increase=2,minimum=12):
    global cf
    current_size = cf.cget("size")
    new_size = current_size + increase
    new_size = max(minimum, new_size)
    cf.configure(size=new_size)

root = tk.Tk()
root.geometry("320x180")
root.overrideredirect(True)
root.configure(bg="#2E1A47")
root.is_dragging = False
root.is_resizing = False
root.attributes("-topmost", True)
frame = tk.Frame(root, bg="#2E1A47", highlightthickness=2, highlightbackground="#555555")
frame.pack(fill="both", expand=True)
cf = font.Font(family="Consolas", size=12)
textbox = tk.Text(frame, wrap="word", font=cf, bg="#2E1A47", fg="#FFFFFF", insertbackground="#ffffff")
textbox.pack(fill="both", expand=True, padx=10, pady=10)
textbox.bind("<Key>", handle_key)
root.bind("<Button-1>", start_drag)
root.bind("<B1-Motion>", drag)
root.bind("<ButtonRelease-1>", stop_drag)
resize_handle = tk.Label(root, bg="#D1A7FF", cursor="size_nw_se")
resize_handle.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")
resize_handle.bind("<Button-1>", start_resize)
resize_handle.bind("<B1-Motion>", resize)
resize_handle.bind("<ButtonRelease-1>", stop_resize)
thread1 = threading.Thread(target=check_func, daemon=True)
thread2 = threading.Thread(target=diff, daemon=True)
thread1.start()
thread2.start()

root.mainloop()
