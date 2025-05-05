<template>
  <div class="product-card" :class="{ 'is-hidden': isHidden, 'is-deleted': isDeleted }">
    <div class="product-image">
      <img :src="product.images[0] || '/placeholder.png'" :alt="product.name">
    </div>
    <div class="product-info">
      <h3 class="product-name">{{ product.name }}</h3>
      <p class="product-type">{{ product.type }}</p>
      <p v-if="!isHidden && !isDeleted" class="product-price">
        {{ product.price }} ₽
      </p>
      <p v-else-if="isHidden" class="product-status">
        Нет в наличии
      </p>
    </div>
    <div class="product-actions">
      <button v-if="!isHidden && !isDeleted" class="action-btn edit" @click="$emit('edit', product)">
        Редактировать
      </button>
      <button v-if="!isHidden && !isDeleted" class="action-btn hide" @click="$emit('hide', product)">
        Скрыть
      </button>
      <button v-if="!isDeleted" class="action-btn delete" @click="$emit('delete', product)">
        Удалить
      </button>
      <button v-if="isDeleted" class="action-btn restore" @click="$emit('restore', product)">
        Восстановить
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Product } from '~/types/product'

defineProps<{
  product: Product
  isHidden?: boolean
  isDeleted?: boolean
}>()

defineEmits<{
  (e: 'edit', product: Product): void
  (e: 'hide', product: Product): void
  (e: 'delete', product: Product): void
  (e: 'restore', product: Product): void
}>()
</script>

<style scoped>
.product-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
}

.product-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.product-image {
  width: 100%;
  height: 200px;
  overflow: hidden;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-info {
  padding: 1rem;
}

.product-name {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
  font-weight: 600;
}

.product-type {
  color: #666;
  margin: 0 0 0.5rem;
  font-size: 0.9rem;
}

.product-price {
  font-size: 1.2rem;
  font-weight: 600;
  color: #4CAF50;
  margin: 0;
}

.product-status {
  color: #f44336;
  font-weight: 500;
  margin: 0;
}

.product-actions {
  padding: 1rem;
  display: flex;
  gap: 0.5rem;
  border-top: 1px solid #eee;
}

.action-btn {
  padding: 0.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  flex: 1;
  transition: background-color 0.2s;
}

.edit {
  background-color: #2196F3;
  color: white;
}

.edit:hover {
  background-color: #1976D2;
}

.hide {
  background-color: #FFC107;
  color: black;
}

.hide:hover {
  background-color: #FFA000;
}

.delete {
  background-color: #f44336;
  color: white;
}

.delete:hover {
  background-color: #d32f2f;
}

.restore {
  background-color: #4CAF50;
  color: white;
}

.restore:hover {
  background-color: #388E3C;
}

.is-hidden {
  opacity: 0.7;
}

.is-deleted {
  opacity: 0.5;
}
</style> 