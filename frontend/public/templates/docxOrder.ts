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
      new TableRow({
        children: [
					`${orderData.products.length}`,
          `${orderData.products[0].productName}`,
          `${orderData.products[0].article}`,
          `${orderData.products[0].quantity}`,
          `${orderData.products[0].units}`,
          `${orderData.products[0].price}`,
          `${orderData.products[0].productAmount}`,
        ].map((text) => new TableCell({ children: [new Paragraph(text)] })),
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
      text: `${orderData.amountLitter}`,
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
    new Paragraph({
      spacing: {
        before: 200,
      },
      children: [
        new TextRun({
          text: `Директор `,
        }),
        new TextRun({
          text: `${orderData.companyNameBuyer}`,
        }),
        new TextRun({
          text: `${orderData.buyerName}`,
        }),
      ],
    }),

    new Paragraph({
      spacing: {
        before: 200,
      },
      children: [
        new TextRun({
          text: `Директор `,
        }),
        new TextRun({
          text: `${orderData.companyNameSaller}`,
        }),
        new TextRun({
          text: `${orderData.sallerName}`,
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
