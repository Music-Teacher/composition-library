import { ref } from 'vue'

export function useServerUrl () {
  const serverUrl = ref("http://localhost:5556");
  return { serverUrl };
}

export function useFetchCompositionIds() {
  const compositionIds = ref([])

  const fetchCompositionIds = async () => {
    try {
      const serverUrl = useServerUrl().serverUrl.value;
      const response = await fetch(serverUrl + "/compositions/ids");
      if (!response.ok) {
        throw new Error('Failed to fetch composition IDs');
      }
      const data = await response.json();
      compositionIds.value = data;
    } catch (error) {
      console.error('Error fetching composition IDs:', error);
    }
  }
  fetchCompositionIds();
  console.log("Fetched composition IDs:", compositionIds.value);

  return { compositionIds };
}

export function useSyncCompositions() {
  const syncCompositions = async () => {
    try {
      const serverUrl = useServerUrl().serverUrl.value;
      const response = await fetch(serverUrl + "/refresh_database");
      if (!response.ok) {
        throw new Error('Failed to refresh database');
      }
      const data = await response.json();
    } catch (error) {
      console.error('Error refreshing database:', error);
    }
  }
  syncCompositions();
}
