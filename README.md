# CubePilot 🧊

CubePilot is a Python-based 3x3 Rubik's Cube solver project.

The goal of this project is to build a beginner-friendly Rubik's Cube solving application that can eventually capture cube faces using a camera, detect sticker colours, convert them into cube notation, and generate a valid solution using standard Rubik's Cube moves like `R`, `U`, `F2`, `L'`, etc.

This project is being built step-by-step to learn Python, computer vision, file handling, external libraries, and full-stack deployment.

---

## Current Features

- Accepts Rubik's Cube state face-by-face
- Validates cube input
- Checks whether the cube is already solved
- Uses the `kociemba` Python package to generate a solution
- Explains each move in simple human-readable language
- Saves solve history to a local JSON file

---

## Tech Stack

- Python
- Kociemba Rubik's Cube Solver
- JSON for local history storage
- VS Code
- Git/GitHub

Planned:

- OpenCV for camera capture
- Colour detection from cube stickers
- Web frontend
- Python backend API
- Deployment on Vercel, Render, or Fly.io

---

## Project Roadmap

### Stage 1: Manual Cube Solver ✅

The user manually enters the cube state in this order:

```text
U face, R face, F face, D face, L face, B face
```

Each face contains 9 stickers.

Example solved cube:

```text
UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB
```

---

### Stage 2: Move Explainer ✅

The solver output is converted into easy instructions.

Example:

```text
R  = Turn the right face clockwise
R' = Turn the right face anti-clockwise
R2 = Turn the right face twice
```

---

### Stage 3: Solve History ✅

Each solve attempt is saved in `history.json` with:

- Timestamp
- Cube string
- Solution
- Move count

---

### Stage 4: Terminal Menu 🔜

Add a simple terminal menu:

```text
1. Solve a cube
2. View solve history
3. Clear solve history
4. Exit
```

---

### Stage 5: Camera Capture 🔜

Use Python and OpenCV to open the Mac camera and capture one cube face at a time.

---

### Stage 6: Colour Detection 🔜

Detect the 9 sticker colours on each face and convert them into cube notation.

---

### Stage 7: Web App 🔜

Create a simple website where users can:

- Scan cube faces
- View detected colours
- Confirm or edit stickers
- Generate solution
- Follow step-by-step solving instructions

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Musalinux/cube-pilot.git
cd cube-pilot
```

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install kociemba
```

Run the app:

```bash
python main.py
```

---

## Example Input

```text
U face: UUUUUUUUU
R face: RRRRRRRRR
F face: FFFFFFFFF
D face: DDDDDDDDD
L face: LLLLLLLLL
B face: BBBBBBBBB
```

Expected output:

```text
Cube is already solved. No moves needed.
```

---

## Rubik's Cube Move Notation

| Move | Meaning |
|---|---|
| U | Turn upper face clockwise |
| U' | Turn upper face anti-clockwise |
| U2 | Turn upper face twice |
| D | Turn bottom face clockwise |
| D' | Turn bottom face anti-clockwise |
| D2 | Turn bottom face twice |
| R | Turn right face clockwise |
| R' | Turn right face anti-clockwise |
| R2 | Turn right face twice |
| L | Turn left face clockwise |
| L' | Turn left face anti-clockwise |
| L2 | Turn left face twice |
| F | Turn front face clockwise |
| F' | Turn front face anti-clockwise |
| F2 | Turn front face twice |
| B | Turn back face clockwise |
| B' | Turn back face anti-clockwise |
| B2 | Turn back face twice |

---

## Why I Am Building This

I am building CubePilot as a hands-on Python side project to learn real-world programming by solving an actual physical puzzle.

This project helps me practise:

- Python fundamentals
- Functions and validation
- External libraries
- File handling with JSON
- Error handling
- Git/GitHub workflow
- Computer vision basics
- Web app development
- Deployment

---

## Future Vision

The final version of CubePilot will allow users to scan all six faces of a scrambled Rubik's Cube using their laptop camera and instantly receive a step-by-step solution.

The long-term goal is to make it:

- Beginner-friendly
- Fully free to use
- Browser-based
- Python-powered
- Portfolio-ready

---

## Status

Currently in active development.

Completed:

- Manual cube input
- Solver integration
- Solved cube detection
- Move explanation
- JSON history storage

Next:

- Terminal menu
- Camera capture using OpenCV
