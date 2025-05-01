# CaptainsLog

**FREE TO THE WORLD FROM CALLUM / DX COMMANDER**  
Lightweight Net Controller Logging Software  
For General Logging or Net Controllers
Download link at the bottom of this page  
https://github.com/DXCommander/captainslog/releases/tag/V001

---

### 🖥️ Platform
- Runs anywhere on a Windows machine — even ancient laptops
- No dependencies — fully portable (can run from a USB stick)
- Written in Python — can run on Mac/Linux (just remove the Notepad-specific lines)

---

### 🎙️ Net Control Features
- Fast manual logging: just fill in `My Callsign`, `Frequency`, and `Mode`
- Add QSOs using `Space`, `Tab`, or `Return` between fields
- **Right-click** on any logged row to:
  - Edit the entry
  - Delete it
  - Mark a station as **LEFT** (they’ve left the net)
  - Mark a station as **REJOINED** (they’ve come back)

> *LEFT entries are automatically styled in light grey for clarity.*

---

### 🔥 NEW in V0.604+
#### Operator-focused improvements:
- **Alt+W** clears a half-completed QSO instantly (acts as a “No Copy” bail-out)
- Edit window now includes **Frequency** and **Mode** fields
- Row selection styling improved for readability (blue highlight + black text)
- Context menu simplified: `LEFT` and `REJOINED` for quick, clear logging

---

### 💾 Logging & Data Storage
- All logs are saved as `current_log.json` in a `/logs/` subfolder
- Stored in plain JSON format — fully human-readable and recoverable
- The entire file is rewritten after every Add / Edit / Delete
- **Supports large logs** — tested with 10,000+ QSOs

> LEFT and REJOINED status is stored safely in each QSO's `tags` array

---

### 📤 ADIF Export
- Right-click → **Export to ADIF**
- Output saved alongside your log in the `/logs/` folder
- Optional: opens automatically in Notepad (Windows only)

---

### 🧪 Testing the Logger?
Just start it up and bash in some callsigns — that’s how real ops roll.  
You’ll get a feel for the flow in no time.  
Need fake callers? Log a few off the top of your head — M0ZZZ, W1WOW, JA1COOL...

---

### 🔭 Coming Soon (V0.605+)
- **Start Net** / **End Net** session controls
- **Hide LEFT** / **Show LEFT** filters to manage visibility
- Top-level **menu bar** with File / Net / Settings / Help
- Future options for pop-out windows showing active stations only

---

### 🧠 Notes
- There is no "Save" button — the log is always live
- If `current_log.json` exists at startup, you’ll be prompted to load it
- If declined, your next QSO will start a fresh log and overwrite the file

---

### 🎉 Enjoy!
Made with care, curiosity, and collaboration  
By **Callum, M0MCX** and **ChatGPT (OpenAI)**  
_1st May 2025_
