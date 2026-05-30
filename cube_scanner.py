from pathlib import Path
import json
import math

import cv2
import numpy as np

from main import solve_cube, explain_solution, print_cube_faces, validate_cube_string


CAPTURE_FOLDER = Path("captures")
CALIBRATION_FILE = CAPTURE_FOLDER / "colour_calibration.json"
SCANNED_CUBE_FILE = CAPTURE_FOLDER / "scanned_cube.json"

FACE_ORDER = ["U", "R", "F", "D", "L", "B"]


def open_camera():
    for camera_index in range(4):
        camera = cv2.VideoCapture(camera_index, cv2.CAP_AVFOUNDATION)

        if camera.isOpened():
            print(f"Camera opened successfully using index {camera_index}")
            return camera

    return None


def load_calibration():
    if not CALIBRATION_FILE.exists():
        print("No calibration file found.")
        print("Run this first:")
        print("python camera_test.py")
        print("Then press 'a' and calibrate all colours.")
        return {}

    with open(CALIBRATION_FILE, "r") as file:
        return json.load(file)


def get_grid_details(frame):
    height, width = frame.shape[:2]

    grid_size = min(width, height) // 2
    start_x = (width - grid_size) // 2
    start_y = (height - grid_size) // 2
    cell_size = grid_size // 3

    return start_x, start_y, grid_size, cell_size


def get_sample_points(frame):
    start_x, start_y, grid_size, cell_size = get_grid_details(frame)

    points = []

    for row in range(3):
        for col in range(3):
            center_x = start_x + col * cell_size + cell_size // 2
            center_y = start_y + row * cell_size + cell_size // 2
            points.append((center_x, center_y))

    return points


def draw_cube_grid(frame):
    start_x, start_y, grid_size, cell_size = get_grid_details(frame)

    cv2.rectangle(
        frame,
        (start_x, start_y),
        (start_x + grid_size, start_y + grid_size),
        (255, 255, 255),
        2,
    )

    for i in range(1, 3):
        cv2.line(
            frame,
            (start_x + i * cell_size, start_y),
            (start_x + i * cell_size, start_y + grid_size),
            (255, 255, 255),
            2,
        )

        cv2.line(
            frame,
            (start_x, start_y + i * cell_size),
            (start_x + grid_size, start_y + i * cell_size),
            (255, 255, 255),
            2,
        )

    return frame


def draw_sample_points(frame):
    points = get_sample_points(frame)

    for index, (x, y) in enumerate(points, start=1):
        cv2.circle(frame, (x, y), 8, (0, 255, 255), -1)

        cv2.putText(
            frame,
            str(index),
            (x + 10, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2,
        )

    return frame


def draw_text(frame, text, y=40):
    cv2.putText(
        frame,
        text,
        (20, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2,
    )

    return frame


def get_average_bgr_from_point(frame, x, y, sample_size=12):
    height, width = frame.shape[:2]

    x1 = max(x - sample_size, 0)
    x2 = min(x + sample_size, width)
    y1 = max(y - sample_size, 0)
    y2 = min(y + sample_size, height)

    sample_area = frame[y1:y2, x1:x2]
    average_bgr = np.mean(sample_area, axis=(0, 1))

    return [
        int(average_bgr[0]),
        int(average_bgr[1]),
        int(average_bgr[2]),
    ]


def bgr_to_rgb(bgr_colour):
    b, g, r = bgr_colour
    return [int(r), int(g), int(b)]


def bgr_to_hsv(bgr_colour):
    bgr_pixel = np.uint8([[bgr_colour]])
    hsv_pixel = cv2.cvtColor(bgr_pixel, cv2.COLOR_BGR2HSV)[0][0]
    h, s, v = hsv_pixel
    return [int(h), int(s), int(v)]


def bgr_to_lab(bgr_colour):
    bgr_pixel = np.uint8([[bgr_colour]])
    lab_pixel = cv2.cvtColor(bgr_pixel, cv2.COLOR_BGR2LAB)[0][0]
    l, a, b = lab_pixel
    return [int(l), int(a), int(b)]


def colour_distance_lab(lab_1, lab_2):
    return math.sqrt(
        (lab_1[0] - lab_2[0]) ** 2
        + (lab_1[1] - lab_2[1]) ** 2
        + (lab_1[2] - lab_2[2]) ** 2
    )


def classify_using_calibration(sample_lab, calibration):
    distances = {}

    for colour_name, colour_data in calibration.items():
        reference_lab = colour_data["lab"]
        distance = colour_distance_lab(sample_lab, reference_lab)
        distances[colour_name] = round(distance, 2)

    closest_colour = min(distances, key=distances.get)

    return closest_colour, distances


def scan_current_face(frame, calibration):
    points = get_sample_points(frame)
    scanned_stickers = []

    for index, (x, y) in enumerate(points, start=1):
        average_bgr = get_average_bgr_from_point(frame, x, y)

        rgb_colour = bgr_to_rgb(average_bgr)
        hsv_colour = bgr_to_hsv(average_bgr)
        lab_colour = bgr_to_lab(average_bgr)

        predicted_colour, distances = classify_using_calibration(lab_colour, calibration)

        sticker = {
            "sticker": index,
            "rgb": rgb_colour,
            "hsv": hsv_colour,
            "lab": lab_colour,
            "predicted_colour": predicted_colour,
            "distances": distances,
        }

        scanned_stickers.append(sticker)

    return scanned_stickers


def print_scanned_face(face_letter, scanned_stickers):
    print()
    print(f"Scanned {face_letter} face:")
    print("----------------")

    colours = [sticker["predicted_colour"] for sticker in scanned_stickers]

    print(colours[0:3])
    print(colours[3:6])
    print(colours[6:9])

    print()
    print("Detailed sticker data:")

    for sticker in scanned_stickers:
        print(
            f"Sticker {sticker['sticker']}: "
            f"Predicted={sticker['predicted_colour']} "
            f"RGB={sticker['rgb']} "
            f"LAB={sticker['lab']}"
        )


def print_colour_grid(title, colours):
    print()
    print(title)
    print("-" * len(title))
    print(colours[0:3])
    print(colours[3:6])
    print(colours[6:9])


def build_colour_to_face_map(scanned_faces):
    """
    Use the centre sticker of each scanned face to decide which colour belongs to U/R/F/D/L/B.

    Example:
    If the U face centre is detected as white, then white -> U.
    If the R face centre is detected as red, then red -> R.
    """

    colour_to_face = {}

    for face_letter in FACE_ORDER:
        centre_sticker = scanned_faces[face_letter][4]
        centre_colour = centre_sticker["predicted_colour"]

        if centre_colour in colour_to_face:
            existing_face = colour_to_face[centre_colour]
            raise ValueError(
                f"Duplicate centre colour detected: {centre_colour}. "
                f"It was already mapped to {existing_face}, but also found for {face_letter}."
            )

        colour_to_face[centre_colour] = face_letter

    return colour_to_face


def convert_scanned_faces_to_cube_string(scanned_faces):
    colour_to_face = build_colour_to_face_map(scanned_faces)

    print()
    print("Colour to face mapping:")
    print("-----------------------")
    for colour, face in colour_to_face.items():
        print(f"{colour} -> {face}")

    cube_string = ""

    for face_letter in FACE_ORDER:
        stickers = scanned_faces[face_letter]

        for sticker in stickers:
            predicted_colour = sticker["predicted_colour"]

            if predicted_colour not in colour_to_face:
                raise ValueError(f"Unknown colour found: {predicted_colour}")

            cube_letter = colour_to_face[predicted_colour]
            cube_string += cube_letter

    return cube_string


def save_scanned_cube(scanned_faces, cube_string):
    SCANNED_CUBE_FILE.parent.mkdir(exist_ok=True)

    data = {
        "face_order": FACE_ORDER,
        "cube_string": cube_string,
        "scanned_faces": scanned_faces,
    }

    with open(SCANNED_CUBE_FILE, "w") as file:
        json.dump(data, file, indent=4)

    print()
    print(f"Scanned cube saved to: {SCANNED_CUBE_FILE}")


def print_scan_instructions():
    print()
    print("CubePilot Full Cube Scanner")
    print("---------------------------")
    print("Controls:")
    print("SPACE = scan current face and move to next")
    print("r     = rescan current face")
    print("q     = quit")
    print()
    print("Scan order:")
    print("U -> R -> F -> D -> L -> B")
    print()
    print("Important:")
    print("For this MVP, scan each face straight-on.")
    print("Keep the cube at the same distance and lighting as calibration.")
    print("Make sure the centre sticker sits on point 5.")
    print()


def main():
    calibration = load_calibration()

    if not calibration:
        return

    required_colours_count = 6

    if len(calibration) < required_colours_count:
        print("Calibration is incomplete.")
        print(f"Expected 6 colours, found {len(calibration)}.")
        print("Run python camera_test.py and calibrate all colours first.")
        return

    camera = open_camera()

    if camera is None:
        print("Could not open camera.")
        return

    print_scan_instructions()

    face_index = 0
    scanned_faces = {}

    while True:
        success, frame = camera.read()

        if not success:
            print("Could not read frame from camera.")
            break

        clean_frame = frame.copy()
        display_frame = frame.copy()

        current_face = FACE_ORDER[face_index]

        display_frame = draw_cube_grid(display_frame)
        display_frame = draw_sample_points(display_frame)

        draw_text(
            display_frame,
            f"SCAN {current_face} FACE | SPACE=scan | r=rescan | q=quit",
            y=40,
        )

        draw_text(
            display_frame,
            "Place centre sticker on point 5",
            y=75,
        )

        cv2.imshow("CubePilot Full Cube Scanner", display_frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord(" "):
            scanned_stickers = scan_current_face(clean_frame, calibration)
            scanned_faces[current_face] = scanned_stickers

            print_scanned_face(current_face, scanned_stickers)

            face_index += 1

            if face_index >= len(FACE_ORDER):
                print()
                print("All 6 faces scanned.")
                break

            next_face = FACE_ORDER[face_index]
            print()
            print(f"Now scan {next_face} face.")

        elif key == ord("r"):
            print()
            print(f"Rescan mode: still on {current_face} face.")

        elif key == ord("q"):
            print("Closing scanner.")
            camera.release()
            cv2.destroyAllWindows()
            return

    camera.release()
    cv2.destroyAllWindows()

    try:
        cube_string = convert_scanned_faces_to_cube_string(scanned_faces)

        print()
        print("Generated cube string:")
        print(cube_string)

        print_cube_faces(cube_string)

        print()
        print("Sticker counts:")
        for face in FACE_ORDER:
            print(f"{face}: {cube_string.count(face)}")

        is_valid, validation_message = validate_cube_string(cube_string)

        print()
        print("Validation:")
        print(validation_message)

        if not is_valid:
            print("Cube string failed basic validation. Not solving.")
            return

        save_scanned_cube(scanned_faces, cube_string)

        answer = solve_cube(cube_string)

        print()
        print("Solution:")
        print(answer)

        print()
        print("Step-by-step explanation:")
        explain_solution(answer)

    except Exception as error:
        print()
        print("Scanner error:")
        print(error)


if __name__ == "__main__":
    main()