# example + video show (연주+지윤 합침)
# opencv web stream backend
import os # folder & file 관리
import sys
from flask import Flask, render_template, Response, url_for, redirect, session
import cv2
from numpy import concatenate, double
from gaze_tracking import GazeTracking
import datetime
import schedule

app = Flask(__name__)
gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
text = ""

app.secret_key = 'abcdefg'

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

def repeated_by_second01_set(gaze): # start check 용
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

def repeated_by_second01(gaze): # file write here
    """
    현재시각과 집중여부 출력
    """
    now=datetime.datetime.now()
    print(now)
    global tmp_concentrate_frame_cnt #집중이면 1, 비집중이면 0
    global f
    if gaze.is_center():
        print("concentrate")
        tmp_concentrate_frame_cnt=1
        # ----------- write data
        data = now.strftime('%H:%M:%S.%f') + " c\n"
        f.write(data)
    else:
        print("Unconcentrated")
        tmp_concentrate_frame_cnt=0
        # ----------- write data
        data = now.strftime('%H:%M:%S.%f') + " u\n"
        f.write(data)

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
    schedule.every(0.08).seconds.do(repeated_by_second01_set, gaze) #약 0.1초에 1개씩 출력하도록 스케줄링 (보통 1초에 9~12개)
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

def gen_frames_run(): # 프로그램 실행 + 데이터 파일에 저장 (file name = date)
    currentdir = os.getcwd() # 현재 이 파일이 있는 디렉토리 (이 디렉토리의 history folder에 데이터 저장)
    historydir = currentdir + "/history" #데이터 파일 넣을 디렉토리
    now = datetime.datetime.now()
    global f
    f = open(historydir + "/" + now.strftime('%Y-%m-%d_%H-%M-%S') + ".txt", 'w') # ../history/2022-05-31.txt 형태로 생성
    # --------------------------------------------파일 만들기--------------------------------------------------
    global frame
    global webcam
    webcam = cv2.VideoCapture(0)
    _, frame = webcam.read()
    schedule.every(0.08).seconds.do(repeated_by_second01, gaze) #약 0.1초에 1개씩 출력하도록 스케줄링 (보통 1초에 9~12개)
    print("시작시간 : ",end="")
    print_time()
    global frame_cnt
    global concentrate_frame_cnt
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
            # ----------- write data (마지막 줄 : 시간 + 집중도%)
            now = datetime.datetime.now()
            data = now.strftime('%H:%M:%S.%f') + " " + str(double(concentrate_frame_cnt/frame_cnt)*100)
            f.write(data)
            f.close()
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

@app.route('/calender', methods=['POST']) # calender로 보낼 정보(월별, 일별로 배열에 담아서..?)
def tocalender():
    if 'month_now' not in session: # session의 정보 비었다면
        current_time=datetime.datetime.now()
        month=current_time.strftime('%m') # 문자열로 월 저장
        session['current_time']=month # session에 지금 월 담음
        print(session['current_time'])
        
    currentdir = os.getcwd()
    historydir = currentdir + "/history"
    cnt = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
           -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
           -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1] # 집중도 cnt 31개
    color=[] # r - red, y - yellow, g - green, n - none
    file_list = os.listdir(historydir)
    for i in file_list:
        if i[5:7] == month: #지금 달
            day=int(i[8:10])
            day_index=day-1
            with open(historydir + "/" + i,'r') as f:
                # 파일 읽기
                lastline = f.readlines()[-1]
                concen = int(float(lastline.split()[1]))
                cnt[day_index-1]=cnt[day_index-1]+concen # cnt에 정확도 add
                
    for k in cnt:
        if k == -1:
            color.append('n')
        elif k >= 0 and k < 30:
            color.append('r')
        elif k >= 30 and k < 70:
            color.append('y')
        elif k >= 70:
            color.append('g')
    
    return render_template("calender.html", color = color)

@app.route('/daily')
def todaily():
    return render_template('daily.html')

@app.route('/graph', methods=['POST'])
def tograph():
    mday = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
           -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
           -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1] # 집중도 일 별(31개)
    mday_cnt = [0,0,0,0,0,0,0,0,0,0,
           0,0,0,0,0,0,0,0,0,0,
           0,0,0,0,0,0,0,0,0,0,0] # cnt 일 별
    conavg = 0 # 평균 집중도
    cntprogram = 0 # 실행 횟수
    conbest = 0 # 집중도 best 날짜(일)
    conworst = 100 # 집중도 worst 날짜(일)
    conbest_day = None
    conworst_day = None
    m = session['current_time'] # session month
    lastmonth = int(m) - 1 # 지난 달
    lastmonth_concen = 0
    lastmonth_cntprogram = 0
    currentdir = os.getcwd()
    historydir = currentdir + "/history"
    file_list = os.listdir(historydir)
    
    for i in file_list:
        if i[5:7] == m: #지금 달
            cntprogram+=1 # 실행 횟수 cnt
            with open(historydir + "/" + i,'r') as f:
                # 파일 읽기
                lastline = f.readlines()[-1]
                concen = int(float(lastline.split()[1]))
                if concen > conbest:
                    conbest = concen # 집중도 best
                    conbest_day = i[8:10]
                if concen < conworst:
                    conworst = concen # 집중도 worst
                    conworst_day = i[8:10]
                conavg += concen
                
                day_index = int(i[8:10])
                day_index-=1
                mday[day_index]+=concen
                mday_cnt[day_index]+=1 # 일 별 cnt +1
        elif i[5:7] == lastmonth: # 지난 달
            lastmonth_cntprogram+=1
            with open(historydir + "/" + i,'r') as f:
                # 파일 읽기
                lastline = f.readlines()[-1]
                concen = int(float(lastline.split()[1]))
                lastmonth_concen += concen
    conavg/=cntprogram # 평균 집중도
    if lastmonth_cntprogram == 0: # 0으로 나눌 수 없으니까
        lastmonth_concen = 0
    else:
        lastmonth_concen/=lastmonth_cntprogram # 지난 달 평균 집중도
    
    month_dif = conavg - lastmonth_concen
    # 일 별 그래프 저장(합친 거에 나누기 해서 일 별 평균 집중도)
    for n in range(len(mday_cnt)):
        if mday_cnt[n] != 0:
            mday[n]/=mday_cnt[n]
             
    return render_template('graph.html', mday=mday, conavg=conavg, cntprogram=cntprogram, conbest_day=conbest_day, conworst_day=conworst_day, month_dif=month_dif, )

@app.route('/program_run')
def torun():
    return render_template('program_run.html')

@app.route('/program_setting')
def tosetting():
    return render_template('program_setting.html')

@app.route('/program_terminate')
def toPterminate():
    return render_template('program_terminate.html')

@app.route('/terminate', methods=['POST'])
def letterminate():
    global f
    global frame_cnt
    global concentrate_frame_cnt
    print("종료시간 : ", end="")
    print_time()
    print("전체 프레임 수 : ", end="")
    print(frame_cnt)
    print("집중 프레임 수 : ", end="")
    print(concentrate_frame_cnt)
    print("집중도(%) : ", end="")
    print(double(concentrate_frame_cnt/frame_cnt)*100)
    # ----------- write data (마지막 줄 : 시간 + 집중도%)
    now = datetime.datetime.now()
    data = now.strftime('%H:%M:%S.%f') + " " + str(double(concentrate_frame_cnt/frame_cnt)*100)
    f.write(data)
    f.close()
    webcam.release()
    cv2.destroyAllWindows()
    return redirect(url_for('toPterminate')) 

if __name__ == "__main__": # start Flask server(5000번지)
    app.run(debug=True)