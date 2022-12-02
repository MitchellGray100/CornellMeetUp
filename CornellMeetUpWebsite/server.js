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

var globalUsername ="";

app.get("/", function(req, res) {
  console.log(globalUsername)
  res.redirect("/sign-in");
})

app.post("/profile", function(req, res) {
  console.log(globalUsername)
  res.render(__dirname + "/profile.html", {
    username: globalUsername
  });
})

app.get("/register", function(req, res) {
  res.sendFile(__dirname + "/register.html");
})

app.get("/sign-in", function(req, res) {
  res.sendFile(__dirname + "/index.html");
})

app.get("/failed-login", function(req, res) {
  res.sendFile(__dirname + "/failed-login.html");
})

app.get("/failed-register", function(req, res) {
  res.sendFile(__dirname + "/failed-register.html");
})

app.post("/check-username", function(req, res) {
  var apiUrl = "https://cornellmeetup.azurewebsites.net/api/userinfo?type=get&username="+req.body.username;
  var request = https.get(apiUrl, function(response) {
    var output;

    if(response.statusCode == 500)
    {
      res.redirect(307,"/create-user");
    }
    else
    {
      res.redirect("/failed-register");
    }
    })
})

app.post("/log-in-buffer", function(req,res) {
  var username = req.body.username;
  var password = req.body.password;
  var apiUrl = "https://cornellmeetup.azurewebsites.net/api/userinfo?type=get&username=" + username;
  var request = https.get(apiUrl, function(response) {
    var output;
      if(response.statusCode == 200)
      {
        res.redirect(307, "/map");
      }
      else
      {
        res.redirect("/failed-login");
      }
  });
})

app.post("/map", function(req, res) {
  var username = req.body.username;
  var password = req.body.password;
  globalUsername = username;

  var apiUrl = "https://cornellmeetup.azurewebsites.net/api/authservice?type=authenticate&username=" + username + "&password=" + password;
  var request = https.get(apiUrl, function(response) {
    var output;
    response.on("data", function(data) {
      const output = JSON.parse(data);
      if(output == true)
      {
        res.render(__dirname + "/map.html", {
          username: username
        });
      }
      else
      {
        res.redirect("/failed-login");
      }
    });


  })
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

app.post("/create-user", function(req, res) {
  var list = req.body.groups.split(",");
  var groupList = [];

  for (var i = 0; i < list.length; i++) {
    groupList.push(parseInt(list[i]));
  }
  var url = "https://cornellmeetup.azurewebsites.net/api/userinfo?type=add";
  var postData = JSON.stringify({
    "id": req.body.username,
    "password": req.body.password,
    "last_online": "11/30/22",
    "groups": groupList,
    "info": {
      "birthday": req.body.birthday,
      "time_zone": req.body.timezone,
      "profile_picture_id": req.body.pfp
    }
  });



  var request = https.request(url, options, function(response) {
    res.on('data', d => {
      process.stdout.write(d);
    })
    // console.log(response);
  })
  request.on('error', (e) => {
    console.error(e);
  });
  request.write(postData);
  request.end();


  for (var i = 0; i < groupList.length; i++) {
    var url = "https://cornellmeetup.azurewebsites.net/api/groupinfo?type=addmember&groupname=" + groupList[i] + "&username=" + req.body.username;

    var request = https.request(url, function(response) {
      res.on('data', d => {
        process.stdout.write(d);
      })
      // console.log(response);
    })
    request.on('error', (e) => {
      console.error(e);
    });
    request.write(postData);
    request.end();
  }

  var locationPostData = JSON.stringify({
    "longitude": 0,
    "latitude": 0
  });

  var url = "https://cornellmeetup.azurewebsites.net/api/locationinfo?type=add&username=" + req.body.username;
  var request = https.request(url, options, function(response) {
    res.on('data', d => {
      process.stdout.write(d);
    })
  })
  request.on('error', (e) => {
    console.error(e);
  });
  request.write(locationPostData);
  request.end();

  res.redirect("/sign-in");
})

app.listen(3000, function() {
  console.log("Server started on port 3000");
});

function getUserLocation(username) {
  console.log("called method using: " + String(username));
}
