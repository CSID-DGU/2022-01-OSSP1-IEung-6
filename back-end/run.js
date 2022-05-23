const express = require("express");
const cors = require("cors"); //다른 사이트(front)에서 나의 서버에 요청하는 것 허가
const bodyParser=require("body-parser"); //post request data의 body로부터의 파라미터 편리하게 추출
const app = express();
const port = 4001; //포트 num

app.use(bodyParser.urlencoded({extended: false}));
app.use(bodyParser.json());
app.use(cors());

app.post("/setserver",(req,res)=>{
    const {spawn} = require("child_process"); //다른 파일 돌리기
    const checkpy = spawn("python", ["../example.py"]); //python ../example.py 수행됨    
    resultStr = ""; //save result

    console.log("program run 서버 시작");

    checkpy.stdout.on("data",(stdData)=>{ //stdout data stream start
        console.log(stdData.toSting()); //실행 결과
        resultStr += stdData.toString();
    });

    checkpy.stdout.on('data',()=>{ //stdout data stream end
        let resultData = JSON.parse(resultStr); //parse string 2 JSON
        res.send(resultData); //res send
    });
});

app.listen(port, () => { //server open
    console.log(`start server on ${port}`);
});