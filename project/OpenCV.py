import cv2

#def annotation_process():
image_path = input("Path of image: ").strip()
upper_corner_x = 100
upper_corner_y = 100
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

user_input = input("is this okay?").strip()

if user_input == 'yes':
    success = cv2.imwrite("annotated_uploads/boxed_image.jpg", rect1)
    if success:
        print("Saved image")

cv2.waitKey(0)
cv2.destroyAllWindows()