install: pip install -r requirements.txt
lint: flake8 src/ --count --select=E9,F63,F7,F82
run: jupyter notebook