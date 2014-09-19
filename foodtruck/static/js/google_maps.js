(function() {

    var geocoder = new google.maps.Geocoder();
    var currentLocation = "";
    var markers = [];

    function addMarker(location, foodtruck) {
        var shape = {
            coords: [1, 1, 1, 16, 14, 16, 14 , 1],
            type: 'poly'
        };

        var image = {
            url: 'static/images/foodtruck.png',
            size: new google.maps.Size(16, 16),
            origin: new google.maps.Point(0,0),
            anchor: new google.maps.Point(0, 16)
        };

        var marker = new google.maps.Marker({
            position: location,
            icon: image,
            shape: shape,
            map: map
        });

        google.maps.event.addListener(marker, 'click', function() {
            address=foodtruck['address'];
            block=foodtruck['block'];
            lot=foodtruck['lot'];
            schedule=foodtruck['schedule'];
            html = ["<div id='foodtruck'><div id='location'><div>",
                    address, "</div>", "<div>", "block: ", block,
                    " lot: ", lot, "</div>", "</div>", "<a href=",
                    schedule, ">schedule</a>", "</div>"].join("");
            document.getElementById("info-panel").innerHTML = html;
        });

        markers.push(marker);
    }

    function setAllMap(map) {
        for (var i = 0; i < markers.length; i++) {
            markers[i].setMap(map);
        }
    }

    function deleteMarkers() {
        document.getElementById('info-panel').innerHTML = "";
        clearMarkers();
        markers = [];
    }

    function clearMarkers() {
        setAllMap(null);
    }

    function getFoodtrucks(pos) {
        lat = pos.lat().toFixed(3);
        lng = pos.lng().toFixed(3);
        radius = 250;
        api_path = "get_nearby_foodtrucks" +
                   "/" + lat.toString() +
                   "/" + lng.toString() +
                   "/" + radius.toString();

        var xhr = new XMLHttpRequest();
        xhr.open("GET", api_path, false);
        xhr.send();

        var foodtrucks = JSON.parse(xhr.responseText);
        return foodtrucks
    }

    function setMarkers(map, foodtrucks) {
        for (var key in foodtrucks) {
            var pos = key.split(":");
            var myLatLng = new google.maps.LatLng(pos[0], pos[1]);
            addMarker(myLatLng, foodtrucks[key]);
        }
    }

    function setFoodtrucks(pos) {
        var foodtrucks = getFoodtrucks(pos);
        setMarkers(map, foodtrucks);
    }

    function updateMarkerPosition() {
        document.getElementById('info-panel').innerHTML = "";
        deleteMarkers();
    }

    var lat = 37.791;
    var lng = -122.393;
    var myLocation = new google.maps.LatLng(lat, lng);

    var mapOptions = {
        center: new google.maps.LatLng(37.791, -122.393),
        zoom: 15,
    };
    var map = new google.maps.Map(document.getElementById("map-canvas"),
        mapOptions);

    var marker = new google.maps.Marker({
        position: myLocation,
        map: map,
        draggable: true,
        title:"set your location here"
    });

    // Update current position info.
    updateMarkerPosition(myLocation);
    setFoodtrucks(myLocation);

    google.maps.event.addListener(marker, 'drag', function() {
        deleteMarkers();
    });

    google.maps.event.addListener(marker, 'dragend', function() {
        pos = marker.getPosition();
        setFoodtrucks(pos);
    });

})();
