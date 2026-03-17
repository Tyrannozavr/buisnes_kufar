import { defineQueryOptions} from "@pinia/colada"
import { getMyCompany } from "~/api/companyOwner"
import { QueryKeys } from "~/constants/queryKeys"

export const getMyCompanyQuery = defineQueryOptions(() => ({
	key: [QueryKeys.GET_MY_COMPANY],
	query: () => getMyCompany(),
}))