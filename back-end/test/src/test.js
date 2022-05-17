import React, { useState, useEffect, useRef } from "react";
import { Redirect } from "react-router-dom";
import Webcam from "react-webcam";

function initialCheck(){
    var checkStr;

    const [state, setState] = useState(0); //1이면 성공

    const initCheck = () => {
        const webcamRef = useRef();
        const checkByServer = () => {
            setTimeout(function(){
                fetch("http://localhost:/4000/setserver",{
                    method: "post",
                    headers:{
                        "content-type": "application/json",
                    },
                })
                .then((res) => res.json())
                .then((json) => {
                    checkStr = json.text;
                });
            }, 1000);

            if(checkStr == "Looking center") {
                console.log("시작");
                setState(1);
                window.localStorage.setItem("start","true");

                clearInterval(interval);
            }
            else setState(0);
        };
    };

    useEffect(()=>{
        interval = setInterval(()=>{
            
        })

        const videoConstraints = {
            width: 1280,
            height: 720,
            facingMode: "user",
        };

        return(
            <div>
                <Webcam
                    audio={false}
                    ref={webcamRef}
                    mirrored={true}
                    videoConstraints={videoConstraints}
                    height={0.5 * `${window.innerHeight}`}
                    width={0.8 * `${window.innerWidth}`}
                />
            </div>
        );
    });

    return(
        <div>
            {
                //초기 설정 성공하면 실행 화면으로 넘어감
                window.localStorage.getItem("start") == "true" && (
                    <Redirect to={{ pathname: "/testserver.html"}}/>
                )
            }
        </div>
    )
}

export default initialCheck;