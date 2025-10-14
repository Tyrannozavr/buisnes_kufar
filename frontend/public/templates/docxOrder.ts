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
  UnderlineType,
} from "docx";
import type { GoodsDeal, Product } from "~/types/dealState";

export const generateDocxOrder = async (orderDealData: GoodsDeal ) => {
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
                `${orderDealData.saller.inn}  ${orderDealData.saller.companyName}
${orderDealData.saller.legalAddress}  
${orderDealData.saller.mobileNumber}
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
${orderDealData.buyer.mobileNumber}
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
        text: `Заказ № ${orderDealData.dealNumber} от ${orderDealData.date}`,
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
      ...orderDealData.goods.goodsList?.map((good: Product, index: number) => {
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
      }),
    ],
  });

  // Итоговая информация
  const summary = [
    new Paragraph({
      text: `Итого: ${orderDealData.goods.amountPrice}`,
      spacing: {
        before: 200,
      },
      indent: {
        start: 6000,
        hanging: 0,
      },
    }),
    new Paragraph({
      text: `В том числе НДС: ${orderDealData.goods.amountPrice}`,
      indent: {
        start: 6000,
        hanging: 1180,
      },
    }),
    new Paragraph({
      text: `Всего наименований ${orderDealData.goods.goodsList.length}, на сумму ${orderDealData.goods.amountPrice} руб.`,
      spacing: {
        before: 500,
      },
    }),
    new Paragraph({
      text: `${orderDealData.goods.amountWord}`,
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
              children: [new Paragraph(`${orderDealData.buyer.name}`)],
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
              children: [new Paragraph(`${orderDealData.saller.companyName}`)],
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
              children: [new Paragraph(`${orderDealData.saller.name}`)],
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
