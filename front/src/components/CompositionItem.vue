<script setup>
import { store } from '../store/store.js'
</script>

<template>
  <div class="composition" :class="{ finished: project_finished, unfinished: !project_finished }">
    <div class="coverart" v-if="!!composition.coverart">
      <img :src="cover_art_source(composition.coverart)" alt="Cover Art" title="Cover Art" loading="lazy" />
    </div>
    <h2 class="title">{{ title }}</h2>
    <h3 class="artist">Artist: {{ composition.artist }}</h3>
    <h3 class="album">
      <span v-if="composition.album">Album: {{ composition.album }}</span>
      <span v-else-if="composition.ep">EP: {{ composition.ep }}</span>
      <span v-else-if="project_finished">Single</span>
    </h3>
    <p class="status" v-if="project_finished && !composition.coverart">{{ composition.status }}</p>
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
        Last activity:
        <span class="text_information" :title="composition.last_activity">{{
          pretty_last_activity
        }}</span>
      </p>
      <p class="als_file_path">
        File name:
        <span class="text_information" :title="composition.als_file_path">{{
          composition.als_file_name
        }}</span>
      </p>
      <p v-if="has_main_audio_file" class="audio_file">
        Latest audio:
        <span class="text_information" :title="main_audio_file_name">{{
          short_main_audio_file_name
        }}</span>
      </p>
      <p v-if="has_main_audio_file" class="audio_source">
        <audio controls>
          <source :src="main_audio_file_source" :type="'audio/' + main_audio_extension" />
        </audio>
      </p>
      <p v-if="project_finished && !has_main_audio_file" class="audio_file" :class="{ not_exported: project_finished }">
        Sound file not exported
      </p>
      <p v-if="!composition.info_file" class="no_info_file">
        Info file missing. <button @click="store.createInfoFile(composition.full_als_file_path)">Create?</button>
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
        return this.audio_file_name(this.composition.audio_files[0])
      }
      return null
    },
    short_main_audio_file_name() {
      return store.shorten_string(this.main_audio_file_name, 20)
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
    pretty_last_activity() {
      return new Date(this.composition.last_activity).toDateString()
    },
    lyrics() {
      return this.project_finished ? (this.composition.lyrics || 'N/A') : (this.composition.lyrics)
    },
    title() {
      return this.composition.title || this.composition.als_file_name
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
    cover_art_source(cover_art_path) {
      return store.getCoverArt(cover_art_path)
    },
  },
}
</script>
