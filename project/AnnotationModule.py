import cv2

# subscribe to ImageSubmittedMessage
# Receives Message like the one below
# message = ImageSubmittedMessage(
#     image_id=image_id,
#     path=str(saved_path),
#     source=source,
# )
# Then must annotate that image (AnnotationModule)

class AnnotationModule:
    def __init__(self, path: str):
        self.image_path = path
        self.annotation_data = None

    def resize_image(self):
        # read in image
        img = cv2.imread(self.image_path)

        # Resize the image while preserving aspect ratio
        original_height, original_width = img.shape[:2]

        new_width = 600
        aspect_ratio = new_width / original_width
        new_height = int(original_height * aspect_ratio)
        img = cv2.resize(img, (new_width, new_height))

        return img.copy()


    def _get_user_annotation_input(self):
        upper_corner_x = input("Enter upper corner x position: ").strip()
        upper_corner_y = input("Enter upper corner y position: ").strip()
        lower_corner_x = input("Enter lower corner x position: ").strip()
        lower_corner_y = input("Enter lower corner y position: ").strip()

        # TODO : should validate all coordinates that they are ints

        rect1 = self.resize_image()

        cv2.rectangle(rect1, (upper_corner_x, upper_corner_y), (lower_corner_x, lower_corner_y), (0, 255, 255), 2)
        cv2.imshow("Rectangle", rect1)

        # cv2.putText(image, "Dog", (370, 398), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2, cv2.LINE_AA)
        # cv2.imshow("Text Annotations", image)

        cv2.waitKey(0)
        cv2.destroyAllWindows()
