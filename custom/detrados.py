from zep.helpers import create_tree, rewrite_file


def strip_trados(handoff, locales=None, write=True):
    """
    Strips any p tag that precedes the h1 tag (TRADOS side-effect).
    :param handoff: Handoff object
    :param locales: tuple
    :param write: boolean
    :return: nothing
    """
    handoff.verify_handoff_exists(localized=True)

    if locales is None:                 # if locales not specified, use all locales
        locales = handoff.locales

    for locale in locales:
        files = handoff.get_localized_files(locale)
        for file in files:
            # print('Creating tree from {}'.format(file))
            tree = create_tree(file)
            h1_tag = tree.h1
            previous_p_tag = h1_tag.find_previous('p')
            if previous_p_tag:
                previous_p_tag.decompose()
            if write:
                rewrite_file(file, tree)
        print('Removed TRADOS tags in {} articles.'.format(locale))
