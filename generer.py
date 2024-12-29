import sys

EPSILON = "E"

def parse_rules(rules):
    grammar = {}
    start_symbol = None

    for line in rules:
        line = line.strip()
        if not line or ':' not in line:
            continue

        lhs, rhs = map(str.strip, line.split(':', 1))
        rhs_options = [option.strip().split() for option in rhs.split('|')]

        if start_symbol is None:
            start_symbol = lhs

        if lhs not in grammar:
            grammar[lhs] = []

        grammar[lhs].extend(rhs_options)

    return grammar, start_symbol

def generate_words(grammar, start_symbol, max_length):
    results = set()

    def expand(symbols, current_word):
        if len(current_word) > max_length:
            return
        if len(symbols) == 0:
            results.add(current_word)
            return

        first, *rest = symbols

        if first in grammar:  # Non-terminal symbol
            for option in grammar[first]:
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
        with open(grammar_file, "r") as file:
            rules = file.readlines()

        grammar, start_symbol = parse_rules(rules)
        words = generate_words(grammar, start_symbol, max_length)

        for word in words:
            print(word)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
