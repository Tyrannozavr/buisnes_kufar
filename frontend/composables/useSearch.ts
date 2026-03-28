import { ref, type Ref } from "vue";

const HIGHLIGHT_CLASS = "search-highlight";
const ACTIVE_CLASS = "search-highlight-active";

const escapeRegex = (value: string): string =>
	value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

const clearHighlights = (root: HTMLElement): void => {
	root.querySelectorAll(`mark.${HIGHLIGHT_CLASS}`).forEach((mark) => {
		const parent = mark.parentNode;
		if (!parent) {
			return;
		}
		while (mark.firstChild) {
			parent.insertBefore(mark.firstChild, mark);
		}
		parent.removeChild(mark);
		parent.normalize();
	});
	root.querySelectorAll("input, textarea").forEach((el) => {
		const h = el as HTMLElement;
		h.style.backgroundColor = "";
		h.style.outline = "";
		h.classList.remove(ACTIVE_CLASS);
	});
};

const collectTextNodes = (root: HTMLElement): Text[] => {
	const out: Text[] = [];
	const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
		acceptNode(node: Node): number {
			const parent = (node as Text).parentElement;
			if (!parent) {
				return NodeFilter.FILTER_REJECT;
			}
			if (parent.closest("script, style, noscript")) {
				return NodeFilter.FILTER_REJECT;
			}
			if (parent.closest("textarea, input")) {
				return NodeFilter.FILTER_REJECT;
			}
			if (parent.closest(`mark.${HIGHLIGHT_CLASS}`)) {
				return NodeFilter.FILTER_REJECT;
			}
			return NodeFilter.FILTER_ACCEPT;
		},
	});
	let n: Node | null = walker.nextNode();
	while (n) {
		out.push(n as Text);
		n = walker.nextNode();
	}
	return out;
};

const highlightTextNode = (textNode: Text, query: string): void => {
	const text = textNode.textContent ?? "";
	if (!text) {
		return;
	}
	const pattern = escapeRegex(query);
	const regex = new RegExp(`(${pattern})`, "gi");
	const parts = text.split(regex);
	if (parts.length <= 1) {
		return;
	}
	const fragment = document.createDocumentFragment();
	for (let i = 0; i < parts.length; i++) {
		const part = parts[i];
		if (!part) {
			continue;
		}
		const isMatch = i % 2 === 1;
		if (isMatch) {
			const mark = document.createElement("mark");
			mark.className = HIGHLIGHT_CLASS;
			mark.style.backgroundColor = "#ffeb3b";
			mark.textContent = part;
			fragment.appendChild(mark);
		} else {
			fragment.appendChild(document.createTextNode(part));
		}
	}
	textNode.parentNode?.replaceChild(fragment, textNode);
};

const highlightInputs = (root: HTMLElement, queryLower: string): void => {
	const q = queryLower.trim();
	if (!q) {
		return;
	}
	root.querySelectorAll("input, textarea").forEach((el) => {
		const field = el as HTMLInputElement | HTMLTextAreaElement;
		const val = field.value?.toLowerCase() ?? "";
		if (val.includes(q)) {
			field.style.backgroundColor = "#ffeb3b";
		}
	});
};

/** Все совпадения в порядке документа (как в Ctrl+F): mark, затем поля с подстрокой */
const collectMatchesInDocumentOrder = (
	root: HTMLElement,
	queryLower: string
): HTMLElement[] => {
	const q = queryLower.trim();
	if (!q) {
		return [];
	}
	const nodes = Array.from(
		root.querySelectorAll(`mark.${HIGHLIGHT_CLASS}, input, textarea`)
	) as HTMLElement[];
	return nodes.filter((el) => {
		if (el.tagName === "MARK") {
			return el.classList.contains(HIGHLIGHT_CLASS);
		}
		const v = (el as HTMLInputElement).value?.toLowerCase() ?? "";
		return v.includes(q);
	});
};

const applyActiveStyles = (matches: HTMLElement[], activeIndex: number): void => {
	matches.forEach((el, i) => {
		const active = i === activeIndex;
		if (el.tagName === "MARK") {
			el.classList.toggle(ACTIVE_CLASS, active);
			el.style.backgroundColor = active ? "#ff9800" : "#ffeb3b";
			el.style.outline = active ? "2px solid #e65100" : "";
		} else {
			const h = el as HTMLElement;
			h.classList.toggle(ACTIVE_CLASS, active);
			h.style.backgroundColor = "#ffeb3b";
			h.style.outline = active ? "2px solid #e65100" : "";
		}
	});
};

export const useSearch = () => {
	const matchTotal: Ref<number> = ref(0);
	/** 1-based для отображения «3 / 12», 0 если нет совпадений */
	const matchCurrent: Ref<number> = ref(0);

	let matches: HTMLElement[] = [];
	let activeIndex = -1;

	const syncActiveScroll = (): void => {
		if (activeIndex < 0 || activeIndex >= matches.length) {
			return;
		}
		const el = matches[activeIndex];
		if (!el) {
			return;
		}
		el.scrollIntoView({ block: "center", behavior: "smooth" });
	};

	const updateActiveMatch = (): void => {
		applyActiveStyles(matches, activeIndex);
		matchTotal.value = matches.length;
		matchCurrent.value =
			matches.length === 0 ? 0 : activeIndex + 1;
		syncActiveScroll();
	};

	const searchInDocument = (element: HTMLElement | null, inputValue: string): void => {
		if (!element) {
			return;
		}
		clearHighlights(element);
		matches = [];
		activeIndex = -1;
		matchTotal.value = 0;
		matchCurrent.value = 0;

		const trimmed = inputValue.trim();
		if (!trimmed) {
			return;
		}
		const queryLower = trimmed.toLowerCase();

		const textNodes = collectTextNodes(element);
		for (const textNode of textNodes) {
			highlightTextNode(textNode, trimmed);
		}
		highlightInputs(element, queryLower);

		matches = collectMatchesInDocumentOrder(element, queryLower);
		if (matches.length > 0) {
			activeIndex = 0;
			updateActiveMatch();
		}
	};

	const goToNextMatch = (): void => {
		if (matches.length === 0) {
			return;
		}
		activeIndex = (activeIndex + 1) % matches.length;
		updateActiveMatch();
	};

	const goToPreviousMatch = (): void => {
		if (matches.length === 0) {
			return;
		}
		activeIndex = (activeIndex - 1 + matches.length) % matches.length;
		updateActiveMatch();
	};

	/** Enter — следующее; Shift+Enter — предыдущее */
	const handleSearchKeydown = (e: KeyboardEvent): void => {
		if (e.key !== "Enter") {
			return;
		}
		e.preventDefault();
		if (e.shiftKey) {
			goToPreviousMatch();
		} else {
			goToNextMatch();
		}
	};

	return {
		searchInDocument,
		goToNextMatch,
		goToPreviousMatch,
		handleSearchKeydown,
		matchTotal,
		matchCurrent,
	};
};
