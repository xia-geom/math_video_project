from __future__ import annotations

import string
import xml.etree.ElementTree as ET

import pytest

from tools import tts


@pytest.mark.parametrize("letter,spoken", [
    ("y", "i grec"),
    ("Y", "i grec"),
    ("x", "iks"),
    ("X", "iks"),
    ("a", "a"),
    ("A", "a"),
])
def test_letter_alias_has_explicit_speech_and_preserves_caption_case(letter, spoken) -> None:
    token = tts.char(letter)
    element = ET.fromstring(token)

    assert element.tag == "sub"
    assert element.attrib == {"alias": spoken}
    assert element.text == letter
    assert tts.strip_ssml(token) == letter
    assert tts.prepare_math_speech(token) == spoken


def test_letter_policy_covers_exactly_the_latin_alphabet() -> None:
    assert set(tts.FRENCH_LETTER_NAMES) == set(string.ascii_lowercase)
    assert all(isinstance(name, str) and name for name in tts.FRENCH_LETTER_NAMES.values())


@pytest.mark.parametrize("value", ["", "xy", "é", "K", "1", " ", "x ", "<", "\n"])
def test_char_rejects_non_letter_or_multiple_character_input(value) -> None:
    with pytest.raises(ValueError):
        tts.char(value)


def test_aliases_are_authoritative_and_remain_valid_xml_text() -> None:
    source = '<sub alias="A &amp; y">notation</sub>'

    # The author's alias is intentional: do not reinterpret its A or y.
    prepared = tts.prepare_math_speech(source)

    assert prepared == "A &amp; y"
    assert ET.fromstring(f"<speak>{prepared}</speak>").text == "A & y"


@pytest.mark.parametrize("source,spoken", [
    ("<say-as interpret-as='characters'>y</say-as>", "i grec"),
    ('<say-as interpret-as="characters">xy</say-as>', "iks i grec"),
    ('<say-as format="casesensitive" interpret-as="characters">X</say-as>', "iks"),
])
def test_legacy_character_spelling_uses_the_shared_french_names(source, spoken) -> None:
    assert tts.prepare_math_speech(source) == spoken


def test_non_ascii_legacy_symbols_are_not_silently_converted_to_latin_letters() -> None:
    source = "<say-as interpret-as='characters'>K</say-as>"

    assert tts.prepare_math_speech(source) == source


@pytest.mark.parametrize("annotation", ["<!-- pronunciation note -->", "<?speech note?>"])
def test_xml_annotations_inside_atomic_directives_do_not_break_preparation(annotation) -> None:
    source = f'<sub alias="i grec">y{annotation}</sub>'
    phoneme = f"<phoneme alphabet='ipa' ph='iks'>x{annotation}</phoneme>"

    assert tts.prepare_math_speech(source) == "i grec"
    assert tts.prepare_math_speech(phoneme) == phoneme


def test_unambiguous_letters_are_normalized_without_guessing_french_a_or_y() -> None:
    source = "Le point A appartient à l'axe x, et y reste une variable."

    assert tts.prepare_math_speech(source) == (
        "Le point a appartient à l'axe iks, et y reste une variable."
    )


@pytest.mark.parametrize("source", [
    "Il y a un angle; on y revient.",
    "C'est l'angle d'un triangle; j'y vois une relation.",
    "S’il n’a rien, l’angle d’une figure reste inchangé.",
    "A-t-il compris ? Oui, dit-il, peut-être.",
])
def test_french_contractions_and_hyphenated_words_are_byte_identical(source) -> None:
    assert tts.prepare_math_speech(source) == source


def test_existing_pronunciation_directives_and_unrelated_ssml_are_preserved() -> None:
    source = (
        "<lang xml:lang='fr-FR'><prosody rate=\"-3%\">"
        "<phoneme alphabet='ipa' ph='iks'>x</phoneme> et "
        '<say-as interpret-as="name">X</say-as>'
        "<break time='200ms'/><bookmark mark='x > y'/>"
        "</prosody></lang>"
    )

    assert tts.prepare_math_speech(source) == source


def test_replacing_text_keeps_attributes_bookmarks_and_other_markup_intact() -> None:
    source = (
        '<prosody rate="-3%">La variable x'
        "<bookmark mark='x > y'/> puis "
        '<sub alias="i grec">y</sub><break time="150ms"/>.</prosody>'
    )

    assert tts.prepare_math_speech(source) == (
        '<prosody rate="-3%">La variable iks'
        "<bookmark mark='x > y'/> puis "
        'i grec<break time="150ms"/>.</prosody>'
    )


def test_chars_preserves_written_symbols_while_preparing_each_spoken_name() -> None:
    source = tts.chars("X", "y")

    assert tts.strip_ssml(source) == "X y"
    assert tts.prepare_math_speech(source) == "iks i grec"


@pytest.mark.parametrize("left,right", [
    ("A", "a"),
    ("A", "à"),
    ("O", "au"),
])
def test_adjacent_marked_vowel_and_same_french_sound_require_rephrasing(left, right) -> None:
    with pytest.raises(ValueError):
        tts.validate_pronunciation(f"Le point {tts.char(left)} {right} une image.")


def test_french_preposition_before_marked_a_also_requires_rephrasing() -> None:
    with pytest.raises(ValueError):
        tts.validate_pronunciation(f"On applique la transformation à {tts.char('A')}.")


def test_repeated_marked_vowels_and_legacy_spelling_use_the_same_guard() -> None:
    with pytest.raises(ValueError):
        tts.validate_pronunciation(tts.chars("a", "A"))
    with pytest.raises(ValueError):
        tts.validate_pronunciation("<say-as interpret-as='characters'>A</say-as> a une image.")


def test_unambiguous_raw_math_vowel_cannot_bypass_the_guard() -> None:
    with pytest.raises(ValueError):
        tts.validate_pronunciation("Le point A a une image.")


def test_bookmarks_and_transparent_wrappers_do_not_hide_repeated_vowels() -> None:
    source = (
        f"Le point <prosody rate='-3%'>{tts.char('A')}</prosody>"
        "<bookmark mark='next'/> a une image."
    )

    with pytest.raises(ValueError):
        tts.validate_pronunciation(source)


@pytest.mark.parametrize("separator", [". ", ", ", "; ", " : ", "<break time='150ms'/>"])
def test_authored_pause_separates_repeated_vowel_sounds(separator) -> None:
    tts.validate_pronunciation(f"{tts.char('A')}{separator}a une image.")


@pytest.mark.parametrize("pause", [
    "<break time='0ms'/>",
    "<break time='0s'/>",
    "<break strength='none'/>",
    "<break time='0ms' strength='strong'/>",
])
def test_zero_length_break_does_not_hide_adjacent_vowels(pause) -> None:
    with pytest.raises(ValueError):
        tts.validate_pronunciation(f"Le point {tts.char('A')}{pause} a une image.")


def test_meaningful_repeated_variables_and_ordinary_french_are_allowed() -> None:
    tts.validate_pronunciation(f"On calcule {tts.char('a')} fois {tts.char('a')}.")
    tts.validate_pronunciation("Il y a un angle à analyser.")
    tts.validate_pronunciation(f"Le point {tts.char('A')} devient le point B.")


def test_repetition_guard_is_not_a_general_phonetic_dictionary() -> None:
    # A word beginning with the same vowel is not a repeated standalone vowel.
    tts.validate_pronunciation(f"Le point {tts.char('A')} appartient au triangle.")
