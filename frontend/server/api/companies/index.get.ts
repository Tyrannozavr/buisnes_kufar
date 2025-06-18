import { defineEventHandler, getQuery } from 'h3'
import type { Company } from '~/types/company'
import { companies } from '../companies.get'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const page = Number(query.page) || 1
  const perPage = Number(query.perPage) || 10

  // Calculate pagination
  const total = companies.length
  const totalPages = Math.ceil(total / perPage)
  const start = (page - 1) * perPage
  const end = start + perPage

  // Get paginated data
  const data = companies.slice(start, end)

  return {
    data,
    pagination: {
      total,
      page,
      perPage,
      totalPages
    }
  }
}) 