import { defineStore } from "pinia";
import type {
  GoodsDeal,
  ServicesDeal,
  EditPersonDeal,
  Product,
} from "~/types/dealState";
import type {
  BuyerDealResponse,
  DealUpdate,
  OrderItemUpdate,
} from "~/types/dealResponse";
import { convert as numberToWordsRu } from "number-to-words-ru";
import { usePurchasesApi } from "~/api/purchases";

interface Purchases {
  purchases: {
    goodsDeals: GoodsDeal[];
    servicesDeals: ServicesDeal[];
  };
}

export const usePurchasesStore = defineStore("purchases", {
  state: (): Purchases => ({
    purchases: {
      goodsDeals: [],
      servicesDeals: [],
    },
  }),

  getters: {
    findGoodsDealByDealNumber: (state) => {
      return (dealNumber: string) =>
        state.purchases.goodsDeals?.find(
          (deal) => dealNumber === deal.buyerOrderNumber,
        );
    },

    findServicesDealByDealNumber: (state) => {
      return (dealNumber: string) =>
        state.purchases.servicesDeals?.find(
          (deal) => dealNumber === deal.buyerOrderNumber,
        );
    },

    findGoodsDeal: (state) => {
      return (dealId: number) =>
        state.purchases.goodsDeals?.find((deal) => dealId === deal.dealId);
    },

    findServicesDeal: (state) => {
      return (dealId: number) =>
        state.purchases.servicesDeals?.find((deal) => dealId === deal.dealId);
    },

    lastGoodsDeal: (state): GoodsDeal | undefined => {
      if (state.purchases.goodsDeals?.[0]) {
        const goodsDeals = state.purchases.goodsDeals;
        let maxDealId = 0;
        goodsDeals?.forEach((deal) => {
          if (deal.dealId > maxDealId) {
            maxDealId = deal.dealId;
          }
        });

        const lastDeal = state.purchases.goodsDeals?.find(
          (deal) => deal.dealId === maxDealId,
        );

        return lastDeal;
      }
    },

    lastServicesDeal: (state): ServicesDeal | undefined => {
      if (state.purchases.servicesDeals?.[0]) {
        const servicesDeals = state.purchases.servicesDeals;
        let maxDealId = 0;
        servicesDeals?.forEach((deal) => {
          if (deal.dealId > maxDealId) {
            maxDealId = deal.dealId;
          }
        });

        const lastDeal = state.purchases.servicesDeals?.find(
          (deal) => deal.dealId === maxDealId,
        );

        return lastDeal;
      }
    },

    createBodyForUpdate:
      (state) =>
      (orderId: number): DealUpdate | null => {
        const deal: GoodsDeal | ServicesDeal | undefined =
          state.purchases.goodsDeals?.find((d) => d.dealId === orderId) ??
          state.purchases.servicesDeals?.find((d) => d.dealId === orderId);

        if (!deal) return null;

        const items = "goods" in deal ? deal.goods : deal.services;
        const products = "goodsList" in items ? items.goodsList : items.servicesList;

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
      this.purchases.goodsDeals = [];
      this.purchases.servicesDeals = [];
    },
    //получение и заполнение списка сделок
    async getDeals() {
      await this.clearStore();

      const { getDealById, getBuyerDeals } = usePurchasesApi();
      const buyerDeals = await getBuyerDeals();
      const dealsIds: number[] = [
        ...new Set(buyerDeals?.map((deal: BuyerDealResponse) => deal.id) || []),
      ];

      //функция для преобразования и данных и заполнения списка сделок
      const fillDeals = async (dealId: number) => {
        const dealResponse = await getDealById(dealId);
        if (dealResponse) {
          if (dealResponse.deal_type === "Товары") {
            this.addNewGoodsDeal({
              dealId: dealResponse.id,
              buyerOrderNumber: dealResponse.buyer_order_number,
              sellerOrderNumber: dealResponse.seller_order_number,
              date: dealResponse.created_at,
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
              seller: {
                sellerName: dealResponse.seller_company.name,
                companyName: dealResponse.seller_company.company_name,
                phone: dealResponse.seller_company.phone,
                slug: dealResponse.seller_company.slug,
                companyId: dealResponse.seller_company.id,
                email: dealResponse.seller_company.email,
                inn: dealResponse.seller_company.inn,
                legalAddress: dealResponse.seller_company.legal_address,
              },
              buyer: {
                buyerName: dealResponse.buyer_company.name,
                companyName: dealResponse.buyer_company.company_name,
                phone: dealResponse.buyer_company.phone,
                slug: dealResponse.buyer_company.slug,
                companyId: dealResponse.buyer_company.id,
                email: dealResponse.buyer_company.email,
                inn: dealResponse.buyer_company.inn,
                legalAddress: dealResponse.buyer_company.legal_address,
              },
              status: dealResponse.status,
              billNumber: dealResponse.bill_number || "",
              billDate: dealResponse.bill_date || "",
              contractNumber: dealResponse.contract_number || "",
              contractDate: dealResponse.contract_date || "",
              supplyContractNumber: dealResponse.supply_contracts_number || "",
              supplyContractDate: dealResponse.supply_contracts_date || "",
              closingDocuments: dealResponse.closing_documents || [],
              othersDocuments: dealResponse.others_documents || [],
            });
          } else if (dealResponse.deal_type === "Услуги") {
            this.addNewServicesDeal({
              dealId: dealResponse.id,
              buyerOrderNumber: dealResponse.buyer_order_number,
              sellerOrderNumber: dealResponse.seller_order_number,
              date: dealResponse.created_at,
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
              seller: {
                sellerName: dealResponse.seller_company.name,
                companyName: dealResponse.seller_company.company_name,
                phone: dealResponse.seller_company.phone,
                slug: dealResponse.seller_company.slug,
                companyId: dealResponse.seller_company.id,
                email: dealResponse.seller_company.email,
                inn: dealResponse.seller_company.inn,
                legalAddress: dealResponse.seller_company.legal_address,
              },
              buyer: {
                buyerName: dealResponse.buyer_company.name,
                companyName: dealResponse.buyer_company.company_name,
                phone: dealResponse.buyer_company.phone,
                slug: dealResponse.buyer_company.slug,
                companyId: dealResponse.buyer_company.id,
                email: dealResponse.buyer_company.email,
                inn: dealResponse.buyer_company.inn,
                legalAddress: dealResponse.buyer_company.legal_address,
              },
              status: dealResponse.status,
              billNumber: dealResponse.bill_number || "",
              billDate: dealResponse.bill_date || "",
              contractNumber: dealResponse.contract_number || "",
              contractDate: dealResponse.contract_date || "",
              supplyContractNumber: dealResponse.supply_contracts_number || "",
              supplyContractDate: dealResponse.supply_contracts_date || "",
              closingDocuments: dealResponse.closing_documents || [],
              othersDocuments: dealResponse.others_documents || [],
            });
          }
        }
      };

      //заполнение списка сделок (последовательно, чтобы избежать дублирования)
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
      const exists = this.purchases.goodsDeals?.some((d) => d.dealId === newDeal.dealId);
      if (!exists) {
        this.purchases.goodsDeals?.push(newDeal);
      }
    },

    addNewServicesDeal(newDeal: ServicesDeal) {
      if (!newDeal) return;
      const exists = this.purchases.servicesDeals?.some((d) => d.dealId === newDeal.dealId);
      if (!exists) {
        this.purchases.servicesDeals?.push(newDeal);
      }
    },

    amountInGoodsList() {
      this.purchases.goodsDeals?.map((deal) => {
        deal.goods.goodsList?.map((good) => {
          good.amount = good.price * good.quantity;
        });
      });
    },

    amountInServicesList() {
      this.purchases.servicesDeals?.map((deal) => {
        deal.services.servicesList?.map((good) => {
          good.amount = good.price * good.quantity;
        });
      });
    },

    amountPriceInGoods() {
      this.purchases.goodsDeals?.map((deal) => {
        deal.goods.amountPrice = Number(
          deal.goods.goodsList?.reduce(
            (acc: number, good: Product) => good.amount + acc,
            0,
          ),
        );
      });
    },

    amountPriceInServices() {
      this.purchases.servicesDeals?.map((deal) => {
        deal.services.amountPrice = Number(
          deal.services.servicesList?.reduce(
            (acc: number, good: Product) => good.amount + acc,
            0,
          ),
        );
      });
    },

    amountWordGoods() {
      this.purchases.goodsDeals?.map((deal) => {
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
      this.purchases.servicesDeals?.map((deal) => {
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
        const goodsDeals = this.purchases.goodsDeals;
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
        const servicesDeals = this.purchases.servicesDeals;
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
      if (comments !== undefined) {
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
      if (comments !== undefined) {
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
