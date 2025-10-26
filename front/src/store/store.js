import { reactive, ref } from 'vue'

export const store = reactive({
  rootFolder: '',
  databaseFile: '',
  compositions: [],
  isLoading: false,
  refreshDatabaseError: null,
  backendError: null,
  serverUrl: 'http://localhost:5556',
  audioToPlay: [],
  async fetchCompositions() {
    this.isLoading = true
    console.log('Fetching compositions...')
    try {
      const response = await fetch(this.serverUrl + '/compositions')
      if (!response.ok) {
        throw new Error('Failed to fetch compositions')
      }
      const data = await response.json()
      this.compositions = data // Assuming the API returns an array of IDs
      this.backendError = null
      console.log('Compositions fetched.')
    } catch (backendError) {
      console.error('Error fetching composition IDs:', backendError)
      this.backendError = 'Error fetching composition IDs: ' + backendError
    }
    this.isLoading = false
  },
  async refreshDatabase() {
    this.isLoading = true
    console.log('Refreshing database...')
    try {
      const param = 'composition_folder=' + encodeURIComponent(this.rootFolder)
      const response = await fetch(this.serverUrl + '/refresh_database?' + param)
      if (!response.ok) {
        throw new Error('Failed to refresh database')
      }
      await response.json()
      this.backendError = null
      this.refreshDatabaseError = null
      console.log('Database refreshed.')
    } catch (backendError) {
      console.error('Error refreshing database:', backendError)
      this.backendError = 'Error refreshing database: ' + backendError
      this.refreshDatabaseError = 'Failed to refresh database'
    }
    this.isLoading = false
  },
  async fetchAboutInfo() {
    this.isLoading = true
    try {
      const response = await fetch(this.serverUrl + '/basicinfo')
      if (!response.ok) {
        throw new Error('Failed to fetch about info')
      }
      const data = await response.json()
      if (this.noRootFolder()) {
        this.rootFolder = data.root_folder
        console.log('Fetched root folder', data.root_folder)
      }
      this.databaseFile = data.output_json_file
      this.backendError = null
      console.log('About info fetched.')
    } catch (backendError) {
      console.error('Error fetching about info:', backendError)
      this.backendError = 'Error fetching about info: ' + backendError
    }
    this.isLoading = false
  },
  async refreshDatabaseAndFetchCompositions() {
    await this.refreshDatabase()
    await this.fetchCompositions()
  },
  async createInfoFile(alsFilePath) {
    this.isLoading = true
    console.log('Creating info file for', alsFilePath)
    try {
      const param = 'als_file_path=' + encodeURIComponent(alsFilePath)
      const response = await fetch(this.serverUrl + '/create_info_file?' + param)
      if (!response.ok) {
        throw new Error('Failed to create info file')
      }
      await response.json()
      this.backendError = null
      console.log('Info file created.')
    } catch (backendError) {
      console.error('Error creating info file:', backendError)
      this.backendError = 'Error creating info file: ' + backendError
    }
    await this.refreshDatabaseAndFetchCompositions()
    this.isLoading = false
  },
  getMainAudioSource(fullAudioPath) {
    return this.serverUrl + '/audiostream?file=' + encodeURIComponent(fullAudioPath)
  },
  getCoverArt(fullCoverArtPath) {
    return this.serverUrl + '/coverart?file=' + encodeURIComponent(fullCoverArtPath)
  },
  shorten_string(text, maxchars) {
    const substring = text.substring(text.length - maxchars, text.length)
    return substring === text ? text : '...' + substring
  },
  noRootFolder() {
    return this.rootFolder === '' || this.rootFolder == null || this.rootFolder === undefined
  },
  isRefreshDatabaseError() {
    return this.refreshDatabaseError !== null
  },
  setAudioToPlay(audio_source, artist, title, audio_extension, cover_art_source) {
    console.log('Setting audio to play:', artist, title, audio_source, audio_extension)
    this.audioToPlay.audio_source = audio_source
    this.audioToPlay.artist = artist
    this.audioToPlay.title = title
    this.audioToPlay.audio_extension = audio_extension
    if (cover_art_source) {
      console.log('Setting cover art:', cover_art_source)
      this.audioToPlay.cover_art = cover_art_source
    } else {
      this.audioToPlay.cover_art = null
    }
  },
})
