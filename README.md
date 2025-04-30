# CaptainsLog

**FREE TO THE WORLD FROM CALLUM / DX COMMANDER**  
Lightweight Net Controller Logging Software
Download link: https://github.com/DXCommander/captainslog/releases/tag/V001

---

### 🖥️ Platform
- Runs anywhere on a Windows machine — even ancient laptops
- No dependencies — fully portable (can run from a USB stick)
- Written in Python — can run on Mac/Linux (remove Notepad export lines)

---

### 🎙️ Net Control Features
- Manual entry: just fill in `My Callsign`, `Current Freq`, and `Mode`
- Add QSOs using `Space` or `Tab` between fields
- Right-click a row to:
  - Edit, Delete, or Cancel
  - Mark a station as **LEFT** or **Rejoined**
- "Left" QSOs are shown in **light grey** for visual tracking

---

### 💾 Logging & Data Storage
- Logs stored as `current_log.json` in `/logs/` under your run directory
- It's just a readable text file in JSON format
- The log is **re-written in full** after every Add / Edit / Delete
- Optimized for up to ~10,000 QSOs per session

---

### 📤 ADIF Export
- Right-click any record → **Export to ADIF**
- Output is saved in the same `/logs/` directory
- You’ll be prompted to open it in Notepad (Windows only)

---

### 🧠 Notes
- There is no "Save" button — the log is always live
- If `current_log.json` exists, you will be prompted to load it on startup
- If you choose not to load it, the next logged QSO will overwrite it

---

### 🎉 Enjoy!
Made with care and curiosity by **Callum, M0MCX**  
_30th May 2024_
