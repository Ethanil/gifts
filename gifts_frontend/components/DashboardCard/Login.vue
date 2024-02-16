<template>
    <v-card
        variant="outlined"
        max-width="450"
        width="100%"
        class="mx-auto my-5 pa-5"
    >
        <v-alert
            v-if="loginAlert.text || loginAlert.title"
            color="error"
            icon="$error"
            :text="loginAlert.text"
            :title="loginAlert.title"
            class="ma-2"
        />
        <v-form validate-on="blur" @submit.prevent="handleLoginClick">
            <v-text-field
                v-model="loginFormRef.email"
                prepend-inner-icon="mdi-email-outline"
                label="Email"
                :rules="emailRules"
            />
            <v-text-field
                v-model="loginFormRef.password"
                prepend-inner-icon="mdi-lock-outline"
                :append-inner-icon="
                    showLoginPassword ? 'mdi-eye' : 'mdi-eye-off'
                "
                :type="showLoginPassword ? 'test' : 'password'"
                label="Passwort"
                :rules="nonEmptyRules('Passwort')"
                @click:append-inner="showLoginPassword = !showLoginPassword"
            />
            <v-btn
                color="primary"
                :loading="loading"
                type="submit"
                block
                class="mt-2"
            >
                Login
            </v-btn>
            <v-card-text class="text-center">
                <span
                    color="primary"
                    class="cursor-pointer text-primary"
                    @click="emit('update:registrationDialog', true)"
                >
                    Jetzt Registrieren <v-icon icon="mdi-chevron-right" />
                </span>
            </v-card-text>
        </v-form>
    </v-card>
</template>
<script setup lang="ts">
const emit = defineEmits(["update:registrationDialog"]);
const loading = ref(false);
const { signIn } = useAuth();

const emailRules = [
    (email: string): boolean | string => {
        if (
            String(email)
                .toLowerCase()
                .match(
                    /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|.(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/,
                ) !== null
        )
            return true;
        return "Gültige Email eingeben";
    },
];
function nonEmptyRules(value: string) {
    return [
        (input: string): boolean | string => {
            if (input) return true;
            return value + " eingeben";
        },
    ];
}

const loginAlert = ref({} as { title: string; text: string });
const showLoginPassword = ref(false);
const loginFormRef = ref({
    email: "",
    password: "",
});
async function handleLoginClick(event: any) {
    loading.value = true;
    const results = await event;
    loading.value = false;
    if (results.valid) {
        try {
            const _ = await signIn(loginFormRef.value, { external: true });
            loginAlert.value = {} as { title: string; text: string };
        } catch (e: any) {
            switch (e.response.status) {
                case 401:
                    loginAlert.value.title = "Email ist nicht bekannt";
                    break;
                case 403:
                    loginAlert.value.title = "Passwort falsch";
                    break;
                default:
                    loginAlert.value.title =
                        "unbekannter Fehler: " + e.response;
            }
        }
    }
}
</script>
