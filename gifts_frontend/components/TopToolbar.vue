<template>
    <div>
        <v-app-bar density="compact" color="primary">
            <template #prepend>
                <v-app-bar-nav-icon @click="emit('iconClick')" />
            </template>

            <template #append>
                <BottomLegend />
                <div style="flex-wrap: nowrap">
                    <v-menu
                        transition="slide-y-transition"
                        location="bottom"
                        open-on-click
                        :close-on-content-click="false"
                    >
                        <template #activator="{ props }">
                            <v-btn icon v-bind="props">
                                <v-icon> mdi-dots-vertical </v-icon>
                            </v-btn>
                        </template>
                        <div>
                            <v-card>
                                <v-list>
                                    <ProfileForm
                                        v-if="
                                            status === 'authenticated' &&
                                            isFullUser
                                        "
                                    >
                                        <template #activator="{ props }">
                                            <v-list-item
                                                class="px-4"
                                                prepend-icon="mdi-account"
                                                v-bind="props"
                                            >
                                                {{ (data as any).firstName }}
                                                {{ (data as any).lastName }}
                                            </v-list-item>
                                        </template>
                                    </ProfileForm>
                                </v-list>
                                <v-divider v-if="status === 'authenticated'" />
                                <v-list>
                                    <v-list-item>
                                        <v-list-item-action class="mx-1">
                                            <v-switch
                                                v-model="
                                                    theme.global.current.value
                                                        .dark
                                                "
                                                append-icon="mdi-weather-night"
                                                prepend-icon="mdi-white-balance-sunny"
                                                @click.stop="toggleTheme"
                                            />
                                        </v-list-item-action>
                                    </v-list-item>
                                    <v-list-item
                                        v-if="status === 'authenticated'"
                                        prepend-icon="mdi-logout"
                                        to="/login"
                                        @click="logout"
                                    >
                                        <v-list-item-title>
                                            Logout
                                        </v-list-item-title>
                                    </v-list-item>
                                </v-list>
                            </v-card>
                        </div>
                    </v-menu>
                </div>
            </template>
            <div
                v-if="status === 'authenticated'"
                class="d-flex align-center ga-2"
            >
                <v-btn
                    variant="tonal"
                    elevation="1"
                    :to="{ path: '/', query: route.query }"
                    class="px-2 px-sm-4"
                    min-width="0"
                >
                    <v-icon>mdi-gift</v-icon>
                    <span class="d-none d-sm-inline ms-2">Geschenke</span>
                </v-btn>

                <v-btn
                    v-if="isFullUser"
                    variant="tonal"
                    elevation="1"
                    :to="{ path: '/guestManagement' }"
                    class="px-2 px-sm-4"
                    min-width="0"
                >
                    <v-icon>mdi-account-group</v-icon>
                    <span class="d-none d-sm-inline ms-2">Gast Verwaltung</span>
                </v-btn>
            </div>
            <router-link
                v-else
                style="text-decoration: none; color: inherit"
                to="/"
            >
                <v-toolbar-title>Geschenke</v-toolbar-title>
            </router-link>
        </v-app-bar>
    </div>
</template>

<script setup lang="ts">
const emit = defineEmits(["iconClick", "openProfile"]);
import { useTheme } from "vuetify";
const { signOut, status, data } = useAuth();
const isFullUser = computed(
    () => !(data.value as unknown as User)?.onlyViewing || false,
);
async function logout() {
    await signOut();
}
const theme = useTheme();
function toggleTheme() {
    const selectedTheme = theme.global.current.value.dark ? "light" : "dark";
    localStorage.setItem("selectedTheme", selectedTheme);
    theme.global.name.value = selectedTheme;
}

const route = useRoute();
</script>

<style></style>
