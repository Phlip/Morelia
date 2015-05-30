#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from morelia.config import get_config


def should_skip(tags_list, pattern):
    tags_list = set(tags_list)
    matching_tags = pattern.split()
    negative_tags = [tag[1:] for tag in matching_tags if tag.startswith('-')]
    positive_tags = [tag for tag in matching_tags if not tag.startswith('-')]
    if negative_tags:
        return bool(set(negative_tags) & tags_list)
    if positive_tags:
        return not set(positive_tags).issubset(tags_list)
    return False


def tags(tags_list, config=None):
    """ Skip decorated test methods or classes if tags matches.

    Tags are matched to patterns provided by config object.

    :param list tags_list: list of tags for test
    :param morelia.config.Config config: optional configuration object
    """
    if config is None:
        config = get_config()
    pattern = config.get_tags_pattern()
    return unittest.skipIf(should_skip(tags_list, pattern), 'Tags not matched')
