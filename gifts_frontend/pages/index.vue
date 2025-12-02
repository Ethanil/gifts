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
const navBar = ref(false);
function navBarToggle() {
    navBar.value = !navBar.value;
}
onMounted(() => {
    localStorage.setItem("selectedTheme", "dark");
});
</script>
