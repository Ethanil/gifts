<template>
    <v-bottom-sheet inset>
        <template #activator="{ props }">
            <v-btn icon="mdi-help" v-bind="props" />
        </template>
        <v-card class="pa-5">
            <div class="mx-auto">
                <v-card-title> Legende </v-card-title>
                <v-container>
                    <v-row>
                        <v-col cols="2">
                            <v-icon icon="mdi-pencil" />
                        </v-col>
                        <v-col> Geschenk bzw Liste bearbeiten </v-col>
                        <v-divider />
                    </v-row>
                    <v-row>
                        <v-col cols="2">
                            <v-icon icon="mdi-delete" />
                        </v-col>
                        <v-col> Geschenk löschen </v-col>
                        <v-divider />
                    </v-row>
                    <v-row>
                        <v-col cols="2">
                            <v-icon icon="mdi-lock" />
                        </v-col>
                        <v-col> Geschenk reservieren </v-col>
                        <v-divider />
                    </v-row>
                    <v-row>
                        <v-col cols="2">
                            <v-icon icon="mdi-lock-off" />
                        </v-col>
                        <v-col> Geschenk Reservierung zurückziehenn </v-col>
                        <v-divider />
                    </v-row>
                    <v-row>
                        <v-col cols="2">
                            <v-icon icon="mdi-share" />
                        </v-col>
                        <v-col>
                            Geschenk zur Reservierung für andere öffnen
                        </v-col>
                        <v-divider />
                    </v-row>
                    <v-row>
                        <v-col cols="2">
                            <v-icon icon="mdi-share-off" />
                        </v-col>
                        <v-col> Reservierungsöffnung zurückziehen </v-col>
                        <v-divider />
                    </v-row>
                    <v-row>
                        <v-col cols="2">
                            <v-icon icon="custom:MessageLockOutline" />
                        </v-col>
                        <v-col> Reservierungsöffnung anfragen </v-col>
                        <v-divider />
                    </v-row>
                    <v-row>
                        <v-col cols="2">
                            <v-icon icon="custom:MessageLockOffOutline" />
                        </v-col>
                        <v-col>
                            Reservierungsöffnungs-anfrage zurückziehen
                        </v-col>
                        <v-divider />
                    </v-row>
                    <v-row>
                        <v-col cols="2">
                            <v-btn icon="mdi-plus" color="primary" size="45" />
                        </v-col>
                        <v-col> Eine neue Geschenkliste erstellen </v-col>
                        <v-divider />
                    </v-row>
                    <v-row>
                        <v-col cols="2"> </v-col>
                        <v-col>
                            Eine Liste kann gelöscht werden, indem alle
                            Beschenkten aus ihr entfernt werden
                        </v-col>
                        <v-divider />
                    </v-row>
                    <v-row>
                        <v-col cols="2"> </v-col>
                        <v-col>
                            Nur Beschenkte können sehen, wer ein Geschenk
                            reserviert hat. Beschenkte sehen alle Geschenke, die
                            ein Beschenkter hinzugefügt hat.
                        </v-col>
                    </v-row>
                </v-container>
            </div>
        </v-card>
    </v-bottom-sheet>
</template>
