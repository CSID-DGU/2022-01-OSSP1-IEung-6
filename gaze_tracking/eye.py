import math
import numpy as np
import cv2
from .pupil import Pupil


class Eye(object):
    """
    눈을 분리하기 위해 새 프레임을 만들고 동공 감지를 하는 클래스
    """

    LEFT_EYE_POINTS = [36, 37, 38, 39, 40, 41]
    RIGHT_EYE_POINTS = [42, 43, 44, 45, 46, 47]

    def __init__(self, original_frame, landmarks, side, calibration):
        self.frame = None
        self.origin = None
        self.center = None
        self.pupil = None
        self.landmark_points = None

        self._analyze(original_frame, landmarks, side, calibration)

    @staticmethod
    def _middle_point(p1, p2):
        """
        중심값 계산
        """
        x = int((p1.x + p2.x) / 2)
        y = int((p1.y + p2.y) / 2)
        return (x, y)

    def _isolate(self, frame, landmarks, points):
        """
        얼굴의 다른 부분이 없는 프레임을 가지도록 눈을 분리함

        인자값:
            frame (numpy.ndarray): 얼굴이 들어있는 프레임
            landmarks (dlib.full_object_detection): 얼굴 영역의 얼굴 랜드마크
            points (list): 68-landmark에서 눈 점
        """
        region = np.array([(landmarks.part(point).x, landmarks.part(point).y) for point in points])
        region = region.astype(np.int32)
        self.landmark_points = region

        # 눈만 나오게 mask 적용하기
        height, width = frame.shape[:2]
        black_frame = np.zeros((height, width), np.uint8)
        mask = np.full((height, width), 255, np.uint8)
        cv2.fillPoly(mask, [region], (0, 0, 0))
        eye = cv2.bitwise_not(black_frame, frame.copy(), mask=mask)

        # 눈만 자르기
        margin = 5
        min_x = np.min(region[:, 0]) - margin
        max_x = np.max(region[:, 0]) + margin
        min_y = np.min(region[:, 1]) - margin
        max_y = np.max(region[:, 1]) + margin

        self.frame = eye[min_y:max_y, min_x:max_x]
        self.origin = (min_x, min_y)

        height, width = self.frame.shape[:2]
        self.center = (width / 2, height / 2)

    def _analyze(self, original_frame, landmarks, side, calibration):
        """
        새 프레임에서 눈을 감지하고 분리하고 calibration한 데이터를 전송하고
        동공 객체를 초기화 함

        인자값:
            original_frame (numpy.ndarray): 사용자로부터 받은 프레임
            landmarks (dlib.full_object_detection): 얼굴 영역의 얼굴 랜드마크
            side: 왼쪽 눈(0), 오른쪽 눈(1) 구분자
            calibration (calibration.Calibration): 이진화된 threshold 값
        """
        if side == 0:
            points = self.LEFT_EYE_POINTS
        elif side == 1:
            points = self.RIGHT_EYE_POINTS
        else:
            return

        self._isolate(original_frame, landmarks, points)

        if not calibration.is_complete():
            calibration.evaluate(self.frame, side)

        threshold = calibration.threshold(side)
        self.pupil = Pupil(self.frame, threshold)
