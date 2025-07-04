import { ref, onUnmounted } from 'vue'

interface WebSocketMessage {
  type: string
  [key: string]: any
}

interface WebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void
  onOpen?: () => void
  onClose?: () => void
  onError?: (error: Event) => void
}

export function useWebSocket(url: string, options: WebSocketOptions = {}) {
  const socket = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const isConnecting = ref(false)
  const error = ref<string | null>(null)

  const connect = () => {
    if (socket.value?.readyState === WebSocket.OPEN) {
      return
    }

    isConnecting.value = true
    error.value = null

    try {
      socket.value = new WebSocket(url)

      socket.value.onopen = () => {
        isConnected.value = true
        isConnecting.value = false
        options.onOpen?.()
      }

      socket.value.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          options.onMessage?.(message)
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e)
        }
      }

      socket.value.onclose = (event) => {
        isConnected.value = false
        isConnecting.value = false
        options.onClose?.()
      }

      socket.value.onerror = (event) => {
        isConnected.value = false
        isConnecting.value = false
        error.value = 'WebSocket connection error'
        options.onError?.(event)
      }
    } catch (e) {
      isConnecting.value = false
      error.value = 'Failed to create WebSocket connection'
    }
  }

  const disconnect = () => {
    if (socket.value) {
      socket.value.close()
      socket.value = null
    }
    isConnected.value = false
    isConnecting.value = false
  }

  const send = (message: WebSocketMessage) => {
    if (socket.value?.readyState === WebSocket.OPEN) {
      socket.value.send(JSON.stringify(message))
    } else {
      console.error('WebSocket is not connected')
    }
  }

  const sendTyping = (isTyping: boolean) => {
    send({
      type: 'typing',
      is_typing: isTyping
    })
  }

  const ping = () => {
    send({ type: 'ping' })
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    socket,
    isConnected,
    isConnecting,
    error,
    connect,
    disconnect,
    send,
    sendTyping,
    ping
  }
} 