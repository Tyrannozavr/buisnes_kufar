import { defineStore } from 'pinia'
import type { Chat } from '~/types/chat'

export const useChatUnreadStore = defineStore('chatUnread', {
	state: () => ({
		chatsWithUnread: 0,
	}),

	getters: {
		hasUnread: (state) => state.chatsWithUnread > 0,
		badgeText: (state) => {
			if (state.chatsWithUnread <= 0) return ''
			return state.chatsWithUnread > 99 ? '99+' : String(state.chatsWithUnread)
		},
	},

	actions: {
		setFromChats(chats: Chat[]) {
			this.chatsWithUnread = chats.filter((chat) => (chat.unread_count ?? 0) > 0).length
		},

		async refresh() {
			const token = useCookie('access_token')
			if (!token.value) {
				this.chatsWithUnread = 0
				return
			}

			try {
				const { $api } = useNuxtApp()
				const chats = await $api.get<Chat[]>('/v1/chats')
				this.setFromChats(chats)
			} catch {
				// оставляем предыдущее значение
			}
		},

		clear() {
			this.chatsWithUnread = 0
		},
	},
})
