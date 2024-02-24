<template>
    <v-bottom-sheet inset max-height="90%">
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
                            Geschenk zum gemeinsamen Verschenken freigeben,
                            dadurch können mehrere Personen das selbe Geschenk
                            reservieren
                        </v-col>
                        <v-divider />
                    </v-row>
                    <v-row>
                        <v-col cols="2">
                            <v-icon icon="mdi-share-off" />
                        </v-col>
                        <v-col>
                            Das Gemeinsam-Verschenken wieder einschränken
                        </v-col>
                        <v-divider />
                    </v-row>
                    <v-row>
                        <v-col cols="2">
                            <v-icon icon="custom:MessageLockOutline" />
                        </v-col>
                        <v-col>
                            Anfrage stellen, ob das Geschenk gemeinsam
                            verschenkt werden soll
                        </v-col>
                        <v-divider />
                    </v-row>
                    <v-row>
                        <v-col cols="2">
                            <v-icon icon="custom:MessageLockOffOutline" />
                        </v-col>
                        <v-col>
                            Gemeinsam-Verschenken-Anfrage wieder zurückziehen
                        </v-col>
                        <v-divider />
                    </v-row>
                    <v-row>
                        <v-col cols="2">
                            <v-avatar
                                color="primary"
                                icon="mdi-eye-off-outline"
                                size="35"
                            />
                        </v-col>
                        <v-col>
                            Dieses Geschenk ist geheim, das heißt nur nicht
                            Beschenkte können es sehen
                        </v-col>
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
