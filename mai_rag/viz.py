"""
mai_rag.viz — purpose-built, editorial-styled charts so notebooks stay thin.

Palette matches the in-app editorial lessons (cream paper, burgundy accent) so
notebook output and the course read as one thing. The single most-reused chart
is `compare()` / `compare_runs()` — the before/after delta scorecard that is the
spine of Modules 2–5: every technique is judged by whether it moves it.
"""
from __future__ import annotations

import numpy as np

# Editorial palette
PAPER = "#F4F2EC"
INK = "#1C1C1E"
MUTED = "#6B6B6B"
LINE = "#D8D6D0"
ACCENT = "#8B2E1F"        # burgundy
ACCENT_SOFT = "#B8674F"
GOOD = "#5E6B3B"          # sepia-green


def _ax(figsize=(8, 4.5)):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(LINE)
    ax.tick_params(colors=INK, labelsize=9)
    ax.title.set_color(INK)
    return fig, ax


def scorecard(summary: dict[str, float], title: str = "Scorecard"):
    """Horizontal bars, one per evaluator, on a 0–1 scale."""
    import matplotlib.pyplot as plt

    names = list(summary.keys())
    vals = [summary[n] for n in names]
    fig, ax = _ax(figsize=(8, 0.5 * len(names) + 1.5))
    y = np.arange(len(names))
    ax.barh(y, vals, color=ACCENT, height=0.6)
    ax.set_yticks(y, names)
    ax.set_xlim(0, 1)
    ax.invert_yaxis()
    ax.set_title(title, fontsize=13, loc="left", style="italic")
    for i, v in enumerate(vals):
        ax.text(min(v + 0.02, 0.97), i, f"{v:.2f}", va="center", color=INK, fontsize=9)
    ax.axvline(0.7, color=ACCENT_SOFT, ls="--", lw=1, alpha=0.6)
    plt.tight_layout()
    return ax


def compare(before: dict[str, float], after: dict[str, float],
            labels=("baseline", "candidate"), title: str = "Did we beat the baseline?"):
    """Grouped before/after bars per evaluator, with the delta annotated. The
    recurring visual of the pillar."""
    import matplotlib.pyplot as plt

    names = [n for n in before if n in after] or list(after.keys())
    b = [before.get(n, 0.0) for n in names]
    a = [after.get(n, 0.0) for n in names]
    x = np.arange(len(names))
    w = 0.38
    fig, ax = _ax(figsize=(max(7, 1.3 * len(names)), 4.8))
    ax.bar(x - w / 2, b, w, label=labels[0], color=ACCENT_SOFT)
    ax.bar(x + w / 2, a, w, label=labels[1], color=ACCENT)
    ax.set_xticks(x, names, rotation=25, ha="right")
    ax.set_ylim(0, 1)
    ax.axhline(0.7, color=MUTED, ls="--", lw=1, alpha=0.5)
    ax.set_title(title, fontsize=13, loc="left", style="italic")
    for i, n in enumerate(names):
        d = after.get(n, 0) - before.get(n, 0)
        ax.text(x[i], max(a[i], b[i]) + 0.02, f"{d:+.2f}",
                ha="center", color=(GOOD if d >= 0 else ACCENT), fontsize=8, fontweight="bold")
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    plt.tight_layout()
    return ax


def per_case_heatmap(results: list[dict], title: str = "Read the distribution, not the mean"):
    """Cases × evaluators heatmap — surfaces the catastrophic 0.2 hiding under a
    0.9 average."""
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap

    evaluators = sorted({r["evaluator"] for r in results})
    cases = sorted({r["case_id"] for r in results})
    M = np.full((len(cases), len(evaluators)), np.nan)
    ci = {c: i for i, c in enumerate(cases)}
    ei = {e: i for i, e in enumerate(evaluators)}
    for r in results:
        M[ci[r["case_id"]], ei[r["evaluator"]]] = r["score"]

    cmap = LinearSegmentedColormap.from_list("ed", ["#9B2D1F", "#E8E2D0", GOOD])
    fig, ax = _ax(figsize=(1.1 * len(evaluators) + 2, 0.45 * len(cases) + 2))
    im = ax.imshow(M, cmap=cmap, vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(evaluators)), evaluators, rotation=30, ha="right")
    ax.set_yticks(range(len(cases)), [f"case {c}" for c in cases])
    ax.set_title(title, fontsize=12, loc="left", style="italic")
    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    plt.tight_layout()
    return ax


def confusion_matrix(decisions, labels=None,
                     title: str = "The gate: did it pause exactly the unsafe ones?"):
    """Render a confusion matrix for a binary/multi-class gate (Lab 7 Move 7).

    `decisions` is a list of `(true_label, predicted_label)` pairs — e.g. the
    turn's ground-truth tag vs the gate's held/proceeded decision. `labels` fixes
    the row/column order; if None it's inferred (sorted union of both axes). The
    diagonal is correct calls; off-diagonal cells are where the gate over-blocked
    (false positive → alert fatigue) or leaked an unsafe turn (false negative →
    the action that shipped). Editorial palette, same as the rest of viz.

    NEW helper, ships with Lab 7. If it ever slips, Move 7 falls back to
    per_case_heatmap with tag rows."""
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap

    pairs = [(str(t), str(p)) for t, p in decisions]
    if labels is None:
        labels = sorted({t for t, _ in pairs} | {p for _, p in pairs})
    labels = [str(x) for x in labels]
    idx = {l: i for i, l in enumerate(labels)}

    M = np.zeros((len(labels), len(labels)), dtype=int)
    for t, p in pairs:
        if t in idx and p in idx:
            M[idx[t], idx[p]] += 1

    cmap = LinearSegmentedColormap.from_list("ed", ["#F4F2EC", ACCENT_SOFT, ACCENT])
    fig, ax = _ax(figsize=(1.0 * len(labels) + 2.5, 0.9 * len(labels) + 2))
    im = ax.imshow(M, cmap=cmap, aspect="auto")
    ax.set_xticks(range(len(labels)), labels, rotation=30, ha="right")
    ax.set_yticks(range(len(labels)), labels)
    ax.set_xlabel("gate decision (predicted)", color=INK, fontsize=9)
    ax.set_ylabel("ground-truth tag", color=INK, fontsize=9)
    ax.set_title(title, fontsize=12, loc="left", style="italic")
    thresh = M.max() / 2 if M.max() else 0.5
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, str(M[i, j]), ha="center", va="center",
                    color=(PAPER if M[i, j] > thresh else INK), fontsize=9)
    plt.tight_layout()
    return ax


def compare_runs(store, label_a: str, label_b: str, **kw):
    """Read two persisted runs from the data layer (by label) and `compare()`
    them. This is why runs persist — Module 2's run is already in the DB."""
    def means(label):
        rows = store.conn.execute(
            "SELECT r.evaluator, AVG(r.score) AS m FROM eval_results r "
            "JOIN eval_runs e ON e.id = r.run_id "
            "WHERE e.id = (SELECT MAX(id) FROM eval_runs WHERE label = ?) "
            "GROUP BY r.evaluator", (label,),
        ).fetchall()
        return {row["evaluator"]: float(row["m"]) for row in rows}

    return compare(means(label_a), means(label_b), labels=(label_a, label_b), **kw)


def query_umap(store, queries: list[str] | None = None, title: str = "Seeing retrieval"):
    """Project all chunk embeddings + optional queries into 2D. Needs the viz
    extra:  pip install "mai_rag[viz]"."""
    try:
        import umap  # noqa
    except ImportError as exc:
        raise ImportError('UMAP not installed. Run:  pip install "mai_rag[viz]"') from exc
    import matplotlib.pyplot as plt
    from .store import embed

    rows = store.conn.execute("SELECT content FROM chunks").fetchall()
    texts = [r["content"] for r in rows]
    vecs = embed(texts)
    reducer = umap.UMAP(random_state=0)
    pts = reducer.fit_transform(vecs)
    fig, ax = _ax(figsize=(7, 6))
    ax.scatter(pts[:, 0], pts[:, 1], s=12, color=MUTED, alpha=0.5, label="chunks")
    if queries:
        qpts = reducer.transform(embed(queries))
        ax.scatter(qpts[:, 0], qpts[:, 1], s=160, marker="X", color=ACCENT, label="query")
    ax.set_title(title, fontsize=12, loc="left", style="italic")
    ax.legend(frameon=False, fontsize=9)
    ax.axis("off")
    return ax
