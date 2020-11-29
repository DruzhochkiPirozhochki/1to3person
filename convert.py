import pymorphy2

from const import DICTS

case_mapping = {
    "Nom": "nomn",
    "Gen": "gent",
    "Dat": "datv",
    "Acc": "accs",
    "Ins": "ablt",
    "Loc": "loct"
}

morph = pymorphy2.MorphAnalyzer(path=DICTS)


def change_case(word, new_case):
    word = morph.parse(word)[0]
    return word.inflect({case_mapping.get(new_case, "nomn")}).word


def verb_to_present(word):
    verb_mapping = {
        'скажу': 'говорит', 'замечу': 'замечает', 'подмечу': 'подмечает',
        'отмечу': 'отмечает', 'вижу': 'видит', 'представлю': 'представляет',
        'признаюсь': 'признается', 'боюсь': 'боится', 'добавлю': 'добавляет',
        'допущу': 'допускает', 'обращу': 'обращает', 'осмелюсь': 'осмеливается',
        'позволю': 'позволяет', 'предположу': 'предполагает',
        'скажем': 'говорят', 'заметим': 'замечают', 'подметим': 'подмечают',
        'отметим': 'отмечают', 'видим': 'видят', 'представляем': 'представляют',
        'признаемся': 'признаются', 'признаёмся': 'признаются', 'боимся': 'боятся', 'добавим': 'добавляют',
        'допустим': 'допускают', 'обращаем': 'обращают', 'осмелимся': 'осмеливаются',
        'позволим': 'позволяют', 'предположим': 'предполагают'
    }
    if word in verb_mapping:
        return verb_mapping[word]
    else:
        return word


def make_replacement(word, gender=None, num=None, case=None):
    word = word.lower().strip()
    new_word = word

    p = morph.parse(word)

    personal_male = {'я': 'он', 'меня_р': 'его', 'мне_д': 'ему', 'меня_в': 'него', 'мной': 'им', 'мною': 'им',
                     'мне_п': 'нем'}

    personal_female = {'я': 'она', 'меня_р': 'ее', 'мне_д': 'ей', 'меня_в': 'нее', 'мной': 'ей', 'мною': 'ее',
                       'мне_п': 'ней'}

    personal_plural = {'мы': 'они', 'нас': 'их', 'нам': 'им', 'нас_в': 'их', 'нами': 'ими', 'нас_п': 'них'}

    posessive_male = [
        'мой', 'моего', 'моему', 'моим', 'моем', 'моём',
        'моя', 'моей', 'мою',
        'моё', 'мое',
        'мои', 'моих', 'моим', 'моими'
    ]

    posessive_female = [
        'мой', 'моего', 'моему', 'моим', 'моем', 'моём',
        'моя', 'моей', 'мою',
        'моё', 'мое',
        'мои', 'моих', 'моим', 'моими'
    ]

    posessive_plural = [
        'наш', 'нашего', 'нашему', 'нашим', 'нашем',
        'наша', 'нашей', 'нашу',
        'наше',
        'наши', 'наших', 'нашим', 'нашими'
    ]

    if not (('VERB' in p[0].tag) or ('NOUN' in p[0].tag)):

        # posessive pronouns
        if word in posessive_female:
            new_word = 'ее'
            return new_word
        elif word in posessive_male:
            new_word = 'его'
            return new_word
        elif word in posessive_plural:
            new_word = 'их'
            return new_word

        if num == 'Sing' or num is None:
            # female pronouns
            if gender == 'Fem':
                if case == 'Dat':
                    word = word + '_д'
                elif case == 'Acc':
                    word = word + '_в'
                elif case == 'Loc':
                    word = word + '_п'
                elif case == 'Gen':
                    word = word + '_р'
                if word in personal_female:
                    new_word = personal_female[word]
                    return new_word
                else:
                    print(word + ' not found')

            # male pronouns
            elif gender == 'Masc':
                if case == 'Dat':
                    word = word + '_д'
                elif case == 'Acc':
                    word = word + '_в'
                elif case == 'Loc':
                    word = word + '_п'
                elif case == 'Gen':
                    word = word + '_р'
                if word in personal_male:
                    new_word = personal_male[word]
                    return new_word
                else:
                    print(word + ' not found')

        # plural pronouns
        elif num == 'Plur' or num is None:
            if case == 'Ins':
                word = word + '_в'
            elif case == 'Loc':
                word = word + '_п'
            if word in personal_plural:
                new_word = personal_plural[word]
                return new_word
            else:
                print(word + ' not found')

    # verb detection
    else:
        if 'VERB' in p[0].tag:
            p = p[0]
            # print('word description: ', p)
            if p.tag.person != None:
                new_word = p.inflect({'3per'}).word
        else:
            i = 0
            max_idx = len(p) - 1
            while not 'VERB' in p[i].tag:
                if i != max_idx:
                    i += 1
                else:
                    break
            p = p[i]
            if 'VERB' in p.tag:
                # print('word description: ', p)
                if p.tag.person != None:
                    new_word = p.inflect({'3per'}).word

    return new_word


def name_to_case(name, gender=None, case='Gen'):
    t_name = ''
    case = case_mapping.get(case, "gent")

    if gender == 'Fem':
        gender = 'femn'
    elif gender == 'Masc':
        gender = 'masc'
    tokens = name.split(' ')

    morph = pymorphy2.MorphAnalyzer()

    for token in tokens:
        p = morph.parse(token)
        i = 0
        max_idx = len(p) - 1
        while not gender in p[i].tag:
            if i != max_idx:
                i += 1
            else:
                break
        p = p[i]
        if p.inflect({case}) is not None:
            t_name += p.inflect({case}).word + ' ' # todo: wtf

    new_name = t_name[0].upper()
    for i in range(len(t_name)):
        if t_name[i] == ' ' or t_name[i] == '-':
            if i < len(t_name) - 1:
                new_name += t_name[i + 1].upper()
        else:
            if i < len(t_name) - 1:
                new_name += t_name[i + 1]

    return new_name


if __name__ == '__main__':
    print(make_replacement('мои', num='Plur'))
    print(make_replacement('я', gender='Fem', num='Sing'))
    print(make_replacement('летаю'))
