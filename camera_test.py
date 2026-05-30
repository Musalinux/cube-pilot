from datetime import datetime
from pathlib import Path

import cv2


CAPTURE_FOLDER = Path("captures")
CAPTURE_FOLDER.mkdir(exist_ok=True)


def open_camera():
    """
    Try to open the Mac camera.
    We try camera indexes 0, 1, 2, 3 because different machines expose cameras differently.
    """

    for camera_index in range(4):
        camera = cv2.VideoCapture(camera_index, cv2.CAP_AVFOUNDATION)

        if camera.isOpened():
            print(f"Camera opened successfully using index {camera_index}")
            return camera

    return None


def draw_cube_grid(frame):
    """
    Draws a 3x3 square grid in the middle of the camera frame.
    Later, this grid will help us detect the 9 cube sticker colours.
    """

    height, width = frame.shape[:2]

    grid_size = min(width, height) // 2

    start_x = (width - grid_size) // 2
    start_y = (height - grid_size) // 2

    cell_size = grid_size // 3

    # Outer rectangle
    cv2.rectangle(
        frame,
        (start_x, start_y),
        (start_x + grid_size, start_y + grid_size),
        (255, 255, 255),
        2,
    )

    # Inner grid lines
    for i in range(1, 3):
        # Vertical lines
        cv2.line(
            frame,
            (start_x + i * cell_size, start_y),
            (start_x + i * cell_size, start_y + grid_size),
            (255, 255, 255),
            2,
        )

        # Horizontal lines
        cv2.line(
            frame,
            (start_x, start_y + i * cell_size),
            (start_x + grid_size, start_y + i * cell_size),
            (255, 255, 255),
            2,
        )

    return frame, start_x, start_y, grid_size


def save_capture(frame):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = CAPTURE_FOLDER / f"cube_face_{timestamp}.jpg"

    cv2.imwrite(str(file_path), frame)

    print(f"Captured image saved to: {file_path}")


def main():
    camera = open_camera()

    if camera is None:
        print("Could not open camera.")
        print("On Mac, check System Settings > Privacy & Security > Camera.")
        print("Allow VS Code, Terminal, or Python to access the camera.")
        return

    print()
    print("CubePilot Camera Test")
    print("--------------------")
    print("Controls:")
    print("c = capture image")
    print("q = quit")
    print()

    while True:
        success, frame = camera.read()

        if not success:
            print("Could not read frame from camera.")
            break

        frame, start_x, start_y, grid_size = draw_cube_grid(frame)

        cv2.putText(
            frame,
            "Place one cube face inside the grid | Press c to capture | Press q to quit",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv2.imshow("CubePilot Camera Test", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("c"):
            save_capture(frame)

        elif key == ord("q"):
            print("Closing camera.")
            break

    camera.release()
    cv2.destroyAllWindows()


main()