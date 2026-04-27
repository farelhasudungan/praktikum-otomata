import re
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

# =========================
# TOKEN DATA
# =========================
RESERVED_WORDS = {
    "if", "else", "elif", "for", "while", "do", "return",
    "int", "float", "double", "char", "void", "bool", "string",
    "break", "continue", "class", "def", "import", "from",
    "True", "False", "None", "and", "or", "not", "in",
    "print", "input", "len", "range", "pass", "lambda",
    "try", "except", "finally", "with", "as", "yield",
    "new", "delete", "this", "self", "static", "const",
    "public", "private", "protected", "struct", "enum",
    "switch", "case", "default", "typedef", "include",
    "namespace", "using", "auto", "long", "short", "unsigned"
}

MATH_OPERATORS = set("+-*/%=<>!")
SYMBOLS = set("(){}[];,.:@#\\^~`?$&")

# Palette
COLORS = {
    "bg":          "#1E1E2E",   # dark background
    "panel":       "#181825",   # darker panel
    "surface":     "#313244",   # card/input surface
    "border":      "#45475A",   # subtle border
    "accent":      "#89B4FA",   # blue accent
    "header_bg":   "#11111B",   # header

    "fg":          "#CDD6F4",   # main text
    "fg_dim":      "#BAC2DE",   # secondary text
    "fg_muted":    "#6C7086",   # muted text

    "reserved":    "#CBA6F7",   # purple - reserved words
    "variable":    "#89DCEB",   # cyan  - variables
    "symbol":      "#F38BA8",   # red   - symbols
    "math":        "#A6E3A1",   # green - math
    "string":      "#F9E2AF",   # yellow - strings/numbers
    "unknown":     "#F38BA8",   # red   - unknown

    "btn_primary": "#89B4FA",
    "btn_danger":  "#F38BA8",
    "btn_neutral": "#585B70",
}

# =========================
# TOKENIZER
# =========================
def classify_token(token):
    if token in RESERVED_WORDS:
        return "Reserved Word"
    elif re.match(r'^".*"$|^\'.*\'$', token):
        return "String"
    elif re.match(r'^[0-9]+(\.[0-9]+)?$', token):
        return "Math"
    elif token in MATH_OPERATORS or token in {"//", "**", "==", "!=", "<=", ">=", "&&", "||", "++", "--"}:
        return "Math"
    elif token in SYMBOLS:
        return "Symbol"
    elif re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', token):
        return "Variable"
    else:
        return "Unknown"

def tokenize(code):
    # Match strings, floats, ints, identifiers, multi-char ops, single chars
    pattern = r'"[^"]*"|\'[^\']*\'|[a-zA-Z_][a-zA-Z0-9_]*|[0-9]+(?:\.[0-9]+)?|//|==|!=|<=|>=|\*\*|\+\+|--|&&|\|\||[^\s]'
    return re.findall(pattern, code)

# =========================
# MAIN LOGIC
# =========================
def analyze_code():
    code = input_box.get("1.0", tk.END).strip()
    if not code:
        messagebox.showwarning("Peringatan", "Input program kosong!")
        return

    tokens = tokenize(code)

    output_box.config(state="normal")
    output_box.delete("1.0", tk.END)

    counts = {"Reserved Word": 0, "Variable": 0, "Symbol": 0, "Math": 0, "String": 0, "Unknown": 0}

    for token in tokens:
        category = classify_token(token)
        counts[category] += 1
        tag = category.replace(" ", "_")
        line = f"  {token:<20} →  {category}\n"
        output_box.insert(tk.END, line, tag)

    output_box.config(state="disabled")

    # Update stats bar
    total = len(tokens)
    stats_label.config(text=(
        f"Total: {total}   |   "
        f"Reserved: {counts['Reserved Word']}   "
        f"Variable: {counts['Variable']}   "
        f"Math: {counts['Math']}   "
        f"Symbol: {counts['Symbol']}   "
        f"String: {counts['String']}   "
        f"Unknown: {counts['Unknown']}"
    ))

def load_file():
    path = filedialog.askopenfilename(
        filetypes=[("Source Files", "*.py *.c *.cpp *.java *.txt"), ("All Files", "*.*")]
    )
    if path:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        input_box.delete("1.0", tk.END)
        input_box.insert(tk.END, content)
        stats_label.config(text=f"File dimuat: {path.split('/')[-1]}")

def copy_output():
    content = output_box.get("1.0", tk.END).strip()
    if content:
        root.clipboard_clear()
        root.clipboard_append(content)
        messagebox.showinfo("Berhasil", "Output berhasil disalin ke clipboard!")

def clear_all():
    input_box.delete("1.0", tk.END)
    output_box.config(state="normal")
    output_box.delete("1.0", tk.END)
    output_box.config(state="disabled")
    stats_label.config(text="Siap menganalisis...")

# =========================
# HELPER: Create styled button
# =========================
def make_button(parent, text, command, color):
    return tk.Button(
        parent, text=text, command=command,
        bg=color, fg=COLORS["header_bg"],
        font=("Consolas", 10, "bold"),
        relief="flat", cursor="hand2",
        padx=14, pady=6,
        activebackground=COLORS["fg_dim"],
        activeforeground=COLORS["header_bg"],
        bd=0
    )

# =========================
# UI SETUP
# =========================
root = tk.Tk()
root.title("Lexical Tokenizer Analyzer")
root.geometry("1050x700")
root.minsize(800, 600)
root.configure(bg=COLORS["bg"])

# ===== HEADER =====
header = tk.Frame(root, bg=COLORS["header_bg"], pady=12)
header.pack(fill="x")

tk.Label(
    header,
    text="⬡  LEXICAL TOKENIZER",
    fg=COLORS["accent"], bg=COLORS["header_bg"],
    font=("Consolas", 16, "bold")
).pack(side="left", padx=20)

tk.Label(
    header,
    text="Tokenizer & Lexical Analyzer v1.0",
    fg=COLORS["fg_muted"], bg=COLORS["header_bg"],
    font=("Consolas", 9)
).pack(side="left")

# ===== BODY =====
body = tk.Frame(root, bg=COLORS["bg"])
body.pack(fill="both", expand=True, padx=16, pady=10)

body.columnconfigure(0, weight=1)
body.columnconfigure(1, weight=1)
body.rowconfigure(1, weight=1)

# --- Input Panel ---
tk.Label(
    body, text="INPUT PROGRAM",
    fg=COLORS["accent"], bg=COLORS["bg"],
    font=("Consolas", 10, "bold")
).grid(row=0, column=0, sticky="w", padx=4, pady=(0,4))

input_box = ScrolledText(
    body,
    wrap=tk.WORD, font=("Consolas", 11),
    bg=COLORS["surface"], fg=COLORS["fg"],
    insertbackground=COLORS["accent"],
    selectbackground=COLORS["border"],
    relief="flat", bd=0,
    padx=10, pady=10
)
input_box.grid(row=1, column=0, sticky="nsew", padx=(0, 8))

# --- Output Panel ---
tk.Label(
    body, text="HASIL TOKEN",
    fg=COLORS["accent"], bg=COLORS["bg"],
    font=("Consolas", 10, "bold")
).grid(row=0, column=1, sticky="w", padx=4, pady=(0,4))

output_box = ScrolledText(
    body,
    wrap=tk.WORD, font=("Consolas", 11),
    bg=COLORS["panel"], fg=COLORS["fg"],
    selectbackground=COLORS["border"],
    relief="flat", bd=0, state="disabled",
    padx=10, pady=10
)
output_box.grid(row=1, column=1, sticky="nsew")

# Token color tags
output_box.tag_config("Reserved_Word", foreground=COLORS["reserved"])
output_box.tag_config("Variable",      foreground=COLORS["variable"])
output_box.tag_config("Symbol",        foreground=COLORS["symbol"])
output_box.tag_config("Math",          foreground=COLORS["math"])
output_box.tag_config("String",        foreground=COLORS["string"])
output_box.tag_config("Unknown",       foreground=COLORS["unknown"])

# ===== BUTTON BAR =====
btn_bar = tk.Frame(root, bg=COLORS["bg"])
btn_bar.pack(pady=10)

make_button(btn_bar, "▶  Analyze",   analyze_code, COLORS["btn_primary"]).pack(side="left", padx=6)
make_button(btn_bar, "📂  Load File", load_file,    COLORS["btn_neutral"]).pack(side="left", padx=6)
make_button(btn_bar, "📋  Copy Output", copy_output, COLORS["btn_neutral"]).pack(side="left", padx=6)
make_button(btn_bar, "✕  Clear",     clear_all,    COLORS["btn_danger"]).pack(side="left", padx=6)

# ===== LEGEND ROW =====
legend = tk.Frame(root, bg=COLORS["header_bg"], pady=6)
legend.pack(fill="x")

legend_items = [
    ("Reserved Word", COLORS["reserved"]),
    ("Variable",      COLORS["variable"]),
    ("Math / Number", COLORS["math"]),
    ("Symbol",        COLORS["symbol"]),
    ("String",        COLORS["string"]),
    ("Unknown",       COLORS["unknown"]),
]

tk.Label(legend, text="LEGEND:", fg=COLORS["fg_muted"], bg=COLORS["header_bg"],
         font=("Consolas", 9, "bold")).pack(side="left", padx=14)

for label, color in legend_items:
    tk.Label(legend, text=f"● {label}", fg=color, bg=COLORS["header_bg"],
             font=("Consolas", 9)).pack(side="left", padx=10)

# ===== STATUS BAR =====
stats_label = tk.Label(
    root, text="Siap menganalisis...",
    fg=COLORS["fg_muted"], bg=COLORS["panel"],
    font=("Consolas", 9), anchor="w", padx=14, pady=4
)
stats_label.pack(fill="x", side="bottom")

root.mainloop()