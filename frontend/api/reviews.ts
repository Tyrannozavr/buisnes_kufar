import type { Review } from '~/types/review'

export const useReviewsApi = () => {
  const submitReview = async (companyId: string, reviewData: { rating: number; text: string }) => {
    return await useApi<Review>(`/companies/${companyId}/reviews`, {
      method: 'POST',
      body: reviewData
    })
  }

  return {
    submitReview
  }
} 