import kociemba


VALID_FACELET_LETTERS = {"U", "R", "F", "D", "L", "B"}


def validate_cube_string(cube_string):
    cube_string = cube_string.strip().upper()

    if len(cube_string) != 54:
        return False, "Cube string must be exactly 54 characters long."

    for letter in cube_string:
        if letter not in VALID_FACELET_LETTERS:
            return False, f"Invalid letter found: {letter}. Use only U, R, F, D, L, B."

    for letter in VALID_FACELET_LETTERS:
        count = cube_string.count(letter)
        if count != 9:
            return False, f"Letter {letter} appears {count} times. Each face must appear exactly 9 times."

    return True, "Cube string looks valid."


def solve_cube(cube_string):
    is_valid, message = validate_cube_string(cube_string)

    if not is_valid:
        return message

    try:
        solution = kociemba.solve(cube_string)

        if solution == "":
            return "Cube is already solved. No moves needed."

        return solution

    except Exception as error:
        return f"Solver error: {error}"


print("CubePilot - 3x3 Rubik's Cube Solver")
print("-----------------------------------")
print("Enter cube state in this order:")
print("U face, then R face, then F face, then D face, then L face, then B face")
print()
print("Example solved cube:")
print("UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB")
print()

cube_input = input("Enter your 54-character cube string: ")

answer = solve_cube(cube_input)

print()
print("Solution:")
print(answer)