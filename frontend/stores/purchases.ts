import { defineStore } from "pinia";
import type {
  GoodsDeal,
  ServicesDeal,
  EditPersonDeal,
  Services,
  Product,
} from "~/types/dealState";
import { convert as numberToWordsRu } from "number-to-words-ru";

interface Purchases {
  purchases: {
    goodsDeals: GoodsDeal[] | null;
    servicesDeals: ServicesDeal[] | null;
  };
}

export const usePurchasesStore = defineStore("purchases", {
  state: (): Purchases => ({
    purchases: {
      goodsDeals: [
        {
          dealNumber: 666,
          goods: {
            goodsList: [
              {
                name: "Что-то уругое",
                article: 696969,
                quantity: 1,
                units: "штучка",
                price: 69_000,
                amount: 0,
                type: "товар",
              },
            ],
            amountPrice: 0,
            amountWord: "",
            comments: "",
          },
          date: `${new Date().getDate()}.${new Date().getMonth()}.${new Date().getFullYear()}`,
          saller: {
            inn: 7777777,
            name: "Yasha Lava",
            companyName: "DeppAndHard",
            legalAddress: "somewhere",
            mobileNumber: "+23423423433",
          },
          buyer: {
            inn: 3423423,
            name: "Sergey",
            companyName: "Home secrets",
            legalAddress: "Minsk, Svisloch river",
            mobileNumber: "+3754445457474",
          },
          state: "в процессе",
          bill: "просмотр",
          supplyContract: "просмотр",
          accompanyingDocuments: "просмотр",
          invoice: "просмотр",
          othersDocuments: "просмотр",
        },
      ],

      servicesDeals: [],
    },
  }),

  getters: {
    findDeal: (state) => {
      return (dealNumber: number) =>
        state.purchases.goodsDeals?.find(
          (deal) => dealNumber === deal.dealNumber
        );
    },
  },

  actions: {
    //функция для получения закупок с сервера
    async getPurchases() {},

    amountInGoodsList() {
      this.purchases.goodsDeals?.map((deal) => {
        deal.goods.goodsList?.map((good) => {
          good.amount = good.price * good.quantity;
        });
      });
    },

    amountPriceInGoods() {
      this.purchases.goodsDeals?.map((deal) => {
        deal.goods.amountPrice = Number(
          deal.goods.goodsList?.reduce(
            (acc: number, good: Product) => good.amount + acc,
            0
          )
        );
      });
    },

    amountWord() {
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

    addNewGood(dealNumber: number, newGood: Product) {
      const goodsList = this.findDeal(dealNumber)?.goods.goodsList;
      if (goodsList) {
        goodsList.push(newGood);
      }
    },

    editSallerGoodsDeal(
      dealNumber: number,
      newSallerGoodsDeal: EditPersonDeal
    ) {
      const sallerGoodsDeal = this.findDeal(dealNumber)?.saller;
      if (sallerGoodsDeal) {
        Object.assign(sallerGoodsDeal, newSallerGoodsDeal);
      }
    },

    editBuyerGoodsDeal(dealNumber: number, newSallerGoodsDeal: EditPersonDeal) {
      const buyerGoodsDeal = this.findDeal(dealNumber)?.buyer;
      if (buyerGoodsDeal) {
        Object.assign(buyerGoodsDeal, newSallerGoodsDeal);
      }
    },

    editGood(dealNumber: number, newGoodsList: Product[]) {
      const goodsList = this.findDeal(dealNumber)?.goods.goodsList;
      if (goodsList) {
        Object.assign(goodsList, newGoodsList);
      }
    },

    editComments(dealNumber: number, comments: string) {
      const goods = this.findDeal(dealNumber)?.goods;
      if (goods) {
        goods.comments = comments;
      }
    },
  },
});
