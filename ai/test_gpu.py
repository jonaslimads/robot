import cv2
import os

print('OpenCL available:', cv2.ocl.haveOpenCL())

import cv2.ocl

assets_path = "/home/jonas/Projects/bot/assets"

img = cv2.UMat(cv2.imread(os.path.join(assets_path, "image.jpeg"), cv2.IMREAD_COLOR))
imgUMat = cv2.UMat(img)
gray = cv2.cvtColor(imgUMat, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (7, 7), 1.5)
gray = cv2.Canny(gray, 0, 50)

cv2.imshow("edges", gray)
cv2.waitKey()
