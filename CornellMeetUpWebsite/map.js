var map, marker, radius = 20;

function GetMap() {
  //Initialize a map instance.
  map = new atlas.Map('myMap', {
    view: 'Auto',

    // center: [-76.480132,42.447763],
    // bounds: [-76.487878,42.451176 ,-76.459641 ,42.442595],
    // maxBounds: [-76.498871,42.454015,-76.456354,42.438181],
    zoom: 1,
    renderWorldCopies: false,
    authOptions: {
      authType: 'subscriptionKey',
      subscriptionKey: 'EagCYfI95TLS8s0QVYUUaGhC-yI3TdnJA-K1KagP3AI'
    }
  });
  // map.setCamera({
  //    maxBounds:  [-76.498871,42.454015,-76.456354,42.438181],
  //    });

  //Wait until the map resources are ready.
  map.events.add('ready', function() {
    // //Create a HTML marker and add it to the map.
    marker = new atlas.HtmlMarker({
      htmlContent: '<img class="pulseIcon circleImage" alt="Html Marker" src="https://scontent.fagc3-1.fna.fbcdn.net/v/t39.30808-6/307483802_5493931864058602_2042803574326332288_n.jpg?_nc_cat=104&ccb=1-7&_nc_sid=09cbfe&_nc_ohc=GyQv2RNKbFAAX_G2dfA&_nc_oc=AQnglKqXqJpU3sgIfRtNwdzfPaT76NxyjGBRSGovHRC0KkNpSHoa5ioF1NX-gLBsQlM&_nc_ht=scontent.fagc3-1.fna&oh=00_AfC9-AukwUZbm_83gcSPplheLmSqXxbYKxLg4pyRy-AArA&oe=638737B8"/>',
      position: [-76.480132, 42.447763]
    });
    // marker2 = new atlas.HtmlMarker({
    //     htmlContent: '<img class="pulseIcon circleImage" alt="Html Marker" src="https://media-exp1.licdn.com/dms/image/C4E03AQHGLj1lKIoLLA/profile-displayphoto-shrink_800_800/0/1649639958797?e=1674691200&v=beta&t=WKOja5KyassK3RuVibvPX5jtoxb_uElakoxerM-5qXE"/>',
    //     position: [-76.480032,42.447763]
    // });
    map.markers.add(marker);
    // map.markers.add(marker2);
    //
    // //Start the animation.
    console.log("start animations");
    animateMarker(0);
    // animateMarker(marker2, 0);
    console.log("passed animations");
  });
}

function positionOnMap(username) {

  var longitude = getUserLocation(username);
  console.log("reached2");
  return [
    Math.cos(username) * 20,
    Math.sin(username) * 20
  ];

  // return [longitude, latitude];

}

function animateMarker(username) {
  //Update the position of the marker for the animation frame.
  marker.setOptions({
    position: positionOnMap(username / 1000)
  });
  console.log("reached");

  //Request the next frame of the animation.
  requestAnimationFrame(animateMarker);
}
