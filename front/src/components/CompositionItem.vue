<script setup>
</script>

<template>
  <div :class="{ composition: true, finished: status === 'Finished' }">
    <h2 class="songname">{{ name }}</h2>
    <h3 class="artist">Artist: {{ artist }}</h3>
    <h3 class="album">Album: {{ album }}</h3>
    <p class="status">Status: {{ status }}</p>
    <div class="activity_path">
      <p class="last_activity">Last modified: <span>{{ last_activity }}</span></p>
      <p class="als_file_path">File path: <span>{{ als_file_path }}</span></p>
      <p class="audio_file">
        <audio controls v-if="audio_file">
          <source :src="audio_source" :type="'audio/'+audio_extension" />
        </audio>
        <span v-else>Sound file exported</span>
      </p>
    </div>
    <details>
      <summary>More info</summary>
      <table border="0" cellpadding="5">
        <tbody>
          <tr>
            <th>Lyrics</th>
            <td>{{ lyrics }}</td>
          </tr>
          <tr>
            <th>Chords</th>
            <td>{{ chords }}</td>
          </tr>
        </tbody>
      </table>
    </details>
  </div>
</template>

<script>
export default {
  props: [
    'id',
    'name',
    'artist',
    'album',
    'ep',
    'lyrics',
    'chords',
    'extra_info',
    'status',
    'rework',
    'als_file_path',
    'project_dir',
    'root_folder',
    'als_file_name',
    'audio_file',
    'last_activity'
  ],
  computed: {
    audio_source() {
      return this.audio_file ? `http://localhost:5556/composition/${this.id}/audio` : null;
    },
    audio_extension() {
      if (this.audio_file) {
        const parts = this.audio_file.split('.');
        return parts.length > 1 ? parts[parts.length - 1] : null;
      }
      return null;
    }
  },
  // mounted() {
  //   if (this.audio_file) {
  //     this.importAudio();
  //   } 
  // },
  // methods: {
  //   async importAudio() {
  //     if (this.audio_file) {
  //       console.log("Importing audio file:", this.audio_file);
  //       this.audio_source = await import("../hello.wav");
  //     }
  //     console.log("Importing music");
  //     try {
  //       const response = await fetch('http://localhost:5556/refresh_database');
  //       if (!response.ok) {
  //         throw new Error('Failed to fetch composition IDs');
  //       }
  //       const data = await response.json();
  //     } catch (error) {
  //       console.error('Error fetching composition IDs:', error);
  //     }
  //     console.log("Database refreshed.");
  //   }
  // }
}
</script>
