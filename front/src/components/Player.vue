<script setup>
import { store } from '../store/store.js'
</script>

<template>
  <div class="audio_player_container" v-if="audio_source">
    <div class="audio_player_cover_art" v-if="cover_art_source">
      <img :src="cover_art_source" alt="Cover Art" title="Cover Art" />
    </div>
    <div class="audio_information">
      <div class="audio_player_title" v-if="title">
        {{ title }}
      </div>
      <div class="audio_player_artist_album" v-if="artist">
        {{ artist }}
      </div>
    </div>
    <div class="audio_player_controls">
      <audio controls loop autoplay controlslist="play nofullscreen nodownload noplaybackrate">
        <source :src="audio_source" :type="'audio/' + audio_extension" />
      </audio>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      playing: false,
    }
  },
  watch: {
    audio_source: function (newVal, oldVal) {
      if (newVal !== oldVal) {
        console.log('Audio source changed, playing new audio')
        this.$nextTick(() => {
          if (this.audio_element) {
            this.audio_element.pause()
            this.audio_element.load()
            this.audio_element.play()
            this.playing = true
          }
        })
      }
    },
  },
  computed: {
    audio_selected() {
      return !!this.audio_source
    },
    audio_source() {
      return store.audioToPlay.audio_source
    },
    artist() {
      return store.audioToPlay.artist
    },
    title() {
      return store.audioToPlay.title
    },
    audio_extension() {
      return store.audioToPlay.audio_extension
    },
    cover_art_source() {
      if (store.audioToPlay.cover_art) {
        return store.audioToPlay.cover_art
      }
    },
    audio_element() {
      return this.$el.querySelector('audio')
    },
  },
  async mounted() {
    document.addEventListener('keydown', this.onKeyDown)
  },
  beforeDestroy() {
    document.removeEventListener('keyup', this.onKeyDown)
  },
  methods: {
    async onKeyDown(event) {
      if (event.code == 'Space' && this.audio_selected && this.audio_element) {
        console.log("'Space' pressed, toggling play/pause")
        this.playing = !this.playing
        event.preventDefault()
        if (this.playing) {
          console.log("Playing audio")
          this.audio_element.play()
        } else {
          console.log("Pausing audio")
          this.audio_element.pause()
        }
      }
    },
  },
}
</script>
