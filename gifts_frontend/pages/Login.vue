<template>
    <div>
        <TopToolbar />
        <div>
            <DashboardCardLogin
                @update:registration-dialog="
                    (val) => (registrationDialog = val)
                "
                @update:password-reset-dialog="
                    (val) => (passwordResetDialog = val)
                "
            />
            <DashboardCardRegister v-model="registrationDialog" />
            <DashboardCardPasswordReset v-model="passwordResetDialog" />
        </div>
    </div>
</template>
<script setup lang="ts">
definePageMeta({
    auth: { unauthenticatedOnly: true, navigateAuthenticatedTo: "/" },
});
const registrationDialog = ref(false);
const passwordResetDialog = ref(false);
</script>
