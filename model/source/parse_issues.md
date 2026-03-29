# Parse Issues Log

Known anomalies in the parse output that have not yet been resolved.
Each entry describes the issue, its location, and the proposed resolution.

---

## Issue 001
**Heading:** `A HIGHWAY SIGN:  SIMI VALLEY ROAD` (scene 12)
**Issue:** Contains a colon mid-string (not at the end), so it was not
caught by the stage_direction classifier. It is a shot description, not
a scene, but currently classified as a scene because `ROAD` is not in
the location keyword list and no shot opener word appears at the start.
**Proposed fix:** Detect colons anywhere in the heading (not just at end)
as a stage direction signal, or add `SIGN` to the shot keywords.

## Issue 002
**Heading:** `COFFEE SHOP` (scene 16)
**Issue:** `DUDE'S BATHROOM` and `NORTH HOLLYWOOD AUTO CIRCUS` appear as
shots within COFFEE SHOP, but they are distinct locations and should be
their own scenes.
**Proposed fix:** Expand the location keyword list to include BATHROOM,
CIRCUS, and similar terms.

## Issue 003
**Heading:** `CHIEF'S OFFICE` (scene 31)
**Issue:** `CAB` appears as a shot within CHIEF'S OFFICE, but it is a
distinct location.
**Proposed fix:** Add CAB to the location keyword list or scene patterns.
