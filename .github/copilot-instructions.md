# Copilot Instructions

## Package & environment management

- **Always use [uv](https://docs.astral.sh/uv/)** for all Python-related tasks:
  - `uv add <package>` to add dependencies (never `pip install` or edit `requirements.txt`).
  - `uv remove <package>` to remove dependencies.
  - `uv run <command>` to run scripts/tools inside the project environment (e.g. `uv run streamlit run app.py`).
  - `uv sync` to sync the virtual environment from the lockfile.
  - `uv lock` to regenerate the lockfile after manual `pyproject.toml` edits.
- **Do not** use `pip`, `pip-tools`, `pipenv`, `poetry`, `conda`, or `requirements.txt`.
- Dependencies are declared in `pyproject.toml` and locked in `uv.lock`.

## Running the app

```sh
uv run streamlit run app.py
```
