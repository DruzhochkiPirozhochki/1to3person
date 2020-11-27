import pymorphy2

def make_replacement(word, gender=None, num=None, case=None):

    word = word.lower()
    new_word = word

    morph = pymorphy2.MorphAnalyzer()
    p = morph.parse(word)

    personal_male = {'я': 'он', 'меня': 'его', 'мне_д': 'ему', 'мной': 'им', 'мною': 'им', 'мне_п': 'нем'}

    personal_female = {'я': 'она', 'меня': 'ее', 'мне_д': 'ей', 'мной': 'ей', 'мною': 'ее', 'мне_п': 'ней'}

    personal_plural = {'мы': 'они', 'нас': 'их', 'нам': 'им', 'нас_в': 'их', 'нами': 'ими', 'нас_п': 'них'}

    genitive_male = [
        'мой', 'моего', 'моему', 'моим', 'моем', 'моём',
        'моя', 'моей', 'мою',
        'моё', 'мое',
        'мои', 'моих', 'моим', 'моими'
    ]

    genitive_female = [
        'мой', 'моего', 'моему', 'моим', 'моем', 'моём',
        'моя', 'моей', 'мою',
        'моё', 'мое',
        'мои', 'моих', 'моим', 'моими'
    ]

    genitive_plural = [
        'наш', 'нашего', 'нашему', 'нашим', 'нашем',
        'наша', 'нашей', 'нашу',
        'наше',
        'наши', 'наших', 'нашим', 'нашими'
    ]

    if not (('VERB' in p[0].tag) or ('NOUN' in p[0].tag)):
        if num == 'Sing':

            # female pronouns
            if gender == 'Fem':
                if word in genitive_female:
                    new_word = 'ее'
                else:
                    if case == 'Acc':
                        word = word + '_д'
                    elif case == 'Loc':
                        word = word + '_п'
                    if word in personal_female:
                        new_word = personal_female[word]
                    else:
                        print(word + ' not found')

            # male pronouns
            elif gender == 'Masc':
                if word in genitive_male:
                    new_word = 'его'
                else:
                    if case == 'Acc':
                        word = word + '_д'
                    elif case == 'Loc':
                        word = word + '_п'
                    if word in personal_male:
                        new_word = personal_male[word]
                    else:
                        print(word + ' not found')

        # plural pronouns
        elif num == 'Plur':
            if word in genitive_plural:
                new_word = 'их'
            else:
                if case == 'Ins':
                    word = word + '_в'
                elif case == 'Loc':
                    word = word + '_п'
                if word in personal_plural:
                    new_word = personal_plural[word]
                else:
                    print(word + ' not found')

    # verb detection
    else:
        if 'VERB' in p[0].tag:
            p = p[0]
            print('word description: ', p)
            if p.tag.person != None:
                new_word = p.inflect({'3per'}).word
        else:
            i = 0
            while not 'VERB' in p[i].tag:
                i += 1
            p = p[i]
            print('word description: ', p)
            if p.tag.person != None:
                new_word = p.inflect({'3per'}).word

    return new_word


if __name__ == '__main__':
    print(make_replacement('моя', gender='Fem', num='Sing'))
    print(make_replacement('летаю'))
