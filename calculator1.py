import tkinter as tk
import math
import json
import os
import ast
import operator

# =========================
# FILES
# =========================
HISTORY_FILE = "history.json"

# =========================
# COLORS - CASIO STYLE
# =========================
BG_MAIN = "#2d2d2d"
BG_DISPLAY = "#1a1a1a"
BG_HEADER = "#1e5a9a"
BTN_NUM = "#f5f5f5"
BTN_OP = "#e0e0e0"
BTN_FUNC = "#d0d0d0"
BTN_EQUAL = "#1e5a9a"
BTN_SHIFT = "#4a4a4a"
TEXT_DARK = "#1a1a1a"
TEXT_LIGHT = "#ffffff"
TEXT_ORANGE = "#ff8c00"
TEXT_GREEN = "#00c853"

# =========================
# STATE
# =========================
memory_value = 0.0
history_list = []
shift_active = False
history_window = None

# =========================
# LOAD / SAVE HISTORY
# =========================
def load_history():
    global history_list
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history_list = json.load(f)
        except:
            history_list = []

def save_history():
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history_list, f)
    except:
        pass

# =========================
# HISTORY WINDOW
# =========================
def open_history():
    global history_window
    if history_window is not None and history_window.winfo_exists():
        history_window.lift()
        return

    history_window = tk.Toplevel(root)
    history_window.title("History")
    history_window.geometry("380x400")
    history_window.configure(bg=BG_MAIN)
    history_window.transient(root)

    tk.Label(history_window, text="History", fg="#aaa", bg=BG_MAIN,
             font=("Arial", 11, "bold")).pack(anchor="w", padx=10, pady=8)

    listbox = tk.Listbox(history_window, bg=BG_DISPLAY, fg="#ddd",
                         font=("Consolas", 11), bd=0)
    listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    for h in history_list:
        listbox.insert(tk.END, h)
    listbox.see(tk.END)

    def clear_and_close():
        clear_history()
        listbox.delete(0, tk.END)

    tk.Button(history_window, text="Clear History", bg="#d32f2f", fg=TEXT_LIGHT,
              bd=0, padx=10, pady=5, command=clear_and_close).pack(pady=(0, 10))

# =========================
# FORMAT
# =========================
def format_number(n):
    try:
        f = float(n)
        if f.is_integer():
            return str(int(f))
        return str(round(f, 10)).rstrip('0').rstrip('.')
    except:
        return str(n)

# =========================
# MEMORY SYSTEM
# =========================
def memory_add():
    global memory_value
    try:
        val = display.get()
        if val:
            memory_value += float(val)
            mem_label.config(text=f"M: {format_number(memory_value)}")
    except:
        pass

def memory_subtract():
    global memory_value
    try:
        val = display.get()
        if val:
            memory_value -= float(val)
            mem_label.config(text=f"M: {format_number(memory_value)}")
    except:
        pass

def memory_recall():
    display.delete(0, tk.END)
    display.insert(0, format_number(memory_value))

def memory_clear():
    global memory_value
    memory_value = 0.0
    mem_label.config(text="M: 0")

# =========================
# SHIFT FUNCTION
# =========================
def toggle_shift():
    global shift_active
    shift_active = not shift_active
    shift_indicator.config(text="S" if shift_active else "")

# =========================
# CORE FUNCTIONS
# =========================
def press(x):
    if x == ".":
        current = display.get()
        if not current:
            display.insert(tk.END, "0.")
            return
        last_num = current
        for op in "+-*/(":
            if op in last_num:
                last_num = last_num.split(op)[-1]
        if "." in last_num:
            return
    display.insert(tk.END, x)

def clear():
    display.delete(0, tk.END)

def delete():
    text = display.get()
    if text:
        display.delete(len(text) - 1, tk.END)

def square():
    try:
        val = display.get()
        if val:
            result = float(val) ** 2
            display.delete(0, tk.END)
            display.insert(0, format_number(result))
            history_list.append(f"{val}² = {format_number(result)}")
            save_history()
    except:
        display.delete(0, tk.END)
        display.insert(0, "Error")

def cube():
    try:
        val = display.get()
        if val:
            result = float(val) ** 3
            display.delete(0, tk.END)
            display.insert(0, format_number(result))
            history_list.append(f"{val}³ = {format_number(result)}")
            save_history()
    except:
        display.delete(0, tk.END)
        display.insert(0, "Error")

def safe_eval(expr):
    """Safe math evaluator without using eval()"""
    allowed_ops = {
        ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg,
        ast.Mod: operator.mod  # add this line in allowed_ops
    }
    allowed_funcs = {
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "asin": math.asin, "acos": math.acos, "atan": math.atan,
        "sqrt": math.sqrt, "log": math.log10, "ln": math.log,
        "exp": math.exp
    }
    allowed_names = {"pi": math.pi, "e": math.e}

    def eval_expr(node):
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.Constant):
            return node.n
        if isinstance(node, ast.BinOp):
            return allowed_ops[type(node.op)](eval_expr(node.left), eval_expr(node.right))
        if isinstance(node, ast.UnaryOp):
            return allowed_ops[type(node.op)](eval_expr(node.operand))
        if isinstance(node, ast.Call):
            if node.func.id in allowed_funcs:
                return allowed_funcs[node.func.id](*[eval_expr(arg) for arg in node.args])
            raise ValueError("Function not allowed")
        if isinstance(node, ast.Name):
            if node.id in allowed_names:
                return allowed_names[node.id]
            raise ValueError("Name not allowed")
        raise ValueError("Invalid expression")

    tree = ast.parse(expr, mode='eval')
    return eval_expr(tree.body)

def calculate(event=None):
    expr = display.get()
    if not expr:
        return
    try:
        result = safe_eval(expr)
        display.delete(0, tk.END)
        display.insert(0, format_number(result))

        entry = f"{expr} = {format_number(result)}"
        history_list.append(entry)
        save_history()
    except:
        display.delete(0, tk.END)
        display.insert(0, "Error")

def clear_history():
    global history_list
    history_list = []
    save_history()

# =========================
# BUTTON ACTIONS
# =========================
def action(x):
    global shift_active

    if x == "SHIFT":
        toggle_shift()
        return

    if shift_active:
        shift_map = {"sin": "asin(", "cos": "acos(", "tan": "atan(", "x²": "x³"}
        if x in shift_map:
            if x == "x²":
                cube()
                toggle_shift()
                return
            else:
                display.insert(tk.END, shift_map[x])
                toggle_shift()
                return

    actions = {
        "=": calculate,
        "C": clear,
        "DEL": delete,
        "π": lambda: press("pi"),
        "x²": square,
        "sqrt": lambda: press("sqrt("),
        "log": lambda: press("log("),
        "ln": lambda: press("ln("),
        "sin": lambda: press("sin("),
        "cos": lambda: press("cos("),
        "tan": lambda: press("tan("),
        "M+": memory_add,
        "M-": memory_subtract,
        "MR": memory_recall,
        "MC": memory_clear,
    }
    if x in actions:
        actions[x]()
    else:
        press(x)

# =========================
# UI SETUP
# =========================
root = tk.Tk()
root.title("Efezino model")
root.geometry("420x650")
root.minsize(420, 650)
root.configure(bg=BG_MAIN)
root.protocol("WM_DELETE_WINDOW", lambda: (save_history(), root.destroy()))

root.bind("<Return>", calculate)
root.bind("<BackSpace>", lambda e: delete())
root.bind("<Escape>", lambda e: clear())

# =========================
# MENU BAR
# =========================
menubar = tk.Menu(root, bg=BG_HEADER, fg=TEXT_LIGHT, tearoff=0)
root.config(menu=menubar)
history_menu = tk.Menu(menubar, bg=BG_HEADER, fg=TEXT_LIGHT, tearoff=0)
menubar.add_cascade(label="History", menu=history_menu)
history_menu.add_command(label="View History", command=open_history)
history_menu.add_separator()
history_menu.add_command(label="Clear History", command=clear_history)

# =========================
# HEADER
# =========================
header = tk.Frame(root, bg=BG_HEADER)
header.pack(fill="x")

tk.Label(header, text="∑", fg=TEXT_LIGHT, bg=BG_HEADER,
         font=("Arial", 18, "bold")).pack(side="left", padx=(15, 5), pady=10)

tk.Label(header, text="Efezino model", fg=TEXT_LIGHT, bg=BG_HEADER,
         font=("Arial", 16, "bold")).pack(side="left", pady=10)

tk.Label(header, text="NATURAL-V.P.A.M.", fg=TEXT_LIGHT, bg=BG_HEADER,
         font=("Arial", 8)).pack(side="right", padx=15, pady=10)

# =========================
# STATUS BAR
# =========================
status_bar = tk.Frame(root, bg=BG_MAIN)
status_bar.pack(fill="x", padx=10, pady=(5, 0))

shift_indicator = tk.Label(status_bar, text="", fg=TEXT_ORANGE, bg=BG_MAIN,
                           font=("Arial", 12, "bold"))
shift_indicator.pack(side="left")

mem_label = tk.Label(status_bar, text="M: 0", fg=TEXT_GREEN, bg=BG_MAIN,
                     font=("Arial", 9))
mem_label.pack(side="left", padx=10)

# =========================
# DISPLAY
# =========================
display = tk.Entry(
    root,
    font=("Consolas", 24),
    bg=BG_DISPLAY,
    fg=TEXT_LIGHT,
    insertbackground=TEXT_LIGHT,
    bd=2,
    relief="sunken",
    justify="right"
)
display.pack(fill="x", padx=7, pady=7, ipady=9)
display.focus()

# =========================
# LOAD HISTORY
# =========================
load_history()

def memory_clear():
    global memory
    memory = 0

def memory_recall():
    display.delete(0, tk.END)
    display.insert(0, str(memory))

def memory_add():
    global memory
    try:
        memory += float(display.get())
    except:
        pass

def memory_subtract():
    global memory
    try:
        memory -= float(display.get())
    except:
        pass
# =========================
# BUTTONS
# =========================
buttons = [
    ("SHIFT", "DEL", "C", "x²","%"),
    ("sin", "cos", "tan", "/"),
    ("sqrt", "log", "ln", "*"),
    ("7", "8", "9", "-"),
   
    ("4", "5", "6", "+"),
    ("1", "2", "3", "("),
    ("0","00", ".", ")", "=")
]

shift_labels = [
    ("", "", "", "x³"), # Row 1
    ("sin⁻¹", "cos⁻¹", "tan⁻¹", ""), # Row 2
    ("", "", ""), # Row 3
    ("", "", ""), # Row 4
    ("", "", ""), # Row 5
    ("", "", ""), # Row 6
    ("", "", "") # Row 7
]

memory = 0

for i, row in enumerate(buttons):
    label_frame = tk.Frame(root, bg=BG_MAIN)
    label_frame.pack(fill="x", padx=4)
    for col, s_label in enumerate(shift_labels[i]):
        label_frame.grid_columnconfigure(col, weight=1)
        tk.Label(label_frame, text=s_label, fg=TEXT_ORANGE, bg=BG_MAIN,
                 font=("Arial", 9)).grid(row=0, column=col)

    frame = tk.Frame(root, bg=BG_MAIN)
    frame.pack(expand=True, fill="both", padx=2, pady=2)

    for col, btn in enumerate(row):
        frame.grid_columnconfigure(col, weight=1)

        if btn in "0123456789.":
            color = BTN_NUM
            txt_color = TEXT_DARK
        elif btn == "=":
            color = BTN_EQUAL
            txt_color = TEXT_LIGHT
        elif btn == "SHIFT":
            color = BTN_SHIFT
            txt_color = TEXT_LIGHT
        elif btn in "+-*/()":
            color = BTN_OP
            txt_color = TEXT_DARK
        else:
            color = BTN_FUNC
            txt_color = TEXT_DARK

        button = tk.Button(
            frame,
            text=btn,
            font=("Arial", 13, "bold"),
            fg=txt_color,
            bg=color,
            activebackground="#b0b0b0",
            activeforeground=TEXT_DARK,
            bd=1,
            relief="raised",
            command=lambda x=btn: action(x)
        )
        button.grid(row=0, column=col, sticky="nsew", padx=2, pady=2)
        frame.grid_rowconfigure(0, weight=1)

# =========================
# MEMORY BUTTONS
# =========================
mem_frame = tk.Frame(root, bg=BG_MAIN)
mem_frame.pack(fill="x", padx=10, pady=(5, 10))

for btn in ("M+", "M-", "MR", "MC"):
    b = tk.Button(
        mem_frame,
        text=btn,
        font=("Arial", 11, "bold"),
        fg=TEXT_DARK,
        bg=BTN_OP,
        activebackground="#b0b0b0",
        activeforeground=TEXT_DARK,
        bd=1,
        relief="raised",
        command=lambda x=btn: action(x)
    )
    b.pack(side="left", expand=True, fill="both", padx=2, pady=2)

root.mainloop()