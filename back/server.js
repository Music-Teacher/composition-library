const express = require('express')
const cors = require('cors');
const request = require('postman-request');
const moment = require('moment');
const fs = require('fs');
const sharp = require('sharp');
const os = require('node:os');
const _ = require('lodash')

// Log function
function log(message) {
  console.log(`[${moment().format()}] ${message}`);
}
log("OS: " + os.platform())

// Set up express server
const app = express()
app.use(cors())
const port = 5556

// Configure music_lister access
PYTHON_BACKEND_URL = "localhost:5555"

// Initialise database file
var database;
const read_database = () => {
  try {
    database = JSON.parse(fs.readFileSync('../database/database.json', 'utf8'));
  } catch (error) {
    log("Could not read database file");
    console.error(error);
    log(error);
  }
};
read_database();

// Configure routes
app.get('/refresh_database', (req, res) => {
  log("Looking to update database");
  add_query = '';
  if(req.query.composition_folder) {
    log("With new composition folder: " + req.query.composition_folder);
    const params = new URLSearchParams(req.query);
    add_query = '?' + params.toString();
  }
  request('http://' + PYTHON_BACKEND_URL + '/refresh' + add_query, function (error, response, body) {
    if (error) {
      console.error('Error making request to Python Backend:', error);
      res.status(500).send('Error making request to Python Backend');
      log("Error making request to Python Backend: "+ error)
      return;
    }
    if (response.statusCode !== 200) {
      console.error('Non-200 response status code:', response.statusCode);
      res.status(response.statusCode).send('Non-200 response status code');
      log("Non-200 response status code: " + response.statusCode)
      return;
    }
    res.send(response);
    read_database();
    log("Database updated")
  });
})

app.get('/basicinfo', (req, res) => {
  log("Looking for basic info");
  const basicInfo = _.pick(database, ['root_folder', 'output_json_file']);
  res.json(basicInfo); // Send the array as JSON
  log("Basic info returned")
})

app.get('/compositions', (req, res) => {
  log("Looking for all composition data");
  const compositions = database['compositions'];
  res.json(compositions); // Send the array as JSON
  log("Compositions returned")
})

app.get('/audiostream', (req, res) => { // /audiostream?file=full_audio_path
  log("Looking for audio stream")
  if(!req.query.file) {
    res.status(500).send('No file provided');
    log("No file provided")
  }
  const full_audio_path = decodeURIComponent(req.query.file)
  log("Full audio path: " + full_audio_path);
  if(!fs.existsSync(full_audio_path)) {
    res.status(404).send('Audio file not found');
    log("Audio file not found")
    return;
  }
  res.sendFile(full_audio_path);
  log("Audio returned")
})

app.get('/coverart', (req, res) => { // /coverart?file=full_cover_art_path
  log("Looking for cover art")
  if(!req.query.file) {
    res.status(500).send('No file provided');
    log("No file provided")
  }
  const full_cover_art_path = decodeURIComponent(req.query.file)
  log("Full cover art path: " + full_cover_art_path);

  if(!fs.existsSync(full_cover_art_path)) {
    res.status(404).send('Cover art file not found');
    log("Cover art file not found")
    return;
  }

  sharp(full_cover_art_path)
      .resize(150, 150)
      .png()
      .toBuffer()
      .then(data => res.type('png').send(data))
  log("Cover art returned")
})

app.get('/create_info_file', (req, res) => { // /create_info_file?als_file_path=full_als_file_path
  log("Looking to create info file")
  if(!req.query.als_file_path) {
    res.status(500).send('No ALS file path provided');
    log("No ALS file path provided")
  }
  const als_file_path = decodeURIComponent(req.query.als_file_path)
  log("Full ALS file path: " + als_file_path);

  request('http://' + PYTHON_BACKEND_URL + '/create_info_file?als_file_path=' + encodeURIComponent(als_file_path), function (error, response, body) {
    if (error) {
      console.error('Error making request to Python Backend:', error);
      res.status(500).send('Error making request to Python Backend');
      log("Error making request to Python Backend: "+ error)
      return;
    }
    if (response.statusCode !== 200) {
      console.error('Non-200 response status code:', response.statusCode);
      res.status(response.statusCode).send('Non-200 response status code');
      log("Non-200 response status code: " + response.statusCode)
      return;
    }
    res.send(response);
    read_database();
    log("Info file created and database updated")
  });
})

app.get('/rename_project', (req, res) => { // /rename_project?als_file_path=als_file_path&artist=artist&title=title
  log("Looking to rename project")
  if(!req.query.als_file_path || !req.query.artist || !req.query.title) {
    res.status(500).send('Missing parameters');
    log("Missing parameters")
  }
  const als_file_path = decodeURIComponent(req.query.als_file_path)
  const artist = decodeURIComponent(req.query.artist)
  const title = decodeURIComponent(req.query.title)
  log(`Renaming project at ${als_file_path} to ${artist} - ${title}`);

  request('http://' + PYTHON_BACKEND_URL + '/rename_project?als_file_path=' + encodeURIComponent(als_file_path) + '&artist=' + encodeURIComponent(artist) + '&title=' + encodeURIComponent(title), function (error, response, body) {
    if (error) {
      console.error('Error making request to Python Backend:', error);
      res.status(500).send('Error making request to Python Backend');
      log("Error making request to Python Backend: "+ error)
      return;
    }
    if (response.statusCode !== 200) {
      console.error('Non-200 response status code:', response.statusCode);
      res.status(response.statusCode).send('Non-200 response status code');
      log("Non-200 response status code: " + response.statusCode)
      return;
    }
    res.send(response);
    read_database();
    log("Project renamed and database updated")
  });
}

app.listen(port, () => {
  log(`Backend listening on port ${port}`)
})
