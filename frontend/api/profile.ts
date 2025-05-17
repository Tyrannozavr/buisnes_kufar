import type { UserProfile } from '~/types/user'

export const useProfileApi = () => {
  const getProfile = async () => {
    return await useApi<UserProfile>('/profile')
  }

  const updateProfile = async (profileData: Partial<UserProfile>) => {
    return await useApi<UserProfile>('/profile', {
      method: 'PUT',
      body: profileData
    })
  }

  const uploadAvatar = async (file: File) => {
    const formData = new FormData()
    formData.append('avatar', file)
    return await useApi<UserProfile>('/profile/avatar', {
      method: 'POST',
      body: formData
    })
  }

  return {
    getProfile,
    updateProfile,
    uploadAvatar
  }
} 