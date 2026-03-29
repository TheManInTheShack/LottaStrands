# Parse Issues Log

Known anomalies in the parse output that have not yet been resolved.
Each entry describes the issue, its location, and the proposed resolution.

---

## Issue 001 ✓ RESOLVED
**Heading:** `A HIGHWAY SIGN:  SIMI VALLEY ROAD` (scene 12)
**Issue:** Colon mid-string not caught by stage_direction classifier;
HIGHWAY matched location patterns causing false scene classification.
**Fix:** Added SIGN to SHOT_KEYWORDS and moved SHOT_KEYWORDS check before
SCENE_PATTERNS in classify_heading so shot keywords win on conflict.
Removed CRANE from SHOT_KEYWORDS to avoid false positive with
CRANE JACKSON'S FOUNTAIN STREET THEATER (proper name, not camera move).

## Issue 002 ✓ RESOLVED
**Heading:** `COFFEE SHOP` (scene 16)
**Issue:** `DUDE'S BATHROOM` and `NORTH HOLLYWOOD AUTO CIRCUS` appeared as
shots within COFFEE SHOP, but they are distinct locations.
**Fix:** Added BATHROOM and CIRCUS to SCENE_PATTERNS location keyword list.

## Issue 003 ✓ RESOLVED
**Heading:** `CHIEF'S OFFICE` (scene 31)
**Issue:** `CAB` appeared as a shot within CHIEF'S OFFICE, but it is a
distinct location.
**Fix:** Added CAB to SCENE_PATTERNS location keyword list.
