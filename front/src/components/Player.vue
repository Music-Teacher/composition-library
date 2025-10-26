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
  watch: {
    audio_source: function (newVal, oldVal) {
      if (newVal !== oldVal) {
        console.log('Audio source changed, playing new audio')
        this.$nextTick(() => {
          const audioElement = this.$el.querySelector('audio')
          if (audioElement) {
            audioElement.pause()
            audioElement.load()
            audioElement.play()
          }
        })
      }
    },
  },
  computed: {
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
  },
}
</script>
