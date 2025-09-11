<script setup>
import { store } from '../store/store.js'
import CompositionItem from './CompositionItem.vue'
</script>

<template>
  <div class="controls">
    <div class="sort">
      <label for="sortSelect">Sort by: </label
      ><select v-model="sortBy" @change="sortCompositions" id="sortSelect">
        <option value="activity">Last activity</option>
        <option value="status">Status</option>
        <option value="title">Title</option>
        <option value="artist">Artist</option>
        <option value="album">Album</option>
      </select>
      <label>
        <input v-model="reverseSort" type="checkbox" />
        <span>reverse</span>
      </label>
    </div>
    <div class="filter">
      Only show:
      <label>
        <input v-model="onlyFinished" @change="filterFinished" type="checkbox" />
        <span>Finished</span>
      </label>
      <label>
        <input v-model="onlyInProgress" @change="filterInProgress" type="checkbox" />
        <span>In Progress</span>
      </label>
    </div>
    <div class="refresh">
      <button id="refreshButton" @click="syncCompositions" :disabled="store.isLoading">
        Refresh
      </button>
    </div>
  </div>
  <div class="compositions">
    <CompositionItem
      v-for="composition in sortedFilteredCompositions"
      :id="composition['id']"
      :key="composition['als_file_path']"
      :name="composition['name']"
      :artist="composition['artist']"
      :album="composition['album']"
      :ep="composition['ep']"
      :lyrics="composition['lyrics']"
      :chords="composition['chords']"
      :extra_info="composition['extra_info']"
      :status="composition['status']"
      :rework="composition['rework']"
      :als_file_path="composition['als_file_path']"
      :project_dir="composition['project_dir']"
      :root_folder="composition['root_folder']"
      :als_file_name="composition['als_file_name']"
      :audio_files="composition['audio_files']"
      :last_activity="composition['last_activity']"
    />
  </div>
</template>

<script>
export default {
  data() {
    return {
      pollingInterval: null,
      sortBy: 'activity',
      reverseSort: false,
      refreshing: false,
      onlyFinished: false,
      onlyInProgress: false,
    }
  },
  computed: {
    sortedFilteredCompositions() {
      console.log(
        'Sort:',
        this.sortBy,
        'Reverse:',
        this.reverseSort,
        'Filter Finished:',
        this.onlyFinished,
        'Filter In Progress:',
        this.onlyInProgress,
      )
      let outputCompositions = store.compositions.slice() // Create a copy of the array

      // Filtering
      if (this.onlyFinished) {
        outputCompositions = outputCompositions.filter((c) => c.status === 'Finished')
      } else if (this.onlyInProgress) {
        outputCompositions = outputCompositions.filter((c) => c.status !== 'Finished')
      }

      // Sorting
      outputCompositions = outputCompositions.sort((a, b) => {
        let returnValue = 0
        if (this.sortBy === 'activity') {
          returnValue = new Date(b.last_activity) - new Date(a.last_activity)
        } else if (this.sortBy === 'status') {
          if (a.status === b.status) returnValue = 0
          else if (a.status === 'Finished') returnValue = -1
          else returnValue = 1
        } else if (this.sortBy === 'title') {
          returnValue = a.name.localeCompare(b.name)
        } else if (this.sortBy === 'artist') {
          returnValue = a.artist.localeCompare(b.artist)
        } else if (this.sortBy === 'album') {
          returnValue = a.album.localeCompare(b.album)
        }
        if (this.reverseSort == true) {
          return returnValue * -1
        }
        return returnValue
      })
      return outputCompositions
    },
  },
  async mounted() {
    await store.fetchCompositions()
    await store.refreshDatabase()
    await store.fetchCompositions()
  },
  created() {
    this.sortBy = 'activity'
  },
  beforeDestroy() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval)
    }
  },
  beforeCreate() {
    this.pollingInterval = setInterval(async () => {
      await store.refreshDatabase()
      await store.fetchCompositions()
    }, 30000) // 30 seconds
  },
  methods: {
    async syncCompositions() {
      await store.refreshDatabase()
      await store.fetchCompositions()
    },
    sortCompositions() {
      this.$forceUpdate()
    },
    filterFinished() {
      this.onlyInProgress = false
      this.$forceUpdate()
    },
    filterInProgress() {
      this.onlyFinished = false
      this.$forceUpdate()
    },
  },
}
</script>
