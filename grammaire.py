def eliminate_epsilon(non_terminals, rules):
    """Eliminate ε-productions."""
    nullable = {nt for nt, prods in rules.items() if "ε" in prods}
    
    while True:
        new_nullable = nullable.copy()
        for nt, prods in rules.items():
            if any(all(symbol in nullable for symbol in prod) for prod in prods if prod != "ε"):
                new_nullable.add(nt)
        if new_nullable == nullable:
            break
        nullable = new_nullable

    new_rules = {}
    for nt, prods in rules.items():
        new_prods = []
        for prod in prods:
            if prod == "ε":
                continue
            new_prods += generate_nullable_productions(prod, nullable)
        new_rules[nt] = list(set(new_prods))  # Remove duplicates
    return new_rules

def generate_nullable_productions(production, nullable):
    """Generate all possible productions by removing nullable non-terminals."""
    results = [""]
    for symbol in production:
        if symbol in nullable:
            results = [res + symbol for res in results] + results
        else:
            results = [res + symbol for res in results]
    return list(set(results))

def eliminate_unit_rules(non_terminals, rules):
    """Eliminate unit rules."""
    new_rules = {}
    for nt in non_terminals:
        new_prods = []
        unit_targets = [prod for prod in rules[nt] if prod in non_terminals]
        non_unit_prods = [prod for prod in rules[nt] if prod not in non_terminals]
        while unit_targets:
            target = unit_targets.pop()
            for prod in rules[target]:
                if prod in non_terminals and prod not in unit_targets:
                    unit_targets.append(prod)
                elif prod not in new_prods:
                    new_prods.append(prod)
        new_rules[nt] = non_unit_prods + new_prods
    return new_rules

def convert_to_chomsky(non_terminals, terminals, rules):
    """Convert the grammar to Chomsky Normal Form (CNF)."""
    new_rules = {}
    
    # Step 1: Convert terminals in productions longer than 1 to non-terminals
    term_to_nonterm = {}
    for nt, prods in rules.items():
        new_prods = []
        for prod in prods:
            if len(prod) > 1:
                new_prod = []
                for symbol in prod:
                    if symbol in terminals:
                        if symbol not in term_to_nonterm:
                            new_nt = f"T_{symbol}"
                            term_to_nonterm[symbol] = new_nt
                            new_rules[new_nt] = [symbol]
                        new_prod.append(term_to_nonterm[symbol])
                    else:
                        new_prod.append(symbol)
                new_prods.append("".join(new_prod))
            else:
                new_prods.append(prod)
        new_rules[nt] = new_prods

    # Step 2: Break down productions longer than 2 into binary rules
    final_rules = {}
    counter = 1
    for nt, prods in new_rules.items():
        final_prods = []
        for prod in prods:
            if len(prod) > 2:
                prev_nt = prod[0]
                for i in range(1, len(prod) - 1):
                    new_nt = f"X{counter}"
                    counter += 1
                    final_rules[new_nt] = [prev_nt + prod[i]]
                    prev_nt = new_nt
                final_prods.append(prev_nt + prod[-1])
            else:
                final_prods.append(prod)
        final_rules[nt] = final_prods

    # Merge the new rules
    final_rules.update({nt: prods for nt, prods in new_rules.items() if nt not in final_rules})
    return final_rules

def convert_to_greibach(non_terminals, terminals, rules):
    """Convert the grammar to Greibach Normal Form."""
    def starts_with_terminal(prod):
        return prod[0] in terminals

    new_rules = {}
    for nt in non_terminals:
        new_prods = []
        for prod in rules[nt]:
            if starts_with_terminal(prod):
                new_prods.append(prod)
            else:
                # Replace leading non-terminal with its productions
                replacement_nt = prod[0]
                for replacement_prod in rules[replacement_nt]:
                    new_prods.append(replacement_prod + prod[1:])
        # Ensure no production has non-terminal at the start
        final_prods = []
        for prod in new_prods:
            while not starts_with_terminal(prod):
                replacement_nt = prod[0]
                prod = rules[replacement_nt][0] + prod[1:]
            final_prods.append(prod)
        new_rules[nt] = list(set(final_prods))  # Remove duplicates
    return new_rules

def print_grammar(rules):
    """Print the grammar in a readable format."""
    for nt, prods in rules.items():
        print(f"{nt} -> {' | '.join(prods)}")

# Example usage
non_terminals = {"S", "W", "Y", "X", "A", "Z"}
terminals = {"c", "a", "b"}

rules = {
    "S": ["WY", "XY"],
    "A": ["ZA", "c"],
    "W": ["XA"],
    "X": ["a"],
    "Y": ["b"],
    "Z": ["c"],
}

print("Original Grammar:")
print_grammar(rules)

# Step 1: Eliminate ε-productions
rules = eliminate_epsilon(non_terminals, rules)
print("\nAfter Eliminating ε-productions:")
print_grammar(rules)

# Step 2: Eliminate unit rules
rules = eliminate_unit_rules(non_terminals, rules)
print("\nAfter Eliminating Unit Rules:")
print_grammar(rules)

# Step 3: Convert to CNF
rules = convert_to_chomsky(non_terminals, terminals, rules)
print("\nAfter Converting to CNF:")
print_grammar(rules)

# Step 4: Convert to GNF
rules = convert_to_greibach(non_terminals, terminals, rules)
print("\nAfter Converting to GNF:")
print_grammar(rules)
