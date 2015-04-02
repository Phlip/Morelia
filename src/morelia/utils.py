def to_unicode(text):
    ''' Try convert to unicode independently on python version. '''
    try:
        text = text.decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError, AttributeError):
        pass
    return text
