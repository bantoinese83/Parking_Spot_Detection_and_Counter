import argparse
import atexit
import random
import time

import cv2
import numpy as np

from base_logging import Logger
from events import startup, run, shutdown
from util import get_parking_lot_spots_bboxes, empty_or_occupied, EMPTY

# Constants
COLOR_RED = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)

# Initialize the logger
logger = Logger()


def calculate_image_difference(image1, image2):
    """Calculate the difference between two images."""
    return np.mean(image1) - np.mean(image2)


def draw_empty_or_occupied_count(frame, empty_count, occupied_count):
    """Draw the count of empty and occupied spots on the frame."""
    cv2.putText(
        frame,
        f"Empty: {empty_count}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        COLOR_GREEN,
        2,
        cv2.LINE_AA,
    )
    cv2.putText(
        frame,
        f"Occupied: {occupied_count}",
        (10, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        COLOR_RED,
        2,
        cv2.LINE_AA,
    )
    return frame


def draw_parking_spots_on_frame(frame, parking_spots):
    """Draw parking spots on the frame."""
    for spot_index, spot in enumerate(parking_spots):
        x1, y1, w, h = spot
        cropped_spot = frame[y1 : y1 + h, x1 : x1 + w, :]
        spot_status = empty_or_occupied(cropped_spot)
        color = COLOR_RED if spot_status else COLOR_GREEN
        frame = cv2.rectangle(frame, (x1, y1), (x1 + w, y1 + h), color, 2)
        label = (
            f"{chr(65 + spot_index // 20)}{spot_index % 20 + 1}"  # Generate the label
        )
        cv2.putText(
            frame,
            label,
            (x1 + 5, y1 + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )
    return frame


def draw_occupied_spots(frame, occupied_spots, parking_spot_timestamps):
    """Draw all occupied spots on the frame."""
    spots_to_draw = random.sample(occupied_spots, min(5, len(occupied_spots)))

    # Calculate the position of the table
    height, width, _ = frame.shape
    table_top_left = (width - 1000, height - 140)
    table_bottom_right = (width - 210, height - 10)

    # Draw the table
    cv2.rectangle(frame, table_top_left, table_bottom_right, COLOR_RED, 2)

    if spots_to_draw:
        for index, spot in enumerate(spots_to_draw):
            label = f"{chr(65 + spot // 16)}{spot % 16 + 1}"  # Generate the label
            text_position = (
                table_top_left[0] + 10,
                table_top_left[1] + 30 + 20 * index,
            )
            timestamp = parking_spot_timestamps[spot]
            parked_time = time.ctime(timestamp)
            elapsed_time = time.time() - timestamp
            cv2.putText(
                frame,
                f"Occ Spot: {label}, Parked at: {parked_time}, Elapsed time: {elapsed_time:.2f} seconds",
                text_position,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,  # Reduce the font size
                COLOR_RED,
                2,
                cv2.LINE_AA,
            )
            cv2.imshow("frame", frame)
            cv2.waitKey(2000)  # Wait for 2000 ms (2 seconds)
    else:
        text_position = (table_top_left[0] + 10, table_top_left[1] + 30)
        cv2.putText(
            frame,
            "No spots are occupied",
            text_position,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,  # Reduce the font size
            COLOR_GREEN,
            2,
            cv2.LINE_AA,
        )
    return frame


def draw_available_spots(frame, available_spots):
    """Draw all available spots on the frame."""
    spots_to_draw = random.sample(available_spots, min(5, len(available_spots)))

    # Calculate the position of the table
    height, width, _ = frame.shape
    table_top_left = (width - 200, height - 140)
    table_bottom_right = (width - 10, height - 10)

    # Draw the table
    cv2.rectangle(frame, table_top_left, table_bottom_right, COLOR_GREEN, 2)

    if spots_to_draw:
        for index, spot in enumerate(spots_to_draw):
            label = f"{chr(65 + spot // 16)}{spot % 16 + 1}"  # Generate the label
            text_position = (
                table_top_left[0] + 10,
                table_top_left[1] + 30 + 20 * index,
            )
            cv2.putText(
                frame,
                f"Avail Spot: {label}",
                text_position,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,  # Reduce the font size
                COLOR_GREEN,
                2,
                cv2.LINE_AA,
            )
            cv2.imshow("frame", frame)
            cv2.waitKey(2000)  # Wait for 2000 ms (2 seconds)
    else:
        text_position = (table_top_left[0] + 10, table_top_left[1] + 30)
        cv2.putText(
            frame,
            "All spots are occupied",
            text_position,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,  # Reduce the font size
            COLOR_RED,
            2,
            cv2.LINE_AA,
        )
    return frame


def process_frame(
    frame,
    parking_spots,
    frame_number,
    step,
    previous_frame,
    parking_spot_timestamps,
    previous_spot_statuses,
):
    """Process each frame of the video."""
    empty_count, occupied_count = 0, 0
    image_differences = [None for _ in parking_spots]
    spot_statuses = []  # List to store the status of each spot

    for spot_index, spot in enumerate(parking_spots):
        x1, y1, w, h = spot
        cropped_spot = frame[y1 : y1 + h, x1 : x1 + w, :]
        if frame_number % step == 0 and previous_frame is not None:
            image_differences[spot_index] = calculate_image_difference(
                cropped_spot, previous_frame
            )
        spot_status = empty_or_occupied(cropped_spot)
        spot_statuses.append(spot_status)
        if spot_status:
            occupied_count += 1
        else:
            empty_count += 1

        # Generate the label for the spot
        label = f"{chr(65 + spot_index // 20)}{spot_index % 20 + 1}"

        # If the spot just became occupied, record the current time
        if spot_status and not previous_spot_statuses[spot_index]:
            parking_spot_timestamps[spot_index] = time.time()
            logger.log_info(
                f"Car parked at spot {label} at {time.ctime(parking_spot_timestamps[spot_index])}"
            )

        # If the spot just became empty, calculate the duration and record the exit time
        elif not spot_status and previous_spot_statuses[spot_index]:
            exit_time = time.time()
            parked_duration = exit_time - parking_spot_timestamps[spot_index]
            logger.log_info(
                f"Car left spot {label} at {time.ctime(exit_time)}, was parked for {parked_duration:.2f} seconds"
            )
            parking_spot_timestamps[spot_index] = None

        # If the spot is occupied, calculate the elapsed time and display it
        elif spot_status:
            elapsed_time = time.time() - parking_spot_timestamps[spot_index]
            cv2.putText(
                frame,
                f"Time: {elapsed_time:.2f}",
                (x1 + 5, y1 + 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

    frame = draw_parking_spots_on_frame(frame, parking_spots)
    frame = draw_empty_or_occupied_count(frame, empty_count, occupied_count)

    if frame_number % 10 == 0:
        logger.log_info(
            f"Frame: {frame_number}, Empty: {empty_count}, Occupied: {occupied_count}"
        )

    available_spots = [i for i, status in enumerate(spot_statuses) if status == EMPTY]
    frame = draw_available_spots(frame, available_spots)

    occupied_spots = [i for i, status in enumerate(spot_statuses) if status != EMPTY]
    frame = draw_occupied_spots(frame, occupied_spots, parking_spot_timestamps)

    return frame, spot_statuses


def process_video(video_path, mask_path, step):
    video_capture = cv2.VideoCapture(video_path)
    mask_image = cv2.imread(mask_path, 0)
    connected_components = cv2.connectedComponentsWithStats(mask_image, 4, cv2.CV_32S)
    parking_spots = get_parking_lot_spots_bboxes(connected_components)

    frame_number = 0
    previous_frame = None

    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if not ret:
            break

        frame = process_frame(
            frame,
            parking_spots,
            frame_number,
            step,
            previous_frame,
            [0] * len(parking_spots),
            [False] * len(parking_spots),
        )[0]
        cv2.imshow("frame", frame)

        if cv2.waitKey(25) & 0xFF == ord("q"):
            break

        previous_frame = frame.copy()
        frame_number += 1

    video_capture.release()
    cv2.destroyAllWindows()


def parse_command_line_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Process a video and detect parking spots."
    )
    parser.add_argument(
        "--video",
        type=str,
        default="data/parking_1920_1080_loop.mp4",
        help="Path to the video file.",
    )
    parser.add_argument(
        "--mask",
        type=str,
        default="data/mask_1920_1080.png",
        help="Path to the mask image.",
    )
    parser.add_argument(
        "--step", type=int, default=100, help="Step to process the video."
    )
    return parser.parse_args()


def main():
    startup()
    run()

    try:
        args = parse_command_line_arguments()
        process_video(args.video, args.mask, args.step)
        logger.log_success("Video processing completed successfully.")
    except KeyboardInterrupt:
        logger.log_info("Program interrupted by the user.")
    except Exception as e:
        logger.log_error(f"Error occurred during main execution: {str(e)}")

        atexit.register(shutdown)


if __name__ == "__main__":
    main()
