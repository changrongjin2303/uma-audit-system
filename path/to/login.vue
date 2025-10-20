<script>
import { ref } from 'vue'
import { useUserStore } from '@/store/user'
import request from '@/utils/request' // 确保正确导入 request

export default {
  setup() {
    const userStore = useUserStore()
    const username = ref('admin')
    const password = ref('')
    const loading = ref(false)

    const login = async () => {
      try {
        loading.value = true
        // 确保 request 已正确导入且为函数
        const res = await request.post('/api/login', {
          username: username.value,
          password: password.value
        })
        if (res.data.success) {
          userStore.setToken(res.data.token)
          // 跳转到主页
        }
      } catch (error) {
        console.error('Login failed:', error)
      } finally {
        loading.value = false
      }
    }

    return {
      username,
      password,
      loading,
      login
    }
  }
}
</script>