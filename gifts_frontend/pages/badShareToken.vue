<template>
    <div>
        <v-btn color="primary" type="submit" block class="mt-2" to="/login">
            LOGIN
        </v-btn>
        Invalid Share Token, maybe it is not up to date anymore?
    </div>
</template>
<script setup lang="ts">
definePageMeta({
    auth: { unauthenticatedOnly: true, navigateAuthenticatedTo: "/" },
});
</script>
