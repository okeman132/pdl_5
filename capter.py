import cv2

# 1.creating a video object
video = cv2.VideoCapture(0) 
# 2. Variable
a = 0
# 3. While loop
while True:
    a = a + 1
    # 4.Create a frame object
    check, frame = video.read()
    # Converting to grayscale
    #gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    # 5.show the frame!
    cv2.imshow("Capturing",frame)
    # 6.for playing 
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
# 7. image saving
scale_percent =  30# percent of original size
width = int(frame.shape[1] * scale_percent / 100)
height = int(frame.shape[0] * scale_percent / 100)
dim = (width, height)
resized = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
showPic = cv2.imwrite("dataset/filename.jpg",resized)
print(showPic)
cv2.imshow("Resized image", resized)
import base64
my_string = base64.b64encode(resized.read())
print(my_string.decode('utf-8'))
cv2.waitKey(0)
# 8. shutdown the camera
video.release()
cv2.destroyAllWindows 