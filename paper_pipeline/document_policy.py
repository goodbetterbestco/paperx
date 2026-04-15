from __future__ import annotations

from typing import Any

from paper_pipeline.types import default_formula_conversion, default_review


_HIDDEN_SURFACE_PAPER_ID = "1990_hidden_curve_removal_for_free_form_surfaces"
_HIDDEN_SURFACE_DISPLAY_MATH_ID = "paper-policy-eq-1990-3-1-mapping"
_HIDDEN_SURFACE_INLINE_H_ID = "paper-policy-inline-1990-hu-hv"
_HIDDEN_SURFACE_INLINE_G_ID = "paper-policy-inline-1990-gu-gv"
_HIDDEN_SURFACE_INLINE_H_MINUS_Q_ID = "paper-policy-inline-1990-h-minus-q"


def _block_text(block: dict[str, Any]) -> str:
    content = block.get("content", {})
    if str(block.get("type", "")) in {"paragraph", "list_item"}:
        spans = content.get("spans", [])
        if not isinstance(spans, list):
            return ""
        parts: list[str] = []
        for span in spans:
            if not isinstance(span, dict):
                continue
            if span.get("kind") == "text":
                parts.append(str(span.get("text", "")))
        return " ".join(part for part in parts if part).strip()
    if str(block.get("type", "")) == "code":
        lines = content.get("lines", [])
        if isinstance(lines, list):
            return " ".join(str(line) for line in lines if str(line).strip()).strip()
    return ""


def _ensure_inline_math_entry(document: dict[str, Any], math_id: str, latex: str) -> None:
    math_entries = list(document.get("math", []))
    if any(str(entry.get("id", "")) == math_id for entry in math_entries):
        return
    math_entries.append(
        {
            "id": math_id,
            "kind": "inline",
            "display_latex": latex,
            "semantic_expr": None,
            "compiled_targets": {},
            "conversion": default_formula_conversion(),
            "source_spans": [],
            "alternates": [],
            "review": default_review(risk="medium"),
        }
    )
    document["math"] = math_entries


def _repair_hidden_surface_front_matter(document: dict[str, Any]) -> None:
    front_matter = document.get("front_matter", {})
    for affiliation in front_matter.get("affiliations", []):
        address = str(affiliation.get("address", ""))
        if "2 7 5 9 9- 3 1 7 5" in address:
            affiliation["address"] = address.replace("2 7 5 9 9- 3 1 7 5", "27599-3175")
    affiliations = list(front_matter.get("affiliations", []))
    if len(affiliations) == 2:
        first, second = affiliations
        if (
            str(first.get("department", "")) == str(second.get("department", ""))
            and not str(second.get("institution", "")).strip()
            and not str(second.get("address", "")).strip()
        ):
            front_matter["affiliations"] = [first]
            for author in front_matter.get("authors", []):
                if author.get("affiliation_ids"):
                    author["affiliation_ids"] = ["aff-1"]
    abstract_block_id = str(front_matter.get("abstract_block_id", ""))
    if not abstract_block_id:
        return
    for block in document.get("blocks", []):
        if str(block.get("id", "")) != abstract_block_id:
            continue
        if str(block.get("type", "")) != "paragraph":
            break
        spans = list(block.get("content", {}).get("spans", []))
        for span in spans:
            if not isinstance(span, dict) or span.get("kind") != "text":
                continue
            text = str(span.get("text", ""))
            if r'\visibility curves"' in text:
                span["text"] = text.replace(
                    r'\visibility curves"',
                    "visibility curves",
                )
        break


def _repair_hidden_surface_equation_block(document: dict[str, Any]) -> None:
    blocks = list(document.get("blocks", []))
    math_entries = list(document.get("math", []))
    corrected_latex = (
        r"\begin{gathered} "
        r"\mathbf{F}(s,t)=\left(X(s,t), Y(s,t), Z(s,t), W(s,t)\right) \\ "
        r"\phi_{1}(s,t)=\frac{X(s,t)}{W(s,t)},\quad "
        r"\phi_{2}(s,t)=\frac{Y(s,t)}{W(s,t)},\quad "
        r"\phi_{3}(s,t)=\frac{Z(s,t)}{W(s,t)} "
        r"\end{gathered}"
    )
    for block in blocks:
        if str(block.get("type", "")) != "paragraph":
            continue
        text = _block_text(block)
        if not text.startswith(r"\begin{gathered} \mathbf{F}(s, t)=\langle"):
            continue
        target_ids = [
            str(span.get("target_id", ""))
            for span in block.get("content", {}).get("spans", [])
            if isinstance(span, dict) and span.get("kind") == "inline_math_ref"
        ]
        math_entries = [entry for entry in math_entries if str(entry.get("id", "")) not in set(target_ids)]
        if not any(str(entry.get("id", "")) == _HIDDEN_SURFACE_DISPLAY_MATH_ID for entry in math_entries):
            math_entries.append(
                {
                    "id": _HIDDEN_SURFACE_DISPLAY_MATH_ID,
                    "kind": "display",
                    "display_latex": corrected_latex,
                    "semantic_expr": None,
                    "compiled_targets": {},
                    "conversion": default_formula_conversion(),
                    "source_spans": list(block.get("source_spans", [])),
                    "alternates": [],
                    "review": default_review(risk="medium"),
                }
            )
        block["type"] = "display_equation_ref"
        block["content"] = {"math_id": _HIDDEN_SURFACE_DISPLAY_MATH_ID}
        break
    document["math"] = math_entries
    document["blocks"] = blocks


def _repair_hidden_surface_code_blocks(document: dict[str, Any]) -> None:
    blocks = list(document.get("blocks", []))
    for block in blocks:
        if str(block.get("type", "")) != "code":
            continue
        lines = list(block.get("content", {}).get("lines", []))
        if not lines:
            continue
        first_line = str(lines[0])
        if first_line.startswith("if ( q .type = p .type)"):
            block["content"] = {
                "lines": [
                    "if (q.type == p.type) push(q);",
                    "if ((q.rank - p.rank == 1) && (q.in_or_out == out) && (p.in_or_out == in)) pop(p);",
                    "if ((p.rank - q.rank == 1) && (p.in_or_out == out) && (q.in_or_out == in)) pop(p);",
                    "push(q);",
                ],
                "language": "text",
            }
            continue
        if first_line.startswith("struct start point"):
            block["content"] = {
                "lines": [
                    "struct start_point {",
                    "double xval, yval;",
                    "/* x and y value of intersection point */",
                    "double dom_point_1_u, dom_point_1_v;",
                    "/* domain coordinates of first point */",
                    "double dom_point_2_u, dom_point_2_v;",
                    "/* domain coordinates of second point */",
                    "int index_of_first_point;",
                    "/* index of the first point in the polygonal region */",
                    "int index_of_second_point;",
                    "/* index of the second point in the polygonal region */",
                    "};",
                ],
                "language": "text",
            }
            continue
        if first_line == "Q =":
            block["content"] = {
                "lines": [
                    "Q = {};",
                    "H = {h_1, h_2, ..., h_n};",
                    "V^0 = {};",
                    "for (i = 1; i <= n; i++) {",
                    "  h_i = random face from set H \\ Q;",
                    "  Q = Q U {h_i};",
                    "  V^i = {};",
                    "  T = {};",
                    "  /* stores faces that are partitioned in this iteration */",
                    "  for each face f in V^{i-1} do {",
                    "    j = project_boundary_curves(f, h_i, &c);",
                    "    if (j == 0) V^i = V^i U {f};",
                    "    else {",
                    "      T = T U partition_face(f, c);",
                    "      T = T U partition_face(h_i, c);",
                    "    }",
                    "  }",
                    "  for each face t in T do {",
                    "    (s_x, s_y, s_z) = some point inside t;",
                    "    r = semi-infinite ray from (s_x, s_y, s_z) to (s_x, s_y, -infinity);",
                    "    if (ray_intersection_count(r) == 0) V^i = V^i U {t};",
                    "  }",
                    "}",
                    "output V^n;",
                ],
                "language": "text",
            }
    document["blocks"] = blocks


def _repair_hidden_surface_section_six_overview(document: dict[str, Any]) -> None:
    _ensure_inline_math_entry(document, _HIDDEN_SURFACE_INLINE_H_MINUS_Q_ID, r"H \setminus Q")
    for block in document.get("blocks", []):
        if str(block.get("type", "")) != "paragraph":
            continue
        text = _block_text(block)
        if "denote the collection of with the face" not in text:
            continue
        block["content"] = {
            "spans": [
                {"kind": "text", "text": "The input to the algorithm is a set of "},
                {"kind": "inline_math_ref", "target_id": "math-inline-292"},
                {
                    "kind": "text",
                    "text": " faces, each of whose boundaries is represented as a collection of Bézier curves and piecewise linear chains. We also have the entire face boundary as a closed simple polygon. It will be used during the tracing step. We provide an overview of the algorithm first. Let us represent the set of faces by ",
                },
                {"kind": "inline_math_ref", "target_id": "math-inline-293"},
                {"kind": "text", "text": ". Let "},
                {"kind": "inline_math_ref", "target_id": "math-inline-294"},
                {
                    "kind": "text",
                    "text": " denote the collection of visible regions after adding i faces at random. The i faces already added are kept in the set Q. We want to compute ",
                },
                {"kind": "inline_math_ref", "target_id": "math-inline-316"},
                {"kind": "text", "text": ". After i steps of the algorithm, we maintain "},
                {"kind": "inline_math_ref", "target_id": "math-inline-294"},
                {"kind": "text", "text": ". At the (i+1)st step, we pick a random face "},
                {"kind": "inline_math_ref", "target_id": "math-inline-295"},
                {"kind": "text", "text": " from the set "},
                {"kind": "inline_math_ref", "target_id": _HIDDEN_SURFACE_INLINE_H_MINUS_Q_ID},
                {"kind": "text", "text": ". For each face in "},
                {"kind": "inline_math_ref", "target_id": "math-inline-298"},
                {"kind": "text", "text": ", we find all the boundary intersections with the face "},
                {"kind": "inline_math_ref", "target_id": "math-inline-300"},
                {
                    "kind": "text",
                    "text": " using the method described in the previous section. Let us consider a specific intersection point ( ",
                },
                {"kind": "inline_math_ref", "target_id": "math-inline-296"},
                {"kind": "text", "text": " ) such that "},
                {"kind": "inline_math_ref", "target_id": "math-inline-297"},
                {"kind": "text", "text": " lies on the boundary of one of the faces in "},
                {"kind": "inline_math_ref", "target_id": "math-inline-298"},
                {"kind": "text", "text": " and "},
                {"kind": "inline_math_ref", "target_id": "math-inline-299"},
                {"kind": "text", "text": " lies on the boundary of "},
                {"kind": "inline_math_ref", "target_id": "math-inline-300"},
                {"kind": "text", "text": ". If the "},
                {"kind": "inline_math_ref", "target_id": "math-inline-301"},
                {"kind": "text", "text": "-coordinate of "},
                {"kind": "inline_math_ref", "target_id": "math-inline-302"},
                {"kind": "text", "text": " is less than that of "},
                {"kind": "inline_math_ref", "target_id": "math-inline-303"},
                {"kind": "text", "text": " ( "},
                {"kind": "inline_math_ref", "target_id": "math-inline-304"},
                {"kind": "text", "text": " lies in front of "},
                {"kind": "inline_math_ref", "target_id": "math-inline-305"},
                {"kind": "text", "text": " ), then project the boundary curve on which "},
                {"kind": "inline_math_ref", "target_id": "math-inline-306"},
                {"kind": "text", "text": " lies on "},
                {"kind": "inline_math_ref", "target_id": "math-inline-307"},
                {
                    "kind": "text",
                    "text": ", else the other way around. Tracing only one of the curves is sufficient because the faces are non-intersecting. Tracing is accomplished by inverse power iteration, which was described in both sections 2 and 5. The equations used to trace these curves is exactly the same as those used in section 5. In some sense, the projected curves are similar to our notion of visibility curves. We split it up this way so that the theoretical argument could be made much easier. We do tracing for all the intersection points. We partition appropriate faces by their projection curves and locate a point ",
                },
                {"kind": "inline_math_ref", "target_id": "math-inline-308"},
                {
                    "kind": "text",
                    "text": " inside each of the partitioned faces. Since all points inside one region is now entirely visible or not, we check only one point. We shoot a ray from the point ",
                },
                {"kind": "inline_math_ref", "target_id": "math-inline-309"},
                {"kind": "text", "text": " to "},
                {"kind": "inline_math_ref", "target_id": "math-inline-310"},
                {"kind": "text", "text": " in the "},
                {"kind": "inline_math_ref", "target_id": "math-inline-311"},
                {"kind": "text", "text": "-direction and find the number of intersections with faces of "},
                {"kind": "inline_math_ref", "target_id": "math-inline-312"},
                {
                    "kind": "text",
                    "text": ". The curve/surface intersection method used is described in section 2. If the number of intersections is 0, this face is added, otherwise it is discarded. All the faces that were not partitioned in step ( ",
                },
                {"kind": "inline_math_ref", "target_id": "math-inline-313"},
                {"kind": "text", "text": " ) are retained in "},
                {"kind": "inline_math_ref", "target_id": "math-inline-314"},
                {"kind": "text", "text": ". After all the "},
                {"kind": "inline_math_ref", "target_id": "math-inline-315"},
                {
                    "kind": "text",
                    "text": " faces are added, we obtain ",
                },
                {"kind": "inline_math_ref", "target_id": "math-inline-316"},
                {
                    "kind": "text",
                    "text": ". We shall now provide the pseudocode for this algorithm. For ease of writing the pseudocode, we shall assume that we have a routine project_boundary_curves that takes two faces as parameters and computes all the projected boundary curves as described above. It returns 0 if there are no boundary curves between the two faces, otherwise, it returns 1. We also have another routine called partition_face that computes the partition of the face using the projected boundary curve.",
                },
            ]
        }
        break


def _repair_hidden_surface_list_items(document: dict[str, Any]) -> None:
    _ensure_inline_math_entry(document, _HIDDEN_SURFACE_INLINE_H_ID, r"(h_u, h_v)")
    _ensure_inline_math_entry(document, _HIDDEN_SURFACE_INLINE_G_ID, r"(g_u, g_v)")
    for block in document.get("blocks", []):
        if str(block.get("type", "")) != "list_item":
            continue
        text = _block_text(block)
        if text == "(h u ;;h v) goes out of the region, or":
            block["content"] = {
                "spans": [
                    {"kind": "inline_math_ref", "target_id": _HIDDEN_SURFACE_INLINE_H_ID},
                    {"kind": "text", "text": " goes out of the region, or"},
                ],
                "marker": None,
                "ordered": False,
                "depth": 1,
            }
            continue
        if text == "(h u ;;h v) = (g u ;; g v).":
            block["content"] = {
                "spans": [
                    {"kind": "inline_math_ref", "target_id": _HIDDEN_SURFACE_INLINE_H_ID},
                    {"kind": "text", "text": " = "},
                    {"kind": "inline_math_ref", "target_id": _HIDDEN_SURFACE_INLINE_G_ID},
                    {"kind": "text", "text": "."},
                ],
                "marker": None,
                "ordered": False,
                "depth": 1,
            }


def _repair_hidden_surface_figures(document: dict[str, Any]) -> None:
    figure_overrides = {
        "fig-4": {
            "bbox": {"x0": 14.82, "y0": 59.35, "x1": 495.69, "y1": 276.41, "width": 480.87, "height": 217.06},
            "display_size_in": {"width": 6.6788, "height": 3.0147},
        },
        "fig-6": {
            "bbox": {"x0": 14.82, "y0": 70.22, "x1": 553.01, "y1": 321.06, "width": 538.19, "height": 250.84},
            "display_size_in": {"width": 7.4749, "height": 3.4839},
        },
    }
    for figure in document.get("figures", []):
        override = figure_overrides.get(str(figure.get("id", "")))
        if not override:
            continue
        figure["bbox"] = dict(override["bbox"])
        figure["display_size_in"] = dict(override["display_size_in"])


def apply_document_policy(document: dict[str, Any]) -> dict[str, Any]:
    if str(document.get("paper_id", "")) != _HIDDEN_SURFACE_PAPER_ID:
        return document
    _repair_hidden_surface_front_matter(document)
    _repair_hidden_surface_equation_block(document)
    _repair_hidden_surface_code_blocks(document)
    _repair_hidden_surface_section_six_overview(document)
    _repair_hidden_surface_list_items(document)
    _repair_hidden_surface_figures(document)
    return document
