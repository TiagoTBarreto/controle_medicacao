import psycopg2
import requests
import schedule
import time

from urllib.parse import urlparse
from datetime import datetime, timedelta


# Seu token de bot do Telegram
TOKEN = '7864374268:AAFf-24MzpFBm7Z8zR1FWCAnv1xvB6h_99Q'

# URL da API do Telegram para enviar a mensagem
url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

# URL de conexão com o banco de dados
database_url = "postgresql://db_bot_medicacaov2_gzom_user:NVPCbyvTXX6pU49hFFW5J0hHGotIKHrK@dpg-cu7dqgjv2p9s73bfnfb0-a/db_bot_medicacaov2_gzom"

# Parse da URL de conexão
parsed_url = urlparse(database_url)

# Extrair informações de conexão
db_user = parsed_url.username
db_password = parsed_url.password
db_host = parsed_url.hostname
db_port = parsed_url.port
db_name = parsed_url.path[1:]  # Remove a barra inicial

# Conectar ao banco de dados PostgreSQL
conn = psycopg2.connect(
    dbname=db_name,
    user=db_user,
    password=db_password,
    host=db_host,
    port=db_port
)

# Função para enviar a mensagem
def enviar_mensagem(chat_id, mensagem):
    payload = {
        'chat_id': chat_id,
        'text': mensagem
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print(f"Mensagem enviada para o chat {chat_id} com sucesso!")
    else:
        print(f"Erro ao enviar mensagem para o chat {chat_id}: {response.status_code}")

# Função para obter os horários de medicação e cuidadores da base de dados
def obter_horarios_cuidadores():
    cursor = conn.cursor()

    # Consulta SQL para obter os dados necessários
    cursor.execute("""
        SELECT p.nome_paciente, p.telefone_parente, cd.nome_cuidador, c.chat_id, r.nome_remedio, r.dosagem, r.tipo, h.hora
        FROM horario_remedios h
        JOIN remedio r ON h.id_remedio = r.id_remedio
        JOIN cuidador_chat c ON h.id_cuidador = c.id_cuidador
        JOIN paciente p ON h.id_paciente = p.id_paciente
        JOIN cuidador cd ON h.id_cuidador = cd.id_cuidador
        WHERE h.data_inicio <= CURRENT_DATE AND h.data_fim >= CURRENT_DATE
    """)

    # Recupera todos os resultados da consulta
    horarios_cuidadores = cursor.fetchall()

    # Fechar o cursor
    cursor.close()

    return horarios_cuidadores

# Função para agendar as mensagens
def agendar_mensagens():
    horarios_cuidadores = obter_horarios_cuidadores()

    # Iterar sobre os horários de medicação e agendar as mensagens
    for nome_paciente, telefone_parente, nome_cuidador, chat_id, nome_remedio, dosagem, tipo, hora in horarios_cuidadores:
        
        # Garantir que a hora esteja no formato HH:MM (remover os segundos)
        try:
            # Converte a hora para um objeto datetime e depois formata para "HH:MM"
            hora_formatada = datetime.strptime(str(hora), "%H:%M:%S").strftime("%H:%M")
        except ValueError:
            print(f"Erro de formatação para o horário: {hora}")
            continue  # Pular esta iteração se a hora não for válida
        
        # Criar a mensagem
        mensagem = f"Olá, {nome_cuidador}. Lembrete: Está na hora do paciente {nome_paciente} ser medicado: {nome_remedio} ({dosagem} - {tipo}). Qualquer emergência entrar em contato com um parente nesse número: {telefone_parente}"
        
        # Agendar a mensagem para o horário de medicação
        schedule.every().day.at(hora_formatada).do(enviar_mensagem, chat_id=chat_id, mensagem=mensagem)

# Iniciar o agendamento das mensagens
agendar_mensagens()

# Loop para manter o agendamento
while True:
    schedule.run_pending()  # Executa as tarefas agendadas
    time.sleep(1)  # Pausa por 1 segundo para não consumir muito CPU
