## -------------------------- Imports -------------------------- ##

import psycopg2
import pandas as pd

from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
from urllib.parse import urlparse

from tabulate import tabulate
import pandas as pd
from telegram.constants import ParseMode

## -------------------------- Conexão DB -------------------------- ##
database_url = "postgresql://db_bot_medicacaov2_xi9p_user:Kn3Irb9oGJnmVrXv3xYd6JIKHvdDIxMF@dpg-cu5u2ld2ng1s73bk49og-a/db_bot_medicacaov2_xi9p"

url = urlparse(database_url)

conn = psycopg2.connect(
    dbname=url.path[1:],  
    user=url.username,     
    password=url.password, 
    host=url.hostname,     
    port=url.port          
)

cursor = conn.cursor()

## -------------------------- 1.0 Funções basicas -------------------------- ##
# função responsavel pelo /start do bot e para mostrar as primeiras opcoes para o usuario
async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Olá! Escolha uma opção:\n1 - Consultar\n2 - Adicionar\n3 - Deletar\n4 - Sair')
    return 0  

# função responsavel por receber a opcao escolhida pelo usuario e direcionar para as diferentes possibilidades
# consultar, adicionar, deletar ou sair do bot
async def handle_menu(update: Update, context: CallbackContext) -> int:
    user_choice = update.message.text.strip()

    if user_choice == '1':  # Opcao de consulta
        return await consultar(update, context)

    elif user_choice == '2':  # Opcao de adicionar
        return await adicionar(update, context)

    elif user_choice == '3': # Opcao de deletar
        return await deletar(update, context)

    elif user_choice == '4':  # Opcao de Sair
        await update.message.reply_text('Até logo!')
        return await voltar(update, context)
    else:
        await update.message.reply_text('Opção inválida. Por favor, escolha novamente.')
        return 0  # Retorna para essa funcao novamente

## -------------------------- 2. Direcionamento do fluxo -------------------------- ##

async def consultar(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Escolha uma opção de Consulta:\n1 - Pacientes\n2 - Cuidadores\n3 - Remédios\n4 - Horários de Remédios\n5 - Voltar')
    return 1  # Direciona para as opcoes de consulta

async def adicionar(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Escolha uma opção de Adicionar:\n1 - Paciente\n2 - Cuidador\n3 - Remédio\n4 - Horário de Remédios\n5 - Voltar')
    return 2  # Direciona para as opcoes de adicionar

async def deletar(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Escolha uma opção de Deletar:\n1 - Paciente\n2 - Cuidador\n3 - Remédio\n4 - Horário de Remédios\n5 - Voltar')
    return 3  # Direciona para as opcoes de deletar

async def voltar(update: Update, context: CallbackContext) -> int:
    return await start(update, context)  # Volta ao menu principal e reinicia a conversa

## -------------------------- 3. Parte de consulta -------------------------- ##

async def consulta_opcao(update: Update, context: CallbackContext) -> int:

    if not update.message:
        return 0  # Se a mensagem for None, volta ao menu inicial
    
    opcao = update.message.text
    if opcao == '1':  # Opcao para Consultar Paciente
        await update.message.reply_text('Digite o nome do Paciente (ou todos):') # Responsavel por exibir a mensagem ao usuario para receber input
        return 4  # Direciona para a funcao 4 (consulta_nome_paciente)

    elif opcao == '2':  # Opcao para Consultar Cuidador
        await update.message.reply_text('Digite o nome do Cuidador (ou todos):') # Responsavel por exibir a mensagem ao usuario para receber input
        return 5  # Direciona para a funcao 5 (consulta_nome_cuidador)
    
    elif opcao == '3':  # Opcao para Consultar Remedio
        await update.message.reply_text('Digite o nome do Remédio (ou todos):') # Responsavel por exibir a mensagem ao usuario para receber input
        return 6 # Direciona para a funcao 6 (consulta_nome_remedio)

    elif opcao == '4':  # Opcao para Consultar Horários de Remédios
        await update.message.reply_text('Digite o nome do Paciente ou do Cuidador (ou todos):') # Responsavel por exibir a mensagem ao usuario para receber input
        return 7 # Direciona para a funcao 7 (consulta_horario_remedio)
        
    elif opcao == '5':  # Opção para Voltar
        return await voltar(update, context)  # Chama a funcao para retornar ao menu principal
    else:
        await update.message.reply_text("Opção inválida. Tente novamente.")
        return await voltar(update, context)  # Chama a funcao para retornar ao menu principal

# -------------------- 3.1 Consulta paciente -------------------- #
async def consulta_nome_paciente(update: Update, context: CallbackContext) -> int:
    # Recebe o input do usuario do nome do paciente desejado para consulta
    nome_paciente = update.message.text.strip()

    # Se o nome for todos exibe todos os pacientes cadastrados na base
    if nome_paciente == 'todos':
        cursor.execute("SELECT * FROM paciente")

    # Se nao for todos exibe os que tiverem a correspondencia do nome escrito
    else:    
        cursor.execute("SELECT * FROM paciente WHERE lower(nome_paciente) LIKE %s;", (f"%{nome_paciente.lower()}%",))
    
    # Recupera os dados da consulta
    pacientes = cursor.fetchall()

    # Se a consulta voltar vazia exibe uma mensagem para o usuario relatando que nao tem paciente cadastrado com esse nome
    if not pacientes:
        await update.message.reply_text(f"Nenhum paciente encontrado com o nome {nome_paciente}.")

    # Se a consulta nao voltar vazia formata a consulta e exibe a mensagem para o usuario  
    else:
        response = ""
        for row in pacientes:
            response += f"ID: {row[0]}\n"
            response += f"Nome: {row[1]}\n"
            response += f"Idade: {row[2]}\n"
            response += f"Documento de Identificação: {row[3]}\n"
            response += f"Telefone: {row[4] if row[4] else 'Não informado'}\n\n"

        # Exibe a mensagem para o usuario conforme a formatacao realizada
        await update.message.reply_text(response)

    # Exibe mensagem e volta para menu principal
    await update.message.reply_text('Voltando ao menu principal...')
    return await voltar(update, context)  

# -------------------- 3.2 Consulta cuidador -------------------- #
async def consulta_nome_cuidador(update: Update, context: CallbackContext) -> int:
    # Recebe o input do usuario do nome do cuidador desejado para consulta
    nome_cuidador = update.message.text.strip()

    # Se o nome for todos exibe todos os cuidadores cadastrados na base
    if nome_cuidador == 'todos':
        cursor.execute("SELECT * FROM cuidador")
    
    # Se nao for todos exibe os que tiverem a correspondencia do nome escrito
    else:
        cursor.execute("SELECT * FROM cuidador WHERE lower(nome_cuidador) LIKE %s;", (f"%{nome_cuidador.lower()}%",))
    
    # Recupera os dados da consulta
    cuidador = cursor.fetchall()

    # Se a consulta voltar vazia exibe uma mensagem para o usuario relatando que nao tem cuidador cadastrado com esse nome
    if not cuidador:
        await update.message.reply_text(f"Nenhum cuidador encontrado com o nome {nome_cuidador}.")
    
    # Se a consulta nao voltar vazia formata a consulta e exibe a mensagem para o usuario  
    else:
        response = ""
        for row in cuidador:
            response += f"ID: {row[0]}\n"
            response += f"Nome: {row[1]}\n"
            response += f"Documento de Identificação: {row[2]}\n"
            response += f"Telefone: {row[3] if row[3] else 'Não informado'}\n\n"

        # Exibe a mensagem para o usuario conforme a formatacao realizada
        await update.message.reply_text(response)

    # Exibe mensagem e volta para menu principal
    await update.message.reply_text('Voltando ao menu principal...')
    return await voltar(update, context) 

# -------------------- 3.3 Consulta remedio -------------------- #
async def consulta_nome_remedio(update: Update, context: CallbackContext) -> int:
    # Recebe o input do usuario do nome do remedio desejado para consulta
    nome_remedio = update.message.text.strip()

    # Se o nome for todos exibe todos os remedios cadastrados na base
    if nome_remedio == 'todos':
        cursor.execute("SELECT * FROM remedio")
    
    # Se nao for todos exibe os que tiverem a correspondencia do nome escrito
    else:
        cursor.execute("SELECT * FROM remedio WHERE lower(nome_remedio) LIKE %s;", (f"%{nome_remedio.lower()}%",))
    
    # Recupera os dados da consulta
    remedio = cursor.fetchall()

    # Se a consulta voltar vazia exibe uma mensagem para o usuario relatando que nao tem remedio cadastrado com esse nome
    if not remedio:
        await update.message.reply_text(f"Nenhum remedio encontrado com o nome {nome_remedio}.")

    # Se a consulta nao voltar vazia formata a consulta e exibe a mensagem para o usuario  
    else:
        response = ""
        for row in remedio:
            
            response += f"ID: {row[0]}\n"
            response += f"Nome: {row[1]}\n"
            response += f"Dosagem: {row[2]}\n"
            response += f"Tipo: {row[3]}\n\n"

        # Exibe a mensagem para o usuario conforme a formatacao realizada
        await update.message.reply_text(response)

    # Exibe mensagem e volta para menu principal
    await update.message.reply_text('Voltando ao menu principal...')
    return await voltar(update, context)  # Chama a funcao para retornar ao menu principal

# -------------------- 3.4 Consulta Horario de Remedio -------------------- #
async def consulta_horario_remedio(update: Update, context: CallbackContext) -> int:
    # Recebe o input do usuario do nome do paciente ou cuidador desejado para consulta
    nome_paciente_cuidador = update.message.text.strip()

    # Se o nome for todos exibe todos os horarios cadastrados na base
    if nome_paciente_cuidador == 'todos':
        cursor.execute("SELECT p.nome_paciente, c.nome_cuidador, r.nome_remedio, r.dosagem, r.tipo, h.data_inicio, h.data_fim, h.hora FROM horario_remedios h JOIN paciente p ON h.id_paciente = p.id_paciente JOIN cuidador c ON h.id_cuidador = c.id_cuidador JOIN remedio r ON h.id_remedio = r.id_remedio")
    
    # Se nao for todos exibe os que tiverem a correspondencia do nome do paciente ou cuidador
    else:
        cursor.execute("SELECT p.nome_paciente, c.nome_cuidador, r.nome_remedio, r.dosagem, r.tipo, h.data_inicio, h.data_fim, h.hora FROM horario_remedios h JOIN paciente p ON h.id_paciente = p.id_paciente JOIN cuidador c ON h.id_cuidador = c.id_cuidador JOIN remedio r ON h.id_remedio = r.id_remedio WHERE (lower(nome_paciente) LIKE %s) OR (lower(nome_cuidador) LIKE %s);", (f"%{nome_paciente_cuidador.lower()}%", f"%{nome_paciente_cuidador.lower()}%"))
    
    # Recupera os dados da consulta
    paciente_cuidador = cursor.fetchall()

    # Se a consulta voltar vazia exibe uma mensagem para o usuario relatando que o paciente/cuidador nao tem horario de remedio cadastrado
    if not paciente_cuidador:
       
        await update.message.reply_text(f"O paciente/cuidador {nome_paciente_cuidador} não tem horário de remédio cadastrado.")
    
    # Se a consulta nao voltar vazia formata a consulta e exibe a mensagem para o usuario  
    else:
        response = ""
        for row in paciente_cuidador:
            response += f"Nome Paciente: {row[0]}\n"
            response += f"Nome Cuidador: {row[1]}\n"
            response += f"Nome Remédio: {row[2]}\n"
            response += f"Dosagem: {row[3]}\n\n"
            response += f"Tipo: {row[4]}\n\n"
            response += f"Data Inicio: {row[5]}\n\n"
            response += f"Data Fim: {row[6]}\n\n"
            response += f"Hora: {row[7]}\n\n"

        # Exibe a mensagem para o usuario conforme a formatacao realizada
        await update.message.reply_text(response)

    # Exibe mensagem e volta para menu principal
    await update.message.reply_text('Voltando ao menu principal...')
    return await voltar(update, context)  

## ------------------- 4. Parte de Adicionar ----------------------------- ##
async def adicionar_opcao(update: Update, context: CallbackContext) -> int:
    # Recebe o input do usuario de qual quer adicionar
    opcao = update.message.text

    if opcao == '1':  # Opcao para Adicionar Paciente
        await update.message.reply_text("Digite o nome do paciente:")
        return 11  # Redireciona para a funcao 11 (adicionar_paciente_nome)

    elif opcao == '2':  # Opcao para Adicionar Cuidador
        await update.message.reply_text("Digite o nome do cuidador:")
        return 15  # Redireciona para a funcao 15 (adicionar_cuidador_nome)

    elif opcao == '3':  # Opcao para Adicionar Remedio
        await update.message.reply_text("Digite o nome do remédio:")
        return 18  # Redireciona para a funcao 18 (adicionar_remedio_nome)

    elif opcao == '4':  # Opcao para Adicionar Horario
        # Consulta todos os pacientes para poder dar opcoes para o usuario
        cursor.execute("SELECT * FROM paciente")
        pacientes = cursor.fetchall()

        # Se a consulta voltar vazia exibe uma mensagem para o usuario relatando que nao tem paciente cadastrado
        if not pacientes:
            await update.message.reply_text(f"Nenhum paciente encontrado.")
            return await voltar(update, context)  # Volta para o início
        
        # Se a consulta nao voltar vazia formata a consulta e exibe a mensagem para o usuario  
        else:
            response = ""
            for row in pacientes:
                # Acessando os valores da tupla pelos índices
                response += f"ID: {row[0]}\n"
                response += f"Nome: {row[1]}\n"
                response += f"Idade: {row[2]}\n"
                response += f"Documento de Identificação: {row[3]}\n"
                response += f"Telefone: {row[4] if row[4] else 'Não informado'}\n\n"

        # Exibe a mensagem para o usuario conforme a formatacao realizada
        await update.message.reply_text(response)
        await update.message.reply_text("Digite o ID do paciente:")
        return 21 # Redireciona para a funcao 21 (adicionar_horario_id_paciente)

    elif opcao == '5':  # Opcao para voltar
        # Exibe mensagem e volta para menu principal
        await update.message.reply_text('Voltando ao menu principal...')
        return await voltar(update, context)  

# -------------------- 4.1.1 Adicionar Paciente  -------------------- #
import logging

# Configuração do logging
logging.basicConfig(level=logging.DEBUG)

# -------------------- 4.1.1 Adicionar Nome do Paciente  -------------------- #
async def adicionar_paciente_nome(update: Update, context: CallbackContext) -> int:
    # Recebe o input do usuario do nome do paciente desejado para adicionar
    nome = update.message.text.strip()
    context.user_data["nome_paciente"] = nome  # Armazena o nome 
    logging.debug(f"Nome do paciente: {nome}")

    # Solicita o input do usuario da idade do paciente para adicionar
    await update.message.reply_text("Digite a idade do paciente:")
    return 12  # Redireciona para a funcao 12 (adicionar_paciente_idade)

# -------------------- 4.1.2 Adicionar Idade do Paciente  -------------------- #
async def adicionar_paciente_idade(update: Update, context: CallbackContext) -> int:
    # Recebe o input do usuario da idade do paciente para adicionar
    try:
        idade = int(update.message.text.strip())
        context.user_data["idade"] = idade  # Armazena a idade 
        logging.debug(f"Idade do paciente: {idade}")

        # Solicita o input do usuario do documento de identificacao do paciente para adicionar
        await update.message.reply_text("Digite o documento de identificação do paciente:")
        return 13  # Redireciona para a funcao 13 (adicionar_paciente_documento)
    except ValueError:
        await update.message.reply_text("Por favor, insira uma idade válida (apenas números).")
        return 11  # Redireciona para a funcao 11 para solicitar o input novamente da idade (adicionar_paciente_nome)

# -------------------- 4.1.3 Adicionar Documento do Paciente  -------------------- #
async def adicionar_paciente_documento(update: Update, context: CallbackContext) -> int:
    # Recebe o input do usuario do documento do paciente para adicionar
    documento = update.message.text.strip()
    context.user_data["documento_paciente"] = documento  # Armazena o documento

    # Solicita o input do usuario do telefone de um parente do paciente para adicionar
    await update.message.reply_text("Digite o telefone de um parente (opcional, ou digite 'PULAR'):")
    return 14  # Redireciona para a funcao 14 (adicionar_paciente_telefone)

# -------------------- 4.1.4 Adicionar Telefone do Paciente  -------------------- #
async def adicionar_paciente_telefone(update: Update, context: CallbackContext) -> int:
    # Recebe o input do usuario do telefone do parente do paciente para adicionar
    telefone = update.message.text.strip()

    # Se o input for pular define como None
    if telefone.lower() == "pular":
        telefone = None  # Define telefone como None se for opcional

    context.user_data["telefone_parente"] = telefone  # Armazena o telefone 
    logging.debug(f"Telefone do parente: {telefone}")

    # Insere o paciente no banco de dados apenas após coletar todos os dados
    cursor.execute(""" 
        INSERT INTO paciente (nome_paciente, idade, documento_identificacao, telefone_parente)
        VALUES (%s, %s, %s, %s) RETURNING id_paciente;
    """, (context.user_data["nome_paciente"], context.user_data["idade"], context.user_data["documento_paciente"], telefone))
    paciente_id = cursor.fetchone()[0]
    conn.commit()

    # Exibe mensagem e volta para menu principal
    await update.message.reply_text(f"Paciente {context.user_data['nome_paciente']} adicionado com sucesso! ID: {paciente_id}")
    return await voltar(update, context)  

# -------------------- 4.2 Adicionar Cuidador  -------------------- #

# -------------------- 4.2.1 Adicionar Nome do Cuidador  -------------------- #
async def adicionar_cuidador_nome(update: Update, context: CallbackContext) -> int:
    # Recebe o input do usuario do nome do cuidador desejado para adicionar
    nome = update.message.text.strip()
    context.user_data["nome_cuidador"] = nome  # Armazena o nome 
    logging.debug(f"Nome do cuidador: {nome}")

    # Solicita o input do usuario do documento do cuidador para adicionar
    await update.message.reply_text("Digite o documento de identificacao do cuidador:")
    return 16  # Redireciona para a funcao 16 (adicionar_cuidador_documento)

# -------------------- 4.2.2 Adicionar Documento do Cuidador  -------------------- #
async def adicionar_cuidador_documento(update: Update, context: CallbackContext) -> int:

    # Recebe o input do usuario do documento do cuidador desejado para adicionar
    documento = update.message.text.strip()
    context.user_data["documento_identificacao"] = documento  # Armazena o documento 

    logging.debug(f"Documento do cuidador: {documento}")

    # Solicita o input do usuario do telefone do cuidador para adicionar
    await update.message.reply_text("Digite o telefone do cuidador (obrigatório):")
    return 17  # Redireciona para a funcao 16 (adicionar_cuidador_telefone)

# -------------------- 4.2.3 Adicionar Telefone do Cuidador  -------------------- #
async def adicionar_cuidador_telefone(update: Update, context: CallbackContext) -> int:
    # Recebe o input do usuario do telefone do cuidador desejado para adicionar
    telefone = update.message.text.strip()

    context.user_data["telefone"] = telefone  # Armazena o telefone
    logging.debug(f"Telefone do cuidador: {telefone}")

    # Insere o cuidador no banco de dados apenas após coletar todos os dados
    cursor.execute(""" 
        INSERT INTO cuidador (nome_cuidador, documento_identificacao, telefone)
        VALUES (%s, %s, %s) RETURNING id_cuidador;
    """, (context.user_data["nome_cuidador"], context.user_data["documento_identificacao"], telefone))
    id_cuidador = cursor.fetchone()[0]
    conn.commit()

    logging.debug(f"Cuidador inserido com ID: {id_cuidador}")

    # Exibe mensagem e volta para menu principal
    await update.message.reply_text(f"Cuidador {context.user_data['nome_cuidador']} adicionado com sucesso! ID: {id_cuidador}")
    return await voltar(update, context)  


# -------------------- 4.3 Adicionar Remedio  -------------------- #
# -------------------- 4.3.1 Adicionar Nome do Remedio  -------------------- #
async def adicionar_remedio_nome(update: Update, context: CallbackContext) -> int:
    # Recebe o input do usuario do nome do remedio desejado para adicionar
    nome = update.message.text.strip()
    context.user_data["nome_remedio"] = nome  # Armazena o nome
    logging.debug(f"Nome do remedio: {nome}")

    # Solicita o input do usuario da dosagem do remedio para adicionar
    await update.message.reply_text("Digite a dosagem remedio:")
    return 19  # Redireciona para a funcao 19 (adicionar_remedio_dosagem)

# -------------------- 4.3.2 Adicionar Dosagem do Remedio  -------------------- #
async def adicionar_remedio_dosagem(update: Update, context: CallbackContext) -> int:
    # Recebe o input do usuario da dosagem do remedio desejado para adicionar
    dosagem = update.message.text.strip()
    context.user_data["dosagem"] = dosagem  # Armazena o dosagem no contexto
    logging.debug(f"Dosagem do remedio: {dosagem}")
    
    # Solicita o input do usuario do tipo do remedio para adicionar
    await update.message.reply_text("Digite o tipo do remédio:")
    return 20  # Redireciona para a funcao 20 (adicionar_remedio_tipo)

# -------------------- 4.3.3 Adicionar Tipo do Remedio  -------------------- #

async def adicionar_remedio_tipo(update: Update, context: CallbackContext) -> int:

    # Recebe o input do usuario do tipo do remedio desejado para adicionar
    tipo = update.message.text.strip()
    context.user_data["tipo"] = tipo  # Armazena o tipo no contexto
    logging.debug(f"tipo do remedio: {tipo}")

    # Insere o remedio no banco de dados apenas após coletar todos os dados
    cursor.execute(""" 
        INSERT INTO remedio (nome_remedio, dosagem, tipo)
        VALUES (%s, %s, %s) RETURNING id_remedio;
    """, (context.user_data["nome_remedio"], context.user_data["dosagem"], tipo))
    id_remedio = cursor.fetchone()[0]
    conn.commit()

    logging.debug(f"remedio inserido com ID: {id_remedio}")

    # Exibe mensagem e volta para menu principal
    await update.message.reply_text(f"remedio {context.user_data['nome_remedio']} adicionado com sucesso! ID: {id_remedio}")
    return await voltar(update, context)  # Retorna ao menu principal

## -------------------- 4.4 Adicionar Horario de Remedio  -------------------- ##
# -------------------- 4.4.1 Adicionar Id do Paciente  -------------------- #
async def adicionar_horario_id_paciente(update: Update, context: CallbackContext) -> int:
    # Recebe o input do usuario do id do paciente desejado para adicionar
    id_paciente = update.message.text.strip()
    context.user_data["id_paciente"] = id_paciente  # Armazena o id do paciente
    logging.debug(f"Id Paciente: {id_paciente}")

    # Consulta todos os cuidadores para poder dar opcoes para o usuario
    cursor.execute("SELECT * FROM cuidador")
    cuidador = cursor.fetchall()

    # Se a consulta voltar vazia exibe uma mensagem para o usuario relatando que nao tem cuidador cadastrado
    if not cuidador:
        await update.message.reply_text(f"Nenhum cuidador encontrado.")
        return await voltar(update, context)  # Volta para o início

    # Se a consulta nao voltar vazia formata a consulta e exibe a mensagem para o usuario  
    else:
        response = ""
        for row in cuidador:
            response += f"ID: {row[0]}\n"
            response += f"Nome: {row[1]}\n"
            response += f"Documento de Identificação: {row[2]}\n"
            response += f"Telefone: {row[3]}\n\n"

    # Exibe a mensagem para o usuario conforme a formatacao realizada
    await update.message.reply_text(response)

    await update.message.reply_text("Digite o id do cuidador:")
    return 22  # Redireciona para a funcao 22 (adicionar_horario_id_cuidador)

# -------------------- 4.4.2 Adicionar Id do Cuidador  -------------------- #
async def adicionar_horario_id_cuidador(update: Update, context: CallbackContext) -> int:
    # Recebe o input do usuario do id do cuidador desejado para adicionar
    id_cuidador = update.message.text.strip()
    context.user_data["id_cuidador"] = id_cuidador  # Armazena o id do cuidador
    logging.debug(f"Id Paciente: {id_cuidador}")

    # Consulta todos os remedios para poder dar opcoes para o usuario
    cursor.execute("SELECT * FROM remedio")
    remedio = cursor.fetchall()

    # Se a consulta voltar vazia exibe uma mensagem para o usuario relatando que nao tem remedio cadastrado
    if not remedio:
        await update.message.reply_text(f"Nenhum remédio encontrado.")
        return await voltar(update, context)  # Volta para o início

    # Se a consulta nao voltar vazia formata a consulta e exibe a mensagem para o usuario  
    else:
        response = ""
        for row in remedio:
                # Acessando os valores da tupla pelos índices
            response += f"ID: {row[0]}\n"
            response += f"Nome: {row[1]}\n"
            response += f"Dosagem: {row[2]}\n"
            response += f"Tipo: {row[3]}\n\n"

    # Exibe a mensagem para o usuario conforme a formatacao realizada
    await update.message.reply_text(response)

    await update.message.reply_text("Digite o id do remédio:")
    return 23  # Redireciona para a funcao 23 (adicionar_horario_id_remedio)

# -------------------- 4.4.3 Adicionar Id do Remedio  -------------------- #
async def adicionar_horario_id_remedio(update: Update, context: CallbackContext) -> int:
    # Recebe o input do usuario do id do remedio desejado para adicionar
    id_remedio = update.message.text.strip()
    context.user_data["id_remedio"] = id_remedio  # Armazena o id do remedio 
    logging.debug(f"id_remedio do remedio: {id_remedio}")

    # Solicita o input do usuario da data inicio do remedio
    await update.message.reply_text("Digite a data ínicio do remédio: (Formato dd/MM/AAAA)")
    return 24  # Redireciona para a funcao 24 (adicionar_horario_data_inicio)

# -------------------- 4.4.4 Adicionar Data Inicio  -------------------- #
async def adicionar_horario_data_inicio(update: Update, context: CallbackContext) -> int:
    # Recebe o input data inicio desejada para adicionar e faz a formatacao conforme padroes do database
    data_inicio = update.message.text.strip()
    data_inicio_iso = datetime.strptime(data_inicio, "%d/%m/%Y").strftime("%Y-%m-%d")

    context.user_data["data_inicio"] = data_inicio_iso  # Armazena a data inicio

    logging.debug(f"data_inicio do remedio: {data_inicio}")
    # Solicita o input do usuario da data fim do remedio
    await update.message.reply_text("Digite a data fim do remédio: (Formato dd/MM/AAAA)")
    return 25 # Redireciona para a funcao 25 (adicionar_horario_data_fim)

# -------------------- 4.4.5 Adicionar Data Fim  -------------------- #
async def adicionar_horario_data_fim(update: Update, context: CallbackContext) -> int:
    # Recebe o input data fim desejada para adicionar e faz a formatacao conforme padroes do database
    data_fim = update.message.text.strip()
    data_fim_iso = datetime.strptime(data_fim, "%d/%m/%Y").strftime("%Y-%m-%d")
    context.user_data["data_fim"] = data_fim_iso  # Armazena a data fim
    logging.debug(f"data_fim do remedio: {data_fim}")

    # Solicita o input do usuario da hora do remedio
    await update.message.reply_text("Digite o horário: (08:00 ou 20:00)")
    return 26 # Redireciona para a funcao 26 (adicionar_horario_horario)

# -------------------- 4.4.6 Adicionar Hora  -------------------- #

async def adicionar_horario_horario(update: Update, context: CallbackContext) -> int:
    # Recebe o input da hora desejada para adicionar e faz a formatacao conforme padroes do database
    horario = update.message.text.strip()
    horario_iso = datetime.strptime(horario, "%H:%M").strftime("%H:%M:%S")
    context.user_data["horario"] = horario_iso  # Armazena o horario
    logging.debug(f"horario do remedio: {horario}")

    # Insere o remedio no banco de dados apenas após coletar todos os dados
    cursor.execute(""" 
        INSERT INTO horario_remedios (id_paciente, id_cuidador, id_remedio, data_inicio, data_fim, hora)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_remedio;
    """, (context.user_data["id_paciente"], context.user_data["id_cuidador"], context.user_data["id_remedio"], context.user_data["data_inicio"], context.user_data["data_fim"], context.user_data["horario"]))
    id_remedio = cursor.fetchone()[0]
    conn.commit()

    await update.message.reply_text("Horário inserido com sucesso")
    return await voltar(update, context)  # Retorna ao menu principal

## -------------------- 5. Deletar -------------------- ##

async def deletar_opcao(update: Update, context: CallbackContext) -> int:
    opcao = update.message.text
    if opcao == '1':  # Deletar Paciente
        # Consulta todos os pacientes para poder dar opcoes para o usuario
        cursor.execute("SELECT * FROM paciente")
        paciente = cursor.fetchall()

        # Se a consulta voltar vazia exibe uma mensagem para o usuario relatando que nao tem paciente cadastrado
        if not paciente:
            await update.message.reply_text(f"Nenhum paciente encontrado.")
            return await voltar(update, context)  # Volta para o início

        # Se a consulta nao voltar vazia formata a consulta e exibe a mensagem para o usuario  
        else:
            response = ""
            for row in paciente:
                response += f"ID: {row[0]}\n"
                response += f"Nome: {row[1]}\n"
                response += f"Idade: {row[2]}\n"
                response += f"Documento de Identificacao: {row[3]}\n"
                response += f"Telefone Parente: {row[4]}\n\n"
        
        # Exibe a mensagem para o usuario conforme a formatacao realizada
        await update.message.reply_text(response)

        await update.message.reply_text("Digite o ID do paciente a ser deletado:")
        return 27  # Redireciona para a funcao 27 (deletar_paciente)

    elif opcao == '2':  # Deletar Cuidador
        # Consulta todos os cuidadores para poder dar opcoes para o usuario
        cursor.execute("SELECT * FROM cuidador")
        cuidador = cursor.fetchall()

        # Se a consulta voltar vazia exibe uma mensagem para o usuario relatando que nao tem cuidador cadastrado
        if not cuidador:
            await update.message.reply_text(f"Nenhum cuidador encontrado.")
            return await voltar(update, context)  # Volta para o início

        # Se a consulta nao voltar vazia formata a consulta e exibe a mensagem para o usuario  
        else:
            response = ""
            for row in cuidador:
                response += f"ID: {row[0]}\n"
                response += f"Nome: {row[1]}\n"
                response += f"Documento de Identificacao: {row[2]}\n"
                response += f"Telefone: {row[3]}\n\n"
        
        # Exibe a mensagem para o usuario conforme a formatacao realizada
        await update.message.reply_text(response)

        await update.message.reply_text("Digite o ID do cuidador a ser deletado:")
        return 28  # Redireciona para a funcao 28 (deletar_cuidador)

    elif opcao == '3':  # Deletar Remédio
        # Consulta todos os remedios para poder dar opcoes para o usuario
        cursor.execute("SELECT * FROM remedio")
        remedio = cursor.fetchall()

        # Se a consulta voltar vazia exibe uma mensagem para o usuario relatando que nao tem remedio cadastrado
        if not remedio:
            await update.message.reply_text(f"Nenhum remedio encontrado.")
            return await voltar(update, context)  # Volta para o início

        # Se a consulta nao voltar vazia formata a consulta e exibe a mensagem para o usuario  
        else:
            response = ""
            for row in remedio:
                    # Acessando os valores da tupla pelos índices
                response += f"ID: {row[0]}\n"
                response += f"Nome: {row[1]}\n"
                response += f"Dosagem: {row[2]}\n"
                response += f"Tipo: {row[3]}\n\n"
        
        # Exibe a mensagem para o usuario conforme a formatacao realizada
        await update.message.reply_text(response)

        await update.message.reply_text("Digite o ID do remédio a ser deletado:")
        return 29  # Redireciona para a funcao 29 (deletar_remedio)

    elif opcao == '4':  # Deletar Horário de Remédio
        # Consulta todos os pacientes para poder dar opcoes para o usuario
        cursor.execute("SELECT * FROM paciente")
        paciente = cursor.fetchall()

        # Se a consulta voltar vazia exibe uma mensagem para o usuario relatando que nao tem paciente cadastrado
        if not paciente:
            await update.message.reply_text(f"Nenhum paciente encontrado.")
            return await voltar(update, context)  # Volta para o início

        # Se a consulta nao voltar vazia formata a consulta e exibe a mensagem para o usuario  
        else:
            response = ""
            for row in paciente:
                response += f"ID: {row[0]}\n"
                response += f"Nome: {row[1]}\n"
                response += f"Idade: {row[2]}\n"
                response += f"Documento de Identificacao: {row[3]}\n"
                response += f"Telefone Parente: {row[4]}\n\n"
        
        # Exibe a mensagem para o usuario conforme a formatacao realizada
        await update.message.reply_text(response)

        await update.message.reply_text("Digite o ID do paciente:")
        return 30  # Redireciona para a funcao 30 (deletar_horario_id_paciente)
    
    elif opcao == '5':  # Voltar
        await update.message.reply_text('Voltando...')
        await start(update, context)
        return await voltar(update, context)  # Volta para o início

# -------------------- 5.1 Deletar paciente  -------------------- #
async def deletar_paciente(update: Update, context: CallbackContext) -> int:

    # Recebe o input do usuario do id do paciente desejado para deletar
    id_paciente_deletar = update.message.text.strip()

    # Deleta o paciente no banco de dados de paciente e todos os horarios de remedio associados 
    try:
        cursor.execute(f"DELETE FROM horario_remedios WHERE id_paciente = {id_paciente_deletar}")
        cursor.execute(f"DELETE FROM paciente WHERE id_paciente = {id_paciente_deletar}")
        conn.commit()
    except Exception as e:
        conn.rollback()  # Caso ocorra algum erro, desfaz a transação
        print(f"Erro ao deletar o paciente: {e}")

    await update.message.reply_text("Paciente deletado com sucesso")
    return await voltar(update, context)  # Retorna ao menu principal

# -------------------- 5.2 Deletar cuidador  -------------------- #
async def deletar_cuidador(update: Update, context: CallbackContext) -> int:

    # Recebe o input do usuario do id do cuidador desejado para deletar
    id_cuidador_deletar = update.message.text.strip()

    # Deleta o cuidador no banco de dados de cuidador e todos os horarios de remedio associados 
    try:
        cursor.execute(f"DELETE FROM horario_remedios WHERE id_cuidador = {id_cuidador_deletar}")
        cursor.execute(f"DELETE FROM cuidador WHERE id_cuidador = {id_cuidador_deletar}")
        conn.commit()
    except Exception as e:
        conn.rollback()  # Caso ocorra algum erro, desfaz a transação
        print(f"Erro ao deletar o cuidador: {e}")

    await update.message.reply_text("Cuidador deletado com sucesso")
    return await voltar(update, context)  # Retorna ao menu principal

# -------------------- 5.3 Deletar remedio  -------------------- #
async def deletar_remedio(update: Update, context: CallbackContext) -> int:

    # Recebe o input do usuario do id do remedio desejado para deletar
    id_remedio_deletar = update.message.text.strip()

    # Deleta o remedio no banco de dados de remedio e todos os horarios de remedio associados 
    try:
        cursor.execute(f"DELETE FROM horario_remedios WHERE id_remedio = {id_remedio_deletar}")
        cursor.execute(f"DELETE FROM remedio WHERE id_remedio = {id_remedio_deletar}")
        conn.commit()
    except Exception as e:
        conn.rollback()  
        print(f"Erro ao deletar o remedio: {e}")

    await update.message.reply_text("Remedio deletado com sucesso")
    return await voltar(update, context)  # Retorna ao menu principal

# -------------------- 5.4 Deletar Horario Remedio  -------------------- #
# -------------------- 5.4.1 Deletar Horario Id paciente  -------------------- #
async def deletar_horario_id_paciente(update: Update, context: CallbackContext) -> int:
# Recebe o input do usuario do id do paciente desejado para adicionar
    id_paciente = update.message.text.strip()
    context.user_data["id_paciente"] = id_paciente  # Armazena o id do paciente
    logging.debug(f"Id Paciente: {id_paciente}")

    # Consulta todos os remedios para poder dar opcoes para o usuario
    cursor.execute(f"SELECT * FROM remedio WHERE id_remedio IN (SELECT DISTINCT id_remedio FROM horario_remedios WHERE id_paciente = {id_paciente} )")
    remedio = cursor.fetchall()

    # Se a consulta voltar vazia exibe uma mensagem para o usuario relatando que nao tem remedio cadastrado
    if not remedio:
        await update.message.reply_text(f"Nenhum remedio encontrado para esse paciente.")
        return await voltar(update, context)  # Volta para o início

    # Se a consulta nao voltar vazia formata a consulta e exibe a mensagem para o usuario  
    else:
        response = ""
        for row in remedio:
            response += f"ID: {row[0]}\n"
            response += f"Nome: {row[1]}\n"
            response += f"Dosagem: {row[2]}\n"
            response += f"Tipo: {row[3]}\n\n"

    # Exibe a mensagem para o usuario conforme a formatacao realizada
    await update.message.reply_text(response)

    await update.message.reply_text("Digite o id do remedio:")
    return 31  # Redireciona para a funcao 31 (deletar_horario_id_remedio)

# -------------------- 5.4.2 Deletar Horario Id Remedio  -------------------- #
async def deletar_horario_id_remedio(update: Update, context: CallbackContext) -> int:
    # Recebe o input do usuario do id do remedio desejado para adicionar
    id_remedio = update.message.text.strip()
    context.user_data["id_remedio"] = id_remedio  # Armazena o id do remedio
    logging.debug(f"Id Remedio: {id_remedio}")

    try:
        cursor.execute(
            "DELETE FROM horario_remedios WHERE id_paciente = %s AND id_remedio = %s",
            (context.user_data["id_paciente"], context.user_data["id_remedio"])  
        )
        conn.commit() 
    except Exception as e:
        conn.rollback()  
        print(f"Erro ao deletar o remedio: {e}")

    await update.message.reply_text("Remedio deletado com sucesso")
    return await voltar(update, context)  # Retorna ao menu principal


# -------------------- 6.0 Funcao cancel para retornar ao menu principal  -------------------- #
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Operação cancelada. Voltando...')
    return 0  


# -------------------- 7.0 Funcao Main que configura o Bot  -------------------- #
def main() -> None:
    # Conectando o bot com a API do Telegram
    application = Application.builder().token('7864374268:AAFf-24MzpFBm7Z8zR1FWCAnv1xvB6h_99Q').build()

    # Definindo o comportamento do bot com ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],  # A partir do comando /start
        states = {
                0: [MessageHandler(filters.TEXT, handle_menu)],
                1: [MessageHandler(filters.TEXT, consulta_opcao)],
                2: [MessageHandler(filters.TEXT, adicionar_opcao)],
                3: [MessageHandler(filters.TEXT, deletar_opcao)],
                4: [MessageHandler(filters.TEXT, consulta_nome_paciente)],
                5: [MessageHandler(filters.TEXT, consulta_nome_cuidador)],
                6: [MessageHandler(filters.TEXT, consulta_nome_remedio)],
                7: [MessageHandler(filters.TEXT, consulta_horario_remedio)],
                11: [MessageHandler(filters.TEXT & ~filters.COMMAND, adicionar_paciente_nome)],
                12: [MessageHandler(filters.TEXT & ~filters.COMMAND, adicionar_paciente_idade)],
                13: [MessageHandler(filters.TEXT & ~filters.COMMAND, adicionar_paciente_documento)],
                14: [MessageHandler(filters.TEXT & ~filters.COMMAND, adicionar_paciente_telefone)],
                15: [MessageHandler(filters.TEXT & ~filters.COMMAND, adicionar_cuidador_nome)],
                16: [MessageHandler(filters.TEXT & ~filters.COMMAND, adicionar_cuidador_documento)],
                17: [MessageHandler(filters.TEXT & ~filters.COMMAND, adicionar_cuidador_telefone)],
                18: [MessageHandler(filters.TEXT & ~filters.COMMAND, adicionar_remedio_nome)],
                19: [MessageHandler(filters.TEXT & ~filters.COMMAND, adicionar_remedio_dosagem)],
                20: [MessageHandler(filters.TEXT & ~filters.COMMAND, adicionar_remedio_tipo)],
                21: [MessageHandler(filters.TEXT & ~filters.COMMAND, adicionar_horario_id_paciente)],
                22: [MessageHandler(filters.TEXT & ~filters.COMMAND, adicionar_horario_id_cuidador)],
                23: [MessageHandler(filters.TEXT & ~filters.COMMAND, adicionar_horario_id_remedio)],
                24: [MessageHandler(filters.TEXT & ~filters.COMMAND, adicionar_horario_data_inicio)],
                25: [MessageHandler(filters.TEXT & ~filters.COMMAND, adicionar_horario_data_fim)],
                26: [MessageHandler(filters.TEXT & ~filters.COMMAND, adicionar_horario_horario)],
                27: [MessageHandler(filters.TEXT & ~filters.COMMAND, deletar_paciente)],
                28: [MessageHandler(filters.TEXT & ~filters.COMMAND, deletar_cuidador)],
                29: [MessageHandler(filters.TEXT & ~filters.COMMAND, deletar_remedio)],
                30: [MessageHandler(filters.TEXT & ~filters.COMMAND, deletar_horario_id_paciente)],
                31: [MessageHandler(filters.TEXT & ~filters.COMMAND, deletar_horario_id_remedio)],
            },
        fallbacks=[MessageHandler(filters.TEXT, cancel)],
    )

    application.add_handler(conv_handler)

    # Rodando a aplicacao
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
