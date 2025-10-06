import html2canvas from "html2canvas-pro";
import { jsPDF } from "jspdf";

export const usePdfGenerator = () => {
  const replaceTextareasAndInputs = (element: any) => {
    const newElement: HTMLElement = element.cloneNode(true);
		document.body.appendChild(newElement)
		newElement.style.lineHeight = '1.75'
		newElement.style.fontSize = '32px'

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
			span.style.lineHeight = '1.75'
      span.style.minHeight = input.offsetHeight + "px";
      span.style.minWidth = input.offsetWidth + "px";
      span.style.padding = "3px";
			span.style.marginBlock = '30px'
      input.parentNode?.replaceChild(span, input);
    });

    return newElement;
  };

  const downloadPdf = async (element: HTMLElement | null, fileName: string) => {		
		const newElement = replaceTextareasAndInputs(element)
    console.log(newElement);

    const canvas = await html2canvas(newElement, { scale: 1, useCORS: true });
    const imgData = canvas.toDataURL("img/pdf");

    const pdf = new jsPDF("p", "mm", "a4");
    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();

    const imgWidth = pageWidth * 0.85;
    const imgHeight = (canvas.height * imgWidth) / canvas.width;

    let position = 10;
    let heightLeft = imgHeight;

    while (heightLeft > 0) {
      pdf.addImage(imgData, "PNG", 16, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;
      if (heightLeft > 0) {
        pdf.addPage();
        position = -heightLeft + imgHeight;
      }
    }

    pdf.save(`${fileName}.pdf`);
  };

const printDocument = (element: HTMLElement | any): void => {
	const newElement = replaceTextareasAndInputs(element)
	const printWindow = window.open('','', 'height=842, width=595')
	printWindow?.document.writeln(`
	<html>
		<head>
			<title>Печать документа ...</title>
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
			${newElement.innerHTML}
		</body>
	</html>
	`)
	printWindow?.document.close()
	printWindow?.focus()
	printWindow?.print()
	printWindow?.close()
}  

return {
    downloadPdf,
		printDocument,
		replaceTextareasAndInputs,
  };
};
