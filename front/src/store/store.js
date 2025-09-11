import { reactive, ref } from 'vue'

export const store = reactive({
  rootFolder: '',
  databaseFile: '',
  compositions: [],
  isLoading: false,
  error: null,
  serverUrl: 'http://localhost:5556',
  async fetchCompositions() {
    console.log('Fetching compositions...')
    try {
      const response = await fetch(this.serverUrl + '/compositions')
      if (!response.ok) {
        throw new Error('Failed to fetch compositions')
      }
      const data = await response.json()
      this.compositions = data // Assuming the API returns an array of IDs
    } catch (error) {
      console.error('Error fetching composition IDs:', error)
    }
    console.log('Compositions fetched.')
    this.isLoading = false
  },
  async refreshDatabase() {
    this.isLoading = true
    console.log('Refreshing database...')
    try {
      const param = 'composition_folder=' + encodeURIComponent(this.rootFolder)
      const response = await fetch(this.serverUrl + '/refresh_database?' + param)
      if (!response.ok) {
        throw new Error('Failed to fetch composition IDs')
      }
      const data = await response.json()
    } catch (error) {
      console.error('Error fetching composition IDs:', error)
    }
    console.log('Database refreshed.')
    this.isLoading = false
  },
  async fetchAboutInfo() {
    try {
      const response = await fetch(this.serverUrl + '/basicinfo')
      if (!response.ok) {
        throw new Error('Failed to fetch basic info')
      }
      const data = await response.json()
      this.rootFolder = data.root_folder
      this.databaseFile = data.output_json_file
    } catch (error) {
      console.error('Error fetching composition IDs:', error)
    }
  },
  getMainAudioSource(fullAudioPath) {
    return this.serverUrl + '/audiostream?file=' + encodeURIComponent(fullAudioPath)
  },
})
