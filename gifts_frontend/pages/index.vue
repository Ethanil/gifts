<template>
    <div>
        <TopToolbar @icon-click="navBar = !navBar" />
        <GiftDashboard :nav-bar="navBar" />
    </div>
</template>
<script setup lang="ts">
const navBar = ref(true);
</script>
