# Source Corrections Log

Manual edits made to `the_big_lebowski.txt` after acquisition.
Each entry records the original text, the corrected text, location, and reason.

---

## Correction 001
**File:** `the_big_lebowski.txt`
**Location:** Line ~1705 (action paragraph, Dude asleep on couch)
**Issue:** Line break mid-sentence split an ALL CAPS label across two lines.
The second line (`BEACH LEAGUE PLAYOFFS 1987.`) was being classified as a
scene heading by the parser.

**Original:**
```
In his outflung hand lies a cassette case labeled VENICE
BEACH LEAGUE PLAYOFFS 1987.
```

**Corrected:**
```
In his outflung hand lies a cassette case labeled VENICE BEACH LEAGUE PLAYOFFS 1987.
```
