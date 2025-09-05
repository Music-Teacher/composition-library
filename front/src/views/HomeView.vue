<script setup>
import About from '../components/About.vue'
import CompositionGrid from '../components/CompositionGrid.vue'
</script>

<template>
  <main>
    <About :aboutInfo="aboutInfo" />
    <CompositionGrid :compositionIds="compositionIds" />
  </main>
</template>

<script>
export default {
  data() {
    return {
      compositionIds: [], // State to store the composition IDs
      aboutInfo: [] // State to store the basic composition info
    };
  },
  created() {
    this.fetchCompositionIds();
    this.fetchAboutInfo();
  },
  methods: {
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
    async fetchAboutInfo() {
      try {
        const response = await fetch('http://localhost:5556/basicinfo');
        if (!response.ok) {
          throw new Error('Failed to fetch basic info');
        }
        const data = await response.json();
        this.aboutInfo = data; // Assuming the API returns an array of IDs
        this.aboutInfo["number_of_compositions"] = this.compositionIds.length;
      } catch (error) {
        console.error('Error fetching composition IDs:', error);
      }
    }
  }
}
</script>