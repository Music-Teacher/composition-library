<script setup>
import { store } from '../store/store.js'
import About from '../components/About.vue'
import CompositionGrid from '../components/CompositionGrid.vue'
</script>

<template>
  <main>
    <About
      :rootFolder="store.rootFolder"
      :databaseFile="store.databaseFile"
      :numberOfCompositions="store.compositions.length"
    />
    <CompositionGrid />
  </main>
</template>

<script>
</script>