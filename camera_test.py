from datetime import datetime
from pathlib import Path
import json
import math

import cv2
import numpy as np


CAPTURE_FOLDER = Path("captures")
CAPTURE_FOLDER.mkdir(exist_ok=True)

CALIBRATION_FILE = CAPTURE_FOLDER / "colour_calibration.json"


# These are only fallback labels.
# Once calibrated, the app will use your real cube colours from your camera.
COLOUR_KEYS = {
    "w": "white",
    "y": "yellow",
    "r": "red",
    "o": "orange",
    "g": "green",
    "b": "blue",
}


def open_camera():
    """
    Open Mac camera.
    On macOS, CAP_AVFOUNDATION usually works better.
    """

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


def draw_cube_grid(frame):
    start_x, start_y, grid_size, cell_size = get_grid_details(frame)

    # Outer square
    cv2.rectangle(
        frame,
        (start_x, start_y),
        (start_x + grid_size, start_y + grid_size),
        (255, 255, 255),
        2,
    )

    # Inner grid lines
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


def get_sample_points(frame):
    start_x, start_y, grid_size, cell_size = get_grid_details(frame)

    points = []

    for row in range(3):
        for col in range(3):
            center_x = start_x + col * cell_size + cell_size // 2
            center_y = start_y + row * cell_size + cell_size // 2

            points.append((center_x, center_y))

    return points


def draw_sample_points(frame):
    points = get_sample_points(frame)

    for index, point in enumerate(points, start=1):
        x, y = point

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


def rough_classify_from_hsv_and_rgb(rgb_colour, hsv_colour):
    """
    This is only a fallback rough guess.

    Important:
    Camera lighting can make white look orange/brown.
    Real classification should use calibration.
    """

    r, g, b = rgb_colour
    h, s, v = hsv_colour

    max_channel = max(r, g, b)
    min_channel = min(r, g, b)
    channel_gap = max_channel - min_channel

    # White/grey detection:
    # White usually has similar R, G, B values.
    # Under shadows it may not be super bright, so we don't require very high V.
    if channel_gap < 45 and v > 90 and s < 90:
        return "white"

    if v < 45:
        return "unknown/dark"

    # Red wraps around HSV.
    if h <= 8 or h >= 170:
        return "red"

    if 9 <= h <= 22:
        return "orange"

    if 23 <= h <= 38:
        return "yellow"

    if 39 <= h <= 85:
        return "green"

    if 86 <= h <= 135:
        return "blue"

    return "unknown"


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

    print()
    print(f"Calibration saved to: {CALIBRATION_FILE}")


def colour_distance_lab(lab_1, lab_2):
    """
    Simple Euclidean distance in LAB colour space.
    LAB is better than raw RGB for comparing visible colours.
    """

    return math.sqrt(
        (lab_1[0] - lab_2[0]) ** 2
        + (lab_1[1] - lab_2[1]) ** 2
        + (lab_1[2] - lab_2[2]) ** 2
    )


def classify_using_calibration(sample_lab, calibration):
    if not calibration:
        return None

    closest_colour = None
    closest_distance = float("inf")

    for colour_name, colour_data in calibration.items():
        reference_lab = colour_data["lab"]
        distance = colour_distance_lab(sample_lab, reference_lab)

        if distance < closest_distance:
            closest_distance = distance
            closest_colour = colour_name

    return closest_colour


def sample_colours(frame):
    points = get_sample_points(frame)
    calibration = load_calibration()

    samples = []

    for index, point in enumerate(points, start=1):
        x, y = point

        average_bgr = get_average_bgr_from_point(frame, x, y)

        rgb_colour = bgr_to_rgb(average_bgr)
        hsv_colour = bgr_to_hsv(average_bgr)
        lab_colour = bgr_to_lab(average_bgr)

        calibrated_prediction = classify_using_calibration(lab_colour, calibration)
        rough_prediction = rough_classify_from_hsv_and_rgb(rgb_colour, hsv_colour)

        if calibrated_prediction:
            final_prediction = calibrated_prediction
            prediction_type = "calibrated"
        else:
            final_prediction = rough_prediction
            prediction_type = "rough"

        sample = {
            "sticker": index,
            "rgb": rgb_colour,
            "hsv": hsv_colour,
            "lab": lab_colour,
            "predicted_colour": final_prediction,
            "prediction_type": prediction_type,
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
            f"Predicted={sample['predicted_colour']} "
            f"({sample['prediction_type']})"
        )


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


def calibrate_colour(frame, colour_name):
    """
    Calibrate one colour using the centre sticker.

    Put the selected colour face inside the grid,
    then press the matching key:
    w = white, y = yellow, r = red, o = orange, g = green, b = blue
    """

    points = get_sample_points(frame)

    # Sticker 5 is the centre sticker in a 3x3 grid.
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
    print(f"Calibrated {colour_name}:")
    print(f"RGB={rgb_colour}")
    print(f"HSV={hsv_colour}")
    print(f"LAB={lab_colour}")


def print_current_calibration():
    calibration = load_calibration()

    print()
    print("Current calibration:")
    print("--------------------")

    if not calibration:
        print("No colours calibrated yet.")
        return

    for colour_name, data in calibration.items():
        print(
            f"{colour_name}: "
            f"RGB={data['rgb']} "
            f"HSV={data['hsv']} "
            f"LAB={data['lab']}"
        )


def clear_calibration():
    if CALIBRATION_FILE.exists():
        CALIBRATION_FILE.unlink()

    print()
    print("Calibration cleared.")


def draw_status_text(frame):
    cv2.putText(
        frame,
        "s=sample | c=capture | w/y/r/o/g/b=calibrate | p=show calibration | x=clear calibration | q=quit",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
    )

    return frame


def main():
    camera = open_camera()

    if camera is None:
        print("Could not open camera.")
        print("Check System Settings > Privacy & Security > Camera.")
        return

    print()
    print("CubePilot Camera Colour Sampler")
    print("-------------------------------")
    print("Controls:")
    print("s = sample 9 sticker colours")
    print("c = capture image")
    print("w = calibrate WHITE using centre sticker")
    print("y = calibrate YELLOW using centre sticker")
    print("r = calibrate RED using centre sticker")
    print("o = calibrate ORANGE using centre sticker")
    print("g = calibrate GREEN using centre sticker")
    print("b = calibrate BLUE using centre sticker")
    print("p = print current calibration")
    print("x = clear calibration")
    print("q = quit")
    print()
    print("Important:")
    print("For calibration, place that colour face inside the grid and press its key.")
    print("Example: show the white face, then press w.")
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
        display_frame = draw_status_text(display_frame)

        cv2.imshow("CubePilot Camera Colour Sampler", display_frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):
            samples = sample_colours(clean_frame)
            print_colour_samples(samples)
            save_colour_samples(samples)

        elif key == ord("c"):
            save_capture(clean_frame)

        elif key in [ord(k) for k in COLOUR_KEYS.keys()]:
            pressed_key = chr(key)
            colour_name = COLOUR_KEYS[pressed_key]
            calibrate_colour(clean_frame, colour_name)

        elif key == ord("p"):
            print_current_calibration()

        elif key == ord("x"):
            clear_calibration()

        elif key == ord("q"):
            print("Closing camera.")
            break

    camera.release()
    cv2.destroyAllWindows()


main()