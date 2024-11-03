# Imports
import pickle
import networkx as nx
import numpy as np
import random


def save_with_pickle(file, directory, file_name):
    path = directory + file_name + '.pkl'
    with open(path, "wb") as f:
        pickle.dump(file, f)


def load_with_pickle(directory, file_name):
    path = directory + file_name + '.pkl'
    with open(path, "rb") as f:
        return pickle.load(f)


def inicializa_grafo(nos, porcentagem_adultos):
    # Criando o Grafo
    grafo = nx.Graph()

    # Escolhendo os nós que serão os adultos e crianças
    adultos = list(random.sample(list(nos), round(porcentagem_adultos * len(nos))))
    criancas = list(set(nos) - set(adultos))

    for i in adultos:
        grafo.add_node(i, classe="Adulto")

    for i in criancas:
        grafo.add_node(i, classe="Criança")
    return grafo


def cria_arestas(grafo, lista_nos, prob_criacao_arestas, nome_aresta, peso):
    # Cria arestas entre todos os nós da lista
    for i in range(len(lista_nos) - 1):
        for j in range(i + 1, len(lista_nos)):
            if random.random() < prob_criacao_arestas:
                if not grafo.has_edge(lista_nos[i], lista_nos[j]):
                    grafo.add_edge(lista_nos[i], lista_nos[j])
                nx.set_edge_attributes(grafo, {(lista_nos[i], lista_nos[j]): {nome_aresta: peso}})
    return grafo


def contabiliza_nos(grafo):
    adultos_nao_agrupados = []
    criancas_nao_agrupadas = []
    for i, j in grafo.nodes.items():
        if j['classe'] == "Adulto":
            adultos_nao_agrupados.append(i)
        else:
            criancas_nao_agrupadas.append(i)
    return adultos_nao_agrupados, criancas_nao_agrupadas


def separa_adultos(porc_tam_familia, populacao, adultos_nao_agrupados):
    total = 0
    for i, j in porc_tam_familia.items():
        total += round(j * populacao / int(i))
    adultos_separados = adultos_nao_agrupados[0:total]
    del adultos_nao_agrupados[0:total]
    return adultos_separados


def gera_camada_familia(grafo, porc_tam_familia, nome_aresta, peso):
    # Contabilização dos nós de cada classe
    adultos_nao_agrupados, criancas_nao_agrupadas = contabiliza_nos(grafo)

    # Separa 1 adulto para compor cada família
    populacao = len(adultos_nao_agrupados) + len(criancas_nao_agrupadas)
    adultos_separados = separa_adultos(porc_tam_familia, populacao, adultos_nao_agrupados)

    # Familias com 1 integrante
    solo = round(porc_tam_familia['1'] * populacao)
    del adultos_separados[0:solo]
    del porc_tam_familia['1']

    # Agrupando demais familias
    adultos_e_criancas = adultos_nao_agrupados + criancas_nao_agrupadas
    random.shuffle(adultos_e_criancas)
    tamanho = 2

    for i in porc_tam_familia.values():

        for _ in range(round((i * populacao) / tamanho)):
            aux = list()
            aux.append(adultos_separados.pop())

            for _ in range(tamanho - 1):
                # Como os valores são arredondados, pode faltar elemento, causando erro de remoção de lista vazia
                if len(adultos_e_criancas):
                    aux.append(adultos_e_criancas.pop())
            grafo = cria_arestas(grafo, aux, 1, nome_aresta, peso)
        tamanho += 1

    # Agrupa os nós que sobraram em um único conjunto
    if adultos_separados or adultos_e_criancas:
        grafo = cria_arestas(grafo, adultos_separados + adultos_e_criancas, 1, nome_aresta, peso)
    return grafo


def remove_elem(lista, list_elem_removidos):
    for i in list_elem_removidos:
        lista.remove(i)


def separa_nos(grafo, crit_agrup, valor_agrup):
    if valor_agrup == 'Todos':
        nos = []
        for i, j in grafo.nodes.items():
            nos.append(i)
        return nos
    else:
        nos = []
        for i, j in grafo.nodes.items():
            if j[crit_agrup] == valor_agrup:
                nos.append(i)
        return nos


def gera_camada(grafo, crit_agrup, valor_agrup, porc_agrup, lim_inf, lim_sup, prob_criacao_arestas, nome_aresta, peso):
    # Seleciona os nós
    nos = separa_nos(grafo, crit_agrup, valor_agrup)

    # Separa nós a serem utilizados
    total_nos_agrup = round(len(nos) * porc_agrup)
    nos_agrupamento = random.sample(nos, total_nos_agrup)

    while len(nos_agrupamento):

        # Tamanho randdômico dos agrupamentos
        tam_grupo = random.randint(lim_inf, lim_sup)

        if len(nos_agrupamento) > tam_grupo:
            grupo = random.sample(nos_agrupamento, tam_grupo)
            cria_arestas(grafo, grupo, prob_criacao_arestas, nome_aresta, peso)
            remove_elem(nos_agrupamento, grupo)

        else:
            cria_arestas(grafo, nos_agrupamento, prob_criacao_arestas, nome_aresta, peso)
            nos_agrupamento.clear()
    return grafo


def gera_camada_relacionamento(grafo, prob_criacao_arestas, nome_aresta, peso, dicionario):
    for i in dicionario.keys():
        for j in dicionario[i]:
            if random.random() <= prob_criacao_arestas:
                grafo.add_edge(i, j)
                nx.set_edge_attributes(grafo, {(i, j): {nome_aresta: peso}})
    return grafo


def gera_camada_mobilidade(grafo, nos, matriz_OD, porc_transporte, lim_inf, lim_sup, prob_criacao_arestas, nome_aresta,
                           peso):
    users_transporte_publico = random.sample(nos, int(len(nos) * porc_transporte))
    for key1 in matriz_OD.keys():
        for key2 in matriz_OD[key1].keys():
            elementos_comuns = list(set(users_transporte_publico) & set(matriz_OD[key1][key2]))
            while len(elementos_comuns):
                tam_grupo = random.randint(lim_inf, lim_sup)

                if len(elementos_comuns) > tam_grupo:
                    grupo = random.sample(elementos_comuns, tam_grupo)
                    cria_arestas(grafo, grupo, prob_criacao_arestas, nome_aresta, peso)
                    remove_elem(elementos_comuns, grupo)

                else:
                    if len(elementos_comuns) > lim_inf:
                        cria_arestas(grafo, elementos_comuns, prob_criacao_arestas, nome_aresta, peso)
                    elementos_comuns.clear()
    return grafo


"""def gera_camada_mobilidade(grafo, prob_criacao_arestas, nome_aresta, peso, dicionario):
    for antena in dicionario.keys():
        cria_arestas(grafo, dicionario[antena], prob_criacao_arestas, nome_aresta, peso)
    print("Fim mobilidade")
    return grafo"""


def soma_pesos(grafo):
    for i, j, k in grafo.edges.data():
        nx.set_edge_attributes(grafo, {(i, j): {'Total': round(sum(k.values()), 2)}})
        edge_data = grafo.get_edge_data(i, j)
    return grafo


def main():
    AMOSTRAGEM = False

    # Lendo os objetos Pickles
    if AMOSTRAGEM:
        nos = list(load_with_pickle('../Pickles/Amostragem/', 'amostragem_nos'))
        users = load_with_pickle('../Pickles/Amostragem/', 'dict_dados')
        matriz_OD = load_with_pickle('../Pickles/Amostragem/', 'matriz_OD')
    else:
        nos = list(load_with_pickle('../Pickles/Dados Completos/', 'nos'))
        users = load_with_pickle('../Pickles/Dados Completos/', 'dict_dados')
        matriz_OD = load_with_pickle('../Pickles/Dados Completos/', 'matriz_OD')

    porc_tam_familia = {'1': 0.12, '2': 0.22, '3': 0.25, '4': 0.21, '5': 0.11,
                        '6': 0.05, '7': 0.02, '8': 0.01, '9': 0.005, '10': 0.005}

    print(f'Quantidade de nós: {len(nos)}')
    print(f'Quantidade de locais de residência: {len(matriz_OD.keys())}')

    # Inicializando o Grafo
    grafo = inicializa_grafo(nos, 0.76)

    # Camada Família
    grafo = gera_camada_familia(grafo, porc_tam_familia, 'Família', 0.125)
    print("Camada Família Finalizada!")

    # Camada Trabalho
    grafo = gera_camada(grafo, 'classe', 'Adulto', 1, 5, 30, 0.05, 'Trabalho', 0.238)
    print("Camada Trabalho Finalizada!")

    # Camada Escola
    grafo = gera_camada(grafo, 'classe', 'Criança', 0.6, 16, 30, 0.05, 'Escola', 0.12)
    print("Camada Escola Finalizada!")

    # Camada Religião
    grafo = gera_camada(grafo, 'classe', 'Todos', 0.4, 10, 100, 0.01, 'Religião', 0.01)
    print("Camada Religião Finalizada!")

    # Camada Aleatória
    grafo = gera_camada(grafo, 'classe', 'Todos', 1, 2, 2, 1, 'Aleatória', 0.006)
    print("Camada Aleatória Finalizada!")

    # Camada Relacionamentos
    grafo = gera_camada_relacionamento(grafo, 1, 'Relacionamento', 0.08, users)
    print("Camada Relacionamentos Finalizada!")

    # Camada de Mobilidade Urbana (Matriz Origem-Destino)
    grafo = gera_camada_mobilidade(grafo, nos, matriz_OD, 0.5, 10, 30, 0.05, 'Mobilidade OD', 0.04)
    print("Camada Mobilidade Finalizada!")

    # Camada Mobilidade
    # grafo = gera_camada_mobilidade(grafo, 0.01, 'Mobilidade', 0.15, dict_mobil)

    grafo = soma_pesos(grafo)
    nx.write_graphml(grafo, "rede_uberlandia.graphml")


if __name__ == '__main__':
    main()
