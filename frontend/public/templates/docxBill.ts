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

export const generateDocxBill = async(data: any) => {
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

    sections: [{
        properties: {
            page: {
                margin: {
                    top: 720,
                    bottom: 720,
                    left: 720,
                    right: 720,
                }
            }
        },
        children: [
            // ФИО ИП
            new Paragraph({
                children: [
                    new TextRun({
                        text: "Индивидуальный предприниматель ",
                        bold: true
                    }),
                    new TextRun("ФИОИП")
                ]
            }),
            
            // Адрес для документов
            new Paragraph("АдресДляДокументов"),
            
            // Контактные данные
            new Paragraph("КонтактныеДанные"),
            
            // Пустая строка
            new Paragraph(""),
            
            // Таблица с банковскими реквизитами
            new Table({
                width: {
                    size: 100,
                    type: WidthType.PERCENTAGE,
                },
                borders: {
                    top: { style: BorderStyle.SINGLE, size: 1 },
                    bottom: { style: BorderStyle.SINGLE, size: 1 },
                    left: { style: BorderStyle.SINGLE, size: 1 },
                    right: { style: BorderStyle.SINGLE, size: 1 },
                    // insideHorizontal: { style: BorderStyle.SINGLE, size: 1 },
                    // insideVertical: { style: BorderStyle.SINGLE, size: 1 },
                },
                rows: [
                    // Первая строка таблицы
                    new TableRow({
                        children: [
                            new TableCell({
                                children: [new Paragraph("НаименованиеБанкаИГородБанка")],
                                columnSpan: 4,
                                borders: {
                                    bottom: {style: BorderStyle.NONE, size: 0, color: "FFFFFF"}
                                }
                            }),
                            new TableCell({
                                children: [new Paragraph({
                                    children: [new TextRun("БИК")],
                                    alignment: AlignmentType.CENTER,
                                })],
                            }),
                            new TableCell({
                                children: [new Paragraph("БИК")],
                                borders: {
                                    bottom: {style: BorderStyle.NONE, size: 0, color: "FFFFFF"}
                                }
                            }),
                        ],
                    }),
                    // Вторая строка таблицы
                    new TableRow({
                        children: [
                            new TableCell({
                                children: [new Paragraph("")],
                                columnSpan: 4,
                                borders: {
                                    bottom: {style: BorderStyle.NONE, size: 0, color: "FFFFFF"}
                                }
                            }),
                            new TableCell({
                                children: [new Paragraph({
                                    children: [new TextRun("Сч.")],
                                    alignment: AlignmentType.CENTER,
                                })],
                                borders: {
                                    bottom: {style: BorderStyle.NONE, size: 0, color: "FFFFFF"}
                                }
                            }),
                            new TableCell({
                                children: [new Paragraph("КоррСчет")],
                                borders: {
                                    bottom: {style: BorderStyle.NONE, size: 0, color: "FFFFFF"}
                                }
                            }),
                        ],
                    }),
                    // Третья строка таблицы
                    new TableRow({
                        children: [
                            new TableCell({
                                children: [new Paragraph("Банк получателя")],
                                columnSpan: 4,
                            }),
                            new TableCell({
                                children: [new Paragraph("")],
                            }),
                            new TableCell({
                                children: [new Paragraph("")],
                            }),
                        ],
                    }),
                    // Четвертая строка таблицы
                    new TableRow({
                        children: [
                            new TableCell({
                                children: [new Paragraph({
                                    children: [new TextRun("ИНН")],
                                    alignment: AlignmentType.CENTER,
                                })],
                            }),
                            new TableCell({
                                children: [new Paragraph("ИНН")],
                            }),
                            new TableCell({
                                children: [new Paragraph({
                                    children: [new TextRun("КПП")],
                                    alignment: AlignmentType.CENTER,
                                })],
                            }),
                            new TableCell({
                                children: [new Paragraph("КПП")],
                            }),
                            new TableCell({
                                children: [new Paragraph({
                                    children: [new TextRun("Сч. №")],
                                    alignment: AlignmentType.CENTER,
                                })],
                                borders: {
                                    bottom: {style: BorderStyle.NONE, size: 0, color: "FFFFFF"}
                                }
                            }),
                            new TableCell({
                                children: [new Paragraph("РасчетныйСчет")],
                                borders: {
                                    bottom: {style: BorderStyle.NONE, size: 0, color: "FFFFFF"}
                                }
                            }),
                        ],
                    }),
                    // Пятая строка таблицы
                    new TableRow({
                        children: [
                            new TableCell({
                                children: [new Paragraph("Индивидуальный предприниматель ФИОИП")],
                                columnSpan: 4,
                                borders: {
                                    bottom: {style: BorderStyle.NONE, size: 0, color: "FFFFFF"}
                                }
                            }),
                            new TableCell({
                                children: [new Paragraph("")],
                                borders: {
                                    bottom: {style: BorderStyle.NONE, size: 0, color: "FFFFFF"}
                                }
                            }),
                            new TableCell({
                                children: [new Paragraph("")],
                                borders: {
                                    bottom: {style: BorderStyle.NONE, size: 0, color: "FFFFFF"}
                                }
                            }),
                        ],
                    }),
                    // Шестая строка таблицы
                    new TableRow({
                        children: [
                            new TableCell({
                                children: [new Paragraph("Получатель")],
                                columnSpan: 4,
                            }),
                            new TableCell({
                                children: [new Paragraph("")],
                            }),
                            new TableCell({
                                children: [new Paragraph("")],
                            }),
                        ],
                    }),
                ],
            }),
            
            // Пустая строка
            new Paragraph(""),
            
            // Заголовок счета
            new Paragraph({
                children: [
                    new TextRun({
                        text: `Счёт № {номер документа} от {датаДокумента}`,
                        bold: true,
                        size: 28,
                    }),
                    // new TextRun("НомерДокумента"),
                    // new TextRun({
                    //     text: " от ",
                    //     bold: true,
                    //     size: 28,
                    // }),
                    // new TextRun("ДатаДокумента"),
                ],
                alignment: AlignmentType.CENTER,
            }),
            
            // Пустая строка
            new Paragraph(""),
            
            // Таблица с поставщиком и покупателем
            new Table({
                width: {
                    size: 100,
                    type: WidthType.PERCENTAGE,
                },
                borders: {
                    top: { style: BorderStyle.NONE },
                    bottom: { style: BorderStyle.NONE },
                    left: { style: BorderStyle.NONE },
                    right: { style: BorderStyle.NONE },
                    insideHorizontal: { style: BorderStyle.NONE },
                    insideVertical: { style: BorderStyle.NONE },
                },
                rows: [
                    new TableRow({
                        children: [
                            new TableCell({
                                children: [new Paragraph({
                                    children: [new TextRun("Поставщик:")],
                                    alignment: AlignmentType.LEFT,
                                })],
                                width: {
                                    size: 20,
                                    type: WidthType.PERCENTAGE,
                                },
                            }),
                            new TableCell({
                                children: [new Paragraph("ФИОИП")],
                                width: {
                                    size: 80,
                                    type: WidthType.PERCENTAGE,
                                },
                            }),
                        ],
                    }),
                    new TableRow({
                        children: [
                            new TableCell({
                                children: [new Paragraph({
                                    children: [new TextRun("Покупатель:")],
                                    alignment: AlignmentType.LEFT,
                                })],
                            }),
                            new TableCell({
                                children: [new Paragraph("НазваниеКонтр, ИННКонтр, КППКонтр")],
                            }),
                        ],
                    }),
                ],
            }),
            
            // Пустая строка
            new Paragraph(""),
            
            // Фактурная часть
            new Paragraph("ФактурнаяЧасть"),
            
            // Пустая строка
            new Paragraph(""),
            
            // Всего к оплате
            new Paragraph({
                children: [
                    new TextRun({
                        text: "Всего к оплате: ",
                        bold: true
                    }),
                    new TextRun({
                        text:"СуммаДокументаПрописью",
                        underline: {type: UnderlineType.SINGLE},
                    }),
                ],
            }),

            new Paragraph(""),
            
            // Комментарий
            new Paragraph("Комментарий"),
            
            // Пустая строка
            new Paragraph(""),
            
            // Таблица с подписью
            new Table({
                width: {
                    size: 100,
                    type: WidthType.PERCENTAGE,
                },
                borders: {
                    top: { style: BorderStyle.NONE },
                    bottom: { style: BorderStyle.NONE },
                    left: { style: BorderStyle.NONE },
                    right: { style: BorderStyle.NONE },
                    insideHorizontal: { style: BorderStyle.NONE },
                    insideVertical: { style: BorderStyle.NONE },
                },
                rows: [
                    new TableRow({
                        children: [
                            new TableCell({
                                children: [new Paragraph({
                                    children: [new TextRun("Поставщик")],
                                    alignment: AlignmentType.CENTER,
                                })],
                                width: {
                                    size: 10,
                                    type: WidthType.PERCENTAGE,
                                },
                            }),
                            new TableCell({
                                children: [new Paragraph({
                                    children: [new TextRun("Индивидуальный предприниматель")],
                                    alignment: AlignmentType.CENTER,
                                })],
                                width: {
                                    size: 35,
                                    type: WidthType.PERCENTAGE,
                                },
                            }),
                            new TableCell({
                                children: [new Paragraph({
                                    children: [
                                        new TextRun({
                                            text: `                                    `,
                                            underline: {type: UnderlineType.SINGLE},
                                        }),
                                    ],
                                })],
                                width: {
                                    size: 10,
                                    type: WidthType.PERCENTAGE,
                                },
                            }),
                            new TableCell({
                                children: [new Paragraph({
                                    children: [new TextRun({
                                        text:"ФИОДляПодписи",
                                        underline: {type: UnderlineType.SINGLE},
                                        })],
                                    alignment: AlignmentType.CENTER,
                                    })],
                                width: {
                                    size: 40,
                                    type: WidthType.PERCENTAGE,
                                },
                            }),
                        ],
                    }),
                    new TableRow({
                        children: [
                            new TableCell({
                                children: [new Paragraph("")],
                            }),
                            new TableCell({
                                children: [new Paragraph({
                                    children: [new TextRun("должность")],
                                    alignment: AlignmentType.CENTER,
                                })],
                            }),
                            new TableCell({
                                children: [new Paragraph({
                                    children: [new TextRun("подпись")],
                                    alignment: AlignmentType.CENTER,
                                })],
                            }),
                            new TableCell({
                                children: [new Paragraph({
                                    children: [new TextRun("расшифровка подписи")],
                                    alignment: AlignmentType.CENTER,
                                })],
                            }),
                        ],
                    }),
                ],
            }),
        ],
    }],
});

		return await Packer.toBlob(doc)
	}