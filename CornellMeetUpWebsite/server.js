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

const options = {
  method: 'POST'
}

app.get("/", function(req, res) {
  res.redirect("/sign-in");
})

app.post("/profile", function(req, res) {
  res.render(__dirname + "/profile.html", {
    username: req.body.username
  });
})

app.post("/settings", function(req, res) {
  console.log(req.body.username);

  res.render(__dirname + "/settings.html", {
    username: req.body.username
  });
})

app.get("/settings", function(req, res) {
  console.log(req.body.username);
  res.render(__dirname + "/settings.html", {
    username: req.body.username
  });
})

app.post("/make-group", function(req, res) {

  res.render(__dirname + "/make-group.html", {
    username: req.body.username
  });
})

app.post("/create-group", function(req, res) {
  var apiUrl = "https://cornellmeetup.azurewebsites.net/api/groupinfo?type=newgroup&groupname=" + req.body.groupname;
  var request = https.get(apiUrl, function(response) {
    if (response.statusCode == 200) {
      var apiUrl = "https://cornellmeetup.azurewebsites.net/api/groupinfo?type=addmember&groupname=" + req.body.groupname + "&username=" + req.body.username;
      var request = https.get(apiUrl, function(response) {})

      var apiUrl = "https://cornellmeetup.azurewebsites.net/api/userinfo?type=get&username=" + req.body.username;
      var request = https.get(apiUrl, function(response) {
        response.on("data", function(data) {
          const output = JSON.parse(data);
          var apiUrl = "https://cornellmeetup.azurewebsites.net/api/userinfo?type=update&username=" + req.body.username;

          var groupList = output.groups;
          groupList.push(req.body.groupname);

          var postData = JSON.stringify({
            "groups": groupList
          });

          var request = https.request(apiUrl, options, function(response) {
            res.on('data', d => {
              process.stdout.write(d);
            });

          });
          request.on('error', (e) => {
            console.error(e);
          });
          request.write(postData);
          request.end();
        });
      })
    }
  })

  res.redirect(307, "/make-group");
})


app.post("/delete-profile", function(req, res) {
  var apiUrl = "https://cornellmeetup.azurewebsites.net/api/userinfo?type=get&username=" + req.body.username;
  var request = https.get(apiUrl, function(response) {
    response.on("data", function(data) {
      const output = JSON.parse(data);
      for (var i = 0; i < output.groups.length; i++) {
        var url = "https://cornellmeetup.azurewebsites.net/api/groupinfo?type=removemember&groupname=" + output.groups[i] + "&username=" + req.body.username;
        var request = https.request(url, options, function(response) {
          res.on('data', d => {
            process.stdout.write(d);
          })
          // console.log(response);
        })
        request.on('error', (e) => {
          console.error(e);
        });
        request.end();
      }

    });
  })

  var apiUrl = "https://cornellmeetup.azurewebsites.net/api/userinfo?type=delete&username=" + req.body.username;
  var request = https.get(apiUrl, function(response) {})
  var apiUrl = "https://cornellmeetup.azurewebsites.net/api/locationinfo?type=delete&username=" + req.body.username;
  var request = https.get(apiUrl, function(response) {})

  res.redirect("/");
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
  var apiUrl = "https://cornellmeetup.azurewebsites.net/api/userinfo?type=get&username=" + req.body.username;
  var request = https.get(apiUrl, function(response) {
    var output;

    if (response.statusCode == 500) {
      res.redirect(307, "/create-user");
    } else {
      res.redirect("/failed-register");
    }
  })
})

app.post("/update-profile", function(req, res) {
  var apiUrl = "https://cornellmeetup.azurewebsites.net/api/userinfo?type=get&username=" + req.body.username;
  var request = https.get(apiUrl, function(response) {
    response.on("data", function(data) {
      const output = JSON.parse(data);
      var apiUrl = "https://cornellmeetup.azurewebsites.net/api/userinfo?type=update&username=" + req.body.username;
      birthday = req.body.birthday;
      timezone = req.body.timezone;
      pfp = req.body.pfp;
      var list = req.body.groups.split(",");

      var groupList = [];
      for (var i = 0; i < list.length; i++) {
        groupList.push(list[i]);
      }

      var actualBirthday;
      var actualTimezone;
      var actualPfp;
      var actualGroups;


      if (birthday) {
        actualBirthday = birthday;
      } else {
        actualBirthday = output.info.birthday;
      }
      if (timezone) {
        actualTimezone = timezone;
      } else {
        actualTimezone = output.info.time_zone;
      }
      if (pfp) {
        actualPfp = pfp;
      } else {
        actualPfp = output.info.profile_picture_id;
      }

      if (groupList[0] != "") {
        //removing user from all groups
        for (var i = 0; i < output.groups.length; i++) {
          var url = "https://cornellmeetup.azurewebsites.net/api/groupinfo?type=removemember&groupname=" + output.groups[i] + "&username=" + req.body.username;
          var request = https.request(url, options, function(response) {
            res.on('data', d => {
              process.stdout.write(d);
            })
            // console.log(response);
          })
          request.on('error', (e) => {
            console.error(e);
          });
          request.end();
        }
        //adding user to all new groups
        for (var i = 0; i < groupList.length; i++) {
          var url = "https://cornellmeetup.azurewebsites.net/api/groupinfo?type=addmember&groupname=" + groupList[i] + "&username=" + req.body.username;
          var request = https.request(url, options, function(response) {
            res.on('data', d => {
              process.stdout.write(d);
            })
            // console.log(response);
          })
          request.on('error', (e) => {
            console.error(e);
          });
          request.end();
        }
        actualGroups = groupList;
      } else {
        actualGroups = output.groups;
      }


      var postData = JSON.stringify({
        "groups": actualGroups,
        "info": {
          "birthday": actualBirthday,
          "time_zone": actualTimezone,
          "profile_picture_id": actualPfp
        }
      });

      var request = https.request(apiUrl, options, function(response) {
        res.on('data', d => {
          process.stdout.write(d);
        })

      });
      request.on('error', (e) => {
        console.error(e);
      });
      request.write(postData);
      request.end();
      res.redirect(307, "/profile");
    });




  })


})

app.post("/log-in-buffer", function(req, res) {
  var username = req.body.username;
  var password = req.body.password;
  var apiUrl = "https://cornellmeetup.azurewebsites.net/api/userinfo?type=get&username=" + username;
  var request = https.get(apiUrl, function(response) {
    var output;
    if (response.statusCode == 200) {
      res.redirect(307, "/login-in-buffer-part-two");
    } else {
      res.redirect("/failed-login");
    }
  });
})

app.post("/login-in-buffer-part-two", function(req,res) {
  var username = req.body.username;
  var password = req.body.password;
  var apiUrl = "https://cornellmeetup.azurewebsites.net/api/authservice?type=authenticate&username=" + username + "&password=" + password;
  var request = https.get(apiUrl, function(response) {
    response.on("data", function(data) {
      const output = JSON.parse(data);
      if (output == true) {
        res.redirect(307, "/map");
      } else {
        res.redirect("/failed-login");
      }
    });
})
})

app.post("/map", function(req, res) {
  var username = req.body.username;

  res.render(__dirname + "/map.html", {
    username: req.body.username
  });
})

app.get("/map", function(req, res) {
  console.log(req.body.username);
  res.render(__dirname + "/map.html", {
    username: req.body.username
  });
})


app.post("/create-user", function(req, res) {
  var list = req.body.groups.split(",");
  var groupList = [];

  for (var i = 0; i < list.length; i++) {
    groupList.push(list[i]);
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

app.listen(Number(process.env.PORT), function() {
  console.log("Server started on port " + process.env.PORT);
});
