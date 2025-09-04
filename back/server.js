const express = require('express')
const cors = require('cors');
var _ = require('lodash')
const app = express()
app.use(cors())
const port = 3000

// Read database file
var fs = require('fs');
var database = JSON.parse(fs.readFileSync('../database/database.json', 'utf8'));

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
