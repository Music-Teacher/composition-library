<script setup>
import { store } from '../store/store.js'
</script>

<template>
  <div class="composition" :class="{ finished: project_finished, unfinished: !project_finished }">
    <div class="cover_art" v-if="!!composition.cover_art">
      <img :src="cover_art_source" alt="Cover Art" title="Cover Art" loading="lazy" />
    </div>
    <h2 class="title">
      {{ title }}
    </h2>
    <h3 class="artist">Artist: {{ composition.artist }}</h3>
    <h3 class="album">
      <span v-if="composition.album">Album: {{ composition.album }}</span>
      <span v-else-if="composition.ep">EP: {{ composition.ep }}</span>
      <span v-else-if="project_finished">Single</span>
    </h3>
    <p class="file_name" v-if="can_be_renamed">
      <button @click="store.rename_project(composition.full_als_file_path, artist, title)">
        Rename to "{{ artist }} - {{ title }}"
      </button>
    </p>
    <p class="status" v-if="project_finished && !composition.cover_art">{{ composition.status }}</p>
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
      <p v-if="has_main_audio_file" class="audio_file audio_source" @click.prevent="play_this_audio(composition.audio_files[0])">
        Latest audio:
        <span class="text_information" :title="play_main_audio_file_name">
          {{ short_main_audio_file_name }}
        </span>
      </p>
      <p
        v-if="project_finished && !has_main_audio_file"
        class="audio_file"
        :class="{ not_exported: project_finished }"
      >
        Sound file not exported
      </p>
      <p v-if="!composition.info_file" class="no_info_file">
        Info file missing.
        <button @click="store.createInfoFile(composition.full_als_file_path)">Create?</button>
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
              <p v-for="audio_file in other_audio_files" class="audio_source" @click.prevent="play_this_audio(audio_file)">
                <span class="text_information">{{ audio_file_name(audio_file) }}</span>
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
    play_main_audio_file_name() {
      if (this.has_main_audio_file) {
        return "Play audio " + this.main_audio_file_name
      }
      return "No audio available"
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
      return this.project_finished ? this.composition.lyrics || 'N/A' : this.composition.lyrics
    },
    title() {
      return this.composition.title || this.composition.als_file_name
    },
    artist() {
      return this.composition.artist || null
    },
    pretty_title() {
      let pretty_title = ''
      if (this.composition.artist) {
        pretty_title += this.composition.artist + ' - '
      }
      if (this.composition.title) {
        pretty_title += this.composition.title
      } else {
        pretty_title += this.composition.als_file_name
      }
      return pretty_title
    },
    cover_art_source() {
      if (this.composition.cover_art) {
        return store.getCoverArt(this.composition.cover_art)
      }
      return null
    },
    can_be_renamed() {
      return this.composition.artist && this.composition.title && this.composition.als_file_name !== `${this.artist} - ${this.title}.als`
    },
  },
  methods: {
    audio_extension(audio_file_path) {
      const parts = audio_file_path.split('.')
      return parts.length > 1 ? parts[parts.length - 1] : null
    },
    audio_file_name(audio_file_path) {
      return audio_file_path.substring(audio_file_path.replaceAll("\\", "/").lastIndexOf('/') + 1)
    },
    audio_file_source(audio_file_path) {
      return store.getMainAudioSource(audio_file_path)
    },
    play_this_audio(audio_file) {
      store.setAudioToPlay(
        audio_file,
        this.audio_file_name(audio_file),
        this.artist,
        this.title,
        this.audio_extension(audio_file),
        this.cover_art_source,
      )
    },
  },
}
</script>
