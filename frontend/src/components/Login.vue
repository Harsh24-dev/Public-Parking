<script setup>
import { ref } from 'vue';
import { RouterLink, useRouter } from 'vue-router';

const email = ref('');
const password = ref('');
const message = ref('');
const router = useRouter();

async function login() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email.value,
                password: password.value,
            }),
            credentials : 'include',
        });
        
        const data = await response.json();
        
        if (response.ok){
            const token = data["Authentication-token"];
            const role = data.role;

            if (!token || !role) {
                message.value = "Invalid login response from server."
                return;
            }
        
            localStorage.setItem('auth_token', token);
            localStorage.setItem('email',data.email);
            localStorage.setItem('role',role);

            if (role === 'admin') {
                router.push('/admin_dashboard');
            } else if (role === "user") {
                router.push("/user_dashboard");
            } else {
                errorMessage.value = "Unrecognized role.";
            }
        } else {
            message.value = data.message || "Invalid email or password.";
        }
    } catch (error){
        console.error('Login Error:', error);
        message.value = "Something went wrong. Please try again.";
    }
}
</script>

<template>
    <div class="container d-flex justify-content-center align-items-center vh-100">
        <div class="card p-4 shadow" style="min-width: 350px;">
            <div class="mb-4 text-center">
                <h1>Welcome to Parking App</h1>
                <h2>Login</h2>
            </div>

            <form class = 'container-fluid' @submit.prevent="login">
                <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" v-model="email" id="email" class="form-control" required/>
                </div>
                <div class = "mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" v-model="password" id="password" class="form-control" required/>
                </div>
                <button type="submit" class="btn btn-primary">Login</button>
            </form>

            <RouterLink class="d-block mt-3 text-center" to='/register'>Create new User?</RouterLink>
            
            <div v-if="message" class="alert alert-danger mt-3">
                {{ message }}
            </div>

        </div>
    </div>
    
</template>