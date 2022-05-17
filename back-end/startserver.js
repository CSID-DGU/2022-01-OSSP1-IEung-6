//시작 자세 체크 서버(program_setting.html과 연결, 이후에 프론트 담당이 react로 구현)
//program_setting.html에서 post를 보내야 함. -> 이후에 서버 작동
const express = require("express");
const cors = require("cors"); //다른 사이트(front)에서 나의 서버에 요청하는 것 허가
const bodyParser = require("body-parser"); //post request data의 body로부터의 파라미터 편리하게 추출
const app = express();
const port = 4000; //포트 num

app.use(bodyParser.urlencoded({extended: false}));
app.use(bodyParser.json());
app.use(cors());

app.post("/setserver",(req,res)=>{
    const {spawn} = require("child_process"); //다른 파일 돌리기
    const checkpy = spawn("python", ["../example.py"]); //python ../example.py 수행됨    
    const sendText = {text: ""};

    console.log("초기 자세설정 서버 시작");

    checkpy.stdout.on("data",(data)=>{ //stdout data stream start
        console.log(data.toString()); //실행 결과 console 출력
        sendText.text = data.toString();
        res.send(sendText);
    });

    checkpy.stderr.on('data', (data) => { //에러
        console.log(data.toString());
    });
});

app.listen(port, () => { //server open
    console.log(`start server on ${port}`);
});