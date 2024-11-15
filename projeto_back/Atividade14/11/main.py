import psutil  # Biblioteca para coletar informações do sistema
import platform  # Biblioteca para coletar informações sobre o sistema operacional
from os import system

class SistemaDiagnostico:
    def __init__(self):
        """
        Inicializa o sistema de diagnóstico e coleta informações do sistema.
        """
        self.sistema = platform.system()  # Nome do sistema operacional (Windows, Linux, etc.)
        self.versao = platform.version()  # Versão do sistema operacional
        self.processador = platform.processor()  # Processador do sistema
        self.memoria_total = psutil.virtual_memory().total  # Memória total do sistema em bytes
        self.temperatura = None  # Variável para armazenar a temperatura do CPU

        # Verifica se o sistema possui sensor de temperatura
        if hasattr(psutil, "sensors_temperatures"):
            temp_info = psutil.sensors_temperatures()
            if 'coretemp' in temp_info:
                self.temperatura = temp_info['coretemp'][0].current  # Coleta a temperatura da CPU

    def exibir_informacoes_sistema(self):
        """
        Exibe informações gerais do sistema operacional, processador e memória.
        """
        print(f"Sistema Operacional: {self.sistema} - Versão: {self.versao}")
        print(f"Processador: {self.processador}")
        print(f"Memória Total: {round(self.memoria_total / (1024**3), 2)} GB")

    def exibir_status_bateria(self):
        """
        Exibe o status da bateria, se disponível.
        """
        bateria = psutil.sensors_battery()  # Obtém informações da bateria
        if bateria:
            percent = bateria.percent  # Percentual da bateria
            carregando = "Carregando" if bateria.power_plugged else "Descarregando"
            print(f"Bateria: {percent}% - Status: {carregando}")
        else:
            print("Informações de bateria não disponíveis.")

    def exibir_processos(self):
        """
        Exibe uma lista de todos os processos em execução com nome, ID e uso de CPU.
        """
        print("\nProcessos em execução:")
        print(f"{'Nome':<25} {'ID':<10} {'Uso de CPU (%)'}")
        for processo in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                nome = processo.info['name'] or "N/A"
                pid = processo.info['pid']
                cpu_percent = processo.info['cpu_percent']
                print(f"{nome:<25} {pid:<10} {cpu_percent:.2f}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    def diagnosticar(self):
        """
        Realiza o diagnóstico com base em perguntas e informações coletadas do sistema.
        """
        print("Bem-vindo ao sistema de diagnóstico de computadores.")
        self.exibir_informacoes_sistema()
        self.exibir_status_bateria()
        
        # Pergunta os sintomas ao usuário
        computador_nao_liga = input("O computador não liga? (s/n): ").strip().lower() == 's'
        tela_preta = input("O computador liga mas fica com a tela preta? (s/n): ").strip().lower() == 's'
        lentidao = input("O computador está muito lento? (s/n): ").strip().lower() == 's'
        superaquecimento = input("O computador está superaquecendo? (s/n): ").strip().lower() == 's'
        erros_sistema = input("Há mensagens de erro frequentes no sistema? (s/n): ").strip().lower() == 's'

        # Coleta de métricas adicionais do sistema
        cpu_percent = psutil.cpu_percent(interval=1)  # Percentual de uso da CPU
        mem_info = psutil.virtual_memory()  # Informações de uso da memória

        print(f"\nUso de CPU: {cpu_percent}%")
        print(f"Memória em uso: {round(mem_info.used / (1024**3), 2)} GB de {round(mem_info.total / (1024**3), 2)} GB")
        if self.temperatura:
            print(f"Temperatura da CPU: {self.temperatura}°C\n")
        else:
            print("Não foi possível obter a temperatura da CPU\n")

        # Regras do sistema especialista para diagnóstico com base nos sintomas
        if computador_nao_liga:
            print("Verifique se o cabo de alimentação está conectado e se a fonte de alimentação está funcionando.")
            print("Possível problema: Falha na fonte de alimentação ou problema de hardware.")
        elif tela_preta:
            print("Tente verificar as conexões do monitor e reiniciar o computador.")
            print("Possível problema: Falha no monitor, cabo de vídeo ou placa gráfica.")
        elif lentidao:
            if superaquecimento or (self.temperatura and self.temperatura > 80):
                print("Verifique se o sistema de ventilação está funcionando e limpe os ventiladores.")
                print("Possível problema: Superaquecimento devido ao acúmulo de poeira ou falha no sistema de refrigeração.")
            elif mem_info.percent > 80:
                print("A memória está quase totalmente utilizada. Considere fechar alguns programas.")
                print("Possível problema: Falta de memória RAM.")
            elif cpu_percent > 80:
                print("O uso da CPU está alto. Considere verificar por processos em segundo plano.")
                print("Possível problema: Uso excessivo de CPU.")
            else:
                print("Verifique se há malware ou muitos programas em execução no sistema.")
            
            # Exibe lista de processos se o sistema estiver lento
            self.exibir_processos()

        elif superaquecimento or (self.temperatura and self.temperatura > 80):
            print("Verifique a temperatura do CPU e limpe os ventiladores.")
            print("Possível problema: Acúmulo de poeira ou falha na ventilação.")
        elif erros_sistema:
            print("Considere atualizar o sistema operacional ou verificar por erros no disco.")
            print("Possível problema: Corrupção de arquivos do sistema ou falhas de software.")
        else:
            print("Não foi possível identificar um problema específico.")
            print("Recomendações: Verifique se todos os cabos e conexões estão corretos e reinicie o computador.")


# Instancia a classe SistemaDiagnostico e executa o método de diagnóstico
sistema_diagnostico = SistemaDiagnostico()
sistema_diagnostico.diagnosticar()
