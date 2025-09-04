<script setup>
const props = defineProps(['compositionId'])
</script>

<template>
  <div
    :class="{ composition: true, finished: composition['status'] === 'Finished' }"
    :data-activity="composition['last_activity']"
    :data-status="composition['status']"
    :data-title="composition['name']"
    :data-album="composition['album']"
    :data-artist="composition['artist']"
  >
    <h2 class="songname">{{ composition["name"] }}</h2>
    <h3 class="artist">Artist: {{ composition["artist"] }}</h3>
    <h3 class="album">Album: {{ composition["album"] }}</h3>
    <p class="status">Status: {{ composition["status"] }}</p>
    <div class="activity_path">
      <p class="last_activity">Last modified: <span>{{ composition["last_activity"] }}</span></p>
      <p class="als_file_path">File path: <span>{{ composition["als_file_path"] }}</span></p>
      <p class="audio_file">Sound file exported</p>
    </div>
    <details>
      <summary>More info</summary>
      <table border="0" cellpadding="5">
        <tbody>
          <tr>
            <th>Lyrics</th>
            <td>{{ composition["lyrics"] }}</td>
          </tr>
          <tr>
            <th>Chords</th>
            <td>{{ composition["chords"] }}</td>
          </tr>
        </tbody>
      </table>
    </details>
  </div>
</template>

<script>
export default {
  data() {
    return {
      composition: [] // State to store the composition IDs
    };
  },
  created() {
    this.fetchComposition();
  },
  methods: {
    async fetchComposition() {
      try {
        const response = await fetch('http://localhost:3000/composition/id/' + this.compositionId);
        if (!response.ok) {
          throw new Error('Failed to fetch composition IDs');
        }
        const data = await response.json();
        this.composition = data; // Assuming the API returns an array of IDs
      } catch (error) {
        console.error('Error fetching composition IDs:', error);
      }
    }
  }
}
</script>
