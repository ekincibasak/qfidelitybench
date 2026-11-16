# Reproducibility

## Verified environment

The compact portfolio was installed and tested in a **new isolated virtual environment**, without system site packages, on macOS14.6 arm64 / Python3.9.6. Installation downloaded dependencies independently of the research environment. `pip check`, `demo.py` and all three minimal tests passed. The runtime requirements include the transitive tzdata dependency discovered during resolution. Version pins are not cryptographic wheel hashes.

The historical research tests also passed (102 tests) in the preserved research environment; those broader tests and the full production archive are deliberately not included here. The research environment was not upgraded.

## Install and run

Use Python3.9.6 to match the tested interpreter, from the repository root:

```sh
python3.9 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
.venv/bin/python demo.py
.venv/bin/python -m unittest discover -s tests -v
```

Python3.9 is deprecated by the pinned Qiskit version. Newer Python, Windows and Linux portability have not been verified; do not infer support from a successful macOS replay. No network connection or account credentials are needed at replay time after dependencies are installed. Run normally, without Python's `-O` option, since scientific assertions are part of the checks. No unsafe OpenMP environment override is used or required by this replay.

The expected final replay lines include `PASS: archived counts, equal budgets, verified functions and noiseless reference.` and the warning that one repetition cannot establish improvement. The three tests cover archived reconstruction, copied artifact hashes and the frozen dataset-level null result. A successful test of the saved result is a consistency check, not independent regeneration of every production output.

## Scope of reproduction

Included: two index-selected archived cases, necessary verified source copies, aggregate result tables/JSON and unchanged figures. The demonstration recomputes exact probabilities but samples no new shots. Paired uses512+512 shots; other arms use1024. Five count streams correspond to forward, reverse, paired-forward, paired-reverse and random measurements.

Not included: production runners, full38,828-file result directory, original1000-repeat measurement arrays, historical Git objects, hardware credentials or local virtual environments. Thus the full production experiment cannot be rerun from this compact portfolio alone. Parent hashes support provenance checks when the complete research archive is separately available; they are not a replacement for that archive.

`MANIFEST.sha256` lists every intended public file except itself. It can be checked on macOS using `shasum -a 256 -c MANIFEST.sha256`. A private inventory including that manifest is maintained separately for release bookkeeping; no internal audit document is included in the public repository.
