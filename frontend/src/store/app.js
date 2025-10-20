import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    sidebar: {
      opened: localStorage.getItem('sidebarStatus') ? !!localStorage.getItem('sidebarStatus') : true,
      withoutAnimation: false
    },
    device: 'desktop',
    size: localStorage.getItem('size') || 'default',
    tagsView: true,
    fixedHeader: true,
    showLogo: true,
    theme: 'light'
  }),

  getters: {
    sidebarOpened: (state) => state.sidebar.opened,
    isMobile: (state) => state.device === 'mobile'
  },

  actions: {
    toggleSideBar() {
      this.sidebar.opened = !this.sidebar.opened
      this.sidebar.withoutAnimation = false
      if (this.sidebar.opened) {
        localStorage.setItem('sidebarStatus', '1')
      } else {
        localStorage.setItem('sidebarStatus', '0')
      }
    },

    closeSideBar({ withoutAnimation }) {
      localStorage.setItem('sidebarStatus', '0')
      this.sidebar.opened = false
      this.sidebar.withoutAnimation = withoutAnimation
    },

    toggleDevice(device) {
      this.device = device
    },

    setSize(size) {
      this.size = size
      localStorage.setItem('size', size)
    },

    setTheme(theme) {
      this.theme = theme
      localStorage.setItem('theme', theme)
      
      // 切换Element Plus主题
      if (theme === 'dark') {
        document.documentElement.classList.add('dark')
        document.documentElement.classList.add('el-dark')
        document.body.setAttribute('data-theme', 'dark')
      } else {
        document.documentElement.classList.remove('dark')
        document.documentElement.classList.remove('el-dark')
        document.body.removeAttribute('data-theme')
      }
    },

    toggleTagsView() {
      this.tagsView = !this.tagsView
    },

    toggleFixedHeader() {
      this.fixedHeader = !this.fixedHeader
    },

    toggleLogo() {
      this.showLogo = !this.showLogo
    }
  },

  persist: {
    key: 'app-settings',
    storage: localStorage,
    paths: ['sidebar', 'size', 'theme', 'tagsView', 'fixedHeader', 'showLogo']
  }
})