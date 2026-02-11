import { defineStore } from "pinia";
import type {
  GoodsDeal,
  ServicesDeal,
  EditPersonDeal,
  Product,
} from "~/types/dealState";
import type { BuyerDealResponse } from "~/types/dealReasponse";
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
  },

  actions: {
    async clearStore() {
      this.purchases.goodsDeals = [];
      this.purchases.servicesDeals = [];
    },
    //получение и заполнение списка сделок
    async getDeals() {
      this.clearStore();

      const { getDealById, getBuyerDeals } = usePurchasesApi();
      const buyerDeals = await getBuyerDeals();
      const dealsIds: number[] =
        buyerDeals?.map((deal: BuyerDealResponse) => deal.id) || [];

      //функция для преобразования и данных и заполнения списка сделок
      const fillDeals = async (dealId: number) => {
        const dealResponse = await getDealById(dealId);

        if (dealResponse) {
          if (dealResponse.deal_type === "Товары") {
            this.addNewGoodsDeal({
              dealId: dealResponse.id,
              buyerOrderNumber: dealResponse.buyer_order_number,
              sellerOrderNumber: dealResponse.seller_order_number,
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
                comments: "",
              },
              date: dealResponse.created_at,
              saller: {
                sallerName: dealResponse.seller_company.name,
                companyName: dealResponse.seller_company.company_name,
                phone: dealResponse.seller_company.phone,
                slug: dealResponse.seller_company.slug,
                sallerId: dealResponse.seller_company.id,
                email: dealResponse.seller_company.email,
                inn: dealResponse.seller_company.inn,
                legalAddress: dealResponse.seller_company.legal_address,
              },
              buyer: {
                buyerName: dealResponse.buyer_company.name,
                companyName: dealResponse.buyer_company.company_name,
                phone: dealResponse.buyer_company.phone,
                slug: dealResponse.buyer_company.slug,
                buyerId: dealResponse.buyer_company.id,
                email: dealResponse.buyer_company.email,
                inn: dealResponse.buyer_company.inn,
                legalAddress: dealResponse.buyer_company.legal_address,
              },
              status: dealResponse.status,
              bill: dealResponse.bill_number || "",
              supplyContract:
                dealResponse.supply_contracts_number ||
                dealResponse.contract_number ||
                "",
              closingDocuments: "",
              othersDocuments: "",
            } as GoodsDeal);
          } else if (dealResponse.deal_type === "Услуги") {
            this.addNewServicesDeal({
              dealId: dealResponse.id,
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
                comments: "",
              },
              date: dealResponse.created_at,
              saller: {
                sallerName: dealResponse.seller_company.name,
                companyName: dealResponse.seller_company.company_name,
                phone: dealResponse.seller_company.phone,
                slug: dealResponse.seller_company.slug,
                sallerId: dealResponse.seller_company.id,
                email: dealResponse.seller_company.email,
                inn: dealResponse.seller_company.inn,
              },
              buyer: {
                buyerName: dealResponse.buyer_company.name,
                companyName: dealResponse.buyer_company.company_name,
                phone: dealResponse.buyer_company.phone,
                slug: dealResponse.buyer_company.slug,
                buyerId: dealResponse.buyer_company.id,
                email: dealResponse.buyer_company.email,
                inn: dealResponse.buyer_company.inn,
              },
              status: dealResponse.status,
              bill: dealResponse.bill_number || "",
              contract:
                dealResponse.supply_contracts_number ||
                dealResponse.contract_number ||
                "",
              closingDocuments: "",
              othersDocuments: "",
            } as ServicesDeal);
          }
        }
      };

      //заполнение списка сделок
      for (const dealId of dealsIds) {
        await fillDeals(dealId);
      }
    },

    addNewGoodsDeal(newDeal: GoodsDeal) {
      if (newDeal) {
        this.purchases.goodsDeals?.push(newDeal);
      }
    },

    addNewServicesDeal(newDeal: ServicesDeal) {
      if (newDeal) {
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

    editSallerGoodsDeal(dealId: number, newSallerGoodsDeal: EditPersonDeal) {
      const sallerGoodsDeal = this.findGoodsDeal(dealId)?.saller;
      if (sallerGoodsDeal) {
        Object.assign(sallerGoodsDeal, newSallerGoodsDeal);
      }
    },

    editSallerServicesDeal(
      dealId: number,
      newSallerServicesDeal: EditPersonDeal,
    ) {
      const sallerServicesDeal = this.findServicesDeal(dealId)?.saller;
      if (sallerServicesDeal) {
        Object.assign(sallerServicesDeal, newSallerServicesDeal);
      }
    },

    editBuyerGoodsDeal(dealId: number, newSallerGoodsDeal: EditPersonDeal) {
      const buyerGoodsDeal = this.findGoodsDeal(dealId)?.buyer;
      if (buyerGoodsDeal) {
        Object.assign(buyerGoodsDeal, newSallerGoodsDeal);
      }
    },

    editBuyerServicesDeal(
      dealId: number,
      newSallerServicesDeal: EditPersonDeal,
    ) {
      const buyerServicesDeal = this.findServicesDeal(dealId)?.buyer;
      if (buyerServicesDeal) {
        Object.assign(buyerServicesDeal, newSallerServicesDeal);
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
      saller: EditPersonDeal,
      buyer: EditPersonDeal,
      newGoodsList: Product[],
      comments?: string,
    ) {
      this.amountInGoodsList();
      this.amountPriceInGoods();
      this.amountWordGoods();
      this.editSallerGoodsDeal(dealId, saller);
      this.editBuyerGoodsDeal(dealId, buyer);
      this.editGood(dealId, newGoodsList);
      if (comments) {
        this.editGoodsComments(dealId, comments);
      }
    },

    async fullUpdateServicesDeal(
      dealId: number,
      saller: EditPersonDeal,
      buyer: EditPersonDeal,
      newServiceList: Product[],
      comments?: string,
    ) {
      this.amountInServicesList();
      this.amountPriceInServices();
      this.amountWordServices();
      this.editSallerServicesDeal(dealId, saller);
      this.editBuyerServicesDeal(dealId, buyer);
      this.editService(dealId, newServiceList);
      if (comments) {
        this.editServicesComments(dealId, comments);
      }
    },
  },
});
