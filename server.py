# window 창 뜨는 거 지워도 되는데 나중에 최종 전에 지워주삼~~
# 영상 크기 조정 필요함

# ////////////////////////////////////////////////////////////
# example + video show (연주+지윤 합침)
# opencv web stream backend
import sys
from flask import Flask, render_template, Response, redirect, url_for
import cv2
from numpy import concatenate, double
from gaze_tracking import GazeTracking
import datetime
import schedule

app = Flask(__name__)
gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
text = ""

def show_webcam(gaze, frame):
    """
    화면에 웹캠과 집중여부를 실시간으로 띄워줌
    """
    _, frame = webcam.read()
    returnFrame = frame
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
    return returnFrame

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

def print_time():
    """
    하나의 레포트 시작시간, 종료시간 기록용
    """
    now=datetime.datetime.now()
    print(now)

def startcheck(tmp_concentrate_frame_cnt):
    """
    시작 서버용 (일단은 30프레임동안 연속해서 집중으로 뜨면 초기 설정 완료)
    """
    global check_sum
    if tmp_concentrate_frame_cnt == 1: # 집중
        check_sum+=1
    else:
        check_sum=0
    
    return check_sum
    

def gen_frames_set(): # 프로그램 초기 설정
    global frame
    global webcam
    webcam = cv2.VideoCapture(0)
    _, frame = webcam.read()
    schedule.every(0.08).seconds.do(repeated_by_second01, gaze) #약 0.1초에 1개씩 출력하도록 스케줄링 (보통 1초에 9~12개)
    print("시작시간 : ",end="")
    print_time()
    frame_cnt=0
    concentrate_frame_cnt=0
    global check_sum # sum이 30 되면 초기 설정 완료 
    check_sum = 0
    while True:
        frame = show_webcam(gaze, frame)
        schedule.run_pending() #위에서 스케줄링 한 시간마다 수행
        frame_cnt+=1 # 위 함수 수행할 때마다 프레임증가
        concentrate_frame_cnt+=tmp_concentrate_frame_cnt #global 변수로 선언한 집중 프레임수 더하기
        
        global check30
        check30 = startcheck(tmp_concentrate_frame_cnt)
        if check30 == 30: # 초기 설정 완료 -> 화면에 완료 표시 하기
            font = cv2.FONT_HERSHEY_SIMPLEX
            puttxt = "Done Setting !!"
            cv2.putText(frame, puttxt,(60, 250),font, 2, (255, 0, 0), 3)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("종료시간 : ", end="")
            print_time()
            print("전체 프레임 수 : ", end="")
            print(frame_cnt)
            print("집중 프레임 수 : ", end="")
            print(concentrate_frame_cnt)
            print("집중도(%) : ", end="")
            print(double(concentrate_frame_cnt/frame_cnt)*100)
            break
        
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield(b'--frame\r\n' 
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        if check30 == 30:
            break
    webcam.release()
    cv2.destroyAllWindows()

def gen_frames_run(): # 프로그램 실행
    global frame
    global webcam
    webcam = cv2.VideoCapture(0)
    _, frame = webcam.read()
    schedule.every(0.08).seconds.do(repeated_by_second01, gaze) #약 0.1초에 1개씩 출력하도록 스케줄링 (보통 1초에 9~12개)
    print("시작시간 : ",end="")
    print_time()
    frame_cnt=0
    concentrate_frame_cnt=0
    while True:
        frame = show_webcam(gaze, frame)
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
            print("집중도(%) : ", end="")
            print(double(concentrate_frame_cnt/frame_cnt)*100)
            break
        
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield(b'--frame\r\n' 
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    webcam.release()
    cv2.destroyAllWindows()

@app.route('/') # localhost:5000
def tomain():
    return render_template('main.html')

@app.route('/video_show_set') # returns streaming response
def video_show_set():
    return Response(gen_frames_set(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_show_run') # returns streaming response
def video_show_run():
    return Response(gen_frames_run(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/calender')
def tocalender():
    return render_template('calender.html')

@app.route('/daily')
def todaily():
    return render_template('daily.html')

@app.route('/graph')
def tograph():
    return render_template('graph.html')

@app.route('/program_run')
def torun():
    return render_template('program_run.html')

@app.route('/program_setting')
def tosetting():
    return render_template('program_setting.html')

if __name__ == "__main__": #start Flask server(5000번지)
    app.run(debug=True)