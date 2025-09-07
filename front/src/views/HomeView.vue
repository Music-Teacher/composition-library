<script setup>
import About from '../components/About.vue'
import CompositionGrid from '../components/CompositionGrid.vue'
</script>

<template>
  <main>
    <About :aboutInfo="aboutInfo" />
    <CompositionGrid />
  </main>
</template>

<script>
export default {
  data() {
    return {
      aboutInfo: [] // State to store the basic composition info
    };
  },
  created() {
    this.fetchAboutInfo();
  },
  methods: {
    async fetchAboutInfo() {
      try {
        const response = await fetch('http://localhost:5556/basicinfo');
        if (!response.ok) {
          throw new Error('Failed to fetch basic info');
        }
        const data = await response.json();
        this.aboutInfo = data; // Assuming the API returns an array of IDs
      } catch (error) {
        console.error('Error fetching composition IDs:', error);
      }
    }
  }
}
</script>