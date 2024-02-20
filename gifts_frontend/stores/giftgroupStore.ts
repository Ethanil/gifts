import { mande, defaults } from "mande";
import type { User } from "./userStore";
const api = mande(`${useRuntimeConfig().public.auth.baseURL}/giftgroups`);
export type Giftgroup = {
    id: number;
    editable: boolean;
    isBeingGifted: boolean;
    name: string;
    invitations?: User[];
    isInvited?: boolean;
    usersBeingGifted?: User[];
    invitableUsers?: User[];
};
export const useGiftGroupStore = defineStore("giftgroups", {
    state: () => ({
        giftgroups: [] as Giftgroup[],
    }),

    actions: {
        async loadFromAPI() {
            try {
                const { token, data } = useAuth();
                defaults.headers.Authorization = String(token.value);
                const response = await api.get({});
                this.giftgroups = response as Giftgroup[];
                // change name of own giftgroup
                if (
                    this.giftgroups.length > 0 &&
                    (this.giftgroups[0].name ==
                        `${(data.value as any).firstName} ${
                            (data.value as any).lastName
                        }'s Liste` ||
                        this.giftgroups[0].name ==
                            `${(data.value as any).firstName} ${
                                (data.value as any).lastName
                            }'s Liste`)
                ) {
                    this.giftgroups[0].name = "Meine Liste";
                }
            } catch (error) {
                console.log(error);
                return error;
            }
        },
        async addGroup(giftgroup: Giftgroup) {
            try {
                const _ = await api.post(giftgroup);
            } catch (error) {
                console.log(error);
                return error;
            } finally {
                await this.loadFromAPI();
            }
        },
        async updateGroup(giftgroup: Giftgroup) {
            try {
                const _ = await api.put(`/${giftgroup.id}`, giftgroup);
            } catch (error) {
                console.log(error);
                return error;
            } finally {
                await this.loadFromAPI();
            }
        },
        async joinGroup(giftgroup: Giftgroup) {
            try {
                const _ = await api.post(`/${giftgroup.id}`, giftgroup);
            } catch (error) {
                console.log(error);
                return error;
            } finally {
                await this.loadFromAPI();
            }
        },
        async declineInvitation(giftgroup: Giftgroup) {
            try {
                const _ = await api.post(
                    `/${giftgroup.id}?decline=true`,
                    giftgroup,
                );
            } catch (error) {
                console.log(error);
                return error;
            } finally {
                await this.loadFromAPI();
            }
        },
    },
    getters: {
        getGiftgroups(state) {
            if (!state.giftgroups) return [];
            return state.giftgroups;
        },
    },
});
