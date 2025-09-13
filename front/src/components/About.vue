<script setup>
import { store } from '../store/store.js'
</script>

<template>
  <div class="lister_details menu_section">
    <details>
      <summary>About this library</summary>
      <ul>
        <li class="root_folder">
          Root folder:
          <input type="text" :placeholder="rootFolder" v-model="localRootFolder" />
          <button @click="validateFolder" :disabled="localRootFolder === rootFolder">
            Validate
          </button>
        </li>
        <li class="database_file">
          Database file:
          <span class="file_path">{{ databaseFile }}</span>
        </li>
        <li class="number_of_compositions">Number of compositions: {{ numberOfCompositions }}</li>
      </ul>
    </details>
    <div class="refresh">
      <button id="refreshButton" @click="syncCompositions" :disabled="store.isLoading">
        Refresh
      </button>
    </div>
  </div>
</template>

<script>
export default {
  props: ['rootFolder', 'databaseFile', 'numberOfCompositions'],
  data() {
    return {
      localRootFolder: '',
    }
  },
  async mounted() {
    await store.fetchAboutInfo()
    this.localRootFolder = this.rootFolder
  },
  methods: {
    async validateFolder(event) {
      console.log('Validating folder:', this.localRootFolder)
      console.log('Previous folder:', this.rootFolder)
      store.rootFolder = this.localRootFolder
    },
    async syncCompositions() {
      await store.refreshDatabase()
      await store.fetchCompositions()
    },
  },
}
</script>
