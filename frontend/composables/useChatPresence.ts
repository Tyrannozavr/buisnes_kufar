type PresenceMessage = Record<string, unknown>

let presenceSocket: WebSocket | null = null
let pingInterval: ReturnType<typeof setInterval> | null = null
let reconnectTimeout: ReturnType<typeof setTimeout> | null = null
const listeners = new Set<(message: PresenceMessage) => void>()

function buildPresenceUrl(): string | null {
	const accessToken = useCookie('access_token')
	if (!accessToken.value) return null

	const config = useRuntimeConfig()
	const base = config.public.apiBaseUrl?.replace(/^http/, 'ws')
	if (!base) return null

	return `${base}/v1/chats/presence/ws?token=${accessToken.value}`
}

function scheduleReconnect() {
	if (reconnectTimeout) return
	reconnectTimeout = setTimeout(() => {
		reconnectTimeout = null
		connectChatPresence()
	}, 5000)
}

export function connectChatPresence() {
	if (!import.meta.client) return

	const url = buildPresenceUrl()
	if (!url) return

	if (
		presenceSocket?.readyState === WebSocket.OPEN
		|| presenceSocket?.readyState === WebSocket.CONNECTING
	) {
		return
	}

	presenceSocket = new WebSocket(url)

	presenceSocket.onopen = () => {
		if (pingInterval) clearInterval(pingInterval)
		pingInterval = setInterval(() => {
			if (presenceSocket?.readyState === WebSocket.OPEN) {
				presenceSocket.send(JSON.stringify({ type: 'ping' }))
			}
		}, 30000)
	}

	presenceSocket.onmessage = (event) => {
		try {
			const message = JSON.parse(event.data) as PresenceMessage
			listeners.forEach((handler) => handler(message))
		} catch {
			// ignore malformed payloads
		}
	}

	presenceSocket.onclose = () => {
		if (pingInterval) {
			clearInterval(pingInterval)
			pingInterval = null
		}
		presenceSocket = null

		const token = useCookie('access_token')
		if (token.value) {
			scheduleReconnect()
		}
	}

	presenceSocket.onerror = () => {
		presenceSocket?.close()
	}
}

export function disconnectChatPresence() {
	if (reconnectTimeout) {
		clearTimeout(reconnectTimeout)
		reconnectTimeout = null
	}
	if (pingInterval) {
		clearInterval(pingInterval)
		pingInterval = null
	}
	if (presenceSocket) {
		presenceSocket.onclose = null
		presenceSocket.close()
		presenceSocket = null
	}
}

export function onChatPresenceMessage(handler: (message: PresenceMessage) => void) {
	listeners.add(handler)
	return () => listeners.delete(handler)
}
