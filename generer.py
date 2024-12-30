import sys

EPSILON = "ε"

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
            right_rules = [rule.strip().replace("E", EPSILON) for rule in right.split('|')]

            if start_symbol is None:
                start_symbol = left  # The first non-terminal is the start symbol

            non_terminals.add(left)
            # Split each rule into individual symbols
            productions[left] = [list(rule) for rule in right_rules]

        #print(productions)

    return non_terminals, terminals, start_symbol, productions

def generate_words(non_terminals, terminals, start_symbol, productions, max_length):
    results = set()

    def expand(symbols, current_word):
        if len(current_word) > max_length:
            return
        if len(symbols) == 0:
            results.add(current_word)
            return

        first, *rest = symbols

        if first in productions:  # Non-terminal symbol
            for option in productions[first]:
                expand(option + rest, current_word)
        elif first == EPSILON:  # Handle epsilon
            expand(rest, current_word)
        else:  # Terminal symbol
            expand(rest, current_word + first)

    expand([start_symbol], "")
    return sorted(results)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generer.py <grammar_file> <max_length>")
        sys.exit(1)

    grammar_file = sys.argv[1]
    max_length = int(sys.argv[2])

    try:
        # Read the grammar
        non_terminals, terminals, start_symbol, productions = read_grammar(grammar_file)

        # Generate words
        words = generate_words(non_terminals, terminals, start_symbol, productions, max_length)

        for word in words:
            print(word)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
