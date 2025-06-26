#import "ru-numbers.typ": ru-words
#import "@preview/zero:0.3.3": num, set-group
#set-group(size: 3, separator: sym.space.thin, threshold: 4)

#let act = json("act.json")
#let act_sum = act.jobs.map(job => float(job.at("count")) * float(job.at("price"))).sum()
#let act_nds = act_sum * 0.15  // НДС 18%
#let act_total = act_sum + act_nds

= Акт выполненных работ (оказания услуг)

#datetime.today().display("[day].[month].[year]")

#table(
  columns: 2,
  stroke: none,
  inset: (left: 0pt),
  [*Исполнитель:*], [ООО «Мобайл»],
  [*Заказчик:*],    [#act.customer.at("name")]
)

Мы, представители Исполнителя #text(weight: "bold")[ООО «Мобайл»],
#linebreak()
в лице директора Смоляк Полины Викторовны
#linebreak()
с одной стороны, и представители Заказчика #text(weight: "bold")[#act.customer.at("name")],
#linebreak()
в лице директора #act.customer.at("signatory")
#linebreak()
с другой стороны, составили настоящий акт о том, что Исполнителем были выполнены следующие работы (оказаны следующие услуги) по договору №211-17 от 01.06.2017 г.:

#table(
  columns: 6,
  [№], [Наименование товара], [Ед. изм.], [Кол-во], [Цена], [Сумма],
  ..for (index, job) in act.jobs.enumerate() {(
    [
      #(index + 1)
    ], [
      #job.at("task")
    ], [
      #job.at("unit")
    ], [
      #job.at("count")
    ], [
      #num(float(job.at("price")))
    ], [
      #num(float(job.at("count")) * float(job.at("price")))
    ]
  )}
)

#align(right)[
  #text(weight: "bold")[Итого:] #num(act_sum)
  #linebreak()
  #text(weight: "bold")[В том числе НДС (15%):] #num(act_nds)
  #linebreak()
  #text(weight: "bold")[Всего (с учетом НДС):] #num(act_total)
]

Всего оказано услуг на сумму (с НДС): #text(weight: "bold")[#ru-words(int(act_total))] рублей 00 коп.
#linebreak()
в т.ч. НДС — #text(weight: "bold")[#ru-words(int(act_nds))] рублей 00 коп.

Вышеперечисленные работы (услуги) выполнены полностью и в срок. Заказчик претензий по объему, качеству и срокам оказания услуг не имеет.

#table(
  columns: 2,
  stroke: none,
  inset: (left: 0pt),
  [
    ЗАКАЗЧИК\
    #act.customer.at("name")\
    ИНН #act.customer.at("INN") КПП #act.customer.at("KPP")\
    Адрес: #act.customer.at("address")\
    Р/с #act.customer.at("bank").at("current_account")\
    К/с #act.customer.at("bank").at("corporate_account")\
    Банк #act.customer.at("bank").at("name")\
    БИК #act.customer.at("bank").at("BIC")\
    Директор #act.customer.at("signatory")\
    (подпись)\
    М.П.
  ], [
    ИСПОЛНИТЕЛЬ\
    ООО «Мобайл»\
    ИНН 9876543210 КПП 12345678\
    Адрес: г. Москва, ул. Серова, 25\
    Р/с 12345678901234567890\
    К/с 123456789012\
    Банк Гаммабанк\
    БИК 74569882\
    Директор П.В. Смоляк\
    (подпись)\
    М.П.
  ],[
    \
    #text("________________/") #act.customer.at("signatory") /
  ], [
    \
    #text("________________/") Смоляк П.В. /
  ]
)
