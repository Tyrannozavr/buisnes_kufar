import {useChatsApi} from "~/api/chats";

const { createChat } = useChatsApi()


export async function navigateToChat(companyId: number) {
    const { chat_id } = await createChat(companyId)
    if (chat_id) {
        navigateTo(`/profile/messages/${chat_id}`)
    }
}