<template>
    <TopToolbar />
    <div>
        <DashboardCardLogin
            @update:registration-dialog="(val) => (registrationDialog = val)"
        />
        <DashboardCardRegister v-model="registrationDialog" />
    </div>
</template>
<script setup lang="ts">
definePageMeta({
    auth: { unauthenticatedOnly: true, navigateAuthenticatedTo: "/" },
});
const registrationDialog = ref(false);
</script>
