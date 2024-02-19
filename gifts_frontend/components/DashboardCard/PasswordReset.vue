<template>
    <v-dialog v-model="passwordResetDialog" max-width="450px">
        <v-card width="100%" class="mx-auto pa-7">
            <v-form
                v-if="!phase2Reset"
                validate-on="blur lazy"
                :loading="loading"
                @submit.prevent="sendResetMail"
            >
                <v-text-field
                    v-model="email"
                    label="Email"
                    :rules="[emailRule, nonEmptyRule('Email')]"
                />
                <v-btn color="primary" type="submit" block class="mt-2">
                    Passwort zurücksetzen
                </v-btn>
                <v-btn
                    color="primary"
                    block
                    class="mt-2"
                    @click="phase2Reset = true"
                >
                    Email Code eingeben
                </v-btn>
                <v-btn color="primary" block class="mt-2" @click="cancel">
                    Abbrechen
                </v-btn>
            </v-form>
            <v-form
                v-if="phase2Reset"
                validate-on="blur lazy"
                :loading="loading"
                @submit.prevent="resetPassword"
            >
                <v-text-field
                    v-model="emailCode"
                    label="Zeichenfolge aus der Email"
                    :rules="[nonEmptyRule('Zeichenfolge')]"
                />
                <v-text-field
                    v-model="email"
                    label="Email"
                    :rules="[emailRule, nonEmptyRule('Email')]"
                />
                <v-text-field
                    v-model="password"
                    class="mt-5"
                    :type="showPassword1 ? 'text' : 'password'"
                    :append-inner-icon="
                        showPassword1 ? 'mdi-eye' : 'mdi-eye-off'
                    "
                    label="Neues Passwort"
                    counter
                    validate-on="input"
                    max-errors="10"
                    :loading="true"
                    :rules="passwordRules"
                    @click:append-inner="showPassword1 = !showPassword1"
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
                </v-text-field>
                <v-text-field
                    v-model="reentered_password"
                    class="mt-3"
                    :type="showPassword2 ? 'text' : 'password'"
                    :append-inner-icon="
                        showPassword2 ? 'mdi-eye' : 'mdi-eye-off'
                    "
                    label="Passwort wiederholen"
                    counter
                    validate-on="input"
                    max-errors="10"
                    :rules="[
                        ...reenteredPasswordRules,
                        nonEmptyRule('Passwort'),
                    ]"
                    @click:append-inner="showPassword2 = !showPassword2"
                />
                <v-btn color="primary" type="submit" block class="mt-2">
                    Passwort setzen
                </v-btn>
                <v-btn color="primary" block class="mt-2" @click="cancel">
                    Abbrechen
                </v-btn>
            </v-form>
        </v-card>
    </v-dialog>
</template>
<script setup lang="ts">
const loading = ref(false);
// Phase 1:Send email
const passwordResetDialog = defineModel<boolean>();
const phase2Reset = ref(false);
const email = ref("");
const emailRule = (email: string): boolean | string => {
    if (
        String(email)
            .toLowerCase()
            .match(
                /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|.(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/,
            ) !== null
    )
        return true;
    return "Gültige Email eingeben";
};
// Phase 2: Set new password
const emailCode = ref("");
const password = ref("");
const reentered_password = ref("");
const showPassword1 = ref(false);
const showPassword2 = ref(false);

const reenteredPasswordRules = [
    (pw: string): boolean | string => {
        if (pw === password.value) return true;
        return "Die Passwörter stimmen nicht überein";
    },
];
const passwordStrengthColor = ref("red");
const passwordStrengthWidth = ref("0");
watch(
    () => password.value,
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
watch(
    () => passwordResetDialog.value,
    (newValue) => {
        if (!newValue)
            setTimeout(() => {
                phase2Reset.value = false;
            }, 100);
    },
);
function cancel() {
    passwordResetDialog.value = false;
    setTimeout(() => {
        phase2Reset.value = false;
    }, 100);
}

const userStore = useUserStore();

async function sendResetMail(event: any) {
    const results = await event;
    if (results.valid) {
        userStore.requestPasswordReset(email.value);
        phase2Reset.value = true;
    }
}
const { signIn } = useAuth();
async function resetPassword(event: any) {
    const results = await event;
    if (results.valid) {
        try {
            loading.value = true;
            userStore
                .resetPassword(email.value, password.value, emailCode.value)
                .then(async () => {
                    const _ = await signIn(
                        { email: email.value, password: password.value },
                        { external: true },
                    );
                });

        } catch (e: any) {
            console.log(e);
        } finally {
            loading.value = false;
            cancel();
        }
    }
}
</script>
