import { reactive, ref } from 'vue'

export const store = reactive({
  rootFolder: '',
  databaseFile: '',
  compositions: [],
  isLoading: false,
  error: null,
  async fetchCompositions() {
    console.log("Fetching compositions...");
    try {
      const response = await fetch('http://localhost:5556/compositions');
      if (!response.ok) {
        throw new Error('Failed to fetch compositions');
      }
      const data = await response.json();
      this.compositions = data; // Assuming the API returns an array of IDs
    } catch (error) {
      console.error('Error fetching composition IDs:', error);
    }
    console.log("Compositions fetched.");
    this.isLoading = false;
  },
  async refreshDatabase() {
    this.isLoading = true;
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
    this.isLoading = false;
  },
  async fetchAboutInfo() {
    try {
      const response = await fetch('http://localhost:5556/basicinfo');
      if (!response.ok) {
        throw new Error('Failed to fetch basic info');
      }
      const data = await response.json();
      this.rootFolder = data.root_folder;
      this.databaseFile = data.output_json_file;
    } catch (error) {
      console.error('Error fetching composition IDs:', error);
    }
  }
})
