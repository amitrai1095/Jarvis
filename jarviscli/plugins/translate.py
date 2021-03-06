from plugin import plugin, require, alias
from googletrans import Translator
from googletrans.constants import LANGCODES, LANGUAGES, SPECIAL_CASES
import nltk


@require(network=True)
@alias('trans')
@plugin('translate')
def translate(jarvis, s):
    """
    Translates from one language to another and allows input to be somewhat natural.

    Usage:

    'Jarvis, please translate, from English to French, Hello, how are you?'

    OR

    'Jarvis, could you translate Hello, how are you? from English to French for me please?'
    """

#   Check whether user has entered translate by itself or with extra parameters
    if s != "":
        words = nltk.word_tokenize(s.lower())
        currentPos = 0
        finalPos = 0
        srcs = None
        des = None

#       Search input string for source language
        for i in range(len(words)):
            word = words[i]
            currentPos = i

#           Do not include lang codes in the tests when using full sentence command since words can conflict with them (Eg. hi -> Hindi).
#           This code looks like it includes them, but since the googletrans API is implemented such that the languages are stored in
#           dictionaries, when the "in" operator is used, it only checks the keys of the dictionary, not the values. Therefore, the
#           LANG_CODES dictionary must be used to check full language names instead of the LANGUAGES dictionary. For more clarification,
#           have a look at the code on the googletrans github.
            if (word in LANGCODES):
                srcs = word
                break

#       Search input string for destination language starting from the word after the source language
        for i in range(currentPos + 1, len(words)):
            word = words[i]
            finalPos = i
#           Do not include LANGCODES in the tests when using full sentence command since words can conflict with them (Eg. hi -> Hindi)
            if (word in LANGCODES):
                des = word
                break

#       If both languages found, work out where the text to be translated is in the sentence and perform the translation
        if (des and srcs):
            if(currentPos < 2):
                tex = " ".join(words[finalPos + 1:])
            else:
                tex = " ".join(words[:currentPos - 1])  # Discards extra words at the end of the sentence
            performTranslation(srcs, des, tex)
#       Otherwise perform the default method for translation
        else:
            jarvis.say("\nSorry, I couldn't understand your translation request. Please enter the request in steps.")
            default(jarvis)
    else:
        default(jarvis)


def default(jarvis):
    """
    Default function that is called when translate is entered alone or
    when input is not understood when translate is entered with additional parameters
    """
#   Get source language
    jarvis.say('\nEnter source language ')
    srcs = jarvis.input().lower().strip()
#   Check source language
    while (
        srcs not in LANGUAGES) and (
        srcs not in SPECIAL_CASES) and (
            srcs not in LANGCODES):
        if srcs in SPECIAL_CASES:
            srcs = SPECIAL_CASES[srcs]
        elif srcs in LANGCODES:
            srcs = LANGCODES[srcs]
        else:
            jarvis.say("\nInvalid source language\nEnter again")
            srcs = jarvis.input().lower()
#   Get destination language
    jarvis.say('\nEnter destination language ')
    des = jarvis.input().lower().strip()
#   Check destination language
    while (
        des not in LANGUAGES) and (
        des not in SPECIAL_CASES) and (
            des not in LANGCODES):
        if des in SPECIAL_CASES:
            des = SPECIAL_CASES[des]
        elif des in LANGCODES:
            des = LANGCODES[des]
        else:
            jarvis.say("\nInvalid destination language\nEnter again")
            des = jarvis.input().lower()

    jarvis.say('\nEnter text ')
    tex = jarvis.input()

    performTranslation(srcs, des, tex)


def performTranslation(srcs, des, tex):
    """
    Function to actually perform the translation of text and print the result
    """
    translator = Translator()
    result = translator.translate(tex, dest=des, src=srcs)
    result = u"""
[{src}] {original}
    ->
[{dest}] {text}
[pron.] {pronunciation}
    """.strip().format(src=result.src, dest=result.dest, original=result.origin,
                       text=result.text, pronunciation=result.pronunciation)
    print("\n" + result)
