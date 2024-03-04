import { mande, defaults } from "mande";
const api = mande(`${useRuntimeConfig().public.auth.baseURL}/users`);
export type User = {
    email: string;
    firstName: string;
    lastName: string;
    avatar: string;
};
export const useUserStore = defineStore("user", {
    state: () => ({
        users: [] as User[],
    }),

    actions: {
        async loadFromAPI() {
            try {
                const { token } = useAuth();
                defaults.headers.Authorization = String(token.value);
                const response = await api.get();
                this.users = response as User[];
            } catch (error) {
                console.log(error);
                return error;
            }
        },
        async requestPasswordReset(email: string) {
            try {
                const _ = await api.post(`/${email}`);
            } catch (error) {
                console.log(error);
                return error;
            }
        },
        async resetPassword(email: string, password: string, code: string) {
            try {
                const _ = await api.patch(`/${email}`, {
                    password: password,
                    code: code,
                });
            } catch (error) {
                console.log(error);
                return error;
            }
        },
        async updateUser(
            oldPassword: string,
            newFirstName: string,
            newLastName: string,
            newPassword: string,
            avatar: string,
        ) {
            try {
                const { data } = useAuth();
                const body = {
                    email: (data.value as any).email,
                    firstName: newFirstName,
                    lastName: newLastName,
                    oldPassword: oldPassword,
                    avatar: avatar,
                } as any;
                if (newPassword !== "") {
                    body["newPassword"] = newPassword;
                }
                console.log(body);
                const _ = await api.put(`/${(data.value as any).email}`, body);
            } catch (error) {
                console.log(error);
                return error;
            } finally {
                const { data, signIn } = useAuth();
                signIn({
                    email: (data.value as any).email,
                    password: newPassword !== "" ? newPassword : oldPassword,
                });
                this.loadFromAPI();
            }
        },
    },
});
