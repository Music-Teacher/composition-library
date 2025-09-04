<script setup>
const props = defineProps(['aboutInfo'])
</script>

<template>
  <div class="lister_details">
    <details>
      <summary>About this list</summary>
      <ul>
        <li>Root folder: <span class="file_path">{{ props.aboutInfo["root_folder"] }}</span></li>
        <li>
          Output JSON file:
          <span class="file_path">{{ props.aboutInfo["output_json_file"] }}</span>
        </li>
        <li>Number of compositions: {{ props.aboutInfo["number_of_compositions"] }}</li>
      </ul>
    </details>
  </div>
</template>
