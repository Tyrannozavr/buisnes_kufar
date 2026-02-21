import { defineStore } from "pinia";
import type {
  GoodsDeal,
  ServicesDeal,
  EditPersonDeal,
  Product,
} from "~/types/dealState";
import { convert as numberToWordsRu } from "number-to-words-ru";
import { usePurchasesApi } from "~/api/purchases";
import type { DealUpdate, OrderItemUpdate, SellerDealResponse } from "~/types/dealResponse";

interface Sales {
  sales: {
    goodsDeals: GoodsDeal[];
    servicesDeals: ServicesDeal[];
  };
}

export const useSalesStore = defineStore("sales", {
  state: (): Sales => ({
    sales: {
      goodsDeals: [],
      servicesDeals: [],
    },
  }),

  getters: {
    findGoodsDealByDealNumber: (state) => {
      return (dealNumber: string) =>
        state.sales.goodsDeals?.find(
          (deal) => dealNumber === deal.sellerOrderNumber,
        );
    },

    findServicesDealByDealNumber: (state) => {
      return (dealNumber: string) =>
        state.sales.servicesDeals?.find(
          (deal) => dealNumber === deal.sellerOrderNumber,
        );
    },

    findGoodsDeal: (state) => {
      return (dealId: number) =>
        state.sales.goodsDeals?.find((deal) => dealId === deal.dealId);
    },

    findServicesDeal: (state) => {
      return (dealId: number) =>
        state.sales.servicesDeals?.find((deal) => dealId === deal.dealId);
    },

    lastGoodsDeal: (state): GoodsDeal | undefined => {
      if (state.sales.goodsDeals?.[0]) {
        const goodsDeals = state.sales.goodsDeals;
        let maxDealId = 0;
        goodsDeals?.forEach((deal) => {
          if (deal.dealId > maxDealId) {
            maxDealId = deal.dealId;
          }
        });

        const lastDeal = state.sales.goodsDeals?.find(
          (deal) => deal.dealId === maxDealId,
        );

        return lastDeal;
      }
    },

    lastServicesDeal: (state): ServicesDeal | undefined => {
      if (state.sales.servicesDeals?.[0]) {
        const servicesDeals = state.sales.servicesDeals;
        let maxDealId = 0;
        servicesDeals?.forEach((deal) => {
          if (deal.dealId > maxDealId) {
            maxDealId = deal.dealId;
          }
        });

        const lastDeal = state.sales.servicesDeals?.find(
          (deal) => deal.dealId === maxDealId,
        );

        return lastDeal;
      }
    },

    createBodyForUpdate:
      (state) =>
      (orderId: number): DealUpdate | null => {
        const deal: GoodsDeal | ServicesDeal | undefined =
          state.sales.goodsDeals?.find((d) => d.dealId === orderId) ??
          state.sales.servicesDeals?.find((d) => d.dealId === orderId);

        if (!deal) return null;

        const items = "goods" in deal ? deal.goods : deal.services;
        const products =
          "goodsList" in items ? items.goodsList : items.servicesList;

        const itemsList: OrderItemUpdate[] = (products ?? []).map((p) => ({
          product_name: p.name?.trim() || "—",
          quantity: p.quantity,
          unit_of_measurement: p.units?.trim() || "шт",
          price: p.price,
        }));

        const body: DealUpdate = {
          items: itemsList,
          comments: items.comments ?? undefined,
        };
        if (deal.status) body.status = deal.status;
        if (deal.contractNumber) body.contract_number = deal.contractNumber;
        if (deal.billNumber) body.bill_number = deal.billNumber;
        if (deal.supplyContractNumber)
          body.supply_contracts_number = deal.supplyContractNumber;
        return body;
      },
  },

  actions: {
    async clearStore() {
      this.sales.goodsDeals = [];
      this.sales.servicesDeals = [];
    },
    //получение и заполнение списка сделок
    async getDeals() {
      this.clearStore();

      const { getDealById, getSellerDeals } = usePurchasesApi();
      const sellerDeals = await getSellerDeals();
      const dealsIds: number[] = [
        ...new Set(
          sellerDeals?.map((deal: SellerDealResponse) => deal.id) || [],
        ),
      ];

      //функция для преобразования и данных и заполнения списка сделок
      const fillDeals = async (dealId: number) => {
        const dealResponse = await getDealById(dealId);

        if (dealResponse) {
          if (dealResponse.deal_type === "Товары") {
            this.addNewGoodsDeal({
              dealId: dealResponse.id,
              sellerOrderNumber: dealResponse.seller_order_number,
              buyerOrderNumber: dealResponse.buyer_order_number,
              goods: {
                goodsList: dealResponse.items.map((item: any) => ({
                  name: item.product_name,
                  article: item.product_article,
                  quantity: item.quantity,
                  units: item.unit_of_measurement,
                  price: item.price,
                  amount: item.amount,
                  type: dealResponse.deal_type,
                })),
                amountPrice: 0,
                amountWord: "",
                comments: dealResponse.comments ?? "",
              },
              date: dealResponse.created_at,
              seller: {
                companyName: dealResponse.seller_company.company_name,
                sellerName: dealResponse.seller_company.name,
                phone: dealResponse.seller_company.phone,
                slug: dealResponse.seller_company.slug,
                companyId: dealResponse.seller_company.id,
                inn: dealResponse.seller_company.inn,
                email: dealResponse.seller_company.email,
                legalAddress: dealResponse.seller_company.legal_address,
              },
              buyer: {
                buyerName: dealResponse.buyer_company.name,
                companyName: dealResponse.buyer_company.company_name,
                phone: dealResponse.buyer_company.phone,
                slug: dealResponse.buyer_company.slug,
                companyId: dealResponse.buyer_company.id,
                inn: dealResponse.buyer_company.inn,
                email: dealResponse.buyer_company.email,
                legalAddress: dealResponse.buyer_company.legal_address,
              },
              status: dealResponse.status,
              billNumber: dealResponse.bill_number || "",
              billDate: dealResponse.bill_date || "",
              supplyContractNumber: dealResponse.supply_contracts_number || "",
              closingDocuments: dealResponse.closing_documents || [],
              othersDocuments: dealResponse.others_documents || [],
            });
          } else if (dealResponse.deal_type === "Услуги") {
            this.addNewServicesDeal({
              dealId: dealResponse.id,
              sellerOrderNumber: dealResponse.seller_order_number,
              buyerOrderNumber: dealResponse.buyer_order_number,
              services: {
                servicesList: dealResponse.items.map((item: any) => ({
                  name: item.product_name,
                  article: item.product_article,
                  quantity: item.quantity,
                  units: item.unit_of_measurement,
                  price: item.price,
                  amount: item.amount,
                  type: dealResponse.deal_type,
                })),
                amountPrice: 0,
                amountWord: "",
                comments: dealResponse.comments ?? "",
              },
              date: dealResponse.created_at,
              seller: {
                companyName: dealResponse.seller_company.company_name,
                sellerName: dealResponse.seller_company.name,
                phone: dealResponse.seller_company.phone,
                slug: dealResponse.seller_company.slug,
                companyId: dealResponse.seller_company.id,
                email: dealResponse.seller_company.email,
                inn: dealResponse.seller_company.inn,
              },
              buyer: {
                companyName: dealResponse.buyer_company.company_name,
                buyerName: dealResponse.buyer_company.name,
                phone: dealResponse.buyer_company.phone,
                slug: dealResponse.buyer_company.slug,
                companyId: dealResponse.buyer_company.id,
                email: dealResponse.buyer_company.email,
                inn: dealResponse.buyer_company.inn,
              },
              status: dealResponse.status,
              billNumber: dealResponse.bill_number || "",
              billDate: dealResponse.bill_date || "",
              supplyContractNumber: dealResponse.supply_contracts_number || "",
              supplyContractDate: dealResponse.supply_contracts_date || "",
              contractNumber: dealResponse.contract_number || "",
              contractDate: dealResponse.contract_date || "",
              closingDocuments: dealResponse.closing_documents || [],
              othersDocuments: dealResponse.others_documents || [],
            });
          }
        }
      };

      //заполнение списка сделок
      for (const dealId of dealsIds) {
        await fillDeals(dealId);
      }
    },

    async createNewDealVersion(dealId: number) {
      const { createNewDealVersion } = usePurchasesApi();
      const body = this.createBodyForUpdate(dealId);
      await createNewDealVersion(dealId, body ?? {});
    },

    addNewGoodsDeal(newDeal: GoodsDeal) {
      if (!newDeal) return;
      const exists = this.sales.goodsDeals?.some(
        (d) => d.dealId === newDeal.dealId,
      );
      if (!exists) {
        this.sales.goodsDeals?.push(newDeal);
      }
    },

    addNewServicesDeal(newDeal: ServicesDeal) {
      if (!newDeal) return;
      const exists = this.sales.servicesDeals?.some(
        (d) => d.dealId === newDeal.dealId,
      );
      if (!exists) {
        this.sales.servicesDeals?.push(newDeal);
      }
    },

    amountInGoodsList() {
      this.sales.goodsDeals?.map((deal) => {
        deal.goods.goodsList?.map((good) => {
          good.amount = good.price * good.quantity;
        });
      });
    },

    amountInServicesList() {
      this.sales.servicesDeals?.map((deal) => {
        deal.services.servicesList?.map((good) => {
          good.amount = good.price * good.quantity;
        });
      });
    },

    amountPriceInGoods() {
      this.sales.goodsDeals?.map((deal) => {
        deal.goods.amountPrice = Number(
          deal.goods.goodsList?.reduce(
            (acc: number, good: Product) => good.amount + acc,
            0,
          ),
        );
      });
    },

    amountPriceInServices() {
      this.sales.servicesDeals?.map((deal) => {
        deal.services.amountPrice = Number(
          deal.services.servicesList?.reduce(
            (acc: number, good: Product) => good.amount + acc,
            0,
          ),
        );
      });
    },

    amountWordGoods() {
      this.sales.goodsDeals?.map((deal) => {
        deal.goods.amountWord = numberToWordsRu(deal.goods.amountPrice, {
          showNumberParts: {
            fractional: false,
          },
          showCurrency: {
            integer: false,
          },
        });
      });
    },

    amountWordServices() {
      this.sales.servicesDeals?.map((deal) => {
        deal.services.amountWord = numberToWordsRu(deal.services.amountPrice, {
          showNumberParts: {
            fractional: false,
          },
          showCurrency: {
            integer: false,
          },
        });
      });
    },

    addNewGood(dealId: number, newGood: Product) {
      const goodsList = this.findGoodsDeal(dealId)?.goods.goodsList;
      if (goodsList) {
        goodsList.push(newGood);
      }
    },

    addNewService(dealId: number, newService: Product) {
      const servicesList = this.findServicesDeal(dealId)?.services.servicesList;
      if (servicesList) {
        servicesList.push(newService);
      }
    },

    editSellerGoodsDeal(dealId: number, newSellerGoodsDeal: EditPersonDeal) {
      const sellerGoodsDeal = this.findGoodsDeal(dealId)?.seller;
      if (sellerGoodsDeal) {
        Object.assign(sellerGoodsDeal, newSellerGoodsDeal);
      }
    },

    editSellerServicesDeal(
      dealId: number,
      newSellerServicesDeal: EditPersonDeal,
    ) {
      const sellerServicesDeal = this.findServicesDeal(dealId)?.seller;
      if (sellerServicesDeal) {
        Object.assign(sellerServicesDeal, newSellerServicesDeal);
      }
    },

    editBuyerGoodsDeal(dealId: number, newSellerGoodsDeal: EditPersonDeal) {
      const buyerGoodsDeal = this.findGoodsDeal(dealId)?.buyer;
      if (buyerGoodsDeal) {
        Object.assign(buyerGoodsDeal, newSellerGoodsDeal);
      }
    },

    editBuyerServicesDeal(
      dealId: number,
      newSellerServicesDeal: EditPersonDeal,
    ) {
      const buyerServicesDeal = this.findServicesDeal(dealId)?.buyer;
      if (buyerServicesDeal) {
        Object.assign(buyerServicesDeal, newSellerServicesDeal);
      }
    },

    editGood(dealId: number, newGoodsList: Product[]) {
      const goodsDeal = this.findGoodsDeal(dealId);
      if (goodsDeal) {
        goodsDeal.goods.goodsList = [...newGoodsList];
      }
    },

    editService(dealId: number, newServiceList: Product[]) {
      const serviceDeal = this.findServicesDeal(dealId);
      if (serviceDeal) {
        serviceDeal.services.servicesList = [...newServiceList];
      }
    },

    editGoodsComments(dealId: number, comments: string) {
      const goods = this.findGoodsDeal(dealId)?.goods;
      if (goods) {
        goods.comments = comments;
      }
    },

    editServicesComments(dealId: number, comments: string) {
      const goods = this.findServicesDeal(dealId)?.services;
      if (goods) {
        goods.comments = comments;
      }
    },

    removeGoodsDeal(dealId: number) {
      if (dealId) {
        const goodsDeal = this.findGoodsDeal(dealId);
        const goodsDeals = this.sales.goodsDeals;
        const { deleteDealById } = usePurchasesApi();

        if (goodsDeal) {
          const index = goodsDeals?.findIndex((goods: GoodsDeal) => {
            return goods.dealId === goodsDeal.dealId;
          });

          if (index !== -1 && typeof index !== "undefined") {
            goodsDeals?.splice(index, 1);
            deleteDealById(dealId);
          }
        }
      }
    },

    removeServicesDeal(dealId: number) {
      if (dealId) {
        const servicesDeal = this.findServicesDeal(dealId);
        const servicesDeals = this.sales.servicesDeals;
        const { deleteDealById } = usePurchasesApi();

        if (servicesDeal) {
          const index = servicesDeals?.findIndex((service: ServicesDeal) => {
            return service.dealId === servicesDeal.dealId;
          });

          if (index !== -1 && typeof index !== "undefined") {
            servicesDeals?.splice(index, 1);
            deleteDealById(dealId);
          }
        }
      }
    },

    async fullUpdateGoodsDeal(
      dealId: number,
      seller: EditPersonDeal,
      buyer: EditPersonDeal,
      newGoodsList: Product[],
      comments?: string,
    ) {
      this.amountInGoodsList();
      this.amountPriceInGoods();
      this.amountWordGoods();
      this.editSellerGoodsDeal(dealId, seller);
      this.editBuyerGoodsDeal(dealId, buyer);
      this.editGood(dealId, newGoodsList);
      if (comments) {
        this.editGoodsComments(dealId, comments);
      }
      const { updateDealById } = usePurchasesApi();
      const body = this.createBodyForUpdate(dealId);
      if (body) {
        await updateDealById(dealId, body);
      }
    },

    async fullUpdateServicesDeal(
      dealId: number,
      seller: EditPersonDeal,
      buyer: EditPersonDeal,
      newServiceList: Product[],
      comments?: string,
    ) {
      this.amountInServicesList();
      this.amountPriceInServices();
      this.amountWordServices();
      this.editSellerServicesDeal(dealId, seller);
      this.editBuyerServicesDeal(dealId, buyer);
      this.editService(dealId, newServiceList);
      if (comments) {
        this.editServicesComments(dealId, comments);
      }
      const { updateDealById } = usePurchasesApi();
      const body = this.createBodyForUpdate(dealId);
      if (body) {
        await updateDealById(dealId, body);
      }
    },
  },
});
