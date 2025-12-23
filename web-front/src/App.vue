<template>
  <router-view />
</template>

<script setup lang="ts">
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

#app {
  width: 100%;
  height: 100vh;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

/* 确保 Element Plus 容器全屏 */
.el-container {
  width: 100% !important;
  height: 100% !important;
}

.el-aside {
  height: 100% !important;
}

.el-main {
  width: 100% !important;
  height: 100% !important;
  overflow: auto;
}
</style>
