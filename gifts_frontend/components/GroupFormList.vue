<template>
    <v-list
        v-if="
            outerProps.emptyStrategy !== 'hide' || outerProps.users.length > 0
        "
        density="compact"
        slim
    >
        <v-list-subheader>
            <v-icon :icon="outerProps.titleIcon" />
            {{ outerProps.title }}
        </v-list-subheader>
        <template
            v-for="(
                [user, avt, isBase64, isSpecialGroupUser], key
            ) in userWithAvatar"
            :key="key"
        >
            <v-list-item>
                <template #prepend>
                    <div
                        v-if="isBase64"
                        class="mr-1 d-flex justify-center align-center"
                    >
                        <v-avatar size="32" :image="user.avatar" />
                    </div>
                    <div v-else class="mr-1 d-flex justify-center align-center">
                        <span style="height: 32px" v-html="avt"></span>
                    </div>
                </template>
                <span class="text-h6"
                    >{{ user.firstName }} {{ user.lastName }}</span
                >
                <template
                    v-if="
                        !isSpecialGroupUser &&
                        outerProps.actionEnabled &&
                        (!data ||
                            outerProps.ownActionEnabled ||
                            (data as any).email !== user.email)
                    "
                    #append
                >
                    <v-tooltip v-if="outerProps.actionTooltip">
                        <template #activator="{ props }">
                            <v-icon
                                v-bind="props"
                                :icon="outerProps.actionIcon"
                                @click="emit('action', user)"
                            />
                        </template>
                        {{ outerProps.actionTooltip(user) }}
                    </v-tooltip>
                    <v-icon v-else :icon="outerProps.actionIcon" />
                </template>
                <template
                    v-else-if="
                        !isSpecialGroupUser &&
                        outerProps.ownActionEnabled &&
                        data.email === user.email
                    "
                    #append
                >
                    <v-tooltip v-if="outerProps.ownActionTooltip">
                        <template #activator="{ props }">
                            <v-icon
                                v-bind="props"
                                :icon="outerProps.ownActionIcon"
                                @click="emit('action', user)"
                            />
                        </template>
                        {{ outerProps.ownActionTooltip(user) }}
                    </v-tooltip>
                    <v-icon v-else :icon="ownActionIcon" />
                </template>
                <template
                    v-else-if="isSpecialGroupUser && outerProps.isOwnGroup"
                    #append
                >
                    <v-tooltip>
                        <template #activator="{ props }">
                            <v-icon
                                v-bind="props"
                                icon="mdi-delete"
                                @click="emit('removeFromGroup', user)"
                            />
                        </template>
                        Schenkende*r entfernen
                    </v-tooltip>
                </template>
            </v-list-item>
        </template>
    </v-list>
</template>
<script setup lang="ts">
import type { PropType } from "vue";
const { data } = useAuth();
import avatar from "animal-avatar-generator";
const outerProps = defineProps({
    users: { type: Array<User>, required: true },
    actionEnabled: { type: Boolean, default: true },
    actionIcon: { type: String, default: undefined },
    actionTooltip: { type: Function, default: undefined },
    ownActionEnabled: { type: Boolean, default: true },
    ownActionIcon: { type: String, default: undefined },
    ownActionTooltip: { type: Function, default: undefined },
    title: { type: String, required: true },
    titleIcon: { type: String, default: undefined },
    emptyStrategy: {
        type: String as PropType<"do nothing" | "hide">,
        default: "do nothing",
    },
    startViewingGroupId: { type: Number, default: -1 },
    isOwnGroup: { type: Boolean, default: false },
    specialUsers: { type: Array<String>, default: [] },
});
const userWithAvatar = computed(() =>
    outerProps.users.map(
        (user) =>
            [
                user,
                avatar(user.avatar, {
                    size: 32,
                    blackout: false,
                }).replaceAll("\n", ""),
                user.avatar.split(";").length === 2,
                user.onlyViewing &&
                    outerProps.specialUsers.includes(user.email),
            ] as [User, string, boolean, boolean],
    ),
);
const emit = defineEmits(["action", "removeFromGroup"]);
</script>
