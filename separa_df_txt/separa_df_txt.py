def separa_df_txt(df):
    for artigo in df.loc[:,['sigla','nome_jornal','termo_de_busca', 'artigo']].reset_index().values:
        df.drop(['artigo'], axis=1).to_csv(f'./values/{artigo[1]}_{artigo[2]}_{artigo[3].lower()}.csv')
        break
        
    for artigo in df.loc[:,['sigla','nome_jornal','termo_de_busca', 'artigo']].reset_index().values:
        texto = artigo[4]

        
        with open(f'./data/{artigo[0]}_{artigo[1]}_{str(artigo[2]).replace(" ", "_")}_{artigo[3]}.txt', 'a', encoding='utf-8', errors='ignore') as artigo:
            
            artigo.write(f"{texto}")