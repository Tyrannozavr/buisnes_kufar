import {
	connectChatPresence,
	disconnectChatPresence,
	onChatPresenceMessage,
} from '~/composables/useChatPresence'
import { useChatUnreadStore } from '~/stores/chatUnread'

export default defineNuxtPlugin(() => {
	if (!import.meta.client) return

	const accessToken = useCookie('access_token')
	const chatUnreadStore = useChatUnreadStore()

	let unsubscribePresence: (() => void) | null = null
	let refreshTimer: ReturnType<typeof setTimeout> | null = null

	const scheduleUnreadRefresh = () => {
		if (refreshTimer) clearTimeout(refreshTimer)
		refreshTimer = setTimeout(() => {
			refreshTimer = null
			void chatUnreadStore.refresh()
		}, 400)
	}

	const subscribePresenceEvents = () => {
		if (unsubscribePresence) return
		unsubscribePresence = onChatPresenceMessage((message) => {
			if (message.type === 'new_message' || message.type === 'messages_read') {
				scheduleUnreadRefresh()
			}
		})
	}

	const teardownPresenceEvents = () => {
		unsubscribePresence?.()
		unsubscribePresence = null
		if (refreshTimer) {
			clearTimeout(refreshTimer)
			refreshTimer = null
		}
	}

	watch(
		accessToken,
		(token) => {
			if (token) {
				connectChatPresence()
				subscribePresenceEvents()
				void chatUnreadStore.refresh()
			} else {
				disconnectChatPresence()
				teardownPresenceEvents()
				chatUnreadStore.clear()
			}
		},
		{ immediate: true },
	)
})
