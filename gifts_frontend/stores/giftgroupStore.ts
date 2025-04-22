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
    isSpecialUser?: string[];
    lastUpdated?: Date;
    shareToken?: string;
    shareTokenExpireDate?: Date;
};
type DataBaseGiftGroup = Omit<
    Omit<
        Omit<
            Omit<Omit<Giftgroup, "shareTokenExpireDate">, "lastUpdated">,
            "usersBeingGifted"
        >,
        "invitableUsers"
    >,
    "invitations"
> & {
    invitations: string[];
    usersBeingGifted: string[];
    invitableUsers: string[];
    lastUpdated: string;
    shareTokenExpireDate: string;
};
function transformToDataBaseGiftGroup(giftgroup: Giftgroup): DataBaseGiftGroup {
    const res = {} as DataBaseGiftGroup;
    res.id = giftgroup.id;
    res.editable = giftgroup.editable;
    res.isBeingGifted = giftgroup.isBeingGifted;
    res.name = giftgroup.name;
    res.isSecretGroup = giftgroup.isSecretGroup;
    res.id = giftgroup.id;
    res.isInvited = giftgroup.isInvited;
    if (Object.hasOwn(giftgroup, "invitations")) {
        res.invitations = giftgroup.invitations!.map((user) => user.email);
    } else {
        res.invitations = [];
    }
    if (Object.hasOwn(giftgroup, "usersBeingGifted")) {
        res.usersBeingGifted = giftgroup.usersBeingGifted!.map(
            (user) => user.email,
        );
    } else {
        res.usersBeingGifted = [];
    }
    if (Object.hasOwn(giftgroup, "invitableUsers")) {
        res.invitableUsers = giftgroup.usersBeingGifted!.map(
            (user) => user.email,
        );
    } else {
        res.invitableUsers = [];
    }
    res.lastUpdated = "";
    return res;
}
export const useGiftGroupStore = defineStore("giftgroups", {
    state: () => ({
        databaseGiftgroups: [] as DataBaseGiftGroup[],
    }),
    actions: {
        async loadFromAPI() {
            try {
                const { token } = useAuth();
                defaults.headers.Authorization = String(token.value);
                const response = await api.get({});
                this.databaseGiftgroups = response as DataBaseGiftGroup[];
            } catch (error) {
                console.log(error);
                return error;
            }
        },
        async loadWithShareTokenFromAPI(shareToken: string) {
            const response = await api.get(`shared/${shareToken}`);
            this.databaseGiftgroups = [response] as DataBaseGiftGroup[];
        },
        async addGroup(giftgroup: Giftgroup) {
            try {
                const _ = await api.post(
                    transformToDataBaseGiftGroup(giftgroup),
                );
            } catch (error) {
                console.log(error);
                return error;
            } finally {
                await this.loadFromAPI();
            }
        },
        async updateGroup(giftgroup: Giftgroup) {
            try {
                const _ = await api.put(
                    `/${giftgroup.id}`,
                    transformToDataBaseGiftGroup(giftgroup),
                );
            } catch (error) {
                console.log(error);
                return error;
            } finally {
                await this.loadFromAPI();
            }
        },
        async joinGroup(giftgroup: Giftgroup) {
            try {
                const _ = await api.post(
                    `/${giftgroup.id}`,
                    transformToDataBaseGiftGroup(giftgroup),
                );
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
                    transformToDataBaseGiftGroup(giftgroup),
                );
            } catch (error) {
                console.log(error);
                return error;
            } finally {
                await this.loadFromAPI();
            }
        },
        async addSpecialUser(giftgroup: Giftgroup, user_email: string) {
            try {
                const _ = await api.post(
                    `/${giftgroup.id}?specialUserEmail=${user_email}`,
                    transformToDataBaseGiftGroup(giftgroup),
                );
            } catch (error) {
                console.log(error);
                return error;
            } finally {
                await this.loadFromAPI();
            }
        },
        async removeFromGroup(giftgroup: Giftgroup, user_email: string) {
            try {
                const _ = await api.delete(`/${giftgroup.id}/${user_email}`);
            } catch (error) {
                console.log(error);
                return error;
            } finally {
                await this.loadFromAPI();
            }
        },
        async generateShareToken(
            giftgroup_id: number,
            expireDate: Date,
        ): Promise<string> {
            let shareToken;
            if (!expireDate) return "";
            try {
                const localDate = new Date(
                    expireDate.getTime() -
                        expireDate.getTimezoneOffset() * 60000,
                )
                    .toISOString()
                    .split("T")[0];
                shareToken = await api.post(
                    `/${giftgroup_id}/share?endDate=${localDate}`,
                );
                shareToken = (shareToken as any)["shareToken"] as string;
            } catch (error) {
                console.log(error);
                return error as string;
            } finally {
                await this.loadFromAPI();
            }
            return shareToken;
        },
        async deleteShareToken(giftgroup_id: number) {
            try {
                const _ = await api.delete(`/${giftgroup_id}/share`);
            } catch (error) {
                console.log(error);
                return error;
            } finally {
                await this.loadFromAPI();
            }
        },
        async updateShareTokenExpireDate(
            giftgroup_id: number,
            expireDate: Date,
        ) {
            if (!expireDate) return;
            try {
                const localDate = new Date(
                    expireDate.getTime() -
                        expireDate.getTimezoneOffset() * 60000,
                )
                    .toISOString()
                    .split("T")[0];
                const _ = await api.patch(
                    `/${giftgroup_id}/share?endDate=${localDate}`,
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
            const res = Array<Giftgroup>(state.databaseGiftgroups.length);
            for (const [
                index,
                dataBaseGiftGroup,
            ] of state.databaseGiftgroups.entries()) {
                res[index] = {} as Giftgroup;
                res[index].id = dataBaseGiftGroup.id;
                res[index].editable = dataBaseGiftGroup.editable;
                res[index].isBeingGifted = dataBaseGiftGroup.isBeingGifted;
                if (!res[index].isBeingGifted || res[index].editable) {
                    res[index].name = dataBaseGiftGroup.name;
                } else {
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
                res[index].isSpecialUser = dataBaseGiftGroup.isSpecialUser;
                res[index].lastUpdated = new Date(
                    Date.parse(dataBaseGiftGroup.lastUpdated),
                );
                res[index].shareToken = dataBaseGiftGroup.shareToken;
                res[index].shareTokenExpireDate = new Date(
                    Date.parse(dataBaseGiftGroup.shareTokenExpireDate),
                );
            }
            return res;
        },
    },
});
