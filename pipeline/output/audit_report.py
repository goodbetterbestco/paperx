from __future__ import annotations

from typing import Any


def render_audit_markdown(report: dict[str, Any], *, top_n: int) -> str:
    lines = [
        "# Canonical Corpus Audit",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- Papers audited: `{report['paper_count']}`",
        f"- Canonical coverage: `{report['canonical_count']} / {report['paper_count']}`",
        f"- Missing canonical outputs: `{report['missing_canonical_count']}`",
        f"- Semantic IR coverage: `{report['formula_classification']['semantic_expr_units']} / {report['formula_classification']['semantic_formula_units']}` semantic formula units",
        f"- JSON report: `{report['report_paths']['json']}`",
        f"- Markdown report: `{report['report_paths']['markdown']}`",
        "",
    ]

    corpus_policy_counts = report["formula_classification"]["semantic_policies"]
    corpus_category_counts = report["formula_classification"]["categories"]
    corpus_role_counts = report["formula_classification"]["roles"]
    if corpus_policy_counts or corpus_category_counts:
        top_roles = sorted(corpus_role_counts.items(), key=lambda item: (-int(item[1]), item[0]))[:6]
        top_categories = sorted(corpus_category_counts.items(), key=lambda item: (-int(item[1]), item[0]))[:8]
        lines.extend(
            [
                "## Formula Policy Coverage",
                "",
                f"- Semantic formula units: `{corpus_policy_counts.get('semantic', 0)}`",
                f"- Structure-only formula units: `{corpus_policy_counts.get('structure_only', 0)}`",
                f"- Graphic-only formula units: `{corpus_policy_counts.get('graphic_only', 0)}`",
            ]
        )
        if top_roles:
            lines.append(f"- Top roles: {', '.join(f'`{name}`={count}' for name, count in top_roles)}")
        if top_categories:
            lines.append(f"- Top categories: {', '.join(f'`{name}`={count}' for name, count in top_categories)}")
        lines.append("")

    if report["missing_canonical_papers"]:
        lines.extend(
            [
                "## Missing Canonical Outputs",
                "",
            ]
        )
        for index, paper_id in enumerate(report["missing_canonical_papers"], start=1):
            lines.append(f"{index}. `{paper_id}`")
        lines.append("")

    lines.extend(
        [
            "## Highest-Risk Canonical Papers",
            "",
        ]
    )

    canonical_papers = [paper for paper in report["papers"] if paper.get("has_canonical")]
    for index, paper in enumerate(canonical_papers[:top_n], start=1):
        counts = paper["counts"]
        top_issues = sorted(paper["issues"], key=lambda issue: (-int(issue["count"]), issue["label"]))[:4]
        issue_summary = ", ".join(f"{issue['label']}={issue['count']}" for issue in top_issues) or "none"
        lines.extend(
            [
                f"{index}. `{paper['paper_id']}` — score `{paper['score']}`",
                f"   Title: {paper['title']}",
                f"   Path: `{paper['canonical_path']}`",
                f"   Counts: math `{counts['math_entries']}`, figures `{counts['figures']}`, references `{counts['references']}`, sections `{counts['sections']}`",
                f"   Formula policies: semantic `{counts['semantic_formula_units']}`, structure-only `{counts['structure_only_formula_units']}`, graphic-only `{counts['graphic_only_formula_units']}`, semantic IR `{counts['semantic_expr_units']}`",
                f"   Main issues: {issue_summary}",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"
