// 页面加载完成后执行初始化地图操作
$(function () {
    getHt();
    initMap();
    setInterval(initMap, 60000);
});

markers = [];
map = null;

function getHt() {
    var all_height = $(window).height();
    var div_height = all_height - 84;
    $("#car_control").css("height", div_height + "px");
    $("#map_box").css("height", div_height + "px");
}


function initMap() {
    map = new BMap.Map("map_box");
    // var point = new BMap.Point(convertCoordinate(125.30078125,43.87986755));  // 初始化地图中心点
    var convertor = new BMap.Convertor();
    var point = new BMap.Point(125.30078125, 43.87986755);
    var convertCallback = function (data) {
        if (data.status === 0) {
            var baiduLng = data.points[0].lng;
            var baiduLat = data.points[0].lat;
            // 在这里可以使用转换后的百度坐标进行其他操作
            map.centerAndZoom(new BMap.Point(baiduLng, baiduLat), 17);
            // console.log('转换后的百度坐标（BD-09）:', baiduLng, baiduLat);
        }
    };
    convertor.translate([point], 1, 5, convertCallback);
    // map.centerAndZoom(point, 17);  // 初始化地图缩放级别
    map.enableScrollWheelZoom(true);  // 启用鼠标滚轮缩放

    // 添加地图类型控件
    var size1 = new BMap.Size(10, 50);
    map.addControl(new BMap.MapTypeControl({
        offset: size1,
        mapTypes: [
            BMAP_NORMAL_MAP,
            BMAP_HYBRID_MAP
        ]
    }));
    $.ajax({
        url: "/get_table_data",
        type: "get",
        dataType: "json",
        success: function (data) {
            data[0].forEach(function (item) {
                var point = new BMap.Point(item[2], item[3]);
                var convertCallback = function (data) {
                    if (data.status === 0) {
                        var baiduLng = data.points[0].lng;
                        var baiduLat = data.points[0].lat;
                        var points = new BMap.Point(baiduLng, baiduLat);
                        addMarker(points, item[1]);
                        // console.log('转换后的百度坐标（BD-09）:', baiduLng, baiduLat);
                    }
                };
                convertor.translate([point], 1, 5, convertCallback);
            });
        }
    });
}

// 添加标记点
function addMarker(point, nodeID) {
    var marker = new BMap.Marker(point);  // 创建标记点
    var icon = new BMap.Icon("../static/img/jiedian.png", new BMap.Size(30, 30));
    marker.setIcon(icon);

    marker.addEventListener("click", function () {
        // 点击标记点时的操作，可以自定义
        alert("事件：" + nodeID);
    });
    markers.push(marker);  // 将标记点添加到数组中
    map.addOverlay(marker);  // 将标记点添加到地图中
}
