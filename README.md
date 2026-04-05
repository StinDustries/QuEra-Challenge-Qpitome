# Qpitome — QuEra Challenge @ YQuantum 2026

Team **Qpitome**'s submission for the [QuEra Challenge](https://github.com/YQuantum-2026/QuEra-Challenge) at YQuantum 2026.

---

## 🧩 The Challenge

This project explores a deceptively counterintuitive claim from the world of quantum computing:

> **A 1-qubit gate can be harder to implement than a 2-qubit gate.**

Through a technical write-up, code, and visualizations, we walk through why this is true by examining gate synthesis, quantum error correction, and architecture constraints on QuEra's neutral-atom hardware — using QuEra's [Bloqade](https://bloqade.quera.com/latest/digital/) SDK.

---

## 📁 Repository Structure

```
.
├── STAR1/          # Gate synthesis explorations (part 1)
├── STAR2/          # Gate synthesis explorations (part 2)
├── STAR3/          # Gate synthesis explorations (part 3)
├── STAR4/          # Gate synthesis explorations (part 4)
├── SYNTH1/         # Synthesis methods and comparisons (part 1)
├── SYNTH2/         # Synthesis methods and comparisons (part 2)
├── SYNTH3/         # Synthesis methods and comparisons (part 3)
├── SYNTH4/         # Synthesis methods and comparisons (part 4)
├── assets/         # Images and supporting files
├── bloqade_tutorial.ipynb   # Workshop tutorial notebook
├── challenge.md    # Formal challenge statement and guidelines
├── pyproject.toml  # Project dependencies (managed with uv)
├── uv.lock         # Locked dependency versions
├── writeup.pdf     # Project write-up
└── yquantum.pdf   # Final presentation
```

---

## ⚙️ Setup

This project uses Python 3.12 and [`uv`](https://github.com/astral-sh/uv) for dependency management.

### 1. Install `uv`

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

Verify:
```bash
uv --version
```

### 2. Install dependencies and activate the environment

```bash
# Create and sync the virtual environment
uv sync

# Activate it (macOS/Linux)
source .venv/bin/activate

# Activate it (Windows PowerShell)
.venv\Scripts\activate
```

### 3. Explore!

---

## 📦 Dependencies

| Package | Version |
|---|---|
| Python | 3.12.x |
| `bloqade` | ≥ 0.32.0 |
| `bloqade-circuit[tsim]` | ≥ 0.11.2 |
| `jupyterlab` | ≥ 4.5.3 |

All dependencies are pinned in `uv.lock` and declared in `pyproject.toml`.

---

## 📝 Deliverables

This submission includes:

1. **Technical write-up** — A narrative with code, plots, and visualizations arguing why 1-qubit gates can be unexpectedly costly, with source code organized across the `STAR` and `SYNTH` folders.
2. **Supporting code and figures** — All notebooks and scripts used to build and support our argument.
3. **Presentation** (`yquantum.pptx`) — Slides summarizing our findings and their significance for the future of quantum computing.
