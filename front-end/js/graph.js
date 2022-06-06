const el = document.getElementById('chart');
    const data = {
    /* const exampledate='2022/05/01' 
    이런식으로 categories안에 변수로도 데이터 넣을 수 있음!*/
        categories: [
            '2022/05/01',
            '2022/05/02',
            '2022/05/03',
            '2022/05/04',
            '2022/05/05',
            '2022/05/06',
            '2022/05/07',
            '2022/05/08',
            '2022/05/09',
            '2022/05/10',
            '2022/05/11',
            '2022/05/12',
            '2022/05/13',
            '2022/05/14',
            '2022/05/15',
            '2022/05/16',
            '2022/05/17',
            '2022/05/18',
            '2022/05/19',
            '2022/05/20',
            '2022/05/21',
            '2022/05/22',
            '2022/05/23',
            '2022/05/24',
            '2022/05/25',
            '2022/05/26',
            '2022/05/27',
            '2022/05/28',
            '2022/05/29',
            '2022/05/30',
            '2022/05/31',
        ],
        series: [
            {
                name: 'Concentrate',
                data: [20, 40, 25, 50, 55, 45, 33, 34, 20, 67, 80, 13, 20, 40, 25, 50, 15, 45, 75, 47, 20, 30, 22, 13,20, 40, 25, 50, 15, 89, 33, 34, 20, 30, 22, 13 ],
            }
        ],
    };

    const options = {
        series: {
            /*그래프 확대 속성*/
            zoomable: true,
            /*그래프 버블 텍스트 속성*/
            dataLabels : {
                visible:true, offsetY:-10
            }
        },
    /*그래프 버블 텍스트 속성*/
        theme: {
            series: {
                dataLabels: {
                    fontFamily: 'monaco',
                    fontSize: 13,
                    fontWeight: 700,
                    useSeriesColor: true,
                    textBubble: {
                        visible: true,
                        arrow: {
                            visible: true,
                            width: 6,
                            height: 6,
                            direction: 'bottom'
                        }
                    }
                }
            }
        },
        /*그래프 차트 제목, x축, y축 속성*/ 
        chart: { title: 'Monthly Concentration', width: 800, height: 500 },
        xAxis: { 
            pointOnColumn: false, 
            title: { text: 'Date' },
            tick:{ interval: 6. },
            label:{ interval: 6, }, 
            date: { format: 'YY-MM-DD' }
        },
        yAxis: { 
            title: 'Concetration (%)',
            scale: {
                min: 0,
                max: 100,
                stepSize: 20,
            },
        },
        legend: {
            visible:false
        }
    };
const chart = toastui.Chart.areaChart({ el, data, options });