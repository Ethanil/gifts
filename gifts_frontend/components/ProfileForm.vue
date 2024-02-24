<template>
    <v-dialog max-width="450px">
        <template #activator="{ props }">
            <slot name="activator" :props="props"></slot>
        </template>
        <v-card width="100%" class="mx-auto pa-7">
            <v-card-title>
                <v-container>
                    <v-row>
                        <v-col>Profil von {{ (data as any)!.email }}</v-col>
                        <v-spacer></v-spacer>
                        <v-col>
                            <v-container>
                                <v-row justify="center">
                                    <span
                                        class="mr-1"
                                        v-html="generatedAvatar"
                                    ></span>
                                </v-row>
                                <v-row justify="center"
                                    >
                                    <v-btn
                                        color="primary"
                                        icon="mdi-dice-6-outline"
                                        @click="
                                            formData.avatar = (
                                                Math.random() + 1
                                            )
                                                .toString(36)
                                        "
                                    />
                                </v-row>
                            </v-container>
                        </v-col>
                    </v-row>
                </v-container>
            </v-card-title>
            <v-form validate-on="blur lazy" @submit.prevent="saveProfile">
                <v-text-field
                    v-model="formData.oldPassword"
                    label="Aktuelles Passwort"
                    :type="showPasswords.oldPassword ? 'text' : 'password'"
                    :rules="[nonEmptyRule('Passwort')]"
                >
                    <template #append-inner>
                        <v-icon
                            :icon="
                                showPasswords.oldPassword
                                    ? 'mdi-eye'
                                    : 'mdi-eye-off'
                            "
                            class="cursor-pointer"
                            @mousedown="showPasswords.oldPassword = true"
                            @mouseup="showPasswords.oldPassword = false"
                            @touchstart="showPasswords.oldPassword = true"
                            @touchend="showPasswords.oldPassword = false"
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
                    v-model="formData.firstName"
                    label="Vorname"
                    :disabled="formData.oldPassword === ''"
                    :rules="[nonEmptyRule('Vorname')]"
                />
                <v-text-field
                    v-model="formData.lastName"
                    label="Nachname"
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
                    <template #loader>
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
                            :icon="
                                showPasswords.newPassword
                                    ? 'mdi-eye'
                                    : 'mdi-eye-off'
                            "
                            class="cursor-pointer"
                            @mousedown="showPasswords.newPassword = true"
                            @mouseup="showPasswords.newPassword = false"
                            @touchstart="showPasswords.newPassword = true"
                            @touchend="showPasswords.newPassword = false"
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
                    v-model="formData.reentered_newPassword"
                    label="Neues Passwort bestätigen"
                    :type="
                        showPasswords.reentered_newPassword
                            ? 'text'
                            : 'password'
                    "
                    class="mt-5"
                    :disabled="
                        formData.oldPassword === '' ||
                        formData.newPassword === ''
                    "
                    :rules="
                        formData.newPassword !== '' ||
                        formData.reentered_newPassword !== ''
                            ? [reenteredPasswordRule]
                            : []
                    "
                >
                    <template #append-inner>
                        <v-icon
                            :icon="
                                showPasswords.reentered_newPassword
                                    ? 'mdi-eye'
                                    : 'mdi-eye-off'
                            "
                            class="cursor-pointer"
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
import avatar from "animal-avatar-generator";
const { data } = useAuth();

const generatedAvatar = computed(() =>
    avatar(formData.value.avatar, {
        size: 100,
        blackout: false,
    }).replaceAll("\n", ""),
);

const formData = ref({
    firstName: (data.value as any)!.firstName,
    lastName: (data.value as any)!.lastName,
    oldPassword: "",
    newPassword: "",
    reentered_newPassword: "",
    avatar: (data.value as any)!.avatar,
});
const userStore = useUserStore();
async function saveProfile(event: any) {
    const results = await event;
    if (results.valid) {
        userStore.updateUser(
            formData.value.oldPassword,
            formData.value.firstName,
            formData.value.lastName,
            formData.value.newPassword,
            formData.value.avatar
        );
    }
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
