"""
REORDER SLIDES 7, 8, 9
=======================

Current order (wrong):
  Slide 7 (data-slide=6): "What are you taxed on"
  Slide 8 (data-slide=7): Linking/60-day or other
  Slide 9 (data-slide=8): Another

Desired order:
  Slide 7: When years link & temporary absences
  Slide 8: 60-day exemption
  Slide 9: What are you taxed on

Run this in your GitHub/malaysia-tax-guide folder:

    cd C:\\Users\\elect\\OneDrive\\Documents\\GitHub\\malaysia-tax-guide
    python reorder_slides.py

Edits index.html in place. Commit and push when happy.
"""

import re, os, sys

FILE = "index.html"

if not os.path.exists(FILE):
    print(f"ERROR: Can't find '{FILE}' in {os.getcwd()}")
    sys.exit(1)

with open(FILE, "r", encoding="utf-8") as f:
    html = f.read()

# --- Find all slide boundaries ---
# Each slide starts with <div class="slide" data-slide="N">
# and ends just before the next <div class="slide"

slide_starts = [(m.start(), m.group(1)) for m in re.finditer(r'<div class="slide"\s+data-slide="(\d+)"', html)]

if not slide_starts:
    print("ERROR: Could not find any slides.")
    sys.exit(1)

print(f"  Found {len(slide_starts)} slides total.")

def get_slide_content(html, slide_starts, data_slide_num):
    """Extract the full HTML of a slide by its data-slide number."""
    for i, (pos, num) in enumerate(slide_starts):
        if num == str(data_slide_num):
            start = pos
            if i + 1 < len(slide_starts):
                end = slide_starts[i + 1][0]
            else:
                # Last slide — find end differently
                end = html.find('<!-- Navigation', start)
                if end == -1:
                    end = html.find('<div class="progress-bar"', start)
                if end == -1:
                    end = len(html)
            return start, end, html[start:end]
    return None, None, None

# --- Extract slides 6, 7, 8 (which are display slides 7, 8, 9) ---
start6, end6, content6 = get_slide_content(html, slide_starts, 6)
start7, end7, content7 = get_slide_content(html, slide_starts, 7)
start8, end8, content8 = get_slide_content(html, slide_starts, 8)

if any(c is None for c in [content6, content7, content8]):
    print("ERROR: Could not find one or more of data-slide 6, 7, 8")
    print(f"  data-slide=6: {'found' if content6 else 'NOT FOUND'}")
    print(f"  data-slide=7: {'found' if content7 else 'NOT FOUND'}")
    print(f"  data-slide=8: {'found' if content8 else 'NOT FOUND'}")
    sys.exit(1)

# --- Identify which is which by looking for keywords ---
def identify_slide(content):
    content_lower = content.lower()
    if 'what are you taxed on' in content_lower or 'taxed on' in content_lower:
        return 'taxed_on'
    elif '60-day' in content_lower or '60 day' in content_lower or 'sixty day' in content_lower:
        return '60_day'
    elif 'link' in content_lower or 'temporary absence' in content_lower:
        return 'linking'
    else:
        return 'unknown'

id6 = identify_slide(content6)
id7 = identify_slide(content7)
id8 = identify_slide(content8)

print(f"  data-slide=6 (slide 7): {id6}")
print(f"  data-slide=7 (slide 8): {id7}")
print(f"  data-slide=8 (slide 9): {id8}")

# --- Desired order: linking=6, 60_day=7, taxed_on=8 ---
slides_by_id = {}
for ds_num, content, ident in [(6, content6, id6), (7, content7, id7), (8, content8, id8)]:
    slides_by_id[ident] = content

desired_order = ['linking', '60_day', 'taxed_on']
missing = [d for d in desired_order if d not in slides_by_id]

if missing:
    print(f"\n  WARNING: Could not identify these slide types: {missing}")
    print(f"  Identified slides: {list(slides_by_id.keys())}")
    print(f"\n  Let me show you what's on each slide so you can check:")
    for ds_num, content, ident in [(6, content6, id6), (7, content7, id7), (8, content8, id8)]:
        # Extract the heading
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL)
        heading = h1_match.group(1) if h1_match else '(no h1 found)'
        heading = re.sub(r'<[^>]+>', '', heading).strip()
        print(f"    data-slide={ds_num}: \"{heading}\" → identified as: {ident}")
    print(f"\n  Proceeding with best-effort reorder based on what was found...")
    
    # Fall back: just use whatever we have in the order we find them
    # Put any identified ones in the right spot, leave unknowns where they are
    available = {}
    all_contents = [(6, content6, id6), (7, content7, id7), (8, content8, id8)]
    
    reordered = [None, None, None]
    used = set()
    
    for target_idx, target_id in enumerate(desired_order):
        for ds_num, content, ident in all_contents:
            if ident == target_id and ds_num not in used:
                reordered[target_idx] = content
                used.add(ds_num)
                break
    
    # Fill remaining slots with unmatched slides
    for ds_num, content, ident in all_contents:
        if ds_num not in used:
            for i in range(3):
                if reordered[i] is None:
                    reordered[i] = content
                    used.add(ds_num)
                    break
    
    new_slide6, new_slide7, new_slide8 = reordered
else:
    new_slide6 = slides_by_id['linking']
    new_slide7 = slides_by_id['60_day']
    new_slide8 = slides_by_id['taxed_on']
    print(f"\n  All three slides identified. Reordering...")

# --- Update data-slide numbers in the content ---
def set_data_slide(content, new_num):
    return re.sub(r'data-slide="\d+"', f'data-slide="{new_num}"', content, count=1)

new_slide6 = set_data_slide(new_slide6, 6)
new_slide7 = set_data_slide(new_slide7, 7)
new_slide8 = set_data_slide(new_slide8, 8)

# --- Replace in HTML ---
# Replace the entire block from start of slide 6 to end of slide 8
block_start = start6
block_end = end8

new_block = new_slide6 + new_slide7 + new_slide8

html = html[:block_start] + new_block + html[block_end:]

# --- Write ---
with open(FILE, "w", encoding="utf-8") as f:
    f.write(html)

print(f"\n{'='*55}")
print(f"Done! Slides reordered:")
print(f"  Slide 7: When years link & temporary absences")
print(f"  Slide 8: 60-day exemption")
print(f"  Slide 9: What are you taxed on")
print(f"")
print(f"NEXT STEPS:")
print(f"  1. Open index.html in your browser to check")
print(f"  2. Commit and push in GitHub Desktop")
