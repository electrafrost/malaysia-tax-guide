"""
GENERATE PRESENTER VERSION WITH SPEAKER NOTES
===============================================

This creates presenter.html from your index.html.
presenter.html has speaker notes toggled with the P key.

DO NOT push presenter.html to GitHub — it's for local use only.

Run in your malaysia-tax-guide folder:
    cd C:\\Users\\elect\\OneDrive\\Documents\\GitHub\\malaysia-tax-guide
    python make_presenter.py
"""

import re, os, sys

FILE = "index.html"
OUTPUT = "presenter.html"

if not os.path.exists(FILE):
    print(f"ERROR: Can't find '{FILE}' in {os.getcwd()}")
    sys.exit(1)

with open(FILE, "r", encoding="utf-8") as f:
    html = f.read()

# ============================================================
# SPEAKER NOTES — keyed by slide number (0-indexed data-slide)
# Roughly 20-25 seconds of talking per slide = 10 min total
# ============================================================

notes = {
    0: """Welcome. I'm Electra Frost, I'm a chartered tax adviser and accountant with over 20 years in Australian public practice. I'm here at Network School on a DE Rantau visa, same as many of you. This is a short guide to help you understand your Malaysian individual tax position — specifically for people earning income from foreign entities. Let's get into it.""",

    1: """Quick disclaimer. This is general information, not advice specific to your situation. Your obligations depend on your own facts — how many days you're here, where you physically do your work, and how your income is structured. Confirm your position with a qualified tax adviser before you file or decide not to file.""",

    2: """So who is this for? You're a foreigner living in or spending time in Malaysia. Your income comes from outside — a foreign employer, your own foreign company, freelance work for overseas clients. You have no Malaysian employer, no Malaysian clients, no Malaysian business. You might be on a DE Rantau visa, a tourist visa, or something else. If that's you, keep listening.""",

    3: """The first thing to establish is whether you're a tax resident or a non-resident. This is not about your visa or your citizenship — it's about physical presence. The main test: if you're in Malaysia for 182 days or more in a calendar year, you're resident for that year. There are other tests — linked periods and a 90-day historical test — which I'll explain next. If you don't pass any test, you're non-resident for that year. For those of you who arrived in 2024, you may well be non-resident for YA 2024.""",

    4: """Keep a spreadsheet — seriously. Log every single entry and exit with the date, direction, which country, and why you travelled. This is your primary evidence for the 182-day test. The purpose column matters because it affects whether days abroad can count toward linked residency periods. Do this while you remember it — don't try to reconstruct it at tax time. Back it up with passport stamps or screenshots from your immigration app.""",

    5: """Here's how the count actually works. It's a calendar year — January 1 to December 31 — not a rolling 12 months. Day of arrival counts, day of departure doesn't. Days don't need to be consecutive. If you're based here at NS and you're not away for months at a time, you'll almost certainly hit 182 days without needing to think about it. But if your year is tight — long European summer, conference circuit in Q4 — then you need the next slide.""",

    6: """Two fallback tests if you're short of 182 days. First, linked periods under section 7(1)(b). If you have a block of presence in Malaysia that connects to another block in the same or adjacent year, temporary absences between those blocks can count as days in Malaysia. The absences need to be connected to your Malaysian life — a conference trip, a holiday, visiting family. The law doesn't define connected precisely, which is why your purpose-of-travel notes matter.

Second, the 90-day historical test under section 7(1)(c). If you were present for at least 90 days this year AND you were resident or present for 90-plus days in three of the four preceding years, this year counts as resident. Your history supports the current year — not the other way around. This is why you keep records going back at least five years.""",

    7: """What are you actually taxed on? If you're resident — Malaysian-sourced income, plus foreign-sourced income received in Malaysia, subject to exemptions through 2036. Progressive rates, zero to 30 percent, with reliefs and rebates available. If you're non-resident — Malaysian-sourced income only. Flat 30 percent. No reliefs, no rebates. The key question becomes: is your income Malaysian-sourced?""",

    8: """Source rules. Malaysia taxes income where the work is physically performed. Not where you're paid. Not where your company is registered. If you're sitting here at NS doing your work, that work is performed in Malaysia and the income is Malaysian-sourced. I know that's uncomfortable. The common misconception is that because your salary lands in a foreign bank account from a foreign company, it's not taxable here. Wrong. Source follows the work, not the money.""",

    9: """The 60-day exemption. If you're a non-resident and you're in Malaysia for 60 days or fewer in the calendar year, your employment income is exempt. But — and this is important — it's employment income only. Freelancers, contractors, and directors' fees are excluded. And once you cross 60 days, even across multiple visits, it's gone. For most of you spending meaningful time here, this won't apply. The question then becomes whether a Double Tax Agreement can help.""",

    10: """DTA relief, Article 15. If you're non-resident and tax resident in your home country, a DTA may override Malaysia's right to tax your employment income. But it's not automatic — you have to claim it, and all three tests must be met: present 183 days or fewer, paid by a foreign employer, and salary not borne by a Malaysian entity. Fail any one and Malaysia taxes at 30 percent. And critically — Article 15 does not apply to freelancers or contractors. This is an employment-only provision.""",

    11: """For residents, two mechanisms prevent double taxation. The FSI exemption — foreign-sourced income received in Malaysia is temporarily exempt through 2036 if it was taxed at source. This covers dividends, interest, royalties, investment returns. But it does not cover income from services you performed in Malaysia — that's Malaysian-sourced regardless. Second, bilateral tax relief under Schedule 7 — if Malaysia taxes income that was also taxed abroad, you claim a credit. Must be a resident, and claim within two years.""",

    12: """The nil filing question. Section 77 requires every person chargeable to tax to furnish a return. No chargeable income means no strict obligation. But there's a strategic reason to file anyway, which I'll explain next.""",

    13: """Here's the case for voluntary filing. It comes down to limitation periods. When you file a return, section 90(1) creates a deemed assessment. Section 91 then gives LHDN five years from the end of the year of assessment to raise additional assessments. After that, you're clear. If you don't file, there's no deemed assessment, no clock running, and the Director General can assess you by best judgment at any time under section 90(3) with no time limit. Filing starts the clock.""",

    14: """Filed versus unfiled — the comparison is stark. A nil return creates a deemed assessment, starts the five-year clock, and documents your position at the time you formed it. No return means no clock, open-ended exposure, and you have to argue your position after the fact. Have you checked the Hasil portal to see if LHDN expects returns from you? Can you explain and defend your position if asked?""",

    15: """The common objection — doesn't filing put me in the tax net? No. A return completed with zeros says: I was present in Malaysia, I assessed my position, and I concluded I have no Malaysian-source income and no tax liability. That is a statement of facts and legal analysis, not an admission of jurisdiction.""",

    16: """If you hold a visa tied to income thresholds — like DE Rantau — LHDN already knows you earn money. Immigration and tax authorities share data. A person known to be an income-earning foreign national who has never filed is in a weaker position than someone who has filed a nil return. A clean filing history removes a line of enquiry before it starts.""",

    17: """My personal take. If there's a lot of low-hanging fruit around me and they come to harvest, I'm making sure I don't get picked. File. State your position. Start the clock. Be the green fruit up high.""",

    18: """Your nil filing position — the summary table. Whether you're resident or non-resident, if your chargeable income is genuinely nil, filing protects that position. The limitation clock starts when you lodge. Recommended strategy for both: file voluntarily.""",

    19: """Practical next steps. YA 2024 is overdue — file now. YA 2025 is due 30 April 2026 with a 15-day extension for e-filing. Set up a login at mytax.hasil.gov.my using your passport number. Check your portal — if you applied for DE Rantau you'll have a tax ID number and you can see what LHDN expects. Use a licensed Malaysian tax agent if you can — they carry professional indemnity insurance. And for late nil returns, the penalty is 10 percent of tax payable — on a nil return, that's zero.""",

    20: """If you get it wrong, you can amend. Section 77B allows one self-amendment within six months of the original filing due date. Outside that window, you can still make a voluntary disclosure by letter. Get it right the first time if you can, but the system does allow correction.""",

    21: """This is the MyTax portal. I'll click through a few screenshots so you can see what the interface looks like.""",
    22: """Here's the next screen...""",
    23: """And the form layout...""",
    24: """Filing details...""",
    25: """And submission.""",

    26: """A note about me. I am not a licensed Malaysian tax agent — I cannot give you advice or file your return. I have 20-plus years in Australian public practice, sold my practices, and now work at the institutional level building systems. If you want more help with this, ask Network School to give me a space and support to build it properly.""",

    27: """Thank you. My sessions and office hours are on lu.ma/electrafrost. I'm doing this pro bono because I want Network School to retain its long-termers and be a success. This is general information only — confirm with the legislation, the public rulings, or a licensed tax agent.""",
}

# ============================================================
# BUILD PRESENTER HTML
# ============================================================

# 1. Add presenter CSS
presenter_css = """
  /* Presenter notes */
  .presenter-notes {
    display: none;
    position: fixed;
    bottom: 48px;
    left: 0;
    right: 0;
    max-height: 30vh;
    overflow-y: auto;
    background: rgba(21, 34, 56, 0.95);
    color: #e8e6e1;
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    line-height: 1.6;
    padding: 1.2rem 3vw;
    z-index: 200;
    border-top: 2px solid #4a7d94;
  }
  .presenter-notes.visible {
    display: block;
  }
  .presenter-notes .note-timer {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: #4a7d94;
    margin-bottom: 0.5rem;
    letter-spacing: 0.08em;
  }
  .presenter-notes .note-text {
    max-width: 70ch;
  }
  .presenter-hint {
    position: fixed;
    top: 12px;
    right: 12px;
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: var(--text-dim);
    opacity: 0.4;
    z-index: 300;
    letter-spacing: 0.06em;
  }
"""

# Insert CSS before </style>
html_out = html.replace('</style>', presenter_css + '\n</style>')

# 2. Add the notes panel div before </body>
notes_div = """
<div class="presenter-notes" id="presenterNotes">
  <div class="note-timer" id="noteTimer">SLIDE 1 — 0:00</div>
  <div class="note-text" id="noteText"></div>
</div>
<div class="presenter-hint" id="presenterHint">Press P for notes</div>
"""

html_out = html_out.replace('</body>', notes_div + '\n</body>')

# 3. Build the notes JS object
notes_js_entries = []
for slide_num in sorted(notes.keys()):
    text = notes[slide_num].replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
    notes_js_entries.append(f'  {slide_num}: `{text}`')

notes_js_obj = ',\n'.join(notes_js_entries)

# 4. Add presenter JS before </script>
presenter_js = """
  // Presenter notes
  const presenterNotes = {
""" + notes_js_obj + """
  };

  const notesPanel = document.getElementById('presenterNotes');
  const noteTimer = document.getElementById('noteTimer');
  const noteText = document.getElementById('noteText');
  const presenterHint = document.getElementById('presenterHint');
  let notesVisible = false;
  let presenterStartTime = null;

  function updateNotes() {
    const note = presenterNotes[current] || '(no notes for this slide)';
    noteText.textContent = note;
    
    let elapsed = '';
    if (presenterStartTime) {
      const secs = Math.floor((Date.now() - presenterStartTime) / 1000);
      const mins = Math.floor(secs / 60);
      const remainSecs = secs % 60;
      elapsed = mins + ':' + String(remainSecs).padStart(2, '0');
    } else {
      elapsed = '0:00';
    }
    noteTimer.textContent = 'SLIDE ' + (current + 1) + ' of ' + total + ' — ' + elapsed;
  }

  // Patch the existing goTo function to also update notes
  const originalGoTo = goTo;
  goTo = function(n) {
    originalGoTo(n);
    if (notesVisible) updateNotes();
  };

  document.addEventListener('keydown', function(e) {
    if (e.key === 'p' || e.key === 'P') {
      notesVisible = !notesVisible;
      notesPanel.classList.toggle('visible', notesVisible);
      presenterHint.style.display = notesVisible ? 'none' : 'block';
      if (notesVisible) {
        if (!presenterStartTime) presenterStartTime = Date.now();
        updateNotes();
      }
    }
  });

  // Update timer every second when notes are visible
  setInterval(function() {
    if (notesVisible) updateNotes();
  }, 1000);
"""

html_out = html_out.replace('</script>', presenter_js + '\n</script>')

# ============================================================
# WRITE
# ============================================================

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(html_out)

print(f"Created: {OUTPUT}")
print(f"Speaker notes for {len(notes)} slides")
print(f"")
print(f"HOW TO USE:")
print(f"  1. Open presenter.html in your browser")
print(f"  2. Press P to toggle speaker notes")
print(f"  3. A timer starts when you first press P")
print(f"  4. Notes update as you advance slides")
print(f"  5. Start Loom, share your browser tab, and present")
print(f"")
print(f"DO NOT push presenter.html to GitHub.")
print(f"Add it to .gitignore or just don't commit it.")
print(f"")
print(f"To keep it out of GitHub Desktop, create a .gitignore file with:")
print(f"  presenter.html")
print(f"  *.py")
