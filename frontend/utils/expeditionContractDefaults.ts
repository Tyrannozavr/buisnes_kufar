import {
	emptyCarriageParty,
	type CarriagePartyPayload,
} from './carriageContractDefaults'

/** Текст договора экспедиции по умолчанию (§4.2). */
export const DEFAULT_EXPEDITION_CONTRACT_BODY = `
<p><strong>1. Предмет договора</strong></p>
<p>1.1. Экспедитор обязуется за вознаграждение и за счёт Клиента выполнить или организовать выполнение определённых договором экспедиционных услуг, связанных с перевозкой груза.</p>
<p><strong>2. Обязанности сторон</strong></p>
<p>2.1. Клиент предоставляет Экспедитору сведения о грузе, документы и инструкции, необходимые для исполнения поручения.</p>
<p>2.2. Экспедитор действует добросовестно и в интересах Клиента, информирует о ходе исполнения.</p>
<p><strong>3. Расчёты</strong></p>
<p>3.1. Вознаграждение Экспедитора и порядок оплаты согласовываются сторонами дополнительно.</p>
<p><strong>4. Ответственность</strong></p>
<p>4.1. Стороны несут ответственность в соответствии с действующим законодательством РФ.</p>
`.trim()

export type ExpeditionContractPayload = {
	city: string
	client: CarriagePartyPayload
	forwarder: CarriagePartyPayload
	bodyHtml: string
	clientDetailsCheck: boolean
	forwarderDetailsCheck: boolean
}

export const emptyExpeditionContractPayload = (): ExpeditionContractPayload => ({
	city: '',
	client: emptyCarriageParty(),
	forwarder: emptyCarriageParty(),
	bodyHtml: DEFAULT_EXPEDITION_CONTRACT_BODY,
	clientDetailsCheck: true,
	forwarderDetailsCheck: true,
})
