import sys #연주
import cv2
from numpy import concatenate, double
from gaze_tracking import GazeTracking
import datetime
import schedule

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
frame = webcam.read()
text = ""

def show_webcam(gaze, frame):
    """
    화면에 웹캠과 집중여부를 실시간으로 띄워줌
    """
    _, frame = webcam.read()
    gaze.refresh(frame)
    frame = gaze.annotated_frame()
    if gaze.is_center():
        text = "concentrate"
    # 만약 중앙으로 보는 것으로 인식했다면 결과 stdout에 print and release   
        sys.stdout.flush()

    else:
        text="Unconcentrated"
    cv2.putText(frame, text, (20, 60), cv2.FONT_HERSHEY_DUPLEX, 1.0, (147, 58, 31), 2)
    cv2.putText(frame, "horizontal : "+str(gaze.horizontal_ratio()), (20, 90), cv2.FONT_HERSHEY_DUPLEX, 1.0, (147, 58, 31), 2)
    
    left_pupil = gaze.pupil_left_coords()
    right_pupil = gaze.pupil_right_coords()
    cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 140), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
    cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 185), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

    cv2.imshow("Detect Concentration", frame)
def repeated_by_second01(gaze):
    """
    현재시각과 집중여부 출력
    """
    now=datetime.datetime.now()
    print(now)
    global tmp_concentrate_frame_cnt #집중이면 1, 비집중이면 0
    if gaze.is_center():
        print("concentrate")
        tmp_concentrate_frame_cnt=1
    else:
        print("Unconcentrated")
        tmp_concentrate_frame_cnt=0
schedule.every(0.08).seconds.do(repeated_by_second01, gaze) #약 0.1초에 1개씩 출력하도록 스케줄링 (보통 1초에 9~12개)

def print_time():
    """
    하나의 레포트 시작시간, 종료시간 기록용
    """
    now=datetime.datetime.now()
    print(now)


print("시작시간 : ",end="")
print_time()
frame_cnt=0
concentrate_frame_cnt=0
while True:
    show_webcam(gaze, frame)
    schedule.run_pending() #위에서 스케줄링 한 시간마다 수행
    frame_cnt+=1 # 위 함수 수행할 때마다 프레임증가
    concentrate_frame_cnt+=tmp_concentrate_frame_cnt #global 변수로 선언한 집중 프레임수 더하기
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("종료시간 : ", end="")
        print_time()
        print("전체 프레임 수 : ", end="")
        print(frame_cnt)
        print("집중 프레임 수 : ", end="")
        print(concentrate_frame_cnt)
        print("집중도 (집중 프레임수 / 전체 프레임 수) : ", end="")
        print(double(concentrate_frame_cnt/frame_cnt))
        break 
webcam.release()
cv2.destroyAllWindows()