def movie_quotes(name):
    """Возвращает цитаты известных персонажей из фильмов

    >>> movie_quotes('Элли')
    'Тото, у меня такое ощущение, что мы не в Канзасе!'

    >>> movie_quotes('Шерлок')
    'Элементарно, Ватсон!'

    >>> movie_quotes('Дарт Вейдер')
    'Люк, я — твой отец.'

    >>> movie_quotes('Леонид Тощев')
    'Персонаж пока не известен миллионам.'
    """
    quotes = {
        'Элли': 'Тото, у меня такое ощущение, что мы не в Канзасе!',
        'Шерлок': 'Элементарно, Ватсон!',
        'Дарт Вейдер': 'Люк, я — твой отец.',
    }
    return quotes.get(name, 'Персонаж пока не известен миллионам.')
