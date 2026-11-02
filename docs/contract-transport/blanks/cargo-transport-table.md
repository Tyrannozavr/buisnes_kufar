# Общий блок: таблица груза и транспорта

Стоит на бланках **Заявка** и **Договор-заявка**. В макетах ТЗ залита **серым** как `ТАБЛИЦА`.

На А4 **не набирается**. Заполняется из заказа на перевозку. Править — кнопка **«Редактировать данные перевозки»** (диалог груза / транспорта в ЛК «Перевозки»).

Образец вёрстки: `dev/+ТЗ_Договор на перевозку грузов 22.08.2026/Документы/+Заявка к Договору перевозки грузов.docx`.

| Подпись на бланке | Источник | Поле в коде сейчас |
|-------------------|----------|---------------------|
| Дата загрузки | груз | `cargo_data.loading_date` |
| Дата разгрузки | груз | `cargo_data.unloading_date` |
| Время загрузки | груз | `cargo_data.loading_time` |
| Время выгрузки | груз | `cargo_data.unloading_time` |
| Адрес загрузки | груз | `cargo_data.loading_address` |
| Адрес выгрузки | груз | `cargo_data.unloading_address` |
| Маршрут | груз | `cargo_data.route` |
| Контактное лицо на загрузке | груз | `cargo_data.contact_loading` |
| Контактное лицо на разгрузке | груз | `cargo_data.contact_unloading` |
| Наименование груза | груз | `cargo_data.cargo_name` |
| Условия перевозки | груз | `cargo_data.transport_conditions` |
| Тоннаж, тн | груз | `cargo_data.gross_weight` (в ЛК сейчас кг — при выводе в тонны) |
| Количество мест | груз | `cargo_data.places_count` |
| Объём | груз | `cargo_data.volume` |
| Ставка за перевозку, условия оплаты | груз | `cargo_data.rate` + `cargo_data.payment_terms` |
| Водитель (ФИО) | транспорт | `transport_snapshot.driver.full_name` |
| Паспорт РФ | транспорт | **нет в ЛК водителя** (есть `license_number`) |
| Контактный телефон | транспорт | `transport_snapshot.driver.phone` |
| Марка тягача | транспорт | `transport_snapshot.vehicle.name` |
| Гос. номер тягача | транспорт | `transport_snapshot.vehicle.plate_number` |
| Номер п/п | транспорт | `transport_snapshot.vehicle.trailer_plate_number` |
