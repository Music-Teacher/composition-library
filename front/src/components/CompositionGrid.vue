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
      <span v-for="(information, filter) in filtersAvailable">
        {{ filter[0].toUpperCase() + filter.slice(1) }}:
        <label v-for="value in information[0]">
          <input
            v-model="filtersSelected[make_filter_index(filter, value)]"
            @change="toggleFilter(filter, value, information[1])"
            type="checkbox"
          />
          <span>{{ value }}</span>
        </label>
      </span>
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
    }
  },
  computed: {
    filtersAvailable() {
      const filters = ['status', 'artist', 'album', 'ep']
      let filtersAvailable = {}
      filters.forEach((filter) => {
        const filterValues = this.uniqueFilterArray(filter)
        if (filterValues.length >= 2) {
          const exclusive = filterValues.length == 2 ? true : false
          filtersAvailable[filter] = [filterValues, exclusive]
        }
      })
      return filtersAvailable
    },
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
      let outputCompositions = store.compositions.slice()

      // Whole filtering
      outputCompositions = outputCompositions.filter((c) => {
        let categoryMatch = {}
        for (let filter in this.filtersSelected) {
          const filterName = filter.split(':')[0]
          const filterValue = filter.split(':')[1]
          if (!!this.filtersSelected[filter]) {
            if (c[filterName] === filterValue) {
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
            returnValue = a[this.sortBy].localeCompare(b[this.sortBy])
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
    uniqueFilterArray(key) {
      const array = store.compositions.filter((c) => !!c[key]).map((c) => c[key])
      return [...new Set(array)]
    },
    toggleFilter(filter, value, exclusive) {
      if (!!exclusive) {
        this.filtersAvailable[filter][0].forEach((e) => {
          if (e !== value) {
            this.filtersSelected[this.make_filter_index(filter, e)] = false
          }
        })
      }
      console.log(this.filtersSelected)
    },
    make_filter_index(filter, value) {
      return filter + ':' + value
    },
  },
}
</script>
