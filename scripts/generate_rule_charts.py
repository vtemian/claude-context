#!/usr/bin/env python3
"""Generate comparison charts for rule-count experiments (03 and 04)."""

import json
from pathlib import Path


def load_results(results_dir: str, experiment: str) -> dict[int, list[float]]:
    """Load results grouped by rule count."""
    metrics_dir = Path(results_dir) / "metrics"
    by_rules = {}

    for f in metrics_dir.glob(f"{experiment}*.json"):
        data = json.loads(f.read_text())
        r = data["parameters"].get("num_rules", 0)
        if r not in by_rules:
            by_rules[r] = []
        by_rules[r].append(data["overall_compliance"])

    return by_rules


def generate_comparison_dot(exp03: dict, exp04: dict) -> str:
    """Generate graphviz DOT for side-by-side comparison."""

    lines = [
        'digraph comparison {',
        '    rankdir=TB;',
        '    node [shape=none, fontname="Helvetica"];',
        '    edge [style=invis];',
        '',
        '    // Title',
        '    title [label="Rule Count Compliance: Terse vs Verbose\\n(Experiments 03 & 04)", fontsize=16, fontname="Helvetica Bold"];',
        '',
        '    // Legend',
        '    legend [label=<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="2">',
        '        <TR><TD BGCOLOR="#2196F3" WIDTH="20"> </TD><TD> Terse (03)</TD>',
        '            <TD WIDTH="20"> </TD>',
        '            <TD BGCOLOR="#FF9800" WIDTH="20"> </TD><TD> Verbose (04)</TD></TR>',
        '        <TR><TD COLSPAN="5"> </TD></TR>',
        '        <TR><TD BGCOLOR="#4CAF50" WIDTH="20"> </TD><TD> 80-100%</TD>',
        '            <TD WIDTH="20"> </TD>',
        '            <TD BGCOLOR="#FFC107" WIDTH="20"> </TD><TD> 40-79%</TD></TR>',
        '        <TR><TD BGCOLOR="#F44336" WIDTH="20"> </TD><TD> 0-39%</TD>',
        '            <TD COLSPAN="3"> </TD></TR>',
        '    </TABLE>>];',
        '',
        '    // Data table',
        '    data [label=<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">',
        '        <TR><TD BGCOLOR="#E0E0E0"><B>Rules</B></TD><TD BGCOLOR="#E0E0E0"><B>Terse</B></TD><TD BGCOLOR="#E0E0E0"><B>Verbose</B></TD><TD BGCOLOR="#E0E0E0"><B>Diff</B></TD></TR>',
    ]

    for rules in sorted(exp03.keys()):
        terse_vals = exp03[rules]
        verbose_vals = exp04.get(rules, [0])

        terse_avg = sum(terse_vals) / len(terse_vals)
        verbose_avg = sum(verbose_vals) / len(verbose_vals)
        diff = verbose_avg - terse_avg

        # Color based on compliance
        def get_color(val):
            if val >= 0.8:
                return "#C8E6C9"  # Light green
            elif val >= 0.4:
                return "#FFF9C4"  # Light yellow
            else:
                return "#FFCDD2"  # Light red

        terse_color = get_color(terse_avg)
        verbose_color = get_color(verbose_avg)

        # Diff color
        if diff > 0.05:
            diff_color = "#C8E6C9"
            diff_sign = "+"
        elif diff < -0.05:
            diff_color = "#FFCDD2"
            diff_sign = ""
        else:
            diff_color = "#FFFFFF"
            diff_sign = ""

        lines.append(f'        <TR><TD>{rules}</TD>'
                    f'<TD BGCOLOR="{terse_color}">{terse_avg:.0%}</TD>'
                    f'<TD BGCOLOR="{verbose_color}">{verbose_avg:.0%}</TD>'
                    f'<TD BGCOLOR="{diff_color}">{diff_sign}{diff:.0%}</TD></TR>')

    # Summary row
    terse_mean = sum(sum(v)/len(v) for v in exp03.values()) / len(exp03)
    verbose_mean = sum(sum(v)/len(v) for v in exp04.values()) / len(exp04)
    diff_mean = verbose_mean - terse_mean

    lines.append(f'        <TR><TD BGCOLOR="#E0E0E0"><B>Mean</B></TD>'
                f'<TD BGCOLOR="#E0E0E0"><B>{terse_mean:.0%}</B></TD>'
                f'<TD BGCOLOR="#E0E0E0"><B>{verbose_mean:.0%}</B></TD>'
                f'<TD BGCOLOR="#E0E0E0"><B>{diff_mean:+.0%}</B></TD></TR>')

    lines.extend([
        '    </TABLE>>];',
        '',
        '    title -> legend [style=invis];',
        '    legend -> data [style=invis];',
        '}',
    ])

    return '\n'.join(lines)


def generate_bar_chart_dot(exp03: dict, exp04: dict) -> str:
    """Generate horizontal bar chart comparing both experiments."""

    lines = [
        'digraph barchart {',
        '    rankdir=LR;',
        '    node [shape=none, fontname="Helvetica"];',
        '    edge [style=invis];',
        '',
        '    // Title',
        '    title [label="Compliance by Rule Count\\nTerse (blue) vs Verbose (orange)", fontsize=14, fontname="Helvetica Bold"];',
        '',
    ]

    prev_node = None
    for rules in sorted(exp03.keys()):
        terse_avg = sum(exp03[rules]) / len(exp03[rules])
        verbose_avg = sum(exp04.get(rules, [0])) / len(exp04.get(rules, [1]))

        terse_width = max(int(terse_avg * 200), 2)
        verbose_width = max(int(verbose_avg * 200), 2)

        node_id = f"r{rules}"

        lines.append(f'    {node_id} [label=<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="2">')
        lines.append(f'        <TR><TD ALIGN="RIGHT" WIDTH="40">{rules}</TD>')
        lines.append(f'            <TD BGCOLOR="#2196F3" WIDTH="{terse_width}" HEIGHT="12"> </TD>')
        lines.append(f'            <TD ALIGN="LEFT" WIDTH="40">{terse_avg:.0%}</TD></TR>')
        lines.append(f'        <TR><TD></TD>')
        lines.append(f'            <TD BGCOLOR="#FF9800" WIDTH="{verbose_width}" HEIGHT="12"> </TD>')
        lines.append(f'            <TD ALIGN="LEFT">{verbose_avg:.0%}</TD></TR>')
        lines.append(f'    </TABLE>>];')

        if prev_node:
            lines.append(f'    {prev_node} -> {node_id};')
        prev_node = node_id

    lines.extend([
        '',
        f'    title -> r{min(exp03.keys())} [style=invis];',
        '}',
    ])

    return '\n'.join(lines)


def main():
    results_dir = "/Users/whitemonk/projects/ai/claude-context/results"

    exp03 = load_results(results_dir, "03-rule-count")
    exp04 = load_results(results_dir, "04-verbose-rules")

    if not exp03 or not exp04:
        print("Missing results for one or both experiments")
        return

    charts_dir = Path(results_dir) / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)

    # Generate comparison table
    dot = generate_comparison_dot(exp03, exp04)
    dot_file = charts_dir / "03-04-comparison.dot"
    dot_file.write_text(dot)
    print(f"Generated: {dot_file}")

    # Generate bar chart
    dot = generate_bar_chart_dot(exp03, exp04)
    dot_file = charts_dir / "03-04-barchart.dot"
    dot_file.write_text(dot)
    print(f"Generated: {dot_file}")

    # Generate PNGs
    import subprocess
    for dot_file in charts_dir.glob("03-04*.dot"):
        png_file = dot_file.with_suffix(".png")
        result = subprocess.run(
            ["dot", "-Tpng", str(dot_file), "-o", str(png_file)],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"Generated: {png_file}")
        else:
            print(f"Error: {result.stderr}")


if __name__ == "__main__":
    main()
