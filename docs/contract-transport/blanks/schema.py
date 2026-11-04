"""Каталог полей бланков ТЗ «Договор на перевозку грузов».

Не бизнес-логика Продаж. Только: что на бланке, можно ли править, откуда значение.
Канон для чтения: соседние *.md. Этот файл — тот же набор, чтобы не гадать по docx.

Цвет на бланке (печать ч/б):
  static       — чёрный, не поле
  yellow       — автозаполнение, править на А4 можно
  red          — автозаполнение, на А4 нельзя
  gray_block   — целый блок (таблица / доп. условия)
  template     — текст из редактора шаблонов
  dialog_only  — строгий бланк: только диалог, вёрстка заморожена
  diff         — красный шрифт: отличие от договора поставки, не про edit
"""

from __future__ import annotations

from typing import Literal, TypedDict

OnBlank = Literal["static", "yellow", "red", "gray_block", "template", "dialog_only", "diff"]
FormKind = Literal["flexible", "strict"]


class Field(TypedDict, total=False):
    id: str
    label: str
    on_blank: OnBlank
    source: str
    note: str


class Blank(TypedDict, total=False):
    id: str
    title: str
    family: Literal["A", "B"]
    kind: FormKind
    parent: str | None
    sample: str
    fields: list[Field]


# --- общие куски -----------------------------------------------------------

_PREAMBLE_PARTY = [
    Field(id="{side}.full_name", label="ПОЛНОЕ НАЗВАНИЕ ОРГАНИЗАЦИИ", on_blank="yellow", source="company.lk"),
    Field(id="{side}.role_label", label="роль в кавычках", on_blank="diff", source="static"),
    Field(id="{side}.official.position", label="ДОЛЖНОСТЬ", on_blank="yellow", source="company.officials"),
    Field(id="{side}.official.name", label="ФИО", on_blank="yellow", source="company.officials"),
    Field(id="{side}.foundation.kind", label="ДОКУМЕНТ ОСНОВАНИЯ", on_blank="yellow", source="company.lk"),
    Field(id="{side}.foundation.title", label="НАЗВАНИЕ ДОКУМЕНТА", on_blank="yellow", source="company.lk"),
    Field(id="{side}.ogrn", label="ОГРН", on_blank="yellow", source="company.lk", note="только если сторона ИП"),
]

_REQUISITES = [
    Field(id="{side}.legal_type", label="ТИП ОРГАНИЗАЦИИ", on_blank="yellow", source="company.lk"),
    Field(id="{side}.name", label="НАЗВАНИЕ ОРГАНИЗАЦИИ", on_blank="yellow", source="company.lk"),
    Field(id="{side}.index_address", label="ИНДЕКС, ЮРИДИЧЕСКИЙ АДРЕС", on_blank="yellow", source="company.lk"),
    Field(id="{side}.inn", label="ИНН", on_blank="yellow", source="company.lk"),
    Field(id="{side}.kpp", label="КПП", on_blank="yellow", source="company.lk"),
    Field(id="{side}.account", label="РАСЧЕТНЫЙ СЧЕТ", on_blank="yellow", source="company.lk"),
    Field(id="{side}.bank", label="НАЗВАНИЕ БАНКА", on_blank="yellow", source="company.lk"),
    Field(id="{side}.corr", label="КОРР.СЧЕТ БАНКА", on_blank="yellow", source="company.lk"),
    Field(id="{side}.bik", label="БИК", on_blank="yellow", source="company.lk"),
]

CARGO_TRANSPORT_TABLE = Field(
    id="cargo_transport_table",
    label="таблица груз + ТС",
    on_blank="gray_block",
    source="shipment.cargo + shipment.transport",
    note="править через «Редактировать данные перевозки»; карта полей — cargo-transport-table.md",
)

# Код сейчас: frontend/types/transport.ts CargoData + transport_snapshot
CARGO_TRANSPORT_CELLS: list[Field] = [
    Field(id="loading_date", label="Дата загрузки", source="cargo_data.loading_date"),
    Field(id="unloading_date", label="Дата разгрузки", source="cargo_data.unloading_date"),
    Field(id="loading_time", label="Время загрузки", source="cargo_data.loading_time"),
    Field(id="unloading_time", label="Время выгрузки", source="cargo_data.unloading_time"),
    Field(id="loading_address", label="Адрес загрузки", source="cargo_data.loading_address"),
    Field(id="unloading_address", label="Адрес выгрузки", source="cargo_data.unloading_address"),
    Field(id="route", label="Маршрут", source="cargo_data.route"),
    Field(id="contact_loading", label="Контакт на загрузке", source="cargo_data.contact_loading"),
    Field(id="contact_unloading", label="Контакт на разгрузке", source="cargo_data.contact_unloading"),
    Field(id="cargo_name", label="Наименование груза", source="cargo_data.cargo_name"),
    Field(id="transport_conditions", label="Условия перевозки", source="cargo_data.transport_conditions"),
    Field(id="tonnage", label="Тоннаж, тн", source="cargo_data.gross_weight", note="в ЛК вес в кг"),
    Field(id="places_count", label="Количество мест", source="cargo_data.places_count"),
    Field(id="volume", label="Объём", source="cargo_data.volume"),
    Field(id="rate_payment", label="Ставка, условия оплаты", source="cargo_data.rate + payment_terms"),
    Field(id="driver_name", label="Водитель ФИО", source="transport_snapshot.driver.full_name"),
    Field(id="driver_passport", label="Паспорт РФ", source="нет в ЛК водителя", note="есть license_number"),
    Field(id="driver_phone", label="Телефон", source="transport_snapshot.driver.phone"),
    Field(id="vehicle_name", label="Марка тягача", source="transport_snapshot.vehicle.name"),
    Field(id="vehicle_plate", label="Гос. номер тягача", source="transport_snapshot.vehicle.plate_number"),
    Field(id="trailer_plate", label="Номер п/п", source="transport_snapshot.vehicle.trailer_plate_number"),
]


def _expand(fields: list[Field], side: str) -> list[Field]:
    out: list[Field] = []
    for f in fields:
        item = dict(f)
        item["id"] = f["id"].replace("{side}", side)
        out.append(item)  # type: ignore[arg-type]
    return out


BLANKS: list[Blank] = [
    Blank(
        id="carriage_contract",
        title="Договор перевозки грузов",
        family="A",
        kind="flexible",
        parent=None,
        sample="2_Страница_Договор перевозки.docx",
        fields=[
            Field(id="number", label="№ договора", on_blank="yellow", source="system.number"),
            Field(id="city", label="ГОРОД", on_blank="yellow", source="company.city заказчика"),
            Field(id="date", label="дата", on_blank="yellow", source="system.date"),
            *_expand(_PREAMBLE_PARTY, "customer"),
            *_expand(_PREAMBLE_PARTY, "carrier"),
            Field(id="preamble_formula", label="юрлицо / ИП", on_blank="static", source="company.type"),
            Field(id="body", label="ТЕКСТ ДОГОВОРА", on_blank="template", source="template.body"),
            Field(id="sign.customer", label="подпись Заказчик", on_blank="yellow", source="company.officials"),
            Field(id="sign.carrier", label="подпись Перевозчик", on_blank="yellow", source="company.officials"),
        ],
    ),
    Blank(
        id="carriage_application",
        title="Заявка к договору перевозки",
        family="A",
        kind="flexible",
        parent="carriage_contract",
        sample="Документы/+Заявка к Договору перевозки грузов.docx",
        fields=[
            Field(id="parent.number", label="№ договора-родителя", on_blank="red", source="parent.number"),
            Field(id="parent.date", label="дата договора-родителя", on_blank="red", source="parent.date"),
            Field(id="number", label="№ заявки (1, 2, 3…)", on_blank="red", source="system.number"),
            Field(id="date", label="дата заявки", on_blank="red", source="system.date"),
            Field(id="header.customer", label="строка Заказчик в шапке", on_blank="yellow", source="company.lk"),
            Field(id="header.carrier", label="строка Перевозчик в шапке", on_blank="yellow", source="company.lk"),
            CARGO_TRANSPORT_TABLE,
            Field(id="extra_terms", label="ДОПОЛНИТЕЛЬНЫЕ УСЛОВИЯ", on_blank="gray_block", source="template.body"),
            *_expand(_REQUISITES, "customer"),
            *_expand(_REQUISITES, "carrier"),
            Field(id="sign.customer", label="должность/ФИО Заказчик", on_blank="yellow", source="company.officials"),
            Field(id="sign.carrier", label="должность/ФИО Перевозчик", on_blank="yellow", source="company.officials"),
        ],
    ),
    Blank(
        id="carriage_order",
        title="Договор-заявка",
        family="A",
        kind="flexible",
        parent=None,
        sample="Документы/+Договор-заявка.docx",
        fields=[
            Field(id="number", label="№ 000001…", on_blank="red", source="system.number", note="в образце красный; маска 000000"),
            Field(id="date", label="дата в строке названия", on_blank="red", source="system.date"),
            Field(id="city", label="ГОРОД", on_blank="yellow", source="company.city заказчика"),
            Field(id="preamble_date", label="дата в преамбуле", on_blank="yellow", source="system.date"),
            *_expand(_PREAMBLE_PARTY, "customer"),
            *_expand(_PREAMBLE_PARTY, "carrier"),
            Field(id="intro_static", label="Перевозчик принимает…", on_blank="static", source="static"),
            CARGO_TRANSPORT_TABLE,
            Field(id="extra_terms", label="пункты 1–7 + шаблон", on_blank="gray_block", source="template.body"),
            *_expand(_REQUISITES, "customer"),
            *_expand(_REQUISITES, "carrier"),
            Field(id="sign.customer", label="подпись Заказчик", on_blank="yellow", source="company.officials"),
            Field(id="sign.carrier", label="подпись Перевозчик", on_blank="yellow", source="company.officials"),
        ],
    ),
    Blank(
        id="expedition_contract",
        title="Договор транспортной экспедиции",
        family="B",
        kind="flexible",
        parent=None,
        sample="5_Страница_Договор экспедиции.docx",
        fields=[
            Field(id="number", label="№ договора", on_blank="yellow", source="system.number"),
            Field(id="city", label="ГОРОД", on_blank="yellow", source="company.city клиента"),
            Field(id="date", label="дата", on_blank="yellow", source="system.date"),
            *_expand(_PREAMBLE_PARTY, "client"),
            *_expand(_PREAMBLE_PARTY, "forwarder"),
            Field(id="body", label="ТЕКСТ ДОГОВОРА", on_blank="template", source="template.body"),
            *_expand(_REQUISITES, "client"),
            *_expand(_REQUISITES, "forwarder"),
            Field(id="sign.client", label="подпись Клиент", on_blank="yellow", source="company.officials"),
            Field(id="sign.forwarder", label="подпись Экспедитор", on_blank="yellow", source="company.officials"),
        ],
    ),
    Blank(
        id="forwarder_assignment",
        title="Поручение экспедитору",
        family="B",
        kind="strict",
        parent="expedition_contract",
        sample="Документы/+Поручение экспедитору.docx",
        fields=[
            Field(id="parent.number", label="№ договора экспедиции", on_blank="red", source="parent.number"),
            Field(id="parent.date", label="дата договора экспедиции", on_blank="red", source="parent.date"),
            Field(id="date", label="1 дата", on_blank="dialog_only", source="system.date"),
            Field(id="number", label="2 номер", on_blank="dialog_only", source="system.number"),
            Field(id="shipper", label="3 Грузоотправитель", on_blank="dialog_only", source="counterparties + поставщик"),
            Field(id="client", label="4 Клиент", on_blank="dialog_only", source="поставщик | покупатель"),
            Field(id="consignee", label="5 Грузополучатель", on_blank="dialog_only", source="покупатель"),
            Field(id="forwarder", label="6 Экспедитор", on_blank="dialog_only", source="сторона договора экспедиции"),
            Field(id="notify_party", label="7 Уведомить о прибытии", on_blank="dialog_only", source="user.dialog"),
            Field(id="origin_country", label="8 Страна происхождения", on_blank="dialog_only", source="user.dialog"),
            Field(id="ready_to_ship", label="9 Товары готовы…", on_blank="dialog_only", source="user.dialog"),
            Field(id="transport_mode", label="10 Вид транспорта", on_blank="dialog_only", source="enum auto/rail/sea/air", note="дефолт автомобильный"),
            Field(id="destination", label="11 Пункт назначения", on_blank="dialog_only", source="company.fill_addresses покупателя"),
            Field(id="insurance", label="12 Страхование", on_blank="dialog_only", source="user.dialog"),
            Field(id="commodity_code", label="13 Товарный код", on_blank="dialog_only", source="user.dialog"),
            Field(id="marking", label="14 Маркировка", on_blank="dialog_only", source="user.dialog | cargo"),
            Field(id="places_packaging", label="15 Места, упаковка", on_blank="dialog_only", source="user.dialog | cargo"),
            Field(id="weight_gross_net", label="16 Вес брутто, нетто", on_blank="dialog_only", source="order.lines × карточка товара"),
            Field(id="volume", label="17 Объём", on_blank="dialog_only", source="user.dialog | cargo"),
            Field(id="value", label="18 Стоимость", on_blank="dialog_only", source="сумма заказа"),
            Field(id="package_size", label="19 Размер упаковки", on_blank="dialog_only", source="user.dialog"),
            Field(id="required_docs", label="20 Требуемые документы", on_blank="dialog_only", source="user.dialog"),
            Field(id="notes", label="21 Особые отметки", on_blank="dialog_only", source="user.dialog"),
            Field(id="client_signature", label="22 Подпись клиента", on_blank="dialog_only", source="company.officials"),
        ],
    ),
    Blank(
        id="forwarder_receipt",
        title="Экспедиторская расписка",
        family="B",
        kind="strict",
        parent="expedition_contract",
        sample="Документы/+Экспедиторская расписка.doc",
        fields=[
            Field(id="parent.number", label="№ договора экспедиции", on_blank="red", source="parent.number"),
            Field(id="parent.date", label="дата договора экспедиции", on_blank="red", source="parent.date"),
            Field(id="date", label="1 дата", on_blank="dialog_only", source="system.date"),
            Field(id="number", label="2 номер", on_blank="dialog_only", source="system.number"),
            Field(id="shipper", label="3 Грузоотправитель", on_blank="dialog_only", source="counterparties + поставщик"),
            Field(id="client", label="4 Клиент", on_blank="dialog_only", source="поставщик | покупатель"),
            Field(id="forwarder", label="5 Экспедитор", on_blank="dialog_only", source="сторона договора экспедиции"),
            Field(id="origin_country", label="6 Страна происхождения", on_blank="dialog_only", source="user.dialog"),
            Field(id="commodity_code", label="7 Товарный код", on_blank="dialog_only", source="user.dialog"),
            Field(id="marking", label="8 Маркировка", on_blank="dialog_only", source="user.dialog | cargo"),
            Field(id="places_packaging", label="9 Места, упаковка", on_blank="dialog_only", source="user.dialog | cargo"),
            Field(id="weight_gross_net", label="10 Вес брутто, нетто", on_blank="dialog_only", source="order.lines × карточка товара"),
            Field(id="volume", label="11 Объём", on_blank="dialog_only", source="user.dialog | cargo"),
            Field(id="value", label="12 Стоимость", on_blank="dialog_only", source="сумма заказа"),
            Field(id="package_size", label="13 Размер упаковки", on_blank="dialog_only", source="user.dialog"),
            Field(id="terms", label="14 Условия", on_blank="dialog_only", source="user.dialog"),
            Field(id="notes", label="15 Особые отметки", on_blank="dialog_only", source="user.dialog"),
            Field(id="client_signature", label="16 Подпись клиента", on_blank="dialog_only", source="company.officials"),
        ],
    ),
    Blank(
        id="warehouse_receipt",
        title="Складская расписка",
        family="B",
        kind="strict",
        parent="expedition_contract",
        sample="Документы/+Складская расписка.docx",
        fields=[
            Field(id="parent.number", label="№ договора экспедиции", on_blank="red", source="parent.number"),
            Field(id="parent.date", label="дата договора экспедиции", on_blank="red", source="parent.date"),
            Field(id="date", label="1 дата", on_blank="dialog_only", source="system.date"),
            Field(id="number", label="2 номер", on_blank="dialog_only", source="system.number"),
            Field(id="client", label="3 Клиент", on_blank="dialog_only", source="поставщик | покупатель"),
            Field(id="forwarder", label="4 Экспедитор", on_blank="dialog_only", source="сторона договора экспедиции"),
            Field(id="warehouse", label="5 Склад", on_blank="dialog_only", source="user.dialog"),
            Field(id="origin_country", label="6 Страна происхождения", on_blank="dialog_only", source="user.dialog"),
            Field(id="insurance", label="7 Страхование", on_blank="dialog_only", source="user.dialog"),
            Field(id="commodity_code", label="8 Товарный код", on_blank="dialog_only", source="user.dialog"),
            Field(id="marking", label="9 Маркировка", on_blank="dialog_only", source="user.dialog | cargo"),
            Field(id="places_packaging", label="10 Места, упаковка", on_blank="dialog_only", source="user.dialog | cargo"),
            Field(id="weight_gross_net", label="11 Вес брутто, нетто", on_blank="dialog_only", source="order.lines × карточка товара"),
            Field(id="volume", label="12 Объём", on_blank="dialog_only", source="user.dialog | cargo"),
            Field(id="value", label="13 Стоимость", on_blank="dialog_only", source="сумма заказа"),
            Field(id="package_size", label="14 Размер упаковки", on_blank="dialog_only", source="user.dialog"),
            Field(id="terms", label="15 Условия", on_blank="dialog_only", source="user.dialog"),
            Field(id="notes", label="16 Особые отметки", on_blank="dialog_only", source="user.dialog"),
            Field(id="forwarder_signature", label="17 Подпись экспедитора", on_blank="dialog_only", source="company.officials экспедитора"),
        ],
    ),
]


def blank_by_id(blank_id: str) -> Blank:
    for b in BLANKS:
        if b["id"] == blank_id:
            return b
    raise KeyError(blank_id)


if __name__ == "__main__":
    for b in BLANKS:
        print(f"{b['id']:24} {b['kind']:8} fields={len(b['fields'])}  {b['title']}")
