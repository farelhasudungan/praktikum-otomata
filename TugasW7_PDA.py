import sys
import tkinter as tk
from collections import deque
from dataclasses import dataclass, field
from tkinter import messagebox, ttk


EPS = "eps"


@dataclass(frozen=True)
class Transition:
    from_state: str
    read_symbol: str
    stack_top: str
    to_state: str
    push_symbols: str


@dataclass(frozen=True)
class TraceRow:
    state: str
    index: int
    remaining: str
    stack: str
    action: str


@dataclass(frozen=True)
class SimulationResult:
    accepted: bool
    reason: str
    trace: tuple[TraceRow, ...]
    explored: int


@dataclass
class PDA:
    name: str
    description: str
    states: list[str]
    alphabet: list[str]
    stack_alphabet: list[str]
    start_state: str
    start_stack: str
    final_states: list[str]
    acceptance_mode: str
    transitions: list[Transition]
    accepted_examples: list[str] = field(default_factory=list)
    rejected_examples: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Configuration:
    state: str
    index: int
    stack: tuple[str, ...]


def normalize_symbol(value: str) -> str:
    value = value.strip()
    if not value:
        return EPS
    if value.lower() in {"eps", "epsilon", "e", "lambda"}:
        return EPS
    return value


def parse_list(value: str) -> list[str]:
    parts = value.replace("\n", ",").split(",")
    return [part.strip() for part in parts if part.strip()]


def list_text(values: list[str]) -> str:
    return ", ".join(values)


def stack_to_tuple(value: str) -> tuple[str, ...]:
    value = normalize_symbol(value)
    if value == EPS:
        return tuple()
    if "," in value:
        return tuple(parse_list(value))
    return tuple(ch for ch in value.replace(" ", ""))


def format_stack(stack: tuple[str, ...]) -> str:
    return "".join(stack) if stack else EPS


def format_remaining(input_string: str, index: int) -> str:
    remaining = input_string[index:]
    return remaining if remaining else EPS


def transition_action(t: Transition) -> str:
    return (
        f"{t.from_state} -- read={t.read_symbol}, "
        f"top={t.stack_top}, push={t.push_symbols} -> {t.to_state}"
    )


def is_accepting(pda: PDA, config: Configuration, input_string: str) -> bool:
    if config.index != len(input_string):
        return False
    if pda.acceptance_mode == "empty_stack":
        return len(config.stack) == 0
    return config.state in set(pda.final_states)


def transition_matches(t: Transition, config: Configuration, input_string: str) -> bool:
    if t.from_state != config.state:
        return False

    if t.read_symbol != EPS:
        if config.index >= len(input_string):
            return False
        if input_string[config.index] != t.read_symbol:
            return False

    if t.stack_top == EPS:
        return True

    return bool(config.stack) and config.stack[0] == t.stack_top


def apply_transition(t: Transition, config: Configuration) -> Configuration:
    next_index = config.index + (0 if t.read_symbol == EPS else 1)

    if t.stack_top == EPS:
        rest_stack = config.stack
    else:
        rest_stack = config.stack[1:]

    pushed = stack_to_tuple(t.push_symbols)
    next_stack = pushed + rest_stack
    return Configuration(t.to_state, next_index, next_stack)


def validate_input_symbols(pda: PDA, input_string: str) -> str | None:
    alphabet = set(pda.alphabet)
    for ch in input_string:
        if ch not in alphabet:
            return ch
    return None


def simulate_npda(pda: PDA, input_string: str, max_steps: int = 5000) -> SimulationResult:
    invalid = validate_input_symbols(pda, input_string)
    start_config = Configuration(
        pda.start_state,
        0,
        stack_to_tuple(pda.start_stack),
    )
    start_row = TraceRow(
        start_config.state,
        start_config.index,
        format_remaining(input_string, start_config.index),
        format_stack(start_config.stack),
        "Start configuration",
    )

    if invalid is not None:
        return SimulationResult(
            False,
            f"Rejected: simbol input '{invalid}' tidak ada pada alphabet PDA.",
            (start_row,),
            0,
        )

    queue = deque([(start_config, (start_row,))])
    visited = {start_config}
    explored = 0
    last_trace = (start_row,)

    while queue and explored < max_steps:
        config, trace = queue.popleft()
        last_trace = trace
        explored += 1

        if is_accepting(pda, config, input_string):
            mode = "empty stack" if pda.acceptance_mode == "empty_stack" else "final state"
            return SimulationResult(
                True,
                f"Accepted: input habis dan syarat {mode} terpenuhi.",
                trace,
                explored,
            )

        for transition in pda.transitions:
            if not transition_matches(transition, config, input_string):
                continue

            next_config = apply_transition(transition, config)
            if next_config in visited:
                continue

            visited.add(next_config)
            next_row = TraceRow(
                next_config.state,
                next_config.index,
                format_remaining(input_string, next_config.index),
                format_stack(next_config.stack),
                transition_action(transition),
            )
            queue.append((next_config, trace + (next_row,)))

    if explored >= max_steps:
        reason = (
            "Rejected: batas simulasi tercapai. "
            "Periksa kemungkinan epsilon-loop pada transisi."
        )
    else:
        reason = "Rejected: tidak ada jalur transisi yang mencapai konfigurasi accept."

    return SimulationResult(False, reason, last_trace, explored)


def make_presets() -> dict[str, PDA]:
    anbn = PDA(
        name="L = { a^n b^n | n >= 1 }",
        description="Menerima jumlah a dan b yang sama, semua a muncul sebelum b.",
        states=["q0", "q1", "qf"],
        alphabet=["a", "b"],
        stack_alphabet=["A", "$"],
        start_state="q0",
        start_stack="$",
        final_states=["qf"],
        acceptance_mode="final_state",
        transitions=[
            Transition("q0", "a", "$", "q0", "A$"),
            Transition("q0", "a", "A", "q0", "AA"),
            Transition("q0", "b", "A", "q1", EPS),
            Transition("q1", "b", "A", "q1", EPS),
            Transition("q1", EPS, "$", "qf", "$"),
        ],
        accepted_examples=["ab", "aabb", "aaabbb"],
        rejected_examples=["", "aab", "abb", "ba"],
    )

    balanced_parentheses = PDA(
        name="Balanced Parentheses",
        description="Menerima string kurung yang seimbang.",
        states=["q", "qf"],
        alphabet=["(", ")"],
        stack_alphabet=["X", "$"],
        start_state="q",
        start_stack="$",
        final_states=["qf"],
        acceptance_mode="final_state",
        transitions=[
            Transition("q", "(", "$", "q", "X$"),
            Transition("q", "(", "X", "q", "XX"),
            Transition("q", ")", "X", "q", EPS),
            Transition("q", EPS, "$", "qf", "$"),
        ],
        accepted_examples=["", "()", "(())", "(()())"],
        rejected_examples=["(()", "())(", ")("],
    )

    palindrome = PDA(
        name="Palindrome {a,b}",
        description="Menerima palindrome sederhana atas alphabet {a,b}.",
        states=["q_push", "q_pop", "qf"],
        alphabet=["a", "b"],
        stack_alphabet=["a", "b", "$"],
        start_state="q_push",
        start_stack="$",
        final_states=["qf"],
        acceptance_mode="final_state",
        transitions=[
            Transition("q_push", "a", "$", "q_push", "a$"),
            Transition("q_push", "a", "a", "q_push", "aa"),
            Transition("q_push", "a", "b", "q_push", "ab"),
            Transition("q_push", "b", "$", "q_push", "b$"),
            Transition("q_push", "b", "a", "q_push", "ba"),
            Transition("q_push", "b", "b", "q_push", "bb"),
            Transition("q_push", EPS, "$", "q_pop", "$"),
            Transition("q_push", EPS, "a", "q_pop", "a"),
            Transition("q_push", EPS, "b", "q_pop", "b"),
            Transition("q_push", "a", "$", "q_pop", "$"),
            Transition("q_push", "a", "a", "q_pop", "a"),
            Transition("q_push", "a", "b", "q_pop", "b"),
            Transition("q_push", "b", "$", "q_pop", "$"),
            Transition("q_push", "b", "a", "q_pop", "a"),
            Transition("q_push", "b", "b", "q_pop", "b"),
            Transition("q_pop", "a", "a", "q_pop", EPS),
            Transition("q_pop", "b", "b", "q_pop", EPS),
            Transition("q_pop", EPS, "$", "qf", "$"),
        ],
        accepted_examples=["", "a", "aa", "aba", "abba", "baab"],
        rejected_examples=["ab", "aab", "abab", "abb"],
    )

    return {preset.name: preset for preset in (anbn, balanced_parentheses, palindrome)}


PRESETS = make_presets()


class PDAApp:
    BG = "#101820"
    PANEL = "#17212b"
    SURFACE = "#1f2d3a"
    BORDER = "#314456"
    TEXT = "#e8eef4"
    MUTED = "#9caebb"
    ACCENT = "#4fd1c5"
    GREEN = "#66d977"
    RED = "#ff6b6b"
    YELLOW = "#ffd166"
    BLUE = "#7aa2f7"
    PURPLE = "#c099ff"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("PDA Simulator - Pushdown Automata")
        self.root.geometry("1280x820")
        self.root.minsize(1050, 700)
        self.root.configure(bg=self.BG)

        self.current_result: SimulationResult | None = None
        self.animation_index = 0
        self.animation_job = None

        self._build_ui()
        self._load_preset(next(iter(PRESETS)))

    def _build_ui(self):
        self._configure_style()
        self._build_header()

        main = tk.Frame(self.root, bg=self.BG)
        main.pack(fill="both", expand=True, padx=12, pady=10)
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)

        left = tk.Frame(main, bg=self.BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        right = tk.Frame(main, bg=self.BG)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        self._build_definition_panel(left)
        self._build_transition_panel(left)
        self._build_simulation_panel(right)
        self._build_trace_panel(right)

        self.status_var = tk.StringVar(value="Ready.")
        status = tk.Label(
            self.root,
            textvariable=self.status_var,
            bg=self.PANEL,
            fg=self.MUTED,
            font=("Consolas", 9),
            anchor="w",
            padx=12,
            pady=4,
        )
        status.pack(fill="x", side="bottom")

    def _configure_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=self.SURFACE,
            foreground=self.TEXT,
            fieldbackground=self.SURFACE,
            rowheight=25,
            borderwidth=0,
            font=("Consolas", 9),
        )
        style.configure(
            "Treeview.Heading",
            background=self.PANEL,
            foreground=self.YELLOW,
            relief="flat",
            font=("Consolas", 9, "bold"),
        )
        style.map(
            "Treeview",
            background=[("selected", self.BLUE)],
            foreground=[("selected", "#081018")],
        )
        style.configure(
            "TCombobox",
            fieldbackground=self.SURFACE,
            background=self.SURFACE,
            foreground=self.TEXT,
            arrowcolor=self.TEXT,
        )

    def _build_header(self):
        top = tk.Frame(self.root, bg=self.PANEL)
        top.pack(fill="x")
        tk.Frame(top, bg=self.ACCENT, height=3).pack(fill="x")

        row = tk.Frame(top, bg=self.PANEL)
        row.pack(fill="x", padx=16, pady=12)
        tk.Label(
            row,
            text="PDA SIMULATOR",
            bg=self.PANEL,
            fg=self.ACCENT,
            font=("Consolas", 18, "bold"),
        ).pack(side="left")
        tk.Label(
            row,
            text="Pushdown Automata - Accepted / Rejected checker",
            bg=self.PANEL,
            fg=self.MUTED,
            font=("Consolas", 10),
        ).pack(side="left", padx=14)

    def _build_definition_panel(self, parent):
        card = self._card(parent)
        card.pack(fill="x", pady=(0, 8))
        self._section_title(card, "PDA DEFINITION", self.ACCENT)

        preset_row = tk.Frame(card, bg=self.PANEL)
        preset_row.pack(fill="x", padx=12, pady=(2, 8))
        tk.Label(preset_row, text="Preset", **self._label_kw()).pack(side="left")
        self.preset_var = tk.StringVar()
        self.preset_combo = ttk.Combobox(
            preset_row,
            textvariable=self.preset_var,
            values=list(PRESETS.keys()),
            state="readonly",
            width=34,
        )
        self.preset_combo.pack(side="left", padx=(8, 6))
        self._button(preset_row, "Load Preset", self._load_selected_preset, self.BLUE).pack(
            side="left", padx=3
        )
        self._button(preset_row, "Reset Preset", self._reset_preset, self.PURPLE).pack(
            side="left", padx=3
        )

        fields = tk.Frame(card, bg=self.PANEL)
        fields.pack(fill="x", padx=12, pady=(0, 10))
        for col in range(4):
            fields.columnconfigure(col, weight=1)

        self.states_var = tk.StringVar()
        self.alphabet_var = tk.StringVar()
        self.stack_alphabet_var = tk.StringVar()
        self.start_state_var = tk.StringVar()
        self.start_stack_var = tk.StringVar()
        self.final_states_var = tk.StringVar()
        self.acceptance_var = tk.StringVar(value="Final state")
        self.max_steps_var = tk.IntVar(value=5000)

        self._entry_field(fields, "States", self.states_var, 0, 0)
        self._entry_field(fields, "Input alphabet", self.alphabet_var, 0, 1)
        self._entry_field(fields, "Stack alphabet", self.stack_alphabet_var, 0, 2)
        self._entry_field(fields, "Start state", self.start_state_var, 1, 0)
        self._entry_field(fields, "Start stack", self.start_stack_var, 1, 1)
        self._entry_field(fields, "Final states", self.final_states_var, 1, 2)

        mode_frame = tk.Frame(fields, bg=self.PANEL)
        mode_frame.grid(row=1, column=3, sticky="ew", padx=5, pady=4)
        tk.Label(mode_frame, text="Accept by", **self._label_kw()).pack(anchor="w")
        ttk.Combobox(
            mode_frame,
            textvariable=self.acceptance_var,
            values=["Final state", "Empty stack"],
            state="readonly",
            width=16,
        ).pack(fill="x")

        steps_frame = tk.Frame(fields, bg=self.PANEL)
        steps_frame.grid(row=0, column=3, sticky="ew", padx=5, pady=4)
        tk.Label(steps_frame, text="Max steps", **self._label_kw()).pack(anchor="w")
        tk.Spinbox(
            steps_frame,
            from_=50,
            to=100000,
            increment=100,
            textvariable=self.max_steps_var,
            bg=self.SURFACE,
            fg=self.TEXT,
            insertbackground=self.ACCENT,
            relief="flat",
            font=("Consolas", 10),
        ).pack(fill="x")

        self.description_var = tk.StringVar()
        tk.Label(
            card,
            textvariable=self.description_var,
            bg=self.PANEL,
            fg=self.MUTED,
            font=("Consolas", 9),
            anchor="w",
            wraplength=760,
            justify="left",
        ).pack(fill="x", padx=12, pady=(0, 10))

    def _build_transition_panel(self, parent):
        card = self._card(parent)
        card.pack(fill="both", expand=True)
        self._section_title(card, "TRANSITION EDITOR", self.YELLOW)

        cols = ("from", "read", "top", "to", "push")
        self.transition_tree = ttk.Treeview(card, columns=cols, show="headings", height=11)
        headers = {
            "from": "From",
            "read": "Read",
            "top": "Stack Top",
            "to": "To",
            "push": "Push",
        }
        widths = {"from": 115, "read": 70, "top": 90, "to": 115, "push": 90}
        for col in cols:
            self.transition_tree.heading(col, text=headers[col])
            self.transition_tree.column(col, width=widths[col], anchor="center")
        self.transition_tree.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        self.transition_tree.bind("<<TreeviewSelect>>", self._on_transition_selected)

        editor = tk.Frame(card, bg=self.PANEL)
        editor.pack(fill="x", padx=12, pady=(0, 10))
        for col in range(5):
            editor.columnconfigure(col, weight=1)

        self.tr_from_var = tk.StringVar()
        self.tr_read_var = tk.StringVar()
        self.tr_top_var = tk.StringVar()
        self.tr_to_var = tk.StringVar()
        self.tr_push_var = tk.StringVar()

        self._entry_field(editor, "From", self.tr_from_var, 0, 0)
        self._entry_field(editor, "Read", self.tr_read_var, 0, 1)
        self._entry_field(editor, "Top", self.tr_top_var, 0, 2)
        self._entry_field(editor, "To", self.tr_to_var, 0, 3)
        self._entry_field(editor, "Push", self.tr_push_var, 0, 4)

        buttons = tk.Frame(card, bg=self.PANEL)
        buttons.pack(fill="x", padx=12, pady=(0, 12))
        self._button(buttons, "Add Transition", self._add_transition, self.GREEN).pack(
            side="left", padx=(0, 6)
        )
        self._button(buttons, "Update Selected", self._update_transition, self.BLUE).pack(
            side="left", padx=6
        )
        self._button(buttons, "Delete Selected", self._delete_transition, self.RED).pack(
            side="left", padx=6
        )
        self._button(buttons, "Clear Fields", self._clear_transition_fields, self.PURPLE).pack(
            side="left", padx=6
        )

        note = (
            "Use 'eps' for epsilon. Stack top is displayed on the left, "
            "for example A$ means A is on top of $."
        )
        tk.Label(
            card,
            text=note,
            bg=self.PANEL,
            fg=self.MUTED,
            font=("Consolas", 8),
            anchor="w",
        ).pack(fill="x", padx=12, pady=(0, 10))

    def _build_simulation_panel(self, parent):
        card = self._card(parent)
        card.pack(fill="x", pady=(0, 8))
        self._section_title(card, "SIMULATION", self.ACCENT)

        input_row = tk.Frame(card, bg=self.PANEL)
        input_row.pack(fill="x", padx=12, pady=(0, 8))
        tk.Label(input_row, text="Input string", **self._label_kw()).pack(anchor="w")
        self.input_var = tk.StringVar()
        entry = tk.Entry(
            input_row,
            textvariable=self.input_var,
            bg=self.SURFACE,
            fg=self.TEXT,
            insertbackground=self.ACCENT,
            relief="flat",
            font=("Consolas", 18, "bold"),
            justify="center",
        )
        entry.pack(fill="x", ipady=8)
        entry.bind("<Return>", lambda _event: self.run_analyze())

        btns = tk.Frame(card, bg=self.PANEL)
        btns.pack(fill="x", padx=12, pady=(0, 10))
        self._button(btns, "Analyze", self.run_analyze, self.GREEN).pack(
            side="left", fill="x", expand=True, padx=(0, 4)
        )
        self._button(btns, "Step-by-step", self.run_step_by_step, self.PURPLE).pack(
            side="left", fill="x", expand=True, padx=4
        )
        self._button(btns, "Clear", self.clear_simulation, self.RED).pack(
            side="left", fill="x", expand=True, padx=(4, 0)
        )

        self.result_status_var = tk.StringVar(value="STATUS")
        self.result_reason_var = tk.StringVar(value="Masukkan string lalu klik Analyze.")
        result = tk.Frame(card, bg=self.SURFACE, highlightbackground=self.BORDER, highlightthickness=1)
        result.pack(fill="x", padx=12, pady=(0, 10))
        self.result_status_label = tk.Label(
            result,
            textvariable=self.result_status_var,
            bg=self.SURFACE,
            fg=self.MUTED,
            font=("Consolas", 11, "bold"),
            anchor="w",
        )
        self.result_status_label.pack(fill="x", padx=10, pady=(8, 0))
        self.result_reason_label = tk.Label(
            result,
            textvariable=self.result_reason_var,
            bg=self.SURFACE,
            fg=self.TEXT,
            font=("Consolas", 10),
            anchor="w",
            justify="left",
            wraplength=420,
        )
        self.result_reason_label.pack(fill="x", padx=10, pady=(2, 8))

        self.quick_frame = tk.Frame(card, bg=self.PANEL)
        self.quick_frame.pack(fill="x", padx=12, pady=(0, 10))

    def _build_trace_panel(self, parent):
        card = self._card(parent)
        card.pack(fill="both", expand=True)
        self._section_title(card, "EXECUTION TRACE", self.YELLOW)

        cols = ("step", "state", "pos", "remaining", "stack", "action")
        self.trace_tree = ttk.Treeview(card, columns=cols, show="headings", height=16)
        headings = {
            "step": "#",
            "state": "State",
            "pos": "Index",
            "remaining": "Remaining",
            "stack": "Stack",
            "action": "Action",
        }
        widths = {
            "step": 40,
            "state": 80,
            "pos": 55,
            "remaining": 95,
            "stack": 95,
            "action": 260,
        }
        for col in cols:
            self.trace_tree.heading(col, text=headings[col])
            self.trace_tree.column(col, width=widths[col], anchor="center")
        self.trace_tree.column("action", anchor="w")
        self.trace_tree.pack(fill="both", expand=True, padx=(12, 0), pady=(0, 12), side="left")

        scrollbar = ttk.Scrollbar(card, orient="vertical", command=self.trace_tree.yview)
        self.trace_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", pady=(0, 12), padx=(0, 12))

    def _section_title(self, parent, text, color):
        row = tk.Frame(parent, bg=self.PANEL)
        row.pack(fill="x", padx=12, pady=(10, 8))
        tk.Frame(row, bg=color, width=4, height=16).pack(side="left", padx=(0, 8))
        tk.Label(
            row,
            text=text,
            bg=self.PANEL,
            fg=color,
            font=("Consolas", 10, "bold"),
        ).pack(side="left")

    def _card(self, parent):
        return tk.Frame(
            parent,
            bg=self.PANEL,
            highlightbackground=self.BORDER,
            highlightthickness=1,
        )

    def _label_kw(self):
        return {
            "bg": self.PANEL,
            "fg": self.MUTED,
            "font": ("Consolas", 9, "bold"),
            "anchor": "w",
        }

    def _entry_field(self, parent, label, variable, row, col):
        frame = tk.Frame(parent, bg=self.PANEL)
        frame.grid(row=row, column=col, sticky="ew", padx=5, pady=4)
        tk.Label(frame, text=label, **self._label_kw()).pack(anchor="w")
        tk.Entry(
            frame,
            textvariable=variable,
            bg=self.SURFACE,
            fg=self.TEXT,
            insertbackground=self.ACCENT,
            relief="flat",
            font=("Consolas", 10),
        ).pack(fill="x", ipady=3)

    def _button(self, parent, text, command, color):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=self.SURFACE,
            fg=color,
            activebackground=color,
            activeforeground="#081018",
            relief="flat",
            bd=0,
            padx=12,
            pady=7,
            cursor="hand2",
            font=("Consolas", 9, "bold"),
            highlightbackground=color,
            highlightthickness=1,
        )
        button.bind("<Enter>", lambda _e, b=button, c=color: b.config(bg=c, fg="#081018"))
        button.bind("<Leave>", lambda _e, b=button, c=color: b.config(bg=self.SURFACE, fg=c))
        return button

    def _load_selected_preset(self):
        self._load_preset(self.preset_var.get())

    def _reset_preset(self):
        selected = self.preset_var.get() or next(iter(PRESETS))
        self._load_preset(selected)
        self.status_var.set(f"Preset '{selected}' dimuat ulang.")

    def _load_preset(self, preset_name: str):
        if preset_name not in PRESETS:
            return
        pda = PRESETS[preset_name]
        self.preset_var.set(preset_name)
        self.description_var.set(pda.description)
        self.states_var.set(list_text(pda.states))
        self.alphabet_var.set(list_text(pda.alphabet))
        self.stack_alphabet_var.set(list_text(pda.stack_alphabet))
        self.start_state_var.set(pda.start_state)
        self.start_stack_var.set(pda.start_stack)
        self.final_states_var.set(list_text(pda.final_states))
        self.acceptance_var.set("Empty stack" if pda.acceptance_mode == "empty_stack" else "Final state")
        self._replace_transitions(pda.transitions)
        self._build_quick_tests(pda)
        self.clear_simulation(update_status=False)
        self.status_var.set(f"Preset aktif: {pda.name}")

    def _replace_transitions(self, transitions: list[Transition]):
        for item in self.transition_tree.get_children():
            self.transition_tree.delete(item)
        for transition in transitions:
            self.transition_tree.insert(
                "",
                "end",
                values=(
                    transition.from_state,
                    transition.read_symbol,
                    transition.stack_top,
                    transition.to_state,
                    transition.push_symbols,
                ),
            )

    def _build_quick_tests(self, pda: PDA):
        for child in self.quick_frame.winfo_children():
            child.destroy()

        tk.Label(
            self.quick_frame,
            text="Quick tests",
            bg=self.PANEL,
            fg=self.MUTED,
            font=("Consolas", 9, "bold"),
        ).pack(anchor="w", pady=(0, 4))

        row = tk.Frame(self.quick_frame, bg=self.PANEL)
        row.pack(fill="x")
        examples = [(value, True) for value in pda.accepted_examples]
        examples += [(value, False) for value in pda.rejected_examples]
        for value, should_accept in examples[:8]:
            label = value if value else "eps"
            color = self.GREEN if should_accept else self.RED
            self._button(
                row,
                label,
                lambda v=value: self._quick_test(v),
                color,
            ).pack(side="left", padx=(0, 4), pady=2)

    def _quick_test(self, value: str):
        self.input_var.set(value)
        self.run_analyze()

    def _transition_from_fields(self) -> Transition:
        return Transition(
            self.tr_from_var.get().strip(),
            normalize_symbol(self.tr_read_var.get()),
            normalize_symbol(self.tr_top_var.get()),
            self.tr_to_var.get().strip(),
            normalize_symbol(self.tr_push_var.get()),
        )

    def _add_transition(self):
        transition = self._transition_from_fields()
        if not transition.from_state or not transition.to_state:
            messagebox.showwarning("Input kurang", "From dan To state harus diisi.")
            return
        self.transition_tree.insert(
            "",
            "end",
            values=(
                transition.from_state,
                transition.read_symbol,
                transition.stack_top,
                transition.to_state,
                transition.push_symbols,
            ),
        )
        self.status_var.set("Transisi baru ditambahkan.")

    def _update_transition(self):
        selected = self.transition_tree.selection()
        if not selected:
            messagebox.showwarning("Tidak ada pilihan", "Pilih transisi yang ingin diupdate.")
            return
        transition = self._transition_from_fields()
        self.transition_tree.item(
            selected[0],
            values=(
                transition.from_state,
                transition.read_symbol,
                transition.stack_top,
                transition.to_state,
                transition.push_symbols,
            ),
        )
        self.status_var.set("Transisi terpilih diupdate.")

    def _delete_transition(self):
        selected = self.transition_tree.selection()
        if not selected:
            messagebox.showwarning("Tidak ada pilihan", "Pilih transisi yang ingin dihapus.")
            return
        for item in selected:
            self.transition_tree.delete(item)
        self._clear_transition_fields()
        self.status_var.set("Transisi terpilih dihapus.")

    def _clear_transition_fields(self):
        self.tr_from_var.set("")
        self.tr_read_var.set("")
        self.tr_top_var.set("")
        self.tr_to_var.set("")
        self.tr_push_var.set("")

    def _on_transition_selected(self, _event=None):
        selected = self.transition_tree.selection()
        if not selected:
            return
        values = self.transition_tree.item(selected[0], "values")
        if len(values) != 5:
            return
        self.tr_from_var.set(values[0])
        self.tr_read_var.set(values[1])
        self.tr_top_var.set(values[2])
        self.tr_to_var.set(values[3])
        self.tr_push_var.set(values[4])

    def collect_pda(self) -> PDA | None:
        states = parse_list(self.states_var.get())
        alphabet = parse_list(self.alphabet_var.get())
        stack_alphabet = parse_list(self.stack_alphabet_var.get())
        final_states = parse_list(self.final_states_var.get())
        start_state = self.start_state_var.get().strip()
        start_stack = normalize_symbol(self.start_stack_var.get())
        mode = "empty_stack" if self.acceptance_var.get() == "Empty stack" else "final_state"

        if not states or not alphabet or not stack_alphabet:
            messagebox.showerror("Definisi tidak valid", "States, alphabet, dan stack alphabet wajib diisi.")
            return None
        if start_state not in states:
            messagebox.showerror("Definisi tidak valid", "Start state harus ada di daftar states.")
            return None
        missing_finals = [state for state in final_states if state not in states]
        if mode == "final_state" and missing_finals:
            messagebox.showerror(
                "Definisi tidak valid",
                f"Final state tidak dikenal: {', '.join(missing_finals)}",
            )
            return None

        transitions = self._get_transition_rows()
        error = self._validate_transitions(states, alphabet, stack_alphabet, transitions)
        if error:
            messagebox.showerror("Transisi tidak valid", error)
            return None

        for symbol in stack_to_tuple(start_stack):
            if symbol not in stack_alphabet:
                messagebox.showerror(
                    "Definisi tidak valid",
                    f"Start stack memakai simbol '{symbol}' yang tidak ada di stack alphabet.",
                )
                return None

        return PDA(
            name="Custom PDA",
            description=self.description_var.get(),
            states=states,
            alphabet=alphabet,
            stack_alphabet=stack_alphabet,
            start_state=start_state,
            start_stack=start_stack,
            final_states=final_states,
            acceptance_mode=mode,
            transitions=transitions,
        )

    def _get_transition_rows(self) -> list[Transition]:
        transitions = []
        for item in self.transition_tree.get_children():
            values = self.transition_tree.item(item, "values")
            transitions.append(
                Transition(
                    str(values[0]).strip(),
                    normalize_symbol(str(values[1])),
                    normalize_symbol(str(values[2])),
                    str(values[3]).strip(),
                    normalize_symbol(str(values[4])),
                )
            )
        return transitions

    def _validate_transitions(
        self,
        states: list[str],
        alphabet: list[str],
        stack_alphabet: list[str],
        transitions: list[Transition],
    ) -> str | None:
        state_set = set(states)
        alphabet_set = set(alphabet)
        stack_set = set(stack_alphabet)

        for transition in transitions:
            if transition.from_state not in state_set:
                return f"From state '{transition.from_state}' tidak ada di daftar states."
            if transition.to_state not in state_set:
                return f"To state '{transition.to_state}' tidak ada di daftar states."
            if transition.read_symbol != EPS and transition.read_symbol not in alphabet_set:
                return f"Read symbol '{transition.read_symbol}' tidak ada di input alphabet."
            if transition.stack_top != EPS and transition.stack_top not in stack_set:
                return f"Stack top '{transition.stack_top}' tidak ada di stack alphabet."
            for symbol in stack_to_tuple(transition.push_symbols):
                if symbol not in stack_set:
                    return f"Push symbol '{symbol}' tidak ada di stack alphabet."
        return None

    def run_analyze(self):
        self._stop_animation()
        pda = self.collect_pda()
        if pda is None:
            return

        result = simulate_npda(pda, self.input_var.get(), self.max_steps_var.get())
        self.current_result = result
        self._show_result(result)
        self._fill_trace(result.trace)
        self.status_var.set(f"Explored {result.explored} configuration(s).")

    def run_step_by_step(self):
        self._stop_animation()
        pda = self.collect_pda()
        if pda is None:
            return

        result = simulate_npda(pda, self.input_var.get(), self.max_steps_var.get())
        self.current_result = result
        self._clear_trace()
        self.animation_index = 0
        self._set_pending_result()
        self.status_var.set("Animasi step-by-step berjalan...")
        self._animate_next_row()

    def _animate_next_row(self):
        if self.current_result is None:
            return
        trace = self.current_result.trace
        if self.animation_index >= len(trace):
            self._show_result(self.current_result)
            self.status_var.set(f"Explored {self.current_result.explored} configuration(s).")
            self.animation_job = None
            return

        self._insert_trace_row(self.animation_index, trace[self.animation_index])
        self.animation_index += 1
        self.animation_job = self.root.after(650, self._animate_next_row)

    def _stop_animation(self):
        if self.animation_job is not None:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None

    def _show_result(self, result: SimulationResult):
        if result.accepted:
            self.result_status_var.set("ACCEPTED")
            self.result_status_label.config(fg=self.GREEN)
            self.result_reason_label.config(fg=self.GREEN)
        else:
            self.result_status_var.set("REJECTED")
            self.result_status_label.config(fg=self.RED)
            self.result_reason_label.config(fg=self.RED)
        self.result_reason_var.set(result.reason)

    def _set_pending_result(self):
        self.result_status_var.set("RUNNING")
        self.result_reason_var.set("Menampilkan trace satu per satu...")
        self.result_status_label.config(fg=self.PURPLE)
        self.result_reason_label.config(fg=self.TEXT)

    def _fill_trace(self, trace: tuple[TraceRow, ...]):
        self._clear_trace()
        for index, row in enumerate(trace):
            self._insert_trace_row(index, row)

    def _insert_trace_row(self, index: int, row: TraceRow):
        self.trace_tree.insert(
            "",
            "end",
            values=(index, row.state, row.index, row.remaining, row.stack, row.action),
        )
        items = self.trace_tree.get_children()
        if items:
            self.trace_tree.see(items[-1])

    def _clear_trace(self):
        for item in self.trace_tree.get_children():
            self.trace_tree.delete(item)

    def clear_simulation(self, update_status=True):
        self._stop_animation()
        self.input_var.set("")
        self.current_result = None
        self._clear_trace()
        self.result_status_var.set("STATUS")
        self.result_reason_var.set("Masukkan string lalu klik Analyze.")
        self.result_status_label.config(fg=self.MUTED)
        self.result_reason_label.config(fg=self.TEXT)
        if update_status:
            self.status_var.set("Simulasi dibersihkan.")


def run_self_tests() -> int:
    failures = []

    for name, pda in PRESETS.items():
        for value in pda.accepted_examples:
            result = simulate_npda(pda, value)
            if not result.accepted:
                failures.append(f"{name}: expected accepted for {value!r}, got rejected")
        for value in pda.rejected_examples:
            result = simulate_npda(pda, value)
            if result.accepted:
                failures.append(f"{name}: expected rejected for {value!r}, got accepted")

    anbn = PRESETS["L = { a^n b^n | n >= 1 }"]
    invalid_result = simulate_npda(anbn, "abc")
    if invalid_result.accepted or "tidak ada pada alphabet" not in invalid_result.reason:
        failures.append("Invalid input symbol test failed for 'abc'")

    if failures:
        print("SELF TEST FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("SELF TEST PASSED")
    print(f"Preset tested: {len(PRESETS)}")
    return 0


def main():
    if "--test" in sys.argv:
        raise SystemExit(run_self_tests())

    root = tk.Tk()
    PDAApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
