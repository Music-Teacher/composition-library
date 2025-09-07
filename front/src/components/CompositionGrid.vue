<script setup>
import CompositionItem from './CompositionItem.vue'

const props = defineProps(['compositionIds'])
</script>

<template>
  <div class="controls">
    <div class="sort">
      <label for="sortSelect">Sort by: </label
      ><select id="sortSelect">
        <option value="activity">Last activity</option>
        <option value="status">Status</option>
        <option value="title">Title</option>
        <option value="artist">Artist</option>
        <option value="album">Album</option>
      </select>
    </div>
    <div class="filter">
      Only show: <label><input id="showFinished" type="checkbox" /><span>Finished</span></label
      ><label><input id="showNotFinished" type="checkbox" /><span>In Progress</span></label>
    </div>
    <div class="refresh">
      <button id="refreshButton" @click="refresh">Refresh</button>
    </div>
  </div>
  <div class="compositions">
    <CompositionItem
      v-for="id in compositionIds"
      :key="id" 
      :compositionId="id" />
  </div>
</template>

<script>
export default {
  mounted() {
    let sortFilterScript = document.createElement('script');
    sortFilterScript.setAttribute('src', './src/assets/sortfilter.js');
    document.head.appendChild(sortFilterScript);
  },
  creayted() {
    this.fetchCompositionIds();
  },
  methods: {
    async refresh() {
      try {
        const response = await fetch('http://localhost:5556/refresh');
        if (!response.ok) {
          throw new Error('Failed to fetch composition IDs');
        }
        const data = await response.json();
      } catch (error) {
        console.error('Error fetching composition IDs:', error);
      }
      this.fetchCompositionIds();
    },
    async fetchCompositionIds() {
      try {
        const response = await fetch('http://localhost:5556/compositions/ids');
        if (!response.ok) {
          throw new Error('Failed to fetch composition IDs');
        }
        const data = await response.json();
        this.compositionIds = data; // Assuming the API returns an array of IDs
      } catch (error) {
        console.error('Error fetching composition IDs:', error);
      }
    },
  }
}
</script>
