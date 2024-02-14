<template>
  <v-dialog v-model="registrationDialog">
    <v-card max-width="450px" width="100%" class="mx-auto pa-7">
      <v-alert
        v-if="registerAlert.text || registerAlert.title"
        color="error"
        icon="$error"
        :text="registerAlert.text"
        :title="registerAlert.title"
        class="ma-2"
      />
      <v-form validate-on="blur lazy" @submit.prevent="handleRegistrationClick">
        <v-text-field
          v-model="registrationFormRef.firstName"
          label="Vorname"
          :rules="nonEmptyRules('Vorname')"
        />
        <v-text-field
          v-model="registrationFormRef.lastName"
          label="Nachname"
          :rules="nonEmptyRules('Nachname')"
        />
        <v-text-field
          v-model="registrationFormRef.email"
          label="Email"
          :rules="emailRules"
        />
        <v-text-field
          class="mt-5"
          v-model="registrationFormRef.password"
          :type="showPassword1 ? 'text' : 'password'"
          :append-inner-icon="showPassword1 ? 'mdi-eye' : 'mdi-eye-off'"
          label="Passwort"
          counter
          validate-on="input"
          max-errors="10"
          :loading="true"
          :rules="passwordRules"
          @click:append-inner="showPassword1 = !showPassword1"
        >
          <template #loader="slotProps">
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
          class="mt-3"
          v-model="registrationFormRef.reentered_password"
          :type="showPassword2 ? 'text' : 'password'"
          :append-inner-icon="showPassword2 ? 'mdi-eye' : 'mdi-eye-off'"
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
          @click="registrationDialog = false"
          block
          class="mt-2"
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
const emailRules = [
  (email: string): boolean | string => {
    if (
      String(email)
        .toLowerCase()
        .match(
          /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|.(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
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
const passwordRules = [
  (password: string): boolean | string => {
    if (password.length >= 8) return true;
    return "Das Passwort muss mindestens 8 Zeichen lang sein";
  },
  (password: string): boolean | string => {
    if (password.match(/\d/) !== null) return true;
    return "Das Passwort muss mindestens 1 Zahl enthalten";
  },
  (password: string): boolean | string => {
    if (password.match(/[a-z]/) !== null) return true;
    return "Passwort muss mindestens 1 Kleinbuchstaben enthalten";
  },
  (password: string): boolean | string => {
    if (password.match(/[A-Z]/) !== null) return true;
    return "Passwort muss mindestens 1 Großbuchstaben enthalten";
  },
  (password: string): boolean | string => {
    if (password.match(/[^A-Za-z0-9]/) !== null) return true;
    return "Passwort muss mindestens 1 Sonderzeichen enthalten";
  },
];
const reenteredPasswordRules = [
  (password: string): boolean | string => {
    if (password === registrationFormRef.value.password) return true;
    return "Die Passwörter stimmen nicht überein";
  },
];

const showPassword1 = ref(false);
const showPassword2 = ref(false);
const registrationDialog = defineModel();
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
    for (let rule of passwordRules) {
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
      (successes / passwordRules.length) * 100
    );
  }
);

const registerAlert = ref({} as { title: string; text: string });
async function handleRegistrationClick(event: any) {
  loading.value = true;
  const results = await event;
  loading.value = false;
  if (results.valid) {
    try {
      const { reentered_password, ...formWithoutReentered } =
        registrationFormRef.value;
      const resp = await signUp(formWithoutReentered, { external: true });
      registerAlert.value = {} as { title: string; text: string };
    } catch (e: any) {
      switch (e.response.status) {
        case 406:
          registerAlert.value.title = "email existiert bereits!";
          break;
        default:
          registerAlert.value.title = "unbekannter Fehler: " + e.response;
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