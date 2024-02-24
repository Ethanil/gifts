<template>
    <td
        v-if="!mobile"
        class="v-data-table__td v-data-table-column--align-start"
    >
        <template v-if="itemKey == 'picture'">
            <div class="d-flex justify-center align-center">
                <v-avatar
                    v-if="
                        typeof item.picture === 'string' && item.picture !== ''
                    "
                    :image="item.picture as string"
                    :size="60"
                    class="cursor-pointer"
                    @click="emit('openPictureDialog')"
                />
                <v-icon v-else :size="30" icon="mdi-image-remove-outline" />
            </div>
        </template>
        <template v-else-if="itemKey == 'giftStrength'">
            <v-rating
                v-model="rating"
                color="primary"
                readonly
                density="compact"
                size="small"
            />
        </template>
        <template v-else-if="itemKey == 'price'"> {{ itemVal }} € </template>
        <template v-else-if="itemKey == 'availableActions'">
            <GiftDashboardActions
                :item="item"
                @do-action="
                    (gift, queryParams) => emit('doAction', queryParams)
                "
                @edit="emit('editGift')"
                @delete="emit('deleteGift')"
            />
        </template>
        <template v-else-if="itemKey == 'name'">
            <v-tooltip v-if="item.isSecretGift" location="bottom">
                <template #activator="{ props }">
                    <v-badge
                        icon="mdi-eye-off-outline"
                        offset-x="-12"
                        color="primary"
                        v-bind="props"
                    >
                        {{ itemVal }}
                    </v-badge>
                </template>
                Dies ist ein geheimes Geschenk
            </v-tooltip>
            <span v-else>{{ itemVal }}</span>
        </template>
        <template v-else-if="itemKey === 'link' && itemVal !== ''">
            <a :href="itemVal" target="_blank">
                <v-icon icon="mdi-open-in-new" />
            </a>
        </template>
        <template v-else-if="itemKey === 'reservingUsers'">
            <template
                v-if="item.reservingUsers && item.reservingUsers.length > 0"
            >
                <v-dialog
                    v-if="item.reservingUsers && item.reservingUsers.length > 0"
                    max-width="600px"
                >
                    <template #activator="{ props }">
                        <v-container>
                            <v-row
                                class="cursor-pointer"
                                v-bind="props"
                                justify="space-around"
                                no-gutters
                            >
                                <v-col
                                    v-for="(user, key) of item.reservingUsers"
                                    :key="key"
                                >
                                    <v-tooltip location="bottom">
                                        <template #activator="{ props }">
                                            <span
                                                v-bind="props"
                                                v-html="
                                                    reservingUserAvatars![key]
                                                "
                                            ></span>
                                        </template>
                                        {{ user.firstName }} {{ user.lastName }}
                                    </v-tooltip>
                                </v-col>
                            </v-row>
                        </v-container>
                    </template>
                    <GroupFormList
                        :users="item.reservingUsers"
                        :action-enabled="false"
                        title="Reserviert von"
                    />
                </v-dialog>
            </template>
        </template>
        <template v-else>{{ itemVal }}</template>
    </td>
    <v-card v-else class="ma-2" elevation="6">
        <v-container>
            <v-row>
                <v-col>
                    <div class="text-h5 d-flex justify-center">
                        <v-tooltip v-if="item.isSecretGift" location="bottom">
                            <template #activator="{ props }">
                                <v-badge
                                    icon="mdi-eye-off-outline"
                                    offset-x="-12"
                                    color="primary"
                                    v-bind="props"
                                >
                                    {{ item.name }}
                                </v-badge>
                            </template>
                            Dies ist ein geheimes Geschenk
                        </v-tooltip>
                        <div v-else>{{ item.name }}</div>
                    </div>
                </v-col>
            </v-row>
            <v-row>
                <v-col>
                    <div class="text-subtitle-2 d-flex justify-center">
                        {{ item.description }}
                    </div>
                </v-col>
            </v-row>
            <v-row>
                <v-col cols="7">
                    <GiftDashboardActions
                        :item="item"
                        @do-action="
                            (gift, queryParams) => emit('doAction', queryParams)
                        "
                        @edit="emit('editGift')"
                        @delete="emit('deleteGift')"
                    />
                </v-col>
                <v-col>
                    <div class="d-flex justify-center">
                        <v-avatar
                            v-if="
                                typeof item.picture === 'string' &&
                                item.picture !== ''
                            "
                            size="60"
                            :image="item.picture"
                        />
                        <v-icon
                            v-else
                            size="40"
                            icon="mdi-image-remove-outline"
                        />
                    </div>
                    <div class="d-flex justify-center">
                        <v-rating
                            v-model="giftStrength"
                            color="primary"
                            readonly
                            density="compact"
                            size="small"
                        />
                    </div>
                </v-col>
            </v-row>
            <v-row>
                <v-col v-if="item.link !== ''">
                    <div class="d-flex justify-center">
                        <a :href="item.link" target="_blank">
                            <v-icon size="30" icon="mdi-open-in-new" />
                        </a>
                    </div>
                </v-col>
                <v-col>
                    <div class="d-flex justify-center">{{ item.price }} €</div>
                </v-col>
            </v-row>
            <v-dialog
                v-if="item.reservingUsers && item.reservingUsers.length > 0"
                max-width="600px"
            >
                <template #activator="{ props }">
                    <v-container>
                        <v-row v-bind="props" align="center">
                            <v-col>Reserviert von:</v-col>
                            <v-col>
                                <v-container>
                                    <v-row justify="space-around" align="center">
                                        <v-col
                                            v-for="(
                                                user, key
                                            ) of item.reservingUsers"
                                            :key="key"
                                        >
                                            <v-tooltip location="bottom">
                                                <template
                                                    #activator="{ props }"
                                                >
                                                    <span
                                                        v-bind="props"
                                                        v-html="
                                                            reservingUserAvatars![
                                                                key
                                                            ]
                                                        "
                                                    ></span>
                                                </template>
                                                {{ user.firstName }}
                                                {{ user.lastName }}
                                            </v-tooltip>
                                        </v-col>
                                    </v-row>
                                </v-container>
                            </v-col>
                        </v-row>
                    </v-container>
                </template>
                <GroupFormList
                    :users="item.reservingUsers"
                    :action-enabled="false"
                    title="Reserviert von"
                />
            </v-dialog>
        </v-container>
    </v-card>
</template>
<script setup lang="ts">
import { useDisplay } from "vuetify";
const { lgAndUp } = useDisplay();
import avatar from "animal-avatar-generator";
const reservingUserAvatars = computed(() =>
    outerProps.item.reservingUsers?.map((user) =>
        avatar(user.avatar, {
            size: lgAndUp.value ? 40 : 40,
            blackout: false,
        }).replaceAll("\n", ""),
    ),
);
import type { PropType } from "vue";
const outerProps = defineProps({
    itemKey: { type: String, required: true },
    itemVal: {
        type: [Object, String, Number] as PropType<any>,
        required: true,
    },
    item: { type: Object as PropType<Gift>, required: true },
    mobile: { type: Boolean, default: false },
});
const giftStrength = computed(() => outerProps.item.giftStrength);
const rating = outerProps.item.giftStrength;
const emit = defineEmits([
    "openPictureDialog",
    "doAction",
    "editGift",
    "deleteGift",
]);
</script>
