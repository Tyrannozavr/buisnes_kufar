import {
	emptyCarriageParty,
	type CarriagePartyPayload,
} from './carriageContractDefaults'

/** Пункты 1–7 образца договор-заявки (§4.1). */
export const DEFAULT_CARRIAGE_ORDER_EXTRA_TERMS = `
<ol>
<li>Перевозчик подаёт исправное транспортное средство, пригодное для перевозки груза.</li>
<li>Перевозчик контролирует погрузку и размещение груза.</li>
<li>Товарно-транспортная накладная (ТН/ТТН) оформляется в 4 экземплярах.</li>
<li>Приём груза осуществляется по ТН; при выгрузке составляется акт при необходимости.</li>
<li>При обнаружении дефектов упаковки или повреждений груза Перевозчик не убывает с места без отметки.</li>
<li>Оплата перевозки производится не позднее дня, следующего за выставлением счёта.</li>
<li>Настоящий договор-заявка составлен в 2 экземплярах, имеющих одинаковую юридическую силу.</li>
</ol>
`.trim()

export const CARRIAGE_ORDER_INTRO =
	'Перевозчик принимает на себя обязательство перевезти груз на условиях настоящей заявки, а Заказчик — оплатить перевозку.'

export type CarriageOrderPayload = {
	city: string
	preambleDate: string
	customer: CarriagePartyPayload
	carrier: CarriagePartyPayload
	extraTermsHtml: string
	customerDetailsCheck: boolean
	carrierDetailsCheck: boolean
	cargoTableSnapshot?: Record<string, string>
}

export const emptyCarriageOrderPayload = (): CarriageOrderPayload => ({
	city: '',
	preambleDate: '',
	customer: emptyCarriageParty(),
	carrier: emptyCarriageParty(),
	extraTermsHtml: DEFAULT_CARRIAGE_ORDER_EXTRA_TERMS,
	customerDetailsCheck: true,
	carrierDetailsCheck: true,
})
