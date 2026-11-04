import type { NavigationMenuItem } from '~/types/navigation'
import { getMyCompany } from '~/api/companyOwner'
import { isLogisticsTradeActivity } from '~/types/company'

/** Общее меню разделов ЛК (сайдбар + мобильные меню). */
export const useProfileNavigation = () => {
	const route = useRoute()
	const tradeActivity = ref<string | null>(null)
	const companyLoaded = ref(false)

	const loadCompany = async () => {
		try {
			const company = await getMyCompany()
			tradeActivity.value = company?.trade_activity ?? null
		} catch {
			tradeActivity.value = null
		} finally {
			companyLoaded.value = true
		}
	}

	const isLogistics = computed(() => isLogisticsTradeActivity(tradeActivity.value))

	const navigationItems = computed((): NavigationMenuItem[][] => {
		const companyBlock: NavigationMenuItem[] = [
			{ label: 'Управление компанией', type: 'label' },
			{
				label: 'Данные компании',
				icon: 'i-heroicons-building-office',
				to: '/profile',
				active: route.path === '/profile',
			},
		]

		if (isLogistics.value) {
			companyBlock.push(
				{
					label: 'Транспорт',
					icon: 'i-heroicons-truck',
					to: '/profile/transport',
					active: route.path === '/profile/transport',
				},
				{
					label: 'Водители',
					icon: 'i-heroicons-identification',
					to: '/profile/drivers',
					active: route.path === '/profile/drivers',
				},
			)
		} else {
			companyBlock.push({
				label: 'Продукция',
				icon: 'i-heroicons-cube',
				to: '/profile/products',
				active: route.path === '/profile/products',
			})
		}

		companyBlock.push({
			label: 'Объявления',
			icon: 'i-heroicons-megaphone',
			to: '/profile/announcements',
			active: route.path === '/profile/announcements',
		})

		const businessBlock: NavigationMenuItem[] = [
			{ label: 'Бизнес-связи', type: 'label' },
			{
				label: 'Контрагенты',
				icon: 'i-heroicons-user-group',
				to: '/profile/partners',
				active: route.path === '/profile/partners' || route.path === '/profile/counterparties',
			},
			{
				label: 'Перевозчики',
				icon: 'i-heroicons-truck',
				to: '/profile/carriers',
				active: route.path === '/profile/carriers',
			},
		]

		if (!isLogistics.value) {
			businessBlock.push(
				{
					label: 'Поставщики',
					icon: 'i-heroicons-building-storefront',
					to: '/profile/suppliers',
					active: route.path === '/profile/suppliers',
				},
				{
					label: 'Покупатели',
					icon: 'i-heroicons-shopping-cart',
					to: '/profile/buyers',
					active: route.path === '/profile/buyers',
				},
			)
		}

		const docsBlock: NavigationMenuItem[] = [
			{ label: 'Документы и финансы', type: 'label' },
			{
				label: 'Документы',
				icon: 'i-heroicons-document-text',
				to: '/profile/documents',
				active: route.path === '/profile/documents',
			},
		]

		if (!isLogistics.value) {
			docsBlock.push(
				{
					label: 'Договоры',
					icon: 'i-heroicons-document-duplicate',
					to: '/profile/contracts',
					active: route.path === '/profile/contracts',
				},
				{
					label: 'Редактор документов',
					icon: 'i-heroicons-pencil-square',
					to: '/profile/editor',
					active: route.path === '/profile/editor',
				},
				{
					label: 'Закупки',
					icon: 'i-heroicons-shopping-bag',
					to: '/profile/purchases',
					active: route.path === '/profile/purchases',
				},
				{
					label: 'Продажи',
					icon: 'i-heroicons-banknotes',
					to: '/profile/sales',
					active: route.path.startsWith('/profile/sales'),
				},
			)
		}

		const shipmentsBlock: NavigationMenuItem[] = [
			{ label: 'Перевозки', type: 'label' },
			{
				label: 'Перевозки',
				icon: 'i-heroicons-map',
				to: '/profile/shipments',
				active: route.path === '/profile/shipments',
			},
			{
				label: 'Заявки',
				icon: 'i-heroicons-clipboard-document-list',
				to: '/profile/shipment-requests',
				active: route.path === '/profile/shipment-requests',
			},
			{
				label: 'Избранное',
				icon: 'i-heroicons-star',
				to: '/profile/shipment-favorites',
				active: route.path === '/profile/shipment-favorites',
			},
		]

		return [
			companyBlock,
			businessBlock,
			docsBlock,
			shipmentsBlock,
			[
				{ label: 'Управление', type: 'label' },
				{
					label: 'Сообщения',
					icon: 'i-heroicons-chat-bubble-left-right',
					to: '/profile/messages',
					active: route.path.startsWith('/profile/messages'),
					slot: 'messages',
				},
				{
					label: 'Авторизация',
					icon: 'i-heroicons-key',
					to: '/profile/auth',
					active: route.path === '/profile/auth',
				},
				{
					label: 'Администрирование',
					icon: 'i-heroicons-users',
					to: '/profile/administration',
					active: route.path === '/profile/administration',
				},
			],
		]
	})

	/** Плоский список ссылок ЛК (без заголовков групп). */
	const profileLinks = computed(() =>
		navigationItems.value.flatMap(group =>
			group.filter(item => item.type !== 'label' && item.to),
		),
	)

	return {
		tradeActivity,
		companyLoaded,
		isLogistics,
		navigationItems,
		profileLinks,
		loadCompany,
	}
}
