<script setup>
import { ref } from 'vue';
import { RouterLink, useRouter } from 'vue-router';
import { authorizedFetch } from '../utils/api';

const name = ref('');
const location = ref('');
const address = ref('');
const pin_code = ref('');
const price = ref('');
const total_spots = ref('');
const message = ref('');

const router = useRouter()

async function add_lot() {
    const token = localStorage.getItem('authToken');

    try {
        const response = await authorizedFetch('http://127.0.0.1:5000/api/admin/lots', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name.value,
                location: location.value,
                address: address.value,
                pin_code: pin_code.value,
                price: price.value,
                total_spots: total_spots.value,
            }),
            credentials: 'include'
        })

        let result;
        try {
            result = await response.json();
        } catch (jsonErr) {
            console.error('Failed to parse response JSON:', jsonErr);
            message.value = "Server error: Invalid response.";
            return;
        }

        if (!response.ok) {
            console.error(result);
            message.value = result.message || 'Failed to add lot.';
        } else {
            alert(result.message || 'Lot added successfully!');
            router.push('/admin_dashboard');
        }
    } catch (error) {
        console.error('Error:', error);
        message.value = "Something went wrong. Please try again.";
    }
}
</script>

<template>
    <div class="container d-flex justify-content-center align-items-center vh-100">
        <div class="card p-4 shadow" style="min-width: 350px;">
            <div class="mb-4 mt-4 text-center">
                <h1>Parking App</h1>
                <h2>Add New Lot</h2>
            </div>
            <form class = 'container-fluid' @submit.prevent="add_lot">
                <div class="mb-3">
                    <label for="name" class="form-label">Name</label>
                    <input type="name" v-model="name" id="name" class="form-control" required>
                </div>
                <div class = "mb-3">
                    <label for="location" class="form-label">Location</label>
                    <input type="location" v-model="location" id="location" class="form-control" required>
                </div>
                <div class = "mb-3">
                    <label for="address" class="form-label">Address</label>
                    <input type="address" v-model="address" id="address" class="form-control" required>
                </div>
                <div class = "mb-3">
                    <label for="pin_code" class="form-label">Pincode</label>
                    <input type="pin_code" v-model="pin_code" id="pin_code" class="form-control" required>
                </div>
                <div class = "mb-3">
                    <label for="price" class="form-label">Price</label>
                    <input type="price" v-model="price" id="price" class="form-control" required>
                </div>
                <div class = "mb-3">
                    <label for="total_spots" class="form-label">Total Spots</label>
                    <input type="total_spots" v-model="total_spots" id="total_spots" class="form-control" required>
                </div>
                <div class="center-text">
                    <button type="submit" class="btn btn-primary">Add Lot</button>
                </div>
            </form>
            <div v-if="message" class="alert alert-danger mt-3">
                {{ message }}
            </div>
            <div class="text-center mt-4">
                <RouterLink to='/admin_dashboard' class="btn btn-danger text-center text-wrap">Cancel Adding Lot</RouterLink>
            </div>
        </div>
    </div>
</template>