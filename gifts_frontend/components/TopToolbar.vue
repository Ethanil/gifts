<template>
    <div>
        <v-app-bar density="compact" color="primary">
            <v-row class="d-flex align-center">
                <v-col cols="1" class="d-flex align-start">
                    <div>
                        <NuxtLink to="/">
                            <v-icon class="pl-12" size="x-large" color="white">
                                mdi-gift-open-outline
                            </v-icon>
                        </NuxtLink>
                    </div>
                </v-col>
                <v-col class="d-flex justify-space-around">
                    <router-link
                        style="text-decoration: none; color: inherit"
                        to="/"
                    >
                        <v-toolbar-title> Geschenke </v-toolbar-title>
                    </router-link>
                </v-col>
                <v-col cols="1" class="d-flex justify-end">
                    <div style="flex-wrap: nowrap">
                        <v-menu
                            transition="slide-y-transition"
                            location="bottom"
                            open-on-hover
                            close-delay="140"
                            :close-on-content-click="false"
                        >
                            <template #activator="{ props }">
                                <v-btn icon v-bind="props">
                                    <v-icon color="appbar_primary_text">
                                        mdi-dots-vertical
                                    </v-icon>
                                </v-btn>
                            </template>
                            <div>
                                <v-card>
                                    <v-list color="appbar_primary">
                                        <v-list-item
                                            v-if="status === 'authenticated'"
                                            to="/user/profile"
                                            class="px-4"
                                            prepend-icon="mdi-account"
                                        >
                                            {{ (data as any).firstName }}
                                            {{ (data as any).lastName }}
                                        </v-list-item>
                                    </v-list>
                                    <v-divider
                                        v-if="status === 'authenticated'"
                                        style="
                                            border-color: var(
                                                --v-appbar_primary_text
                                            );
                                        "
                                    />
                                    <v-list color="appbar_primary">
                                        <v-list-item>
                                            <v-list-item-action class="mx-1">
                                                <v-switch
                                                    v-model="
                                                        theme.global.current
                                                            .value.dark
                                                    "
                                                    append-icon="mdi-weather-night"
                                                    prepend-icon="mdi-white-balance-sunny"
                                                    @click.prevent="toggleTheme"
                                                />
                                            </v-list-item-action>
                                        </v-list-item>
                                        <v-list-item
                                            v-if="status === 'authenticated'"
                                            prepend-icon="mdi-logout"
                                            to="/login"
                                            @click="logout"
                                        >
                                            <v-list-item-title
                                                class="appbar_primary_text--text"
                                            >
                                                Logout
                                            </v-list-item-title>
                                        </v-list-item>
                                    </v-list>
                                </v-card>
                            </div>
                        </v-menu>
                    </div>
                </v-col>
            </v-row>
        </v-app-bar>
    </div>
</template>

<script setup lang="ts">
import { useTheme } from "vuetify";
const { signOut, status, data } = useAuth();
async function logout() {
    await signOut();
}
const theme = useTheme();
function toggleTheme() {
    const selectedTheme = theme.global.current.value.dark ? "light" : "dark";
    localStorage.setItem("selectedTheme", selectedTheme);
    theme.global.name.value = selectedTheme;
}
</script>

<style></style>
