$(function(){
    initMap();
})
//地图界面高度设置

function initMap(){
    var map = new BMapGL.Map("map_div");    // 创建Map实例
    var point = new BMapGL.Point(125.335116, 43.825);  // 创建点坐标
    map.centerAndZoom(point, 15);                 // 初始化地图，设置中心点坐标和地图级别
    map.enableScrollWheelZoom(true);     //开启鼠标滚轮缩放
    map.setHeading(64.5);   //设置地图旋转角度
    map.setTilt(73);       //设置地图的倾斜角度
    function addMarker(point){
        var iconUrl = '../static/img/jiedian.png'
        var iconSize = new BMapGL.Size(30, 30); // 设置自定义标注图标的尺寸
        var iconOptions = {
            imageSize: iconSize
        };
        var customIcon = new BMapGL.Icon(iconUrl, iconSize, iconOptions); // 创建自定义标注图标对象
        var marker = new BMapGL.Marker(point, {icon: customIcon});
        map.addOverlay(marker);
    }
    // 随机向地图添加25个标注
    var bounds = map.getBounds();
    var sw = bounds.getSouthWest();
    var ne = bounds.getNorthEast();
    var lngSpan = Math.abs(sw.lng - ne.lng);
    var latSpan = Math.abs(ne.lat - sw.lat);
    for (var i = 0; i < 25; i ++) {
        var point = new BMapGL.Point(sw.lng + lngSpan * (Math.random() * 0.7), ne.lat - latSpan * (Math.random() * 0.7));
        addMarker(point);
    }
}


