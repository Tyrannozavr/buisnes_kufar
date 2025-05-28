<script setup lang="ts">
import type { Product } from '~/types/product'
import { useCart } from '~/composables/useCart'
import QuantityControls from '~/components/ui/QuantityControls.vue'

const props = defineProps<{
  product: Product
}>()

const { handleAddToCart, handleIncreaseQuantity, handleDecreaseQuantity, getQuantity, updateQuantity } = useCart()
const quantity = computed(() => getQuantity(props.product.id))

// Функция для ограничения длины имени продукта
const truncateName = (name: string, maxLength: number) => {
  if (name.length <= maxLength) return name
  return name.substring(0, maxLength) + '...'
}
</script>

<template>
  <div class="product-card">
    <NuxtLink :to="`/catalog/items/${product.slug}`" class="product-link">
      <div class="product-image">
        <img :src="product.images[0] || '/images/placeholder.png'" :alt="product.name">
      </div>
      <div class="product-content">
        <div class="product-info">
          <h3 class="product-name" :title="product.name">
            {{ truncateName(product.name, 50) }}
          </h3>
          <p class="product-type">{{ product.type }}</p>
          <p class="product-price">
            {{ product.price.toLocaleString('ru-RU') }} ₽
          </p>
        </div>
      </div>
    </NuxtLink>
    <div class="product-actions">
      <div v-if="quantity > 0" class="quantity-controls">
        <QuantityControls
          :quantity="quantity"
          @update:quantity="(qty: number) => updateQuantity(product.id, qty)"
          @remove="() => handleDecreaseQuantity(product.id, quantity)"
        />
      </div>
      <button 
        v-else 
        class="action-btn add-to-cart"
        @click.stop="handleAddToCart(product)"
      >
        Добавить в корзину
      </button>
    </div>
  </div>
</template>

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

.product-link {
  display: flex;
  flex-direction: column;
  flex: 1;
  text-decoration: none;
  color: inherit;
}

.product-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.product-image {
  width: 100%;
  height: 180px;
  overflow: hidden;
  position: relative;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}

.product-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  justify-content: space-between;
  padding: 1rem;
}

.product-info {
  flex-grow: 1;
}

.product-name {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
  height: 2.8rem;
}

.product-type {
  color: #666;
  margin: 0 0 0.5rem;
  font-size: 0.875rem;
}

.product-price {
  font-size: 1.25rem;
  font-weight: 600;
  color: #4CAF50;
  margin: 0;
}

.product-actions {
  margin-top: 1rem;
  padding: 1rem;
  border-top: 1px solid #eee;
}

.action-btn {
  width: 100%;
  padding: 0.625rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.action-btn:hover {
  transform: translateY(-1px);
}

.add-to-cart {
  background-color: #4CAF50;
  color: white;
}

.add-to-cart:hover {
  background-color: #388E3C;
}

.quantity-controls {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>