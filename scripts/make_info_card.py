"""Hand-authored neofetch-style info card. STATIC=1 emits a frozen frame."""
import os
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

WIDTH, PAD, LINE_H = 628, 22, 21
KEY_W = 104
FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
SWATCHES = ["#ff5f56", "#ffbd2e", "#27c93f", "#58a6ff", "#bc8cff", "#39d353", "#c9d1d9", "#7d8590"]

# (key, value); key None = continuation line, ("", "") = blank spacer
LINES = [
    ("Now", "AI Engineer Intern @ Pindrop Security"),
    (None, "Founder & Engineer @ PreSage.ai"),
    ("Prev", "Software Engineering Intern @ Zyprova"),
    ("School", "B.S. Computer Science @ UC Irvine, '28"),
    ("", ""),
    ("Focus", "agent observability, LLM & agent evaluation,"),
    (None, "harness optimization"),
    ("Stack", "Python, TypeScript, C++, SQL"),
    (None, "LangGraph, FastAPI, React, Kafka, Redis"),
    (None, "GCP, AWS, PostgreSQL, Docker"),
    ("", ""),
    ("Highlights", "cut model spend 81% with LLM observability + eval"),
    (None, "multi-agent orchestrator: issue -> PR, 85% success"),
    (None, "root-cause agent cut debugging time 80%"),
    (None, "doc pipeline 90% faster, $50K revenue"),
    ("", ""),
    ("Building", "AgentRL: agent observability & eval SDK"),
    (None, "autonomous equity trading agent"),
    ("", ""),
    ("Contact", "linkedin.com/in/suhaas-surapaneni"),
]


def main():
    top = 58
    body = []
    step = 0

    def animated(markup, y):
        nonlocal step
        if STATIC:
            return markup
        delay = 0.35 + step * 0.09
        step += 1
        return f'<g class="l" style="animation-delay:{delay:.2f}s">{markup}</g>'

    y = top
    body.append(
        animated(
            f'<text x="{PAD}" y="{y}"><tspan class="user">suhaas</tspan><tspan class="dim">@</tspan>'
            f'<tspan class="user">github</tspan></text>'
            f'<text class="dim" x="{PAD}" y="{y + LINE_H - 4}">{"-" * 13}</text>',
            y,
        )
    )
    y += LINE_H * 2

    for key, value in LINES:
        if key == "":
            y += LINE_H // 2
            continue
        label = f'<text class="key" x="{PAD}" y="{y}">{key}</text>' if key else ""
        body.append(animated(f'{label}<text x="{PAD + KEY_W}" y="{y}">{escape(value)}</text>', y))
        y += LINE_H

    y += 6
    swatches = "".join(
        f'<rect x="{PAD + KEY_W + i * 24}" y="{y - 12}" width="20" height="14" rx="3" fill="{color}"/>'
        for i, color in enumerate(SWATCHES)
    )
    body.append(animated(swatches, y))
    height = y + 24

    OUT.write_text(
        f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" height="{height}" role="img" aria-label="About Suhaas Surapaneni">
<style>
text {{ font-family: {FONT}; font-size: 13px; fill: #c9d1d9; }}
.key {{ fill: #58a6ff; font-weight: 600; }}
.user {{ fill: #39d353; font-weight: 700; font-size: 14px; }}
.dim {{ fill: #7d8590; }}
.title {{ font-size: 12px; fill: #7d8590; }}
.l {{ opacity: 0; animation: print .4s ease-out both; }}
@keyframes print {{ from {{ opacity: 0; transform: translateX(-8px); }} to {{ opacity: 1; transform: none; }} }}
@media (prefers-reduced-motion: reduce) {{ .l {{ animation: none; opacity: 1; }} }}
</style>
<rect x=".5" y=".5" width="{WIDTH - 1}" height="{height - 1}" rx="10" fill="#0d1117" stroke="#30363d"/>
<circle cx="18" cy="17" r="5" fill="#ff5f56"/><circle cx="34" cy="17" r="5" fill="#ffbd2e"/><circle cx="50" cy="17" r="5" fill="#27c93f"/>
<text class="title" x="{WIDTH / 2}" y="21" text-anchor="middle">suhaas@github: ~</text>
{chr(10).join(body)}
</svg>
"""
    )
    print(f"-> {OUT} ({WIDTH}x{height})")


if __name__ == "__main__":
    main()
