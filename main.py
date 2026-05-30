import kociemba


VALID_FACELET_LETTERS = {"U", "R", "F", "D", "L", "B"}
FACE_ORDER = ["U", "R", "F", "D", "L", "B"]
SOLVED_CUBE = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"


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


def get_cube_input_face_by_face():
    print("Enter each face as 9 letters.")
    print("Example for solved U face: UUUUUUUUU")
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


print("CubePilot - 3x3 Rubik's Cube Solver")
print("-----------------------------------")
print("Face order required by solver:")
print("U face, then R face, then F face, then D face, then L face, then B face")
print()

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