<script setup>
import { ref } from 'vue';
import { RouterLink, useRouter } from 'vue-router';

const email = ref('');
const password = ref('');
const full_name = ref('');
const message = ref('');

const router = useRouter()

async function register() {
    try{
        const response = await fetch('http://127.0.0.1:5000/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email.value,
                password: password.value,
                full_name: full_name.value
            }),
            credentials : 'include'
        })
        
        const result = await response.json();
        
        if (!response.ok) {
            console.error(result)
            message.value = result.message || 'Registration failed'
        } else {
            alert(result.message || 'Registration successful!')
            router.push('/login')
        }
    } catch (error){
        console.error('Registration Error:', error);
        mess.value = "Something went wrong. Please try again.";
    }
    
}
</script>

<template>
    <div class="container d-flex justify-content-center align-items-center vh-100">
        <div class="card p-4 shadow" style="min-width: 350px;">
            <div class="mb-4 text-center">
                <h1>Parking App</h1>
                <h2>New User Registration</h2>
            </div>
            <form class = 'container-fluid' @submit.prevent="register">
                <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" v-model="email" id="email" class="form-control" required>
                </div>
                <div class = "mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" v-model="password" id="password" class="form-control" required>
                </div>
                <div class = "mb-3">
                    <label for="full_name" class="form-label">Full Name</label>
                    <input type="text" v-model="full_name" id="full_name" class="form-control" required>
                </div>
                <button type="submit" class="btn btn-primary">Signup</button>
            </form>
            <div v-if="message" class="alert alert-danger mt-3">
                {{ message }}
            </div>
            <RouterLink to='/login' class="d-block mt-3 text-center">Existing User?</RouterLink>
        </div>
    </div>
</template>