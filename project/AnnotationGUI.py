import os
import cv2

def add_coordinate_grid(img, step=50):
    grid = img.copy()
    height, width = grid.shape[:2]

    for x in range(0, width, step):
        cv2.line(grid, (x, 0), (x, height - 1), (200, 200, 200), 1)
        cv2.putText(
            grid,
            str(x),
            (x + 2, 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (0, 0, 255),
            1,
            cv2.LINE_AA,
        )

    for y in range(0, height, step):
        cv2.line(grid, (0, y), (width - 1, y), (200, 200, 200), 1)
        cv2.putText(
            grid,
            str(y),
            (2, y - 2 if y > 15 else y + 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (0, 0, 255),
            1,
            cv2.LINE_AA,
        )

    return grid


def annotate_image(image_path: str):
    #image_path = input("image_path: ").strip()
    img = cv2.imread(image_path)

    if img is None:
        print("Could not load image.")
        return

    original_height, original_width = img.shape[:2]

    new_width = 600
    aspect_ratio = new_width / original_width
    new_height = int(original_height * aspect_ratio)
    img = cv2.resize(img, (new_width, new_height))

    height, width = img.shape[:2]
    print(f"Image size: width={width}, height={height}")
    # x: 0 to width - 1
    # y: 0 to height - 1

    while True:
        grid_img = add_coordinate_grid(img, step=50)
        cv2.imshow("Coordinate Grid", grid_img)
        cv2.waitKey(1)

        upper_corner_x = int(input("upper_corner_x: ").strip())
        upper_corner_y = int(input("upper_corner_y: ").strip())
        lower_corner_x = int(input("lower_corner_x: ").strip())
        lower_corner_y = int(input("lower_corner_y: ").strip())
        annotation_label = input("annotation_label: ").strip()

        preview = grid_img.copy()

        cv2.rectangle(
            preview,
            (upper_corner_x, upper_corner_y),
            (lower_corner_x, lower_corner_y),
            (0, 255, 255),
            2,
        )
        cv2.putText(
            preview,
            annotation_label,
            (upper_corner_x, max(upper_corner_y - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 0, 0),
            2,
            cv2.LINE_AA,
        )

        cv2.imshow("Annotation Preview", preview)
        cv2.waitKey(1)

        confirm = input("Is this okay? (y/n): ").strip().lower()
        if confirm == "y":
            os.makedirs("annotated_uploads", exist_ok=True)

            base_name = os.path.basename(image_path)
            name, ext = os.path.splitext(base_name)
            if not ext:
                ext = ".jpg"

            output_path = os.path.join("annotated_uploads", f"{name}_annotated{ext}")
            success = cv2.imwrite(output_path, preview)
            if success:
                print(f"Saved image to {output_path}")
                print(f"image_metadata for image {name}: upper_corner_x: {upper_corner_x}, upper_corner_y: {upper_corner_y}, lower_corner_x: {lower_corner_x}, lower_corner_y: {lower_corner_y}, annotation_label: {annotation_label}")
                #"image_metadata": image_metadata,
                #"annotation_metadata": annotation_metadata,

            else:
                print("Failed to save image.")

            cv2.destroyAllWindows()
            return success

        cv2.destroyWindow("Annotation Preview")


# def main():
#     while True:
#         print("\nMenu")
#         print("1. Annotate new file")
#         print("2. Exit")
#
#         choice = input("Select an option: ").strip()
#
#         if choice == "1":
#             annotate_image()
#         elif choice == "2":
#             cv2.destroyAllWindows()
#             break
#         else:
#             print("Invalid option.")
#
#
# if __name__ == "__main__":
#     main()
