import {
  Document,
  Packer,
  Paragraph,
  Table,
  TableRow,
  TableCell,
  TextRun,
  AlignmentType,
  WidthType,
  BorderStyle,
} from "docx";
import type { GoodsDeal, ServicesDeal, Product } from "~/types/dealState";
import { normalizeDate } from "~/utils/normalize";
import { useUserStore } from "~/stores/user";

const userStore = useUserStore()
const myCompanyId = userStore.companyId

export const generateDocxOrder = async (orderDealData: GoodsDeal | ServicesDeal ): Promise<Blob> => {
  // Создание таблицы с данными поставщика и покупателя
  const headerTable = new Table({
    rows: [
      new TableRow({
        children: [
          new TableCell({
            children: [new Paragraph("Поставщик:")],
            borders: {
              top: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
              bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
              left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
              right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
            },
          }),
          new TableCell({
            children: [
              new Paragraph(
                `${orderDealData.seller.inn}  ${orderDealData.seller.companyName}
${orderDealData.seller.legalAddress}  
${orderDealData.seller.phone}
			`
              ),
            ],
            borders: {
              top: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
              bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
              left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
              right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
            },
          }),
        ],
      }),
      new TableRow({
        children: [
          new TableCell({
            children: [new Paragraph("Покупатель:")],
            borders: {
              top: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
              bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
              left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
              right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
            },
          }),
          new TableCell({
            children: [
              new Paragraph(
                `${orderDealData.buyer.companyName}
${orderDealData.buyer.legalAddress},
${orderDealData.buyer.phone}
`
              ),
            ],
            borders: {
              top: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
              bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
              left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
              right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
            },
          }),
        ],
      }),
    ],
  });

  // // Заголовок заказа
  const orderTitle = new Paragraph({
    children: [
      new TextRun({
        text: `Заказ № ${myCompanyId === orderDealData.seller.id ? orderDealData.sellerOrderNumber : orderDealData.buyerOrderNumber} от ${normalizeDate(orderDealData.date)} г.`,
        bold: true,
        size: 28,
      }),
    ],
    alignment: AlignmentType.CENTER,
    spacing: {
      before: 1000,
      after: 200,
    },
  });

	//Отдельная констаннта для данных таблицы
	const rowsData = "goods" in orderDealData 
		? orderDealData.goods.goodsList?.map((good: Product, index: number) => {
					return new TableRow({
						children: [
							`${++index}`,
							`${good.name}`,
							`${good.article}`,
							`${good.quantity}`,
							`${good.units}`,
							`${good.price}`,
							`${good.amount}`,
						].map((text) => new TableCell({ children: [new Paragraph(text)] })),
					});
				}) ?? []
		: orderDealData.services.servicesList?.map((service: Product, index: number) => {
					return new TableRow({
						children: [
							`${++index}`,
							`${service.name}`,
							`${service.article}`,
							`${service.quantity}`,
							`${service.units}`,
							`${service.price}`,
							`${service.amount}`,
						].map((text) => new TableCell({ children: [new Paragraph(text)] })),
					});
				}) ?? []

  // Таблица с товарами
  const productTable = new Table({
    width: {
      size: 100,
      type: WidthType.PERCENTAGE,
    },
    rows: [
      new TableRow({
        children: [
          "№",
          "Наименование продукта",
          "Артикул",
          "Количество",
          "Ед. изм.",
          "Цена",
          "Сумма",
        ].map((text) => new TableCell({ children: [new Paragraph(text)] })),
      }),
			...rowsData
			
    ],
  });

  // Итоговая информация
  const summary = [
    new Paragraph({
      text: `Итого: ${("goods" in orderDealData) ? orderDealData.goods.amountPrice : orderDealData.services.amountPrice} р.`,
      spacing: {
        before: 200,
      },
      indent: {
        start: 6000,
        hanging: 0,
      },
    }),
    new Paragraph({
      text: `В том числе НДС: ${("goods" in orderDealData) ? orderDealData.goods.amountPrice : orderDealData.services.amountPrice} р.`,
      indent: {
        start: 6000,
        hanging: 1180,
      },
    }),
    new Paragraph({
      text: `Всего наименований ${("goods" in orderDealData) ? orderDealData.goods.goodsList.length : orderDealData.services.servicesList.length}, на сумму ${("goods" in orderDealData) ? orderDealData.goods.amountPrice : orderDealData.services.amountPrice} руб.`,
      spacing: {
        before: 500,
      },
    }),
    new Paragraph({
      text: `${ ("goods" in orderDealData) ? orderDealData.goods.amountWord : orderDealData.services.amountWord}`,
      spacing: {
        before: 200,
        after: 0,
        line: 1,
      },
    }),
    new Paragraph({
      spacing: {
        line: 1,
        after: 300,
        before: 0,
      },
      text: `___________________________________________________________________________`,
    }),

    new Table({
			width: {
				size: 100,
				type: WidthType.PERCENTAGE,
			},
      rows: [
        new TableRow({
          children: [
            new TableCell({
							width: {
								size: 15,
								type: WidthType.PERCENTAGE,
							},
              children: [new Paragraph(`Директор `)],
              borders: {
                top: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
              },
            }),
            new TableCell({
              children: [new Paragraph(`${orderDealData.buyer.companyName}`)],
              borders: {
                top: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
              },
            }),
            new TableCell({
              children: [new Paragraph(``)],
              borders: {
                top: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
              },
            }),
            new TableCell({
							width: {
								size: 25,
								type: WidthType.PERCENTAGE,
							},
              children: [new Paragraph(`${orderDealData.buyer.buyerName}`)],
              borders: {
                top: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
              },
            }),
          ],
        }),
        new TableRow({
          children: [
            new TableCell({
							width: {
								size: 15,
								type: WidthType.PERCENTAGE,
							},
              children: [new Paragraph(`Директор `)],
              borders: {
                top: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
              },
            }),
            new TableCell({
              children: [new Paragraph(`${orderDealData.seller.companyName}`)],
              borders: {
                top: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
              },
            }),
						new TableCell({
              children: [new Paragraph(``)],
              borders: {
                top: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
              },
            }),
            new TableCell({
							width: {
								size: 25,
								type: WidthType.PERCENTAGE,
							},
              children: [new Paragraph(`${orderDealData.seller.sellerName}`)],
              borders: {
                top: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
              },
            }),
          ],
        }),
      ],
    }),
  ];

  // Создание документа
  const doc = new Document({
    styles: {
      default: {
        document: {
          run: {
            font: "Times New Roman",
            size: 24,
          },
        },
      },
    },
    sections: [
      {
        children: [headerTable, orderTitle, productTable, ...summary],
      },
    ],
  });

  return await Packer.toBlob(doc);
};
