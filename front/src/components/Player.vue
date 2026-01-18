<script setup>
import { store } from '../store/store.js'
</script>

<template>
  <div class="audio_player_container" v-if="audio_selected">
    <div class="audio_player_cover_art" v-if="cover_art_source">
      <img :src="cover_art_source" alt="Cover Art" title="Cover Art" />
    </div>
    <div class="audio_player_information">
      <div class="audio_player_title" v-if="title">
        {{ title }}
      </div>
      <div class="audio_player_artist_album" v-if="artist">
        {{ artist }}
      </div>
    </div>
    <div class="audio_player_controls">
      <div class="audio_file_name">
        <p>{{ audio_file_name }}</p>
      </div>
      <audio controls loop autoplay controlslist="play nofullscreen nodownload noplaybackrate">
        <source :src="audio_source" :type="'audio/' + audio_extension" />
      </audio>
    </div>
    <div class="audio_player_extra_controls">
      <p @click="toggleLoop" :class="{ loop_enabled: loop }">↳↰</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      playing: false,
      loop: false,
    }
  },
  watch: {
    audio_source: function (newVal) {
      console.log('A play audio button was played, will play the audio now (', newVal, ')')
      this.$nextTick(() => {
        this.audio_element.pause()
        this.audio_element.load()
        this.audio_element.play()
        this.playing = true
        this.audio_element.loop = false
        navigator.mediaSession.metadata = new MediaMetadata({
          title: this.title,
          artist: this.artist,
          album: '',
          artwork: [
            { src: this.cover_art_source || '', sizes: '512x512', type: 'image/png' },
          ],
        })
      })
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
    audio_file_name() {
      return store.audioToPlay.audio_file_name
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
    document.removeEventListener('keydown', this.onKeyDown)
  },
  methods: {
    async onKeyDown(event) {
      if (this.audio_selected && this.audio_element) {
        if (event.code == 'Space') {
          console.log("'Space' pressed, toggling play/pause")
          this.playing = !this.playing
          if (this.playing) {
            console.log('Playing audio')
            this.audio_element.play()
          } else {
            console.log('Pausing audio')
            this.audio_element.pause()
          }
          event.preventDefault()
        }
      }
    },
    toggleLoop() {
      this.loop = !this.loop
      if (this.audio_element) {
        this.audio_element.loop = this.loop
      }
    },
  },
}
</script>
