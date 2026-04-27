import tkinter as tk
from tkinter import ttk
import math

# =============================================================
# FSM DEFINITION
# L = { x ∈ (0+1)⁺ | karakter terakhir = 1  ∧  tidak ada substring "00" }
#
# States:
#   S = Start (initial)
#   A = Terakhir baca '0'
#   B = Terakhir baca '1'  ← Accept state
#   C = Dead/Trap (pernah baca "00")
# =============================================================

STATES        = ["S", "A", "B", "C"]
START_STATE   = "S"
ACCEPT_STATES = {"B"}
ALPHABET      = {"0", "1"}

TRANSITIONS = {
    ("S", "0"): "A",  ("S", "1"): "B",
    ("A", "0"): "C",  ("A", "1"): "B",
    ("B", "0"): "A",  ("B", "1"): "B",
    ("C", "0"): "C",  ("C", "1"): "C",
}

STATE_DESC = {
    "S": "Initial state — belum membaca input",
    "A": "Terakhir baca '0', menunggu '1'",
    "B": "Terakhir baca '1' — ACCEPT STATE",
    "C": "Dead/Trap — ditemukan substring '00'",
}

TRANSITION_TABLE = {
    "S": {"0": "A", "1": "B"},
    "A": {"0": "C", "1": "B"},
    "B": {"0": "A", "1": "B"},
    "C": {"0": "C", "1": "C"},
}


# =============================================================
# FSM SIMULATION
# =============================================================
def simulate_fsm(input_string):
    """Return (accepted, steps_list, reason_string)."""
    if not input_string:
        return False, [], "String kosong — harus minimal 1 karakter"
    for ch in input_string:
        if ch not in ALPHABET:
            return False, [], f"Karakter '{ch}' tidak valid. Hanya '0' dan '1'."

    current = START_STATE
    steps = [("—", current, STATE_DESC[current])]
    for char in input_string:
        current = TRANSITIONS[(current, char)]
        steps.append((char, current, STATE_DESC[current]))

    accepted = current in ACCEPT_STATES
    if accepted:
        reason = "DITERIMA — Berakhir dengan '1' dan bebas dari substring '00'"
    elif current == "C":
        reason = "DITOLAK — String mengandung substring '00'"
    else:
        reason = "DITOLAK — Karakter terakhir bukan '1'"

    return accepted, steps, reason


# =============================================================
# GUI APPLICATION
# =============================================================
class FSMApp:

    # ── Colour palette ─────────────────────────────────────────
    BG        = "#0b0f1a"
    BG_PANEL  = "#0e1623"
    BG_CARD   = "#141f30"
    BG_CELL   = "#1a2840"

    CYAN      = "#00d4ff"
    CYAN_DIM  = "#006a80"
    GREEN     = "#00e5a0"
    RED       = "#ff4d6d"
    YELLOW    = "#ffd166"
    PURPLE    = "#b39dff"
    ORANGE    = "#fb923c"
    TEXT      = "#dde6f0"
    TEXT_DIM  = "#4a6080"
    BORDER    = "#1a3050"

    # Per-state fill and stroke colours
    S_FILL   = {"S": "#0e2a45", "A": "#1e2a10", "B": "#0e2a1e", "C": "#2a0e1e"}
    S_STROKE = {"S": "#00d4ff", "A": "#ffd166", "B": "#00e5a0", "C": "#ff4d6d"}

    def __init__(self, root):
        self.root = root
        self.root.title("FSM Simulator — Otomata & Bahasa Formal")
        self.root.geometry("1200x820")
        self.root.configure(bg=self.BG)
        self.root.resizable(True, True)
        self.root.minsize(960, 680)

        # State variables
        self._animation_id   = None
        self._animation_step = -1
        self._current_steps  = []
        self._pulse_phase    = 0.0
        self._highlighted    = None   # state name currently highlighted
        self._active_edge    = None   # (from_state, to_state) active transition

        self._build_ui()
        self._draw_diagram()      # initial draw
        self._tick_pulse()        # start idle pulse animation

    # ===========================================================
    # UI CONSTRUCTION
    # ===========================================================
    def _build_ui(self):
        # Thin top accent stripe
        tk.Frame(self.root, bg=self.CYAN, height=2).pack(fill="x")

        # Header bar
        hdr = tk.Frame(self.root, bg=self.BG_PANEL, height=58)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        left = tk.Frame(hdr, bg=self.BG_PANEL)
        left.pack(side="left", padx=18, fill="y")
        tk.Frame(left, bg=self.CYAN, width=3).pack(
            side="left", fill="y", pady=11, padx=(0, 12))
        tcol = tk.Frame(left, bg=self.BG_PANEL)
        tcol.pack(side="left")
        tk.Label(tcol, text="FSM SIMULATOR",
                 font=("Courier New", 15, "bold"),
                 fg=self.CYAN, bg=self.BG_PANEL).pack(anchor="w", pady=(9, 0))
        tk.Label(tcol, text="Finite State Machine  ·  Teori Bahasa & Automata",
                 font=("Courier New", 8),
                 fg=self.TEXT_DIM, bg=self.BG_PANEL).pack(anchor="w")

        tk.Label(hdr,
                 text="L = { x ∈ (0+1)⁺  |  last(x)=1  ∧  ¬∃'00' ⊆ x }",
                 font=("Courier New", 10), fg=self.YELLOW,
                 bg=self.BG_PANEL).pack(side="right", padx=20, pady=18)

        tk.Frame(self.root, bg=self.BORDER, height=1).pack(fill="x")

        # Body
        body = tk.Frame(self.root, bg=self.BG)
        body.pack(fill="both", expand=True, padx=12, pady=10)

        # Left column: diagram + transition table
        left_col = tk.Frame(body, bg=self.BORDER, bd=1)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        dh = tk.Frame(left_col, bg=self.BG_CARD, height=32)
        dh.pack(fill="x")
        dh.pack_propagate(False)
        tk.Frame(dh, bg=self.GREEN, width=3).pack(
            side="left", fill="y", pady=6, padx=(8, 8))
        tk.Label(dh, text="DIAGRAM  FINITE  STATE  MACHINE",
                 font=("Courier New", 9, "bold"),
                 fg=self.TEXT_DIM, bg=self.BG_CARD).pack(side="left", pady=8)

        self.canvas = tk.Canvas(left_col, bg=self.BG,
                                highlightthickness=0, width=520, height=390)
        self.canvas.pack(fill="both", expand=True)

        tk.Frame(left_col, bg=self.BORDER, height=1).pack(fill="x")
        tbl_frame = tk.Frame(left_col, bg=self.BG_CARD)
        tbl_frame.pack(fill="x")
        self._build_transition_table(tbl_frame)

        # Right column
        right_col = tk.Frame(body, bg=self.BG, width=385)
        right_col.pack(side="right", fill="both")
        right_col.pack_propagate(False)

        self._build_input_panel(right_col)
        self._build_result_panel(right_col)
        self._build_trace_panel(right_col)
        self._build_quicktest_panel(right_col)

        # Status bar
        tk.Frame(self.root, bg=self.BORDER, height=1).pack(fill="x")
        sb = tk.Frame(self.root, bg=self.BG_PANEL, height=22)
        sb.pack(fill="x")
        sb.pack_propagate(False)
        tk.Label(sb,
                 text="  Enter → Analyze   ·   ⏵ Step-by-Step   ·   ✕ Clear",
                 font=("Courier New", 8),
                 fg=self.TEXT_DIM, bg=self.BG_PANEL).pack(side="left", pady=3)

    # ── Input panel ──────────────────────────────────────────────
    def _build_input_panel(self, parent):
        card = tk.Frame(parent, bg=self.BG_CARD,
                        highlightbackground=self.BORDER, highlightthickness=1)
        card.pack(fill="x", pady=(0, 8))

        hdr = tk.Frame(card, bg=self.BG_CARD)
        hdr.pack(fill="x", padx=14, pady=(10, 6))
        tk.Frame(hdr, bg=self.CYAN, width=3, height=13).pack(
            side="left", padx=(0, 8))
        tk.Label(hdr, text="INPUT STRING",
                 font=("Courier New", 9, "bold"),
                 fg=self.TEXT_DIM, bg=self.BG_CARD).pack(side="left")

        self._entry_wrap = tk.Frame(card, bg=self.CYAN_DIM)
        self._entry_wrap.pack(fill="x", padx=14, pady=(0, 6))
        inner = tk.Frame(self._entry_wrap, bg="#0a1828", padx=1, pady=1)
        inner.pack(fill="x")

        self.entry = tk.Entry(inner, font=("Courier New", 22, "bold"),
                              bg="#0a1828", fg="#60efff",
                              insertbackground=self.CYAN,
                              relief="flat", justify="center", bd=0)
        self.entry.pack(fill="x", ipady=9, padx=8)
        self.entry.bind("<Return>",     lambda e: self.run_fsm())
        self.entry.bind("<KeyRelease>", self._on_key)
        self.entry.bind("<FocusIn>",
                        lambda e: self._entry_wrap.config(bg=self.CYAN))
        self.entry.bind("<FocusOut>",
                        lambda e: self._entry_wrap.config(bg=self.CYAN_DIM))

        self._char_var = tk.StringVar(value="0 karakter")
        tk.Label(card, textvariable=self._char_var,
                 font=("Courier New", 8), fg=self.TEXT_DIM,
                 bg=self.BG_CARD).pack(anchor="e", padx=14, pady=(0, 4))

        btn_row = tk.Frame(card, bg=self.BG_CARD)
        btn_row.pack(fill="x", padx=14, pady=(0, 14))
        self._make_btn(btn_row, "▶  ANALYZE",      self.GREEN,  self.run_fsm
                       ).pack(side="left", fill="x", expand=True, padx=(0, 4))
        self._make_btn(btn_row, "⏵  STEP BY STEP", self.PURPLE, self.run_step
                       ).pack(side="left", fill="x", expand=True, padx=(4, 4))
        self._make_btn(btn_row, "✕", self.RED, self.clear_all, width=4
                       ).pack(side="left", padx=(4, 0))

    # ── Result panel ─────────────────────────────────────────────
    def _build_result_panel(self, parent):
        self._result_frame = tk.Frame(parent, bg=self.BG_CARD,
                                      highlightbackground=self.BORDER,
                                      highlightthickness=1)
        self._result_frame.pack(fill="x", pady=(0, 8))

        self._result_icon = tk.Label(self._result_frame, text="◈",
                                     font=("Segoe UI", 22),
                                     fg=self.TEXT_DIM, bg=self.BG_CARD)
        self._result_icon.pack(side="left", padx=(14, 8), pady=10)

        col = tk.Frame(self._result_frame, bg=self.BG_CARD)
        col.pack(side="left", fill="both", expand=True, pady=10)

        self._result_status = tk.Label(col, text="STATUS",
                                       font=("Courier New", 7),
                                       fg=self.TEXT_DIM, bg=self.BG_CARD,
                                       anchor="w")
        self._result_status.pack(anchor="w")

        self._result_var = tk.StringVar(
            value="Masukkan string biner lalu klik ANALYZE")
        self._result_text = tk.Label(col, textvariable=self._result_var,
                                     font=("Segoe UI", 10, "bold"),
                                     fg=self.TEXT_DIM, bg=self.BG_CARD,
                                     wraplength=290, justify="left")
        self._result_text.pack(anchor="w")

    # ── Trace panel ──────────────────────────────────────────────
    def _build_trace_panel(self, parent):
        card = tk.Frame(parent, bg=self.BG_CARD,
                        highlightbackground=self.BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True, pady=(0, 8))

        hdr = tk.Frame(card, bg=self.BG_CARD)
        hdr.pack(fill="x", padx=14, pady=(10, 4))
        tk.Frame(hdr, bg=self.YELLOW, width=3, height=13).pack(
            side="left", padx=(0, 8))
        tk.Label(hdr, text="EXECUTION TRACE",
                 font=("Courier New", 9, "bold"),
                 fg=self.TEXT_DIM, bg=self.BG_CARD).pack(side="left")

        cols = ("Step", "σ", "State", "Keterangan")
        self.tree = ttk.Treeview(card, columns=cols, show="headings", height=9)

        sty = ttk.Style()
        sty.theme_use("clam")
        sty.configure("T.Treeview",
                       background="#0d1b2e", foreground=self.TEXT,
                       fieldbackground="#0d1b2e",
                       font=("Courier New", 9), rowheight=24)
        sty.configure("T.Treeview.Heading",
                       background=self.BG_CELL, foreground=self.YELLOW,
                       font=("Courier New", 9, "bold"), relief="flat")
        sty.map("T.Treeview",
                background=[("selected", self.BG_CELL)],
                foreground=[("selected", self.CYAN)])
        self.tree.configure(style="T.Treeview")

        self.tree.heading("Step",       text="#",          anchor="center")
        self.tree.heading("σ",          text="σ",          anchor="center")
        self.tree.heading("State",      text="State",      anchor="center")
        self.tree.heading("Keterangan", text="Keterangan", anchor="w")
        self.tree.column("Step",        width=35,  anchor="center")
        self.tree.column("σ",           width=35,  anchor="center")
        self.tree.column("State",       width=55,  anchor="center")
        self.tree.column("Keterangan",  width=240, anchor="w")

        sb = ttk.Scrollbar(card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True,
                       padx=(8, 0), pady=(0, 8))
        sb.pack(side="right", fill="y", pady=(0, 8))

    # ── Quick-test panel ─────────────────────────────────────────
    def _build_quicktest_panel(self, parent):
        card = tk.Frame(parent, bg=self.BG_CARD,
                        highlightbackground=self.BORDER, highlightthickness=1)
        card.pack(fill="x", pady=(0, 8))

        hdr = tk.Frame(card, bg=self.BG_CARD)
        hdr.pack(fill="x", padx=14, pady=(10, 6))
        tk.Frame(hdr, bg=self.ORANGE, width=3, height=13).pack(
            side="left", padx=(0, 8))
        tk.Label(hdr, text="QUICK TEST",
                 font=("Courier New", 9, "bold"),
                 fg=self.TEXT_DIM, bg=self.BG_CARD).pack(side="left")

        examples = [
            [("1",True),("01",True),("101",True),("0101",True)],
            [("0",False),("00",False),("100",False),("010010",False)],
        ]
        for row_data in examples:
            row = tk.Frame(card, bg=self.BG_CARD)
            row.pack(fill="x", padx=14, pady=(0, 4))
            for s, ok in row_data:
                fg  = self.GREEN if ok else self.RED
                tag = "✓" if ok else "✗"
                b = tk.Button(row, text=f"{tag} {s}",
                              font=("Courier New", 10, "bold"),
                              bg=self.BG_CELL, fg=fg, relief="flat",
                              padx=8, pady=3, cursor="hand2",
                              highlightbackground=fg, highlightthickness=1,
                              command=lambda v=s: self._quick(v))
                b.bind("<Enter>", lambda e, b=b, c=fg: b.config(bg=c, fg=self.BG))
                b.bind("<Leave>", lambda e, b=b, c=fg: b.config(bg=self.BG_CELL, fg=c))
                b.pack(side="left", padx=(0, 4))
        tk.Frame(card, bg=self.BG_CARD, height=8).pack()

    # ── Transition table ──────────────────────────────────────────
    def _build_transition_table(self, parent):
        hdr = tk.Frame(parent, bg=self.BG_CARD)
        hdr.pack(fill="x", padx=14, pady=(10, 6))
        tk.Frame(hdr, bg=self.CYAN, width=3, height=13).pack(
            side="left", padx=(0, 8))
        tk.Label(hdr, text="TRANSITION TABLE  δ(q, σ)",
                 font=("Courier New", 9, "bold"),
                 fg=self.TEXT_DIM, bg=self.BG_CARD).pack(side="left")

        tbl = tk.Frame(parent, bg=self.BG_CARD)
        tbl.pack(fill="x", padx=14, pady=(0, 12))

        col_specs = [
            ("State q", 9), ("δ(q,0)", 8), ("δ(q,1)", 8),
            ("Type", 12),   ("Description", 32),
        ]
        for ci, (h, w) in enumerate(col_specs):
            tk.Label(tbl, text=h, font=("Courier New", 9, "bold"),
                     fg=self.YELLOW, bg="#050c18",
                     width=w, padx=4, pady=4,
                     relief="flat").grid(row=0, column=ci,
                                         padx=1, pady=(0,2), sticky="ew")

        types = {"S":"Start","A":"Normal","B":"Accept  ◎","C":"Dead  ✗"}
        descs = {"S":"Initial — belum membaca input",
                 "A":"Terakhir '0', tunggu '1'",
                 "B":"Terakhir '1' → diterima",
                 "C":"Trap — ada substring '00'"}

        for r, st in enumerate(STATES):
            for ci, (val, (_, w)) in enumerate(zip(
                [st, TRANSITION_TABLE[st]["0"], TRANSITION_TABLE[st]["1"],
                 types[st], descs[st]], col_specs)):
                tk.Label(tbl, text=val, font=("Courier New", 9),
                         fg=self.S_STROKE[st], bg=self.S_FILL[st],
                         width=w, padx=4, pady=5,
                         relief="flat").grid(row=r+1, column=ci,
                                              padx=1, pady=1, sticky="ew")

    # ── Button factory ────────────────────────────────────────────
    def _make_btn(self, parent, text, color, cmd, width=None):
        kw = dict(font=("Courier New", 10, "bold"),
                  bg=self.BG_CELL, fg=color, relief="flat",
                  padx=10, pady=6, cursor="hand2",
                  highlightbackground=color, highlightthickness=1,
                  command=cmd)
        if width:
            kw["width"] = width
        b = tk.Button(parent, text=text, **kw)
        b.bind("<Enter>", lambda e, b=b, c=color: b.config(bg=c, fg=self.BG))
        b.bind("<Leave>", lambda e, b=b, c=color: b.config(bg=self.BG_CELL, fg=c))
        return b

    # ===========================================================
    # DIAGRAM DRAWING
    # Three-pass approach:
    #   Pass 1 – background + grid
    #   Pass 2 – node circles (so arrows can be drawn on top)
    #   Pass 3 – all arrows (lines, arrowheads, labels) on top of nodes
    # This guarantees arrowheads are never buried by node fills.
    # ===========================================================
    def _get_wh(self):
        self.canvas.update_idletasks()
        return (self.canvas.winfo_width()  or 520,
                self.canvas.winfo_height() or 390)

    def _draw_diagram(self, highlight=None, active_edge=None):
        c = self.canvas
        c.delete("all")
        W, H = self._get_wh()
        cx, cy = W / 2, H / 2

        R   = max(26, min(W, H) * 0.072)   # node radius
        sep = max(55, R * 2.1)             # A↔B curve lateral separation

        # Node positions (match the problem diagram layout)
        pad = min(W, H) * 0.13
        pos = {
            "S": (pad + R,   cy),
            "A": (cx,        cy - min(H, 190) * 0.46),
            "B": (cx,        cy + min(H, 190) * 0.46),
            "C": (W-pad-R,   cy - min(H, 190) * 0.46),
        }

        # Pass 1: background grid
        for x in range(0, W, 30):
            c.create_line(x, 0, x, H, fill="#0c1520", width=1)
        for y in range(0, H, 30):
            c.create_line(0, y, W, y, fill="#0c1520", width=1)

        # "start" entry arrow
        sx0, sy0 = pos["S"]
        c.create_line(sx0-R-48, sy0, sx0-R-1, sy0,
                      arrow=tk.LAST, fill=self.CYAN, width=2,
                      arrowshape=(11, 14, 4))
        c.create_text(sx0-R-28, sy0-13, text="start",
                      font=("Courier New", 9), fill=self.CYAN_DIM)

        # Pass 2: draw nodes first
        self._draw_nodes(c, pos, R, highlight)

        # Pass 3: draw arrows on top of nodes
        self._draw_arrows(c, pos, R, sep, active_edge)

        # Legend
        ly = H - 20
        for sym, col, txt, dx in [
            ("◉", self.GREEN, "Accept state",    0),
            ("◎", self.RED,   "Dead/Trap state", 130),
            ("◈", self.CYAN,  "Active state",    260),
        ]:
            c.create_text(14+dx, ly, text=sym,
                          font=("Segoe UI", 10), fill=col, anchor="w")
            c.create_text(30+dx, ly, text=txt,
                          font=("Courier New", 9),
                          fill=self.TEXT_DIM, anchor="w")

    # ── Pass 2: node circles ──────────────────────────────────────
    def _draw_nodes(self, c, pos, R, highlight):
        for state, (x, y) in pos.items():
            is_hl  = (state == highlight)
            fill   = self.S_FILL[state]
            stroke = self.S_STROKE[state]

            if is_hl:
                c.create_oval(x-R-10, y-R-10, x+R+10, y+R+10,
                              outline=stroke, width=1, dash=(3, 4))
                fill = "#162840" if state != "C" else "#321020"

            c.create_oval(x-R+3, y-R+3, x+R+3, y+R+3,
                          fill="#040810", outline="")            # shadow
            c.create_oval(x-R, y-R, x+R, y+R,
                          fill=fill, outline=stroke,
                          width=3 if is_hl else 2)

            if state in ACCEPT_STATES:                          # inner ring
                c.create_oval(x-R+6, y-R+6, x+R-6, y+R-6,
                              outline=stroke, width=1)

            if state == "C":                                    # dead ×
                d = R * 0.32
                c.create_line(x-d, y-d, x+d, y+d, fill=self.RED, width=1)
                c.create_line(x+d, y-d, x-d, y+d, fill=self.RED, width=1)

            c.create_text(x, y, text=state,
                          font=("Courier New", int(R*0.68), "bold"),
                          fill="#ffffff" if is_hl else stroke)

            names = {"S":"START","A":"STATE A","B":"ACCEPT","C":"DEAD"}
            c.create_text(x, y+R+13, text=names[state],
                          font=("Courier New", 7),
                          fill=stroke if is_hl else self.TEXT_DIM)

    # ── Pass 3: all arrows ────────────────────────────────────────
    def _draw_arrows(self, c, pos, R, sep, active_edge):
        def act(f, t):
            return active_edge == (f, t)

        Sx,Sy = pos["S"];  Ax,Ay = pos["A"]
        Bx,By = pos["B"];  Cx,Cy = pos["C"]

        self._straight(c, Sx,Sy, Ax,Ay, "0", R, act("S","A"))  # S→A
        self._straight(c, Sx,Sy, Bx,By, "1", R, act("S","B"))  # S→B
        self._straight(c, Ax,Ay, Cx,Cy, "0", R, act("A","C"))  # A→C

        mid_y = (Ay + By) / 2
        self._curved(c, Ax,Ay, Bx,By,                           # A→B  (right)
                     (Ax+Bx)/2 + sep, mid_y, "1", R, act("A","B"))
        self._curved(c, Bx,By, Ax,Ay,                           # B→A  (left)
                     (Ax+Bx)/2 - sep, mid_y, "0", R, act("B","A"))

        self._loop(c, Bx, By, 270, "1",   R, act("B","B"))     # B→B
        self._loop(c, Cx, Cy,  90, "0,1", R, act("C","C"))     # C→C

    # ── Straight arrow ────────────────────────────────────────────
    def _straight(self, c, x1,y1, x2,y2, label, R, active):
        col, lcol, lw = self._colours(active)
        dx,dy = x2-x1, y2-y1
        dist  = math.hypot(dx,dy) or 1
        ux,uy = dx/dist, dy/dist
        sx,sy = x1+ux*(R+1), y1+uy*(R+1)  # start on src edge
        ex,ey = x2-ux*(R+1), y2-uy*(R+1)  # end   on dst edge

        c.create_line(sx,sy, ex,ey, fill=col, width=lw)
        self._head(c, ex,ey, ux,uy, col)
        mx,my = (sx+ex)/2, (sy+ey)/2
        self._pill(c, mx-uy*20, my+ux*20, label, col, lcol)

    # ── Curved (quadratic bezier) arrow ───────────────────────────
    def _curved(self, c, x1,y1, x2,y2, ctrl_x,ctrl_y, label, R, active):
        col, lcol, lw = self._colours(active)

        # clip start → source circle edge toward ctrl
        d0 = math.hypot(ctrl_x-x1, ctrl_y-y1) or 1
        sx = x1 + (ctrl_x-x1)/d0*(R+1)
        sy = y1 + (ctrl_y-y1)/d0*(R+1)

        # clip end → dest circle edge toward ctrl
        d1 = math.hypot(ctrl_x-x2, ctrl_y-y2) or 1
        ex = x2 + (ctrl_x-x2)/d1*(R+1)
        ey = y2 + (ctrl_y-y2)/d1*(R+1)

        c.create_line(sx,sy, ctrl_x,ctrl_y, ex,ey,
                      smooth=True, fill=col, width=lw)

        # arrowhead: direction from ctrl toward end node
        udx = (x2-ctrl_x)/d1;  udy = (y2-ctrl_y)/d1
        self._head(c, ex,ey, udx,udy, col)

        # label at bezier midpoint  t=0.5 → 0.25P0 + 0.5ctrl + 0.25P2
        lx = 0.25*sx + 0.5*ctrl_x + 0.25*ex
        ly = 0.25*sy + 0.5*ctrl_y + 0.25*ey
        self._pill(c, lx, ly, label, col, lcol)

    # ── Self-loop arrow ───────────────────────────────────────────
    def _loop(self, c, nx,ny, angle_deg, label, R, active):
        col, lcol, lw = self._colours(active)
        r_lp = R * 0.84
        dist = R + r_lp * 1.4
        rad  = math.radians(angle_deg)
        clx  = nx + math.cos(rad)*dist
        cly  = ny - math.sin(rad)*dist

        c.create_oval(clx-r_lp, cly-r_lp, clx+r_lp, cly+r_lp,
                      outline=col, width=lw)

        # arrowhead at re-entry point
        ea  = math.radians(angle_deg + 180 + 22)
        ax  = clx + math.cos(ea)*r_lp
        ay  = cly - math.sin(ea)*r_lp
        dax,day = nx-ax, ny-ay
        da  = math.hypot(dax,day) or 1
        self._head(c, ax,ay, dax/da, day/da, col)

        # label outside the oval
        self._pill(c,
                   clx + math.cos(rad)*(r_lp+18),
                   cly - math.sin(rad)*(r_lp+18),
                   label, col, lcol)

    # ── Colour helper ─────────────────────────────────────────────
    def _colours(self, active):
        if active:
            return self.CYAN, self.CYAN, 2.4
        return "#5a7a9a", self.YELLOW, 1.7

    # ── Arrowhead (filled triangle, wings outside circle) ─────────
    def _head(self, c, tip_x,tip_y, ux,uy, col):
        hl, hw = 12, 5
        px,py  = -uy, ux
        bx,by  = tip_x - ux*hl, tip_y - uy*hl
        c.create_polygon(tip_x,      tip_y,
                         bx-px*hw,   by-py*hw,
                         bx+px*hw,   by+py*hw,
                         fill=col, outline=col)

    # ── Edge-label pill ───────────────────────────────────────────
    def _pill(self, c, x,y, text, border_col, text_col):
        pad = max(12, len(text)*9 + 10)
        c.create_rectangle(x-pad, y-12, x+pad, y+12,
                            fill=self.BG, outline=border_col, width=1)
        c.create_text(x, y, text=text,
                      font=("Courier New", 11, "bold"), fill=text_col)

    # ===========================================================
    # IDLE PULSE  (updates only one canvas item → no flicker)
    # ===========================================================
    def _tick_pulse(self):
        if self._highlighted is None and self._animation_step == -1:
            self._pulse_phase = (self._pulse_phase + 0.05) % (2*math.pi)
            self.canvas.delete("pulse")
            W, H = self._get_wh()
            R   = max(26, min(W,H)*0.072)
            pad = min(W,H)*0.13
            sx, sy = pad + R, H/2
            gr  = R + 6 + 4*math.sin(self._pulse_phase)
            self.canvas.create_oval(sx-gr, sy-gr, sx+gr, sy+gr,
                                    outline=self.CYAN, width=1,
                                    dash=(2,4), tags="pulse")
        self.root.after(60, self._tick_pulse)

    # ===========================================================
    # FSM LOGIC
    # ===========================================================
    def run_fsm(self):
        self._stop_anim()
        inp = self.entry.get().strip()
        accepted, steps, reason = simulate_fsm(inp)
        self._current_steps = steps

        if not steps:
            self._set_result(reason, ok=None)
            self._draw_diagram()
            return

        self._set_result(reason, ok=accepted)
        self._fill_trace(steps)
        self._highlighted = steps[-1][1]
        self._draw_diagram(highlight=self._highlighted)

    def run_step(self):
        self._stop_anim()
        inp = self.entry.get().strip()
        accepted, steps, reason = simulate_fsm(inp)
        if not steps:
            self._set_result(reason, ok=None)
            return

        self._current_steps  = steps
        self._animation_step = 0
        self._anim_accepted  = accepted
        self._anim_reason    = reason
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._set_result("▶  Animasi berjalan...", ok=None)
        self._result_icon.config(text="◈", fg=self.PURPLE)
        self._next_step()

    def _next_step(self):
        if self._animation_step >= len(self._current_steps):
            self._set_result(self._anim_reason, ok=self._anim_accepted)
            self._animation_step = -1
            self._active_edge    = None
            return

        i = self._animation_step
        char, state, desc = self._current_steps[i]
        self.tree.insert("", "end", values=(i, char, state, desc))

        edge = (self._current_steps[i-1][1], state) if i > 0 else None
        self._highlighted = state
        self._active_edge = edge
        self._draw_diagram(highlight=state, active_edge=edge)

        kids = self.tree.get_children()
        if kids:
            self.tree.see(kids[-1])

        self._animation_step += 1
        self._animation_id = self.root.after(700, self._next_step)

    def _stop_anim(self):
        if self._animation_id:
            self.root.after_cancel(self._animation_id)
            self._animation_id = None
        self._animation_step = -1
        self._active_edge    = None

    def clear_all(self):
        self._stop_anim()
        self._highlighted = None
        self.entry.delete(0, tk.END)
        self._char_var.set("0 karakter")
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._set_result("Masukkan string biner lalu klik ANALYZE", ok=None)
        self._draw_diagram()

    def _quick(self, s):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, s)
        self._char_var.set(f"{len(s)} karakter")
        self.run_fsm()

    def _on_key(self, event=None):
        n = len(self.entry.get())
        self._char_var.set(
            f"{n} karakter  ·  Enter ↵ untuk analyze" if n else "0 karakter")

    def _fill_trace(self, steps):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, (ch, st, desc) in enumerate(steps):
            self.tree.insert("", "end", values=(i, ch, st, desc))

    def _set_result(self, text, ok):
        self._result_var.set(text)
        if ok is True:
            self._result_icon.config(text="✓", fg=self.GREEN,    bg=self.BG_CARD)
            self._result_status.config(text="DITERIMA",          fg=self.GREEN)
            self._result_text.config(fg=self.GREEN)
            self._result_frame.config(highlightbackground=self.GREEN)
        elif ok is False:
            self._result_icon.config(text="✗", fg=self.RED,      bg=self.BG_CARD)
            self._result_status.config(text="DITOLAK",           fg=self.RED)
            self._result_text.config(fg=self.RED)
            self._result_frame.config(highlightbackground=self.RED)
        else:
            self._result_icon.config(text="◈", fg=self.TEXT_DIM, bg=self.BG_CARD)
            self._result_status.config(text="STATUS",            fg=self.TEXT_DIM)
            self._result_text.config(fg=self.TEXT_DIM)
            self._result_frame.config(highlightbackground=self.BORDER)


# =============================================================
# ENTRY POINT
# =============================================================
if __name__ == "__main__":
    root = tk.Tk()
    FSMApp(root)
    root.mainloop()