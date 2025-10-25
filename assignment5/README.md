# assignment5

## TODO List

<!-- markdownlint-disable-next-line -->

- backtester/\__init_.py
- backtester/price_loader.py
- backtester/strategy.py
- backtester/broker.py
- backtester/engine.py
- tests/test_strategy.py
- tests/test_broker.py
- tests/test_engine.py
- tests/conftest.py
- requirements.txt
- pyproject.toml
- .github/workflows/ci.yml
- README.md

## Setup Instructions

1. Clone the repository to your local machine.

```bash
git clone <repository_url>
cd assignment5
```

2. Create a virtual environment (optional but recommended).

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

3. Install the required dependencies.

```bash
pip install -r requirements.txt
```

3. Run the tests

```bash
coverage run -m pytest -q
coverage report -m
coverage html
```

or

```bash
coverage run -m pytest -q && coverage report -m && coverage html
```

4. Get code coverage report

```bash
coverage report --fail-under=90
```
