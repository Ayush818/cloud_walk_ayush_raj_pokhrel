# 🎮 Quake Log Parser

This project parses Quake 3 Arena log files and extracts useful statistics about players and matches.

## ✅ What It Does

### Part I - The Application

**Where:**  
Implemented in `main()` inside `main.py` 

**How:**  
- Parses `log.txt` to identify when a new game starts (`InitGame`) and track player kills (`Kill:`).
- Collects:
  - List of unique players per match (excluding `<world>`).
  - Kill counts per player, adjusting scores when `<world>` is the killer.
  - Total kills per game.
- Organizes parsed data by match (e.g., `game_1`, `game_2`, etc.).

---

### Part II - Tests and Quality Improvements

**Where:**  
Triggered within `main()` in `test.py` after parsing logic (though actual test file not shown here).

**How:**  
- Designed to test core parsing logic like player extraction and kill calculations.
- Accounts for edge cases such as:
  - `<world>` kills
  - Duplicate player names across games
  - Players with zero or negative kills

---

### 🏁 To Run

Make sure you have:
- `main.py`
- `test.py`
- `log.txt`

Then run:
```bash
python main.py for part 1
python test.py for part 2
