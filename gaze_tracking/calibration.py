from __future__ import division
import cv2
from .pupil import Pupil


class Calibration(object):
    """
    사람 개인과 웹캠에 대한 최적의 이진화 threshold 값을 찾아 동공 감지 알고리즘 교정
    """

    def __init__(self):
        self.nb_frames = 20
        self.thresholds_left = []
        self.thresholds_right = []

    def is_complete(self):
        """calibration이 끝나면 true 리턴"""
        return len(self.thresholds_left) >= self.nb_frames and len(self.thresholds_right) >= self.nb_frames

    def threshold(self, side):
        """지정된 눈에 대한 threshold값 리턴

        인자값:
            side: 왼쪽 눈(0), 오른쪽 눈(1) 구분자
        """
        if side == 0:
            return int(sum(self.thresholds_left) / len(self.thresholds_left))
        elif side == 1:
            return int(sum(self.thresholds_right) / len(self.thresholds_right))

    @staticmethod
    def iris_size(frame):
        """
        눈 표면에서 동공이 차지하는 공간의 백분율을 리턴

        인자값:
            frame (numpy.ndarray): 이진화된 동공 프레임
        """
        frame = frame[5:-5, 5:-5]
        height, width = frame.shape[:2]
        nb_pixels = height * width
        nb_blacks = nb_pixels - cv2.countNonZero(frame)
        return nb_blacks / nb_pixels

    @staticmethod
    def find_best_threshold(eye_frame):
        """
        주어진 눈에 대한 프레임을 이진화하는 최적의 threshold 값 계산

        인자값:
            eye_frame (numpy.ndarray): 분석할 눈 프레임
        """
        average_iris_size = 0.48
        trials = {}

        for threshold in range(5, 100, 5):
            iris_frame = Pupil.image_processing(eye_frame, threshold)
            trials[threshold] = Calibration.iris_size(iris_frame)

        best_threshold, iris_size = min(trials.items(), key=(lambda p: abs(p[1] - average_iris_size)))
        return best_threshold

    def evaluate(self, eye_frame, side):
        """
        주어진 이미지를 고려하여 calibration 개선

        인자값:
            eye_frame (numpy.ndarray): 눈 프레임
            side: 왼쪽 눈(0), 오른쪽 눈(1) 구분자
        """
        threshold = self.find_best_threshold(eye_frame)

        if side == 0:
            self.thresholds_left.append(threshold)
        elif side == 1:
            self.thresholds_right.append(threshold)
