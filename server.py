# example + video show (연주+지윤 합침)
# opencv web stream backend
import os # folder & file 관리
import sys
from flask import Flask, render_template, Response, url_for, redirect, session, request
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

    # cv2.imshow("Detect Concentration", frame)
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
        try:
            f.write(data)
        except ValueError:
            print("I/O operation on closed file---")
    else:
        print("Unconcentrated")
        tmp_concentrate_frame_cnt=0
        # ----------- write data
        data = now.strftime('%H:%M:%S.%f') + " u\n"
        try:
            f.write(data)
        except ValueError:
            print("I/O operation on closed file---")

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
    global concentrate_frame_cnt
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
        #frame = show_webcam(gaze, frame)
        _, frame = webcam.read()
        gaze.refresh(frame)
        frame = gaze.annotated_frame()
        if gaze.is_center():
            text = "Concentrate"
        # 만약 중앙으로 보는 것으로 인식했다면 결과 stdout에 print and release   
            sys.stdout.flush()
        else:
            text="Unconcentrate"
        cv2.putText(frame, text, (520, 470), cv2.FONT_HERSHEY_DUPLEX, 0.7, (147, 58, 31), 2)
        # -----------
        schedule.run_pending() #위에서 스케줄링 한 시간마다 수행
        frame_cnt+=1 # 위 함수 수행할 때마다 프레임증가
        concentrate_frame_cnt+=tmp_concentrate_frame_cnt #global 변수로 선언한 집중 프레임수 더하기
        
        global check30
        check30 = startcheck(tmp_concentrate_frame_cnt)
        if check30 == 30: # 초기 설정 완료 -> 화면에 완료 표시 하기
            font = cv2.FONT_HERSHEY_SIMPLEX
            puttxt = "Done Setting !!"
            cv2.putText(frame, puttxt,(70, 60),font, 2, (255, 0, 0), 3)
        
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
    # cv2.destroyAllWindows()

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
        #frame = show_webcam(gaze, frame)
        _, frame = webcam.read()
        gaze.refresh(frame)
        frame = gaze.annotated_frame()
        if gaze.is_center():
            text = "Concentrate"
        # 만약 중앙으로 보는 것으로 인식했다면 결과 stdout에 print and release   
            sys.stdout.flush()
        else:
            text="Unconcentrate"
        cv2.putText(frame, text, (520, 470), cv2.FONT_HERSHEY_DUPLEX, 0.7, (147, 58, 31), 2)
        # -----------
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
    # cv2.destroyAllWindows()

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
    # txt 파일 목록 저장
    currentdir = os.getcwd()
    historydir = currentdir + "/history"
    file_list = os.listdir(historydir)
    # test - 6월 txt 파일 목록 저장
    monthly_file_list = list()
    for i in file_list:
        if (i[5:7] == '06'): # hard coding 수정
            monthly_file_list.append(i)
    # calender 존재 날짜 및 집중도 저장
    calender_file_list = list()
    cct_list = list()
    for i in monthly_file_list:
        with open(historydir + "/" + i,'r') as f:
                lastline = f.readlines()[-1]
                cct = round(float(lastline.split()[1]), 1) # 집중도
        if len(calender_file_list) == 0:
            calender_file_list.append(i[8:10])
            result_cct = cct
            num = 1
        else:
            if (calender_file_list[-1]) != i[8:10]:
                calender_file_list.append(i[8:10])
                cct_list.append(result_cct / num)
                result_cct = cct
                num = 1
            else:
                result_cct += cct
                num += 1
    cct_list.append(result_cct / num) 
    color_list = ['0' for i in range(32)]
    for i in range(len(calender_file_list)):
        if cct_list[i] >= 70:
            color_list[int(calender_file_list[i])] = 'g'
        elif cct_list[i] >= 30:
            color_list[int(calender_file_list[i])] = 'y'
        else:
            color_list[int(calender_file_list[i])] = 'r'
    
    return render_template("calender.html", color_list = color_list)
    
@app.route('/daily')
def todaily():
    # 전송된 삭제 파일 및 날짜 저장
    if request.args.getlist('delete'):
        delete_list = request.args.getlist('delete')
        for i in delete_list:
            d_file = 'history/' + i
            if os.path.isfile(d_file):
                os.remove(d_file)
    if request.args.get('data'):
        data = request.args.get('data')
        if len(data) == 1:
            data = '0' + data
    
    # txt 파일 목록 저장
    currentdir = os.getcwd()
    historydir = currentdir + "/history"
    file_list = os.listdir(historydir)
    # test - 해당 날짜 txt 파일 목록 저장
    daily_file_list = list()
    for i in file_list:
        if (i[5:7] == '06') and (i[8:10] == data): # hard coding 수정
            daily_file_list.append(i)
              
    # txt 파일로부터 집중도 읽어오기
    sum_cct = 0
    sum_time = 0
    cal_time = 0
    cct_list = list() # 집중도
    time_list = list() # 실행시간
    worst_cct = 100
    date = '2022 06 ' + data # hard coding 수정
    num = len(daily_file_list) # 파일 수
    for i in daily_file_list:
        with open(historydir + "/" + i,'r') as f:
            lastline = f.readlines()[-1]
            # 실행 시간 계산
            time_s = list()
            time_f = list()
            time_s.append(int(i[11:13])) # index 0 h
            time_s.append(int(i[14:16])) # index 1 m
            time_s.append(int(i[17:19])) # index 2 s
            time_f.append(int(lastline[0:2])) # index 0 h
            time_f.append(int(lastline[3:5])) # index 1 m
            time_f.append(int(lastline[6:8]))  # index 2 s
            start = time_s[0] * 60 * 60 + time_s[1] * 60 + time_s[2]
            finish = time_f[0] * 60 * 60 + time_f[1] * 60 + time_f[2]
            time = finish - start
            sum_time += time
            time_list.append(time)
            cct = round(float(lastline.split()[1]), 1) # 집중도
            if cct < worst_cct:
                worst_cct = cct
                worst_time = lastline[0:8]
                worst_log = i[11:19]
            cct_list.append(cct)
            sum_cct += cct
    
    for i in range(len(cct_list)):
        cal_time += cct_list[i] * time_list[i]
    result_cct = round(cal_time / sum_time, 1)
    # 집중도별 색상 지정
    if result_cct >= 70:
        color = 'g'
    elif result_cct >= 30:
        color = 'y'
    else:
        color = 'r'
    
    return render_template('daily.html', result_cct = result_cct, cct = cct_list, time = time_list, color = color,
                           date = date, num = num, w_cct = worst_cct, w_time = worst_time, w_log = worst_log, d_list = daily_file_list)


@app.route('/graph', methods=['POST'])
def tograph():
    # txt 파일 목록 저장
    currentdir = os.getcwd()
    historydir = currentdir + "/history"
    file_list = os.listdir(historydir)
    # test - 6월 txt 파일 목록 저장
    monthly_file_list = list()
    prev = list()
    for i in file_list:
        if (i[5:7] == '06'): # hard coding 수정
            monthly_file_list.append(i)
        if (i[5:7] == '05'): # hard coding 수정
            prev.append(i)
    # 집중도 계산
    date_list = list()
    cct_list = list()
    time_list = list()
    best_list = list()
    worst_list = list()
    sum_time = 0
    sum_cct_prev = 0
    result_cct = 0
    best_cct = 0
    worst_cct = 100
    b_cct = 0.0
    w_cct = 100.0
    best_date = ''
    worst_date = ''
    month = '6'
    num = len(monthly_file_list)
    num_prev = len(prev)
    # 이번 달 집중도 계산
    temp = ''
    for i in monthly_file_list:
        if temp == '':
            date_list.append(i[0:10])
        elif temp != i[0:10]:
            date_list.append(i[0:10])
            result_cct = round(result_cct / sum_time, 1)
            cct_list.append(result_cct)
            best_list.append(b_cct)
            worst_list.append(w_cct)
            b_cct = 0.0
            w_cct = 100.0
            time_list = list()
            sum_time = 0
            result_cct = 0
            if best_cct < cct:
                best_cct = cct
                best_date = i[8:10]
            if worst_cct > cct:
                worst_cct = cct
                worst_date = i[8:10]
        with open(historydir + "/" + i,'r') as f:
            lastline = f.readlines()[-1]
            cct = round(float(lastline.split()[1]), 1) # 집중도
            if b_cct < cct:
                b_cct = cct
            if w_cct > cct:
                w_cct = cct
            time_s = list()
            time_f = list()
            time_s.append(int(i[11:13])) # index 0 h
            time_s.append(int(i[14:16])) # index 1 m
            time_s.append(int(i[17:19])) # index 2 s
            time_f.append(int(lastline[0:2])) # index 0 h
            time_f.append(int(lastline[3:5])) # index 1 m
            time_f.append(int(lastline[6:8]))  # index 2 s
            start = time_s[0] * 60 * 60 + time_s[1] * 60 + time_s[2]
            finish = time_f[0] * 60 * 60 + time_f[1] * 60 + time_f[2]
            time = finish - start
            sum_time += time
            time_list.append(time)
            result_cct += time * cct
        temp = i[0:10]
    best_list.append(b_cct)
    worst_list.append(w_cct)
    result_cct = round(result_cct / sum_time, 1)
    cct_list.append(result_cct)
    result_cct = 0
    for i in cct_list:
        result_cct += i
    result_cct = round(result_cct / len(cct_list), 1)
    l = len(date_list)
    # 지난 달 집중도 계산
    for i in prev:
        with open(historydir + "/" + i,'r') as f:
            lastline = f.readlines()[-1]
            cct = round(float(lastline.split()[1]), 1) # 집중도
            sum_cct_prev += cct
    prev_cct = sum_cct_prev / num_prev
    prev_cct = round(prev_cct, 1)
    sub_cct = result_cct - prev_cct
    if sub_cct < 0:
        color = 'b'
    else:
        color = 'r'
    return render_template('graph.html', month = month, cct = result_cct, num = num, cct_b = best_cct, cct_w = worst_cct,
                           date_b = best_date, date_w = worst_date, sub = sub_cct, color = color, date = date_list,
                           cct_list = cct_list, l = l, b_cct = best_list, w_cct = worst_list)

@app.route('/program_run')
def torun():
    return render_template('program_run.html')

@app.route('/program_setting')
def tosetting():
    return render_template('program_setting.html')

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
    #cv2.destroyAllWindows()
    return render_template('program_terminate.html')

@app.errorhandler(404) # error 404 페이지 커스텀
def notfound_error(error):
    return render_template('errorshow.html')

if __name__ == "__main__": # start Flask server(5000번지)
    app.run(debug=True)