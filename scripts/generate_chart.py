#!/usr/bin/env python3
"""Generate compliance chart using graphviz."""

import json
from pathlib import Path

def load_results(results_dir: str, experiment: str) -> dict[int, list[float]]:
    """Load results grouped by padding size."""
    metrics_dir = Path(results_dir) / "metrics"
    by_padding = {}

    for f in metrics_dir.glob(f"{experiment}*.json"):
        data = json.loads(f.read_text())
        p = data["parameters"].get("padding_size", 0)
        if p not in by_padding:
            by_padding[p] = []
        by_padding[p].append(data["overall_compliance"])

    return by_padding

def generate_dot(by_padding: dict[int, list[float]]) -> str:
    """Generate graphviz DOT for horizontal bar chart."""

    lines = [
        'digraph compliance {',
        '    rankdir=LR;',
        '    node [shape=none, fontname="Helvetica"];',
        '    edge [style=invis];',
        '',
        '    // Title',
        '    title [label="CLAUDE.md Compliance vs Context Size\\n(01-scale experiment)", fontsize=16, fontname="Helvetica Bold"];',
        '',
        '    // Legend',
        '    legend [label=<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="2">',
        '        <TR><TD BGCOLOR="#4CAF50" WIDTH="20"> </TD><TD> 80-100%</TD></TR>',
        '        <TR><TD BGCOLOR="#FFC107" WIDTH="20"> </TD><TD> 40-79%</TD></TR>',
        '        <TR><TD BGCOLOR="#F44336" WIDTH="20"> </TD><TD> 0-39%</TD></TR>',
        '    </TABLE>>];',
        '',
        '    // Data rows',
        '    subgraph cluster_chart {',
        '        label="";',
        '        style=invis;',
        '',
    ]

    prev_node = None
    for padding in sorted(by_padding.keys()):
        vals = by_padding[padding]
        avg = sum(vals) / len(vals)
        n = len(vals)

        # Color based on compliance
        if avg >= 0.8:
            color = "#4CAF50"  # Green
        elif avg >= 0.4:
            color = "#FFC107"  # Yellow
        else:
            color = "#F44336"  # Red

        # Bar width proportional to compliance (max 300px)
        bar_width = max(int(avg * 300), 5)

        # Format padding size
        if padding >= 1000:
            label = f"{padding // 1000}K"
        else:
            label = str(padding)

        node_id = f"p{padding}"

        lines.append(f'        {node_id} [label=<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0">')
        lines.append(f'            <TR>')
        lines.append(f'                <TD ALIGN="RIGHT" WIDTH="50">{label}</TD>')
        lines.append(f'                <TD BGCOLOR="{color}" WIDTH="{bar_width}" HEIGHT="25"> </TD>')
        lines.append(f'                <TD ALIGN="LEFT"> {avg:.0%} (n={n})</TD>')
        lines.append(f'            </TR>')
        lines.append(f'        </TABLE>>];')

        if prev_node:
            lines.append(f'        {prev_node} -> {node_id};')
        prev_node = node_id

    lines.extend([
        '    }',
        '',
        '    // Layout',
        '    title -> legend [style=invis];',
        f'    legend -> p{min(by_padding.keys())} [style=invis];',
        '}',
    ])

    return '\n'.join(lines)

def main():
    results_dir = "results"
    experiment = "01-scale"

    by_padding = load_results(results_dir, experiment)

    if not by_padding:
        print("No results found")
        return

    dot = generate_dot(by_padding)

    # Write DOT file
    dot_file = Path("results/charts/01-scale-compliance.dot")
    dot_file.parent.mkdir(parents=True, exist_ok=True)
    dot_file.write_text(dot)
    print(f"Generated: {dot_file}")

    # Generate PNG
    import subprocess
    png_file = dot_file.with_suffix(".png")
    result = subprocess.run(
        ["dot", "-Tpng", str(dot_file), "-o", str(png_file)],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"Generated: {png_file}")
    else:
        print(f"Error generating PNG: {result.stderr}")
        print("Install graphviz with: brew install graphviz")

if __name__ == "__main__":
    main()
