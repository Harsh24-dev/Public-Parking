<script setup>
import { RouterLink, useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'

const email = ref('')

const router = useRouter()

onMounted(() => {
  email.value = localStorage.getItem('email') || 'Admin'
})

function logout() {
  localStorage.clear();
  router.push('/login');
}
</script>

<template>
  <div>
    <div class="text-center mb-3">
      <h2>Welcome to Admin Dashboard</h2>
    </div>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark px-4">
    <div class="navbar-nav d-flex w-100 justify-content-between align-items-center">
      <ul class="navbar-nav me-auto mb-2 mb-lg-0">
        <li class="nav-item">
          <RouterLink class="nav-link" to="/admin_dashboard">Lots</RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink class="nav-link" to="/admin_user">Users</RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink class="nav-link" to="/admin_search">Search</RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink class="nav-link" to="/admin_summary">Summary</RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink class="nav-link text-danger" @click.prevent="logout()" to="#">Logout</RouterLink>
        </li>
      </ul>

      <span class="navbar-text text-light ms-auto">
        Hi, {{ email }}
      </span>
    </div>
  </nav>

  </div>
</template>