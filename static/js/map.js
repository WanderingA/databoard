$(function(){
    initMap();
})


markers = [];
var map;

function initMap(){
    map = new BMapGL.Map("map_div");    // 创建Map实例
    map.enableScrollWheelZoom(true);     //开启鼠标滚轮缩放
    map.setDisplayOptions({poiText:false});   //关闭底图poi标注
    map.setDisplayOptions({poiIcon:false});   //关闭底图poi标注
    //var point = new BMapGL.Point(125.30078125, 43.87986755);  // 创建点坐标
    var convertor = new BMapGL.Convertor();
    var point = new BMapGL.Point(125.30078125, 43.87986755);


    var convertCallback = function (data) {
        if (data.status === 0) {
            var baiduLng = data.points[0].lng;
            var baiduLat = data.points[0].lat;
            // 在这里可以使用转换后的百度坐标进行其他操作
            map.centerAndZoom(new BMapGL.Point(baiduLng, baiduLat), 18);
            map.setHeading(180);   //设置地图旋转角度
            map.setTilt(53);       //设置地图的倾斜角度
            // console.log('转换后的百度坐标（BD-09）:', baiduLng, baiduLat);

        }
    };
    convertor.translate([point], 1, 5, convertCallback);
    //map.centerAndZoom(point, 19);                 // 初始化地图，设置中心点坐标和地图级别
    $.ajax({
        url: "/get_table_data",
        type: "get",
        dataType: "json",
        success: function (data) {
            data[0].forEach(function (item) {
                var point = new BMapGL.Point(item[2], item[3]);
                var convertCallback = function (data) {
                    if (data.status === 0) {
                        var baiduLng = data.points[0].lng;
                        var baiduLat = data.points[0].lat;
                        var points = new BMapGL.Point(baiduLng, baiduLat);
                        addMarker(points, item[1]);
                        // console.log('转换后的百度坐标（BD-09）:', baiduLng, baiduLat);
                    }
                };
                convertor.translate([point], 1, 5, convertCallback);
            });
        }
    });

    var point1 = new BMapGL.Point(125.3137079, 43.88759516);
    var myIcon1 = new BMapGL.Icon("../static/img/wrj.png", new BMapGL.Size(60, 70));
    var marker1 = new BMapGL.Marker(point1, {icon: myIcon1});  // 创建标记点
    map.addOverlay(marker1);  // 将标记点添加到地图中
    var path = [
        new BMapGL.Point(125.3137079, 43.88759516),
        new BMapGL.Point(125.3135079, 43.88739516),
        new BMapGL.Point(125.3133079, 43.88719516),
        new BMapGL.Point(125.3131079, 43.88739516),
        new BMapGL.Point(125.3133079, 43.88759516),
        new BMapGL.Point(125.3135079, 43.88779516),
        new BMapGL.Point(125.3137079, 43.88799516),
    ];
    function animateMarker(marker, path, duration) {
        var startTime = Date.now();
        var forward = true; // 标记是否正向移动

        function moveMarker() {
            var currentTime = Date.now();
            var elapsed = currentTime - startTime;
            var progress = elapsed / duration;

            if (progress >= 1) {
                forward = !forward; // 切换移动方向
                startTime = Date.now(); // 重置起始时间
                progress = 0; // 重置进度为0
            }

            var index;
            if (forward) {
                index = Math.floor(progress * (path.length - 1));
            } else {
                index = Math.floor((1 - progress) * (path.length - 1));
            }
            var point = path[index];
            marker.setPosition(point);

            requestAnimationFrame(moveMarker);

            if (progress === 0) {
                setTimeout(moveMarker, 2000); // 在移动完成后延迟2秒重新开始移动
            }
        }

        moveMarker();
    }

    animateMarker(marker1, path, 10000);
}



function addMarker(point, nodeID){
    var marker = new BMapGL.Marker(point);  // 创建标记点
    var icon = new BMapGL.Icon("../static/img/jiedian.png", new BMapGL.Size(30, 30));
    marker.setIcon(icon);

    marker.addEventListener("click", function () {
        // 点击标记点时的操作，可以自定义
        var infoWindow = new BMapGL.InfoWindow("经度："+point.lng + "<br>" + "纬度："+ point.lat + "<br>" + "事件：" + nodeID);
        map.openInfoWindow(infoWindow, point);
        //alert("事件：" + nodeID);
    });
    markers.push(marker);  // 将标记点添加到数组中
    map.addOverlay(marker);  // 将标记点添加到地图中
}
