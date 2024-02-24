<template>
    <div>
        <TopToolbar @icon-click="navBarToggle" />
        <GiftDashboard
            :nav-bar-toggle="navBar"
            @nav-bar-toggle="navBarToggle"
        />
    </div>
</template>
<script setup lang="ts">
const navBar = ref(true);
function navBarToggle() {
    navBar.value = !navBar.value;
}
</script>
