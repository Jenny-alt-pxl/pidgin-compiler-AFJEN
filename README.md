"""
Main Runner Script for Yaoundé Compiler Project
CS4110 - Compiler Construction
Runs lexical analysis, parsing, and full test suite
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))

from lexical_analyzer import LexicalAnalyzer
from parser import parse_statement
from semantic_analyzer import SemanticAnalyzer
from test_cases import TestRunner


def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def run_single_statement_analysis(statement: str):
    """Analyze a single statement"""
    print_header(f"ANALYZING: {statement[:70]}")
    
    # Lexical Analysis
    analyzer = LexicalAnalyzer()
    tokens = analyzer.tokenize(statement)
    
    print("LEXICAL ANALYSIS")
    print("-" * 80)
    print(f"Tokens extracted: {len(tokens) - 1}\n")
    analyzer.print_tokens(tokens)
    
    # Syntactic Analysis
    tree, success, _ = parse_statement(statement)
    print("\n\nSYNTACTIC ANALYSIS")
    print("-" * 80)
    print(f"Parse Result: {'✓ ACCEPTED' if success else '✗ REJECTED'}\n")
    
    if tree:
        print("Parse Tree:")
        tree.print_tree()

    # Semantic Analysis
    semantic = SemanticAnalyzer()
    result = semantic.analyze(statement)
    print("\n\nSEMANTIC ANALYSIS")
    print("-" * 80)
    print(f"Category: {result['category']}")
    print(f"Intent: {result['intent']}")
    print(f"Valid syntax: {'yes' if result['valid_syntax'] else 'no'}")
    
    return success


def run_demo():
    """Run demo with a few sample statements"""
    print_header("YAOUNDÉ COMPILER - INTERACTIVE DEMO")
    
    demo_statements = [
        "Brother, drop me na at Carrefour Yaoundé",
        "The light done cut again",
        "Internet dey do again? I try restart modem",
    ]
    
    for i, stmt in enumerate(demo_statements, 1):
        success = run_single_statement_analysis(stmt)
        print("\n")
    
    print_header("DEMO COMPLETE")


def run_full_test_suite():
    """Run comprehensive test suite on all 15 statements"""
    runner = TestRunner()
    runner.run_all_tests()
    
    # Generate report
    report_path = os.path.join("analysis", "test_report.txt")
    print(f"\n\nGenerating test report: {report_path}")
    runner.generate_report(report_path)


def generate_semantic_report():
    """Generate semantic analysis JSON output for the full corpus."""
    analyzer = SemanticAnalyzer()
    report_path = analyzer.generate_report("analysis/semantic_report.json")
    print_header("SEMANTIC REPORT GENERATED")
    print(f"Report saved to: {report_path}")
    return report_path


def show_menu():
    """Show interactive menu"""
    while True:
        print_header("YAOUNDÉ COMPILER PROJECT - MAIN MENU")
        print("1. Run Demo Analysis (3 sample statements)")
        print("2. Analyze Single Statement (enter your own)")
        print("3. Run Full Test Suite (all 15 statements)")
        print("4. Generate Semantic Report (JSON)")
        print("5. View Project Information")
        print("6. Exit")
        print()
        
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == "1":
            run_demo()
            
        elif choice == "2":
            stmt = input("\nEnter a statement to analyze: ").strip()
            if stmt:
                run_single_statement_analysis(stmt)
            else:
                print("No statement entered.")
                
        elif choice == "3":
            run_full_test_suite()
            
        elif choice == "4":
            generate_semantic_report()
            
        elif choice == "5":
            show_project_info()
            
        elif choice == "6":
            print("\nThank you for using Yaoundé Compiler!")
            sys.exit(0)
            
        else:
            print("\nInvalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


def show_project_info():
    """Display project information"""
    print_header("PROJECT INFORMATION")
    
    info = """
YAOUNDÉ COMPILER CONSTRUCTION PROJECT
Course: CS4110 - Compiler Construction
Instructor: Engr. Tanwi Nkiamboh
Institution: ICT University

PROJECT OBJECTIVE:
Design and implement a mini-language analyzer for lexical and syntactic analysis
of informal urban communication in Yaoundé, detecting patterns related to:
- Commuting and transportation
- Market activities
- Security issues
- Weather and environment
- Electricity and utilities
- Everyday transactions
- University life

KEY FEATURES:
✓ Lexical Analysis: 15 token types
✓ Token Specification: Regex patterns for all token types
✓ Context-Free Grammar: Complete CFG for Yaoundé patterns
✓ LL(1) Parser: Predictive recursive descent parser
✓ Test Suite: 15 collected authentic statements
✓ Analysis: FIRST/FOLLOW sets, LL(1) parsing table
✓ Documentation: Complete project documentation

COLLECTED DATA:
- 15 authentic statements from Yaoundé
- 140+ total tokens
- 100+ unique tokens
- 15 token type categories

LINGUISTIC PATTERNS CAPTURED:
- Code-mixing (French, English, Pidgin)
- Pidgin aspect markers (dey, done, go, fit)
- Urban slang (garrr, ekiee, wahala, zéro-zéro)
- Non-standard syntax patterns
- Elliptical and fragmentary speech

PROJECT FILES:
├── data/
│   ├── collected_statements.txt    - 15 authentic statements
│   ├── token_specification.md      - Token types & patterns
│   └── grammar_rules.md            - CFG production rules
├── src/
│   ├── lexical_analyzer.py         - Tokenizer
│   └── parser.py                   - LL(1) parser
├── tests/
│   └── test_cases.py               - Test suite
├── analysis/
│   ├── first_follow_sets.md        - FIRST/FOLLOW calculation
│   ├── ll1_parsing_table.md        - LL(1) parsing table
│   └── test_report.txt             - Generated test results
└── README.md                       - Full documentation

USAGE:
1. Run demo: analyzes 3 sample statements
2. Analyze custom: enter any statement for analysis
3. Full test: runs all 15 collected statements
4. View results: parsing tree, token details, acceptance status

DELIVERABLES:
[✓] Data Collection (10 marks)
[✓] Token Specification & Lexical Analysis (10 marks)
[✓] Token Frequency Analysis (10 marks)
[✓] CFG Design & Transformation (20 marks)
[✓] LL(1) Parsing Table (20 marks)
[✓] Parser Implementation (10 marks)
[✓] Testing & Validation (10 marks)
[✓] Documentation & Report (10 marks)

STATUS: Complete and Ready for Presentation
"""
    
    print(info)


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Command-line mode
        if sys.argv[1] == "demo":
            run_demo()
        elif sys.argv[1] == "test":
            run_full_test_suite()
        elif sys.argv[1] in {"report", "export-json"}:
            generate_semantic_report()
        elif sys.argv[1] == "analyze" and len(sys.argv) > 2:
            statement = " ".join(sys.argv[2:])
            run_single_statement_analysis(statement)
        else:
            print("Usage:")
            print("  python main.py demo              - Run demo")
            print("  python main.py test              - Run full test suite")
            print("  python main.py analyze <text>    - Analyze custom statement")
            print("  python main.py report            - Export semantic analysis JSON")
            print("  python main.py export-json       - Alias for report")
            print("  python main.py                   - Interactive menu")
    else:
        # Interactive mode
        show_menu()


if __name__ == "__main__":
    main()
