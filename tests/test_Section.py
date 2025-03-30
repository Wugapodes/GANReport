import pytest

from ganreport.Section import Section


def wikilink(section, text):
    return "[[Wikipedia:Good article nominations#" + section + "|" + text + "]]"


def load_section_names(file_path):
    with open(file_path, "r") as f:
        return [line.rstrip("\n") for line in f]


def load_link_params(file_path):
    with open(file_path, "r") as f:
        return [[x.strip() for x in line.rstrip().split(",")] for line in f]


@pytest.mark.parametrize(
    "section_name", load_section_names("tests/data/section_names.txt")
)
def test_section_init_raises_no_exception(section_name):
    Section(section_name)


@pytest.mark.parametrize(
    "section_name", load_section_names("tests/data/section_names.txt")
)
def test_section_str_prints_correct_link(section_name):
    test_section = Section(section_name)
    assert str(test_section) == wikilink(section_name, section_name)


@pytest.mark.parametrize(
    "image, text, num", load_link_params("tests/data/section_link_parameters.txt")
)
def test_section_link(image, text, num):
    with open("tests/data/section_names.txt", "r") as f:
        for section_name in f:
            if text is None:
                expected = wikilink(section_name, section_name) + " " + str(num)
            else:
                expected = wikilink(section_name, text) + " " + str(num)
            test_section = Section(section_name)
            assert test_section.link(image, text, num) == expected
