<script setup>
import { ref } from 'vue';
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
      <button id="refreshButton" @click="fetchCompositions" :disabled="refreshing">Refresh</button>
    </div>
  </div>
  <div class="compositions">
    <CompositionItem
      v-for="composition in sortedFilteredCompositions"
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
      :audio_file="composition['audio_file']"
      :last_activity="composition['last_activity']" />
  </div>
</template>

<script>
export default {
  data() {
    return {
      compositions: [],
      pollingInterval: null,
      sortBy: "",
      refreshing: false,
      onlyFinished: false,
      onlyInProgress: false,
    };
  },
  computed: {
    sortedFilteredCompositions() {
      // console.log("Sorting by:", this.sortBy);
      // // This can be expanded to return sorted IDs based on selected criteria
      let outputCompositions = this.compositions.slice(); // Create a copy of the array
      // if (this.sortBy === 'activity') {
      //   // Sort by last activity (assuming compositionIds have a lastActivity property)
      //   sortedCompositionIds = sortedCompositionIds.sort((a,b) => new Date(b.lastActivity) - new Date(a.lastActivity));
      // } else if (this.sortBy === 'status') {
      //   sortedCompositionIds = sortedCompositionIds.sort((a,b) => {
      //     console.log("Comparing status:", a, b);
      //     if (a.status === b.status) return 0;
      //     if (a.status === 'Finished') return 1;
      //     return -1;
      //   });
      // } else if (this.sortBy === 'title') {
      //   // Sort by title (assuming compositionIds have a title property)
      //   sortedCompositionIds = sortedCompositionIds.sort((a,b) => a.title.localeCompare(b.title));
      // } else if (this.sortBy === 'artist') {
      //   // Sort by artist (assuming compositionIds have an artist property)
      //   sortedCompositionIds = sortedCompositionIds.sort((a,b) => a.artist.localeCompare(b.artist));
      // } else if (this.sortBy === 'album') {
      //   // Sort by album (assuming compositionIds have an album property)
      //   sortedCompositionIds = sortedCompositionIds.sort((a,b) => a.album.localeCompare(b.album));
      // }
      // console.log("Sorted IDs:", sortedCompositionIds);
      return outputCompositions;
    },
  },
  mounted() {
    this.sortBy = 'activity';
  },
  created() {
    this.fetchCompositions();
  },
  methods: {
    sortCompositions() {
      this.$forceUpdate();
    },
    filterFinished() {
      this.$forceUpdate();
    },
    filterInProgress() {
      this.$forceUpdate();
    },
    async refresh_database() {
      console.log("Refreshing database...");
      try {
        const response = await fetch('http://localhost:5556/refresh_database');
        if (!response.ok) {
          throw new Error('Failed to fetch composition IDs');
        }
        const data = await response.json();
      } catch (error) {
        console.error('Error fetching composition IDs:', error);
      }
      console.log("Database refreshed.");
    },
    async fetchCompositions() {
      console.log("Fetching compositions...");
      this.refreshing = true;
      try {
        await this.refresh_database();
        const response = await fetch('http://localhost:5556/compositions');
        if (!response.ok) {
          throw new Error('Failed to fetch compositions');
        }
        const data = await response.json();
        this.$nextTick(() => {
          this.compositions = data; // Assuming the API returns an array of IDs
        });
      } catch (error) {
        console.error('Error fetching composition IDs:', error);
      }
      this.refreshing = false;
      console.log("Compositions fetched.");
    },
  }
}
</script>
