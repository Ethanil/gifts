<template>
    <div>
        <TopToolbar @icon-click="navBarToggle" />
        <GuestList></GuestList>
    </div>
</template>
<script setup lang="ts">
const navBar = ref(true);
function navBarToggle() {
    navBar.value = !navBar.value;
}
onMounted(() => {
    localStorage.setItem("selectedTheme", "dark");
});
</script>
