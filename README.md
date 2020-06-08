# Spelling-Error-Correction
Isolated word spelling error corrector based on the noisy channel model.

corpus.txt , spell-errors.txt should be provided on the same folder

program's output name for predictios will be corrects.txt


running command:
python3 proj1.py <test.txt> [noisy]


example without smoothing:
python3 proj1.py test-words-misspelled.txt


example with smoothing:
python3 proj1.py test-words-misspelled.txt noisy
