import {useChatsApi} from "~/api/chats";

const { createChat } = useChatsApi()

export async function navigateToChatById(companyId: number) {
    const chatData = await createChat({
        participantId: companyId,
    })
    if (chatData.id) {
        navigateTo(`/profile/messages/${chatData.id}`)
    }
}

export async function navigateToChatBySlug(companySlug: string) {
    const chatData = await createChat({
        participantSlug: companySlug,
    })
    if (chatData.id) {
        navigateTo(`/profile/messages/${chatData.id}`)
    }
}

export async function createChatForCompany(companySlug: string, companyName: string, companyLogo?: string | null) {
    try {
        const chatData = await createChat({
            participantSlug: companySlug,
            participantName: companyName,
            participantLogo: companyLogo || undefined
        })
        return chatData
    } catch (error) {
        console.error('Failed to create chat:', error)
        throw error
    }
}
