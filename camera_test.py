from datetime import datetime
from pathlib import Path
import json

import cv2
import numpy as np


CAPTURE_FOLDER = Path("captures")
CAPTURE_FOLDER.mkdir(exist_ok=True)


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


def sample_colours(frame):
    points = get_sample_points(frame)

    samples = []

    for index, point in enumerate(points, start=1):
        x, y = point

        sample_size = 10

        sample_area = frame[
            y - sample_size:y + sample_size,
            x - sample_size:x + sample_size
        ]

        average_bgr = np.mean(sample_area, axis=(0, 1))
        b, g, r = average_bgr

        rgb_colour = [int(r), int(g), int(b)]

        one_pixel = np.uint8([[[b, g, r]]])
        hsv_pixel = cv2.cvtColor(one_pixel, cv2.COLOR_BGR2HSV)[0][0]
        h, s, v = hsv_pixel

        sample = {
            "sticker": index,
            "rgb": rgb_colour,
            "hsv": [int(h), int(s), int(v)]
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
            f"RGB={sample['rgb']} HSV={sample['hsv']}"
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
    print("q = quit")
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

        cv2.putText(
            display_frame,
            "Place one cube face inside the grid | s = sample | c = capture | q = quit",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv2.imshow("CubePilot Camera Colour Sampler", display_frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):
            samples = sample_colours(clean_frame)
            print_colour_samples(samples)
            save_colour_samples(samples)

        elif key == ord("c"):
            save_capture(clean_frame)

        elif key == ord("q"):
            print("Closing camera.")
            break

    camera.release()
    cv2.destroyAllWindows()


main()