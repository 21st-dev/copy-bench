"""docs/results.png: one-shot vs self-verified score per model (published Copy Bench v1 aggregates, all 50 tasks)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROWS = [('GPT-6.2 Astra', 89.1, 92.4), ('GPT-6.2 Sol', 84.1, 88.4), ('GPT-6 Astra', 76.9, 86.7), ('GPT-6.1 Sol', 75.6, 82.2), ('Claude Fable 5.2', 62.4, 69.0), ('Gemini 4 Carbon', 57.0, 67.2), ('GPT-6 Sol', 57.3, 64.5), ('Claude Opus 5.5', 50.1, 59.1), ('Qwen 4 Max', 45.4, 54.4), ('Muse Wonder 1.0', 41.3, 51.9), ('Qwen 3.8 Max Prime', 41.2, 50.1), ('Kimi K3.1 Pro', 34.6, 46.6), ('MiniMax M3', 33.3, 41.9), ('Grok 4.7', 30.3, 39.2), ('Claude Sonnet 5.5', 28.1, 35.8), ('MiMo V2.6 Pro', 16.4, 18.9)]
ROWS = ROWS[::-1]
fig, ax = plt.subplots(figsize=(8, 7.4), dpi=150)
y = range(len(ROWS))
h = 0.38
ax.barh([i + h / 2 for i in y], [r[2] for r in ROWS], h, color="#0033ff", label="Self-verified (step 2, browser)")
ax.barh([i - h / 2 for i in y], [r[1] for r in ROWS], h, color="#9db0ff", label="One-shot (step 1, no browser)")
for i, r in enumerate(ROWS):
    ax.text(r[2] + 0.8, i + h / 2, f"{r[2]:.1f}", va="center", fontsize=8, color="#222")
    ax.text(r[1] + 0.8, i - h / 2, f"{r[1]:.1f}", va="center", fontsize=8, color="#666")
ax.set_yticks(list(y), [r[0] for r in ROWS], fontsize=9)
ax.set_xlim(0, 100)
ax.set_xlabel("Copy Bench score (0-100), 50 tasks")
ax.set_title("Copy Bench v1: how close each model's copy gets", loc="left", fontsize=11)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(loc="lower right", frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig("docs/results.png")
