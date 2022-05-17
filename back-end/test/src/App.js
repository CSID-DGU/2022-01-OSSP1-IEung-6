/*
import logo from './logo.svg';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default App;
*/
import React, { useEffect } from "react";
import { Navigate } from "react-router-dom";
import Webcam from "react-webcam";

var count = 1;

function InitialCheck(){
    var checkStr;
    var states = 0;
    var interval;

    const InitCheck = () => {
        const connectServer = () => {
             setTimeout(function(){
               fetch("http://localhost:4000/setserver",{
                   method: "post",
                   headers:{
                       "content-type": "application/json",
                   },
               })
               .then((res) => res.json())
               .then((json) => {
                   checkStr = json.text;
               });
             }, 10);
           if(checkStr[0] == "1" && count) {
             console.log("시작");
             states = 1;
             window.localStorage.setItem("start","true");
             
             clearInterval(interval);
             count = 0;
           }
           else states = 0;
        };

    useEffect(()=>{
        interval = setInterval(()=>{
          connectServer();
        }, 10000);
    }, []);
  }
    const videoConstraints = {
      width: 1280,
      height: 720,
      facingMode: "user",
    };

    return(
      <div>
        <InitCheck />
          <div>
              <Webcam
                  audio={false}
                  //ref={webcamRef}
                  mirrored={true}
                  videoConstraints={videoConstraints}
                  height={0.5 * `${window.innerHeight}`}
                  width={0.8 * `${window.innerWidth}`}
              />
            </div>
        <div>
            {
                //초기 설정 성공하면 실행 화면으로 넘어감
                window.localStorage.getItem("start") === "true" && (
                    <Navigate to={{ pathname: "./testserver.html"}}/>
                )
            }
        </div>
        </div>
    );
}

export default InitialCheck;