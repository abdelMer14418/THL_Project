import re
import sys

# Parsing and Loading Functions
def read_grammar(filename):
    """Read grammar from a file and return its components."""
    non_terminals = set()
    terminals = set(chr(i) for i in range(97, 123))  # a-z
    productions = {}
    start_symbol = None

    with open(filename, "r") as file:
        for line in file:
            line = line.strip()
            if not line or ':' not in line:
                continue  # Skip empty or malformed lines

            left, right = map(str.strip, line.split(':', 1))
            right_rules = [rule.strip().replace("E", "ε") for rule in right.split('|')]

            if start_symbol is None:
                start_symbol = left  # The first left-hand side is the start symbol

            non_terminals.add(left)
            productions[left] = [rule.split() for rule in right_rules]

    return non_terminals, terminals, start_symbol, productions

def write_grammar(filename, non_terminals, productions):
    """Write the grammar to a file."""
    with open(filename, "w") as file:
        for var in non_terminals:
            rules = productions.get(var, [])
            rules_str = " | ".join(" ".join(r).replace("ε", "E") for r in rules)
            file.write(f"{var} : {rules_str}\n")

def print_grammar(non_terminals, productions):
    """Print the grammar in a readable line-by-line format."""
    for var in non_terminals:
        rules = productions.get(var, [])
        rules_str = " | ".join(" ".join(r) for r in rules)
        print(f"{var} -> {rules_str}")

# Simplification Functions
def remove_null_productions(non_terminals, terminals, start_symbol, productions):
    """Remove null (epsilon) productions."""
    nullable = {v for v, rules in productions.items() if any(r == ["ε"] for r in rules)}
    new_productions = {v: [] for v in non_terminals}

    while True:
        updated = False
        for v, rules in productions.items():
            for rule in rules:
                if all(sym in nullable for sym in rule):
                    if v not in nullable:
                        nullable.add(v)
                        updated = True
        if not updated:
            break

    for v, rules in productions.items():
        for rule in rules:
            if rule == ["ε"]:
                continue
            combinations = [[]]
            for sym in rule:
                if sym in nullable:
                    combinations = [c + [sym] for c in combinations] + combinations
                else:
                    combinations = [c + [sym] for c in combinations]
            for comb in combinations:
                if comb not in new_productions[v]:
                    new_productions[v].append(comb)
    return non_terminals, terminals, start_symbol, new_productions

def remove_unit_productions(non_terminals, productions):
    """Remove unit productions."""
    new_productions = {v: [] for v in non_terminals}
    for v in non_terminals:
        reachable = {v}
        stack = [v]
        while stack:
            current = stack.pop()
            for rule in productions[current]:
                if len(rule) == 1 and rule[0] in non_terminals and rule[0] not in reachable:
                    reachable.add(rule[0])
                    stack.append(rule[0])
                elif rule not in new_productions[v]:
                    new_productions[v].append(rule)
    return non_terminals, new_productions

def convert_to_chomsky_nf(non_terminals, terminals, start_symbol, productions):
    """Convert grammar to Chomsky Normal Form."""
    new_productions = {v: [] for v in non_terminals}
    term_map = {}
    counter = 0

    for v, rules in productions.items():
        for rule in rules:
            if len(rule) == 1:
                new_productions[v].append(rule)
            else:
                updated_rule = []
                for sym in rule:
                    if sym in terminals and sym != "ε":
                        if sym not in term_map:
                            new_var = f"T_{counter}"
                            term_map[sym] = new_var
                            non_terminals.add(new_var)
                            new_productions[new_var] = [[sym]]
                            counter += 1
                        updated_rule.append(term_map[sym])
                    else:
                        updated_rule.append(sym)
                while len(updated_rule) > 2:
                    new_var = f"X_{counter}"
                    counter += 1
                    non_terminals.add(new_var)
                    new_productions[new_var] = [[updated_rule.pop(0), updated_rule[0]]]
                    updated_rule[0] = new_var
                new_productions[v].append(updated_rule)
    return non_terminals, terminals, start_symbol, new_productions

def convert_to_greibach_nf(non_terminals, terminals, start_symbol, productions):
    """Convert grammar to Greibach Normal Form."""
    def starts_with_terminal(rule):
        return len(rule) > 0 and rule[0] in terminals

    terminal_replacements = {v: rules[0][0] for v, rules in productions.items() if v.startswith("T_")}
    updated_productions = {}
    for v, rules in productions.items():
        updated_productions[v] = []
        for rule in rules:
            updated_rule = [terminal_replacements.get(sym, sym) for sym in rule]
            updated_productions[v].append(updated_rule)

    final_productions = {v: [] for v in non_terminals if not v.startswith("T_")}

    def substitute_non_terminal(rule):
        first_sym = rule[0]
        if first_sym in non_terminals:
            substituted_rules = []
            for replacement in updated_productions[first_sym]:
                substituted_rules.append(replacement + rule[1:])
            return substituted_rules
        return [rule]

    for v in final_productions:
        worklist = updated_productions[v][:]
        while worklist:
            rule = worklist.pop(0)
            if starts_with_terminal(rule):
                final_productions[v].append(rule)
            elif len(rule) > 0 and rule[0] in non_terminals:
                substituted_rules = substitute_non_terminal(rule)
                worklist.extend(substituted_rules)
            else:
                final_productions[v].append(rule)

    return list(final_productions.keys()), terminals, start_symbol, final_productions

# Main Execution
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: grammaire <input_file.general>")
        sys.exit(1)

    input_file = sys.argv[1]
    if not input_file.endswith(".general"):
        print("Error: Input file must have the extension .general")
        sys.exit(1)

    try:
        # Read Grammar
        non_terminals, terminals, start_symbol, productions = read_grammar(input_file)

        print("Original Grammar:")
        print_grammar(non_terminals, productions)

        # Remove Null Productions
        non_terminals, terminals, start_symbol, productions = remove_null_productions(non_terminals, terminals, start_symbol, productions)
        print("\nAfter Removing Null Productions:")
        print_grammar(non_terminals, productions)

        # Remove Unit Productions
        non_terminals, productions = remove_unit_productions(non_terminals, productions)
        print("\nAfter Removing Unit Productions:")
        print_grammar(non_terminals, productions)

        # Chomsky Normal Form
        chomsky_file = input_file.replace(".general", ".chomsky")
        cnf_non_terminals, terminals, start_symbol, cnf_productions = convert_to_chomsky_nf(non_terminals, terminals, start_symbol, productions)
        print("\nAfter Converting to Chomsky Normal Form:")
        print_grammar(cnf_non_terminals, cnf_productions)
        write_grammar(chomsky_file, cnf_non_terminals, cnf_productions)

        # Greibach Normal Form
        greibach_file = input_file.replace(".general", ".greibach")
        gnf_non_terminals, terminals, start_symbol, gnf_productions = convert_to_greibach_nf(non_terminals, terminals, start_symbol, productions)
        print("\nAfter Converting to Greibach Normal Form:")
        print_grammar(gnf_non_terminals, gnf_productions)
        write_grammar(greibach_file, gnf_non_terminals, gnf_productions)

        print(f"\nGrammars written to {chomsky_file} and {greibach_file}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
