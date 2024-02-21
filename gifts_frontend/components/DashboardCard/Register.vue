<template>
    <v-dialog v-model="registrationDialog" max-width="450px">
        <v-card width="100%" class="mx-auto pa-7">
            <v-alert
                v-if="registerAlert.text || registerAlert.title"
                color="error"
                icon="$error"
                :text="registerAlert.text"
                :title="registerAlert.title"
                class="ma-2"
            />
            <v-form
                validate-on="blur lazy"
                @submit.prevent="handleRegistrationClick"
            >
                <v-text-field
                    v-model="registrationFormRef.firstName"
                    label="Vorname"
                    :rules="[nonEmptyRule('Vorname')]"
                />
                <v-text-field
                    v-model="registrationFormRef.lastName"
                    label="Nachname"
                    :rules="[nonEmptyRule('Nachname')]"
                />
                <v-text-field
                    v-model="registrationFormRef.email"
                    label="Email"
                    :rules="[emailRule()]"
                />
                <v-text-field
                    v-model="registrationFormRef.password"
                    class="mt-5"
                    :type="showPassword1 ? 'text' : 'password'"
                    :append-inner-icon="
                        showPassword1 ? 'mdi-eye' : 'mdi-eye-off'
                    "
                    label="Passwort"
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
                    v-model="registrationFormRef.reentered_password"
                    class="mt-3"
                    :type="showPassword2 ? 'text' : 'password'"
                    :append-inner-icon="
                        showPassword2 ? 'mdi-eye' : 'mdi-eye-off'
                    "
                    label="Passwort"
                    counter
                    validate-on="input"
                    max-errors="10"
                    :rules="reenteredPasswordRules"
                    @click:append-inner="showPassword2 = !showPassword2"
                />
                <v-btn
                    color="primary"
                    :loading="loading"
                    type="submit"
                    block
                    class="mt-2"
                >
                    Registrieren
                </v-btn>
                <v-btn
                    color="primary"
                    :loading="loading"
                    block
                    class="mt-2"
                    @click="registrationDialog = false"
                >
                    Schließen
                </v-btn>
            </v-form>
        </v-card>
    </v-dialog>
</template>
<script setup lang="ts">
const loading = ref(false);
const { signUp } = useAuth();

const reenteredPasswordRules = [
    (password: string): boolean | string => {
        if (password === registrationFormRef.value.password) return true;
        return "Die Passwörter stimmen nicht überein";
    },
];

const showPassword1 = ref(false);
const showPassword2 = ref(false);
const registrationDialog = defineModel<boolean>();
const registrationFormRef = ref({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    reentered_password: "",
});

const passwordStrengthColor = ref("red");
const passwordStrengthWidth = ref("0");
watch(
    () => registrationFormRef.value.password,
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

const registerAlert = ref({} as { title: string; text: string });
async function handleRegistrationClick(event: any) {
    loading.value = true;
    const results = await event;
    loading.value = false;
    if (results.valid) {
        try {
            // eslint-disable-next-line @typescript-eslint/no-unused-vars
            const { reentered_password, ...formWithoutReentered } =
                registrationFormRef.value;
            const _ = await signUp(formWithoutReentered, { external: true });
            registerAlert.value = {} as { title: string; text: string };
        } catch (e: any) {
            switch (e.response.status) {
                case 406:
                    registerAlert.value.title = "email existiert bereits!";
                    break;
                default:
                    registerAlert.value.title =
                        "unbekannter Fehler: " + e.response;
            }
        }
    }
}
</script>

<style lang="scss">
.password-strength {
    height: 4px;
    transition-property: width, background-color;
    transition-duration: 0.7s;
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
