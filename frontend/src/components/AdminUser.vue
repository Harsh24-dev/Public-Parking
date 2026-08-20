<script setup>
import {ref, onMounted } from 'vue';
import { authorizedFetch } from '../utils/api';
import AdminNavbar from './AdminNavbar.vue';

const users = ref([]);

async function loadUsers() {
    try{
        const res = await authorizedFetch('http://127.0.0.1:5000/api/admin/users');
        if (!res.ok) throw new Error('Failed to fetch users list');
        users.value = await res.json();
    } catch (error) {
        console.error('Error loading users list', error);
    }
}

onMounted(loadUsers)
</script>

<template>
    <AdminNavbar />
    <div class="container mt-4">
        <div class="text-center mb-3">
            <div class="d-flex justify-content-between align-items-center mb-3"><h2>Registered Users List</h2></div>
            <div v-if="users.length" class="table-responsive">
                <table class="table table-striped">
                    <thead class="table-light">
                        <tr>
                            <th>User ID</th>
                            <th>Full Name</th>
                            <th>Email</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="user in users" :key="user.id">
                            <td>{{ user.id }}</td>
                            <td>{{ user.full_name }}</td>
                            <td>{{ user.email }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>