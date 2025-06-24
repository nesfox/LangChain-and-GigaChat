#import "ru-numbers.typ": ru-words
#import "@preview/zero:0.3.3": num, set-group
#set-group(size: 3, separator: sym.space.thin, threshold: 4)

#let invoice = json("invoice.json")

#let invoice_overall_sum = invoice.jobs.map(job => job.at("price") * job.at("count")).sum()
#let invoice_jobs_count = invoice.jobs.len()

#let get_invoice_number(
  // d — дата; по умолчанию берём сегодняшнюю
  num,
  d: datetime.today()
) = {
  d.display(
    "[year repr:last_two padding:zero]" + // YY
    "[month padding:zero]"              + // MM
    "[day padding:zero]"                + // DD
    num,                                 // суффикс
  )
}

#let ru-months = (
  "января",  "февраля", "марта",     "апреля",
  "мая",     "июня",    "июля",      "августа",
  "сентября","октября", "ноября",    "декабря",
)
#let today = datetime.today()


#table(
  columns: (auto, 1fr, auto, auto),
  [ИНН 482423943474], [ОГРНИП 313482405700058], table.cell(rowspan: 2, align: bottom)[Сч. №], table.cell(rowspan: 2, align: bottom)[40802810602230000885],
  table.cell(colspan: 2)[Получатель\
  ИП СМОЛЯК ПОЛИНА ВИКТОРОВНА],
  table.cell(colspan: 2, rowspan: 2)[Банк получателя\
  АО "СБЕР-БАНК"],
  table.cell()[БИК],
  table.cell()[044525593],
  table.cell()[Сч. №],
  table.cell()[30101810200000000593],
)

#set align(center)
#block(below: 1.5em, above: 2em)[
#align(center)[
= СЧЕТ № #get_invoice_number("01") от #today.day()~#ru-months.at(today.month() - 1)~#today.year() г.
]
]

#set align(left)

Плательщик: #invoice.customer.name ИНН #invoice.customer.INN ОГРН #invoice.customer.INN

#table(
  columns: (0.4fr, 2.7fr, 0.7fr, 0.7fr, 0.8fr, 1.3fr),
  table.cell(align: center)[№], [Наименование товара], table.cell(align: center)[Ед. изм.], table.cell(align: center)[Кол-во], table.cell(align: center)[Цена, ₽], table.cell(align: center)[Сумма, ₽],
  ..for (index, job) in invoice.jobs.enumerate() {(
    table.cell(align: center)[
      #(index + 1)
    ],[
      #job.at("task")
    ], table.cell(align: center)[шт], table.cell(align: center)[#num(job.at("count"))], table.cell(align: center)[
      #align(center)[#num(job.at("price"))]
    ],table.cell(align: center)[
      #align(center)[#num(invoice_overall_sum)]
    ]
  )},
  table.cell(colspan: 5, stroke: none, align: right)[*Итого:*], table.cell(align: center)[#num(invoice_overall_sum)],
  table.cell(colspan: 5, stroke: none, align: right)[*НДС:*], table.cell(align: center)[не облагается],
  table.cell(colspan: 5, stroke: none, align: right)[*Всего к оплате:*], table.cell(align: center)[#num(invoice_overall_sum)],
)

Всего наименований #invoice_jobs_count , на сумму #num(invoice_overall_sum) (#ru-words(invoice_overall_sum)) руб ноль копеек. Оплачивая настоящий счёт, вы присоединяетесь к Оферте, опубликованной на сайте https://to.digital/oferta.pdf.

#block(above: 3em)[
  ИП Смоляк #text("__________________________") Смоляк П.В.
]