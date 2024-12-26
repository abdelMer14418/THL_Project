import re
from itertools import product

# Parsing and Loading Functions
def load_grammar(non_terminals, terminals, start_symbol, rules):
    """Load grammar from predefined dictionaries."""
    variables = list(non_terminals)
    terminals = list(terminals) + ["ε"]  # Include epsilon as a valid terminal symbol
    productions = parse_productions(rules, variables, terminals)
    return variables, terminals, start_symbol, productions

def parse_productions(rules, variables, terminals):
    """Parse grammar productions."""
    productions = {}
    for left, rights in rules.items():
        productions[left] = [parse_rule(right, variables + terminals) for right in rights]
    return productions

def parse_rule(rule, symbols):
    """Parse a single rule."""
    if not rule:
        return []

    parsed_rule = []
    while rule:
        match = re.match('|'.join(symbols), rule)
        if not match:
            raise ValueError(f'Error: Undefined symbol in production: {rule}')
        parsed_rule.append(match.group())
        rule = rule[match.end():]
    return parsed_rule

# Simplification Functions
def remove_null_productions(variables, terminals, start_symbol, productions):
    """Remove null (epsilon) productions."""
    nullable = {v for v, rules in productions.items() if any(r == ["ε"] for r in rules)}
    new_productions = {v: [] for v in variables}
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
    return variables, terminals, start_symbol, new_productions

def remove_unit_productions(variables, productions):
    """Remove unit productions."""
    new_productions = {v: [] for v in variables}
    for v in variables:
        reachable = {v}
        stack = [v]
        while stack:
            current = stack.pop()
            for rule in productions[current]:
                if len(rule) == 1 and rule[0] in variables and rule[0] not in reachable:
                    reachable.add(rule[0])
                    stack.append(rule[0])
                elif rule not in new_productions[v]:
                    new_productions[v].append(rule)
    return variables, new_productions

def convert_to_chomsky_nf(variables, terminals, start_symbol, productions):
    """Convert grammar to Chomsky Normal Form."""
    new_productions = {v: [] for v in variables}
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
                            new_var = f'T_{counter}'
                            term_map[sym] = new_var
                            variables.append(new_var)
                            new_productions[new_var] = [[sym]]
                            counter += 1
                        updated_rule.append(term_map[sym])
                    else:
                        updated_rule.append(sym)
                while len(updated_rule) > 2:
                    new_var = f'X_{counter}'
                    counter += 1
                    variables.append(new_var)
                    new_productions[new_var] = [[updated_rule.pop(0), updated_rule[0]]]
                    updated_rule[0] = new_var
                new_productions[v].append(updated_rule)
    return variables, terminals, start_symbol, new_productions

def convert_to_greibach_nf(variables, terminals, start_symbol, productions):
    """Convert grammar to Greibach Normal Form with terminal replacements."""
    def starts_with_terminal(rule):
        """Check if a rule starts with a terminal."""
        return len(rule) > 0 and rule[0] in terminals

    # Replace auxiliary variables (like T_0, T_1) with their corresponding terminals
    terminal_replacements = {v: rules[0][0] for v, rules in productions.items() if v.startswith("T_")}
    
    # Update productions to replace auxiliary variables with their terminals
    updated_productions = {}
    for v, rules in productions.items():
        updated_productions[v] = []
        for rule in rules:
            updated_rule = [terminal_replacements.get(sym, sym) for sym in rule]
            updated_productions[v].append(updated_rule)

    # New productions dictionary
    final_productions = {v: [] for v in variables if not v.startswith("T_")}

    def substitute_non_terminal(rule):
        """Substitute non-terminal at the start of a rule."""
        first_sym = rule[0]
        if first_sym in variables:
            # Replace the first non-terminal with its productions
            substituted_rules = []
            for replacement in updated_productions[first_sym]:
                substituted_rules.append(replacement + rule[1:])
            return substituted_rules
        return [rule]  # No substitution needed

    for v in final_productions:
        worklist = updated_productions[v][:]
        while worklist:
            rule = worklist.pop(0)

            if starts_with_terminal(rule):
                # Rule starts with a terminal, add it directly
                final_productions[v].append(rule)
            elif len(rule) > 0 and rule[0] in variables:
                # Rule starts with a non-terminal, substitute it
                substituted_rules = substitute_non_terminal(rule)
                worklist.extend(substituted_rules)
            else:
                # Preserve malformed or empty rules
                final_productions[v].append(rule)

    return list(final_productions.keys()), terminals, start_symbol, final_productions








def print_grammar(variables, productions):
    """Print the grammar in a readable line-by-line format."""
    for var in variables:
        rules = productions.get(var, [])
        rules_str = " | ".join(" ".join(r) for r in rules)
        print(f"{var} -> {rules_str}")

# Main Execution
if __name__ == "__main__":
    print("Context Free Grammar Transformation")

    # Define Grammar
    non_terminals = {"S", "A", "B", "C", "D"}
    terminals = {"x", "y", "z"}
    rules = {
        "S": ["AB", "C", "ε"],  # ε
        "A": ["xA", "ε"],       # ε
        "B": ["yB", "y"],
        "C": ["zC", "ε"],       # ε
        "D": ["x", "y"]
    }








    start_symbol = "S"

    # Load Grammar
    variables, terminals, start_symbol, productions = load_grammar(non_terminals, terminals, start_symbol, rules)

    print("Original Grammar:")
    print_grammar(variables, productions)

    # Remove Null Productions
    variables, terminals, start_symbol, productions = remove_null_productions(variables, terminals, start_symbol, productions)
    print("\nAfter Removing Null Productions:")
    print_grammar(variables, productions)

    # Remove Unit Productions
    variables, productions = remove_unit_productions(variables, productions)
    print("\nAfter Removing Unit Productions:")
    print_grammar(variables, productions)

    # Convert to Chomsky Normal Form
    variables, terminals, start_symbol, productions = convert_to_chomsky_nf(variables, terminals, start_symbol, productions)
    print("\nAfter Converting to Chomsky Normal Form:")
    print_grammar(variables, productions)

    # Convert to Greibach Normal Form
    variables, terminals, start_symbol, productions = convert_to_greibach_nf(variables, terminals, start_symbol, productions)
    print("\nAfter Converting to Greibach Normal Form:")
    print_grammar(variables, productions)
