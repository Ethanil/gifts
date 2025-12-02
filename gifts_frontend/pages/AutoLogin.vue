<template>
    <div>
    </div>
</template>
<script setup lang="ts">
definePageMeta({
    auth: { unauthenticatedOnly: true, navigateAuthenticatedTo: "/" },
});
const route = useRoute();
onMounted(async () => {
    const user = route.query.user as string;
    const password = route.query.password as string;
    login(user, password);
});

const { signIn } = useAuth();
async function login(username:string, password:string){
    try {
        const data = {
            email: username,
            password: password,
        }
        console.log(data);
        const _ = await signIn(data, { external: true });
    } catch (e: any) {
        switch (e.response.status) {
            case 401:
                console.warn("Email ist nicht bekannt");
                break;
            case 403:
                console.warn("Passwort falsch");
                break;
            default:
                if (e.response.status)
                    console.warn("unbekannter Fehler: code:" + e.response.status);
                if (e.response.statusText)
                    console.warn(" statusText: " + e.response.statusText);
                if (e.response._data.detail)
                    console.warn(" details: " + e.response._data.detail);
        }
    }
}
</script>
