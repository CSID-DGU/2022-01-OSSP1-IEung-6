import numpy as np
import cv2


class Pupil(object):
    """
    동공을 감지하고 위치를 추정하는 클래스
    """

    def __init__(self, eye_frame, threshold):
        self.iris_frame = None
        self.threshold = threshold
        self.x = None
        self.y = None

        self.detect_iris(eye_frame)

    @staticmethod
    def image_processing(eye_frame, threshold):
        """
        눈 프레임에서 동공을 분리하는 작업 수행

        인자값:
            eye_frame (numpy.ndarray): 다른 거 없이 눈만 포함되어 있는 프레임
            threshold (int): 눈 프레임을 이진화하는데 사용하는 threshold

        리턴값:
            동공을 나타내는 요소만 있는 프레임
        """
        kernel = np.ones((3, 3), np.uint8)
        new_frame = cv2.bilateralFilter(eye_frame, 10, 15, 15)
        new_frame = cv2.erode(new_frame, kernel, iterations=3)
        new_frame = cv2.threshold(new_frame, threshold, 255, cv2.THRESH_BINARY)[1]

        return new_frame

    def detect_iris(self, eye_frame):
        """
        동공을 감지하고 중심을 계산해 동공의 위치를 추정함

        인자값:
            eye_frame (numpy.ndarray): 다른 거 없이 눈만 포함되어 있는 프레임
        """
        self.iris_frame = self.image_processing(eye_frame, self.threshold)

        contours, _ = cv2.findContours(self.iris_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2:]
        contours = sorted(contours, key=cv2.contourArea)

        try:
            moments = cv2.moments(contours[-2])
            self.x = int(moments['m10'] / moments['m00'])
            self.y = int(moments['m01'] / moments['m00'])
        except (IndexError, ZeroDivisionError):
            pass
