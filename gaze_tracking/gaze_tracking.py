from __future__ import division
import os
import cv2
import dlib
from .eye import Eye
from .calibration import Calibration


class GazeTracking(object):
    """
    사용자 시선추적 클래스 (눈, 동공의 좌표 감지)
    """

    def __init__(self):
        self.frame = None
        self.eye_left = None
        self.eye_right = None
        self.calibration = Calibration()

        # 얼굴 감지를 위해 _face_detector 사용
        self._face_detector = dlib.get_frontal_face_detector()

        # 주어진 랜드마크를 얻기 위해 _predictor 사용
        cwd = os.path.abspath(os.path.dirname(__file__))
        model_path = os.path.abspath(os.path.join(cwd, "trained_models/shape_predictor_68_face_landmarks.dat"))
        self._predictor = dlib.shape_predictor(model_path)

    @property
    def pupils_located(self):
        """동공의 위치 확인"""
        try:
            int(self.eye_left.pupil.x)
            int(self.eye_left.pupil.y)
            int(self.eye_right.pupil.x)
            int(self.eye_right.pupil.y)
            return True
        except Exception:
            return False

    def _analyze(self):
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        faces = self._face_detector(frame)

        try:
            landmarks = self._predictor(frame, faces[0])
            self.eye_left = Eye(frame, landmarks, 0, self.calibration)
            self.eye_right = Eye(frame, landmarks, 1, self.calibration)

        except IndexError:
            self.eye_left = None
            self.eye_right = None

    def refresh(self, frame):
        """프레임 새로고침 후 분석하기
        인자값 :
            frame (numpy.ndarray): 분석할 프레임
        """
        self.frame = frame
        self._analyze()

    def pupil_left_coords(self):
        """왼쪽 동공의 좌표값 리턴"""
        if self.pupils_located:
            x = self.eye_left.origin[0] + self.eye_left.pupil.x
            y = self.eye_left.origin[1] + self.eye_left.pupil.y
            return (x, y)

    def pupil_right_coords(self):
        """오른쪽 동공의 좌표값 리턴"""
        if self.pupils_located:
            x = self.eye_right.origin[0] + self.eye_right.pupil.x
            y = self.eye_right.origin[1] + self.eye_right.pupil.y
            return (x, y)

    def horizontal_ratio(self):
        """
        0.0 ~ 1.0 사이의 숫자 리턴
        왼쪽 = 0, 중심 = 0.5, 오른쪽 = 1
        
        """
        if self.pupils_located:
            pupil_left = self.eye_left.pupil.x / (self.eye_left.center[0] * 2 - 10)
            pupil_right = self.eye_right.pupil.x / (self.eye_right.center[0] * 2 - 10)
            return (pupil_left + pupil_right) / 2

    def is_right(self):
        if self.pupils_located:
            # return self.horizontal_ratio() <= 0.53
            return self.horizontal_ratio() <= 0.48
           
    def is_left(self):
        if self.pupils_located:
            # return self.horizontal_ratio() >= 0.70
            return self.horizontal_ratio() >= 0.77

    def is_center(self):
        if self.pupils_located:
            # return self.is_right() is not True and self.is_left() is not True
            return  self.horizontal_ratio() < 0.77 and self.horizontal_ratio() > 0.48
    def annotated_frame(self):
        """
        동공이 하이라이트 표시된 메인 프레임 리턴 (십자가 모양)
        """
        frame = self.frame.copy()
        if self.pupils_located:
            color = (0, 255, 0)
            x_left, y_left = self.pupil_left_coords()
            x_right, y_right = self.pupil_right_coords()
            cv2.line(frame, (x_left - 5, y_left), (x_left + 5, y_left), color)
            cv2.line(frame, (x_left, y_left - 5), (x_left, y_left + 5), color)
            cv2.line(frame, (x_right - 5, y_right), (x_right + 5, y_right), color)
            cv2.line(frame, (x_right, y_right - 5), (x_right, y_right + 5), color)

        return frame