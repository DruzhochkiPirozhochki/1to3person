from natasha import Doc, NewsEmbedding, NewsMorphTagger, Segmenter, NewsSyntaxParser, NewsNERTagger
from statistics import mode

from const import FEM_TEXT1

emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
segmenter = Segmenter()
syntax_parser = NewsSyntaxParser(emb)
ner_tagger = NewsNERTagger(emb)


def identify_gender(doc, name=None):
    name_gender = None
    if name is not None:
        namedoc = Doc(name)
        namedoc.segment(segmenter)
        namedoc.tag_morph(morph_tagger)
        namedoc.tag_ner(ner_tagger)

        if len(namedoc.spans) > 0 and namedoc.spans[0].type == "PER":
            name_gender = mode([token.feats.get("Gender") for token in namedoc.spans[0].tokens if
                                token.feats.get("Gender") is not None])

    if type(doc) == str:
        doc = Doc(doc)
        doc.segment(segmenter)
        doc.tag_morph(morph_tagger)
        doc.parse_syntax(syntax_parser)
        doc.tag_ner(ner_tagger)
    genders = {"Fem": 0, "Masc": 0, None: 0}
    for token in doc.tokens:
        if token.pos in ["PRON"]:#["VERB", "AUX", "ADJ"]:
            sent, num = map(lambda x: int(x) - 1, token.head_id.split("_"))
            head = doc.sents[sent].tokens[num]

            if token.rel in ["nsubj"] and token.feats.get("Person") == '1' and head.pos in ["VERB", "AUX", "ADJ"]:
                genders[head.feats.get("Gender")] += 1
            # if token.feats.get("Person") == '1' or head.pos == "PRON" and head.feats.get("Person") == '1':
            #     genders[token.feats.get("Gender")] += 1

    genders[name_gender] += 0.25 * (genders["Masc"] + genders["Fem"] + 1)  # some threshold
    del genders[None]
    return max(genders, key=genders.get)


if __name__ == '__main__':
    assert identify_gender(
        "Я сидела на крыльце. Он жевал жвачку, а потом я ушла домой. Знаю, что это было лишним.",
        "Альфия Васильевна Мулина-Кончарова") == "Fem"

    assert identify_gender(
        "Могу пояснить, что сегодня я был дома и ничего не делал.", "Алексей Васильев") == "Masc"

    assert identify_gender(*FEM_TEXT1) == "Fem"
