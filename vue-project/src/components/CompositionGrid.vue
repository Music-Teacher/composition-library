<script setup>
</script>

<template>
  <div class="controls">
    <div class="sort">
      <label for="sortSelect">Sort by: </label
      ><select id="sortSelect">
        <option value="activity">Last activity</option>
        <option value="status">Status</option>
        <option value="title">Title</option>
        <option value="artist">Artist</option>
        <option value="album">Album</option>
      </select>
    </div>
    <div class="filter">
      Only show: <label><input id="showFinished" type="checkbox" /><span>Finished</span></label
      ><label><input id="showNotFinished" type="checkbox" /><span>In Progress</span></label>
    </div>
  </div>
  <div class="compositions">
    
  </div>
</template>

<script>
  export default {
    mounted() {
      let sortFilterScript = document.createElement('script')
      sortFilterScript.setAttribute('src', './src/assets/sortfilter.js')
      document.head.appendChild(sortFilterScript)
    },
  }
</script>
