"""
ADD RESIDENCY RECORDING SLIDE
==============================

Run this in your GitHub/malaysia-tax-guide folder:

    cd C:\\Users\\elect\\OneDrive\\Documents\\GitHub\\malaysia-tax-guide
    python add_residency_slide.py

It edits index.html in place, inserting a new slide after 
"Resident or non-resident?" and renumbering everything after it.
"""

import re, os, sys

FILE = "index.html"

if not os.path.exists(FILE):
    print(f"ERROR: Can't find '{FILE}' in {os.getcwd()}")
    print("Make sure you're in the malaysia-tax-guide folder.")
    sys.exit(1)

with open(FILE, "r", encoding="utf-8") as f:
    html = f.read()

# --- Step 1: Find the residency slide (contains "Resident or") ---
# Find data-slide="3" (slide 4, 0-indexed)
resident_match = re.search(r'Resident or', html)
if not resident_match:
    print("ERROR: Could not find 'Resident or' in the file.")
    sys.exit(1)

# Find the start of the NEXT slide after this one
# We look for the next <div class="slide" after the match
next_slide_pattern = re.compile(r'<div class="slide"', re.IGNORECASE)
search_start = resident_match.end()

# Find all slide divs after this point
next_slide = next_slide_pattern.search(html, search_start)
if not next_slide:
    print("ERROR: Could not find the next slide after the residency slide.")
    sys.exit(1)

insert_position = next_slide.start()
print(f"  Found 'Resident or' slide. Inserting new slide at position {insert_position}.")

# --- Step 2: Build the new slide HTML ---
new_slide = '''
  <!-- Slide: Recording Your Residency Dates -->
  <div class="slide" data-slide="RENUMBER_ME">
    <div class="section-label">\u2014\u2014 RESIDENCY</div>
    <h1>Record every entry &amp; exit</h1>
    <p>Keep a spreadsheet logging every border crossing. This is your primary evidence for the 182-day test \u2014 and for linking periods across years.</p>

    <div style="overflow-x:auto; margin-top:3vh;">
      <table style="width:100%; border-collapse:collapse; font-family:'DM Sans',sans-serif; font-size:clamp(0.75rem,1.4vw,0.95rem);">
        <thead>
          <tr style="text-align:left; border-bottom:2px solid var(--border);">
            <th style="padding:0.6em 1em; color:var(--accent);">Date</th>
            <th style="padding:0.6em 1em; color:var(--accent);">Direction</th>
            <th style="padding:0.6em 1em; color:var(--accent);">From / To</th>
            <th style="padding:0.6em 1em; color:var(--accent);">Purpose</th>
            <th style="padding:0.6em 1em; color:var(--accent);">Days in MY</th>
          </tr>
        </thead>
        <tbody style="color:var(--text-dim);">
          <tr style="border-bottom:1px solid var(--border);">
            <td style="padding:0.5em 1em;">15 Jan 2024</td>
            <td style="padding:0.5em 1em;">Entry</td>
            <td style="padding:0.5em 1em;">Singapore \u2192 Malaysia</td>
            <td style="padding:0.5em 1em;">Return to KL base</td>
            <td style="padding:0.5em 1em;"></td>
          </tr>
          <tr style="border-bottom:1px solid var(--border);">
            <td style="padding:0.5em 1em;">28 Feb 2024</td>
            <td style="padding:0.5em 1em;">Exit</td>
            <td style="padding:0.5em 1em;">Malaysia \u2192 Thailand</td>
            <td style="padding:0.5em 1em;">Holiday</td>
            <td style="padding:0.5em 1em; color:var(--accent);">45</td>
          </tr>
          <tr style="border-bottom:1px solid var(--border);">
            <td style="padding:0.5em 1em;">5 Mar 2024</td>
            <td style="padding:0.5em 1em;">Entry</td>
            <td style="padding:0.5em 1em;">Thailand \u2192 Malaysia</td>
            <td style="padding:0.5em 1em;">Return to KL base</td>
            <td style="padding:0.5em 1em;"></td>
          </tr>
          <tr style="border-bottom:1px solid var(--border);">
            <td style="padding:0.5em 1em;">20 Jun 2024</td>
            <td style="padding:0.5em 1em;">Exit</td>
            <td style="padding:0.5em 1em;">Malaysia \u2192 Australia</td>
            <td style="padding:0.5em 1em;">Client meetings</td>
            <td style="padding:0.5em 1em; color:var(--accent);">107</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div style="margin-top:2.5vh; display:flex; gap:2vw; flex-wrap:wrap;">
      <div style="flex:1; min-width:200px; padding:1.2em; background:var(--accent-soft); border-radius:8px;">
        <div style="font-family:'DM Mono',monospace; font-size:0.75em; text-transform:uppercase; color:var(--accent); margin-bottom:0.5em;">Why the purpose matters</div>
        <p style="font-size:clamp(0.8rem,1.3vw,0.92rem); color:var(--text-dim); line-height:1.5;">The reason for travel can determine whether days abroad count toward linked residency periods under s.7(1)(b) and the 90-day test under s.7(1)(c). Record it while you remember it.</p>
      </div>
      <div style="flex:1; min-width:200px; padding:1.2em; background:var(--accent-soft); border-radius:8px;">
        <div style="font-family:'DM Mono',monospace; font-size:0.75em; text-transform:uppercase; color:var(--accent); margin-bottom:0.5em;">Tips</div>
        <p style="font-size:clamp(0.8rem,1.3vw,0.92rem); color:var(--text-dim); line-height:1.5;">Count days inclusive of arrival, exclusive of departure. Back it up with passport stamps or immigration app screenshots. Keep one sheet per calendar year.</p>
      </div>
    </div>
  </div>

'''

# --- Step 3: Insert the new slide ---
html = html[:insert_position] + new_slide + html[insert_position:]
print("  Inserted new slide.")

# --- Step 4: Renumber all data-slide attributes ---
# Find all data-slide="N" and renumber sequentially from 0
slides = list(re.finditer(r'data-slide="(\d+)"', html))
print(f"  Found {len(slides)} slides total. Renumbering...")

# Replace from last to first so positions don't shift
for i, match in reversed(list(enumerate(slides))):
    old = match.group(0)
    new = f'data-slide="{i}"'
    html = html[:match.start()] + new + html[match.end():]

total_slides = len(slides)
print(f"  Renumbered to 0-{total_slides - 1} ({total_slides} slides).")

# --- Step 5: Update slide counter display ---
# Look for patterns like "1 / 28" or "/ 28" in the slide count
old_total = total_slides - 1  # what it was before we added one
counter_pattern = re.compile(r'(\d+)\s*/\s*' + str(old_total))
counter_match = counter_pattern.search(html)
if counter_match:
    html = html[:counter_match.start()] + counter_match.group(1) + ' / ' + str(total_slides) + html[counter_match.end():]
    print(f"  Updated slide counter: {old_total} → {total_slides}")
else:
    # Try to find any "/ NUMBER" pattern near slideCount
    counter_pattern2 = re.compile(r'(slideCount[^<]*?)\d+(\s*</)', re.IGNORECASE)
    # Also try updating in JavaScript
    js_pattern = re.compile(r"(totalSlides|slides\.length|'/ '\s*\+\s*)\d+")
    # Brute force: replace "/ 28" with "/ 29" anywhere
    if f'/ {old_total}' in html:
        html = html.replace(f'/ {old_total}', f'/ {total_slides}', 1)
        print(f"  Updated slide counter: {old_total} → {total_slides}")
    else:
        print(f"  WARNING: Could not find slide counter to update. Check manually.")

# Also update any JS that sets total slides
# Common patterns: slides.length will auto-calculate, but hardcoded values need updating
js_total_pattern = re.compile(r'(\$\{slides\.length\}|totalSlides\s*=\s*)\d+')

# --- Step 6: Write the file ---
with open(FILE, "w", encoding="utf-8") as f:
    f.write(html)

print(f"\n{'='*55}")
print(f"Done! index.html now has {total_slides} slides.")
print(f"New slide inserted after 'Resident or non-resident?'")
print(f"")
print(f"NEXT STEPS:")
print(f"  1. Open index.html in your browser to check it looks right")
print(f"  2. In GitHub Desktop, commit the change")
print(f"  3. Push to origin")
print(f"  4. Your live site updates automatically in ~1 minute")
