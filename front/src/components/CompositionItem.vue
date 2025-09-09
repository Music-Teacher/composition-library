<script setup>
const props = defineProps([
  'name',
  'artist',
  'album',
  'ep',
  'lyrics',
  'chords',
  'extra_info',
  'status',
  'rework',
  'als_file_path',
  'project_dir',
  'root_folder',
  'als_file_name',
  'audio_file',
  'last_activity'
])
</script>

<template>
  <div :class="{ composition: true, finished: status === 'Finished' }">
    <h2 class="songname">{{ name }}</h2>
    <h3 class="artist">Artist: {{ artist }}</h3>
    <h3 class="album">Album: {{ album }}</h3>
    <p class="status">Status: {{ status }}</p>
    <div class="activity_path">
      <p class="last_activity">Last modified: <span>{{ last_activity }}</span></p>
      <p class="als_file_path">File path: <span>{{ als_file_path }}</span></p>
      <p class="audio_file">
        <audio controls v-if="audio_file">
          <source :src="audio_file" type="audio/wav" />
        </audio>
        <span v-else>Sound file exported</span>
      </p>
    </div>
    <details>
      <summary>More info</summary>
      <table border="0" cellpadding="5">
        <tbody>
          <tr>
            <th>Lyrics</th>
            <td>{{ lyrics }}</td>
          </tr>
          <tr>
            <th>Chords</th>
            <td>{{ chords }}</td>
          </tr>
        </tbody>
      </table>
    </details>
  </div>
</template>

<script>

</script>
