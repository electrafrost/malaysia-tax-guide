"""
FIX PRESENTATION — COMPREHENSIVE CLEANUP
==========================================

This script fixes all current issues in one pass:
1. Removes the duplicate "Record every entry & exit" slide (the RENUMBER_ME one)
2. Inserts "How the 182-day count works" after the first "Record every entry & exit"  
3. Inserts "When years link & temporary absences" after that
4. Reorders so the flow is:
     Slide 4: Residency test overview
     Slide 5: Record every entry & exit (the good 2026/NS version)
     Slide 6: How the 182-day count works (NEW)
     Slide 7: When years link & temporary absences (NEW)
     Slide 8: What are you taxed on
     Slide 9: Where is your income sourced
     Slide 10: 60-day exemption
     Slide 11: DTA Article 15
     Slide 12: FSI + bilateral
     ...rest unchanged
5. Renumbers all data-slide attributes sequentially
6. Updates slide counter

Run in your malaysia-tax-guide folder:
    cd C:\\Users\\elect\\OneDrive\\Documents\\GitHub\\malaysia-tax-guide
    python fix_all_slides.py
"""

import re, os, sys

FILE = "index.html"

if not os.path.exists(FILE):
    print(f"ERROR: Can't find '{FILE}' in {os.getcwd()}")
    sys.exit(1)

with open(FILE, "r", encoding="utf-8") as f:
    html = f.read()

# ============================================================
# STEP 1: Parse all slides into a list
# ============================================================

# Find every slide's start position
slide_pattern = re.compile(r'<div class="slide[^"]*"\s+data-slide="[^"]*"', re.IGNORECASE)
starts = [m.start() for m in slide_pattern.finditer(html)]

if not starts:
    print("ERROR: No slides found")
    sys.exit(1)

# Find where slides end (the content after the last slide)
# Look for the bottom-bar div
bottom_bar_pos = html.find('<div class="bottom-bar">')
if bottom_bar_pos == -1:
    bottom_bar_pos = html.find('<script>')

# Extract each slide as a string
slides = []
for i, start in enumerate(starts):
    if i + 1 < len(starts):
        end = starts[i + 1]
    else:
        # Last slide - find the closing </div> before bottom-bar
        # We need to find the closing </div>\n\n</div> that ends the deck
        end = bottom_bar_pos
        # Walk backwards to find the end of the last slide content
        # The deck closing </div> is right before bottom-bar
        deck_close = html.rfind('</div>', 0, bottom_bar_pos)
        if deck_close > starts[-1]:
            end = deck_close
    
    slide_html = html[start:end]
    slides.append(slide_html)

print(f"  Found {len(slides)} slides")

# ============================================================
# STEP 2: Identify each slide by content
# ============================================================

def identify(s):
    sl = s.lower()
    if 'renumber_me' in sl:
        return 'DUPLICATE_DELETE'
    elif 'filing tax in' in sl and 'title-slide' in sl:
        return '01_title'
    elif 'general advice' in sl and 'disclaimer' in sl:
        return '02_disclaimer'
    elif 'who is this' in sl:
        return '03_who'
    elif 'resident or' in sl and 'non-resident' in sl and '182 days' in sl:
        return '04_residency_test'
    elif 'record every entry' in sl:
        return '05_record_entries'
    elif 'what are you' in sl and 'taxed on' in sl:
        return '08_taxed_on'
    elif 'where is your income' in sl and 'sourced' in sl:
        return '09_source_rules'
    elif 'dta relief' in sl or ('article 15' in sl and 'non-resident' in sl.split('article 15')[0][-200:]):
        return '11_dta_article15'
    elif '60-day' in sl or '60 day' in sl:
        return '10_60day'
    elif 'fsi exemption' in sl or 'bilateral tax relief' in sl:
        return '12_fsi_bilateral'
    elif "non-resident scenarios" in sl or ("what's taxable" in sl and "non-resident" in sl):
        return '13_nonres_scenarios'
    elif "resident scenarios" in sl or ("what's taxable" in sl and "resident" in sl and "non-resident" not in sl):
        return '14_res_scenarios'
    elif 'nil filing question' in sl or 'do you file' in sl:
        return '15_nil_question'
    elif 'risk-management' in sl or 'filing anyway' in sl:
        return '16_why_file'
    elif 'filed vs unfiled' in sl or 'what changes when you' in sl:
        return '17_filed_vs_unfiled'
    elif "doesn't filing put me" in sl or 'in the tax net' in sl:
        return '18_objection'
    elif 'visa holders' in sl and 'visibility' in sl:
        return '19_visa_visibility'
    elif 'low-hanging fruit' in sl or 'low hanging fruit' in sl:
        return '20_fruit'
    elif 'record-keeping' in sl or 'seven years' in sl:
        return '21_recordkeeping'
    elif 'nil filing strategy' in sl or 'malaysian tax outcome' in sl:
        return '22_summary'
    elif 'when and' in sl and 'how to file' in sl:
        return '23_how_to_file'
    elif 'you can' in sl and 'amend' in sl:
        return '24_amendments'
    elif 'mytax' in sl or ('slide-22' in sl and 'max-height:85vh' in sl):
        return '25_mytax'
    elif 'slide-23' in sl and 'max-height:85vh' in sl:
        return '26_mytax'
    elif 'slide-24' in sl and 'max-height:85vh' in sl:
        return '27_mytax'
    elif 'slide-25' in sl and 'max-height:85vh' in sl:
        return '28_mytax'
    elif 'slide-26' in sl and 'max-height:85vh' in sl:
        return '29_mytax'
    elif 'note from me' in sl or 'what i do' in sl:
        return '30_about_me'
    elif 'end-slide' in sl or 'lu.ma/electrafrost' in sl:
        return '31_end'
    else:
        return 'UNKNOWN'

for i, s in enumerate(slides):
    ident = identify(s)
    # Extract heading for display
    h_match = re.search(r'<h[12][^>]*>(.*?)</h[12]>', s, re.DOTALL)
    heading = re.sub(r'<[^>]+>', '', h_match.group(1)).strip() if h_match else '(image-only slide)'
    print(f"    Slide {i+1}: {ident} — \"{heading[:60]}\"")

# ============================================================
# STEP 3: Remove duplicates and create new slides
# ============================================================

# Filter out the RENUMBER_ME duplicate
clean_slides = [s for s in slides if identify(s) != 'DUPLICATE_DELETE']
removed = len(slides) - len(clean_slides)
print(f"\n  Removed {removed} duplicate slide(s)")

# Create the two new slides
new_slide_182day = '''<div class="slide" data-slide="X">
    <div class="section-label">Residency</div>
    <h2>How the <em>182-day count</em> works</h2>
    <p class="lead">The primary test is simple: are you physically present in Malaysia for <strong>182 days or more</strong> in a calendar year?</p>
    <div class="yr-row">
      <div class="yr-card">
        <div class="yr">Calendar year</div>
        <p>The count runs 1 January to 31 December \u2014 not a rolling 12 months. Each year of assessment stands alone.</p>
      </div>
      <div class="yr-card">
        <div class="yr">How to count</div>
        <p>Day of arrival in Malaysia counts. Day of departure does not. Days do not need to be consecutive \u2014 every day physically present adds to your total.</p>
      </div>
      <div class="yr-card">
        <div class="yr">If you\u2019re based at NS</div>
        <p>If Malaysia is your home base and you\u2019re not away for extended periods, you will almost certainly pass the 182-day test without needing the other provisions.</p>
      </div>
    </div>
    <p style="margin-top:1.5rem; color:var(--text-dim);">But if your year is tight \u2014 maybe you spent two months in Europe over summer and did a long conference circuit in Q4 \u2014 then you may need the linking provisions on the next slide.</p>
  </div>

'''

new_slide_linking = '''<div class="slide" data-slide="X">
    <div class="section-label">Residency</div>
    <h2>When years link &amp; <em>temporary absences</em></h2>
    <p class="lead">If you fall short of 182 days, two other tests can still make you <strong>resident</strong>. Both reward consistent presence and good records.</p>
    <div class="two-col">
      <div class="col-card blue">
        <h3>Linked periods \u2014 s.7(1)(b)</h3>
        <p>If you have a block of presence in Malaysia that connects to another block in the <strong>same or an adjacent year</strong>, temporary absences between them can be treated as days in Malaysia.</p>
        <p style="margin-top:0.6rem;">The absences must be <em>connected</em> to your Malaysian life. A conference in Singapore, a holiday in Thailand, visiting family abroad \u2014 these typically qualify. The legislation doesn\u2019t define \u201cconnected\u201d precisely, which is why recording your <strong>purpose of travel</strong> matters.</p>
      </div>
      <div class="col-card blue">
        <h3>The 90-day historical test \u2014 s.7(1)(c)</h3>
        <p>This is the safety net. If you were present for <strong>at least 90 days</strong> this year, AND you were resident or present for 90+ days in <strong>three of the four preceding years</strong>, this year counts as resident.</p>
        <p style="margin-top:0.6rem;">Your history supports the current year \u2014 not the other way around. This is why keeping records going back <strong>at least five years</strong> matters.</p>
      </div>
    </div>
    <div class="emphasis" style="margin-top:1.2rem;">
      <p>You have a long-term home base in Malaysia but move around for work and conferences. Short trips abroad don\u2019t break your residency \u2014 but your records need to show that Malaysia is where you return to and that your absences are temporary.</p>
    </div>
  </div>

'''

# ============================================================
# STEP 4: Build the correct order
# ============================================================

# Map slides by identity
slide_map = {}
mytax_slides = []
for s in clean_slides:
    ident = identify(s)
    if 'mytax' in ident:
        mytax_slides.append(s)
    elif ident in slide_map:
        print(f"  WARNING: duplicate identity '{ident}' — keeping first instance")
    else:
        slide_map[ident] = s

# Define the correct order
correct_order = [
    '01_title',
    '02_disclaimer',
    '03_who',
    '04_residency_test',
    '05_record_entries',
    'NEW_182day',           # new
    'NEW_linking',          # new
    '08_taxed_on',
    '09_source_rules',
    '10_60day',
    '11_dta_article15',
    '12_fsi_bilateral',
    '13_nonres_scenarios',
    '14_res_scenarios',
    '15_nil_question',
    '16_why_file',
    '17_filed_vs_unfiled',
    '18_objection',
    '19_visa_visibility',
    '20_fruit',
    '21_recordkeeping',
    '22_summary',
    '23_how_to_file',
    '24_amendments',
    'MYTAX_BLOCK',          # placeholder for all mytax slides
    '30_about_me',
    '31_end',
]

# Assemble
ordered_slides = []
for key in correct_order:
    if key == 'NEW_182day':
        ordered_slides.append(new_slide_182day)
    elif key == 'NEW_linking':
        ordered_slides.append(new_slide_linking)
    elif key == 'MYTAX_BLOCK':
        ordered_slides.extend(mytax_slides)
    elif key in slide_map:
        ordered_slides.append(slide_map[key])
    else:
        print(f"  WARNING: '{key}' not found in slides — skipping")

print(f"\n  Assembled {len(ordered_slides)} slides in correct order")

# ============================================================
# STEP 5: Renumber all data-slide attributes
# ============================================================

for i, slide_html in enumerate(ordered_slides):
    # Replace data-slide="anything" with the correct number
    ordered_slides[i] = re.sub(r'data-slide="[^"]*"', f'data-slide="{i}"', slide_html, count=1)

# ============================================================
# STEP 6: Rebuild the HTML
# ============================================================

# Get everything before the first slide
first_slide_pos = starts[0]
header = html[:first_slide_pos]

# Get everything after the last slide (bottom bar, script, etc)
# Find the closing </div> of the deck, then the bottom-bar
deck_end = html.find('</div>', starts[-1] + len(slides[-1]))
# Actually, let's find the bottom-bar and take everything from there
footer_start = html.find('<div class="bottom-bar">')
if footer_start == -1:
    footer_start = html.find('<script>')

# We need the closing </div> of the deck div right before bottom-bar
# Find the last </div> before footer
deck_close_region = html[starts[-1]:footer_start]
# Count how the deck div closes
footer = '\n</div>\n\n' + html[footer_start:]

# Update slide counter in footer
total = len(ordered_slides)
footer = re.sub(r'(\d+)\s*/\s*\d+', f'1 / {total}', footer, count=1)

# Assemble
new_html = header + '\n'.join(ordered_slides) + footer

# ============================================================
# STEP 7: Write
# ============================================================

with open(FILE, "w", encoding="utf-8") as f:
    f.write(new_html)

print(f"\n{'='*60}")
print(f"Done! {total} slides, clean and in order.")
print(f"")
print(f"Slide order:")
for i, s in enumerate(ordered_slides):
    h_match = re.search(r'<h[12][^>]*>(.*?)</h[12]>', s, re.DOTALL)
    heading = re.sub(r'<[^>]+>', '', h_match.group(1)).strip() if h_match else '(image-only)'
    print(f"  {i+1:2d}. {heading[:65]}")
print(f"")
print(f"NEXT STEPS:")
print(f"  1. Open index.html in your browser — check every slide")
print(f"  2. Commit in GitHub Desktop")
print(f"  3. Push to origin")
