<script setup>
import { store } from '../store/store.js'
</script>

<template>
  <div class="lister_details menu_section" :class="{ 'no_root_folder': noRootFolder,  'error': isRootFolderError}">
    <details :open="noRootFolder || isRootFolderError">
      <summary>About this library</summary>
      <ul>
        <li v-if="noRootFolder" class="help_select_root_folder">
          Please enter your composition folder below.
        </li>
        <li class="root_folder">
          <span v-if="isRootFolderError" title="Please review folder">⚠️ </span>
          <span>Composition folder: </span>
          <input
            type="text"
            :placeholder="rootFolder"
            v-model="localRootFolder"
            name="localRootFolder"
          />
          <button @click="validateFolder" :disabled="!noRootFolder && localRootFolder === rootFolder">
            Validate
          </button>
        </li>
        <li v-if="!noRootFolder" class="database_file">
          Database file:
          <span class="text_information">{{ databaseFile }}</span>
        </li>
        <li v-if="!noRootFolder" class="number_of_compositions">
          Number of compositions: {{ numberOfCompositions }}
        </li>
      </ul>
    </details>
    <div class="refresh" v-if="!noRootFolder">
      <button
        id="refreshButton"
        title="Press letter 'r' to refresh"
        @click="store.refreshDatabaseAndFetchCompositions"
        :disabled="store.isLoading"
      >
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
  computed: {
    noRootFolder() {
      return store.noRootFolder()
    },
    isRootFolderError() {
      return store.isRefreshDatabaseError()
    }
  },
  async mounted() {
    await store.fetchAboutInfo()
    this.localRootFolder = store.rootFolder
    document.addEventListener('keyup', this.onKeyUp)
  },
  beforeDestroy() {
    document.removeEventListener('keyup', this.onKeyUp)
  },
  methods: {
    async validateFolder(event) {
      console.log('Validating folder:', this.localRootFolder)
      console.log('Previous folder:', store.rootFolder)
      store.rootFolder = this.localRootFolder
      await store.refreshDatabaseAndFetchCompositions()
    },
    async onKeyUp(event) {
      if (event.key == 'r' && !store.isLoading) {
        console.log("'r' pressed, refreshing compositions")
        store.refreshDatabaseAndFetchCompositions()
      }
    },
  },
}
</script>
