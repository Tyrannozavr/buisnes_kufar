<template>
  <div class="product-card" :class="{ 'is-hidden': isHidden, 'is-deleted': isDeleted }">
    <div class="product-image">
      <img :src="product.images[0] || '/images/placeholder.png'" :alt="product.name">
    </div>
    <div class="product-content">
      <div class="product-info">
        <h3 class="product-name" :title="product.name">
          {{ truncateName(product.name, 60) }}
        </h3>
        <p class="product-type">{{ product.type }}</p>
        <p v-if="!isHidden && !isDeleted" class="product-price">
          {{ product.price.toLocaleString('ru-RU') }} ₽
        </p>
        <p v-else-if="isHidden" class="product-status">
          Нет в наличии
        </p>
      </div>
      <div class="product-actions">
        <template v-if="!isDeleted">
          <template v-if="!isHidden">
            <button class="action-btn edit" @click="$emit('edit', product)">
              Редактировать
            </button>
            <button class="action-btn hide" @click="$emit('hide', product)">
              Скрыть
            </button>
            <button class="action-btn delete" @click="$emit('delete', product)">
              Удалить
            </button>
          </template>
          <template v-else>
            <button class="action-btn restore" @click="$emit('restore', product)">
              Восстановить
            </button>
            <button class="action-btn delete" @click="$emit('delete', product)">
              Удалить
            </button>
          </template>
        </template>
        <template v-else>
          <button class="action-btn restore" @click="$emit('restore', product)">
            Восстановить
          </button>
        </template>
      </div>
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

// Функция для ограничения длины имени продукта
const truncateName = (name: string, maxLength: number) => {
  if (name.length <= maxLength) return name
  return name.substring(0, maxLength) + '...'
}
</script>

<style scoped>
.product-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.product-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.product-image {
  width: 100%;
  height: 240px;
  overflow: hidden;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  justify-content: space-between;
  padding: 1.25rem;
}

.product-info {
  flex-grow: 1;
}

.product-name {
  margin: 0 0 0.75rem;
  font-size: 1.25rem;
  font-weight: 600;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
  height: 3.5rem;
}

.product-type {
  color: #666;
  margin: 0 0 0.75rem;
  font-size: 1rem;
}

.product-price {
  font-size: 1.5rem;
  font-weight: 600;
  color: #4CAF50;
  margin: 0;
}

.product-status {
  color: #f44336;
  font-weight: 500;
  margin: 0;
  font-size: 1.1rem;
}

.product-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  border-top: 1px solid #eee;
  margin-top: 1.25rem;
  padding-top: 1.25rem;
}

.action-btn {
  padding: 0.75rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.action-btn:hover {
  transform: translateY(-1px);
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