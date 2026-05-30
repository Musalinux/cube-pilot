import json
from datetime import datetime
from pathlib import Path

import kociemba


VALID_FACELET_LETTERS = {"U", "R", "F", "D", "L", "B"}
FACE_ORDER = ["U", "R", "F", "D", "L", "B"]
SOLVED_CUBE = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
HISTORY_FILE = Path("history.json")


MOVE_MEANINGS = {
    "U": "Turn the upper face clockwise",
    "D": "Turn the down/bottom face clockwise",
    "R": "Turn the right face clockwise",
    "L": "Turn the left face clockwise",
    "F": "Turn the front face clockwise",
    "B": "Turn the back face clockwise",
}


def validate_cube_string(cube_string):
    cube_string = cube_string.strip().upper()

    if len(cube_string) != 54:
        return False, f"Cube string must be 54 characters long. Yours has {len(cube_string)}."

    for letter in cube_string:
        if letter not in VALID_FACELET_LETTERS:
            return False, f"Invalid letter found: {letter}. Use only U, R, F, D, L, B."

    for letter in FACE_ORDER:
        count = cube_string.count(letter)

        if count != 9:
            return False, f"{letter} appears {count} times. It must appear exactly 9 times."

    return True, "Cube string looks valid."


def solve_cube(cube_string):
    cube_string = cube_string.strip().upper()

    is_valid, message = validate_cube_string(cube_string)

    if not is_valid:
        return message

    if cube_string == SOLVED_CUBE:
        return "Cube is already solved. No moves needed."

    try:
        solution = kociemba.solve(cube_string)

        if solution == "":
            return "Cube is already solved. No moves needed."

        return solution

    except Exception as error:
        return f"Solver error: {error}"


def print_cube_faces(cube_string):
    print()
    print("Cube faces entered:")

    start = 0

    for face in FACE_ORDER:
        face_data = cube_string[start:start + 9]

        print()
        print(f"{face} face:")
        print(face_data[0:3])
        print(face_data[3:6])
        print(face_data[6:9])

        start += 9


def get_cube_input_face_by_face():
    print()
    print("Enter each face as 9 letters.")
    print("Example for solved U face: UUUUUUUUU")
    print()
    print("Face order:")
    print("U face, then R face, then F face, then D face, then L face, then B face")
    print()

    cube_string = ""

    for face in FACE_ORDER:
        while True:
            face_input = input(f"Enter {face} face: ").strip().upper()

            if len(face_input) != 9:
                print(f"Wrong length. {face} face must have exactly 9 letters.")
                continue

            invalid_letters = [letter for letter in face_input if letter not in VALID_FACELET_LETTERS]

            if invalid_letters:
                print("Invalid letters found. Use only U, R, F, D, L, B.")
                continue

            cube_string += face_input
            break

    return cube_string


def explain_single_move(move):
    face = move[0]
    meaning = MOVE_MEANINGS.get(face, "Unknown move")

    if len(move) == 1:
        return f"{move}: {meaning}"

    if move[1] == "'":
        return f"{move}: {meaning.replace('clockwise', 'anti-clockwise')}"

    if move[1] == "2":
        face_name = meaning.split("the ")[1].replace(" clockwise", "")
        return f"{move}: Turn the {face_name} twice"

    return f"{move}: Unknown move type"


def explain_solution(solution):
    if "already solved" in solution.lower():
        print(solution)
        return

    if "error" in solution.lower():
        print(solution)
        return

    moves = solution.split()

    print(f"Total moves: {len(moves)}")
    print()

    for number, move in enumerate(moves, start=1):
        print(f"{number}. {explain_single_move(move)}")


def save_solution_history(cube_string, solution):
    if "error" in solution.lower():
        print()
        print("Not saving because solver returned an error.")
        return

    if "already solved" in solution.lower():
        move_count = 0
    else:
        move_count = len(solution.split())

    new_record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cube_string": cube_string,
        "solution": solution,
        "move_count": move_count
    }

    try:
        with open(HISTORY_FILE, "r") as file:
            history = json.load(file)
    except FileNotFoundError:
        history = []

    history.append(new_record)

    with open(HISTORY_FILE, "w") as file:
        json.dump(history, file, indent=4)

    print()
    print("Solve history saved to history.json")


def view_history():
    print()
    print("Solve History")
    print("-------------")

    try:
        with open(HISTORY_FILE, "r") as file:
            history = json.load(file)
    except FileNotFoundError:
        print("No solve history found yet.")
        return

    if len(history) == 0:
        print("Solve history is empty.")
        return

    for index, record in enumerate(history, start=1):
        print()
        print(f"Solve #{index}")
        print(f"Time: {record['timestamp']}")
        print(f"Move count: {record['move_count']}")
        print(f"Solution: {record['solution']}")


def clear_history():
    with open(HISTORY_FILE, "w") as file:
        json.dump([], file, indent=4)

    print()
    print("Solve history cleared.")


def solve_cube_flow():
    print()
    print("Solve a Cube")
    print("------------")

    choice = input("Type 1 for solved cube test, or 2 to enter cube manually: ").strip()

    if choice == "1":
        cube_input = SOLVED_CUBE
    else:
        cube_input = get_cube_input_face_by_face()

    print()
    print("Final cube string:")
    print(cube_input)

    print_cube_faces(cube_input)

    print()
    print("Sticker counts:")
    for face in FACE_ORDER:
        print(f"{face}: {cube_input.count(face)}")

    answer = solve_cube(cube_input)

    print()
    print("Solution:")
    print(answer)

    print()
    print("Step-by-step explanation:")
    explain_solution(answer)

    save_solution_history(cube_input, answer)


def show_menu():
    print()
    print("CubePilot - 3x3 Rubik's Cube Solver")
    print("-----------------------------------")
    print("1. Solve a cube")
    print("2. View solve history")
    print("3. Clear solve history")
    print("4. Exit")


def main():
    while True:
        show_menu()

        choice = input("Choose an option: ").strip()

        if choice == "1":
            solve_cube_flow()

        elif choice == "2":
            view_history()

        elif choice == "3":
            clear_history()

        elif choice == "4":
            print()
            print("Goodbye. Keep cubing.")
            break

        else:
            print()
            print("Invalid option. Please choose 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()