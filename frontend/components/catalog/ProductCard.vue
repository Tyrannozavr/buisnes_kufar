<script setup lang="ts">
import type { Product } from '~/types/product'
import { useCart } from '~/composables/useCart'

const props = defineProps<{
  product: Product
}>()

const { handleAddToCart, handleIncreaseQuantity, handleDecreaseQuantity, getQuantity, updateQuantity } = useCart()
const quantity = computed(() => getQuantity(props.product.id))
const isEditing = ref(false)
const inputValue = ref('')

// Функция для ограничения длины имени продукта
const truncateName = (name: string, maxLength: number) => {
  if (name.length <= maxLength) return name
  return name.substring(0, maxLength) + '...'
}

const handleQuantityInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  const value = target.value.replace(/[^\d]/g, '')
  inputValue.value = value
}

const handleQuantityBlur = () => {
  const newQuantity = parseInt(inputValue.value) || 0
  if (newQuantity > 0) {
    updateQuantity(props.product.id, newQuantity)
  } else {
    inputValue.value = quantity.value.toString()
  }
  isEditing.value = false
}

const handleQuantityKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter') {
    handleQuantityBlur()
  }
}

const startEditing = () => {
  inputValue.value = quantity.value.toString()
  isEditing.value = true
  // Фокусируемся на поле ввода после его появления
  nextTick(() => {
    const input = document.querySelector('.quantity-input') as HTMLInputElement
    if (input) {
      input.focus()
      input.select()
    }
  })
}
</script>

<template>
  <NuxtLink :to="`/catalog/items/${product.slug}`" class="product-card">
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
      <div class="product-actions">
        <div v-if="quantity > 0" class="quantity-controls">
          <button 
            class="quantity-btn" 
            @click="handleDecreaseQuantity(product.id, quantity)"
            title="Уменьшить количество"
          >
            <UIcon name="i-heroicons-minus" class="w-4 h-4" />
          </button>
          
          <div 
            v-if="!isEditing" 
            class="quantity-display"
            @click="startEditing"
            title="Нажмите для ввода количества"
          >
            <span>{{ quantity }}</span>
            <UIcon name="i-heroicons-pencil-square" class="w-3 h-3 ml-1 text-gray-400" />
          </div>
          <input
            v-else
            type="text"
            class="quantity-input"
            v-model="inputValue"
            @input="handleQuantityInput"
            @blur="handleQuantityBlur"
            @keydown="handleQuantityKeydown"
            ref="quantityInput"
            placeholder="Введите количество"
          />
          
          <button 
            class="quantity-btn" 
            @click="handleIncreaseQuantity(product.id, quantity)"
            title="Увеличить количество"
          >
            <UIcon name="i-heroicons-plus" class="w-4 h-4" />
          </button>
        </div>
        <button 
          v-else 
          class="action-btn add-to-cart"
          @click="handleAddToCart(product)"
        >
          Добавить в корзину
        </button>
      </div>
    </div>
  </NuxtLink>
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
  padding-top: 1rem;
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
  gap: 0.5rem;
}

.quantity-btn {
  width: 28px;
  height: 28px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  background: white;
  color: #4a5568;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.quantity-btn:hover {
  background: #f7fafc;
  border-color: #cbd5e0;
}

.quantity-display {
  min-width: 40px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 500;
  color: #2d3748;
  cursor: text;
  padding: 0 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  background: #f8fafc;
  transition: all 0.2s ease;
}

.quantity-display:hover {
  border-color: #4CAF50;
  background: white;
}

.quantity-input {
  width: 80px;
  height: 28px;
  text-align: center;
  border: 1px solid #4CAF50;
  border-radius: 4px;
  font-size: 0.875rem;
  padding: 0 0.5rem;
  outline: none;
  background: white;
}

.quantity-input:focus {
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
}

.quantity-input::placeholder {
  color: #a0aec0;
}
</style>