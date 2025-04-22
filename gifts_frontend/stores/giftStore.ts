import { mande, defaults } from "mande";
const api = mande(`${useRuntimeConfig().public.auth.baseURL}/gifts`);
export type Gift = {
    id: number;
    name: string;
    price: number;
    giftStrength: number;
    description: string;
    link: string;
    picture: Blob | string;
    availableActions: string[];
    freeForReservationRequest?: User[];
    freeForReservation?: boolean;
    isSecretGift?: boolean;
    reservingUsers?: User[];
    isReceived?: boolean;
};
export type DatabaseGift = Omit<
    Omit<Gift, "freeForReservationRequest">,
    "reservingUsers"
> & {
    giftGroup_id: number;
    user_email: string;
    reservingUsers?: string[];
    freeForReservationRequest?: string[];
};
export enum GiftStrength {
    "Ganz okay" = 1,
    "Okay" = 2,
    "Gut" = 3,
    "Super" = 4,
    "Mega" = 5,
}
enum BackendGiftStrength {
    OKAY = 1,
    GOOD = 2,
    GREAT = 3,
    AMAZING = 4,
    AWESOME = 5,
}
function transformToDataBaseGift(gift: Gift): DatabaseGift {
    const result = {} as DatabaseGift;
    result.id = gift.id;
    result.name = gift.name;
    result.price = gift.price;
    result.giftStrength = gift.giftStrength;
    result.description = gift.description;
    result.link = gift.link;
    result.picture = gift.picture;
    result.availableActions = gift.availableActions;
    result.isSecretGift = gift.isSecretGift;
    if (Object.hasOwn(gift, "freeForReservationRequest"))
        result.freeForReservationRequest = gift.freeForReservationRequest!.map(
            (user) => user.email,
        );
    if (Object.hasOwn(gift, "reservingUsers"))
        result.reservingUsers = gift.reservingUsers!.map((user) => user.email);
    return result;
}
export const useGiftStore = defineStore("gift", {
    state: () => ({
        gifts: {} as { [key: number]: DatabaseGift[] },
        groupId: 0 as number,
    }),

    actions: {
        async loadFromAPI() {
            try {
                const { token } = useAuth();
                defaults.headers.Authorization = String(token.value);
                const response = await api.get();
                this.gifts = response as {
                    [key: number]: DatabaseGift[];
                };
            } catch (error) {
                console.log(error);
                return error;
            }
        },
        async loadWithShareTokenFromAPI(shareToken: string) {
            const response = await api.get(`shared/${shareToken}`);
            this.gifts = response as {
                [key: number]: DatabaseGift[];
            };
        },
        setGroup(giftGroup_id: number) {
            this.groupId = giftGroup_id;
        },
        async addGift(_gift: Gift) {
            const formData = new FormData();
            const gift = transformToDataBaseGift(_gift);
            for (const [key, value] of Object.entries(gift)) {
                switch (typeof value) {
                    case "number":
                        if (key === "giftStrength")
                            formData.append(key, BackendGiftStrength[value]);
                        else formData.append(key, value.toString());
                        break;
                    case "string":
                        formData.append(key, value);
                        break;
                    default:
                        if (key !== "availableActions" && value !== undefined)
                            formData.append(key, value as Blob);
                        break;
                }
            }
            try {
                const { token } = useAuth();
                defaults.headers.Authorization = String(token.value);
                const _ = await fetch(
                    `${useRuntimeConfig().public.auth.baseURL}/gifts/${this.groupId}`,
                    {
                        method: "POST",
                        body: formData,
                        headers: {
                            Authorization: token.value!,
                        },
                    },
                );
            } catch (error) {
                console.log(error);
                return error;
            } finally {
                await this.loadFromAPI();
                await useGiftGroupStore().loadFromAPI();
            }
        },
        async updateGift(_gift: Gift) {
            const formData = new FormData();
            const gift = transformToDataBaseGift(_gift);
            for (const [key, value] of Object.entries(gift)) {
                switch (typeof value) {
                    case "number":
                        if (key === "giftStrength")
                            formData.append(key, BackendGiftStrength[value]);
                        else formData.append(key, value.toString());
                        break;
                    case "string":
                        formData.append(key, value);
                        break;
                    default:
                        if (key !== "availableActions" && value !== undefined)
                            formData.append(key, value as Blob);
                        break;
                }
            }
            try {
                const { token } = useAuth();
                defaults.headers.Authorization = String(token.value);
                const _ = await fetch(
                    `${useRuntimeConfig().public.auth.baseURL}/gifts/${this.groupId}/${gift.id}`,
                    {
                        method: "PUT",
                        body: formData,
                        headers: {
                            Authorization: token.value!,
                        },
                    },
                );
            } catch (error) {
                console.log(error);
                return error;
            } finally {
                await this.loadFromAPI();
                await useGiftGroupStore().loadFromAPI();
            }
        },
        async deleteGift(gift: Gift) {
            try {
                const _ = await api.delete(`/${this.groupId}/${gift.id}`);
            } catch (error) {
                console.log(error);
                return error;
            } finally {
                await this.loadFromAPI();
                await useGiftGroupStore().loadFromAPI();
            }
        },
        async doAction(
            _gift: Gift,
            queryParams: {
                reserve?: boolean;
                freeReserve?: boolean;
                requestFreeReserve?: boolean;
                denyFreeReserve?: boolean;
                markAsReceived?: boolean;
            },
        ) {
            const gift = transformToDataBaseGift(_gift);
            let queryString = "";
            if (queryParams.reserve !== undefined)
                queryString += "reserve=" + queryParams.reserve;
            if (queryParams.freeReserve !== undefined) {
                queryString += queryString !== "" ? "?" : "";
                queryString += "free_reserve=" + queryParams.freeReserve;
            }
            if (queryParams.requestFreeReserve !== undefined) {
                queryString += queryString !== "" ? "?" : "";
                queryString +=
                    "request_free_reserve=" + queryParams.requestFreeReserve;
            }
            if (queryParams.denyFreeReserve !== undefined) {
                queryString += queryString !== "" ? "?" : "";
                queryString +=
                    "deny_free_reserve=" + queryParams.denyFreeReserve;
            }
            if (queryParams.markAsReceived !== undefined) {
                queryString += queryString !== "" ? "?" : "";
                queryString += "mark_as_received=" + queryParams.markAsReceived;
            }
            try {
                const _ = await api.patch(
                    `/${this.groupId}/${gift.id}?${queryString}`,
                );
            } catch (error) {
                console.log(error);
                return error;
            } finally {
                await this.loadFromAPI();
                await useGiftGroupStore().loadFromAPI();
            }
        },
    },
    getters: {
        getGiftsOfCurrentGroup(state): Gift[] {
            if (!state.gifts || !state.gifts[state.groupId]) return [];
            const userStore = useUserStore();
            const result = Array<Gift>(state.gifts[state.groupId].length);
            for (const [index, databaseGift] of state.gifts[
                state.groupId
            ].entries()) {
                result[index] = {} as Gift;
                result[index].id = databaseGift.id;
                result[index].name = databaseGift.name;
                result[index].price = databaseGift.price;
                result[index].giftStrength = databaseGift.giftStrength;
                result[index].description = databaseGift.description;
                result[index].link = databaseGift.link;
                result[index].picture = databaseGift.picture;
                result[index].availableActions = databaseGift.availableActions;
                result[index].isSecretGift = databaseGift.isSecretGift;
                result[index].isReceived = databaseGift.isReceived;
                if (Object.hasOwn(databaseGift, "freeForReservationRequest"))
                    result[index].freeForReservationRequest =
                        databaseGift.freeForReservationRequest!.map(
                            (request_email) =>
                                userStore.users.find(
                                    (user) => user.email === request_email,
                                )!,
                        );
                if (Object.hasOwn(databaseGift, "reservingUsers"))
                    result[index].reservingUsers =
                        databaseGift.reservingUsers!.map(
                            (reserving_email) =>
                                userStore.users.find(
                                    (user) => user.email === reserving_email,
                                )!,
                        );
            }
            return result;
        },
    },
});
