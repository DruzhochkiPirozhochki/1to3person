from copy import copy, deepcopy
from itertools import accumulate
from types import SimpleNamespace

from natasha import (
    Doc
)

from const import DETPRON, SELFDETERMINERS, MYDETERMINERS, QUOTES, segmenter, morph_tagger, syntax_parser, ner_tagger
from convert import make_replacement, change_case, name_to_case
from gender_identification import identify_gender


def transform_word(word, gender, case, num):
    # for now this is mocked
    return word


def add_quotes(quotes, symbol):
    if symbol in QUOTES:
        symbol = QUOTES[symbol]
        if symbol in quotes:
            del quotes[symbol]
        else:
            quotes[symbol] = 1

    return len(quotes) == 0


def find_ambiguous_pronouns(gender, doc, narrator):
    """
    Find all ambiguous pronouns that need to be replaced with name
    :param gender:
    :param doc:
    :return:
    """
    current_token = 0

    tokens = deepcopy(doc.tokens)
    spans = deepcopy(doc.spans)

    # select only ones which have the same gender and belong to a person
    spans = [span for span in spans if span.type == "PER" and span.tokens[0].feats.get("Gender", None) == gender]
    nouns = [token for token in tokens if
             token.pos == "NOUN" and token.feats.get("Gender", None) == gender and token.feats.get("Animacy",
                                                                                                   None) == "Anim"]

    spans_and_nouns = []

    cur_pos_spans = 0
    cur_pos_nouns = 0
    for i in range(len(spans) + len(nouns)):
        if cur_pos_spans >= len(spans):
            spans_and_nouns.extend(nouns[cur_pos_nouns:])
        elif cur_pos_nouns >= len(nouns):
            spans_and_nouns.extend(spans[cur_pos_spans:])
        elif nouns[cur_pos_nouns].start < spans[cur_pos_spans].start:
            spans_and_nouns.append(nouns[cur_pos_nouns])
            cur_pos_nouns += 1
        else:
            spans_and_nouns.append(spans[cur_pos_spans])
            cur_pos_spans += 1

    to_change = {}
    quotes = {}

    for spani, span in enumerate(spans_and_nouns):
        next_span = spans_and_nouns[spani + 1] if spani + 1 < len(spans_and_nouns) else SimpleNamespace(
            start=float('inf'))
        step = '1'
        for i in range(current_token, len(tokens)):
            current_token += 1
            token = tokens[i]

            if token.start <= span.stop:
                # if token is before the name
                continue
            if token.start >= next_span.start:
                # if there is new name already
                break

            if not add_quotes(quotes, token.text):
                continue

            if step == '1' and (token.feats.get("Person", None) == "1" or token.pos == "DET"):
                # todo: also try to find determiners with the same gender
                if token.pos == "PRON":
                    step = '3'
                    to_change[token.id] = (
                        token.start, token.stop, name_to_case(narrator, gender, token.feats.get('Case', 'Gen')).strip())
                elif token.pos == "DET" and token.text.lower().strip() in DETPRON[gender][step]:
                    step = '3'
                    to_change[token.id] = (
                        token.start, token.stop, "свой")  # "put свой "  # the narrator's name after in Genitive case"))
            elif step == '3' and (token.feats.get("Person", None) == "3" or token.pos in ["DET"]):
                if token.pos in ["PRON"]:
                    to_change[token.id] = (token.start, token.stop, token.text)
                    spans[spani:spani] = [SimpleNamespace(text=span.text)]
                    break
                elif token.pos == "DET" and token.text.lower().strip() in DETPRON[gender][step]:
                    obj = token.head_id.split("_")
                    obj_token = doc.sents[int(obj[0]) - 1].tokens[int(obj[1]) - 1]
                    to_change[token.id] = (
                        obj_token.stop, obj_token.stop, f"{name_to_case(span.text, gender=gender, case='Gen').strip()}",
                        obj_token.id)
                    spans[spani:spani] = [SimpleNamespace(text=span.text)]
                    break
    return to_change


def make_change(changes, start, stop, ind):
    changes.append((start, stop, ind))


def transform_text(text, narrator):
    """
    Transform the given text from the first person to third
    :param text: the text itself
    :param narrator: the name of the narrator
    :return:
    """
    transformed = copy(text)
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    doc.parse_syntax(syntax_parser)
    doc.tag_ner(ner_tagger)

    gender = identify_gender(doc)
    ambiguous = find_ambiguous_pronouns(gender, doc, narrator)

    print(ambiguous)
    offsets = [0] * len(doc.tokens)
    quotes = {}

    changes = []

    for i, token in enumerate(doc.tokens):
        new_word = None
        if not add_quotes(quotes, token.text):
            continue

        if token.pos == "VERB" or token.pos == "PRON" and token.feats.get("Person") == '1':
            new_word = make_replacement(token.text, gender,
                                        token.feats.get("Number", None),
                                        token.feats.get("Case", None))
            if new_word.lower().strip() == token.text.lower().strip():
                new_word = None
        elif token.pos == "DET":
            if token.text in SELFDETERMINERS:
                continue
            elif token.text.lower() in MYDETERMINERS:
                sentence = int(token.id.split("_")[0]) - 1
                head = int(token.head_id.split("_")[1]) - 1
                curid = int(token.id.split("_")[1]) - 1
                if curid - head > 3:  # some threshold; if there is a determiner after the object
                    word2insert = doc.sents[sentence - 1].tokens[head]
                    word2insert = change_case(word2insert.text, token.feats.get("Case", None))
                    # print(f"you need to insert {word2insert} after {token.text}")

                    new_determiner = MYDETERMINERS[token.text.lower()]
                    transformed = new_determiner.join(
                        [transformed[:token.start + sum(offsets[:i])], transformed[token.stop + sum(offsets[:i]):]])

                    make_change(changes, token.start, token.start + len(new_determiner), i)

                    offsets[i] += len(new_determiner) - len(token.text)

                    transformed = word2insert.join([transformed[:token.stop + 1 + sum(offsets[:i + 1])] + " ",
                                                    transformed[token.stop + 1 + sum(offsets[:i + 1]):]])

                    make_change(changes, token.stop + 1, token.stop + len(word2insert) + 1 + 1, i)
                    offsets[i] += len(word2insert) + 1
                elif curid - head < 0:
                    new_determiner = make_replacement(token.text, gender, token.feats.get("Number", None),
                                                      token.feats.get("Case", None))
                    transformed = new_determiner.join(
                        [transformed[:token.start + sum(offsets[:i])], transformed[token.stop + sum(offsets[:i]):]])

                    make_change(changes, token.start, token.start + len(new_determiner), i)
                    offsets[i] += len(new_determiner) - len(token.text)
                # else:
                #     new_determiner = MYDETERMINERS[token.text.lower()]
                #     transformed = new_determiner.join(
                #         [transformed[:token.start + sum(offsets[:i])], transformed[token.stop + sum(offsets[:i]):]])
                #     global_offset += len(new_determiner) - len(token.text)
                #     offsets[i] += len(new_determiner) - len(token.text)
                continue

        if token.id in ambiguous:
            ambiguous_replace = ambiguous[token.id]
            if ambiguous_replace[0] == ambiguous_replace[1]:
                transformed = "".join(
                    [transformed[:token.start + sum(offsets[:i])], transformed[token.stop + sum(offsets[:i]):]])
                # make_change(changes, token.start - 1, token.stop, i)

                offsets[doc.tokens.index(token)] -= len(token.text)

                sent, num = map(lambda x: int(x) - 1, ambiguous_replace[3].split('_'))
                another_token = doc.sents[sent].tokens[num]

                ind = doc.tokens.index(another_token)
                transformed = (" " + ambiguous_replace[2]).join([transformed[:another_token.stop + sum(offsets[:ind])],
                                                                 transformed[
                                                                 another_token.stop + sum(offsets[:ind]):]])

                make_change(changes, token.stop, token.stop + len(ambiguous_replace[2]) + 1, i)

                offsets[ind] += len(ambiguous_replace[2]) + 1
                continue
            transformed = ambiguous_replace[2].join(
                [transformed[:ambiguous_replace[0] + sum(offsets[:i])],
                 transformed[ambiguous_replace[1] + sum(offsets[:i]):]])
            make_change(changes, ambiguous_replace[0], ambiguous_replace[0] + len(ambiguous_replace[2]), i)
            offsets[i] += len(ambiguous_replace[2]) - len(token.text)
            continue

        if new_word is not None:
            transformed = new_word.join([transformed[:token.start + sum(offsets[:i])],
                                         transformed[token.stop + sum(offsets[:i]):]])
            make_change(changes, token.start, token.start + len(new_word), i)

            offsets[i] += len(new_word) - len(token.text)

            # doc.syntax.print()

    # capitalize all the first letters in each sentence
    for sent in doc.sents:
        offset = sum(offsets[:doc.tokens.index(sent.tokens[0])])
        transformed = transformed[sent.start + offset].upper().join(
            [transformed[:sent.start + offset], transformed[sent.start + offset + 1:]])

    cum_offsets = [0] + list(accumulate(offsets))
    for i, change in enumerate(changes):
        token_i = change[2]
        changes[i] = (change[0] + cum_offsets[token_i], change[1] + cum_offsets[token_i])
    print(*doc.tokens, sep="\n")
    for change in changes:
        print(change, transformed[change[0]:change[1]])
    return transformed


# todo: fix переносы ???
# todo: fix гендер DONE
# todo: fix заглавные буквы DONE
# todo: fix кавычки и цитаты DONE

if __name__ == '__main__':
    # print(transform_text("Алексей встретил своего деда дома, а я люблю моего", "Masc", "Артем Баханов"))
    # print(make_replacement("я", "Fem", None, "Nom"))
    # print(transform_text(
    #     "Я сидела за столом. Илья играл на гитаре. Маша сидела на его диване. Я сидела на ее очень красивом и прекрасном стуле, а потом посидела на моем. Она лежала и делала работу. Она потом ушла, а он остался.",
    #     "Александра Крапива"))

    # print(transform_text(
    #     "Я с Алиной Бадюк сидела на кухне в Калининграде и разговаривали. Он работал. Через два часа я ушла домой. Она оставалась на кухне."))
    # transform_text("Я пошла в магазин, и она что-то сделала с моим другом. Я не смогла ей противиться и поэтому пошла за ней. Она сказала: \"привет, как твои дела?\"")
    # transform_text("Мой подарок, нет твоего подарка, виню твой подарок, твоему подарку, твоим подарком, о твоем подарке, о твоих подарках.")
    # transform_text("Также хочу пояснить, что за выступления в цирковой группе я получаю денежные средства.")
    # print(transform_text("""По существу заданных вопросов могу пояснить, что
    # по вышеуказанному адресу проживаю с родителями Совуновой Аллой Николаевной и
    # Совуновым Вадимом Евгеньевичем. В свободное от обучения в средней общеобразовательной школе № 96 время я занимаюсь в цирковой студии «Престиж», с которой периодически выступаю, в том числе с выездом.
    # Так, 11.05.2015 года я с напарником по цирковой студии Галич Денисом Юрьевичем
    # поехали в г. Челябинск на выступление в ледовой арене «Трактор». 19.05.2015 года я с Галич Д.Ю. возвращались обратно в г. Омск, для чего на станции Челябинск мы осуществили
    # посадку в пассажирский поезд № 098 сообщением «Кисловодск-Тында» в вагон № 14 на
    # места № 22, 24, 26. На одном месте находился реквизит. Осуществив посадку и заняв свои
    # места мы легли спать, телефон был все время при мне, однако перед тем как лечь спать он
    # выключился, т.к. сел заряд аккумулятора""", "Аля Котик"))
    # print(transform_text("""Я сидела на стуле. В этот момент мой телефон зазвонил.""", "Алла Марутова"))
    #     print(transform_text("""По существу заданных вопросов могу пояснить, что
    # по вышеуказанному адресу проживаю с родителями Совуновой Аллой Николаевной и
    # Совуновым Вадимом Евгеньевичем. В свободное от обучения в средней общеобразовательной школе № 96 время я занимаюсь в цирковой студии «Престиж», с которой периодически выступаю, в том числе с выездом.
    # Так, 11.05.2015 года я с напарником по цирковой студии Галич Денисом Юрьевичем
    # поехали в г. Челябинск на выступление в ледовой арене «Трактор». 19.05.2015 года я с Галич Д.Ю. возвращались обратно в г. Омск, для чего на станции Челябинск мы осуществили
    # посадку в пассажирский поезд № 098 сообщением «Кисловодск-Тында» в вагон № 14 на
    # места № 22, 24, 26. На одном месте находился реквизит. Осуществив посадку и заняв свои
    # места мы легли спать, телефон был все время при мне, однако перед тем как лечь спать он
    # выключился, т.к. сел заряд аккумулятора. Проснувшись утром по станции Петропавловск
    # мы находились на своих местах, так как в вагоне работали пограничники, проводили проверку пассажиров. В вагоне было много пассажиров, некоторые из них в пути следования
    # распивали спиртные напитки. В том числе в вагоне из числа пассажиров были военнослужащие, других отличительных признаков я не запомнила. После того как проводник прошел по вагону и предупредил, что до станции Омск оставалось около 15 минут, я решила
    # пойти поставить свой мобильный телефон на зарядку для того, чтобы позвонить маме и
    # сказать о прибытии поезда. Так, я прошла в нерабочий тамбур, где напротив туалета над
    # окном поставила свой мобильный телефон заряжаться, положив его на верхний уступ окна.
    # В момент, когда я ставила телефон на зарядку, в тамбуре напротив туалета стоял проводник вагона, он видел все мои действия. Проводник дожидался пассажира, который находился в туалете, для того чтобы закрыть туалет перед прибытием на станцию Омск. Поставив телефон на зарядку я решила вернуться на свое место, через минуту за мной вышел из
    # тамбура и проводник и прошел к себе. Я находилась на свое месте около 7-10 минут, после
    # чего решила проверить свой мобильный телефон. Также у меня вызвала подозрение женщина, на вид цыганка, которая прошла в сторону туалета. Так, подойдя к нерабочему тамбуру я увидела, что в розетке осталось только зарядное устройство от моего мобильного
    # телефона, самого телефона не было. Я сразу поняла, что его похитили и пошла к проводнику, сообщила о случившемся, на что проводник ответил что по станции Омск вызовет сотрудников полиции для разбирательств.
    # По прибытию на станцию Омск в вагон зашли сотрудники полиции , которым я указала на место где стоял телефон на зарядке и устно объяснила, что случилось. После этого я
    # сошла по станции Омск вместе с одним из сотрудников полиции и проследовали в дежурную часть Омского ЛУ МВД России, где в присутствии мама – Совуновой Аллы Николаевны я написала заявление и меня опросили сотрудники полиции по факту случившегося.
    # Также поясняю, что мобильный телефон у меня был марки «Iphone» модель «4s», IMEI 013532009242428 в корпусе белого цвета. На момент хищения мобильный телефон находился в чехле черного цвета, на задней стенке чехла изображена девушка с фотоаппаратом. Телефон не имел трещин, сколов иных механических повреждений. Мобильный телефон приобретался за 18 000 рублей примерно в сентябре 2014 года, при этом в данную
    # сумму входила его настройка. В настоящее время с учетом износа, я оцениваю мобильный
    # телефон в 13 500 рублей 00 копеек, как указано в чеке, который я готова выдать. Чехол для
    # меня материальной ценности не представляет. На момент хищения в мобильном телефоне
    # находилась сим-карта оператора ОАО «МТС» с абонентским номером +79835288572. Симкарта материальной ценности сим-карта для меня не представляет, денежных средств на
    # момент хищения на сим-карте не было. Данный абонентский номер оформлен на моего папу – Совунова Вадима Евгеньевича.
    # Также хочу пояснить, что за выступления в цирковой группе я получаю денежные
    # средства. Оплата за наши выступления сдельная, выступаем на бездоговорной основе. В
    # среднем один час выступления стоит от 1 500 рублей, в зависимости от сложности номера.
    # В месяц примерно я зарабатываю от 8 000 до 10 000 рублей. Именно с данных денежных
    # средств был куплен похищенный у меня мобильный телефон, кроме того, из заработанных
    # денег - часть заработка идет на оплату поездок, покупку билетов на транспорт, поэтому, в
    # силу того, что я еще обучаюсь в школе, постоянного заработка не имею, и нахожусь на иждивении родителей в связи с чем, ущерб на сумму 13 500 рублей 00 копеек причиненный
    # мне, является для меня значительным. Мобильный телефон покупался в рассрочку, которая
    # была оформлена на мою маму – Совунову А.Н., однако денежные средства вносила я, по
    # мере их получения за выступления.
    # В настоящее время при мне находится коробка от мобильного телефона марки
    # «Iphone» модель «4s», IMEI 013532009242428 в корпусе белого цвета, два электронных билета на листах А4, копия свидетельства о рождении на мое имя, а также электронная выписка чека из магазина «Связной» и документы из магазина, где приобретали мобильных
    # телефон. Данные предметы и документы я готова выдать.
    # Больше по данному факту мне пояснить нечего. """, "Совунова Анастасия Вадимовна"))

    print(transform_text("""В совершении данного преступления никого не подозреваю. В квартире проживаю один. Квартира принадлежит мне на праве собственности, приобретал я по договору ипотеки в августе 2012 года. Ипотечный договор я заключал с банком ЗАО «Коммерческий Банк «Зернобанк»» в июле 2012 года. По данному договору я получил кредит в размере 600.000 рублей. Платежи по данному кредиту аннуитентные и составляют 8.000 рублей в месяц.
О совершенной краже я сказал Березкиной Анне и моим родителям.

Дополнительно отмечу, что домофона в нашем доме нет. Системы видео-фиксации в подъезде, возле подъезда, по периметру дома отсутствуют. Лиц злоупотребляющих спиртным, собирающихся в подъезде, ведущих антиобщественный образ жизни и проживающих в нашем доме я не знаю. Большая часть жильцов дома – это пенсионеры. За то время, что я проживаю в данном доме каких-либо происшествий криминального характера не происходило. В связи со сказанным, у меня нет никаких предположений относительно того, кто мог бы совершить кражу имущества из моей квартиры.""",
                         "Участник"))
#     print(transform_text("Я была на заводе, когда Андрей подошел ко мне и сказал: \"Я хочу, чтобы ты ушла от меня\". Я отказалась, потому что работаю в это время", "Алиса Купатова"))
