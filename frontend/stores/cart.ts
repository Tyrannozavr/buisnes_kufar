import { defineStore } from 'pinia'
import type { ProductItemPublic} from '~/types/product'

interface CartItem {
  product: ProductItemPublic
  quantity: number
}

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: [] as CartItem[],
  }),

  getters: {
    totalUniqueItems: (state) => state.items.length,
    totalQuantity: (state) => state.items.reduce((sum, item) => sum + item.quantity, 0),
    totalPrice: (state) => state.items.reduce((sum, item) => sum + item.product.price * item.quantity, 0),
    totalItems: (state) => state.items.reduce((sum, item) => sum + item.quantity, 0),
  },

  actions: {
    init() {
      if (process.client) {
        const savedCart = localStorage.getItem('cart')
        if (savedCart) {
          try {
            const parsedCart = JSON.parse(savedCart)
            this.items = parsedCart
            console.log('Loaded initial state from localStorage:', this.items)
          } catch (e) {
            console.error('Error loading cart from localStorage:', e)
          }
        }
      }
    },

    addToCart(product: ProductItemPublic) {
      const existingItem = this.items.find(item => item.product.slug === product.slug)
      
      if (existingItem) {
        existingItem.quantity++
      } else {
        this.items.push({
          product,
          quantity: 1
        })
      }
      this.saveToStorage()
      console.log('Cart after adding:', [...this.items])
    },

    removeFromCart(productSlug: string) {
      const index = this.items.findIndex(item => item.product.slug === productSlug)
      if (index > -1) {
        this.items.splice(index, 1)
        this.saveToStorage()
      }
      console.log('Cart after removing:', [...this.items])
    },

    updateQuantity(productSlug: string, quantity: number) {
      const item = this.items.find(item => item.product.slug === productSlug)
      if (item) {
        item.quantity = Math.max(0, quantity)
        if (item.quantity === 0) {
          this.removeFromCart(productSlug)
        } else {
          this.saveToStorage()
        }
      }
      console.log('Cart after updating quantity:', [...this.items])
    },

    clearCart() {
      this.items = []
      this.saveToStorage()
      console.log('Cart cleared')
    },

    saveToStorage() {
      if (process.client) {
        // Преобразуем Proxy в обычный объект перед сохранением
        const itemsToSave = this.items.map(item => ({
          product: { ...item.product },
          quantity: item.quantity
        }))
        localStorage.setItem('cart', JSON.stringify(itemsToSave))
        console.log('Saved to localStorage:', itemsToSave)
      }
    }
  }
})