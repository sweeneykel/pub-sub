import cv2

#def annotation_process():
image_path = ""
upper_corner_x = 250
upper_corner_y = 250
lower_corner_x = 250
lower_corner_y = 250
annotation_label = "dog"

# read in image
img = cv2.imread(image_path)

# Resize the image while preserving aspect ratio
original_height, original_width = img.shape[:2]

new_width = 600
aspect_ratio = new_width / original_width
new_height = int(original_height * aspect_ratio)
img = cv2.resize(img, (new_width, new_height))

rect1 = img.copy()
# cv2.rectangle() modifies img in place, so saving img afterward saves the version with the box drawn on it.
cv2.rectangle(rect1, (upper_corner_x, upper_corner_y), (lower_corner_x, lower_corner_y), (0, 255, 255), 2)
cv2.putText(rect1, annotation_label, (upper_corner_x, upper_corner_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2, cv2.LINE_AA)

cv2.imshow("Rectangle", rect1)

success = cv2.imwrite("annotated_uploads/boxed_image.jpg", img)
if success:
    print("Saved image")
else:
    print("Failed to save image")

cv2.waitKey(0)
cv2.destroyAllWindows()


def get_user_annotation_input(self):
    upper_corner_x = input("Enter upper corner x position: ").strip()
    upper_corner_y = input("Enter upper corner y position: ").strip()
    lower_corner_x = input("Enter lower corner x position: ").strip()
    lower_corner_y = input("Enter lower corner y position: ").strip()

    # TODO : should validate all coordinates that they are ints

    return True