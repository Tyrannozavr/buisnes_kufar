export const usePdfGenerator = () => {
	const ensureClient = () => {
		if (import.meta.server) {
			throw new Error("usePdfGenerator is client-only (SSR disabled for this feature)");
		}
	};

	/** Те же link/style, что на странице (Tailwind, scoped Vue). */
	const collectDocumentStylesMarkup = (): string => {
		const chunks: string[] = [];
		document.querySelectorAll('link[rel="stylesheet"]').forEach((node) => {
			const link = node as HTMLLinkElement;
			if (!link.href) {
				return;
			}
			const href = link.href.replace(/"/g, "&quot;");
			chunks.push(`<link rel="stylesheet" href="${href}">`);
		});
		document.querySelectorAll("style").forEach((node) => {
			const text = node.textContent;
			if (text?.trim()) {
				chunks.push(`<style>${text}</style>`);
			}
		});
		return chunks.join("\n");
	};

	/**
	 * Внешние CSS подгружаются асинхронно: если вызвать print() сразу — в превью голый HTML
	 * (Times, без border из Tailwind). Ждём link[rel=stylesheet] (или сразу, если лист уже в кэше).
	 */
	const whenPrintDomReady = (doc: Document, callback: () => void): void => {
		const links = [...doc.querySelectorAll('link[rel="stylesheet"]')] as HTMLLinkElement[];
		if (links.length === 0) {
			queueMicrotask(callback);
			return;
		}
		let remaining = links.length;
		const tick = (): void => {
			remaining -= 1;
			if (remaining <= 0) {
				queueMicrotask(callback);
			}
		};
		for (const link of links) {
			if (link.sheet != null) {
				tick();
				continue;
			}
			link.addEventListener("load", tick, { once: true });
			link.addEventListener("error", tick, { once: true });
		}
	};

	const replaceTextareasAndInputs = (element: any) => {
		const newElement: HTMLElement = element.cloneNode(true) as HTMLElement;
		document.body.appendChild(newElement);
		// Не задавать fontSize/lineHeight на корне — ломает наследование Tailwind и сетку таблиц

		const textareas = newElement.querySelectorAll("textarea");
		const inputs = newElement.querySelectorAll("input");

		textareas.forEach((textarea: any) => {
			const div = document.createElement("div");
			div.textContent = textarea.value;
			div.style.cssText = getComputedStyle(textarea).cssText;
			div.style.whiteSpace = "pre-wrap";
			div.style.display = "block";
			div.style.minHeight = textarea.offsetHeight + "px";
			div.style.padding = "5px";
			textarea.parentNode?.replaceChild(div, textarea);
		});

		inputs.forEach((input: any) => {
			const span = document.createElement("span");
			span.textContent = input.value;
			span.style.cssText = getComputedStyle(input).cssText;
			span.style.display = "inline";
			span.style.lineHeight = "1.75";
			span.style.minHeight = input.offsetHeight + "px";
			span.style.minWidth = input.offsetWidth + "px";
			span.style.padding = "3px";
			span.style.marginBlock = "30px";
			input.parentNode?.replaceChild(span, input);
		});

		return newElement;
	};

	const printDocument = (element: HTMLElement | any): void => {
		ensureClient();
		const styleInjection = collectDocumentStylesMarkup();
		const baseHref = (() => {
			try {
				return new URL(".", document.baseURI).href;
			} catch {
				return `${window.location.origin}/`;
			}
		})();
		const printWindow = window.open("", "", "height=600, width=900");
		if (!printWindow) {
			element.remove();
			return;
		}

		const doc = printWindow.document;
		doc.open();
		doc.write(`
<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8" />
		<base href="${baseHref.replace(/"/g, "&quot;")}" />
		<title>Печать документа …</title>
		${styleInjection}
		<style>
			h1 {
				text-align: center;
				font-size: 24px;
			}
			h1 ~ table {
				width: 100%;
			}
			th {
				text-align: start;
			}
		</style>
	</head>
	<body>
		${element.innerHTML}
	</body>
</html>
`);
		doc.close();

		whenPrintDomReady(doc, () => {
			// Дать браузеру применить стили к layout перед диалогом печати
			requestAnimationFrame(() => {
				requestAnimationFrame(() => {
					printWindow.focus();
					printWindow.print();
					printWindow.close();
					element.remove();
				});
			});
		});
	};

	return {
		printDocument,
		replaceTextareasAndInputs,
	};
};
