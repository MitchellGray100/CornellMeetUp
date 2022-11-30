const express = require("express");
const bodyParser = require("body-parser");
const https = require("https");

const app = express();
app.use(bodyParser.urlencoded({extended: true}));

app.get("/", function(req, res) {
    res.sendFile(__dirname + "/map.html");
    const url = "https://api.kanye.rest";

    https.get(url, function(response)
    {
      console.log(response.statusCode);
      response.on("data", function(data){
        const output = JSON.parse(data);
        console.log(output);
      })
    })
    console.log(__dirname);
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

function getUserLocation(username)
{
  console.log("called method using: " + String(username));
}
