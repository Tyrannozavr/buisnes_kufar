import {useChatsApi} from "~/api/chats";

const { createChat } = useChatsApi()


export async function navigateToChatById(companyId: number) {
    const { chat_id } = await createChat({
        participantId: companyId,
    })
    if (chat_id) {
        navigateTo(`/profile/messages/${chat_id}`)
    }
}

export async function navigateToChatBySlug(companySlug: string) {
    const { chat_id } = await createChat({
        participantSlug: companySlug,
    })
    if (chat_id) {
        navigateTo(`/profile/messages/${chat_id}`)
    }
}
