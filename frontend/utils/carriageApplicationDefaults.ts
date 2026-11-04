import {
	emptyCarriageParty,
	type CarriagePartyPayload,
} from '~/utils/carriageContractDefaults'

/** Доп. условия заявки по умолчанию (§3.2). */
export const DEFAULT_CARRIAGE_APPLICATION_EXTRA_TERMS = `
<p><strong>ДОПОЛНИТЕЛЬНЫЕ УСЛОВИЯ</strong></p>
<p>1. Стороны руководствуются условиями рамочного договора перевозки, к которому составлена настоящая заявка.</p>
<p>2. Подача транспортного средства — в сроки, указанные в таблице условий перевозки.</p>
<p>3. Изменение условий заявки допускается по согласованию сторон в письменной форме.</p>
`.trim()

export type CarriageApplicationPayload = {
	customer: CarriagePartyPayload
	carrier: CarriagePartyPayload
	extraTermsHtml: string
	customerDetailsCheck: boolean
	carrierDetailsCheck: boolean
	/** Снимок таблицы на момент «Заполнить данными» (опционально). */
	cargoTableSnapshot?: Record<string, string> | null
}

export const emptyCarriageApplicationPayload = (): CarriageApplicationPayload => ({
	customer: emptyCarriageParty(),
	carrier: emptyCarriageParty(),
	extraTermsHtml: DEFAULT_CARRIAGE_APPLICATION_EXTRA_TERMS,
	customerDetailsCheck: true,
	carrierDetailsCheck: true,
	cargoTableSnapshot: null,
})

export { emptyCarriageParty }
export type { CarriagePartyPayload }
