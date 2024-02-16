<template>
    <v-list
        v-if="emptyStrategy !== 'hide' || users.length > 0"
        density="compact"
        slim
    >
        <v-list-subheader>
            <v-icon :icon="titleIcon" />
            {{ title }}
        </v-list-subheader>
        <template v-for="user in users">
            <v-list-item>
                <template #prepend>
                    <v-avatar
                        :icon="avatar ? '' : 'mdi-account-outline'"
                        :image="avatar"
                    />
                </template>
                {{ user.firstName }} {{ user.lastName }}
                <template v-if="actionEnabled" #append>
                    <v-tooltip v-if="actionTooltip">
                        <template #activator="{ props }">
                            <v-icon
                                v-bind="props"
                                :icon="actionIcon"
                                @click="emit('action', user)"
                            />
                        </template>
                        {{ actionTooltip(user) }}
                    </v-tooltip>
                    <v-icon v-else :icon="actionIcon" />
                </template>
                <template v-else-if="ownActionEnabled && data.email === user.email" #append>
                    <v-tooltip v-if="ownActionTooltip">
                        <template #activator="{ props }">
                            <v-icon
                                v-bind="props"
                                :icon="ownActionIcon"
                                @click="emit('action', user)"
                            />
                        </template>
                        {{ ownActionTooltip(user) }}
                    </v-tooltip>
                    <v-icon v-else :icon="ownActionIcon" />
                </template>
            </v-list-item>
        </template>
    </v-list>
</template>
<script setup lang="ts">
import type { PropType } from "vue";
const {data} = useAuth();
const props = defineProps({
    users: { type: Array<User>, required: true },
    avatar: { type: String },
    actionEnabled: { type: Boolean, default: true },
    actionIcon: { type: String },
    actionTooltip: { type: Function },
    ownActionEnabled: { type: Boolean, default: true },
    ownActionIcon: { type: String },
    ownActionTooltip: { type: Function },
    title: { type: String, required: true },
    titleIcon: { type: String },
    emptyStrategy: {
        type: String as PropType<"do nothing" | "hide">,
        default: "do nothing",
    },
});
const emit = defineEmits(["action"]);
</script>
