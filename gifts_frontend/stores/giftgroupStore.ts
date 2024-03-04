import { mande, defaults } from "mande";
import type { User } from "./userStore";
const api = mande(`${useRuntimeConfig().public.auth.baseURL}/giftgroups`);
export type Giftgroup = {
    id: number;
    editable: boolean;
    isBeingGifted: boolean;
    name: string;
    isSecretGroup: boolean;
    invitations?: User[];
    isInvited?: boolean;
    usersBeingGifted?: User[];
    invitableUsers?: User[];
};
type DataBaseGiftGroup = Omit<
    Omit<Omit<Giftgroup, "usersBeingGifted">, "invitableUsers">,
    "invitations"
> & {
    invitations: string[];
    usersBeingGifted: string[];
    invitableUsers: string[];
};
export const useGiftGroupStore = defineStore("giftgroups", {
    state: () => ({
        databaseGiftgroups: [] as DataBaseGiftGroup[],
    }),
    actions: {
        async loadFromAPI() {
            try {
                const { token, data } = useAuth();
                defaults.headers.Authorization = String(token.value);
                const response = await api.get({});
                this.databaseGiftgroups = response as DataBaseGiftGroup[];
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
        giftgroups(state) {
            const userStore = useUserStore();
            const { data } = useAuth();
            const res = Array<Giftgroup>(state.databaseGiftgroups.length);
            for (const [
                index,
                dataBaseGiftGroup,
            ] of state.databaseGiftgroups.entries()) {
                res[index] = {} as Giftgroup;
                res[index].id = dataBaseGiftGroup.id;
                res[index].editable = dataBaseGiftGroup.editable;
                res[index].isBeingGifted = dataBaseGiftGroup.isBeingGifted;
                if (index !== 0) {
                    res[index].name = dataBaseGiftGroup.name;
                } else if (
                    dataBaseGiftGroup.name ===
                    `${(data.value as any).firstName} ${
                        (data.value as any).lastName
                    }'s Liste`
                ) {
                    res[index].name = "Meine Liste";
                }
                res[index].isSecretGroup = dataBaseGiftGroup.isSecretGroup;
                res[index].id = dataBaseGiftGroup.id;
                res[index].isInvited = dataBaseGiftGroup.isInvited;
                res[index].invitations = dataBaseGiftGroup.invitations.map(
                    (invited_user) =>
                        userStore.users.find(
                            (user) => user.email === invited_user,
                        )!,
                );
                res[index].usersBeingGifted =
                    dataBaseGiftGroup.usersBeingGifted.map(
                        (gifted_user) =>
                            userStore.users.find(
                                (user) => user.email === gifted_user,
                            )!,
                    );
                res[index].invitableUsers =
                    dataBaseGiftGroup.invitableUsers.map(
                        (invitable_user) =>
                            userStore.users.find(
                                (user) => user.email === invitable_user,
                            )!,
                    );
            }
            return res;
        },
    },
});
