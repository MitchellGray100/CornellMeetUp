const express = require("express");
const bodyParser = require("body-parser");
const https = require("https");
const ejs = require("ejs");

const app = express();
app.use(bodyParser.urlencoded({
  extended: true
}));
app.use('*/css', express.static(__dirname + '/css'));
app.use('*/js', express.static(__dirname + '/js'));
app.use('*/images', express.static(__dirname + '/images'));
app.engine('html', require('ejs').renderFile);
app.set('view engine', 'html');
app.set('views', __dirname);


app.get("/", function(req, res) {
  res.redirect("/sign-in");
})

app.get("/register", function(req, res) {
  res.sendFile(__dirname + "/register.html");

})

app.get("/sign-in", function(req, res) {

  res.sendFile(__dirname + "/index.html");
  // const url = "https://api.kanye.rest";
  //
  // https.get(url, function(response)
  // {
  //   console.log(response.statusCode);
  //   response.on("data", function(data){
  //     const output = JSON.parse(data);
  //     console.log(output);
  //   })
  // })
  // console.log(__dirname);
})

app.post("/map", function(req, res) {
  var username = req.body.username;
  res.render(__dirname + "/map.html", {
    username: username
  });
})

app.get("/map", function(req, res) {
  var username = req.body.username;
  res.render(__dirname + "/map.html", {
    username: username
  });
})

const options = {
  method: 'POST'
}


// var postData = JSON.stringify({
//   "id": "bruh_bob_jr",
//   "last-online": "11/30/22",
//   "groups": [1, 2],
//   "info": {
//     "birthday": "11/01/20",
//     "time-zone": "EST",
//     "profile-picture-id": "https://img.bleacherreport.net/img/images/photos/002/169/316/hillbillyjim0_crop_exact.jpg?w=423&h=281&q=75"
//   }
// });
app.post("/create-user", function(req, res) {
  var list = req.body.groups.split(",");
  var groupList = [];

  for(var i = 0; i < list.length; i++)
  {
    groupList.push(parseInt(list[i]));
  }

  // console.log(req.body);
  var url = "https://cornellmeetup.azurewebsites.net/api/userinfo?type=add";
  var postData = JSON.stringify({
    "id": "users_"+req.body.username,
    "password": req.body.password,
    "last-online": "11/30/22",
    "groups": groupList,
    "info": {
      "birthday": req.body.birthday,
      "time-zone": req.body.timezone,
      "profile_picture_id": req.body.pfp
    }
  });


  console.log("postData: " + postData);
  var request = https.request(url, options, function(response) {
    res.on('data', d => {
      process.stdout.write(d);
    })
    console.log(response);
  })
  request.on('error', (e) => {
    console.error(e);
  });
  request.write(postData);
  request.end();


  for(var i = 0; i < groupList.length; i++)
  {
    var url = "https://cornellmeetup.azurewebsites.net/api/groupinfo?type=addmember&groupname="+groupList[i]+"&username="+req.body.username;

    var request = https.request(url, function(response) {
      res.on('data', d => {
        process.stdout.write(d);
      })
      console.log(response);
    })
    request.on('error', (e) => {
      console.error(e);
    });
    request.write(postData);
    request.end();
  }

  // var username = req.body.username;
  // res.render(__dirname + "/map.html", {
  //   username: username
  // });

  var locationPostData = JSON.stringify({
    "longitude": 0,
    "latitude": 0
  });

  var url = "https://cornellmeetup.azurewebsites.net/api/locationinfo?type=add&username=" + req.body.username;
  var request = https.request(url, options, function(response) {
    res.on('data', d => {
      process.stdout.write(d);
    })
    // console.log(response);
  })
  request.on('error', (e) => {
    console.error(e);
  });
  request.write(locationPostData);
  request.end();

  res.redirect("/sign-in");
  // res.sendFile(__dirname + "/map.html", {username:username});
  // const url = "https://api.kanye.rest";
  //
  // https.get(url, function(response)
  // {
  //   console.log(response.statusCode);
  //   response.on("data", function(data){
  //     const output = JSON.parse(data);
  //     console.log(output);
  //   })
  // })
  // console.log(__dirname);
})
//
// app.post("/", function(req, res) {
//   var num1 = Number(req.body.num1);
//   var num2 = Number(req.body.num2);
//
//   var result = num1 + num2;
//   res.write("<p>Result is:");
//   res.write(String(result));
//
//   // res.send("Result is: " + result);
//   res.send();
// });
app.listen(3000, function() {
  console.log("Server started on port 3000");
});

function getUserLocation(username) {
  console.log("called method using: " + String(username));
}
