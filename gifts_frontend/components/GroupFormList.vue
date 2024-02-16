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
        <template v-for="(user, key) in outerProps.users" :key="key">
            <v-list-item>
                <template #prepend>
                    <v-avatar
                        :icon="outerProps.avatar ? '' : 'mdi-account-outline'"
                        :image="outerProps.avatar"
                    />
                </template>
                {{ user.firstName }} {{ user.lastName }}
                <template v-if="outerProps.actionEnabled" #append>
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
                        outerProps.ownActionEnabled && data.email === user.email
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
            </v-list-item>
        </template>
    </v-list>
</template>
<script setup lang="ts">
import type { PropType } from "vue";
const { data } = useAuth();
const outerProps = defineProps({
    users: { type: Array<User>, required: true },
    avatar: { type: String, default: undefined },
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
});
const emit = defineEmits(["action"]);
</script>
