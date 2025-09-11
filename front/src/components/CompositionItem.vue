<script setup>
import { store } from '../store/store.js'
</script>

<template>
  <div :class="{ composition: true, finished: status === 'Finished' }">
    <h2 class="songname">{{ name }}</h2>
    <h3 class="artist">Artist: {{ artist }}</h3>
    <h3 class="album">Album: {{ album }}</h3>
    <p class="status">Status: {{ status }}</p>
    <div class="composition_main_info">
      <p class="last_activity">
        Last modified: <span>{{ last_activity }}</span>
      </p>
      <p class="als_file_path">
        File path: <span>'{{ als_file_path }}'</span>
      </p>
      <p v-if="has_main_audio_file" class="audio_file">
        Latest audio file: <span>'{{ main_audio_file_name }}'</span>
      </p>
      <p v-else class="audio_file" :class="{ not_exported: project_finished }">
        Sound file not exported
      </p>
      <p v-if="has_main_audio_file" class="audio_source">
        <audio controls>
          <source :src="main_audio_file_source" :type="'audio/' + main_audio_extension" />
        </audio>
      </p>
    </div>
    <details class="composition_details">
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
          <tr v-if="has_other_audio_files">
            <th>Other audio</th>
            <td>
              <p v-for="audio_file in other_audio_files" class="audio_source">
                {{ audio_file_name(audio_file) }}<br />
                <audio controls controlslist="play nofullscreen nodownload noplaybackrate">
                  <source
                    :src="audio_file_source(audio_file)"
                    :type="'audio/' + audio_extension(audio_file)"
                  />
                </audio>
              </p>
            </td>
          </tr>
        </tbody>
      </table>
    </details>
  </div>
</template>

<script>
export default {
  props: [
    'id',
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
    'audio_files',
    'last_activity',
  ],
  computed: {
    project_finished() {
      return this.status === 'Finished'
    },
    number_of_audio_files() {
      return this.audio_files.length
    },
    has_main_audio_file() {
      return this.number_of_audio_files >= 1
    },
    has_other_audio_files() {
      return this.number_of_audio_files >= 2
    },
    main_audio_file_source() {
      if (this.has_main_audio_file) {
        return this.audio_file_source(this.audio_files[0])
      }
    },
    main_audio_file_name() {
      if (this.has_main_audio_file) {
        return this.audio_file_name(this.audio_files[0])
      }
      return null
    },
    main_audio_extension() {
      if (this.has_main_audio_file) {
        return this.audio_extension(this.audio_files[0])
      }
      return null
    },
    other_audio_files() {
      if (this.has_other_audio_files) {
        return this.audio_files.slice(1)
      }
      return null
    },
  },
  methods: {
    audio_extension(audio_file_path) {
      const parts = audio_file_path.split('.')
      return parts.length > 1 ? parts[parts.length - 1] : null
    },
    audio_file_name(audio_file_path) {
      return audio_file_path.substring(audio_file_path.lastIndexOf('/') + 1)
    },
    audio_file_source(audio_file_path) {
      return store.getMainAudioSource(audio_file_path)
    },
  },
}
</script>
