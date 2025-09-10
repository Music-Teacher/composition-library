const express = require('express')
const cors = require('cors');
const request = require('postman-request');
var path = require('path');
var _ = require('lodash')

// Set up express server
const app = express()
app.use(cors())
const port = 5556

// Configure music_lister access
PYTHON_BACKEND_URL = "localhost:5555"

// Initialise database file
var fs = require('fs');
const { DiffieHellmanGroup } = require('crypto');
var database;
const read_database = () => {
  database = JSON.parse(fs.readFileSync('../database/database.json', 'utf8'));
};
read_database();

// Configure routes
app.get('/refresh_database', (req, res) => {
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
    read_database();
  });
})

app.get('/basicinfo', (req, res) => {
  console.log("Looking for basic info");
  const basicInfo = _.pick(database, ['root_folder', 'output_json_file']);
  res.json(basicInfo); // Send the array as JSON
})

app.get('/compositions', (req, res) => {
  console.log("Looking for all composition data");
  const compositions = database['compositions'];
  res.json(compositions); // Send the array as JSON
})

app.get('/composition/:id/audio', (req, res) => {
  console.log("Looking for song of composition id: " + req.params.id);
  const compositions = database.compositions;
  const index = _.findIndex(compositions, {'id': req.params.id});
  if (index == -1 || compositions[index].audio_file === "null") {
    res.status(404).send('Composition not found');
    return;
  }
  console.log("Composition found with audio file " + compositions[index].audio_file);
  audio_relative_path = path.relative(__dirname, compositions[index].audio_file.replace("c:", "/mnt/c"));
  full_path = path.resolve(__dirname, audio_relative_path);
  console.log("Full path: " + full_path);
  res.sendFile(full_path);
})

app.listen(port, () => {
  console.log(`Backend listening on port ${port}`)
})
