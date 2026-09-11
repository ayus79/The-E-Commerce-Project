# uv Command Cheat Sheet (with pip equivalents & optimizations)

## Installation

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # Linux/macOS
pip install uv                                     # via pip
brew install uv                                    # macOS Homebrew
pipx install uv                                    # via pipx
```

Upgrade / check version:

```bash
uv self update
uv --version
```

---

## 1. `uv pip` — drop-in pip replacement

Use these when you just want pip, but faster. No project files needed.


| Task                                  | pip                               | uv                                                   |
| ------------------------------------- | --------------------------------- | ---------------------------------------------------- |
| Install package                       | `pip install requests`            | `uv pip install requests`                            |
| Install from file                     | `pip install -r requirements.txt` | `uv pip install -r requirements.txt`                 |
| Install editable                      | `pip install -e .`                | `uv pip install -e .`                                |
| Uninstall                             | `pip uninstall requests`          | `uv pip uninstall requests`                          |
| Freeze                                | `pip freeze`                      | `uv pip freeze`                                      |
| List packages                         | `pip list`                        | `uv pip list`                                        |
| Show package info                     | `pip show requests`               | `uv pip show requests`                               |
| Check for conflicts                   | `pip check`                       | `uv pip check`                                       |
| Compile lockfile from requirements.in | `pip-compile requirements.in`     | `uv pip compile requirements.in -o requirements.txt` |
| Sync env to exact requirements        | (no native equivalent)            | `uv pip sync requirements.txt`                       |
| Create venv                           | `python -m venv .venv`            | `uv venv`                                            |
| Create venv w/ specific Python        | `python3.12 -m venv .venv`        | `uv venv --python 3.12`                              |


`uv pip sync` is worth calling out — it makes the environment **exactly** match the given requirements file (installs missing, removes extras). Plain pip has no equivalent; this is closer to what lockfile-based tools do.

---



## 2. `uv` project workflow (replaces Poetry/pipenv-style usage)

```bash
uv init myproject              # new project, creates pyproject.toml + .venv
uv init --lib mypackage        # library layout (src/ structure)
uv init --app                  # application layout
uv init --no-package           # no defualt package (flat setup)

uv add requests                # add dependency, updates pyproject.toml + uv.lock
uv add "requests>=2.31"        # with version constraint
uv add --dev pytest ruff       # dev-only dependency group
uv add --optional extra-name pandas   # optional dependency group
uv remove requests             # remove dependency

uv sync                        # install exactly what's in uv.lock
uv sync --frozen               # install without re-resolving/updating lock
uv sync --no-dev               # skip dev dependencies
uv sync --all-extras           # include all optional extras

uv lock                        # (re)generate uv.lock without installing
uv lock --upgrade              # upgrade all deps to latest allowed versions
uv lock --upgrade-package requests   # upgrade just one package

uv run python script.py        # run inside project venv, no activation needed
uv run pytest
uv run --some-cli-tool --flag

uv tree                        # show dependency tree
uv export --format requirements-txt > requirements.txt   # export lock to requirements.txt
uv export --no-dev --format requirements-txt > requirements.txt
```

---



## 3. Python version management (replaces pyenv for many use cases)

```bash
uv python list                 # list available/installed Python versions
uv python install 3.12         # install a specific Python version
uv python install 3.11 3.12 3.13   # install multiple
uv python pin 3.12             # pin project to a version (.python-version file)
uv python find 3.12            # find path to an installed interpreter
uv python uninstall 3.11
```

---



## 4. Virtual environments

```bash
uv venv                        # create .venv in current dir
uv venv --python 3.12          # specify Python version
uv venv myenv                  # custom venv name/path
uv venv --seed                 # include pip/setuptools/wheel in venv (off by default)
```

Activate as usual afterward (`source .venv/bin/activate`), or skip activation entirely and just use `uv run`.

---



## 5. Tools (replaces pipx)

```bash
uv tool install ruff            # install a CLI tool globally, isolated
uv tool run ruff check .        # run without installing (like pipx run)
uvx ruff check .                # shorthand alias for `uv tool run`
uv tool list
uv tool uninstall ruff
uv tool upgrade ruff
```

`uvx` is the one you'll use constantly — it's uv's answer to `pipx run`, e.g. `uvx black .`, `uvx cowsay hi`.

---



## 6. Scripts with inline dependencies (PEP 723)

Run a standalone script that declares its own deps at the top — no project setup needed:

```python
# script.py
# /// script
# dependencies = ["requests", "rich"]
# ///
import requests
```

```bash
uv run script.py               # auto-installs deps in an ephemeral env
uv add --script script.py requests   # add a dep to the inline metadata
```

Great for one-off scripts you want reproducible without a whole project.

---



## 7. Production / CI usage

```bash
uv sync --frozen --no-dev              # exact, reproducible, prod-only deps
uv pip install -r requirements.txt     # if still requirements.txt-based
uv export --no-dev --format requirements-txt > requirements.txt   # for pip-only prod images
```

Dockerfile pattern:

```dockerfile
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev
COPY . .
CMD ["uv", "run", "python", "app.py"]
```

---



## 8. Optimization / speed tips

- **Cache mounts in CI/Docker**: `RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen` — persists downloaded wheels across builds, makes rebuilds near-instant.
- `--frozen` **always in CI/prod** — prevents silent re-resolution and version drift on deploy.
- **Multi-stage Docker builds** — build in one stage, `COPY --from=builder /app/.venv /app/.venv` into a slim runtime stage to cut image size.
- **Pin the uv binary version** in Dockerfiles (`uv:0.5.x` not `uv:latest`) so upstream uv changes don't silently alter resolution.
- **Global cache is shared across projects** by default (`~/.cache/uv`) — no need for per-project cache config; this is a big part of why repeated installs are fast.
- `UV_LINK_MODE=copy` env var if you hit hardlink issues across filesystems (e.g. Docker volumes) — otherwise uv uses hardlinks/reflinks to avoid copying files at all.
- `--no-cache` flag to disable caching for one-off reproducibility tests.
- `uv pip compile` with `--generate-hashes` for supply-chain-verified requirements.txt output.
- **Parallel installs are automatic** — uv resolves and installs in parallel by default; nothing to configure.
- **Use** `uv.lock` **(not requirements.txt) for internal projects** — cross-platform lockfile, resolves for multiple platforms/Python versions at once, so the same lock works in dev (macOS) and prod (Linux) without drift.

---



## 9. Useful flags cheat sheet


| Flag                 | Meaning                                                   |
| -------------------- | --------------------------------------------------------- |
| `--frozen`           | Don't update the lockfile, install exactly as locked      |
| `--locked`           | Fail if lockfile would need updating (good for CI checks) |
| `--no-dev`           | Skip dev dependency group                                 |
| `--all-extras`       | Include all optional extras                               |
| `--extra <name>`     | Include a specific optional extra                         |
| `--upgrade`          | Allow upgrading packages during resolution                |
| `--python <version>` | Target a specific Python version                          |
| `--no-cache`         | Disable cache for this command                            |
| `--offline`          | Don't hit the network, use cache only                     |


---
