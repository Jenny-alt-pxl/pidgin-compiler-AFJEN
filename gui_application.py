"""
AFJEN Compiler - graphical interface
CS4110 - Compiler Construction

Type or paste any amount of Yaoundé Pidgin / franc-anglais text and AFJEN gives you:
  * a translation into standard English or French
  * the words it found (lexical analysis) and how well they fit the LL(1) grammar (syntactic analysis)
  * the topic and intent (semantic analysis)
Nothing is ever refused: unknown words and informal fragments are analysed and simply flagged.
"""

import contextlib
import io
import os
import re
import sys
import tkinter as tk
import tkinter.font as tkfont
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))
sys.path.insert(0, os.path.join(HERE, "tests"))

import grammar
import userdict
from dictionary import WordBank, build_dictionary
from lexical_analyzer import TokenType
from parser import analyze_robust
from semantic_analyzer import SemanticAnalyzer
from test_cases import TestRunner
from translator import VERIFIED, translate, translate_ex

APP_NAME = "AFJEN Compiler"

# ---------------------------------------------------------------- palette --
GREEN, GREEN_D, RED, YELLOW = "#0A8F6A", "#067556", "#CE1126", "#FCD116"
BG, CARD, INK, MUTED, LINE = "#EEF2F8", "#FFFFFF", "#17213A", "#66738F", "#DCE3EF"
NAVY, NAVY2 = "#0F1B33", "#1B2D52"
OK_BG, OK_FG = "#D9F2E7", "#0A6B4B"
MID_BG, MID_FG = "#FFF1C9", "#7A5600"
INF_BG, INF_FG = "#E1E9FA", "#2B4B99"

FONT, MONO = "Segoe UI", "Consolas"

TOKEN_COLORS = {
    "NOUN": "#E3F2FD", "PROPER_NOUN": "#CFE6FB", "PRONOUN": "#EDE7F6", "ARTICLE": "#F1F3F6",
    "VERB": "#E4F5E6", "PIDGIN_VERB": "#C8E6C9", "NEGATION": "#FFE3E3", "SUBJUNCTIVE": "#FFE9D6",
    "PIDGIN_MARKER": "#FFF3CC", "INTERJECTION": "#FCE4EC", "CODE_MIXED": "#F8D7F0",
    "ADJECTIVE": "#DDF5F9", "ADVERB": "#DCF2EF", "PREPOSITION": "#F0F4C3", "NUMBER": "#FFECB3",
    "CONNECTOR": "#ECEFF1", "PUNCTUATION": "#ECEFF1", "QUESTION_WORD": "#E5C9EB",
}

CATEGORIES = [
    ("Taxi & Commuting", [0, 1, 2]), ("Internet & Electricity", [3, 4, 5]),
    ("Market & Business", [6, 7, 8]), ("Security & Rainy Season", [9, 10]),
    ("Fuel & Transactions", [11, 12]), ("University & Slang", [13, 14]),
]
SAMPLES = list(VERIFIED.keys())
EXAMPLES = [
    "How you dey? I dey, thank you",
    "The light done cut again, na generator we dey use",
    "Mama, make you reduce am na small",
    "Petrol dey scarce, pump don empty again",
    "Why the bendskin dey charge too much?",
]


# ------------------------------------------------------------ custom widgets --
def round_rect(canvas, x1, y1, x2, y2, r, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2, x1, y2,
           x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(pts, smooth=True, **kw)


class RoundButton(tk.Canvas):
    """Flat rounded button with hover effect."""

    def __init__(self, parent, text, command, bg=GREEN, hover=GREEN_D, fg="white", size=11, bold=True,
                 padx=24, pady=11, radius=12, parent_bg=CARD):
        font = tkfont.Font(family=FONT, size=size, weight="bold" if bold else "normal")
        w = font.measure(text) + 2 * padx
        h = font.metrics("linespace") + 2 * pady
        super().__init__(parent, width=w, height=h, bg=parent_bg, highlightthickness=0, cursor="hand2")
        self._shape = round_rect(self, 1, 1, w - 1, h - 1, radius, fill=bg, outline=bg)
        self.create_text(w / 2, h / 2, text=text, fill=fg, font=font)
        self._bg, self._hover, self._cmd = bg, hover, command
        self.bind("<Enter>", lambda e: self.itemconfigure(self._shape, fill=self._hover, outline=self._hover))
        self.bind("<Leave>", lambda e: self.itemconfigure(self._shape, fill=self._bg, outline=self._bg))
        self.bind("<Button-1>", lambda e: self._cmd())


class Donut(tk.Canvas):
    """Ring showing the grammar coverage percentage."""

    def __init__(self, parent, size=124, bg=CARD):
        super().__init__(parent, width=size, height=size, bg=bg, highlightthickness=0)
        self.size = size
        self.set(0, GREEN)

    def set(self, pct, colour):
        self.delete("all")
        s, pad = self.size, 12
        self.create_oval(pad, pad, s - pad, s - pad, outline="#E6EBF3", width=11)
        if pct > 0:
            self.create_arc(pad, pad, s - pad, s - pad, start=90, extent=-3.6 * min(pct, 99.9), style=tk.ARC,
                            outline=colour, width=11)
        self.create_text(s / 2, s / 2 - 3, text=f"{pct}%", font=(FONT, 16, "bold"), fill=INK)
        self.create_text(s / 2, s / 2 + 17, text="grammar fit", font=(FONT, 8), fill=MUTED)


class AfjenApp:
    def __init__(self, root):
        self.root = root
        root.title(APP_NAME)
        root.geometry("1360x900")
        root.minsize(980, 620)
        root.configure(bg=BG)
        self.semantic = SemanticAnalyzer()
        self.bank = WordBank()
        self.lang = tk.StringVar(value="en")
        self.last_output = ""
        self.last_pair = ("", "")
        self.history = []
        self._live_job = None
        self._style()
        self._header()
        self._tabs()
        root.bind("<Control-Return>", lambda e: self.analyze())
        self.analyze()

    # ---------------------------------------------------------------- style --
    def _style(self):
        st = ttk.Style()
        st.theme_use("clam")
        st.configure(".", font=(FONT, 10), background=BG, foreground=INK)
        st.configure("TFrame", background=BG)
        st.configure("TNotebook", background=BG, borderwidth=0, tabmargins=(22, 10, 22, 0))
        st.configure("TNotebook.Tab", font=(FONT, 10, "bold"), padding=(20, 10), background="#E1E7F1",
                     foreground=MUTED, borderwidth=0)
        st.map("TNotebook.Tab", background=[("selected", CARD)], foreground=[("selected", GREEN)])
        st.configure("Treeview", font=(FONT, 10), rowheight=28, background=CARD, fieldbackground=CARD,
                     borderwidth=0, foreground=INK)
        st.configure("Treeview.Heading", font=(FONT, 9, "bold"), background="#EDF1F8", foreground=MUTED,
                     borderwidth=0, padding=(8, 8))
        st.map("Treeview", background=[("selected", "#CDEEE2")], foreground=[("selected", INK)])
        st.configure("Vertical.TScrollbar", background="#D3DAE8", troughcolor=BG, borderwidth=0, arrowsize=12)
        st.configure("TCombobox", padding=6)

    def _header(self):
        head = tk.Frame(self.root, bg=NAVY)
        head.pack(fill=tk.X)
        bar = tk.Frame(head, bg=NAVY)
        bar.pack(fill=tk.X, padx=30, pady=(16, 14))
        logo = tk.Canvas(bar, width=54, height=54, bg=NAVY, highlightthickness=0)
        logo.pack(side=tk.LEFT, padx=(0, 16))
        round_rect(logo, 1, 1, 53, 53, 14, fill=GREEN, outline=GREEN)
        logo.create_text(27, 28, text="A", font=(FONT, 26, "bold"), fill="white")
        round_rect(logo, 34, 6, 50, 14, 4, fill=YELLOW, outline=YELLOW)
        title = tk.Frame(bar, bg=NAVY)
        title.pack(side=tk.LEFT)
        row = tk.Frame(title, bg=NAVY)
        row.pack(anchor="w")
        tk.Label(row, text="AFJEN", font=(FONT, 24, "bold"), fg=YELLOW, bg=NAVY).pack(side=tk.LEFT)
        tk.Label(row, text=" Compiler", font=(FONT, 24), fg="white", bg=NAVY).pack(side=tk.LEFT)
        tk.Label(title, text="Understand Yaoundé street speech  ·  Pidgin  →  English / Français",
                 font=(FONT, 10), fg="#9FB0D3", bg=NAVY).pack(anchor="w")
        right = tk.Frame(bar, bg=NAVY)
        right.pack(side=tk.RIGHT)
        self.header_stats = tk.Label(right, text="", font=(FONT, 10), fg="#9FB0D3", bg=NAVY, justify=tk.RIGHT)
        self.header_stats.pack(anchor="e")
        flag = tk.Frame(head, height=5)
        flag.pack(fill=tk.X)
        for colour in (GREEN, RED, YELLOW):
            tk.Frame(flag, bg=colour, height=5).pack(side=tk.LEFT, expand=True, fill=tk.X)
        self._refresh_header()

    def _refresh_header(self):
        self.header_stats.configure(
            text=f"{len(build_dictionary())} dictionary words   ·   {self.bank.total_unique} words collected from your text")

    def _tabs(self):
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
        self._tab_translate()
        self._tab_dictionary()
        self._tab_insights()
        self._tab_samples()
        self._tab_tests()
        self._tab_grammar()
        self._tab_about()

    def _card(self, parent, title=None, **pack):
        outer = tk.Frame(parent, bg=LINE)
        outer.pack(**pack)
        card = tk.Frame(outer, bg=CARD)
        card.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        if title:
            tk.Label(card, text=title.upper(), font=(FONT, 8, "bold"), fg=MUTED, bg=CARD).pack(
                anchor="w", padx=18, pady=(14, 6))
        return card

    def _scrolled_text(self, parent, **kw):
        frame = tk.Frame(parent, bg=CARD)
        text = tk.Text(frame, relief=tk.FLAT, highlightthickness=0, **kw)
        sb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        return frame, text

    # ------------------------------------------------------ tab: translate --
    def _tab_translate(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="  ✦  Translate  ")
        canvas = tk.Canvas(tab, bg=BG, highlightthickness=0)
        vbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=vbar.set)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        wrap = tk.Frame(canvas, bg=BG)
        win = canvas.create_window((0, 0), window=wrap, anchor="nw")
        wrap.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(win, width=e.width))
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-e.delta / 120), "units")
                        if self.nb.index(self.nb.select()) == 0 else None)
        pad = tk.Frame(wrap, bg=BG)
        pad.pack(fill=tk.BOTH, expand=True, padx=26, pady=(16, 20))

        # -- step 1: input
        card = self._card(pad, "1 · Type or paste your text  (any length, any words)", fill=tk.X)
        box, self.input = self._scrolled_text(card, height=3, font=(FONT, 14), bg="#F6F8FC", fg=INK,
                                              insertbackground=GREEN, padx=14, pady=12, wrap=tk.WORD)
        box.pack(fill=tk.X, padx=18, pady=(0, 8))
        self.input.insert("1.0", "Brother, drop me na at Carrefour Yaoundé, the traffic done tire me small")
        self.input.bind("<KeyRelease>", self._on_key)
        row = tk.Frame(card, bg=CARD)
        row.pack(fill=tk.X, padx=18, pady=(0, 6))
        RoundButton(row, "Translate & Analyze", self.analyze).pack(side=tk.LEFT)
        RoundButton(row, "Clear", self.clear, bg="#E7ECF5", hover="#D8DFEC", fg=INK, bold=False).pack(
            side=tk.LEFT, padx=10)
        RoundButton(row, "Paste", self.paste, bg="#E7ECF5", hover="#D8DFEC", fg=INK, bold=False).pack(side=tk.LEFT)
        self.count_label = tk.Label(row, text="", font=(FONT, 10), fg=MUTED, bg=CARD)
        self.count_label.pack(side=tk.RIGHT)
        self.live = tk.BooleanVar(value=True)
        tk.Checkbutton(row, text="Live translate", variable=self.live, font=(FONT, 10), fg=MUTED, bg=CARD,
                       activebackground=CARD, selectcolor=CARD, highlightthickness=0, bd=0).pack(side=tk.RIGHT, padx=16)
        chips = tk.Frame(card, bg=CARD)
        chips.pack(fill=tk.X, padx=18, pady=(4, 16))
        tk.Label(chips, text="Try one:", font=(FONT, 9), fg=MUTED, bg=CARD).pack(side=tk.LEFT, padx=(0, 8))
        for ex in EXAMPLES:
            RoundButton(chips, ex if len(ex) < 34 else ex[:32] + "…", lambda t=ex: self.load(t), bg="#EAF6F1",
                        hover="#D2EEE3", fg=GREEN_D, size=9, bold=False, padx=12, pady=6, radius=10).pack(
                side=tk.LEFT, padx=(0, 8))
        self._count_words()

        # -- step 2: translation
        card = self._card(pad, None, fill=tk.X, pady=(14, 0))
        top = tk.Frame(card, bg=CARD)
        top.pack(fill=tk.X, padx=18, pady=(14, 4))
        tk.Label(top, text="2 · TRANSLATION", font=(FONT, 8, "bold"), fg=MUTED, bg=CARD).pack(side=tk.LEFT)
        self.badge = tk.Label(top, text="", font=(FONT, 9, "bold"), padx=10, pady=2)
        self.badge.pack(side=tk.LEFT, padx=12)
        seg = tk.Frame(top, bg="#E3E9F3")
        seg.pack(side=tk.RIGHT)
        self.lang_buttons = {}
        for code, label in (("en", "English"), ("fr", "Français")):
            b = tk.Label(seg, text=label, font=(FONT, 10, "bold"), padx=18, pady=6, cursor="hand2")
            b.pack(side=tk.LEFT, padx=2, pady=2)
            b.bind("<Button-1>", lambda e, c=code: self.set_lang(c))
            self.lang_buttons[code] = b
        self._paint_lang()
        for label, cmd in (("Save…", self.save_translation), ("Copy both", self.copy_both), ("Copy", self.copy_translation)):
            lk = tk.Label(top, text=label, font=(FONT, 10, "underline"), fg=GREEN, bg=CARD, cursor="hand2")
            lk.pack(side=tk.RIGHT, padx=10)
            lk.bind("<Button-1>", lambda e, c=cmd: c())
        box, self.output = self._scrolled_text(card, height=2, font=(FONT, 16), bg=CARD, fg=INK, padx=14, pady=6,
                                               wrap=tk.WORD)
        box.pack(fill=tk.X, padx=18, pady=(0, 4))
        self.output.tag_configure("unk", foreground="#B25E00", underline=True)
        self.note = tk.Label(card, text="", font=(FONT, 9), fg=MUTED, bg=CARD, anchor="w", justify=tk.LEFT,
                             wraplength=1180)
        self.note.pack(fill=tk.X, padx=18, pady=(0, 6))
        self.chip_row = tk.Frame(card, bg=CARD)
        self.chip_row.pack(fill=tk.X, padx=18, pady=(0, 10))

        # -- step 3: analysis
        tk.Label(pad, text="3 · HOW AFJEN READ IT", font=(FONT, 8, "bold"), fg=MUTED, bg=BG).pack(
            anchor="w", pady=(16, 6))
        stats = self._card(pad, None, fill=tk.X)
        srow = tk.Frame(stats, bg=CARD)
        srow.pack(fill=tk.X, padx=18, pady=14)
        self.donut = Donut(srow)
        self.donut.pack(side=tk.LEFT)
        info = tk.Frame(srow, bg=CARD)
        info.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        self.pill = tk.Label(info, text="", font=(FONT, 11, "bold"), padx=14, pady=5)
        self.pill.pack(anchor="w")
        self.detail = tk.Label(info, text="", font=(FONT, 10), fg=MUTED, bg=CARD, anchor="w", justify=tk.LEFT,
                               wraplength=760)
        self.detail.pack(anchor="w", pady=(8, 0))
        tiles = tk.Frame(srow, bg=CARD)
        tiles.pack(side=tk.RIGHT)
        self.tiles = {}
        for key, label in (("words", "words"), ("sentences", "sentences"), ("category", "topic"),
                           ("intent", "intent")):
            t = tk.Frame(tiles, bg="#F4F7FC")
            t.pack(side=tk.LEFT, padx=5)
            v = tk.Label(t, text="–", font=(FONT, 16, "bold"), fg=GREEN_D, bg="#F4F7FC")
            v.pack(padx=18, pady=(10, 0))
            tk.Label(t, text=label, font=(FONT, 9), fg=MUTED, bg="#F4F7FC").pack(pady=(0, 10))
            self.tiles[key] = v

        body = tk.Frame(pad, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, pady=(12, 0))
        body.columnconfigure(0, weight=5, uniform="c")
        body.columnconfigure(1, weight=6, uniform="c")
        left = tk.Frame(body, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        c1 = self._card(left, "Words found (lexical analysis)", fill=tk.BOTH, expand=True)
        cols = ("Word", "Type", "Pos")
        self.tokens = ttk.Treeview(c1, columns=cols, show="headings", height=12)
        for col, w in zip(cols, (150, 150, 60)):
            self.tokens.heading(col, text=col)
            self.tokens.column(col, width=w, anchor="w")
        for name, colour in TOKEN_COLORS.items():
            self.tokens.tag_configure(name, background=colour)
        sb = ttk.Scrollbar(c1, orient=tk.VERTICAL, command=self.tokens.yview)
        self.tokens.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 14), padx=(0, 6))
        self.tokens.pack(fill=tk.BOTH, expand=True, padx=(14, 0), pady=(0, 14))

        right = tk.Frame(body, bg=BG)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        c2 = self._card(right, "Sentence structure (syntactic analysis)", fill=tk.BOTH, expand=True)
        box, self.tree_text = self._scrolled_text(c2, height=12, font=(MONO, 10), bg="#FAFBFE", fg=INK, padx=14,
                                                  pady=10, wrap=tk.NONE)
        box.pack(fill=tk.BOTH, expand=True, padx=(14, 6), pady=(0, 14))
        self.tree_text.tag_configure("node", foreground=NAVY2)
        self.tree_text.tag_configure("leaf", foreground=GREEN_D, font=(MONO, 10, "bold"))
        self.tree_text.tag_configure("sent", foreground=INK, font=(FONT, 10, "bold"))
        self.tree_text.tag_configure("ok", foreground=OK_FG, font=(FONT, 9, "bold"))
        self.tree_text.tag_configure("frag", foreground=MID_FG, font=(FONT, 9, "italic"))

    # --------------------------------------------------------- input helpers --
    def _on_key(self, _event=None):
        self._count_words()
        if self.live.get():
            if self._live_job:
                self.root.after_cancel(self._live_job)
            self._live_job = self.root.after(650, self.analyze)

    def _count_words(self):
        text = self.input.get("1.0", tk.END)
        n = len(re.findall(r"[A-Za-zÀ-ÿ'’-]+", text))
        self.count_label.configure(text=f"{n} word{'s' if n != 1 else ''}")

    def clear(self):
        self.input.delete("1.0", tk.END)
        self._count_words()
        self.input.focus_set()

    def paste(self):
        try:
            clip = self.root.clipboard_get()
        except tk.TclError:
            return
        self.input.delete("1.0", tk.END)
        self.input.insert("1.0", clip)
        self._count_words()
        self.analyze()

    def load(self, text):
        self.input.delete("1.0", tk.END)
        self.input.insert("1.0", text)
        self._count_words()
        self.analyze()

    def _paint_lang(self):
        for code, b in self.lang_buttons.items():
            active = self.lang.get() == code
            b.configure(bg=GREEN if active else "#E3E9F3", fg="white" if active else MUTED)

    def set_lang(self, code):
        self.lang.set(code)
        self._paint_lang()
        self.analyze()

    def copy_both(self):
        en = self._translate_all(self.input.get("1.0", tk.END).strip(), "en")[0]
        fr = self._translate_all(self.input.get("1.0", tk.END).strip(), "fr")[0]
        self.root.clipboard_clear()
        self.root.clipboard_append(f"English: {en}" + chr(10) + f"Français: {fr}")
        self.note.configure(text="✔ English and French copied to the clipboard.")

    def save_translation(self):
        text = self.input.get("1.0", tk.END).strip()
        if not text:
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt")],
                                            initialfile="afjen_translation.txt")
        if path:
            en = self._translate_all(text, "en")[0]
            fr = self._translate_all(text, "fr")[0]
            with open(path, "w", encoding="utf-8") as f:
                f.write("Original:" + chr(10) + text + chr(10) * 2 + "English:" + chr(10) + en + chr(10) * 2
                        + "Français:" + chr(10) + fr + chr(10))
            self.note.configure(text=f"✔ Saved to {os.path.basename(path)}.")

    def copy_translation(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.last_output)
        self.note.configure(text="✔ Copied to the clipboard.")

    # ------------------------------------------------------------- analysis --
    def _translate_all(self, text, lang):
        """Translate any text: verified statements first, rule engine for the rest."""
        whole = translate(text, lang)
        if whole[1] == "verified":
            return whole[0], "verified", []
        pieces, methods, unknown = [], [], []
        for line in [ln for ln in text.splitlines() if ln.strip()]:
            hit = translate(line, lang)
            if hit[1] == "verified":
                pieces.append(hit[0])
                methods.append("verified")
                continue
            for sentence in re.split(r"(?<=[.!?])\s+", line.strip()):
                if not sentence.strip():
                    continue
                r = translate_ex(sentence, lang)
                pieces.append(r["text"])
                methods.append(r["method"])
                unknown += r["unknown"]
        method = "verified" if methods and all(m == "verified" for m in methods) else (
            "partial" if "verified" in methods else "automatic")
        return " ".join(pieces), method, sorted(set(unknown))

    def analyze(self):
        text = self.input.get("1.0", tk.END).strip()
        if not text:
            self.note.configure(text="Type or paste some text above, then press Translate & Analyze.")
            return
        lang = self.lang.get()
        out, method, unknown = self._translate_all(text, lang)
        self.last_output = out
        self.output.configure(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        self.output.insert("1.0", out)
        self.output.configure(height=max(2, min(9, len(out) // 95 + out.count(chr(10)) + 1)))
        if method == "verified":
            self.badge.configure(text="✔ Verified translation", bg=OK_BG, fg=OK_FG)
            note = "Hand-checked translation of collected statements."
        elif method == "partial":
            self.badge.configure(text="◐ Partly verified", bg=MID_BG, fg=MID_FG)
            note = "Some sentences are hand-checked, the rest was produced by the rule engine."
        else:
            self.badge.configure(text="⚙ Automatic translation", bg=MID_BG, fg=MID_FG)
            note = "Produced by AFJEN's rule engine: dey → is/are -ing, done → has/have, go → will, no fit → cannot."
        if unknown:
            note += "   Some words are new to AFJEN - click one to teach it:"
        self.note.configure(text=note)
        for child in self.chip_row.winfo_children():
            child.destroy()
        for word in unknown[:10]:
            RoundButton(self.chip_row, "+ " + word, lambda w=word: self.teach(w), bg="#FFF1C9", hover="#FBE29A",
                        fg=MID_FG, size=9, bold=True, padx=12, pady=5, radius=10).pack(side=tk.LEFT, padx=(0, 8))

        result = analyze_robust(text)
        self._show_tokens(result)
        self._show_structure(result)
        words = [t.value for t in result["tokens"]
                 if t.type not in (TokenType.PUNCTUATION, TokenType.CONNECTOR) or t.value.lower() in ("and", "but", "or")]
        self.bank.record(words)
        self._refresh_header()
        if text not in self.history[:1]:
            self.history.insert(0, text)
            del self.history[30:]
            self.history_list.delete(0, tk.END)
            for item in self.history:
                self.history_list.insert(tk.END, item.replace(chr(10), " ")[:110])
        self._draw_chart()

        cov = result["coverage"]
        n_sent = len(result["sentences"])
        if all(s["kind"] == "full" for s in result["sentences"]):
            self.pill.configure(text="✔  Fits the AFJEN grammar perfectly", bg=OK_BG, fg=OK_FG)
            self.donut.set(100, GREEN)
            self.detail.configure(text="Every sentence has a complete LL(1) parse tree.")
        elif cov >= 50:
            self.pill.configure(text=f"◐  {result['matched']} of {result['total']} clauses fit the grammar",
                                bg=MID_BG, fg=MID_FG)
            self.donut.set(cov, "#E0A100")
            self.detail.configure(text="The rest is informal speech - it is still translated and analysed word by word.")
        else:
            self.pill.configure(text="◔  Informal speech - analysed word by word", bg=INF_BG, fg=INF_FG)
            self.donut.set(cov, "#4C6FD1")
            self.detail.configure(text="This wording is looser than the strict grammar, so AFJEN read it as fragments.")
        sem = self.semantic.analyze(text)
        self.tiles["words"].configure(text=str(len(words)))
        self.tiles["sentences"].configure(text=str(n_sent))
        self.tiles["category"].configure(text=sem["category"])
        self.tiles["intent"].configure(text=sem["intent"])
        self.dict_refresh_counts()

    def _show_tokens(self, result):
        self.tokens.delete(*self.tokens.get_children())
        for tok in result["tokens"]:
            self.tokens.insert("", tk.END, values=(tok.value, tok.type.name, f"{tok.line}:{tok.column}"),
                               tags=(tok.type.name,))

    def _show_structure(self, result):
        t = self.tree_text
        t.configure(state=tk.NORMAL)
        t.delete("1.0", tk.END)
        for i, s in enumerate(result["sentences"], 1):
            t.insert(tk.END, f"Sentence {i}: ", "sent")
            t.insert(tk.END, s["text"][:90] + ("…" if len(s["text"]) > 90 else "") + "\n", "node")
            if s["kind"] == "full":
                t.insert(tk.END, "  ✔ complete parse\n", "ok")
            elif s["kind"] == "partial":
                t.insert(tk.END, f"  ◐ {s['matched']} of {s['total']} clauses parsed\n", "frag")
            else:
                t.insert(tk.END, "  ◔ informal - read as fragments\n", "frag")
            for tree in s["trees"]:
                self._draw_tree(tree, 1)
            for words, _err in s["fragments"]:
                t.insert(tk.END, f"    fragment: “{words}”\n", "frag")
            t.insert(tk.END, "\n")
        t.configure(state=tk.DISABLED)

    def _draw_tree(self, node, depth):
        t, pad = self.tree_text, "   " * depth
        if node.token is not None:
            t.insert(tk.END, f"{pad}└─ ", "node")
            t.insert(tk.END, node.token.value, "leaf")
            t.insert(tk.END, f"  {node.rule}\n", "node")
        else:
            t.insert(tk.END, f"{pad}▾ {node.rule}\n", "node")
            for child in node.children:
                self._draw_tree(child, depth + 1)

    # ------------------------------------------------------ tab: dictionary --
    def _tab_dictionary(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="  ☰  Dictionary  ")
        wrap = tk.Frame(tab, bg=BG)
        wrap.pack(fill=tk.BOTH, expand=True, padx=26, pady=16)

        # add-a-word form
        form = self._card(wrap, "Teach AFJEN a new word", fill=tk.X)
        row = tk.Frame(form, bg=CARD)
        row.pack(fill=tk.X, padx=18, pady=(0, 6))
        self.f_word, self.f_en, self.f_fr = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self.f_type, self.f_gender = tk.StringVar(value="noun"), tk.StringVar(value="m")

        def field(label, var, width, col):
            box = tk.Frame(row, bg=CARD)
            box.grid(row=0, column=col, padx=(0, 12), sticky="w")
            tk.Label(box, text=label, font=(FONT, 9), fg=MUTED, bg=CARD).pack(anchor="w")
            entry = tk.Entry(box, textvariable=var, font=(FONT, 12), relief=tk.FLAT, bg="#F6F8FC", fg=INK,
                             highlightthickness=1, highlightbackground=LINE, highlightcolor=GREEN, width=width,
                             insertbackground=GREEN)
            entry.pack(ipady=6)
            return entry

        self.e_word = field("Word (Pidgin / slang)", self.f_word, 16, 0)
        box = tk.Frame(row, bg=CARD)
        box.grid(row=0, column=1, padx=(0, 12), sticky="w")
        tk.Label(box, text="Type", font=(FONT, 9), fg=MUTED, bg=CARD).pack(anchor="w")
        ttk.Combobox(box, textvariable=self.f_type, values=userdict.TYPES, state="readonly", width=12,
                     font=(FONT, 11)).pack(ipady=4)
        self.e_en = field("English meaning", self.f_en, 22, 2)
        self.e_fr = field("Français (infinitive for verbs)", self.f_fr, 22, 3)
        box = tk.Frame(row, bg=CARD)
        box.grid(row=0, column=4, padx=(0, 12), sticky="w")
        tk.Label(box, text="Gender (FR)", font=(FONT, 9), fg=MUTED, bg=CARD).pack(anchor="w")
        ttk.Combobox(box, textvariable=self.f_gender, values=["m", "f"], state="readonly", width=4,
                     font=(FONT, 11)).pack(ipady=4)
        btn = tk.Frame(row, bg=CARD)
        btn.grid(row=0, column=5, sticky="s")
        RoundButton(btn, "+ Add word", self.add_word_clicked, padx=18, pady=9).pack()
        for e in (self.e_word, self.e_en, self.e_fr):
            e.bind("<Return>", lambda ev: self.add_word_clicked())
        self.form_msg = tk.Label(form, text="Tip: type a word you meet in the street, give its meanings, and it works "
                                            "everywhere at once - translation, tokens and grammar.",
                                 font=(FONT, 9), fg=MUTED, bg=CARD, anchor="w", justify=tk.LEFT, wraplength=1180)
        self.form_msg.pack(fill=tk.X, padx=18, pady=(2, 14))

        # search / count
        top = tk.Frame(wrap, bg=BG)
        top.pack(fill=tk.X, pady=(12, 8))
        self.dict_count = tk.Label(top, text="", font=(FONT, 12, "bold"), fg=INK, bg=BG)
        self.dict_count.pack(side=tk.LEFT)
        RoundButton(top, "Import CSV", self.import_words, bg="#E1E7F1", hover="#D2DAE9", fg=INK, bold=False,
                    size=9, padx=14, pady=6, parent_bg=BG).pack(side=tk.RIGHT, padx=(8, 0))
        RoundButton(top, "Export CSV", self.export_words, bg="#E1E7F1", hover="#D2DAE9", fg=INK, bold=False,
                    size=9, padx=14, pady=6, parent_bg=BG).pack(side=tk.RIGHT, padx=(8, 0))
        RoundButton(top, "Remove selected ★", self.remove_selected, bg="#FBE4E6", hover="#F5CDD1", fg="#A3121F",
                    bold=False, size=9, padx=14, pady=6, parent_bg=BG).pack(side=tk.RIGHT, padx=(8, 0))
        self.search = tk.StringVar()
        self.search.trace_add("write", lambda *a: self._fill_dictionary())
        entry = tk.Entry(top, textvariable=self.search, font=(FONT, 12), relief=tk.FLAT, bg=CARD, fg=INK,
                         highlightthickness=1, highlightbackground=LINE, highlightcolor=GREEN, width=26,
                         insertbackground=GREEN)
        entry.pack(side=tk.RIGHT, ipady=6)
        tk.Label(top, text="Search  ", font=(FONT, 10), fg=MUTED, bg=BG).pack(side=tk.RIGHT)

        card = self._card(wrap, None, fill=tk.BOTH, expand=True)
        cols = ("Word", "Type", "English", "Français")
        self.dict_tree = ttk.Treeview(card, columns=cols, show="headings")
        for col, w in zip(cols, (170, 150, 300, 300)):
            self.dict_tree.heading(col, text=col)
            self.dict_tree.column(col, width=w, anchor="w")
        self.dict_tree.tag_configure("odd", background="#F6F9FD")
        self.dict_tree.tag_configure("mine", background="#FFF6D6")
        sb = ttk.Scrollbar(card, orient=tk.VERTICAL, command=self.dict_tree.yview)
        self.dict_tree.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.dict_tree.pack(fill=tk.BOTH, expand=True)
        self.collected = tk.Label(wrap, text="", font=(FONT, 10), fg=MUTED, bg=BG, anchor="w", justify=tk.LEFT,
                                  wraplength=1200)
        self.collected.pack(fill=tk.X, pady=(10, 0))
        self._fill_dictionary()

    def _fill_dictionary(self):
        self.entries = build_dictionary()
        q = self.search.get().strip().lower()
        self.dict_tree.delete(*self.dict_tree.get_children())
        shown = 0
        for i, row in enumerate(self.entries):
            if q and not any(q in str(c).lower() for c in row):
                continue
            tag = "mine" if row[1].startswith("★") else ("odd" if i % 2 else "")
            self.dict_tree.insert("", tk.END, values=row, tags=(tag,) if tag else ())
            shown += 1
        mine = sum(1 for r in self.entries if r[1].startswith("★"))
        self.dict_count.configure(text=f"{shown} of {len(self.entries)} words   ·   {mine} added by you ★")
        self.dict_refresh_counts()

    def dict_refresh_counts(self):
        if not hasattr(self, "collected"):
            return
        unk = self.bank.unknown_words
        msg = f"Word bank: {self.bank.total_unique} different words collected from the text you analysed"
        msg += (f"  ·  {len(unk)} not in the dictionary yet: {', '.join(unk[:15])}{'…' if len(unk) > 15 else ''}"
                if unk else ".")
        self.collected.configure(text=msg)

    def teach(self, word):
        """Jump to the dictionary form with a word pre-filled (used by the 'new word' chips)."""
        self.nb.select(1)
        self.f_word.set(word)
        self.f_en.set("")
        self.f_fr.set("")
        self.e_en.focus_set()

    def add_word_clicked(self):
        ok, msg = userdict.add_word(self.f_word.get(), self.f_type.get(), self.f_en.get(), self.f_fr.get(),
                                    self.f_gender.get())
        self.form_msg.configure(text=("✔ " if ok else "✘ ") + msg, fg=OK_FG if ok else "#A3121F")
        if ok:
            self.f_word.set("")
            self.f_en.set("")
            self.f_fr.set("")
            self.e_word.focus_set()
            self._fill_dictionary()
            self._refresh_header()
            self.analyze()

    def remove_selected(self):
        sel = self.dict_tree.selection()
        if not sel:
            self.form_msg.configure(text="Select one of your ★ words in the list first.", fg=MUTED)
            return
        word, kind = self.dict_tree.item(sel[0])["values"][:2]
        if not str(kind).startswith("★"):
            self.form_msg.configure(text="Only words you added (★) can be removed.", fg=MUTED)
            return
        userdict.remove_word(str(word))
        self.form_msg.configure(text=f"Removed “{word}”.", fg=MUTED)
        self._fill_dictionary()
        self._refresh_header()
        self.analyze()

    def export_words(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")],
                                            initialfile="afjen_my_words.csv")
        if path:
            n = userdict.export_csv(path)
            self.form_msg.configure(text=f"Exported {n} of your words to {os.path.basename(path)}.", fg=MUTED)

    def import_words(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv"), ("All files", "*.*")])
        if path:
            added, skipped = userdict.import_csv(path)
            self.form_msg.configure(text=f"Imported {added} words ({skipped} skipped).", fg=MUTED)
            self._fill_dictionary()
            self._refresh_header()
            self.analyze()

    # ------------------------------------------------------- tab: insights --
    def _tab_insights(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="  ▤  Insights  ")
        wrap = tk.Frame(tab, bg=BG)
        wrap.pack(fill=tk.BOTH, expand=True, padx=26, pady=16)
        wrap.columnconfigure(0, weight=1, uniform="i")
        wrap.columnconfigure(1, weight=1, uniform="i")
        wrap.rowconfigure(0, weight=1)
        left = tk.Frame(wrap, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        right = tk.Frame(wrap, bg=BG)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        c1 = self._card(left, "Most used words (your word bank)", fill=tk.BOTH, expand=True)
        self.chart = tk.Canvas(c1, bg=CARD, highlightthickness=0)
        self.chart.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 14))
        self.chart.bind("<Configure>", lambda e: self._draw_chart())
        c2 = self._card(right, "History (click to reopen)", fill=tk.BOTH, expand=True)
        box = tk.Frame(c2, bg=CARD)
        box.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 14))
        self.history_list = tk.Listbox(box, font=(FONT, 11), relief=tk.FLAT, bg="#FAFBFE", fg=INK, activestyle="none",
                                       selectbackground="#CDEEE2", selectforeground=INK, highlightthickness=0)
        sb = ttk.Scrollbar(box, orient=tk.VERTICAL, command=self.history_list.yview)
        self.history_list.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_list.pack(fill=tk.BOTH, expand=True)
        self.history_list.bind("<<ListboxSelect>>", self.open_history)

    def _draw_chart(self):
        c = self.chart
        c.delete("all")
        words = self.bank.top_words(10)
        if not words:
            c.create_text(20, 20, anchor="nw", text="Analyse some text and your most used words appear here.",
                          font=(FONT, 11), fill=MUTED)
            return
        w, h = max(c.winfo_width(), 300), max(c.winfo_height(), 200)
        peak = max(n for _, n in words)
        row_h = min(38, (h - 10) / len(words))
        for i, (word, n) in enumerate(words):
            y = 8 + i * row_h
            c.create_text(4, y + row_h / 2, anchor="w", text=word, font=(FONT, 10, "bold"), fill=INK)
            bar = 110 + (w - 190) * n / peak
            round_rect(c, 110, y + 5, max(bar, 122), y + row_h - 5, 6, fill=GREEN if i % 2 == 0 else "#3DB08F",
                       outline="")
            c.create_text(max(bar, 122) + 8, y + row_h / 2, anchor="w", text=str(n), font=(FONT, 10), fill=MUTED)

    def open_history(self, _event=None):
        sel = self.history_list.curselection()
        if sel:
            self.nb.select(0)
            self.load(self.history[sel[0]])

    # --------------------------------------------------------- tab: samples --
    def _tab_samples(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="  ❝  Collected Statements  ")
        wrap = tk.Frame(tab, bg=BG)
        wrap.pack(fill=tk.BOTH, expand=True, padx=26, pady=16)
        tk.Label(wrap, text="The 15 statements collected in Yaoundé, with verified translations. Double-click one to analyse it.",
                 font=(FONT, 10), fg=MUTED, bg=BG).pack(anchor="w", pady=(0, 8))
        card = self._card(wrap, None, fill=tk.BOTH, expand=True)
        cols = ("#", "Category", "Pidgin", "English", "Français")
        self.samples = ttk.Treeview(card, columns=cols, show="headings")
        for col, w in zip(cols, (36, 150, 330, 330, 330)):
            self.samples.heading(col, text=col)
            self.samples.column(col, width=w, anchor="w")
        self.samples.tag_configure("odd", background="#F6F9FD")
        for cat, idxs in CATEGORIES:
            for i in idxs:
                v = VERIFIED[SAMPLES[i]]
                self.samples.insert("", tk.END, values=(i + 1, cat, SAMPLES[i], v["en"], v["fr"]),
                                    tags=("odd",) if i % 2 else ())
        sb = ttk.Scrollbar(card, orient=tk.VERTICAL, command=self.samples.yview)
        self.samples.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.samples.pack(fill=tk.BOTH, expand=True)
        self.samples.bind("<Double-1>", self.open_sample)

    def open_sample(self, _event=None):
        sel = self.samples.selection()
        if sel:
            idx = int(self.samples.item(sel[0])["values"][0]) - 1
            self.nb.select(0)
            self.load(SAMPLES[idx])

    # ----------------------------------------------------------- tab: tests --
    def _tab_tests(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="  ✓  Test Suite  ")
        wrap = tk.Frame(tab, bg=BG)
        wrap.pack(fill=tk.BOTH, expand=True, padx=26, pady=16)
        bar = tk.Frame(wrap, bg=BG)
        bar.pack(fill=tk.X, pady=(0, 10))
        RoundButton(bar, "Run all tests", self.run_all, parent_bg=BG).pack(side=tk.LEFT)
        RoundButton(bar, "Strict grammar: accept / reject", self.run_accept_reject, bg="#E1E7F1", hover="#D2DAE9",
                    fg=INK, bold=False, parent_bg=BG).pack(side=tk.LEFT, padx=10)
        RoundButton(bar, "Export…", self.export, bg="#E1E7F1", hover="#D2DAE9", fg=INK, bold=False,
                    parent_bg=BG).pack(side=tk.RIGHT)
        tk.Label(wrap, text="These exam tests use the strict LL(1) grammar, so they include sentences that are "
                            "deliberately malformed. The Translate tab never rejects your text.",
                 font=(FONT, 9), fg=MUTED, bg=BG, anchor="w", wraplength=1200, justify=tk.LEFT).pack(fill=tk.X, pady=(0, 8))
        card = self._card(wrap, None, fill=tk.BOTH, expand=True)
        box, self.results = self._scrolled_text(card, font=(MONO, 10), bg="#FAFBFE", fg=INK, padx=16, pady=12,
                                                wrap=tk.NONE)
        box.pack(fill=tk.BOTH, expand=True)
        self.results.tag_configure("pass", foreground=OK_FG, font=(MONO, 10, "bold"))
        self.results.tag_configure("fail", foreground="#A3121F", font=(MONO, 10, "bold"))
        self.results.tag_configure("head", foreground=NAVY2, font=(MONO, 10, "bold"))
        self.results.insert("1.0", "Press “Run all tests” to run the full suite.\n", "head")

    def _capture(self, func):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            func()
        return buf.getvalue()

    def _show_results(self, text):
        self.results.delete("1.0", tk.END)
        for line in text.splitlines():
            up = line.upper()
            if "[FAIL]" in up or "SOME TESTS FAILED" in up:
                tag = "fail"
            elif "[PASS]" in up or "PASSED" in up or "✓" in line:
                tag = "pass"
            elif line.startswith(("=", "-")) or (line.strip() and line.strip().isupper()):
                tag = "head"
            else:
                tag = ""
            self.results.insert(tk.END, line + "\n", tag)
        self.last_results = text

    def run_all(self):
        self.root.config(cursor="watch")
        self.root.update_idletasks()
        try:
            self._show_results(self._capture(TestRunner().run_all_tests))
        finally:
            self.root.config(cursor="")

    def run_accept_reject(self):
        self._show_results(self._capture(lambda: TestRunner().run_accept_reject_tests()))

    def export(self):
        text = getattr(self, "last_results", "")
        if not text:
            messagebox.showinfo("Nothing to export", "Run the tests first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt")],
                                            initialfile=f"afjen_test_results_{datetime.now():%Y%m%d_%H%M%S}.txt")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)

    # --------------------------------------------------------- tab: grammar --
    def _tab_grammar(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="  ⌘  Grammar  ")
        wrap = tk.Frame(tab, bg=BG)
        wrap.pack(fill=tk.BOTH, expand=True, padx=26, pady=16)
        conflicts = len(grammar.find_conflicts())
        prods = sum(len(p) for p in grammar.GRAMMAR.values())
        stats = tk.Frame(wrap, bg=BG)
        stats.pack(fill=tk.X, pady=(0, 12))
        for label, value in (("non-terminals", len(grammar.GRAMMAR)), ("productions", prods),
                             ("table entries", len(grammar.TABLE)), ("LL(1) conflicts", conflicts)):
            c = tk.Frame(stats, bg=CARD, highlightthickness=1, highlightbackground=LINE)
            c.pack(side=tk.LEFT, padx=(0, 12))
            tk.Label(c, text=str(value), font=(FONT, 22, "bold"), fg=GREEN_D, bg=CARD).pack(padx=26, pady=(10, 0))
            tk.Label(c, text=label, font=(FONT, 9), fg=MUTED, bg=CARD).pack(padx=26, pady=(0, 10))
        card = self._card(wrap, None, fill=tk.BOTH, expand=True)
        box, txt = self._scrolled_text(card, font=(MONO, 10), bg="#FAFBFE", fg=INK, padx=16, pady=12, wrap=tk.NONE)
        box.pack(fill=tk.BOTH, expand=True)
        txt.tag_configure("nt", foreground=GREEN_D, font=(MONO, 10, "bold"))
        txt.tag_configure("h", foreground=NAVY2, font=(MONO, 11, "bold"))
        txt.insert(tk.END, "PRODUCTIONS\n", "h")
        for nt, ps in grammar.GRAMMAR.items():
            txt.insert(tk.END, f"{nt:<9}", "nt")
            txt.insert(tk.END, " → " + "  |  ".join(" ".join(p) for p in ps) + "\n")
        txt.insert(tk.END, "\nFIRST / FOLLOW\n", "h")
        for nt in grammar.GRAMMAR:
            txt.insert(tk.END, f"{nt:<9}", "nt")
            txt.insert(tk.END, f" FIRST  {{{', '.join(sorted(grammar.FIRST[nt]))}}}\n")
            txt.insert(tk.END, f"{'':<9} FOLLOW {{{', '.join(sorted(grammar.FOLLOW[nt]))}}}\n")
        txt.configure(state=tk.DISABLED)

    # ---------------------------------------------------------- tab: about --
    def _tab_about(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="  ⓘ  About  ")
        wrap = tk.Frame(tab, bg=BG)
        wrap.pack(fill=tk.BOTH, expand=True, padx=26, pady=16)
        card = self._card(wrap, None, fill=tk.BOTH, expand=True)
        msg = (
            "AFJEN COMPILER  ·  CS4110 Compiler Construction, ICT University\n\n"
            "How to use it\n"
            "  1. Type or paste any text on the Translate tab (one word or many paragraphs).\n"
            "  2. Press “Translate & Analyze” (or Ctrl+Enter). Switch English / Français at any time.\n"
            "  3. Read the translation, then look at the words and sentence structure AFJEN found.\n\n"
            "Teach it new words\n"
            "  On the Dictionary tab (or by clicking a yellow “+ word” chip under a translation) add any word with its\n"
            "  English and French meaning. It is saved in data/user_dictionary.json and works immediately in the\n"
            "  lexer, the parser and the translator. Export / import your words as CSV.\n\n"
            "Nothing is refused\n"
            "  Any text is accepted. Unknown words are kept as written and added to your word bank; sentences that\n"
            "  are looser than the strict grammar are analysed clause by clause and word by word.\n\n"
            "Translation badges\n"
            "  ✔ Verified   hand-checked translation of one of the 15 collected statements.\n"
            "  ⚙ Automatic  rule engine: dey → is/are -ing · done/don → has/have · go → will · no fit → cannot ·\n"
            "               make we → let's · make you → please · wahala → trouble.\n\n"
            "Under the hood\n"
            "  Lexical analysis (18 token types, regular expressions) → strict table-driven LL(1) parser →\n"
            "  semantic category and intent → translation. The strict grammar is conflict-free and is used for the\n"
            "  exam accept / reject tests.\n"
        )
        tk.Label(card, text=msg, font=(FONT, 11), fg=INK, bg=CARD, justify=tk.LEFT, anchor="nw").pack(
            fill=tk.BOTH, expand=True, padx=28, pady=24)


def main():
    try:  # crisp text on high-DPI Windows screens
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    root = tk.Tk()
    try:
        root.state("zoomed")
    except tk.TclError:
        pass
    AfjenApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
