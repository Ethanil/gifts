<template>
    <v-dialog max-width="450px">
        <template #activator="{ props }">
            <slot name="activator" :props="props"></slot>
        </template>
        <v-card width="100%" class="mx-auto pa-7">
            <v-container>
                <v-row justify="center"
                    ><span class="text-h5">Profil</span></v-row
                >
                <v-row justify="center">
                    <v-col>
                        <span
                            style="overflow-wrap: anywhere !important"
                            class="text-h5 d-flex justify-center"
                            >{{ (data as any)!.email }}
                        </span>
                    </v-col>
                </v-row>
                <v-row justify="center">
                    <v-avatar
                        v-if="avatarIsBase64"
                        size="106.5"
                        :image="formData.avatar"
                    />
                    <span v-else class="mr-1" v-html="generatedAvatar"></span>
                </v-row>
                <v-row>
                    <v-spacer />
                    <v-col>
                        <div class="d-flex justify-end">
                            <v-btn
                                color="primary"
                                icon="mdi-dice-6-outline"
                                @click="
                                    formData.avatar = (
                                        Math.random() + 1
                                    ).toString(36)
                                "
                            />
                        </div>
                    </v-col>
                    <v-col>
                        <div class="d-flex justify-start">
                            <v-btn
                                color="primary"
                                icon="mdi-upload"
                                @click="onButtonClick"
                            />
                            <input
                                ref="uploader"
                                class="d-none"
                                type="file"
                                accept="image/*"
                                @change="onFileChanged"
                            />
                        </div>
                    </v-col>
                    <v-spacer />
                </v-row>
            </v-container>

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
const uploader = ref(null);
function onButtonClick() {
    window.addEventListener("focus", () => {}, { once: true });
    if (uploader.value) (uploader.value as any).click();
}
function onFileChanged(e: any) {
    handleImageInput(e.target.files);

    // do something
}
const avatarIsBase64 = computed(
    () => formData.value.avatar.split(";").length === 2,
);
const generatedAvatar = computed(() =>
    avatar(formData.value.avatar, {
        size: 100,
        blackout: false,
    }).replaceAll("\n", ""),
);
async function handleImageInput(files: File[] | undefined) {
    if (!files || files.length != 1) {
        formData.value.avatar = (data.value as any)!.avatar;
        return;
    }
    const image = files[0];
    const type = image.type.split("/");
    if (type[0] !== "image" || (type[1] !== "jpeg" && type[1] !== "png")) {
        formData.value.avatar = (data.value as any)!.avatar;
        return;
    }
    const reader = new FileReader();
    reader.readAsDataURL(image);
    reader.onload = () => {
        formData.value.avatar = reader.result as string;
    };
}

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
            formData.value.avatar,
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
