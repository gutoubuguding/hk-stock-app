<template>
  <el-container class="app-container">
    <!-- 顶部导航 -->
    <el-header class="app-header">
      <div class="brand">
        <div class="brand-mark">HK</div>
        <div>
          <div class="logo">港股分析</div>
          <div class="tagline">Market Intelligence</div>
        </div>
      </div>
      <el-menu
        :default-active="currentRoute"
        mode="horizontal"
        router
        class="header-menu"
      >
        <el-menu-item index="/">
          <el-icon><DataLine /></el-icon>
          <span>大盘概览</span>
        </el-menu-item>
        <el-menu-item index="/search">
          <el-icon><Search /></el-icon>
          <span>股票查询</span>
        </el-menu-item>
        <el-menu-item index="/watchlist">
          <el-icon><Star /></el-icon>
          <span>自选股</span>
        </el-menu-item>
        <el-menu-item index="/ipo">
          <el-icon><Promotion /></el-icon>
          <span>新股AI分析</span>
        </el-menu-item>
        <el-menu-item index="/calendar">
          <el-icon><Calendar /></el-icon>
          <span>日历</span>
        </el-menu-item>
        <el-menu-item index="/alerts">
          <el-icon><Bell /></el-icon>
          <span>预警</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>设置</span>
        </el-menu-item>
      </el-menu>
    </el-header>

    <!-- 主内容区 -->
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentRoute = computed(() => route.path)
</script>

<style>
:root {
  --bg: #eef3fb;
  --panel: rgba(255, 255, 255, 0.88);
  --panel-solid: #ffffff;
  --text-main: #172033;
  --text-muted: #778196;
  --border-soft: rgba(119, 129, 150, 0.18);
  --primary: #246bfe;
  --primary-soft: #eaf1ff;
  --red: #f04438;
  --green: #12a150;
  --shadow: 0 18px 45px rgba(28, 45, 84, 0.10);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body,
#app {
  min-height: 100%;
}

body {
  font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  color: var(--text-main);
  background:
    radial-gradient(circle at 8% -8%, rgba(36, 107, 254, 0.18), transparent 34%),
    radial-gradient(circle at 92% 0%, rgba(245, 159, 11, 0.16), transparent 28%),
    linear-gradient(180deg, #f8fbff 0%, var(--bg) 100%);
}

.app-container {
  min-height: 100vh;
}

.app-header {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 28px;
  height: 72px;
  padding: 0 28px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.72);
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 10px 30px rgba(38, 57, 97, 0.08);
  backdrop-filter: blur(18px);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 208px;
}

.brand-mark {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: 14px;
  color: #fff;
  font-weight: 800;
  letter-spacing: -0.04em;
  background: linear-gradient(135deg, #246bfe 0%, #0f2347 100%);
  box-shadow: 0 12px 24px rgba(36, 107, 254, 0.28);
}

.logo {
  font-size: 19px;
  line-height: 1.15;
  font-weight: 800;
  color: var(--text-main);
  white-space: nowrap;
}

.tagline {
  margin-top: 3px;
  font-size: 11px;
  letter-spacing: 0.12em;
  color: var(--text-muted);
  text-transform: uppercase;
}

.header-menu {
  flex: 1;
  min-width: 0;
  border-bottom: none !important;
  background: transparent !important;
}

.header-menu.el-menu--horizontal {
  height: 72px;
}

.header-menu.el-menu--horizontal > .el-menu-item {
  height: 72px;
  border-bottom: 0 !important;
  color: #5f6b82;
  font-weight: 600;
}

.header-menu.el-menu--horizontal > .el-menu-item:hover,
.header-menu.el-menu--horizontal > .el-menu-item.is-active {
  color: var(--primary) !important;
  background: transparent !important;
}

.header-menu.el-menu--horizontal > .el-menu-item.is-active::after {
  content: '';
  position: absolute;
  left: 18px;
  right: 18px;
  bottom: 12px;
  height: 4px;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--primary), #69a2ff);
}

.app-main {
  width: min(1440px, 100%);
  margin: 0 auto;
  padding: 28px;
  min-height: calc(100vh - 72px);
}

.app-main h2 {
  margin-bottom: 18px;
  color: var(--text-main);
  font-size: 28px;
  font-weight: 850;
  letter-spacing: -0.04em;
}

.el-card {
  border: 1px solid var(--border-soft) !important;
  border-radius: 18px !important;
  background: var(--panel) !important;
  box-shadow: var(--shadow) !important;
  overflow: hidden;
}

.el-card__header {
  padding: 16px 20px !important;
  border-bottom: 1px solid rgba(119, 129, 150, 0.12) !important;
  color: #445069;
  font-weight: 700;
}

.el-card__body {
  padding: 20px !important;
}

.el-table {
  border-radius: 16px;
  overflow: hidden;
  --el-table-header-bg-color: #f7f9fd;
  --el-table-row-hover-bg-color: #eef5ff;
}

.el-table th.el-table__cell {
  color: #667085;
  font-weight: 700;
}

.el-tabs__item {
  font-weight: 700;
}

.el-tabs__active-bar {
  height: 3px;
  border-radius: 999px;
}

.el-button {
  font-weight: 700;
  border-radius: 10px !important;
}

.el-input__wrapper,
.el-select__wrapper {
  border-radius: 12px !important;
}

.up { color: var(--red) !important; }
.down { color: var(--green) !important; }
.warn { color: #e6a23c !important; }

@media (max-width: 980px) {
  .app-header {
    height: auto;
    padding: 14px 16px 0;
    align-items: flex-start;
    flex-direction: column;
    gap: 10px;
  }

  .header-menu.el-menu--horizontal {
    width: 100%;
    height: auto;
    overflow-x: auto;
  }

  .header-menu.el-menu--horizontal > .el-menu-item {
    height: 52px;
  }

  .app-main {
    padding: 18px 14px;
  }
}
</style>
