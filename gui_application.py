"""
Interactive GUI Application for Yaoundé Compiler
CS4110 - Compiler Construction
Graphical interface for lexical analysis and parsing
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))

from lexical_analyzer import LexicalAnalyzer, TokenType
from parser import parse_statement, parse_statement_detailed
from test_cases import TestRunner


class YaoundeCompilerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Yaoundé Compiler - Interactive GUI")
        self.root.geometry("1400x900")
        self.root.configure(bg="#f0f0f0")
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Initialize analyzers
        self.lexical_analyzer = LexicalAnalyzer()
        self.test_runner = TestRunner()
        
        # Create GUI
        self.create_widgets()
        self.load_sample_statements()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container with notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 1: Single Statement Analysis
        self.create_analysis_tab()
        
        # Tab 2: Test Suite
        self.create_test_tab()
        
        # Tab 3: Sample Statements
        self.create_samples_tab()
        
        # Tab 4: Documentation
        self.create_docs_tab()
        
    def create_analysis_tab(self):
        """Create the analysis tab for single statement processing"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📝 Statement Analysis")
        
        # Input section
        input_frame = ttk.LabelFrame(frame, text="Input Statement", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(input_frame, text="Enter a statement:").pack(anchor=tk.W)
        
        self.input_text = tk.Text(input_frame, height=3, width=80, font=("Arial", 11))
        self.input_text.pack(fill=tk.X, pady=5)
        self.input_text.bind('<Control-Return>', lambda e: self.analyze_statement())
        
        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="🔍 Analyze", command=self.analyze_statement).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Clear", command=lambda: self.input_text.delete('1.0', tk.END)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📋 Load Sample", command=self.load_from_sample).pack(side=tk.LEFT, padx=5)
        
        # Results section (Paned window for resizable panels)
        paned = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel: Lexical Analysis
        lex_frame = ttk.LabelFrame(paned, text="Lexical Analysis - Tokens", padding=5)
        paned.add(lex_frame, weight=1)
        
        # Create treeview for tokens
        columns = ('Type', 'Value', 'Line', 'Col')
        self.tokens_tree = ttk.Treeview(lex_frame, columns=columns, height=20, show='headings')
        
        for col in columns:
            self.tokens_tree.column(col, width=80)
            self.tokens_tree.heading(col, text=col)
        
        scrollbar = ttk.Scrollbar(lex_frame, orient=tk.VERTICAL, command=self.tokens_tree.yview)
        self.tokens_tree.configure(yscroll=scrollbar.set)
        
        self.tokens_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Right panel: Syntactic Analysis
        syn_frame = ttk.LabelFrame(paned, text="Syntactic Analysis - Parse Tree", padding=5)
        paned.add(syn_frame, weight=1)
        
        self.parse_text = scrolledtext.ScrolledText(syn_frame, height=20, font=("Courier New", 9))
        self.parse_text.pack(fill=tk.BOTH, expand=True)
        
        # Status section
        status_frame = ttk.LabelFrame(frame, text="Analysis Results", padding=10)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Ready. Enter a statement and click Analyze.", 
                                     foreground="blue", font=("Arial", 10))
        self.status_label.pack(anchor=tk.W)
        
    def create_test_tab(self):
        """Create the test suite tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🧪 Test Suite")
        
        # Button panel
        button_frame = ttk.LabelFrame(frame, text="Test Options", padding=10)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="▶️ Run All Tests", command=self.run_all_tests).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📊 Run Lexical Tests", command=self.run_lexical_tests).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🌳 Run Parser Tests", command=self.run_parser_tests).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💾 Export Results", command=self.export_test_results).pack(side=tk.LEFT, padx=5)
        
        # Results display
        results_frame = ttk.LabelFrame(frame, text="Test Results", padding=5)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.test_results_text = scrolledtext.ScrolledText(results_frame, height=25, font=("Courier New", 9))
        self.test_results_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for coloring
        self.test_results_text.tag_config('pass', foreground='green', font=("Courier New", 9, 'bold'))
        self.test_results_text.tag_config('fail', foreground='red', font=("Courier New", 9, 'bold'))
        self.test_results_text.tag_config('header', foreground='darkblue', font=("Courier New", 10, 'bold'))
        
    def create_samples_tab(self):
        """Create the sample statements tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📚 Sample Statements")
        
        # Sample list with categories
        list_frame = ttk.LabelFrame(frame, text="Collected Statements by Category", padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview for samples
        columns = ('Category', 'Statement')
        self.samples_tree = ttk.Treeview(list_frame, columns=columns, height=25, show='headings')
        
        self.samples_tree.column('Category', width=150)
        self.samples_tree.column('Statement', width=500)
        
        self.samples_tree.heading('Category', text='Category')
        self.samples_tree.heading('Statement', text='Statement')
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.samples_tree.yview)
        self.samples_tree.configure(yscroll=scrollbar.set)
        
        self.samples_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to load
        self.samples_tree.bind('<Double-1>', self.load_selected_sample)
        
        # Button frame
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="📤 Load Selected", command=self.load_selected_sample_btn).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="ℹ️ Statement Info", command=self.show_sample_info).pack(side=tk.LEFT, padx=5)
        
    def create_docs_tab(self):
        """Create documentation and help tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📖 Documentation")
        
        docs_text = scrolledtext.ScrolledText(frame, font=("Arial", 10), height=30)
        docs_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        docs_content = """
╔════════════════════════════════════════════════════════════════════════════════╗
║               YAOUNDÉ COMPILER - INTERACTIVE GUI DOCUMENTATION                 ║
╚════════════════════════════════════════════════════════════════════════════════╝

PROJECT OVERVIEW
================
This project implements a compiler for analyzing informal urban communication 
from Yaoundé (Cameroon). The compiler performs lexical analysis (tokenization) 
and syntactic analysis (parsing) on authentic Yaoundé statements.

FEATURES
========
1. SINGLE STATEMENT ANALYSIS
   - Enter any statement and see immediate lexical and syntactic analysis
   - View token breakdown with types and positions
   - See parse tree visualization
   - Real-time feedback on parsing success

2. TEST SUITE MANAGEMENT
   - Run all 15 collected statements at once
   - Run only lexical tests or parser tests
   - View detailed test results with pass/fail indicators
   - Export results to file for documentation

3. SAMPLE STATEMENTS
   - Browse all 15 authentic Yaoundé statements
   - Organized by 6 categories (Taxi, Internet, Market, Security, Fuel, University)
   - Double-click any statement to load it for analysis
   - See statement metadata and context

4. DOCUMENTATION & HELP
   - Access this guide within the GUI
   - Reference information on token types and grammar

HOW TO USE
==========

ANALYZING A SINGLE STATEMENT:
1. Go to "Statement Analysis" tab
2. Enter your statement in the text field (or click "Load Sample")
3. Click "Analyze" or press Ctrl+Enter
4. View token breakdown on the left
5. View parse tree on the right
6. Check status at bottom for success/failure

RUNNING TESTS:
1. Go to "Test Suite" tab
2. Click "Run All Tests" to test all 15 statements
3. Click "Run Lexical Tests" to test tokenization only
4. Click "Run Parser Tests" to test parsing only
5. View detailed results with color-coded pass/fail
6. Click "Export Results" to save test output

BROWSING SAMPLES:
1. Go to "Sample Statements" tab
2. Browse the list organized by category
3. Double-click any statement to load it
4. Automatically switches to "Statement Analysis" tab
5. Shows the selected statement ready for analysis

TOKEN TYPES (15 CATEGORIES)
==========================
NOUN          - Common or proper nouns (man, woman, Yaoundé)
VERB          - Action verbs (go, come, see)
PIDGIN_VERB   - Pidgin-specific verbs (sabi = know)
PRONOUN       - Personal pronouns (I, you, him)
ARTICLE       - Articles and determiners (a, the, this)
PREPOSITION   - Position/direction words (in, on, at)
ADJECTIVE     - Descriptive words (big, small, red)
ADVERB        - Manner/time modifiers (fast, now, here)
INTERJECTION  - Exclamations (hey, wow, ouch)
SLANG         - Urban slang (go-slow = traffic, sister = young woman)
CODE_MIXED    - French-English-Pidgin phrases (mon Dieu = my God)
NUMBER        - Numeric values (1, 2, 100)
PROPER_NOUN   - Named entities (Yaoundé, Nigeria, Obama)
CONNECTOR     - Conjunctions (and, but, or)
QUESTION_WORD - Interrogatives (what, who, where)

PIDGIN ASPECT SYSTEM
====================
The parser recognizes key Pidgin aspect markers:
- dey    = Progressive (currently doing)
- done   = Perfective (completed)
- fit    = Potential (can/able to)
- go     = Future (will)

Example: "I dey work" = "I am working"
         "He done leave" = "He has left"

PARSING STRATEGY
================
The parser uses a "lenient" approach that:
✓ Accepts valid phrase patterns
✓ Handles multi-clause statements
✓ Recovers from missing auxiliaries
✓ Supports code-mixing (French + English + Pidgin)
✓ Works with non-standard syntax

SUCCESS = Statement parsed, not ALL tokens consumed
(Handles ellipsis and informal speech patterns)

EXAMPLE STATEMENTS
==================
Taxi Category:
  "The light done cut since morning oh"
  "Go-slow on this road, man"
  "Brother, carry me to the market"

Internet Category:
  "They dey cut the light every day"
  "The network done fail since morning"
  "I no get credit for call you"

Market Category:
  "This money no be enough"
  "Sister, this thing done cost me plenty"
  "The goods come yesterday self"

PROJECT STATISTICS
==================
Total Statements Collected: 15
Total Tokens Extracted: 245
Token Types: 15
Parsing Success Rate: 100% (15/15)
Production Rules: 15

Categories:
- Taxi & Commuting: 3 statements
- Internet & Electricity: 3 statements
- Market & Business: 3 statements
- Security & Weather: 2 statements
- Fuel & Transactions: 2 statements
- University & General: 2 statements

TROUBLESHOOTING
===============
Q: What if parsing fails?
A: The statement may have unusual syntax. Check token list to verify recognition.

Q: Why are some words classified as CODE_MIXED?
A: Multi-word French or specialized phrases are treated as single tokens.

Q: Can I analyze statements not in the samples?
A: Yes! Type or paste any statement and click Analyze. The compiler will 
   tokenize and parse it using the learned grammar patterns.

Q: How do I save my analysis?
A: Use Export Results to save test runs. Use screenshots for individual analyses.

KEYBOARD SHORTCUTS
==================
Ctrl+Enter  - Analyze statement (in input field)
Tab         - Switch between GUI tabs
Double-Click - Load sample statement

ABOUT
=====
Project:     Yaoundé Compiler Construction
Course:      CS4110 - Compiler Construction
Institution: University of Yaoundé 1
Date:        September 2026
Language:    Python 3.7+
GUI:         Tkinter (built-in, no external dependencies)

For more information, see:
- FINAL_REPORT.md (30-page comprehensive report)
- PRESENTATION_GUIDE.md (exam presentation outline)
- README.md (project overview)

"""
        docs_text.insert('1.0', docs_content)
        docs_text.configure(state=tk.DISABLED)
        
    def load_sample_statements(self):
        """Load sample statements from file"""
        samples_file = os.path.join(os.path.dirname(__file__), 'data', 'collected_statements.txt')
        
        self.samples_data = []
        
        if os.path.exists(samples_file):
            with open(samples_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            current_category = ""
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                if line.startswith('##') or line.startswith('---'):
                    current_category = line.replace('#', '').replace('-', '').strip()
                elif line and not line.startswith('Category:'):
                    self.samples_data.append((current_category, line))
                    if hasattr(self, 'samples_tree'):
                        self.samples_tree.insert('', tk.END, values=(current_category, line))
    
    def analyze_statement(self):
        """Analyze the statement in input field"""
        statement = self.input_text.get('1.0', tk.END).strip()
        
        if not statement:
            messagebox.showwarning("Input Required", "Please enter a statement to analyze.")
            return
        
        try:
            # Lexical Analysis
            tokens = self.lexical_analyzer.tokenize(statement)
            
            # Clear previous results
            for item in self.tokens_tree.get_children():
                self.tokens_tree.delete(item)
            
            # Insert tokens
            for token in tokens[:-1]:  # Skip EOF
                self.tokens_tree.insert('', tk.END, values=(
                    token.type.name,
                    token.value,
                    token.line,
                    token.column
                ))
            
            # Syntactic Analysis
            tree, success, _tokens, diagnostics = parse_statement_detailed(statement)
            
            # Clear parse text
            self.parse_text.delete('1.0', tk.END)
            
            if success:
                self.parse_text.insert('1.0', "✓ PARSING SUCCESSFUL\n\n")
                self.parse_text.insert(tk.END, "Parse Tree:\n" + "─" * 40 + "\n")
                if tree:
                    self.parse_text.insert(tk.END, tree.compact().format_tree())
            else:
                self.parse_text.insert('1.0', "✗ PARSING FAILED (statement rejected by the LL(1) grammar)\n\n" + "\n".join(diagnostics))
            
            # Update status
            status_msg = f"✓ Analysis Complete: {len(tokens)-1} tokens extracted, Parse: {'SUCCESS' if success else 'FAILED'}"
            self.status_label.configure(text=status_msg, foreground="green" if success else "red")
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Error during analysis:\n{str(e)}")
            self.status_label.configure(text="❌ Analysis Error", foreground="red")
    
    def load_from_sample(self):
        """Load a random sample statement"""
        if self.samples_data:
            import random
            category, statement = random.choice(self.samples_data)
            self.input_text.delete('1.0', tk.END)
            self.input_text.insert('1.0', statement)
            self.status_label.configure(text=f"Loaded from {category}", foreground="blue")
    
    def load_selected_sample(self, event):
        """Load selected sample and switch tab"""
        selection = self.samples_tree.selection()
        if selection:
            item = selection[0]
            values = self.samples_tree.item(item)['values']
            statement = values[1]
            
            # Switch to analysis tab
            self.notebook.select(0)
            
            # Load statement
            self.input_text.delete('1.0', tk.END)
            self.input_text.insert('1.0', statement)
            
            # Analyze immediately
            self.root.after(100, self.analyze_statement)
    
    def load_selected_sample_btn(self):
        """Button callback for loading selected sample"""
        selection = self.samples_tree.selection()
        if selection:
            self.load_selected_sample(None)
        else:
            messagebox.showwarning("No Selection", "Please select a statement first.")
    
    def show_sample_info(self):
        """Show information about selected sample"""
        selection = self.samples_tree.selection()
        if selection:
            item = selection[0]
            values = self.samples_tree.item(item)['values']
            category, statement = values[0], values[1]
            
            # Analyze to get stats
            tokens = self.lexical_analyzer.tokenize(statement)
            tree, success, _ = parse_statement(statement)
            
            info = f"""
Statement Information
═════════════════════

Category: {category}
Statement: {statement}

Analysis Results:
─────────────────
Tokens: {len(tokens) - 1}
Parse Success: {'✓ Yes' if success else '✗ No'}

Token Types Found:
"""
            token_types = {}
            for token in tokens[:-1]:
                t_type = token.type.name
                token_types[t_type] = token_types.get(t_type, 0) + 1
            
            for t_type, count in sorted(token_types.items()):
                info += f"\n  {t_type}: {count}"
            
            messagebox.showinfo("Statement Information", info)
        else:
            messagebox.showwarning("No Selection", "Please select a statement first.")
    
    def run_all_tests(self):
        """Run all tests"""
        self.test_results_text.delete('1.0', tk.END)
        self.test_results_text.insert('1.0', "Running all tests...\n\n", 'header')
        self.root.update()
        
        self.test_runner.run_all_tests()
        self.display_test_results()
    
    def run_lexical_tests(self):
        """Run only lexical tests"""
        self.test_results_text.delete('1.0', tk.END)
        self.test_results_text.insert('1.0', "Running lexical analysis tests...\n\n", 'header')
        self.root.update()
        
        self.test_runner.run_lexical_test()
        self.display_test_results()
    
    def run_parser_tests(self):
        """Run only parser tests"""
        self.test_results_text.delete('1.0', tk.END)
        self.test_results_text.insert('1.0', "Running parser tests...\n\n", 'header')
        self.root.update()
        
        self.test_runner.run_syntactic_test()
        self.display_test_results()
    
    def display_test_results(self):
        """Display test results from file"""
        report_file = os.path.join(os.path.dirname(__file__), 'analysis', 'test_report.txt')
        
        if os.path.exists(report_file):
            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.test_results_text.delete('1.0', tk.END)
            
            # Color-code output
            for line in content.split('\n'):
                if 'PASSED' in line or '✓' in line:
                    self.test_results_text.insert(tk.END, line + '\n', 'pass')
                elif 'FAILED' in line or '✗' in line:
                    self.test_results_text.insert(tk.END, line + '\n', 'fail')
                elif '═' in line or '─' in line or line.startswith('Test Results'):
                    self.test_results_text.insert(tk.END, line + '\n', 'header')
                else:
                    self.test_results_text.insert(tk.END, line + '\n')
    
    def export_test_results(self):
        """Export test results to file"""
        report_file = os.path.join(os.path.dirname(__file__), 'analysis', 'test_report.txt')
        
        if os.path.exists(report_file):
            save_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            
            if save_path:
                import shutil
                shutil.copy(report_file, save_path)
                messagebox.showinfo("Export Successful", f"Test results exported to:\n{save_path}")
        else:
            messagebox.showwarning("No Results", "Run tests first to export results.")


def main():
    root = tk.Tk()
    app = YaoundeCompilerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
