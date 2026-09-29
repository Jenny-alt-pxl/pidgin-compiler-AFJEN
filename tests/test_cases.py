"""
Test Cases for Yaoundé Compiler
CS4110 - Compiler Construction
Tests lexical and syntactic analysis on all 15 collected statements
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lexical_analyzer import LexicalAnalyzer, TokenType
from parser import Parser, parse_statement, parse_statement_detailed
from semantic_analyzer import SemanticAnalyzer


class TestRunner:
    """Runs tests and generates reports"""
    
    def __init__(self):
        self.analyzer = LexicalAnalyzer()
        self.test_results = []
    
    # Test statements from data collection
    TEST_STATEMENTS = [
        # Taxi & Commuting Issues
        ("stmt_001", "Brother, drop me na at Carrefour Yaoundé, the traffic done tire me small"),
        ("stmt_002", "Hala me small money, na five hundred francs remain for transport"),
        ("stmt_003", "Taxi! Yaoundé, Yaoundé! Fill am make we go, pas time dey waka!"),
        
        # Internet & Electricity
        ("stmt_004", "Eh mon Dieu, internet dey do again? I don try restart modem, garrr nothing!"),
        ("stmt_005", "The light done cut again, zéro-zéro, na generator we dey use since morning"),
        ("stmt_006", "Je wanda why MTN network no fit work for this quarter, it's always down-down"),
        
        # Market Bargaining & Roadside Business
        ("stmt_007", "Mama, make you reduce am na small, two thousand francs too much for tomatoes, ekiee"),
        ("stmt_008", "Chop na fresh, fresh! Come take am now, I give you good price, no wahala"),
        ("stmt_009", "Brother, the bendskin dey charge too much, five hundred for two kilometers, c'est cher ooo"),
        
        # Security & Rainy Season
        ("stmt_010", "They say checkpoint ahead, document dey for front, make we be careful pass"),
        ("stmt_011", "Rain don fall so, the road done become mud, car stuck for quartier Mambanda"),
        
        # Fuel Scarcity & Everyday Transactions
        ("stmt_012", "Petrol dey scarce, pump don empty again, we go wait small before go fill tank"),
        ("stmt_013", "How much for this phone airtime? OK, load me two thousand balance make I browse"),
        
        # University & General Slang
        ("stmt_014", "Lecture done start, prof say come sit down, but the class dey too crowded, hmmm"),
        ("stmt_015", "After exam finish, we go for beer na, relax small, this semester done tire me"),
    ]
    
    # Extra grammatical sentences (NOT in the collected data) - the grammar must generalise
    EXTRA_ACCEPT = [
        "The taxi don reach Carrefour",
        "Driver, stop here",
        "I no fit pay five hundred",
        "Mama, sell me tomatoes",
        "The network dey slow",
        "Why the bendskin dey charge too much?",
        "Rain dey fall, the road dey wet",
        "Chauffeur, drop me na at Mvog-Ada, make we go",
        "How much for this ticket?",
        "Eh, the light don go again, hmmm",
        "Police dey for checkpoint, show your document",
        "We dey wait for taxi since morning",
        "How you dey?",
        "I dey, thank you",
    ]

    # Malformed sequences - the grammar must reject every one of them
    REJECT = [
        "the the the",
        "for for at",
        "dey dey dey",
        "Brother",
        "",
        "na na",
        "done light cut",
        "at Carrefour",
        "make",
        "the light the",
        "fit dey done",
        "How Why What",
        "Carrefour Yaoundé Mambanda",
        "The the light done cut",
    ]

    def run_accept_reject_tests(self) -> bool:
        """Print accepted/rejected results for collected, extra and malformed sentences."""
        sections = [
            ("COLLECTED STATEMENTS (must be ACCEPTED)", [s for _, s in self.TEST_STATEMENTS], True),
            ("EXTRA GRAMMATICAL SENTENCES (must be ACCEPTED)", self.EXTRA_ACCEPT, True),
            ("MALFORMED SEQUENCES (must be REJECTED)", self.REJECT, False),
        ]
        all_ok = True
        print("=" * 80)
        print("ACCEPTED / REJECTED SENTENCE TESTS (strict LL(1) parser)")
        print("=" * 80)
        for title, sentences, expect in sections:
            print(f"\n{title}")
            print("-" * 80)
            good = 0
            for text in sentences:
                _, accepted, _, diag = parse_statement_detailed(text)
                ok = accepted == expect
                good += ok
                all_ok &= ok
                verdict = "ACCEPTED" if accepted else "REJECTED"
                label = repr(text) if not text else text
                print(f"  [{'PASS' if ok else 'FAIL'}] {verdict:<9} {label[:70]}")
                if not accepted:
                    print(f"         {diag[0][:120]}")
            print(f"  -> {good}/{len(sentences)} as expected")
        print("\n" + ("ALL ACCEPT/REJECT TESTS PASSED" if all_ok else "SOME TESTS FAILED"))
        return all_ok

    def run_lexical_test(self, stmt_id: str, statement: str) -> dict:
        """Test lexical analysis on a statement"""
        tokens = self.analyzer.tokenize(statement)
        
        # Count token types
        token_counts = {}
        for token in tokens:
            if token.type != TokenType.EOF:
                type_name = token.type.value
                token_counts[type_name] = token_counts.get(type_name, 0) + 1
        
        return {
            "stmt_id": stmt_id,
            "statement": statement,
            "total_tokens": len(tokens) - 1,  # Exclude EOF
            "token_types": token_counts,
            "tokens": [t for t in tokens if t.type != TokenType.EOF]
        }
    
    def run_syntactic_test(self, stmt_id: str, statement: str) -> dict:
        """Test syntactic analysis on a statement"""
        tree, success, tokens = parse_statement(statement)
        
        return {
            "stmt_id": stmt_id,
            "statement": statement,
            "accepted": success,
            "tokens_count": len(tokens) - 1,
            "tree": tree
        }
    
    def run_semantic_test(self, stmt_id: str, statement: str) -> dict:
        """Test semantic classification and AST generation"""
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(statement)
        return {
            "stmt_id": stmt_id,
            "statement": statement,
            "category": result["category"],
            "intent": result["intent"],
            "valid_syntax": result["valid_syntax"],
            "ast": result["ast"],
        }

    def run_ast_diagnostic_test(self, stmt_id: str, statement: str) -> dict:
        """Assert parser returns a structured AST and detailed diagnostics."""
        tree, success, tokens, diagnostics = parse_statement_detailed(statement)
        return {
            "stmt_id": stmt_id,
            "statement": statement,
            "accepted": success,
            "tree_present": tree is not None,
            "diagnostics": diagnostics,
            "token_count": len(tokens) - 1,
        }

    def run_semantic_report_test(self) -> str:
        """Export semantic analysis results to JSON and ensure the report file is created."""
        analyzer = SemanticAnalyzer()
        report_path = analyzer.generate_report(output_file="analysis/semantic_report.json")
        return report_path

    def run_summary_report_test(self) -> str:
        """Export a human-readable semantic summary file for the corpus."""
        analyzer = SemanticAnalyzer()
        report_path = analyzer.generate_summary(output_file="analysis/semantic_summary.txt")
        return report_path

    def run_all_tests(self):
        """Run all tests"""
        print("="*80)
        print("AFJEN COMPILER - COMPREHENSIVE TEST SUITE")
        print("CS4110 - Compiler Construction")
        print("="*80)
        
        # Summary statistics
        total_tests = len(self.TEST_STATEMENTS)
        passed_lexical = 0
        passed_syntactic = 0
        passed_semantic = 0
        passed_ast = 0
        
        # Test each statement
        for stmt_id, statement in self.TEST_STATEMENTS:
            print(f"\n{stmt_id.upper()}: {statement[:70]}...")
            
            # Lexical Analysis
            lex_result = self.run_lexical_test(stmt_id, statement)
            print(f"  Lexical: {lex_result['total_tokens']} tokens identified")
            print(f"    Token breakdown: ", end="")
            print(", ".join([f"{k}({v})" for k, v in sorted(lex_result['token_types'].items())]))
            passed_lexical += 1
            
            # Syntactic Analysis
            syn_result = self.run_syntactic_test(stmt_id, statement)
            status = "✓ ACCEPTED" if syn_result['accepted'] else "✗ REJECTED"
            print(f"  Syntactic: {status}")
            passed_syntactic += (1 if syn_result['accepted'] else 0)

            # Semantic Analysis
            sem_result = self.run_semantic_test(stmt_id, statement)
            print(f"  Semantic: {sem_result['category']} / {sem_result['intent']}")
            passed_semantic += (1 if sem_result['valid_syntax'] and sem_result['category'] else 0)

            # AST & Diagnostics check
            ast_result = self.run_ast_diagnostic_test(stmt_id, statement)
            print(f"  AST Diagnostics: {len(ast_result['diagnostics'])} issues")
            passed_ast += (1 if ast_result['tree_present'] else 0)

            if stmt_id == 'stmt_001':
                report_path = self.run_semantic_report_test()
                print(f"  Semantic Report: {report_path}")
                summary_path = self.run_summary_report_test()
                print(f"  Summary Report: {summary_path}")
            
            self.test_results.append({
                'id': stmt_id,
                'statement': statement,
                'lexical': lex_result,
                'syntactic': syn_result,
                'semantic': sem_result,
                'ast_diagnostics': ast_result
            })
        
        # Summary
        print(f"\n{'='*80}")
        print("TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total Statements Tested: {total_tests}")
        print(f"Lexical Analysis: {passed_lexical}/{total_tests} passed ({100*passed_lexical//total_tests}%)")
        print(f"Syntactic Analysis: {passed_syntactic}/{total_tests} passed ({100*passed_syntactic//total_tests}%)")
        print(f"Semantic Analysis: {passed_semantic}/{total_tests} passed ({100*passed_semantic//total_tests}%)")
        print(f"AST Diagnostics: {passed_ast}/{total_tests} passed ({100*passed_ast//total_tests}%)")
        self.accept_reject_ok = self.run_accept_reject_tests()
        
        # Token frequency statistics
        print(f"\n{'='*80}")
        print("TOKEN FREQUENCY ANALYSIS (ALL STATEMENTS)")
        print(f"{'='*80}")
        
        all_token_types = {}
        for result in self.test_results:
            for token_type, count in result['lexical']['token_types'].items():
                all_token_types[token_type] = all_token_types.get(token_type, 0) + count
        
        total_tokens = sum(all_token_types.values())
        print(f"{'Token Type':<20} {'Count':<10} {'Frequency':<10} {'Percentage'}")
        print("-" * 60)
        for token_type in sorted(all_token_types.keys()):
            count = all_token_types[token_type]
            freq = count
            pct = (count / total_tokens) * 100
            print(f"{token_type:<20} {count:<10} {freq:<10} {pct:.1f}%")
        
        print("-" * 60)
        print(f"{'TOTAL':<20} {total_tokens:<10}")
        
        # Acceptance statistics
        print(f"\n{'='*80}")
        print("PARSING RESULTS BY CATEGORY")
        print(f"{'='*80}")
        
        categories = {
            'Taxi & Commuting': ['stmt_001', 'stmt_002', 'stmt_003'],
            'Internet & Electricity': ['stmt_004', 'stmt_005', 'stmt_006'],
            'Market & Business': ['stmt_007', 'stmt_008', 'stmt_009'],
            'Security & Weather': ['stmt_010', 'stmt_011'],
            'Fuel & Transactions': ['stmt_012', 'stmt_013'],
            'University & General': ['stmt_014', 'stmt_015'],
        }
        
        for category, stmt_ids in categories.items():
            accepted = sum(1 for r in self.test_results if r['id'] in stmt_ids and r['syntactic']['accepted'])
            total = len(stmt_ids)
            print(f"{category:<25} {accepted}/{total} accepted ({100*accepted//total}%)")
    
    def generate_report(self, output_file: str = "test_report.txt"):
        """Generate detailed test report"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("AFJEN COMPILER - TEST REPORT\n")
            f.write("CS4110 - Compiler Construction\n")
            f.write("="*80 + "\n\n")
            
            for result in self.test_results:
                f.write(f"Statement {result['id'].upper()}\n")
                f.write(f"Text: {result['statement']}\n")
                f.write(f"Tokens: {result['lexical']['total_tokens']}\n")
                
                f.write("Token Breakdown:\n")
                for token_type, count in sorted(result['lexical']['token_types'].items()):
                    f.write(f"  {token_type}: {count}\n")
                
                status = "ACCEPTED" if result['syntactic']['accepted'] else "REJECTED"
                f.write(f"Parse Result: {status}\n")
                f.write("-" * 80 + "\n\n")
        
        print(f"\nReport saved to {output_file}")


def main():
    """Run all tests"""
    runner = TestRunner()
    runner.run_all_tests()
    runner.generate_report("analysis/test_report.txt")


if __name__ == "__main__":
    main()
