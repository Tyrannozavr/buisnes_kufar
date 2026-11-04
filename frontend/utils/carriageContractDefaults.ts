/** Текст договора по умолчанию (§2.2) — до выбора шаблона. */
export const DEFAULT_CARRIAGE_CONTRACT_BODY = `
<p><strong>1. Предмет договора</strong></p>
<p>1.1. Перевозчик обязуется по заданию Заказчика перевезти вверенный ему груз в пункт назначения и выдать его управомоченному на получение груза лицу, а Заказчик обязуется уплатить за перевозку груза установленную плату.</p>
<p><strong>2. Обязанности сторон</strong></p>
<p>2.1. Заказчик предоставляет Перевозчику сведения о грузе, необходимые для перевозки.</p>
<p>2.2. Перевозчик обеспечивает подачу транспортного средства в согласованные сроки.</p>
<p><strong>3. Расчёты</strong></p>
<p>3.1. Стоимость перевозки и порядок оплаты согласовываются сторонами дополнительно.</p>
<p><strong>4. Ответственность</strong></p>
<p>4.1. Стороны несут ответственность в соответствии с действующим законодательством.</p>
`.trim()

export type CarriagePartyPayload = {
	fullName: string
	companyType: string
	city: string
	index: string
	legalAddress: string
	inn: string
	kpp: string
	ogrn: string
	accountNumber: string
	bankName: string
	correspondentBankAccount: string
	bic: string
	officialPosition: string
	officialName: string
	foundationKind: string
	foundationTitle: string
}

export type CarriageContractPayload = {
	city: string
	customer: CarriagePartyPayload
	carrier: CarriagePartyPayload
	bodyHtml: string
	customerDetailsCheck: boolean
	carrierDetailsCheck: boolean
}

export const emptyCarriageParty = (): CarriagePartyPayload => ({
	fullName: '',
	companyType: '',
	city: '',
	index: '',
	legalAddress: '',
	inn: '',
	kpp: '',
	ogrn: '',
	accountNumber: '',
	bankName: '',
	correspondentBankAccount: '',
	bic: '',
	officialPosition: '',
	officialName: '',
	foundationKind: 'Устава',
	foundationTitle: '',
})
