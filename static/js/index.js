
$(function () {
    char1();
    char2();
    char3();
});

//统计分析图
function char1() {
    var myChart = echarts.init(document.getElementById("char1"));
    var chartData = document.getElementById("char1").getAttribute("data-chart-data");
    chartData = JSON.parse(chartData);
    // chartData = JSON.parse(chartData | safe);
    var option = {
        tooltip: {
            trigger: "item",
            formatter: "{a} <br/>{b} : {c} ({d}%)",
        },
        legend: {
            orient: "vertical",
            x: "right",
            textStyle: {
                color: "#ffffff",
            },
            data: ["Aircraft", "Human", "Tracked", "Wheeled"],
        },
        series: [
            {
                name: "事件类型",
                type: "pie",
                radius: ["40%", "70%"],
                itemStyle: {
                    normal: {
                        label: {
                            show: false,
                        },
                        labelLine: {
                            show: false,
                        },
                    },
                    emphasis: {
                        label: {
                            show: true,
                            position: "center",
                            textStyle: {
                                fontSize: "20",
                                fontWeight: "bold",
                            },
                        },
                    },
                },
                data: chartData,
            },
        ],
    };

    myChart.setOption(option);
    window.addEventListener("resize", function () {
        myChart.resize();
    });
}

function char2() {
    var myChart = echarts.init(document.getElementById("char2"));
    var chartData = document.getElementById("char2").getAttribute("node_status");
    var data = JSON.parse(chartData);
    var option = {
        tooltip: {
            trigger: "axis",
            axisPointer: {
                type: "shadow",
            },
            formatter: function (params) {
                var tar = params[0];
                return tar.name + "<br/>" + tar.seriesName + " : " + tar.value;
            },
        },
        grid: {
            show: true,
            borderWidth: 0,
        },
        xAxis: {
            type: "category",
            data: ["正常", "GPS异常","检波器异常", "角度倾斜"],
            axisLabel: {
                show: true,
                textStyle: {
                    color: "#fff",
                },
            },
            splitLine: {
                lineStyle: {
                    width: 0,
                    type: "solid",
                },
            },
        },
        yAxis: {
            type: "value",
            axisLabel: {
                show: true,
                textStyle: {
                    color: "#fff",
                },
            },
            splitLine: {
                lineStyle: {
                    color: ["#f2f2f2"],
                    width: 0,
                    type: "solid",
                },
            },
        },

        series: [
            {
                name: "数量",
                type: "bar",
                stack: "总量",
                itemStyle: {
                    normal: {
                        label: {
                            show: true,
                            position: "inside",
                        },
                    },
                },
                data: data,
            },
        ],
    };

    myChart.setOption(option);
    window.addEventListener("resize", function () {
        myChart.resize();
    });
}

function char3() {
    var myChart = echarts.init(document.getElementById("char3"));

    var option = {
        grid: {
            show: true,
            borderWidth: 0,
        },
        tooltip: {
            trigger: "axis",
            axisPointer: {
                type: "shadow",
            },
            formatter: function (params) {
                var tar = params[0];
                return tar.name + "<br/>" + tar.seriesName + " : " + tar.value;
            },
        },
        xAxis: [
            {
                type: "category",
                splitLine: {
                    show: false,
                },
                data: ["人", "汽车", "履带车", "飞行器"],
                axisLabel: {
                    show: true,
                    textStyle: {
                        color: "#fff",
                    },
                },
            },
        ],
        yAxis: [
            {
                type: "value",
                splitLine: {
                    show: false,
                },
                axisLabel: {
                    show: true,
                    textStyle: {
                        color: "#fff",
                    },
                },
            },
        ],
        series: [
            {
                name: "出现次数",
                type: "bar",
                stack: "总量",
                itemStyle: {
                    normal: {
                        label: {
                            show: true,
                            position: "inside",
                        },
                    },
                },
                data: [320, 302, 301, 334],
            },
        ],
    };

    myChart.setOption(option);
    window.addEventListener("resize", function () {
        myChart.resize();
    });
}
