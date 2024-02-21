<template>
    <v-dialog max-width="450px">
        <template #activator="{ props }">
            <slot name="activator" :props="props"></slot>
        </template>
        <v-card width="100%" class="mx-auto pa-7">
            <v-card-title
                >Profil von {{ (data as any)!.email }}</v-card-title
            >
            <v-form validate-on="blur lazy" @submit.prevent="saveProfile">
                <v-text-field
                    label="Aktuelles Passwort"
                    :type="showPasswords.oldPassword ? 'text' : 'password'"
                    v-model="formData.oldPassword"
                    :rules="[nonEmptyRule('Passwort')]"
                >
                    <template #append-inner>
                        <v-icon
                            @mousedown="showPasswords.oldPassword = true"
                            @mouseup="showPasswords.oldPassword = false"
                            @touchstart="showPasswords.oldPassword = true"
                            @touchend="showPasswords.oldPassword = false"
                            :icon="
                                showPasswords.oldPassword
                                    ? 'mdi-eye'
                                    : 'mdi-eye-off'
                            "
                            class="cursor-pointer"
                        />
                        <!-- <v-icon
                            @click="
                                showPasswords.oldPassword =
                                    !showPasswords.oldPassword
                            "
                            :icon="
                                showPasswords.oldPassword
                                    ? 'mdi-eye'
                                    : 'mdi-eye-off'
                            "
                            class="cursor-pointer"
                        /> -->
                    </template>
                </v-text-field>
                <v-text-field
                    label="Vorname"
                    v-model="formData.firstName"
                    :disabled="formData.oldPassword === ''"
                    :rules="[nonEmptyRule('Vorname')]"
                />
                <v-text-field
                    label="Nachname"
                    v-model="formData.lastName"
                    :disabled="formData.oldPassword === ''"
                    :rules="[nonEmptyRule('Nachname')]"
                />
                <v-text-field
                    v-model="formData.newPassword"
                    :type="showPasswords.newPassword ? 'text' : 'password'"
                    class="mt-5"
                    label="Neues Passwort"
                    counter
                    :loading="true"
                    :disabled="formData.oldPassword === ''"
                    :rules="
                        formData.newPassword !== '' ||
                        formData.reentered_newPassword !== ''
                            ? passwordRules
                            : []
                    "
                    max-errors="10"
                    validate-on="input"
                >
                    <template #loader="{ isActive }">
                        <div
                            :style="
                                'background-color: ' +
                                passwordStrengthColor +
                                '; width: ' +
                                passwordStrengthWidth +
                                '%;'
                            "
                            class="password-strength"
                        ></div>
                    </template>
                    <template #append-inner>
                        <v-icon
                            @mousedown="showPasswords.newPassword = true"
                            @mouseup="showPasswords.newPassword = false"
                            @touchstart="showPasswords.newPassword = true"
                            @touchend="showPasswords.newPassword = false"
                            :icon="
                                showPasswords.newPassword
                                    ? 'mdi-eye'
                                    : 'mdi-eye-off'
                            "
                            class="cursor-pointer"
                        />
                        <!-- <v-icon
                            v-else
                            @click="
                                showPasswords.newPassword =
                                    !showPasswords.newPassword
                            "
                            :icon="
                                showPasswords.newPassword
                                    ? 'mdi-eye'
                                    : 'mdi-eye-off'
                            "
                            class="cursor-pointer"
                        /> -->
                    </template>
                </v-text-field>
                <v-text-field
                    label="Neues Passwort bestätigen"
                    :type="
                        showPasswords.reentered_newPassword
                            ? 'text'
                            : 'password'
                    "
                    class="mt-5"
                    v-model="formData.reentered_newPassword"
                    :disabled="formData.oldPassword === '' || formData.newPassword === ''"
                    :rules="
                        formData.newPassword !== '' ||
                        formData.reentered_newPassword !== ''
                            ? [reenteredPasswordRule]
                            : []
                    "
                >
                    <template #append-inner>
                        <v-icon
                            @mousedown="
                                showPasswords.reentered_newPassword = true
                            "
                            @mouseup="
                                showPasswords.reentered_newPassword = false
                            "
                            @touchstart="
                                showPasswords.reentered_newPassword = true
                            "
                            @touchend="
                                showPasswords.reentered_newPassword = false
                            "
                            :icon="
                                showPasswords.reentered_newPassword
                                    ? 'mdi-eye'
                                    : 'mdi-eye-off'
                            "
                            class="cursor-pointer"
                        />
                        <!-- <v-icon
                            v-else
                            @click="
                                showPasswords.reentered_newPassword =
                                    !showPasswords.reentered_newPassword
                            "
                            :icon="
                                showPasswords.reentered_newPassword
                                    ? 'mdi-eye'
                                    : 'mdi-eye-off'
                            "
                            class="cursor-pointer"
                        /> -->
                    </template>
                </v-text-field>
                <v-btn type="submit" color="primary" class="mt-2">
                    Speichern
                </v-btn>
            </v-form>
        </v-card>
    </v-dialog>
</template>
<script setup lang="ts">
import { useDisplay } from "vuetify";
const { mobile } = useDisplay();
const { data } = useAuth();

function test(a: any) {
    console.log(a);
    showPasswords.value.oldPassword = true;
}

const formData = ref({
    firstName: (data.value as any)!.firstName,
    lastName: (data.value as any)!.lastName,
    oldPassword: "",
    newPassword: "",
    reentered_newPassword: "",
});
const userStore = useUserStore();
function saveProfile() {
    userStore.updateUser(
        formData.value.oldPassword,
        formData.value.firstName,
        formData.value.lastName,
        formData.value.newPassword,
    );
}
const reenteredPasswordRule = (password: string): boolean | string => {
    if (password === formData.value.newPassword) return true;
    return "Die Passwörter stimmen nicht überein";
};

const showPasswords = ref({
    oldPassword: false,
    newPassword: false,
    reentered_newPassword: false,
});
const passwordStrengthColor = ref("red");
const passwordStrengthWidth = ref("0");
watch(
    () => formData.value.newPassword,
    (newValue) => {
        let successes = 0;
        for (const rule of passwordRules) {
            if (rule(newValue) === true) successes++;
        }
        switch (successes) {
            case 2:
                passwordStrengthColor.value = "orange";
                break;
            case 3:
                passwordStrengthColor.value = "yellow";
                break;
            case 4:
                passwordStrengthColor.value = "green";
                break;
            case 5:
                passwordStrengthColor.value = "blue";
                break;
            default:
                passwordStrengthColor.value = "red";
                break;
        }
        passwordStrengthWidth.value = String(
            (successes / passwordRules.length) * 100,
        );
    },
);
</script>

<style lang="scss">
.password-strength {
    height: 4px;
    transition-property: width, background-color;
    transition-duration: 0.7s;
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 9999;
}
</style>
