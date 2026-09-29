"""
AFJEN Compiler - graphical interface (v3, "Rosewood & Ivory")
CS4110 - Compiler Construction

Type or paste any amount of Yaoundé Pidgin / franc-anglais text and AFJEN gives you:
  * a translation into standard English or Français (verified for the collected statements)
  * the words it found (lexical analysis) and how they fit the LL(1) grammar (syntactic analysis)
  * the topic and intent (semantic analysis)
You can teach it new words and new statements from the front end, and save every result to a file.
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

import corpus
import grammar
import statements
import userdict
from dictionary import WordBank, build_dictionary, letters, sort_key
from lexical_analyzer import TokenType
from parser import analyze_robust
from semantic_analyzer import SemanticAnalyzer
from test_cases import TestRunner
from translator import translate, translate_ex

APP_NAME = "AFJEN Compiler"

# ---------------------------------------------------------------- palette --
PLUM, PLUM2, PLUM3 = "#3A1A3A", "#552653", "#6B3468"
ROSE, ROSE_D = "#B94A6E", "#9C3A5A"
GOLD, GOLD_L = "#C9A24B", "#F1E3BC"
BG, CARD, BORDER = "#FAF6F1", "#FFFFFF", "#E8DED2"
INK, MUTED = "#2E2233", "#85788A"
OK_BG, OK_FG = "#E1EFE6", "#2F6B4A"
MID_BG, MID_FG = "#FBEFD2", "#7C5A0B"
INF_BG, INF_FG = "#EDE4F3", "#5A2F7A"
BLUSH, BLUSH_D = "#F3E7EA", "#EBD4DA"

SERIF, SANS, MONO = "Georgia", "Segoe UI", "Consolas"

TOKEN_COLORS = {
    "NOUN": "#E9F0F8", "PROPER_NOUN": "#D9E6F4", "PRONOUN": "#EFE7F5", "ARTICLE": "#F3F0EC",
    "VERB": "#E4F1E7", "PIDGIN_VERB": "#CFE8D6", "NEGATION": "#F9E0E0", "SUBJUNCTIVE": "#FBE7D3",
    "PIDGIN_MARKER": "#FBEFD2", "INTERJECTION": "#F8E1EA", "CODE_MIXED": "#F3D9EE",
    "ADJECTIVE": "#DDF1F3", "ADVERB": "#DDF0EC", "PREPOSITION": "#EEF2CF", "NUMBER": "#FBEBC4",
    "CONNECTOR": "#EFECE8", "PUNCTUATION": "#EFECE8", "QUESTION_WORD": "#E7D2EC",
}
EXAMPLES = [
    "How you dey? I dey, thank you",
    "The light done cut again, na generator we dey use",
    "Mama, make you reduce am na small",
    "Petrol dey scarce, pump don empty again",
    "Wuna mos pay for bus",
]
PAGES = [("translate", "✦", "Translate"), ("dictionary", "☰", "Dictionary"), ("statements", "❝", "Statements"),
         ("insights", "▤", "Insights"), ("tests", "✓", "Test Suite"), ("grammar", "⌘", "Grammar"),
         ("about", "ⓘ", "About")]
PAGE_SUBTITLE = {
    "translate": "Type or paste any Pidgin or franc-anglais text",
    "dictionary": "Every word AFJEN knows, in alphabetical order - and the words you taught it",
    "statements": "The collected statements and your own, each with a verified English and French translation",
    "insights": "What you have been analysing",
    "tests": "Exam tests for the lexer, the strict LL(1) parser and the translator",
    "grammar": "The conflict-free LL(1) grammar behind the parser",
    "about": "The founders, the story and how AFJEN works",
}


# ------------------------------------------------------------ custom widgets --
def round_rect(canvas, x1, y1, x2, y2, r, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2, x1, y2,
           x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(pts, smooth=True, **kw)


class RoundButton(tk.Canvas):
    """Flat rounded button with hover effect."""

    def __init__(self, parent, text, command, bg=ROSE, hover=ROSE_D, fg="white", size=10, bold=True,
                 padx=22, pady=10, radius=12, parent_bg=CARD):
        font = tkfont.Font(family=SANS, size=size, weight="bold" if bold else "normal")
        w = font.measure(text) + 2 * padx
        h = font.metrics("linespace") + 2 * pady
        super().__init__(parent, width=w, height=h, bg=parent_bg, highlightthickness=0, cursor="hand2")
        self._shape = round_rect(self, 1, 1, w - 1, h - 1, radius, fill=bg, outline=bg)
        self.create_text(w / 2, h / 2, text=text, fill=fg, font=font)
        self._bg, self._hover, self._cmd = bg, hover, command
        self.bind("<Enter>", lambda e: self.itemconfigure(self._shape, fill=self._hover, outline=self._hover))
        self.bind("<Leave>", lambda e: self.itemconfigure(self._shape, fill=self._bg, outline=self._bg))
        self.bind("<Button-1>", lambda e: self._cmd())


def soft_button(parent, text, command, parent_bg=CARD, **kw):
    return RoundButton(parent, text, command, bg=BLUSH, hover=BLUSH_D, fg=PLUM, bold=False, parent_bg=parent_bg, **kw)


class Donut(tk.Canvas):
    """Ring showing the grammar coverage percentage."""

    def __init__(self, parent, size=124, bg=CARD):
        super().__init__(parent, width=size, height=size, bg=bg, highlightthickness=0)
        self.size = size
        self.set(0, ROSE)

    def set(self, pct, colour):
        self.delete("all")
        s, pad = self.size, 12
        self.create_oval(pad, pad, s - pad, s - pad, outline="#EFE6DC", width=11)
        if pct > 0:
            self.create_arc(pad, pad, s - pad, s - pad, start=90, extent=-3.6 * min(pct, 99.9), style=tk.ARC,
                            outline=colour, width=11)
        self.create_text(s / 2, s / 2 - 3, text=f"{pct}%", font=(SERIF, 16, "bold"), fill=INK)
        self.create_text(s / 2, s / 2 + 17, text="grammar fit", font=(SANS, 8), fill=MUTED)


def styled_entry(parent, var=None, width=20, font_size=12):
    return tk.Entry(parent, textvariable=var, font=(SANS, font_size), relief=tk.FLAT, bg="#FBF8F5", fg=INK,
                    highlightthickness=1, highlightbackground=BORDER, highlightcolor=ROSE, width=width,
                    insertbackground=ROSE)


class Modal(tk.Toplevel):
    """Elegant modal window used by the add-word and add-statement forms."""

    def __init__(self, app, title, subtitle, width=620):
        super().__init__(app.root)
        self.app = app
        self.title(title)
        self.configure(bg=BG)
        self.transient(app.root)
        self.resizable(False, False)
        head = tk.Frame(self, bg=PLUM)
        head.pack(fill=tk.X)
        tk.Label(head, text=title, font=(SERIF, 16, "bold"), fg="white", bg=PLUM).pack(anchor="w", padx=24, pady=(18, 2))
        tk.Label(head, text=subtitle, font=(SANS, 10), fg="#D8C2D6", bg=PLUM, wraplength=width - 48,
                 justify=tk.LEFT).pack(anchor="w", padx=24, pady=(0, 16))
        tk.Frame(self, height=3, bg=GOLD).pack(fill=tk.X)
        self.body = tk.Frame(self, bg=BG)
        self.body.pack(fill=tk.BOTH, expand=True, padx=24, pady=18)
        self.message = tk.Label(self, text="", font=(SANS, 10), bg=BG, fg=MUTED, wraplength=width - 48,
                                justify=tk.LEFT, anchor="w")
        self.message.pack(fill=tk.X, padx=24)
        self.buttons = tk.Frame(self, bg=BG)
        self.buttons.pack(fill=tk.X, padx=24, pady=(6, 20))
        self.geometry(f"{width}x1")
        self.bind("<Escape>", lambda e: self.destroy())

    def finish(self):
        self.update_idletasks()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        root = self.app.root
        x = root.winfo_rootx() + (root.winfo_width() - w) // 2
        y = root.winfo_rooty() + (root.winfo_height() - h) // 3
        self.geometry(f"{w}x{h}+{max(x, 0)}+{max(y, 0)}")
        self.grab_set()

    def say(self, text, ok):
        self.message.configure(text=("✔ " if ok else "✘ ") + text, fg=OK_FG if ok else "#A3121F")


class AfjenApp:
    def __init__(self, root):
        self.root = root
        root.title(APP_NAME)
        root.geometry("1440x900")
        root.minsize(1060, 660)
        root.configure(bg=BG)
        self.semantic = SemanticAnalyzer()
        self.bank = WordBank()
        self.lang = tk.StringVar(value="en")
        self.last_output = ""
        self.history = []
        self._live_job = None
        self.pages, self.nav_items, self.current = {}, {}, None
        self._style()
        self._layout()
        for key, _icon, _label in PAGES:
            getattr(self, f"_page_{key}")(self.pages[key])
        self.show("translate")
        root.bind("<Control-Return>", lambda e: self.analyze())
        self.analyze()

    # ----------------------------------------------------------------- style --
    def _style(self):
        st = ttk.Style()
        st.theme_use("clam")
        st.configure(".", font=(SANS, 10), background=BG, foreground=INK)
        st.configure("Treeview", font=(SANS, 10), rowheight=30, background=CARD, fieldbackground=CARD,
                     borderwidth=0, foreground=INK)
        st.configure("Treeview.Heading", font=(SANS, 9, "bold"), background="#F4ECE4", foreground=MUTED,
                     borderwidth=0, padding=(8, 9))
        st.map("Treeview", background=[("selected", "#F0D8DF")], foreground=[("selected", INK)])
        st.configure("Vertical.TScrollbar", background="#E2D6CA", troughcolor=BG, borderwidth=0, arrowsize=12)
        st.configure("TCombobox", padding=6, fieldbackground="#FBF8F5", background=BLUSH)

    # ---------------------------------------------------------------- layout --
    def _layout(self):
        side = tk.Frame(self.root, bg=PLUM, width=252)
        side.pack(side=tk.LEFT, fill=tk.Y)
        side.pack_propagate(False)
        logo = tk.Canvas(side, width=252, height=112, bg=PLUM, highlightthickness=0)
        logo.pack()
        logo.create_oval(26, 26, 78, 78, fill=GOLD, outline=GOLD)
        logo.create_text(52, 52, text="A", font=(SERIF, 26, "bold"), fill=PLUM)
        logo.create_text(92, 44, anchor="w", text="AFJEN", font=(SERIF, 19, "bold"), fill="white")
        logo.create_text(94, 70, anchor="w", text="C O M P I L E R", font=(SANS, 8, "bold"), fill=GOLD)
        tk.Frame(side, height=1, bg=PLUM3).pack(fill=tk.X, padx=22, pady=(0, 14))
        for key, icon, label in PAGES:
            self._nav_item(side, key, icon, label)
        foot = tk.Frame(side, bg=PLUM)
        foot.pack(side=tk.BOTTOM, fill=tk.X, padx=22, pady=20)
        self.side_stats = tk.Label(foot, text="", font=(SANS, 9), fg="#D8C2D6", bg=PLUM, justify=tk.LEFT, anchor="w")
        self.side_stats.pack(anchor="w")
        tk.Label(foot, text="Made with pride in Yaoundé", font=(SERIF, 8, "italic"), fg=GOLD, bg=PLUM).pack(
            anchor="w", pady=(6, 0))

        main = tk.Frame(self.root, bg=BG)
        main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        top = tk.Frame(main, bg=BG)
        top.pack(fill=tk.X, padx=34, pady=(22, 6))
        titles = tk.Frame(top, bg=BG)
        titles.pack(side=tk.LEFT)
        self.page_title = tk.Label(titles, text="", font=(SERIF, 24, "bold"), fg=PLUM, bg=BG)
        self.page_title.pack(anchor="w")
        self.page_sub = tk.Label(titles, text="", font=(SANS, 10), fg=MUTED, bg=BG)
        self.page_sub.pack(anchor="w")
        actions = tk.Frame(top, bg=BG)
        actions.pack(side=tk.RIGHT)
        soft_button(actions, "＋  Add statement", lambda: self.open_statement_dialog(), parent_bg=BG).pack(
            side=tk.RIGHT, padx=(10, 0))
        RoundButton(actions, "＋  Add word", lambda: self.open_word_dialog(), parent_bg=BG).pack(side=tk.RIGHT)
        tk.Frame(main, height=2, bg=GOLD_L).pack(fill=tk.X, padx=34, pady=(8, 0))
        self.stage = tk.Frame(main, bg=BG)
        self.stage.pack(fill=tk.BOTH, expand=True)
        for key, _i, _l in PAGES:
            self.pages[key] = tk.Frame(self.stage, bg=BG)
        self.refresh_side()

    def _nav_item(self, parent, key, icon, label):
        row = tk.Frame(parent, bg=PLUM, cursor="hand2")
        row.pack(fill=tk.X)
        bar = tk.Frame(row, width=4, bg=PLUM)
        bar.pack(side=tk.LEFT, fill=tk.Y)
        ic = tk.Label(row, text=icon, font=(SANS, 13), fg=GOLD, bg=PLUM, width=3)
        ic.pack(side=tk.LEFT, pady=11)
        tx = tk.Label(row, text=label, font=(SANS, 11), fg="#EBDDEA", bg=PLUM, anchor="w")
        tx.pack(side=tk.LEFT, fill=tk.X, expand=True)
        parts = (row, ic, tx)
        for w in parts:
            w.bind("<Button-1>", lambda e, k=key: self.show(k))
            w.bind("<Enter>", lambda e, k=key: self._nav_paint(k, hover=True))
            w.bind("<Leave>", lambda e, k=key: self._nav_paint(k))
        self.nav_items[key] = (row, bar, ic, tx)

    def _nav_paint(self, key, hover=False):
        row, bar, ic, tx = self.nav_items[key]
        active = key == self.current
        bg = PLUM2 if (active or hover) else PLUM
        for w in (row, ic, tx):
            w.configure(bg=bg)
        bar.configure(bg=GOLD if active else bg)
        tx.configure(fg="white" if active else "#EBDDEA", font=(SANS, 11, "bold" if active else "normal"))

    def show(self, key):
        if self.current:
            self.pages[self.current].pack_forget()
        self.current = key
        self.pages[key].pack(fill=tk.BOTH, expand=True)
        for k in self.nav_items:
            self._nav_paint(k)
        label = next(l for k, _i, l in PAGES if k == key)
        self.page_title.configure(text=label)
        self.page_sub.configure(text=PAGE_SUBTITLE[key])
        if key == "insights":
            self.refresh_insights()

    def refresh_side(self):
        n_words = len(build_dictionary())
        n_stmt = len(statements.all_statements())
        self.side_stats.configure(
            text=f"{n_words} dictionary words\n{n_stmt} statements\n{self.bank.total_unique} words collected")

    def _card(self, parent, title=None, **pack):
        outer = tk.Frame(parent, bg=BORDER)
        outer.pack(**pack)
        card = tk.Frame(outer, bg=CARD)
        card.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        if title:
            tk.Label(card, text=title.upper(), font=(SANS, 8, "bold"), fg=ROSE, bg=CARD).pack(
                anchor="w", padx=20, pady=(16, 6))
        return card

    def _scrolled_text(self, parent, **kw):
        frame = tk.Frame(parent, bg=CARD)
        text = tk.Text(frame, relief=tk.FLAT, highlightthickness=0, **kw)
        sb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        return frame, text

    def _table(self, parent, columns, widths, height=None):
        frame = tk.Frame(parent, bg=CARD)
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=height or 10)
        for col, w in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="w")
        sb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        return frame, tree

    # -------------------------------------------------------- page: translate --
    def _page_translate(self, page):
        canvas = tk.Canvas(page, bg=BG, highlightthickness=0)
        vbar = ttk.Scrollbar(page, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=vbar.set)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        wrap = tk.Frame(canvas, bg=BG)
        win = canvas.create_window((0, 0), window=wrap, anchor="nw")
        wrap.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(win, width=e.width))
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-e.delta / 120), "units")
                        if self.current == "translate" else None)
        pad = tk.Frame(wrap, bg=BG)
        pad.pack(fill=tk.BOTH, expand=True, padx=34, pady=(16, 26))

        # -- 1 input
        card = self._card(pad, "1 · Your text  -  any length, any words", fill=tk.X)
        box, self.input = self._scrolled_text(card, height=3, font=(SERIF, 14), bg="#FBF8F5", fg=INK,
                                              insertbackground=ROSE, padx=16, pady=12, wrap=tk.WORD)
        box.pack(fill=tk.X, padx=20, pady=(0, 10))
        self.input.insert("1.0", "Brother, drop me na at Carrefour Yaoundé, the traffic done tire me small")
        self.input.bind("<KeyRelease>", self._on_key)
        row = tk.Frame(card, bg=CARD)
        row.pack(fill=tk.X, padx=20, pady=(0, 6))
        RoundButton(row, "Translate & Analyze", self.analyze).pack(side=tk.LEFT)
        soft_button(row, "Clear", self.clear).pack(side=tk.LEFT, padx=10)
        soft_button(row, "Paste", self.paste).pack(side=tk.LEFT)
        self.count_label = tk.Label(row, text="", font=(SANS, 10), fg=MUTED, bg=CARD)
        self.count_label.pack(side=tk.RIGHT)
        self.live = tk.BooleanVar(value=True)
        tk.Checkbutton(row, text="Live translate", variable=self.live, font=(SANS, 10), fg=MUTED, bg=CARD,
                       activebackground=CARD, selectcolor=CARD, highlightthickness=0, bd=0).pack(side=tk.RIGHT, padx=16)
        chips = tk.Frame(card, bg=CARD)
        chips.pack(fill=tk.X, padx=20, pady=(4, 18))
        tk.Label(chips, text="Try one:", font=(SANS, 9), fg=MUTED, bg=CARD).pack(side=tk.LEFT, padx=(0, 8))
        for ex in EXAMPLES:
            RoundButton(chips, ex if len(ex) < 34 else ex[:32] + "…", lambda t=ex: self.load(t), bg=GOLD_L,
                        hover="#EAD79E", fg="#6A4F0E", size=9, bold=False, padx=12, pady=6, radius=10).pack(
                side=tk.LEFT, padx=(0, 8))
        self._count_words()

        # -- 2 translation
        card = self._card(pad, None, fill=tk.X, pady=(16, 0))
        top = tk.Frame(card, bg=CARD)
        top.pack(fill=tk.X, padx=20, pady=(16, 4))
        tk.Label(top, text="2 · TRANSLATION", font=(SANS, 8, "bold"), fg=ROSE, bg=CARD).pack(side=tk.LEFT)
        self.badge = tk.Label(top, text="", font=(SANS, 9, "bold"), padx=10, pady=2)
        self.badge.pack(side=tk.LEFT, padx=12)
        seg = tk.Frame(top, bg=BLUSH)
        seg.pack(side=tk.RIGHT)
        self.lang_buttons = {}
        for code, label in (("en", "English"), ("fr", "Français")):
            b = tk.Label(seg, text=label, font=(SANS, 10, "bold"), padx=18, pady=6, cursor="hand2")
            b.pack(side=tk.LEFT, padx=2, pady=2)
            b.bind("<Button-1>", lambda e, c=code: self.set_lang(c))
            self.lang_buttons[code] = b
        self._paint_lang()
        box, self.output = self._scrolled_text(card, height=2, font=(SERIF, 17), bg=CARD, fg=INK, padx=16, pady=8,
                                               wrap=tk.WORD)
        box.pack(fill=tk.X, padx=20, pady=(2, 4))
        self.note = tk.Label(card, text="", font=(SANS, 9), fg=MUTED, bg=CARD, anchor="w", justify=tk.LEFT,
                             wraplength=1000)
        self.note.pack(fill=tk.X, padx=20, pady=(0, 6))
        self.chip_row = tk.Frame(card, bg=CARD)
        self.chip_row.pack(fill=tk.X, padx=20)
        bar = tk.Frame(card, bg=CARD)
        bar.pack(fill=tk.X, padx=20, pady=(8, 18))
        RoundButton(bar, "Save to file", self.save_translation, bg=PLUM, hover=PLUM2).pack(side=tk.LEFT)
        soft_button(bar, "Copy", self.copy_translation).pack(side=tk.LEFT, padx=10)
        soft_button(bar, "Copy both languages", self.copy_both).pack(side=tk.LEFT)
        soft_button(bar, "Save as a statement…", self.save_as_statement).pack(side=tk.RIGHT)

        # -- 3 analysis
        tk.Label(pad, text="3 · HOW AFJEN READ IT", font=(SANS, 8, "bold"), fg=ROSE, bg=BG).pack(
            anchor="w", pady=(20, 8))
        stats = self._card(pad, None, fill=tk.X)
        srow = tk.Frame(stats, bg=CARD)
        srow.pack(fill=tk.X, padx=20, pady=16)
        self.donut = Donut(srow)
        self.donut.pack(side=tk.LEFT)
        info = tk.Frame(srow, bg=CARD)
        info.pack(side=tk.LEFT, padx=22, fill=tk.X, expand=True)
        self.pill = tk.Label(info, text="", font=(SANS, 11, "bold"), padx=14, pady=5)
        self.pill.pack(anchor="w")
        self.detail = tk.Label(info, text="", font=(SANS, 10), fg=MUTED, bg=CARD, anchor="w", justify=tk.LEFT,
                               wraplength=520)
        self.detail.pack(anchor="w", pady=(8, 0))
        tiles = tk.Frame(srow, bg=CARD)
        tiles.pack(side=tk.RIGHT)
        self.tiles = {}
        for key, label in (("words", "words"), ("sentences", "sentences"), ("category", "topic"), ("intent", "intent")):
            t = tk.Frame(tiles, bg="#FBF6F0")
            t.pack(side=tk.LEFT, padx=5)
            v = tk.Label(t, text="–", font=(SERIF, 15, "bold"), fg=ROSE, bg="#FBF6F0")
            v.pack(padx=16, pady=(10, 0))
            tk.Label(t, text=label, font=(SANS, 9), fg=MUTED, bg="#FBF6F0").pack(pady=(0, 10))
            self.tiles[key] = v

        body = tk.Frame(pad, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, pady=(14, 0))
        body.columnconfigure(0, weight=5, uniform="c")
        body.columnconfigure(1, weight=6, uniform="c")
        left = tk.Frame(body, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        c1 = self._card(left, "Words found (lexical analysis)", fill=tk.BOTH, expand=True)
        frame, self.tokens = self._table(c1, ("Word", "Type", "Pos"), (150, 150, 60), height=12)
        frame.pack(fill=tk.BOTH, expand=True, padx=(16, 8), pady=(0, 16))
        for name, colour in TOKEN_COLORS.items():
            self.tokens.tag_configure(name, background=colour)
        right = tk.Frame(body, bg=BG)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        c2 = self._card(right, "Sentence structure (syntactic analysis)", fill=tk.BOTH, expand=True)
        box, self.tree_text = self._scrolled_text(c2, height=12, font=(MONO, 10), bg="#FDFBF8", fg=INK, padx=16,
                                                  pady=10, wrap=tk.NONE)
        box.pack(fill=tk.BOTH, expand=True, padx=(16, 8), pady=(0, 16))
        self.tree_text.tag_configure("node", foreground=PLUM2)
        self.tree_text.tag_configure("leaf", foreground=ROSE_D, font=(MONO, 10, "bold"))
        self.tree_text.tag_configure("sent", foreground=INK, font=(SANS, 10, "bold"))
        self.tree_text.tag_configure("ok", foreground=OK_FG, font=(SANS, 9, "bold"))
        self.tree_text.tag_configure("frag", foreground=MID_FG, font=(SANS, 9, "italic"))

    # ------------------------------------------------------------ input helpers --
    def _on_key(self, _event=None):
        self._count_words()
        if self.live.get():
            if self._live_job:
                self.root.after_cancel(self._live_job)
            self._live_job = self.root.after(650, self.analyze)

    def _count_words(self):
        n = len(re.findall(r"[A-Za-zÀ-ÿ'’-]+", self.input.get("1.0", tk.END)))
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
        self.load(clip)

    def load(self, text):
        self.input.delete("1.0", tk.END)
        self.input.insert("1.0", text)
        self._count_words()
        self.show("translate")
        self.analyze()

    def _paint_lang(self):
        for code, b in self.lang_buttons.items():
            active = self.lang.get() == code
            b.configure(bg=ROSE if active else BLUSH, fg="white" if active else MUTED)

    def set_lang(self, code):
        self.lang.set(code)
        self._paint_lang()
        self.analyze()

    # --------------------------------------------------------- copy / save --
    def _current_text(self):
        return self.input.get("1.0", tk.END).strip()

    def copy_translation(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.last_output)
        self.note.configure(text="✔ Copied to the clipboard.")

    def copy_both(self):
        text = self._current_text()
        en, fr = self._translate_all(text, "en")[0], self._translate_all(text, "fr")[0]
        self.root.clipboard_clear()
        self.root.clipboard_append(f"English: {en}" + chr(10) + f"Français: {fr}")
        self.note.configure(text="✔ English and French copied to the clipboard.")

    def save_translation(self):
        text = self._current_text()
        if not text:
            messagebox.showinfo("Nothing to save", "Type or paste some text first.")
            return
        path = filedialog.asksaveasfilename(
            title="Save translation", defaultextension=".txt",
            filetypes=[("Text file", "*.txt"), ("Markdown", "*.md"), ("All files", "*.*")],
            initialfile=f"afjen_translation_{datetime.now():%Y%m%d_%H%M}.txt")
        if not path:
            return
        en, en_method, _ = self._translate_all(text, "en")
        fr, fr_method, _ = self._translate_all(text, "fr")
        nl = chr(10)
        md = path.lower().endswith(".md")
        h1, h2 = ("## ", "## ") if md else ("", "")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"AFJEN Compiler - {datetime.now():%Y-%m-%d %H:%M}" + nl * 2)
            f.write(f"{h1}Original (Pidgin / franc-anglais){nl}{text}{nl * 2}")
            f.write(f"{h2}English ({en_method}){nl}{en}{nl * 2}")
            f.write(f"{h2}Français ({fr_method}){nl}{fr}{nl}")
        self.note.configure(text=f"✔ Saved to {path}")

    def save_as_statement(self):
        text = self._current_text()
        if not text:
            return
        en = self._translate_all(text, "en")[0]
        fr = self._translate_all(text, "fr")[0]
        self.open_statement_dialog(text=text, en=en, fr=fr)

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
        text = self._current_text()
        if not text:
            self.note.configure(text="Type or paste some text above, then press Translate & Analyze.")
            return
        lang = self.lang.get()
        out, method, unknown = self._translate_all(text, lang)
        self.last_output = out
        self.output.configure(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        self.output.insert("1.0", out)
        self.output.configure(height=max(2, min(9, len(out) // 90 + out.count(chr(10)) + 1)))
        if method == "verified":
            self.badge.configure(text="✔ Verified translation", bg=OK_BG, fg=OK_FG)
            note = "Hand-checked translation from the statement collection."
        elif method == "partial":
            self.badge.configure(text="◐ Partly verified", bg=MID_BG, fg=MID_FG)
            note = "Some sentences are verified, the rest was produced by the rule engine."
        else:
            self.badge.configure(text="⚙ Automatic translation", bg=MID_BG, fg=MID_FG)
            note = ("Produced by AFJEN's rule engine (dey → is/are -ing, done → has/have, go → will, no fit → cannot). "
                    "Use “Save as a statement…” to store a corrected, verified version.")
        if unknown:
            note += "   New words - click one to teach it:"
        self.note.configure(text=note)
        for child in self.chip_row.winfo_children():
            child.destroy()
        for word in unknown[:10]:
            RoundButton(self.chip_row, "+ " + word, lambda w=word: self.open_word_dialog(word=w), bg=GOLD_L,
                        hover="#EAD79E", fg="#6A4F0E", size=9, padx=12, pady=5, radius=10).pack(side=tk.LEFT, padx=(0, 8))

        result = analyze_robust(text)
        self._show_tokens(result)
        self._show_structure(result)
        words = [t.value for t in result["tokens"]
                 if t.type not in (TokenType.PUNCTUATION, TokenType.CONNECTOR) or t.value.lower() in ("and", "but", "or")]
        self.bank.record(words)
        if text not in self.history[:1]:
            self.history.insert(0, text)
            del self.history[30:]
        cov = result["coverage"]
        n_sent = len(result["sentences"])
        if all(s["kind"] == "full" for s in result["sentences"]):
            self.pill.configure(text="✔  Fits the AFJEN grammar perfectly", bg=OK_BG, fg=OK_FG)
            self.donut.set(100, "#4E8F6A")
            self.detail.configure(text="Every sentence has a complete LL(1) parse tree.")
        elif cov >= 50:
            self.pill.configure(text=f"◐  {result['matched']} of {result['total']} clauses fit the grammar",
                                bg=MID_BG, fg=MID_FG)
            self.donut.set(cov, GOLD)
            self.detail.configure(text="The rest is informal speech - still translated and analysed word by word.")
        else:
            self.pill.configure(text="◔  Informal speech - analysed word by word", bg=INF_BG, fg=INF_FG)
            self.donut.set(cov, "#8A5BB0")
            self.detail.configure(text="This wording is looser than the strict grammar, so AFJEN read it as fragments.")
        sem = self.semantic.analyze(text)
        self.tiles["words"].configure(text=str(len(words)))
        self.tiles["sentences"].configure(text=str(n_sent))
        self.tiles["category"].configure(text=sem["category"])
        self.tiles["intent"].configure(text=sem["intent"])
        self.refresh_side()
        if hasattr(self, "collected"):
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
            t.insert(tk.END, s["text"][:90] + ("…" if len(s["text"]) > 90 else "") + chr(10), "node")
            if s["kind"] == "full":
                t.insert(tk.END, "  ✔ complete parse" + chr(10), "ok")
            elif s["kind"] == "partial":
                t.insert(tk.END, f"  ◐ {s['matched']} of {s['total']} clauses parsed" + chr(10), "frag")
            else:
                t.insert(tk.END, "  ◔ informal - read as fragments" + chr(10), "frag")
            for tree in s["trees"]:
                self._draw_tree(tree, 1)
            for words, _err in s["fragments"]:
                t.insert(tk.END, f"    fragment: “{words}”" + chr(10), "frag")
            t.insert(tk.END, chr(10))
        t.configure(state=tk.DISABLED)

    def _draw_tree(self, node, depth):
        t, pad = self.tree_text, "   " * depth
        if node.token is not None:
            t.insert(tk.END, f"{pad}└─ ", "node")
            t.insert(tk.END, node.token.value, "leaf")
            t.insert(tk.END, f"  {node.rule}" + chr(10), "node")
        else:
            t.insert(tk.END, f"{pad}▾ {node.rule}" + chr(10), "node")
            for child in node.children:
                self._draw_tree(child, depth + 1)

    # ----------------------------------------------------------- add dialogs --
    def open_word_dialog(self, word=""):
        dlg = Modal(self, "Teach AFJEN a new word",
                    "Give the word and its meanings. It works immediately in the lexer, the parser and the translator.")
        v_word, v_en, v_fr = tk.StringVar(value=word), tk.StringVar(), tk.StringVar()
        v_type, v_gender = tk.StringVar(value="noun"), tk.StringVar(value="m")
        body = dlg.body

        def field(label, var, row, hint=""):
            tk.Label(body, text=label, font=(SANS, 9, "bold"), fg=MUTED, bg=BG).grid(row=row, column=0, sticky="w", pady=(0, 2))
            e = styled_entry(body, var, 34, 12)
            e.grid(row=row + 1, column=0, columnspan=2, sticky="we", ipady=6, pady=(0, 10))
            if hint:
                tk.Label(body, text=hint, font=(SANS, 8), fg=MUTED, bg=BG).grid(row=row, column=1, sticky="e")
            return e

        e_word = field("Word or expression (Pidgin / slang)", v_word, 0)
        tk.Label(body, text="Type", font=(SANS, 9, "bold"), fg=MUTED, bg=BG).grid(row=2, column=0, sticky="w", pady=(0, 2))
        ttk.Combobox(body, textvariable=v_type, values=userdict.TYPES, state="readonly", width=16,
                     font=(SANS, 11)).grid(row=3, column=0, sticky="w", pady=(0, 10), ipady=3)
        tk.Label(body, text="Gender in French (nouns)", font=(SANS, 9, "bold"), fg=MUTED, bg=BG).grid(
            row=2, column=1, sticky="w", padx=(16, 0), pady=(0, 2))
        ttk.Combobox(body, textvariable=v_gender, values=["m", "f"], state="readonly", width=6,
                     font=(SANS, 11)).grid(row=3, column=1, sticky="w", padx=(16, 0), pady=(0, 10), ipady=3)
        e_en = field("English meaning", v_en, 4)
        e_fr = field("Français  (use the infinitive for verbs)", v_fr, 6)
        body.columnconfigure(0, weight=1)

        def submit():
            ok, msg = userdict.add_word(v_word.get(), v_type.get(), v_en.get(), v_fr.get(), v_gender.get())
            dlg.say(msg, ok)
            if ok:
                self._after_data_change()
                v_word.set("")
                v_en.set("")
                v_fr.set("")
                e_word.focus_set()

        for e in (e_word, e_en, e_fr):
            e.bind("<Return>", lambda ev: submit())
        RoundButton(dlg.buttons, "Add word", submit, parent_bg=BG).pack(side=tk.LEFT)
        soft_button(dlg.buttons, "Done", dlg.destroy, parent_bg=BG).pack(side=tk.LEFT, padx=10)
        dlg.finish()
        (e_en if word else e_word).focus_set()

    def open_statement_dialog(self, text="", en="", fr=""):
        dlg = Modal(self, "Add a statement to the collection",
                    "Write the statement exactly as you heard it, then give the correct English and French. "
                    "It becomes a verified translation.", width=700)
        body = dlg.body

        def area(label, value, row, height=2):
            tk.Label(body, text=label, font=(SANS, 9, "bold"), fg=MUTED, bg=BG).grid(row=row, column=0, sticky="w", pady=(0, 2))
            t = tk.Text(body, height=height, width=62, font=(SANS, 11), relief=tk.FLAT, bg="#FBF8F5", fg=INK,
                        highlightthickness=1, highlightbackground=BORDER, highlightcolor=ROSE, wrap=tk.WORD,
                        insertbackground=ROSE, padx=10, pady=8)
            t.grid(row=row + 1, column=0, sticky="we", pady=(0, 10))
            t.insert("1.0", value)
            return t

        t_text = area("Statement (Pidgin / franc-anglais)", text, 0)
        t_en = area("English", en, 2)
        t_fr = area("Français", fr, 4)
        tk.Label(body, text="Topic", font=(SANS, 9, "bold"), fg=MUTED, bg=BG).grid(row=6, column=0, sticky="w", pady=(0, 2))
        v_topic = tk.StringVar(value=statements.topics()[0])
        ttk.Combobox(body, textvariable=v_topic, values=statements.topics(), width=32, font=(SANS, 11)).grid(
            row=7, column=0, sticky="w", ipady=3)
        body.columnconfigure(0, weight=1)

        def submit():
            ok, msg = statements.add_statement(t_text.get("1.0", tk.END), t_en.get("1.0", tk.END),
                                               t_fr.get("1.0", tk.END), v_topic.get())
            dlg.say(msg, ok)
            if ok:
                self._after_data_change()
                dlg.after(700, dlg.destroy)

        RoundButton(dlg.buttons, "Add statement", submit, parent_bg=BG).pack(side=tk.LEFT)
        soft_button(dlg.buttons, "Cancel", dlg.destroy, parent_bg=BG).pack(side=tk.LEFT, padx=10)
        dlg.finish()
        t_text.focus_set() if not text else t_en.focus_set()

    def _after_data_change(self):
        self._fill_dictionary()
        self._fill_statements()
        self.refresh_side()
        self.analyze()

    # ---------------------------------------------------------- page: dictionary --
    def _page_dictionary(self, page):
        wrap = tk.Frame(page, bg=BG)
        wrap.pack(fill=tk.BOTH, expand=True, padx=34, pady=16)
        top = tk.Frame(wrap, bg=BG)
        top.pack(fill=tk.X, pady=(0, 8))
        self.dict_count = tk.Label(top, text="", font=(SERIF, 13, "bold"), fg=PLUM, bg=BG)
        self.dict_count.pack(side=tk.LEFT)
        soft_button(top, "Import CSV", self.import_words, parent_bg=BG, size=9, padx=14, pady=6).pack(side=tk.RIGHT, padx=(8, 0))
        soft_button(top, "Export CSV", self.export_words, parent_bg=BG, size=9, padx=14, pady=6).pack(side=tk.RIGHT, padx=(8, 0))
        soft_button(top, "Remove selected ★", self.remove_selected, parent_bg=BG, size=9, padx=14, pady=6).pack(
            side=tk.RIGHT, padx=(8, 0))
        self.search = tk.StringVar()
        self.search.trace_add("write", lambda *a: self._fill_dictionary())
        styled_entry(top, self.search, 24, 12).pack(side=tk.RIGHT, ipady=6)
        tk.Label(top, text="Search  ", font=(SANS, 10), fg=MUTED, bg=BG).pack(side=tk.RIGHT)

        self.letter = tk.StringVar(value="All")
        self.letter_bar = tk.Frame(wrap, bg=BG)
        self.letter_bar.pack(fill=tk.X, pady=(0, 8))

        card = self._card(wrap, None, fill=tk.BOTH, expand=True)
        frame, self.dict_tree = self._table(card, ("Word", "Type", "English", "Français"), (180, 150, 320, 320))
        frame.pack(fill=tk.BOTH, expand=True)
        self.dict_tree.tag_configure("odd", background="#FBF7F2")
        self.dict_tree.tag_configure("mine", background="#FBEFD2")
        self.form_msg = tk.Label(wrap, text="", font=(SANS, 10), fg=MUTED, bg=BG, anchor="w")
        self.form_msg.pack(fill=tk.X, pady=(8, 0))
        self.collected = tk.Label(wrap, text="", font=(SANS, 10), fg=MUTED, bg=BG, anchor="w", justify=tk.LEFT,
                                  wraplength=1000)
        self.collected.pack(fill=tk.X, pady=(2, 0))
        self._fill_dictionary()

    def _build_letters(self, entries):
        for child in self.letter_bar.winfo_children():
            child.destroy()
        for label in ["All"] + letters(entries):
            active = self.letter.get() == label
            RoundButton(self.letter_bar, label, lambda l=label: self._pick_letter(l),
                        bg=ROSE if active else BLUSH, hover=ROSE_D if active else BLUSH_D,
                        fg="white" if active else PLUM, size=9, bold=active, padx=9, pady=4, radius=8,
                        parent_bg=BG).pack(side=tk.LEFT, padx=(0, 4))

    def _pick_letter(self, label):
        self.letter.set(label)
        self._fill_dictionary()

    def _fill_dictionary(self):
        entries = build_dictionary()
        self._build_letters(entries)
        q = self.search.get().strip().lower()
        pick = self.letter.get()
        self.dict_tree.delete(*self.dict_tree.get_children())
        shown = 0
        for i, row in enumerate(entries):
            if pick != "All" and sort_key(row[0])[:1].upper() != pick:
                continue
            if q and not any(q in str(c).lower() for c in row):
                continue
            tag = "mine" if row[1].startswith("★") else ("odd" if i % 2 else "")
            self.dict_tree.insert("", tk.END, values=row, tags=(tag,) if tag else ())
            shown += 1
        mine = sum(1 for r in entries if r[1].startswith("★"))
        self.dict_count.configure(text=f"{shown} of {len(entries)} words  ·  {mine} added by you ★  ·  A → Z")
        self.dict_refresh_counts()

    def dict_refresh_counts(self):
        unk = self.bank.unknown_words
        msg = f"Word bank: {self.bank.total_unique} different words collected from the text you analysed"
        msg += (f"  ·  {len(unk)} not in the dictionary yet: {', '.join(unk[:15])}{'…' if len(unk) > 15 else ''}"
                if unk else ".")
        self.collected.configure(text=msg)

    def remove_selected(self):
        sel = self.dict_tree.selection()
        if not sel:
            self.form_msg.configure(text="Select one of your ★ words in the list first.")
            return
        word, kind = self.dict_tree.item(sel[0])["values"][:2]
        if not str(kind).startswith("★"):
            self.form_msg.configure(text="Only words you added (★) can be removed.")
            return
        userdict.remove_word(str(word))
        self.form_msg.configure(text=f"Removed “{word}”.")
        self._after_data_change()

    def export_words(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")],
                                            initialfile="afjen_my_words.csv")
        if path:
            n = userdict.export_csv(path)
            self.form_msg.configure(text=f"Exported {n} of your words to {os.path.basename(path)}.")

    def import_words(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv"), ("All files", "*.*")])
        if path:
            added, skipped = userdict.import_csv(path)
            self.form_msg.configure(text=f"Imported {added} words ({skipped} skipped).")
            self._after_data_change()

    # --------------------------------------------------------- page: statements --
    def _page_statements(self, page):
        wrap = tk.Frame(page, bg=BG)
        wrap.pack(fill=tk.BOTH, expand=True, padx=34, pady=16)
        top = tk.Frame(wrap, bg=BG)
        top.pack(fill=tk.X, pady=(0, 10))
        self.stmt_count = tk.Label(top, text="", font=(SERIF, 13, "bold"), fg=PLUM, bg=BG)
        self.stmt_count.pack(side=tk.LEFT)
        soft_button(top, "Export CSV", self.export_statements, parent_bg=BG, size=9, padx=14, pady=6).pack(side=tk.RIGHT, padx=(8, 0))
        soft_button(top, "Remove selected ★", self.remove_statement, parent_bg=BG, size=9, padx=14, pady=6).pack(
            side=tk.RIGHT, padx=(8, 0))
        RoundButton(top, "Analyze selected", self.open_statement, parent_bg=BG, size=9, padx=16, pady=6).pack(side=tk.RIGHT, padx=(8, 0))
        self.stmt_topic = tk.StringVar(value="All topics")
        cb = ttk.Combobox(top, textvariable=self.stmt_topic, values=["All topics"] + statements.topics(),
                          state="readonly", width=24, font=(SANS, 10))
        cb.pack(side=tk.RIGHT, ipady=3)
        cb.bind("<<ComboboxSelected>>", lambda e: self._fill_statements())
        card = self._card(wrap, None, fill=tk.BOTH, expand=True)
        frame, self.stmt_tree = self._table(card, ("#", "Topic", "Source", "Pidgin", "English", "Français"),
                                            (40, 150, 80, 300, 300, 300))
        frame.pack(fill=tk.BOTH, expand=True)
        self.stmt_tree.tag_configure("odd", background="#FBF7F2")
        self.stmt_tree.tag_configure("mine", background="#FBEFD2")
        self.stmt_tree.bind("<Double-1>", lambda e: self.open_statement())
        self.stmt_note = tk.Label(wrap, text="", font=(SANS, 9), fg=MUTED, bg=BG, anchor="w", justify=tk.LEFT,
                                  wraplength=1000)
        self.stmt_note.pack(fill=tk.X, pady=(8, 0))
        self._fill_statements()

    def _fill_statements(self):
        rows = statements.all_statements()
        pick = self.stmt_topic.get()
        self.stmt_tree.delete(*self.stmt_tree.get_children())
        shown = 0
        for i, r in enumerate(rows):
            if pick != "All topics" and r["topic"] != pick:
                continue
            tag = "mine" if r["source"] == "yours" else ("odd" if i % 2 else "")
            label = {"collected": "Collected", "example": "Example", "yours": "Yours ★"}[str(r["source"])]
            self.stmt_tree.insert("", tk.END, values=(r["n"], r["topic"], label, r["text"], r["en"], r["fr"]),
                                  tags=(tag,) if tag else ())
            shown += 1
        collected = sum(1 for r in rows if r["source"] == "collected")
        examples = sum(1 for r in rows if r["source"] == "example")
        mine = sum(1 for r in rows if r["source"] == "yours")
        self.stmt_count.configure(text=f"{shown} of {len(rows)} statements")
        self.stmt_note.configure(
            text=f"{collected} collected in Yaoundé  ·  {examples} further examples  ·  {mine} added by you ★.  "
                 "Double-click a row to analyse it. Replace the examples with statements you heard yourselves.")

    def open_statement(self):
        sel = self.stmt_tree.selection()
        if sel:
            self.load(str(self.stmt_tree.item(sel[0])["values"][3]))

    def remove_statement(self):
        sel = self.stmt_tree.selection()
        if not sel:
            self.stmt_note.configure(text="Select one of your ★ statements first.")
            return
        values = self.stmt_tree.item(sel[0])["values"]
        if "Yours" not in str(values[2]):
            self.stmt_note.configure(text="Only statements you added (★) can be removed.")
            return
        statements.remove_statement(str(values[3]))
        self._after_data_change()

    def export_statements(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")],
                                            initialfile="afjen_statements.csv")
        if path:
            n = statements.export_csv(path)
            self.stmt_note.configure(text=f"Exported {n} statements to {os.path.basename(path)}.")

    # ------------------------------------------------------------ page: insights --
    def _page_insights(self, page):
        wrap = tk.Frame(page, bg=BG)
        wrap.pack(fill=tk.BOTH, expand=True, padx=34, pady=16)
        self.insight_tiles = tk.Frame(wrap, bg=BG)
        self.insight_tiles.pack(fill=tk.X, pady=(0, 14))
        cols = tk.Frame(wrap, bg=BG)
        cols.pack(fill=tk.BOTH, expand=True)
        cols.columnconfigure(0, weight=1, uniform="i")
        cols.columnconfigure(1, weight=1, uniform="i")
        cols.rowconfigure(0, weight=1)
        left = tk.Frame(cols, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        right = tk.Frame(cols, bg=BG)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        c1 = self._card(left, "Most used words (your word bank)", fill=tk.BOTH, expand=True)
        self.chart = tk.Canvas(c1, bg=CARD, highlightthickness=0)
        self.chart.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))
        self.chart.bind("<Configure>", lambda e: self._draw_chart())
        c2 = self._card(right, "History (click to reopen)", fill=tk.BOTH, expand=True)
        box = tk.Frame(c2, bg=CARD)
        box.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))
        self.history_list = tk.Listbox(box, font=(SANS, 11), relief=tk.FLAT, bg="#FDFBF8", fg=INK, activestyle="none",
                                       selectbackground="#F0D8DF", selectforeground=INK, highlightthickness=0)
        sb = ttk.Scrollbar(box, orient=tk.VERTICAL, command=self.history_list.yview)
        self.history_list.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_list.pack(fill=tk.BOTH, expand=True)
        self.history_list.bind("<<ListboxSelect>>", self.open_history)

    def refresh_insights(self):
        for child in self.insight_tiles.winfo_children():
            child.destroy()
        rows = statements.all_statements()
        data = [(len(build_dictionary()), "dictionary words"), (len(rows), "statements"),
                (self.bank.total_unique, "words collected"), (len(self.bank.unknown_words), "waiting to be taught")]
        for value, label in data:
            t = tk.Frame(self.insight_tiles, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
            t.pack(side=tk.LEFT, padx=(0, 12))
            tk.Label(t, text=str(value), font=(SERIF, 22, "bold"), fg=ROSE, bg=CARD).pack(padx=28, pady=(10, 0))
            tk.Label(t, text=label, font=(SANS, 9), fg=MUTED, bg=CARD).pack(padx=28, pady=(0, 10))
        self.history_list.delete(0, tk.END)
        for item in self.history:
            self.history_list.insert(tk.END, item.replace(chr(10), " ")[:110])
        self._draw_chart()

    def _draw_chart(self):
        c = self.chart
        c.delete("all")
        words = self.bank.top_words(10)
        if not words:
            c.create_text(20, 20, anchor="nw", text="Analyse some text and your most used words appear here.",
                          font=(SANS, 11), fill=MUTED)
            return
        w, h = max(c.winfo_width(), 300), max(c.winfo_height(), 200)
        peak = max(n for _, n in words)
        row_h = min(38, (h - 10) / len(words))
        for i, (word, n) in enumerate(words):
            y = 8 + i * row_h
            c.create_text(4, y + row_h / 2, anchor="w", text=word, font=(SANS, 10, "bold"), fill=INK)
            bar = 110 + (w - 190) * n / peak
            round_rect(c, 110, y + 5, max(bar, 122), y + row_h - 5, 6, fill=ROSE if i % 2 == 0 else "#D2779A", outline="")
            c.create_text(max(bar, 122) + 8, y + row_h / 2, anchor="w", text=str(n), font=(SANS, 10), fill=MUTED)

    def open_history(self, _event=None):
        sel = self.history_list.curselection()
        if sel:
            self.load(self.history[sel[0]])

    # -------------------------------------------------------------- page: tests --
    def _page_tests(self, page):
        wrap = tk.Frame(page, bg=BG)
        wrap.pack(fill=tk.BOTH, expand=True, padx=34, pady=16)
        bar = tk.Frame(wrap, bg=BG)
        bar.pack(fill=tk.X, pady=(0, 8))
        RoundButton(bar, "Run all tests", self.run_all, parent_bg=BG).pack(side=tk.LEFT)
        soft_button(bar, "Strict grammar: accept / reject", self.run_accept_reject, parent_bg=BG).pack(side=tk.LEFT, padx=10)
        soft_button(bar, "Export…", self.export, parent_bg=BG).pack(side=tk.RIGHT)
        tk.Label(wrap, text="These exam tests use the strict LL(1) grammar, so they include sentences that are "
                            "deliberately malformed. The Translate page never rejects your text.",
                 font=(SANS, 9), fg=MUTED, bg=BG, anchor="w", wraplength=1000, justify=tk.LEFT).pack(fill=tk.X, pady=(0, 8))
        card = self._card(wrap, None, fill=tk.BOTH, expand=True)
        box, self.results = self._scrolled_text(card, font=(MONO, 10), bg="#FDFBF8", fg=INK, padx=18, pady=12,
                                                wrap=tk.NONE)
        box.pack(fill=tk.BOTH, expand=True)
        self.results.tag_configure("pass", foreground=OK_FG, font=(MONO, 10, "bold"))
        self.results.tag_configure("fail", foreground="#A3121F", font=(MONO, 10, "bold"))
        self.results.tag_configure("head", foreground=PLUM2, font=(MONO, 10, "bold"))
        self.results.insert("1.0", "Press “Run all tests” to run the full suite." + chr(10), "head")

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
            self.results.insert(tk.END, line + chr(10), tag)
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

    # ------------------------------------------------------------- page: grammar --
    def _page_grammar(self, page):
        wrap = tk.Frame(page, bg=BG)
        wrap.pack(fill=tk.BOTH, expand=True, padx=34, pady=16)
        conflicts = len(grammar.find_conflicts())
        prods = sum(len(p) for p in grammar.GRAMMAR.values())
        stats = tk.Frame(wrap, bg=BG)
        stats.pack(fill=tk.X, pady=(0, 12))
        for label, value in (("non-terminals", len(grammar.GRAMMAR)), ("productions", prods),
                             ("table entries", len(grammar.TABLE)), ("LL(1) conflicts", conflicts)):
            c = tk.Frame(stats, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
            c.pack(side=tk.LEFT, padx=(0, 12))
            tk.Label(c, text=str(value), font=(SERIF, 22, "bold"), fg=ROSE, bg=CARD).pack(padx=28, pady=(10, 0))
            tk.Label(c, text=label, font=(SANS, 9), fg=MUTED, bg=CARD).pack(padx=28, pady=(0, 10))
        card = self._card(wrap, None, fill=tk.BOTH, expand=True)
        box, txt = self._scrolled_text(card, font=(MONO, 10), bg="#FDFBF8", fg=INK, padx=18, pady=12, wrap=tk.NONE)
        box.pack(fill=tk.BOTH, expand=True)
        txt.tag_configure("nt", foreground=ROSE_D, font=(MONO, 10, "bold"))
        txt.tag_configure("h", foreground=PLUM2, font=(MONO, 11, "bold"))
        nl = chr(10)
        txt.insert(tk.END, "PRODUCTIONS" + nl, "h")
        for nt, ps in grammar.GRAMMAR.items():
            txt.insert(tk.END, f"{nt:<9}", "nt")
            txt.insert(tk.END, " → " + "  |  ".join(" ".join(p) for p in ps) + nl)
        txt.insert(tk.END, nl + "FIRST / FOLLOW" + nl, "h")
        for nt in grammar.GRAMMAR:
            txt.insert(tk.END, f"{nt:<9}", "nt")
            txt.insert(tk.END, f" FIRST  {{{', '.join(sorted(grammar.FIRST[nt]))}}}" + nl)
            txt.insert(tk.END, f"{'':<9} FOLLOW {{{', '.join(sorted(grammar.FOLLOW[nt]))}}}" + nl)
        txt.configure(state=tk.DISABLED)

    # -------------------------------------------------------------- page: about --
    def _page_about(self, page):
        canvas = tk.Canvas(page, bg=BG, highlightthickness=0)
        vbar = ttk.Scrollbar(page, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=vbar.set)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        wrap = tk.Frame(canvas, bg=BG)
        win = canvas.create_window((0, 0), window=wrap, anchor="nw")
        wrap.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(win, width=e.width))
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-e.delta / 120), "units")
                        if self.current == "about" else (self._wheel_translate(e) if self.current == "translate" else None))
        pad = tk.Frame(wrap, bg=BG)
        pad.pack(fill=tk.BOTH, expand=True, padx=34, pady=(16, 30))

        # hero
        hero = tk.Frame(pad, bg=PLUM)
        hero.pack(fill=tk.X)
        tk.Label(hero, text="The women behind AFJEN", font=(SERIF, 22, "bold"), fg="white", bg=PLUM).pack(
            anchor="w", padx=32, pady=(26, 4))
        tk.Label(hero, text="Founded by Tembong Jennette and Abang Afumbon - the name AFJEN carries the first letters "
                            "of both of them:  AFumbon  +  JENnette.",
                 font=(SANS, 11), fg="#E7D3E4", bg=PLUM, wraplength=1000, justify=tk.LEFT).pack(
            anchor="w", padx=32, pady=(0, 26))
        tk.Frame(pad, height=3, bg=GOLD).pack(fill=tk.X)

        # founders
        row = tk.Frame(pad, bg=BG)
        row.pack(fill=tk.X, pady=(18, 0))
        row.columnconfigure(0, weight=1, uniform="f")
        row.columnconfigure(1, weight=1, uniform="f")
        for col, (initials, name) in enumerate((("TJ", "Tembong Jennette"), ("AA", "Abang Afumbon"))):
            holder = tk.Frame(row, bg=BG)
            holder.grid(row=0, column=col, sticky="nsew", padx=(0, 8) if col == 0 else (8, 0))
            card = self._card(holder, None, fill=tk.BOTH, expand=True)
            inner = tk.Frame(card, bg=CARD)
            inner.pack(fill=tk.X, padx=22, pady=20)
            badge = tk.Canvas(inner, width=76, height=76, bg=CARD, highlightthickness=0)
            badge.pack(side=tk.LEFT)
            badge.create_oval(4, 4, 72, 72, fill=PLUM, outline=GOLD, width=3)
            badge.create_text(38, 38, text=initials, font=(SERIF, 22, "bold"), fill=GOLD)
            text = tk.Frame(inner, bg=CARD)
            text.pack(side=tk.LEFT, padx=18)
            tk.Label(text, text=name, font=(SERIF, 18, "bold"), fg=PLUM, bg=CARD).pack(anchor="w")
            tk.Label(text, text="Founder  ·  co-owner of AFJEN", font=(SANS, 10), fg=ROSE, bg=CARD).pack(anchor="w")
            tk.Label(text, text="Brilliant, brave and relentless.", font=(SERIF, 11, "italic"), fg=MUTED,
                     bg=CARD).pack(anchor="w", pady=(4, 0))

        def story(title, paragraphs, top=16):
            card = self._card(pad, title, fill=tk.X, pady=(top, 0))
            for para in paragraphs:
                tk.Label(card, text=para, font=(SANS, 11), fg=INK, bg=CARD, justify=tk.LEFT, anchor="w",
                         wraplength=1300).pack(fill=tk.X, padx=24, pady=(0, 10))
            tk.Frame(card, height=6, bg=CARD).pack()

        story("Who they are", [
            "AFJEN is the work of two determined women who looked at the way their city really talks - Pidgin, "
            "French, English, Ewondo and street slang, often in a single sentence - and decided that it deserved a "
            "place in computer science. Tembong Jennette and Abang Afumbon do not just write code: they listen, "
            "they care about the words people actually use, and they refuse to let a difficult problem beat them.",
            "Together they turned a hard assignment into something real, useful and beautiful. This project is theirs, "
            "and every line of it carries their effort, their patience and their pride in Yaoundé.",
        ])
        story("How the project came to us - and what it cost", [
            "It began as the final-examination project for CS4110 Compiler Construction at ICT University, set by "
            "Engr. Tanwi Nkiamboh: build a compiler that can read the informal, multilingual speech of Yaoundé - taxis, "
            "markets, bendskins, checkpoints and campus life.",
            "It was not an easy gift. Nothing about it could be copied from a textbook. The words had to be collected "
            "and written down exactly as they were spoken; the grammar broke again and again on real sentences and "
            "had to be rebuilt; there were long hours, setbacks and moments of doubt. They suffered to bring it - and "
            "they kept going until an exam requirement became a working compiler, a translator and a dictionary that "
            "understands the sense behind what people say.",
        ])
        story("How AFJEN works", [
            "1.  You type or paste any amount of Pidgin, franc-anglais, English or French.",
            "2.  Reading the words (lexical analysis): regular expressions cut the text into 18 kinds of token - nouns, "
            "verbs, Pidgin markers like dey, done and fit, numbers, slang, code-mixed phrases - and recognise the "
            "words you taught it.",
            "3.  Checking the structure (syntactic analysis): a table-driven LL(1) parser builds the sentence tree. "
            "Loose, informal sentences are read clause by clause - AFJEN never refuses your text.",
            "4.  Understanding the sense: AFJEN knows expressions by what they mean, not word by word. “you dey ok” "
            "means “you are alright”, but “you dey dey ok so?” means “are you normal?”.",
            "5.  Translating into English or Français: hand-verified translations first, then expressions, then rules "
            "for Pidgin tense (dey = is doing, done = has done, go = will, no fit = cannot, bin = did).",
            "6.  Making it yours: ＋ Add word, ＋ Add statement and Save to file let you keep teaching AFJEN, so it "
            "gets better every time you use it.",
        ])
        tk.Label(pad, text="Made with pride in Yaoundé", font=(SERIF, 14, "italic"), fg=ROSE, bg=BG).pack(pady=(22, 0))

    def _wheel_translate(self, event):
        for child in self.pages["translate"].winfo_children():
            if isinstance(child, tk.Canvas):
                child.yview_scroll(int(-event.delta / 120), "units")
                break


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
