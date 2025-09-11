const express = require('express')
const cors = require('cors');
const request = require('postman-request');
const path = require('path');
const fs = require('fs');
const _ = require('lodash')

// Set up express server
const app = express()
app.use(cors())
const port = 5556

// Configure music_lister access
PYTHON_BACKEND_URL = "localhost:5555"

// Initialise database file
var database;
const read_database = () => {
  database = JSON.parse(fs.readFileSync('../database/database.json', 'utf8'));
};
read_database();

// Configure routes
app.get('/refresh_database', (req, res) => {
  console.log("Looking to update database");
  add_query = '';
  if(req.query.composition_folder) {
    console.log("With new composition folder: " + req.query.composition_folder);
    const params = new URLSearchParams(req.query);
    add_query = '?' + params.toString();
  }
  request('http://' + PYTHON_BACKEND_URL + '/refresh' + add_query, function (error, response, body) {
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

app.get('/audiostream', (req, res) => {
  if(!req.query.file) {
    res.status(500).send('No file provided');
  }
  const full_audio_path = decodeURIComponent(req.query.file)
  console.log("Full audio path: " + full_audio_path);
  if(!fs.existsSync(full_audio_path)) {
    res.status(404).send('Composition not found');
    return;
  }
  res.sendFile(full_audio_path);
})

app.listen(port, () => {
  console.log(`Backend listening on port ${port}`)
})
