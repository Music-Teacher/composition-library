const express = require('express')
const cors = require('cors');
const request = require('postman-request');
var _ = require('lodash')

// Set up express server
const app = express()
app.use(cors())
const port = 5556

// Configure music_lister python program
PYTHON_BACKEND_URL = "localhost:5555"

// Read database file
var fs = require('fs');
var database = JSON.parse(fs.readFileSync('../database/database.json', 'utf8'));

app.get('/refresh', (req, res) => {
  console.log("Looking to update database");
  request('http://' + PYTHON_BACKEND_URL + '/refresh', function (error, response, body) {
    if (error) {
      console.error('Error making request:', error);
      res.status(500).send('Error making request');
      return;
    }
    if (response.statusCode !== 200) {
      console.error('Non-200 response status code:', response.statusCode);
      res.status(response.statusCode).send('Non-200 response status code');
      return;
    }
    res.send(response);
  });
})

app.get('/basicinfo', (req, res) => {
  console.log("Looking for basic info");
  const basicInfo = _.pick(database, ['root_folder', 'output_json_file']);
  res.json(basicInfo); // Send the array as JSON
})

app.get('/compositions/ids', (req, res) => {
  console.log("Looking for all composition ids");
  const compositionIds = _.keys(database.compositions); // Use lodash to get keys
  res.json(compositionIds); // Send the array as JSON
})

app.get('/composition/id/:id', (req, res) => {
  console.log("Looking for composition id: " + req.params.id);
  const composition = database.compositions[''+req.params.id];
  console.log("Composition found with name " + composition["name"]);
  res.send(composition);
})

app.listen(port, () => {
  console.log(`Backend listening on port ${port}`)
})
