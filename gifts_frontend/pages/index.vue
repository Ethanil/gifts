<template>
    <TopToolbar @icon-click="navBar=!navBar"/>
    <GiftDashboard :nav-bar="navBar" />
</template>
<script setup lang="ts">
const navBar = ref(true);
</script>
