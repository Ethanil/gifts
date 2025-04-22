<template>
    <div>
        <v-btn color="primary" type="submit" block class="mt-2" to="/login">
            LOGIN
        </v-btn>
        <GiftDashboard
            :nav-bar-toggle="navBar"
            @nav-bar-toggle="navBarToggle"
        />
    </div>
</template>
<script setup lang="ts">
definePageMeta({
    auth: { unauthenticatedOnly: true, navigateAuthenticatedTo: "/" },
});
const navBar = ref(true);
function navBarToggle() {
    navBar.value = !navBar.value;
}
onMounted(() => {
    localStorage.setItem("selectedTheme", "dark");
});
</script>
