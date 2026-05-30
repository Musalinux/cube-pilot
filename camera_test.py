from datetime import datetime
from pathlib import Path
import json
import math

import cv2
import numpy as np


CAPTURE_FOLDER = Path("captures")
CAPTURE_FOLDER.mkdir(exist_ok=True)

CALIBRATION_FILE = CAPTURE_FOLDER / "colour_calibration.json"

COLOUR_ORDER = ["white", "yellow", "red", "orange", "green", "blue"]


def open_camera():
    for camera_index in range(4):
        camera = cv2.VideoCapture(camera_index, cv2.CAP_AVFOUNDATION)

        if camera.isOpened():
            print(f"Camera opened successfully using index {camera_index}")
            return camera

    return None


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


def load_calibration():
    if not CALIBRATION_FILE.exists():
        return {}

    try:
        with open(CALIBRATION_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {}


def save_calibration(calibration):
    with open(CALIBRATION_FILE, "w") as file:
        json.dump(calibration, file, indent=4)


def clear_calibration():
    if CALIBRATION_FILE.exists():
        CALIBRATION_FILE.unlink()

    print()
    print("Calibration cleared.")


def colour_distance_lab(lab_1, lab_2):
    return math.sqrt(
        (lab_1[0] - lab_2[0]) ** 2
        + (lab_1[1] - lab_2[1]) ** 2
        + (lab_1[2] - lab_2[2]) ** 2
    )


def classify_using_calibration(sample_lab, calibration):
    if not calibration:
        return "unknown", {}

    distances = {}

    for colour_name, colour_data in calibration.items():
        reference_lab = colour_data["lab"]
        distance = colour_distance_lab(sample_lab, reference_lab)
        distances[colour_name] = round(distance, 2)

    closest_colour = min(distances, key=distances.get)

    return closest_colour, distances


def calibrate_current_colour(frame, colour_name):
    """
    Calibration uses the CENTER sticker only.
    This is better because centre stickers define the face colour,
    even when the cube is scrambled.
    """

    points = get_sample_points(frame)

    # Sticker 5 is the centre sticker.
    center_x, center_y = points[4]

    average_bgr = get_average_bgr_from_point(frame, center_x, center_y)

    rgb_colour = bgr_to_rgb(average_bgr)
    hsv_colour = bgr_to_hsv(average_bgr)
    lab_colour = bgr_to_lab(average_bgr)

    calibration = load_calibration()

    calibration[colour_name] = {
        "rgb": rgb_colour,
        "hsv": hsv_colour,
        "lab": lab_colour,
    }

    save_calibration(calibration)

    print()
    print(f"Calibrated {colour_name.upper()}:")
    print(f"RGB={rgb_colour}")
    print(f"HSV={hsv_colour}")
    print(f"LAB={lab_colour}")


def sample_colours(frame):
    points = get_sample_points(frame)
    calibration = load_calibration()

    samples = []

    for index, (x, y) in enumerate(points, start=1):
        average_bgr = get_average_bgr_from_point(frame, x, y)

        rgb_colour = bgr_to_rgb(average_bgr)
        hsv_colour = bgr_to_hsv(average_bgr)
        lab_colour = bgr_to_lab(average_bgr)

        predicted_colour, distances = classify_using_calibration(lab_colour, calibration)

        sample = {
            "sticker": index,
            "rgb": rgb_colour,
            "hsv": hsv_colour,
            "lab": lab_colour,
            "predicted_colour": predicted_colour,
            "distances": distances,
        }

        samples.append(sample)

    return samples


def print_colour_samples(samples):
    print()
    print("Colour samples from 9 stickers:")
    print("--------------------------------")

    for sample in samples:
        print(
            f"Sticker {sample['sticker']}: "
            f"RGB={sample['rgb']} "
            f"HSV={sample['hsv']} "
            f"LAB={sample['lab']} "
            f"Predicted={sample['predicted_colour']}"
        )

        if sample["distances"]:
            print(f"  Distances: {sample['distances']}")


def save_colour_samples(samples):
    file_path = CAPTURE_FOLDER / "latest_colour_samples.json"

    with open(file_path, "w") as file:
        json.dump(samples, file, indent=4)

    print()
    print(f"Colour samples saved to: {file_path}")


def save_capture(frame):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = CAPTURE_FOLDER / f"cube_face_{timestamp}.jpg"

    cv2.imwrite(str(file_path), frame)

    print()
    print(f"Captured image saved to: {file_path}")


def print_current_calibration():
    calibration = load_calibration()

    print()
    print("Current calibration:")
    print("--------------------")

    if not calibration:
        print("No colours calibrated yet.")
        return

    for colour_name in COLOUR_ORDER:
        if colour_name in calibration:
            data = calibration[colour_name]
            print(
                f"{colour_name}: "
                f"RGB={data['rgb']} "
                f"HSV={data['hsv']} "
                f"LAB={data['lab']}"
            )
        else:
            print(f"{colour_name}: not calibrated")


def get_calibration_progress_text(calibration_mode, calibration_index):
    if not calibration_mode:
        return "a=calibrate | SPACE=save colour | s=sample | c=capture | p=print | x=clear | q=quit"

    current_colour = COLOUR_ORDER[calibration_index].upper()

    return f"CALIBRATION: show {current_colour} centre sticker, then press SPACE"


def draw_calibration_status(frame, calibration_mode, calibration_index):
    if not calibration_mode:
        return frame

    current_colour = COLOUR_ORDER[calibration_index].upper()

    draw_text(frame, f"Calibrating: {current_colour}", y=80)
    draw_text(frame, "Put the CENTER sticker inside point 5, then press SPACE", y=115)

    return frame


def main():
    camera = open_camera()

    if camera is None:
        print("Could not open camera.")
        print("Check System Settings > Privacy & Security > Camera.")
        return

    calibration_mode = False
    calibration_index = 0

    print()
    print("CubePilot Camera Colour Sampler")
    print("-------------------------------")
    print("Controls:")
    print("a     = start full calibration")
    print("SPACE = save current calibration colour")
    print("s     = sample 9 sticker colours")
    print("c     = capture image")
    print("p     = print current calibration")
    print("x     = clear calibration")
    print("q     = quit")
    print()
    print("Calibration order:")
    print("white -> yellow -> red -> orange -> green -> blue")
    print()

    while True:
        success, frame = camera.read()

        if not success:
            print("Could not read frame from camera.")
            break

        clean_frame = frame.copy()
        display_frame = frame.copy()

        display_frame = draw_cube_grid(display_frame)
        display_frame = draw_sample_points(display_frame)

        status_text = get_calibration_progress_text(calibration_mode, calibration_index)
        display_frame = draw_text(display_frame, status_text, y=40)
        display_frame = draw_calibration_status(display_frame, calibration_mode, calibration_index)

        cv2.imshow("CubePilot Camera Colour Sampler", display_frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("a"):
            clear_calibration()
            calibration_mode = True
            calibration_index = 0

            print()
            print("Started full calibration.")
            print("Show WHITE centre sticker at point 5 and press SPACE in the camera window.")

        elif key == ord(" "):
            if calibration_mode:
                current_colour = COLOUR_ORDER[calibration_index]

                calibrate_current_colour(clean_frame, current_colour)

                calibration_index += 1

                if calibration_index >= len(COLOUR_ORDER):
                    calibration_mode = False
                    calibration_index = 0

                    print()
                    print("Full calibration completed.")
                    print_current_calibration()
                else:
                    next_colour = COLOUR_ORDER[calibration_index].upper()
                    print()
                    print(f"Now show {next_colour} centre sticker at point 5 and press SPACE.")
            else:
                print()
                print("SPACE only works during calibration. Press 'a' first.")

        elif key == ord("s"):
            samples = sample_colours(clean_frame)
            print_colour_samples(samples)
            save_colour_samples(samples)

        elif key == ord("c"):
            save_capture(clean_frame)

        elif key == ord("p"):
            print_current_calibration()

        elif key == ord("x"):
            clear_calibration()
            calibration_mode = False
            calibration_index = 0

        elif key == ord("q"):
            print("Closing camera.")
            break

    camera.release()
    cv2.destroyAllWindows()


main()