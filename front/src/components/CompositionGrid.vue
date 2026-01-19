<script setup>
import { store } from '../store/store.js'
import CompositionItem from './CompositionItem.vue'
</script>

<template>
  <div class="controls menu_section">
    <div class="sort">
      <label for="sortSelect">Sort by: </label>
      <select v-model="sortBy" @change="sortCompositions" id="sortSelect">
        <option value="activity">Last activity</option>
        <option value="status">Status</option>
        <option value="title">Title</option>
        <option value="artist">Artist</option>
        <option value="album">Album</option>
      </select>
      <label>
        <input v-model="reverseSort" @change="sortCompositions" type="checkbox" />
        <span>reverse</span>
      </label>
    </div>
    <div class="filters">
      <div class="filter" v-for="(information, filter) in filtersAvailable">
        <span v-if="information[0].length >= 2">
          {{ filter[0].toUpperCase() + filter.slice(1) }}:
        </span>
        <label v-for="value in information[0]">
          <!-- Distinguish between filters with one value and others with several values -->
          <input
            v-if="information[0].length >= 2"
            v-model="filtersSelected[make_filter_index(filter, value)]"
            @change="toggleFilter(filter, value, information[1])"
            type="checkbox"
          />
          <input
            v-else-if="information[0].length == 1"
            v-model="filtersSelected[filter]"
            @change="toggleFilter(filter, value, information[1])"
            type="checkbox"
          />
          <span v-if="information[0].length >= 2">{{ value }}</span>
          <span v-else-if="information[0].length == 1">{{
            filter[0].toUpperCase() + filter.slice(1)
          }}</span>
        </label>
      </div>
    </div>
  </div>
  <div class="compositions">
    <CompositionItem v-for="composition in sortedFilteredCompositions" :composition="composition" />
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
      filtersSelected: {},
      onlyFinished: false,
      onlyInProgress: false,
      onlyExportedSongs: false,
    }
  },
  computed: {
    filtersAvailable() {
      const filters = ['status', 'audio', 'artist', 'album', 'ep']
      let filtersAvailable = {}
      filters.forEach((filter) => {
        const filterValues = this.uniqueFilterArray(filter)
        if (filterValues.length == 1 && filterValues[0] === true) {
          filtersAvailable[filter] = [filterValues]
        } else if (filterValues.length >= 2) {
          const exclusive = filterValues.length == 2 ? true : false
          filtersAvailable[filter] = [filterValues, exclusive]
        }
      })
      return filtersAvailable
    },
    sortedFilteredCompositions() {
      console.log('Sort:', this.sortBy, 'Reverse:', this.reverseSort)
      console.log('Filters:', JSON.stringify(this.filtersSelected))
      let outputCompositions = store.compositions.slice()

      // Whole filtering
      outputCompositions = outputCompositions.filter((c) => {
        let categoryMatch = {}
        for (let filter in this.filtersSelected) {
          const filterName = filter.split(':')[0]
          const filterValue = filter.split(':')[1]
          if (!!this.filtersSelected[filter]) {
            if (
              c[filterName] === filterValue ||
              (!filterValue && c[filterName] === this.filtersSelected[filter])
            ) {
              categoryMatch[filterName] = true
              continue
            }
            if (!(filterName in categoryMatch)) {
              categoryMatch[filterName] = false
            }
          }
        }
        if (Object.values(categoryMatch).every((item) => item === true)) return true
      })

      // Sorting
      outputCompositions = outputCompositions.sort((a, b) => {
        let returnValue = 0
        let reverse = !!this.reverseSort ? -1 : 1
        switch (this.sortBy) {
          case 'activity':
            returnValue = new Date(b.last_activity) - new Date(a.last_activity)
            break
          case 'status':
            if (a.status === b.status) returnValue = 0
            else if (a.status === 'Finished') returnValue = -1
            else returnValue = 1
            break
          case 'title':
          case 'artist':
          case 'album':
            if (!a[this.sortBy]) returnValue = 1
            else if (!b[this.sortBy]) returnValue = -1
            else returnValue = a[this.sortBy].localeCompare(b[this.sortBy])
            break
        }
        returnValue *= reverse
        return returnValue
      })
      return outputCompositions
    },
  },
  async mounted() {
    await store.fetchCompositions()
    await store.refreshDatabaseAndFetchCompositions()
  },
  created() {
    this.sortBy = this.$route.query.sort ? this.$route.query.sort : 'activity'
    this.reverseSort = this.$route.query.reverse === 'true' ? true : false
    this.filtersSelected = this.$route.query.filters ? JSON.parse(this.$route.query.filters) : {}
  },
  beforeDestroy() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval)
    }
  },
  beforeCreate() {
    this.pollingInterval = setInterval(async () => {
      if (!store.isLoading) {
        await store.refreshDatabaseAndFetchCompositions()
      }
    }, 30000) // 30 seconds
  },
  methods: {
    sortCompositions() {
      this.$router.push({
        query: { ...this.$route.query, sort: this.sortBy, reverse: this.reverseSort },
      })
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
    filterExportedSongs() {
      this.onlyExportedSongs = false
      this.$forceUpdate()
    },
    uniqueFilterArray(key) {
      const array = store.compositions.filter((c) => !!c[key]).map((c) => c[key])
      return [...new Set(array)]
    },
    toggleFilter(filter, value, exclusive) {
      console.log('Toggling filter:', filter, 'Value:', value, 'Exclusive:', exclusive)
      if (!!exclusive) {
        this.filtersAvailable[filter][0].forEach((e) => {
          const filterIndex = this.make_filter_index(filter, e)
          if (e !== value && filterIndex in this.filtersSelected) {
            this.filtersSelected[filterIndex] = false
          }
        })
      }
      Object.keys(this.filtersSelected).forEach((filterIndex) => {
        if (this.filtersSelected[filterIndex] === false) {
          delete this.filtersSelected[filterIndex]
        }
      })
      this.$router.push({
        query: { ...this.$route.query, filters: JSON.stringify(this.filtersSelected) },
      })
      this.$forceUpdate()
    },
    make_filter_index(filter, value) {
      return filter + ':' + value
    },
  },
}
</script>
