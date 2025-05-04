import type { Company } from '~/types/company'

export const useCompany = () => {
  const company = ref<Company | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchCompany = async () => {
    loading.value = true
    error.value = null
    
    try {
      const { data } = await useFetch<Company>('/api/company/me')
      company.value = data.value
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch company data'
    } finally {
      loading.value = false
    }
  }

  const updateCompany = async (companyData: Partial<Company>) => {
    loading.value = true
    error.value = null
    
    try {
      const { data } = await useFetch('/api/company/me', {
        method: 'PUT',
        body: companyData
      })
      
      if (data.value?.success) {
        await fetchCompany()
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update company data'
    } finally {
      loading.value = false
    }
  }

  return {
    company,
    loading,
    error,
    fetchCompany,
    updateCompany
  }
} 