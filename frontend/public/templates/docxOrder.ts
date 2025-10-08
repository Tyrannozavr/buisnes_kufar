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

export const generateDocxOrder = async (orderData: any) => {
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
                `${orderData.innSaller}  ${orderData.companyNameSaller}
${orderData.urAdressSaller}  
${orderData.mobileNumberSaller}
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
                `${orderData.companyNameBuyer}
${orderData.urAdressBuyer},
${orderData.mobileNumberBuyer}
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
        text: `Заказ № ${orderData.orderNumber} от ${orderData.orderDate}`,
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
      ...orderData.products.map((product: any, index: number) => {
        return new TableRow({
          children: [
            `${++index}`,
            `${product.name}`,
            `${product.article}`,
            `${product.quantity}`,
            `${product.units}`,
            `${product.price}`,
            `${product.productAmount}`,
          ].map((text) => new TableCell({ children: [new Paragraph(text)] })),
        });
      }),
    ],
  });

  // Итоговая информация
  const summary = [
    new Paragraph({
      text: `Итого: ${orderData.amount}`,
      spacing: {
        before: 200,
      },
      indent: {
        start: 6000,
        hanging: 0,
      },
    }),
    new Paragraph({
      text: `В том числе НДС: ${orderData.amount}`,
      indent: {
        start: 6000,
        hanging: 1180,
      },
    }),
    new Paragraph({
      text: `Всего наименований ${orderData.products.length}, на сумму ${orderData.amount} руб.`,
      spacing: {
        before: 500,
      },
    }),
    new Paragraph({
      text: `${orderData.amountWord}`,
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
              children: [new Paragraph(`${orderData.companyNameBuyer}`)],
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
              children: [new Paragraph(`${orderData.buyerName}`)],
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
              children: [new Paragraph(`${orderData.companyNameSaller}`)],
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
              children: [new Paragraph(`${orderData.sallerName}`)],
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
