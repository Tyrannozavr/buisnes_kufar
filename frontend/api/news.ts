import type {NewsItem} from '~/types/news'
import type {UseFetchOptions} from 'nuxt/app'

export const useNewsApi = () => {
    const getAllNews = (options: UseFetchOptions<NewsItem[]> = {}) => {
        return useApi<NewsItem[]>('/news', {
            ...options
        })
    }

    return {
        getAllNews,
    }
}