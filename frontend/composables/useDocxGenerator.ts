import type { GoodsDeal, ServicesDeal } from "~/types/dealState";

export const useDocxGenerator = () => {
  const ensureClient = () => {
    if (import.meta.server) {
      throw new Error("useDocxGenerator is client-only (SSR disabled for this feature)");
    }
  };

  const downloadBlob = (blob: Blob, fileName: string): void => {
    ensureClient();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = fileName;
    link.click();
    URL.revokeObjectURL(url);
  };

  const generateDocxOrder = async (orderDealData: GoodsDeal | ServicesDeal): Promise<Blob> => {
    ensureClient();
    const { generateDocxOrder: generateOrder } = await import('~/public/templates/docxOrder');
    return await generateOrder(orderDealData);
  };

  const generateDocxBill = async (data: any): Promise<Blob> => {
    ensureClient();
    const { generateDocxBill: generateBill } = await import("~/public/templates/docxBill");
    return await generateBill(data);
  };

  return {
    generateDocxOrder,
    generateDocxBill,
    downloadBlob,
  };
};
