PYTHON = python3
PYINSTALLER = pyinstaller
EXECUTABLE_GRAMMAIRE = grammaire
EXECUTABLE_GENERER = generer
GRAMMAR_FILES = exemple1.general exemple2.general exemple3.general
DEFAULT_MAX_LENGTH = 5  

all: $(EXECUTABLE_GRAMMAIRE) $(EXECUTABLE_GENERER)

$(EXECUTABLE_GRAMMAIRE): grammaire.py
	$(PYINSTALLER) --onefile grammaire.py

$(EXECUTABLE_GENERER): generer.py
	$(PYINSTALLER) --onefile generer.py

run: $(EXECUTABLE_GRAMMAIRE) $(EXECUTABLE_GENERER)
	@echo "Running examples with grammaire.py..."
	./dist/$(EXECUTABLE_GRAMMAIRE) exemple1.general
	./dist/$(EXECUTABLE_GRAMMAIRE) exemple2.general
	./dist/$(EXECUTABLE_GRAMMAIRE) exemple3.general

	@echo "Generating words with generer.py..."
	@echo "Using MAX_LENGTH=${MAX_LENGTH}"
	./dist/$(EXECUTABLE_GENERER) exemple1.general ${MAX_LENGTH}
	./dist/$(EXECUTABLE_GENERER) exemple2.general ${MAX_LENGTH}
	./dist/$(EXECUTABLE_GENERER) exemple3.general ${MAX_LENGTH}

clean:
	rm -rf __pycache__ dist build *.spec

test: run

.PHONY: all clean run test
