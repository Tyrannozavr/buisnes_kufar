import { defineStore } from "pinia";
import type {
  GoodsDeal,
  ServicesDeal,
  EditPersonDeal,
  Product,
} from "~/types/dealState";
import { convert as numberToWordsRu } from "number-to-words-ru";
import { usePurchasesApi } from "~/api/purchases";
import type { SellerDealResponse } from "~/types/dealReasponse";

interface Sales {
  sales: {
    goodsDeals: GoodsDeal[]
    servicesDeals: ServicesDeal[] 
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
        const lastDeal = goodsDeals?.[goodsDeals.length - 1];
        return lastDeal;
      }
    },

    lastServicesDeal: (state): ServicesDeal | undefined => {
      if (state.sales.servicesDeals?.[0]) {
        const servicesDeals = state.sales.servicesDeals;
        const lastDeal = servicesDeals?.[servicesDeals.length - 1];
        return lastDeal;
      }
    },
  },

  actions: {
    //получение и заполнение списка сделок
    async getDeals() {
      const { getDealById, getSellerDeals } = usePurchasesApi();
      const sellerDeals = await getSellerDeals();
      const dealsIds: number[] = sellerDeals?.map(
        (deal: SellerDealResponse) => deal.id,
      ) || [];

      //функция для преобразования и данных и заполнения списка сделок
      const fillDeals = async (dealId: number) => {
        const dealResponse = await getDealById(dealId);

        if (dealResponse) {
          if (dealResponse.deal_type === "Товары") {
            this.addNewGoodsDeal({
              dealId: dealResponse.id,
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
                name: dealResponse.seller_company.name,
                phone: dealResponse.seller_company.phone,
                slug: dealResponse.seller_company.slug,
                legalAddress: dealResponse.seller_company.legal_address,
                inn: dealResponse.seller_company.inn,
              },
              buyer: {
                name: dealResponse.buyer_company.name,
                phone: dealResponse.buyer_company.phone,
                slug: dealResponse.buyer_company.slug,
                legalAddress: dealResponse.buyer_company.legal_address,
                inn: dealResponse.buyer_company.inn,
              },
              status: dealResponse.status,
              bill: "",
              supplyContract: dealResponse.contract_number,
              closingDocuments: "",
              othersDocuments: dealResponse.invoice_number || "",
            } as GoodsDeal);
          } else if (dealResponse.deal_type === "Услуги") {
            this.addNewServicesDeal({
              dealId: dealResponse.id,
              sellerOrderNumber: dealResponse.seller_order_number,
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
                name: dealResponse.seller_company.name,
                phone: dealResponse.seller_company.phone,
                slug: dealResponse.seller_company.slug,
                legalAddress: dealResponse.seller_company.legal_address,
                inn: dealResponse.seller_company.inn,
              },
              buyer: {
                name: dealResponse.buyer_company.name,
                phone: dealResponse.buyer_company.phone,
                slug: dealResponse.buyer_company.slug,
                legalAddress: dealResponse.buyer_company.legal_address,
                inn: dealResponse.buyer_company.inn,
              },
              status: dealResponse.status,
              bill: "",
              contract: dealResponse.contract_number,
              closingDocuments: "",
              othersDocuments: dealResponse.invoice_number || "",
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
        this.sales.goodsDeals?.push(newDeal);
      }
    },

    addNewServicesDeal(newDeal: ServicesDeal) {
      if (newDeal) {
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
        const goodsDeals = this.sales.goodsDeals;

        if (goodsDeal) {
          const index = goodsDeals?.findIndex((goods: GoodsDeal) => {
            return goods.dealId === goodsDeal.dealId;
          });

          if (index !== -1 && typeof index !== "undefined") {
            goodsDeals?.splice(index, 1);
          }
        }
      }
    },

    removeServicesDeal(dealId: number) {
      if (dealId) {
        const servicesDeal = this.findServicesDeal(dealId);
        const servicesDeals = this.sales.servicesDeals;

        if (servicesDeal) {
          const index = servicesDeals?.findIndex((service: ServicesDeal) => {
            return service.dealId === servicesDeal.dealId;
          });

          if (index !== -1 && typeof index !== "undefined") {
            servicesDeals?.splice(index, 1);
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
