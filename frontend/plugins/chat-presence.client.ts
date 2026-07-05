import {
	connectChatPresence,
	disconnectChatPresence,
	onChatPresenceMessage,
} from '~/composables/useChatPresence'
import { useChatUnreadStore } from '~/stores/chatUnread'
import { useUserStore } from '~/stores/user'
import { getActiveChatIdFromRoute } from '~/utils/chatUnread'

export default defineNuxtPlugin(() => {
	if (!import.meta.client) return

	const accessToken = useCookie('access_token')
	const chatUnreadStore = useChatUnreadStore()
	const userStore = useUserStore()
	const router = useRouter()

	let unsubscribePresence: (() => void) | null = null
	let refreshTimer: ReturnType<typeof setTimeout> | null = null

	const scheduleUnreadRefresh = () => {
		if (refreshTimer) clearTimeout(refreshTimer)
		refreshTimer = setTimeout(() => {
			refreshTimer = null
			void chatUnreadStore.refresh()
		}, 800)
	}

	const subscribePresenceEvents = () => {
		if (unsubscribePresence) return
		unsubscribePresence = onChatPresenceMessage((message) => {
			if (message.type === 'new_message') {
				const payload = message.message as Record<string, unknown> | undefined
				chatUnreadStore.noteIncomingMessage({
					chatId: Number(message.chat_id),
					senderCompanyId: Number(payload?.sender_company_id) || null,
					viewerCompanyId: userStore.companyId
						? Number(userStore.companyId)
						: null,
					activeChatId: getActiveChatIdFromRoute(router.currentRoute.value),
					pageVisible: document.visibilityState === 'visible',
				})
			}
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
