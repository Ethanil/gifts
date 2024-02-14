<template>
<n-layout-header bordered>
    <n-button>
      <icon type="refresh" size="20" :depth="2" />
    </n-button>
    <n-breadcrumb>
      <n-breadcrumb-item>Dashboard</n-breadcrumb-item>
      <n-breadcrumb-item>Home</n-breadcrumb-item>
    </n-breadcrumb>
    <n-space :size="20" align="center" style="line-height: 1">
      <n-tooltip>
        <template #trigger>
          <router-link :to="{ name: 'about' }">
            <icon type="help" size="22" :depth="2" />
          </router-link>
        </template>
        Dashboard help
      </n-tooltip>
      <n-tooltip>
        <template #trigger>
          <n-a href="https://github.com/zce/fearless" target="_blank">
            <icon type="github" size="22" :depth="2" />
          </n-a>
        </template>
        View on GitHub
      </n-tooltip>
      <n-popover trigger="click" placement="bottom-end" :width="300">
        <template #trigger>
          <n-badge dot processing>
            <icon type="notifications" size="22" :depth="2" />
          </n-badge>
        </template>
        <n-tabs type="line" justify-content="space-evenly" style="--pane-padding: 0">
          <n-tab-pane name="notifications" tab="Notifications (5)">
            <n-list style="margin: 0">
              <n-list-item> Notification</n-list-item>
            </n-list>
          </n-tab-pane>
          <n-tab-pane name="messages" tab="Messages (6)">
            <n-list>
              <n-list-item>Message </n-list-item>
            </n-list>
          </n-tab-pane>
        </n-tabs>
      </n-popover>
      <n-dropdown>
        <n-avatar/>
      </n-dropdown>
    </n-space>
  </n-layout-header>
</template>


<style scoped>
.v-btn {
  height: 100%
}
</style>