<script setup>
import { store } from '../store/store.js'
</script>

<template>
  <div class="composition" :class="{ finished: project_finished, unfinished: !project_finished }">
    <h2 class="songname">{{ composition.title }}</h2>
    <h3 class="artist">Artist: {{ composition.artist }}</h3>
    <h3 class="album">Album: {{ composition.album }}</h3>
    <p class="status" v-if="project_finished">{{ composition.status }}</p>
    <p
      class="rework"
      :class="{ rework_multiple_lines: !!rework_multiple_lines }"
      v-if="!project_finished && needs_rework"
    >
      <span>Rework: </span>
      <span>{{ composition.rework }}</span>
    </p>
    <div class="composition_main_info">
      <p class="last_activity">
        Last activity: <span>{{ composition.last_activity }}</span>
      </p>
      <p class="als_file_path">
        File path: <span>'{{ shortened_als_file_path }}'</span>
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
            <td>{{ composition.lyrics }}</td>
          </tr>
          <tr>
            <th>Chords</th>
            <td>{{ composition.chords }}</td>
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
  props: ['composition'],
  computed: {
    project_finished() {
      return this.composition.status === 'Finished'
    },
    needs_rework() {
      return !!this.composition.rework
    },
    rework_multiple_lines() {
      return this.composition.rework.includes('\n')
    },
    number_of_audio_files() {
      return this.composition.audio_files.length
    },
    has_main_audio_file() {
      return this.number_of_audio_files >= 1
    },
    has_other_audio_files() {
      return this.number_of_audio_files >= 2
    },
    main_audio_file_source() {
      if (this.has_main_audio_file) {
        return this.audio_file_source(this.composition.audio_files[0])
      }
    },
    main_audio_file_name() {
      if (this.has_main_audio_file) {
        return this.shorten_string(this.audio_file_name(this.composition.audio_files[0]), 20, false)
      }
      return null
    },
    main_audio_extension() {
      if (this.has_main_audio_file) {
        return this.audio_extension(this.composition.audio_files[0])
      }
      return null
    },
    other_audio_files() {
      if (this.has_other_audio_files) {
        return this.composition.audio_files.slice(1)
      }
      return null
    },
    shortened_als_file_path() {
      return this.shorten_string(this.composition.als_file_path, 25, true)
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
    shorten_string(text, maxchars, middle) {
      if (this.composition.als_file_path.length >= maxchars) {
        if (!!middle) {
          let start = text.substring(0, maxchars / 2)
          let end = text.substring(text.length - maxchars / 2, text.length)
          let middle = '.....'
          if(text.includes('/')) {
            
          }
          return start + middle + end
        } else {
          return '...' + text.substring(text.length - maxchars, text.length)
        }
      }
      return text
    },
  },
}
</script>
