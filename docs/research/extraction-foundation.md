# Extraction Foundation Research

## Objective

Investigate strategies to decouple extraction from HTML structure.

## Experiments

### Playwright + PDF

Result:
- Successfully renders selectable text.
- Suitable as an intermediate document representation.

Limitations:
- Print rendering differs from screen rendering.
- Requires additional investigation.

---

### PyMuPDF

Result:
- Provides words, blocks and layout coordinates.
- Geometric information appears sufficient to reconstruct document structure.

Limitations:
- Does not infer semantic relationships.

---

### Camelot

Result:
- Correctly detects some tables.

Limitations:
- Table detection is inconsistent.
- Does not solve semantic extraction.

---

### Accessibility Tree

Result:
- Modern Playwright no longer exposes the previous Accessibility API.
- CDP remains available but was not investigated further.

Assessment:
- Unlikely to provide sufficient semantic information for the current HTML structure.

---

## Current Direction

Investigate geometric interpretation of rendered documents using spatial indexing.

Potential techniques:

- bounding boxes
- STRtree
- geometric clustering
- semantic grouping

No implementation has been selected yet.