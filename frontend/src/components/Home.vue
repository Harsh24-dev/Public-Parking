<script setup>
import { RouterLink } from 'vue-router'
</script>
 
<template>
  <div class="container d-flex justify-content-center align-items-center vh-100">
    <div class="card p-4 shadow" style="min-width: 350px;">
    <div class="mb-4 text-center">
      <h2>Parking App</h2>
      <p>We care your car</p>
    </div>
    <div class="input_form" >
      <div class="mb-4 text-center">
        <h3>Welcome to Parking App</h3>
        <p>Hi guys, We help you find most suitable parking spot for your car parking.hope you enjoyed our Services.</p>
      </div>
    </div>
    <div class="mb-4 text-center">
      <RouterLink to="/login" type="button" class="btn btn-primary">Login</RouterLink>
    </div>
    </div>
  </div>
</template>
