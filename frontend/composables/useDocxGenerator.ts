import { generateDocxOrder } from '~/public/templates/docxOrder'
import { generateDocxBill } from "~/public/templates/docxBill";

export const useDocxGenerator = () => {
	generateDocxOrder

	generateDocxBill
	

  const downloadBlob = (blob: Blob, fileName: string): void => {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = fileName;
    link.click();
    URL.revokeObjectURL(url);
  };

	
  return {
    generateDocxOrder,
		generateDocxBill,
    downloadBlob,
  };
};
