def cores_disponiveis():
    '''
        Retorna as cores disponíveis para serem usadas
    '''
    return db(db.colors.used == False).select()

# Inserir cores quando as cores disponíveis tiverem menores que 10

quant_colors = len(cores_disponiveis())

if quant_colors < 10:
    random_colors = randomcolor.RandomColor()

    cor = random_colors.generate(count=(20-quant_colors),format_='rgb',luminosity='random',hue='random')

    for i in cor:
        db.colors.insert(color=i,used=False)

# print '{} cores disponiveis'.format(quant_colors)