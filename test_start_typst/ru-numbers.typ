// --------------------------------------------------------------
// Число → русская пропись (до миллиардов). Typst 0.12+
// --------------------------------------------------------------

#import calc: rem, floor    // rem — остаток; floor — целая часть

// — словари —
#let _units = (
  "ноль", "один", "два", "три", "четыре",
  "пять", "шесть", "семь", "восемь", "девять",
  "десять", "одиннадцать", "двенадцать", "тринадцать", "четырнадцать",
  "пятнадцать", "шестнадцать", "семнадцать", "восемнадцать", "девятнадцать",
)


#let _tens = (
  "", "", "двадцать", "тридцать", "сорок",
  "пятьдесят", "шестьдесят", "семьдесят", "восемьдесят", "девяносто",
)


#let _hundreds = (
  "", "сто", "двести", "триста", "четыреста",
  "пятьсот", "шестьсот", "семьсот", "восемьсот", "девятьсот",
)

// (1-форма, 2–4-форма, 5+-форма, женский род?)
#let _scales = (
  ("",        "",         "",          false),
  ("тысяча",  "тысячи",   "тысяч",     true ),
  ("миллион", "миллиона", "миллионов", false),
  ("миллиард","миллиарда","миллиардов",false),
)

// — выбор формы слова-разряда —
#let _form(n, one, few, many) = {
  let m    = rem(n, 100)
  let last = rem(n, 10)
  if m >= 11 and m <= 14 { many }
  else if last == 1 { one }
  else if last >= 2 and last <= 4 { few }
  else { many }

}

// — пропись триады (0–999) —
#let _chunk(n, fem) = {
  let words = ()

  // сотни
  let h = floor(n / 100)
  if h != 0 { words.push(_hundreds.at(h)) }

  // < 100
  let rest = rem(n, 100)
  if rest < 20 {
    if rest != 0 {
      let w = _units.at(rest)
      if fem and rest == 1 { words.push("одна") }
      else if fem and rest == 2 { words.push("две") }
      else { words.push(w) }
    }
  } else {
    let t = floor(rest / 10)
    words.push(_tens.at(t))

    let u = rem(rest, 10)
    if u != 0 {
      let w = _units.at(u)
      if fem and u == 1 { words.push("одна") }
      else if fem and u == 2 { words.push("две") }
      else { words.push(w) }
    }
  }

  words.join(" ")
}

// — экспортируемая функция —
#let ru-words(n) = {
  if n == 0 { _units.at(0) }
  else {
    let parts = ()
    let scale = 0
    let num   = n

    while num > 0 {
      let chunk = rem(num, 1000)
      if chunk != 0 {
        let (one, few, many, fem) = _scales.at(scale)
        let chunk_words = _chunk(chunk, fem)

        if scale == 0 {
          parts.push(chunk_words)

        } else {
          let name = _form(chunk, one, few, many)
          parts.push(chunk_words + " " + name)
        }
      }
      scale += 1

      num = floor(num / 1000)
    }

    parts.rev().join(" ")
  }
}
