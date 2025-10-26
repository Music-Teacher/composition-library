<script setup>
import { RouterLink, RouterView } from 'vue-router'
import Header from './components/Header.vue'
import Player from './components/Player.vue'
</script>

<template>
  <header>
    <div class="wrapper">
      <Header />
      <!-- <nav>
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/about">About</RouterLink>
      </nav> -->
    </div>
  </header>
  <RouterView />
  <Player />
</template>

<style src="./assets/design.css" scoped></style>
