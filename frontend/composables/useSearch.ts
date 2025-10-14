export const useSearch = () => {
	const searchInDocument = (element: any, inputValue: string) => {
	const allElements = element.querySelectorAll('input, span, h1, h2, div, textarea, a, pre')

	allElements.forEach((el: HTMLElement | any )=> {
		if (el.localName !== 'input' && el.localName !== 'textarea') {
			if (el.textContent.toLowerCase().includes(inputValue.toLowerCase()) && inputValue){
			el.style.backgroundColor = 'yellow'
		} else {
			el.style.backgroundColor = 'transparent'
		}
		}
		else if ( el.localName === 'input' || el.localName === 'textarea') {
			if (el.value.toLowerCase().includes(inputValue.toLowerCase()) && inputValue){
			el.style.backgroundColor = 'yellow'
		} else {
			el.style.backgroundColor = 'transparent'
		}
		}
		
	})
}

	return {
		searchInDocument,
	}
}