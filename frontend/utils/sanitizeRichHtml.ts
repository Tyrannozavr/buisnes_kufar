/** Минимальная санация HTML перед v-html (без внешних зависимостей). */

const BLOCKED_TAGS =
	/<\s*\/?\s*(script|iframe|object|embed|link|meta|base|form|svg|math)\b[^>]*>/gi
const EVENT_ATTR = /\son\w+\s*=\s*(['"]).*?\1|\son\w+\s*=\s*[^\s>]+/gi
const JS_URL =
	/(href|src|xlink:href|action)\s*=\s*(['"]?)\s*javascript:[^'">\s]*\2?/gi

export function sanitizeRichHtml(html: string | null | undefined): string {
	if (!html) return ''
	return html
		.replace(BLOCKED_TAGS, '')
		.replace(EVENT_ATTR, '')
		.replace(JS_URL, '$1="#"')
}
