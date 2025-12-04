import os
import sys
import time
import subprocess
import ctypes
import winreg
import json
import urllib.request
import urllib.error
from colorama import init, Fore, Style
import platform
import threading

# Initialize colorama
init(autoreset=True)

# Cores e Constantes
CYAN = Fore.LIGHTCYAN_EX
WHITE = Fore.LIGHTWHITE_EX
PURPLE = Fore.MAGENTA
RESET = Style.RESET_ALL
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
RED = Fore.RED

# Variável de Idioma Global
CURRENT_LANGUAGE = 'pt' # Padrão: Português

# Dicionário de Textos - TODAS as strings visíveis ao usuário devem estar aqui
# Chave: [Português, Inglês]
TEXTS = {
    # ------------------ GERAL ------------------
    "banner_title": ["Lithium Optimizer v1.0", "Lithium Optimizer v1.0"],
    "banner_subtitle": ["Otimização avançada e segura para Windows", "Advanced and secure optimization for Windows"],
    "banner_info": ["[INFO] Creado por MrLuckke", "[INFO] Created by MrLuckke"],
    "press_enter_return_menu": [
        "Pressione Enter para voltar ao menu principal...", 
        "Press Enter to return to the main menu..."
    ],
    "press_enter_continue": ["Pressione Enter para continuar...", "Press Enter to continue..."],
    "invalid_option_error": ["Opção inválida. Tente novamente.", "Invalid option. Try again."],
    "invalid_input_error": ["Entrada inválida. Tente novamente.", "Invalid input. Try again."],
    "thank_you_message": ["Obrigado por usar o Lithium Optimizer!", "Thank you for using Lithium Optimizer!"],
    "option_continue_or_cancel": ["Deseja continuar? (s/n): ", "Do you want to continue? (y/n): "],
    "action_confirmed": ["O usuário confirmou a ação: ", "User confirmed the action: "],
    "action_cancelled": ["Ação cancelada pelo usuário: ", "Action cancelled by user: "],
    "operation_success": ["Operação concluída com sucesso.", "Operation completed successfully."],
    "critical_error_msg": ["Esta etapa é crítica. Algumas otimizações podem não ter sido aplicadas corretamente.", "This step is critical. Some optimizations may not have been applied correctly."],
    "system_command_fail": ["Falha ao executar comando do sistema.", "Failed to execute system command."],
    "registry_not_found": ["Valor/chave de registro não encontrada. Pode ser que o item já não exista, seguindo normalmente.", "Registry value/key not found. It may be that the item no longer exists, proceeding normally."],
    
    # ------------------ LANGUAGE SELECTION ------------------
    "lang_selection_title": ["Selecione o Idioma:", "Select Language:"],
    "lang_prompt": ["Digite '1' para Português, '2' para English: ", "Enter '1' for Português, '2' for English: "],
    "lang_set_pt": ["Idioma definido para Português.", "Language set to Portuguese."],
    "lang_set_en": ["Idioma definido para English.", "Language set to English."],

    # ------------------ WEBHOOK CONFIG ------------------
    "webhook_config_title": ["Configuração de Relatórios no Discord", "Discord Reports Configuration"],
    "webhook_explanation": [
        "Você pode receber relatórios simples em um canal do Discord enquanto o otimizador roda.\nIsso inclui: o que está sendo otimizado, etapa atual e possíveis impactos.",
        "You can receive simple reports in a Discord channel while the optimizer runs.\nThis includes: what is being optimized, current step, and possible impacts."
    ],
    "webhook_prompt": ["Deseja configurar um webhook do Discord agora? (s/n): ", "Do you want to configure a Discord webhook now? (y/n): "],
    "webhook_url_prompt": ["Cole aqui a URL do webhook do Discord: ", "Paste the Discord webhook URL here: "],
    "webhook_not_configured": ["Webhook do Discord não configurado. Você pode configurar depois editando o código.", "Discord webhook not configured. You can configure it later by editing the code."],
    "webhook_no_url": ["Nenhuma URL informada. Logs remotos desativados.", "No URL provided. Remote logs disabled."],
    "webhook_test_msg": ["Testando envio de mensagem de boas-vindas ao Discord...", "Testing welcome message sent to Discord..."],
    "webhook_configured_success": ["Webhook configurado. Você receberá relatórios durante as otimizações.", "Webhook configured. You will receive reports during optimizations."],

    # ------------------ MAIN MENU ------------------
    "menu_title": ["Menu Principal:", "Main Menu:"],
    "menu_option_select": ["Digite o número da opção e pressione Enter:", "Enter the option number and press Enter:"],
    "menu_option_prompt": ["Selecione uma opção: ", "Select an option: "],
    "menu_opt_1": ["Otimizar Programas de Inicialização", "Optimize Startup Programs"],
    "menu_opt_2": ["Otimizar Registro", "Optimize Registry"],
    "menu_opt_3": ["Otimizar Disco", "Optimize Disk"],
    "menu_opt_4": ["Otimizar Configurações de Display", "Optimize Display Settings"],
    "menu_opt_5": ["Otimizar Rede", "Optimize Network"],
    "menu_opt_6": ["Otimizar Memória", "Optimize Memory"],
    "menu_opt_7": ["Otimização de Sistema (SFC/DISM + Energia)", "System Optimization (SFC/DISM + Power)"],
    "menu_opt_8": ["Criar Ponto de Restauração", "Create Restore Point"],
    "menu_opt_9": ["Otimizar Tudo (Recomendado)", "Optimize All (Recommended)"],
    "menu_opt_10": ["Informações do Sistema", "System Information"],
    "menu_opt_11": ["Sair", "Exit"],

    # ------------------ OPTIMIZE STARTUP ------------------
    "title_startup": ["Otimização de Programas de Inicialização", "Startup Programs Optimization"],
    "explanation_startup": [
        "Esta etapa tenta desativar alguns programas comuns que iniciam junto com o Windows.\n- Impacto positivo: inicialização mais rápida e menor uso de memória.\n- Risco: se você usa algum desses programas no login automático, precisará abri-lo manualmente.\nNada é desinstalado, apenas removido da inicialização automática.",
        "This step attempts to disable some common programs that start with Windows.\n- Positive impact: faster boot-up and lower memory usage.\n- Risk: if you use any of these programs on automatic login, you will need to open them manually.\nNothing is uninstalled, only removed from automatic startup."
    ],
    "startup_optimization_start": ["Iniciando otimização de programas de inicialização...", "Starting startup programs optimization..."],
    "startup_optimization_finish": ["Otimização de programas de inicialização concluída.", "Startup programs optimization complete."],
    "startup_remove_program": ["Removendo {} da inicialização", "Removing {} from startup"],

    # ------------------ OPTIMIZE REGISTRY ------------------
    "title_registry": ["Otimização do Registro do Windows", "Windows Registry Optimization"],
    "explanation_registry": [
        "Esta etapa ajusta algumas chaves de registro para melhorar desempenho geral.\n- Impacto positivo: sistema ligeiramente mais responsivo, menos carregamento desnecessário.\n- Risco: alterações de registro são sensíveis. Um ponto de restauração é recomendado antes.\nAs chaves alteradas são focadas em cache de ícones, efeitos visuais e sistema de arquivos.",
        "This step adjusts some registry keys to improve overall performance.\n- Positive impact: slightly more responsive system, less unnecessary loading.\n- Risk: registry changes are sensitive. A restore point is recommended before.\nChanges focus on icon caching, visual effects, and file system."
    ],
    "registry_cleanup_start": ["Limpando entradas de registro desnecessárias do Explorador...", "Cleaning unnecessary Explorer registry entries..."],
    "registry_remove_entry": ["Removendo entradas desnecessárias do 'Este Computador'", "Removing unnecessary entries from 'This PC'"],
    "registry_performance_start": ["Aplicando ajustes de desempenho no registro...", "Applying performance tweaks to the registry..."],
    "registry_adjusting": ["Ajustando {} em {}", "Adjusting {} in {}"],
    "registry_optimization_finish": ["Otimização do registro concluída.", "Registry optimization complete."],
    
    # ------------------ OPTIMIZE DISK ------------------
    "title_disk": ["Otimização de Disco", "Disk Optimization"],
    "explanation_disk": [
        "Esta etapa limpa arquivos temporários, executa a Limpeza de Disco e otimiza o drive.\n- Impacto positivo: libera espaço em disco e pode melhorar a velocidade de acesso.\n- Risco: arquivos temporários recentes serão apagados; normalmente é seguro.\nRecomendado fechar programas importantes antes de continuar.",
        "This step cleans temporary files, runs Disk Cleanup, and optimizes the drive.\n- Positive impact: frees up disk space and may improve access speed.\n- Risk: recent temporary files will be deleted; usually safe.\nIt is recommended to close important programs before continuing."
    ],
    "disk_cleanup_temp_start": ["Limpando arquivos temporários do sistema...", "Cleaning temporary system files..."],
    "disk_cleanning": ["Limpando {}", "Cleaning {}"],
    "disk_cleanup_start": ["Executando Limpeza de Disco do Windows (cleanmgr)...", "Executing Windows Disk Cleanup (cleanmgr)..."],
    "disk_defrag_start": ["Otimização/Desfragmentação do drive (Windows decidirá a melhor opção)...", "Drive Optimization/Defragmentation (Windows will decide the best option)..."],
    "disk_optimization_finish": ["Otimização de disco concluída.", "Disk optimization complete."],

    # ------------------ OPTIMIZE DISPLAY ------------------
    "title_display": ["Otimização de Display", "Display Optimization"],
    "explanation_display": [
        "Esta etapa tenta melhorar a fluidez visual ajustando efeitos gráficos e possivelmente taxa de atualização.\n- Impacto positivo: sistema mais leve, menos animações pesadas.\n- Risco: alguns efeitos visuais podem ser reduzidos ou desativados.\nNada crítico é removido; são ajustes de aparência e desempenho.",
        "This step tries to improve visual fluidity by adjusting graphic effects and possibly refresh rate.\n- Positive impact: lighter system, fewer heavy animations.\n- Risk: some visual effects may be reduced or disabled.\nNothing critical is removed; these are appearance and performance tweaks."
    ],
    "display_optimization_start": ["Otimizando configurações de exibição...", "Optimizing display settings..."],
    "display_monitor_detected": ["Monitor detectado: {}", "Monitor detected: {}"],
    "display_rate_optimization": ["Otimização básica de taxa de atualização para {} (modo simplificado).", "Basic refresh rate optimization for {} (simplified mode)."],
    "display_wmi_not_found": ["Módulo WMI não encontrado. Instale com: pip install wmi", "WMI module not found. Install with: pip install wmi"],
    "display_basic_optimization": ["Usando apenas otimização visual básica (sem detecção detalhada de monitores).", "Using only basic visual optimization (without detailed monitor detection)."],
    "display_visual_effects_start": ["Aplicando ajustes de efeitos visuais para priorizar desempenho...", "Applying visual effects tweaks to prioritize performance..."],
    "display_adjusting_effect": ["Aplicando ajuste de efeito visual", "Applying visual effect adjustment"],
    "display_apply_settings": ["Aplicando configurações visuais ao usuário atual", "Applying visual settings to current user"],
    "display_optimization_finish": ["Otimização de display concluída.", "Display optimization complete."],

    # ------------------ OPTIMIZE NETWORK ------------------
    "title_network": ["Otimização de Rede", "Network Optimization"],
    "explanation_network": [
        "Esta etapa ajusta parâmetros de rede TCP/IP e DNS para tentar melhorar latência e estabilidade.\n- Impacto positivo: conexões potencialmente mais estáveis e rápidas em alguns cenários.\n- Risco: configurações muito específicas podem não ser ideais para todas as redes.\nVocê sempre pode desfazer ajustes manualmente nas opções de rede do Windows.",
        "This step adjusts TCP/IP and DNS network parameters to try to improve latency and stability.\n- Positive impact: potentially more stable and faster connections in some scenarios.\n- Risk: very specific settings may not be ideal for all networks.\nYou can always undo tweaks manually in Windows network options."
    ],
    "network_optimization_start": ["Otimizando parâmetros globais de TCP/IP...", "Optimizing global TCP/IP parameters..."],
    "network_adjusting": ["Aplicando ajuste de rede", "Applying network adjustment"],
    "network_dns_start": ["Ajustando DNS para servidores públicos do Google (8.8.8.8 / 8.8.4.4)...", "Adjusting DNS to Google public servers (8.8.8.8 / 8.8.4.4)..."],
    "network_dns_primary_eth": ["Definindo DNS principal (Ethernet)", "Setting primary DNS (Ethernet)"],
    "network_dns_secondary_eth": ["Adicionando DNS secundário (Ethernet)", "Adding secondary DNS (Ethernet)"],
    "network_dns_primary_wifi": ["Definindo DNS principal (Wi-Fi)", "Setting primary DNS (Wi-Fi)"],
    "network_dns_secondary_wifi": ["Adicionando DNS secundário (Wi-Fi)", "Adding secondary DNS (Wi-Fi)"],
    "network_optimization_finish": ["Otimização de rede concluída.", "Network optimization complete."],

    # ------------------ OPTIMIZE MEMORY ------------------
    "title_memory": ["Otimização de Memória", "Memory Optimization"],
    "explanation_memory": [
        "Esta etapa ajusta parâmetros de memória virtual e pré-busca do Windows.\n- Impacto positivo: pode melhorar o uso de memória e estabilidade em uso prolongado.\n- Risco: pequenos ajustes em como o Windows gerencia cache e pré-carregamento.\nAs alterações são conservadoras e focadas em estabilidade.",
        "This step adjusts Windows virtual memory and prefetch parameters.\n- Positive impact: may improve memory usage and stability during prolonged use.\n- Risk: minor adjustments to how Windows manages caching and preloading.\nThe changes are conservative and focused on stability."
    ],
    "memory_optimization_start": ["Aplicando otimizações de memória no registro...", "Applying memory optimizations in the registry..."],
    "memory_adjusting": ["Aplicando ajuste de memória", "Applying memory adjustment"],
    "memory_cleanup_start": ["Limpando alguns arquivos temporários relacionados a memória...", "Cleaning some temporary files related to memory..."],
    "memory_cleanning_temp": ["Limpando temporários de memória", "Cleaning memory temporaries"],
    "memory_optimization_finish": ["Otimização de memória concluída.", "Memory optimization complete."],

    # ------------------ OPTIMIZE SYSTEM ------------------
    "title_system": ["Otimização de Sistema (SFC/DISM + Energia)", "System Optimization (SFC/DISM + Power)"],
    "explanation_system": [
        "Esta etapa verifica a integridade dos arquivos de sistema (SFC/DISM) e ajusta o plano de energia.\n- Impacto positivo: corrige arquivos corrompidos do Windows e ajusta energia para melhor desempenho.\n- Risco: nenhuma perda de dados, mas o processo pode demorar alguns minutos.\nRecomendado rodar quando o PC puder ficar sem reinicializações ou desligamentos inesperados.",
        "This step checks system file integrity (SFC/DISM) and adjusts the power plan.\n- Positive impact: corrects corrupted Windows files and adjusts power for better performance.\n- Risk: no data loss, but the process may take a few minutes.\nRecommended to run when the PC can remain without unexpected reboots or shutdowns."
    ],
    "system_sfc_start": ["Executando verificação de arquivos de sistema (sfc /scannow)...", "Running system file check (sfc /scannow)..."],
    "system_sfc_msg": ["Executando SFC /scannow", "Executing SFC /scannow"],
    "system_dism_start": ["Executando checagens de integridade com DISM...", "Running integrity checks with DISM..."],
    "system_dism_check": ["DISM CheckHealth", "DISM CheckHealth"],
    "system_dism_scan": ["DISM ScanHealth", "DISM ScanHealth"],
    "system_dism_restore": ["DISM RestoreHealth", "DISM RestoreHealth"],
    "system_power_start": ["Aplicando plano de energia focado em desempenho...", "Applying power plan focused on performance..."],
    "system_power_high": ["Ativando plano de energia mínimo (alto desempenho)", "Activating minimum power plan (high performance)"],
    "system_power_monitor_ac": ["Desativando desligamento de monitor na energia AC", "Disabling monitor shutdown on AC power"],
    "system_power_monitor_dc": ["Ajustando desligamento de monitor na bateria", "Adjusting monitor shutdown on battery"],
    "system_power_standby_ac": ["Desativando suspensão em energia AC", "Disabling standby on AC power"],
    "system_power_standby_dc": ["Ajustando suspensão na bateria", "Adjusting standby on battery"],
    "system_power_hibernate_ac": ["Desativando hibernação em energia AC", "Disabling hibernation on AC power"],
    "system_power_hibernate_dc": ["Desativando hibernação na bateria", "Disabling hibernation on battery"],
    "system_optimization_finish": ["Otimização de sistema concluída.", "System optimization complete."],

    # ------------------ RESTORE POINT ------------------
    "title_restore_point": ["Criar Ponto de Restauração do Sistema", "Create System Restore Point"],
    "explanation_restore_point": [
        "Um ponto de restauração permite voltar o estado do sistema (arquivos de sistema e registro)\npara antes das otimizações, caso algo não fique como esperado.\n- Recomendado antes de grandes mudanças.\n- Pode levar alguns minutos e requer que a Proteção do Sistema esteja ativada no Windows.",
        "A restore point allows you to revert the system state (system files and registry)\nto before the optimizations, in case something goes wrong.\n- Recommended before major changes.\n- May take a few minutes and requires System Protection to be enabled in Windows."
    ],
    "restore_point_start": ["Criando ponto de restauração do sistema via PowerShell...", "Creating system restore point via PowerShell..."],
    "restore_point_msg": ["Criando ponto de restauração (Checkpoint-Computer)", "Creating restore point (Checkpoint-Computer)"],
    "restore_point_success": ["Ponto de restauração criado (se o recurso estiver habilitado no sistema).", "Restore point created (if the feature is enabled in the system)."],
    "restore_point_fail": ["Não foi possível criar o ponto de restauração. Verifique se a Proteção do Sistema está ativada.", "Could not create the restore point. Check if System Protection is enabled."],
    
    # ------------------ OPTIMIZE ALL ------------------
    "title_optimize_all": ["Otimização Completa do Sistema", "Full System Optimization"],
    "explanation_optimize_all": [
        "Esta opção executa, em sequência, todas as otimizações disponíveis.\n- Ela pode levar um bom tempo, dependendo do seu PC.\n- Recomenda-se fechar programas importantes e, se possível, criar um ponto de restauração antes.\nVocê ainda verá resumos e confirmações em cada etapa importante.",
        "This option executes all available optimizations sequentially.\n- It may take a long time, depending on your PC.\n- It is recommended to close important programs and, if possible, create a restore point before.\nYou will still see summaries and confirmations at each important step."
    ],
    "optimize_all_start": ["Iniciando otimização completa do sistema...", "Starting full system optimization..."],
    "optimize_all_restore_point": ["Primeiro, será criado (se possível) um ponto de restauração do sistema.", "First, a system restore point will be created (if possible)."],
    "optimize_all_restore_point_msg": ["Criando ponto de restauração automático antes da otimização completa", "Creating automatic restore point before full optimization"],
    "optimize_all_finish": ["Todas as otimizações foram concluídas com sucesso.", "All optimizations finished successfully."],

    # ------------------ SYSTEM INFO ------------------
    "title_system_info": ["Informações do Sistema", "System Information"],
    "sys_os": ["Sistema Operacional:", "Operating System:"],
    "sys_version": ["Versão:", "Version:"],
    "sys_arch": ["Arquitetura:", "Architecture:"],
    "sys_processor": ["Processador:", "Processor:"],
    "sys_ram_total": ["RAM Total:", "Total RAM:"],
    "sys_ram_available": ["RAM Disponível:", "Available RAM:"],
    "sys_ram_usage": ["Uso de RAM:", "RAM Usage:"],
    "sys_psutil_warning": ["Módulo psutil não encontrado. Instale com: pip install psutil", "psutil module not found. Install with: pip install psutil"],
    "sys_disk_total": ["Espaço Total em Disco:", "Total Disk Space:"],
    "sys_disk_used": ["Espaço Usado:", "Used Space:"],
    "sys_disk_free": ["Espaço Livre:", "Free Space:"],
    "sys_disk_usage": ["Uso de Disco:", "Disk Usage:"],

    # ------------------ ADMIN CHECK ------------------
    "admin_warning": ["Este script precisa ser executado como administrador para funcionar corretamente.", "This script needs to be run as an administrator to work correctly."],
    "admin_info_restarting": ["Tentando reiniciar com privilégios de administrador...", "Attempting to restart with administrator privileges..."],
    "admin_error_restart": ["Falha ao tentar reiniciar como administrador: {}", "Failed to attempt restart as administrator: {}"],
    "admin_detail": ["Execute o script manualmente como administrador.", "Run the script manually as administrator."],
    "admin_press_enter_exit": ["Pressione Enter para sair...", "Press Enter to exit..."],
}

# ----------------------------------------------------------------------
# FUNÇÃO DE TRADUÇÃO SIMPLIFICADA
# ----------------------------------------------------------------------
def T(key: str) -> str:
    """Retorna a string traduzida baseada no CURRENT_LANGUAGE."""
    lang_index = 0 if CURRENT_LANGUAGE == 'pt' else 1
    # Retorna o texto, ou a chave se não for encontrada para evitar quebrar o programa
    return TEXTS.get(key, ["KEY_NOT_FOUND", "KEY_NOT_FOUND"])[lang_index]


def gradient_text(text: str) -> str:
    """
    Aplica um gradiente suave de cores no texto.
    """
    palette = [CYAN, WHITE, CYAN, WHITE, CYAN]
    out = []
    idx = 0
    for ch in text:
        if ch.isspace():
            out.append(ch)
        else:
            out.append(palette[idx % len(palette)] + ch + RESET)
            idx += 1
    return "".join(out)

def send_discord_log(title: str, description: str, level: str = "INFO") -> None:
    """
    Envia um log simples para o webhook do Discord, se configurado.
    """
    global DISCORD_WEBHOOK_URL
    if not DISCORD_WEBHOOK_URL:
        return

    color = 3066993 if level == "INFO" else (15105570 if level == "WARNING" else 15158332)
    footer_text = "Lithium Optimizer • Logs em tempo real" # Mantido sem tradução

    payload = {
        "username": "Lithium Optimizer",
        "embeds": [
            {
                "title": f"[{level}] {title}",
                "description": description,
                "color": color,
                "footer": {
                    "text": footer_text
                }
            }
        ]
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        DISCORD_WEBHOOK_URL,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "LithiumOptimizerWebhook/1.0"}
    )
    try:
        urllib.request.urlopen(req, timeout=5)
    except urllib.error.HTTPError as e:
        print(f"{YELLOW}[WARNING]{RESET} {T('webhook_config_title').split(' - ')[0]} (HTTP {e.code}). Verifique se a URL do webhook está correta.")
    except urllib.error.URLError:
        print(f"{YELLOW}[WARNING]{RESET} Não foi possível contatar o Discord para enviar o log (problema de rede).")


def log(message: str, level: str = "INFO", send_webhook: bool = True) -> None:
    """
    Log profissional no console + (opcional) envio para Discord.
    """
    prefix_color = {
        "INFO": CYAN,
        "SUCCESS": GREEN,
        "WARNING": YELLOW,
        "ERROR": RED
    }.get(level.upper(), CYAN)

    pretty_message = gradient_text(message)
    print(f"{prefix_color}[{level.upper()}]{RESET} {pretty_message}")

    if send_webhook:
        send_discord_log(level.upper(), message, level.upper())


def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def display_banner():
    """
    Substitui o banner antigo pela arte ASCII, usando a cor PURPLE (MAGENTA).
    """
    clear_screen()
    # Arte ASCII
    print(f"""{PURPLE}
                             ██╗░░░░░██╗████████╗██╗░░██╗██╗██╗░░░██╗███╗░░░███╗
                             ██║░░░░░██║╚══██╔══╝██║░░██║██║██║░░░██║████╗░████║
                             ██║░░░░░██║░░░██║░░░███████║██║██║░░░██║██╔████╔██║
                             ██║░░░░░██║░░░██║░░░██╔══██║██║██║░░░██║██║╚██╔╝██║
                             ███████╗██║░░░██║░░░██║░░██║██║╚██████╔╝██║░╚═╝░██║
                             ╚══════╝╚═╝░░░╚═╝░░░╚═╝░░╚═╝╚═╝░╚═════╝░╚═╝░░░░░╚═╝   [ V 1 ]
""")
    # Adicionando as linhas de informação do banner, agora traduzidas
    width = 70
    print(CYAN + T('banner_title').center(width) + RESET)
    print(CYAN + T('banner_subtitle').center(width) + RESET)
    print(CYAN + T('banner_info').center(width) + RESET)


def check_admin():
    """Check if the script is running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Webhook do Discord (configurado em tempo de execução)
DISCORD_WEBHOOK_URL = None

def select_language():
    """Permite ao usuário selecionar o idioma antes do menu principal."""
    global CURRENT_LANGUAGE
    
    clear_screen()
    
    # Garante que a seleção inicial esteja nos dois idiomas
    print(f"{CYAN}=== {TEXTS['lang_selection_title'][0]} / {TEXTS['lang_selection_title'][1]} ==={RESET}\n")
    print("1. Português")
    print("2. English")
    
    while True:
        choice = input(f"\n{CYAN}{TEXTS['lang_prompt'][0]} / {TEXTS['lang_prompt'][1]}{RESET}")
        
        if choice in ['1', 's', 'p']:
            CURRENT_LANGUAGE = 'pt'
            log(T('lang_set_pt'), "INFO", send_webhook=False)
            break
        elif choice in ['2', 'n', 'e']:
            CURRENT_LANGUAGE = 'en'
            log(T('lang_set_en'), "INFO", send_webhook=False)
            break
        else:
            print(f"{RED}[ERROR]{RESET} {T('invalid_input_error')}")
            time.sleep(1)

def configure_webhook():
    """
    Pergunta ao usuário se deseja usar um webhook do Discord para receber relatórios.
    Executa antes de entrar no menu principal.
    """
    global DISCORD_WEBHOOK_URL

    clear_screen()
    display_banner()
    print(f"\n{CYAN}=== {T('webhook_config_title')} ==={RESET}\n")
    print(T('webhook_explanation'))

    choice = input(T('webhook_prompt')).strip().lower()
    
    # Traduzindo 's' e 'n' para 'y' (yes)
    if CURRENT_LANGUAGE == 'en':
        confirm_key = 'y'
    else:
        confirm_key = 's'
        
    if choice != confirm_key:
        log(T('webhook_not_configured'), "INFO", send_webhook=False)
        input(f"\n{CYAN}{T('press_enter_return_menu')}{RESET}")
        return

    url = input(T('webhook_url_prompt')).strip()
    if not url:
        log(T('webhook_no_url'), "WARNING", send_webhook=False)
        input(f"\n{CYAN}{T('press_enter_return_menu')}{RESET}")
        return

    DISCORD_WEBHOOK_URL = url
    log(T('webhook_test_msg'), "INFO", send_webhook=False)
    send_discord_log(T('webhook_config_title'), T('webhook_configured_success'), "INFO")
    log(T('webhook_configured_success'), "SUCCESS", send_webhook=False)
    input(f"\n{CYAN}{T('press_enter_return_menu')}{RESET}")
    
def run_command(command, description="Executando comando", critical: bool = False):
    """
    Executa um comando e exibe progresso com strings traduzidas.
    """
    log(f"{description}...", "INFO")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.stdout.strip():
            log(result.stdout.strip(), "INFO", send_webhook=False)
        log(T('operation_success'), "SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        # Tenta pegar a mensagem de erro em inglês para checar se é um erro 'leve' de registro
        error_msg_en = e.stderr.strip() or "System command failed."
        
        # Caso comum: valor/chave de registro não encontrada – usa a string salva no TEXTS
        if "The system was unable to find the specified registry value or key" in error_msg_en:
            log(T('registry_not_found'), "INFO")
            return False

        # Se for um erro real, mostra o que falhou
        msg = e.stderr.strip() or T('system_command_fail')
        level = "ERROR" if critical else "WARNING"
        log(msg, level)
        if critical:
            log(T('critical_error_msg'), "WARNING")
        return False

def confirm_action(title_key: str, explanation_key: str) -> bool:
    """
    Mostra um resumo do que será otimizado e o possível impacto,
    usando chaves do dicionário para título e explicação.
    """
    clear_screen()
    title = T(title_key)
    explanation = T(explanation_key)
    
    print(f"{CYAN}=== {title} ==={RESET}\n")
    print(explanation)
    
    if CURRENT_LANGUAGE == 'en':
        prompt_text = "Enter 'y' to continue or any other key to cancel."
        confirm_key = 'y'
        continue_prompt = "Continue? (y/n): "
    else:
        prompt_text = "Digite 's' para continuar ou qualquer outra tecla para cancelar."
        confirm_key = 's'
        continue_prompt = "Continuar? (s/n): "

    print(f"\n{prompt_text}")
    
    choice = input(continue_prompt).strip().lower()
    
    if choice == confirm_key:
        log(f"{T('action_confirmed')} {title}", "INFO")
        return True
    else:
        log(f"{T('action_cancelled')} {title}", "WARNING")
        input(f"\n{CYAN}{T('press_enter_return_menu')}{RESET}")
        return False

def optimize_startup():
    """Optimize startup programs"""
    if not confirm_action("title_startup", "explanation_startup"):
        return
    log(T('startup_optimization_start'), "INFO")
    
    startup_programs = ["Adobe Updater", "Java Update Scheduler", "Skype", "Spotify", 
                        "Steam", "Discord", "Microsoft Teams", "OneDrive"]
    
    for program in startup_programs:
        command = f'reg delete "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run" /v "{program}" /f'
        description = T('startup_remove_program').format(program)
        run_command(command, description)
    
    log(T('startup_optimization_finish'), "SUCCESS")
    input(f"\n{CYAN}{T('press_enter_return_menu')}{RESET}")

def optimize_registry():
    """Clean and optimize the Windows Registry"""
    if not confirm_action("title_registry", "explanation_registry"):
        return

    log(T('registry_cleanup_start'), "INFO")
    
    registry_commands = [
        'reg delete "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\MyComputer\\NameSpace\\{0DB7E03F-FC29-4DC6-9020-FF41B59E513A}" /f',
        'reg delete "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\MyComputer\\NameSpace\\{B4BFCC3A-DB2C-424C-B029-7FE99A87C641}" /f',
        'reg delete "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\MyComputer\\NameSpace\\{D3162B92-9365-467A-956B-92703ACA08AF}" /f',
        'reg delete "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\MyComputer\\NameSpace\\{f86fa3ab-70d2-4fc7-9c99-fcbf05467f3a}" /f'
    ]
    
    for command in registry_commands:
        run_command(command, T('registry_remove_entry'))
    
    log(T('registry_performance_start'), "INFO")
    
    registry_optimizations = [
        ('HKLM\\SYSTEM\\CurrentControlSet\\Control\\FileSystem', 'NtfsDisableLastAccessUpdate', 1, 'REG_DWORD'),
        ('HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management', 'ClearPageFileAtShutdown', 0, 'REG_DWORD'),
        ('HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management', 'LargeSystemCache', 0, 'REG_DWORD'),
        ('HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer', 'MaxCachedIcons', 2000, 'REG_DWORD'),
        ('HKCU\\Control Panel\\Desktop', 'MenuShowDelay', 200, 'REG_SZ')
    ]
    
    for key, value, data, type in registry_optimizations:
        description = T('registry_adjusting').format(value, key.split('\\')[-1]) # Usa .format com chaves
        command = f'reg add "{key}" /v "{value}" /t {type} /d "{data}" /f'
        run_command(command, description)
    
    log(T('registry_optimization_finish'), "SUCCESS")
    input(f"\n{CYAN}{T('press_enter_return_menu')}{RESET}")

def optimize_disk():
    """Optimize disk performance"""
    if not confirm_action("title_disk", "explanation_disk"):
        return

    system_drive = os.environ.get("SystemDrive", "C:")
    
    log(T('disk_cleanup_temp_start'), "INFO")
    
    temp_paths = [
        f"{system_drive}\\Windows\\Temp\\*.*",
        f"{system_drive}\\Windows\\Prefetch\\*.*",
        f"{system_drive}\\Users\\%USERNAME%\\AppData\\Local\\Temp\\*.*",
        f"{system_drive}\\Users\\%USERNAME%\\AppData\\Local\\Microsoft\\Windows\\INetCache\\*.*"
    ]
    
    for path in temp_paths:
        description = T('disk_cleanning').format(path.split('\\')[-2])
        run_command(f'del /q /s /f "{path}"', description)
    
    log(T('disk_cleanup_start'), "INFO")
    run_command(f'cleanmgr /sagerun:1')
    
    log(T('disk_defrag_start'), "INFO")
    run_command(f'defrag {system_drive} /O')
    
    log(T('disk_optimization_finish'), "SUCCESS")
    input(f"\n{CYAN}{T('press_enter_return_menu')}{RESET}")

def optimize_display():
    """Optimize display settings and refresh rates"""
    if not confirm_action("title_display", "explanation_display"):
        return

    log(T('display_optimization_start'), "INFO")
    
    try:
        import wmi
        c = wmi.WMI()
        for monitor in c.Win32_DesktopMonitor():
            log(T('display_monitor_detected').format(monitor.Name), "INFO")
            log(T('display_rate_optimization').format(monitor.Name), "INFO")
    except ImportError:
        log(T('display_wmi_not_found'), "WARNING")
        log(T('display_basic_optimization'), "INFO")
        
    log(T('display_visual_effects_start'), "INFO")
    
    visual_effects_commands = [
        'reg add "HKCU\\Control Panel\\Desktop" /v "DragFullWindows" /t REG_SZ /d "0" /f',
        'reg add "HKCU\\Control Panel\\Desktop" /v "MenuShowDelay" /t REG_SZ /d "200" /f',
        'reg add "HKCU\\Control Panel\\Desktop\\WindowMetrics" /v "MinAnimate" /t REG_SZ /d "0" /f',
        'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v "ListviewAlphaSelect" /t REG_DWORD /d "0" /f',
        'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v "ListviewShadow" /t REG_DWORD /d "0" /f',
        'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v "TaskbarAnimations" /t REG_DWORD /d "0" /f',
        'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v "VisualFXSetting" /t REG_DWORD /d "3" /f'
    ]
    
    for command in visual_effects_commands:
        run_command(command, T('display_adjusting_effect'))
    
    run_command('rundll32.exe user32.dll,UpdatePerUserSystemParameters', T('display_apply_settings'))
    
    log(T('display_optimization_finish'), "SUCCESS")
    input(f"\n{CYAN}{T('press_enter_return_menu')}{RESET}")

def optimize_network():
    """Optimize network settings"""
    if not confirm_action("title_network", "explanation_network"):
        return

    log(T('network_optimization_start'), "INFO")
    
    network_commands = [
        'netsh int tcp set global autotuninglevel=normal', 'netsh int tcp set global chimney=enabled', 
        'netsh int tcp set global rss=enabled', 'netsh int tcp set global netdma=enabled', 
        'netsh int tcp set global fastopen=enabled', 'netsh int tcp set global ecncapability=enabled', 
        'netsh int tcp set global timestamps=disabled', 'netsh int tcp set global initialRto=2000', 
        'netsh int tcp set global minrto=300', 'netsh int tcp set global maxsynretransmissions=2', 
        'netsh int tcp set global fastopenfallback=enabled', 'netsh int tcp set global hystart=enabled'
    ]
    
    for command in network_commands:
        run_command(command, T('network_adjusting'))
    
    print(f"{CYAN}[INFO]{RESET} {T('network_dns_start')}")
    run_command('netsh interface ip set dns "Ethernet" static 8.8.8.8 primary', T('network_dns_primary_eth'))
    run_command('netsh interface ip add dns "Ethernet" 8.8.4.4 index=2', T('network_dns_secondary_eth'))
    run_command('netsh interface ip set dns "Wi-Fi" static 8.8.8.8 primary', T('network_dns_primary_wifi'))
    run_command('netsh interface ip add dns "Wi-Fi" 8.8.4.4 index=2', T('network_dns_secondary_wifi'))
    
    log(T('network_optimization_finish'), "SUCCESS")
    input(f"\n{CYAN}{T('press_enter_return_menu')}{RESET}")

def optimize_memory():
    """Optimize memory usage"""
    if not confirm_action("title_memory", "explanation_memory"):
        return

    log(T('memory_optimization_start'), "INFO")
    
    memory_commands = [
        'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "ClearPageFileAtShutdown" /t REG_DWORD /d "0" /f',
        'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "LargeSystemCache" /t REG_DWORD /d "0" /f',
        'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management\\PrefetchParameters" /v "EnablePrefetcher" /t REG_DWORD /d "3" /f',
        'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management\\PrefetchParameters" /v "EnableSuperfetch" /t REG_DWORD /d "3" /f'
    ]
    
    for command in memory_commands:
        run_command(command, T('memory_adjusting'))
    
    log(T('memory_cleanup_start'), "INFO")
    run_command('powershell -command "Clear-Content -Path \\"$($env:temp)\\*.tmp\\" -Force -ErrorAction SilentlyContinue"', T('memory_cleanning_temp'))
    
    log(T('memory_optimization_finish'), "SUCCESS")
    input(f"\n{CYAN}{T('press_enter_return_menu')}{RESET}")

def optimize_system():
    """Run system file checker and other system optimizations"""
    if not confirm_action("title_system", "explanation_system"):
        return

    log(T('system_sfc_start'), "INFO")
    run_command('sfc /scannow', T('system_sfc_msg'), critical=True)
    
    log(T('system_dism_start'), "INFO")
    run_command('DISM /Online /Cleanup-Image /CheckHealth', T('system_dism_check'))
    run_command('DISM /Online /Cleanup-Image /ScanHealth', T('system_dism_scan'))
    run_command('DISM /Online /Cleanup-Image /RestoreHealth', T('system_dism_restore'), critical=True)
    
    log(T('system_power_start'), "INFO")
    run_command('powercfg -setactive SCHEME_MIN', T('system_power_high'))
    run_command('powercfg -change -monitor-timeout-ac 0', T('system_power_monitor_ac'))
    run_command('powercfg -change -monitor-timeout-dc 15', T('system_power_monitor_dc'))
    run_command('powercfg -change -standby-timeout-ac 0', T('system_power_standby_ac'))
    run_command('powercfg -change -standby-timeout-dc 60', T('system_power_standby_dc'))
    run_command('powercfg -change -hibernate-timeout-ac 0', T('system_power_hibernate_ac'))
    run_command('powercfg -change -hibernate-timeout-dc 0', T('system_power_hibernate_dc'))
    
    log(T('system_optimization_finish'), "SUCCESS")
    input(f"\n{CYAN}{T('press_enter_return_menu')}{RESET}")

def create_restore_point():
    """Cria um ponto de restauração do sistema."""
    if not confirm_action("title_restore_point", "explanation_restore_point"):
        return

    log(T('restore_point_start'), "INFO")
    cmd = 'powershell -Command "Checkpoint-Computer -Description \\"LithiumOptimizer\\" -RestorePointType \\"MODIFY_SETTINGS\\""'
    if run_command(cmd, T('restore_point_msg')):
        log(T('restore_point_success'), "SUCCESS")
    else:
        log(T('restore_point_fail'), "WARNING")
        
    input(f"\n{CYAN}{T('press_enter_return_menu')}{RESET}")

def optimize_all():
    """Run all optimizations"""
    if not confirm_action("title_optimize_all", "explanation_optimize_all"):
        return

    log(F"{T('optimize_all_start')}", "INFO")
    log(T('optimize_all_restore_point'), "INFO")
    
    cmd_restore = 'powershell -Command "Checkpoint-Computer -Description \\"LithiumOptimizer (Otimização Completa)\\" -RestorePointType \\"MODIFY_SETTINGS\\""'
    run_command(cmd_restore, T('optimize_all_restore_point_msg'))
    
    # Run all optimization functions
    optimize_startup()
    optimize_registry()
    optimize_disk()
    optimize_display()
    optimize_network()
    optimize_memory()
    optimize_system()
    
    log(T('optimize_all_finish'), "SUCCESS")
    input(f"\n{CYAN}{T('press_enter_return_menu')}{RESET}")

def show_system_info():
    """Display system information"""
    clear_screen()
    print(f"{CYAN}=== {T('title_system_info')} ==={RESET}\n")
    
    print(f"{CYAN}{T('sys_os')}{RESET} {platform.system()} {platform.release()}")
    print(f"{CYAN}{T('sys_version')}{RESET} {platform.version()}")
    print(f"{CYAN}{T('sys_arch')}{RESET} {platform.machine()}")
    print(f"{CYAN}{T('sys_processor')}{RESET} {platform.processor()}")
    
    try:
        import psutil
        ram = psutil.virtual_memory()
        print(f"{CYAN}{T('sys_ram_total')}{RESET} {ram.total / (1024 ** 3):.2f} GB")
        print(f"{CYAN}{T('sys_ram_available')}{RESET} {ram.available / (1024 ** 3):.2f} GB")
        print(f"{CYAN}{T('sys_ram_usage')}{RESET} {ram.percent}%")
        
        disk = psutil.disk_usage('/')
        print(f"{CYAN}{T('sys_disk_total')}{RESET} {disk.total / (1024 ** 3):.2f} GB")
        print(f"{CYAN}{T('sys_disk_used')}{RESET} {disk.used / (1024 ** 3):.2f} GB")
        print(f"{CYAN}{T('sys_disk_free')}{RESET} {disk.free / (1024 ** 3):.2f} GB")
        print(f"{CYAN}{T('sys_disk_usage')}{RESET} {disk.percent}%")
        
    except ImportError:
        print(f"{YELLOW}[WARNING]{RESET} {T('sys_psutil_warning')}")
    
    input(f"\n{CYAN}{T('press_enter_return_menu')}{RESET}")


def main_menu():
    """Display the main menu with the new banner"""
    menu_options = [
        T("menu_opt_1"), T("menu_opt_2"), T("menu_opt_3"), T("menu_opt_4"),
        T("menu_opt_5"), T("menu_opt_6"), T("menu_opt_7"), T("menu_opt_8"),
        T("menu_opt_9"), T("menu_opt_10"), T("menu_opt_11")
    ]
    
    while True:
        # Atualiza as opções do menu no loop para garantir que as traduções sejam aplicadas
        menu_options = [
            T("menu_opt_1"), T("menu_opt_2"), T("menu_opt_3"), T("menu_opt_4"),
            T("menu_opt_5"), T("menu_opt_6"), T("menu_opt_7"), T("menu_opt_8"),
            T("menu_opt_9"), T("menu_opt_10"), T("menu_opt_11")
        ]
        
        display_banner()
        print(f"\n{CYAN}{T('menu_title')}{RESET}\n")
        
        for i, option in enumerate(menu_options):
            print(f"  {i+1}. {option}")
        
        print(f"\n{CYAN}{T('menu_option_select')}{RESET}")
        
        try:
            choice = input(f"{CYAN}{T('menu_option_prompt')}{RESET}")
            
            if choice.isdigit():
                choice_num = int(choice)
                
                if choice_num == 1:
                    optimize_startup()
                elif choice_num == 2:
                    optimize_registry()
                elif choice_num == 3:
                    optimize_disk()
                elif choice_num == 4:
                    optimize_display()
                elif choice_num == 5:
                    optimize_network()
                elif choice_num == 6:
                    optimize_memory()
                elif choice_num == 7:
                    optimize_system()
                elif choice_num == 8:
                    create_restore_point()
                elif choice_num == 9:
                    optimize_all()
                elif choice_num == 10:
                    show_system_info()
                elif choice_num == 11:
                    print(f"{CYAN}{T('thank_you_message')}{RESET}")
                    sys.exit(0)
                else:
                    print(f"{RED}[ERRO]{RESET} {T('invalid_option_error')}")
                    time.sleep(1)
            else:
                print(f"{RED}[ERRO]{RESET} {T('invalid_input_error')}")
                time.sleep(1)
                
        except KeyboardInterrupt:
            print(f"\n{CYAN}{T('thank_you_message')}{RESET}")
            sys.exit(0)

if __name__ == "__main__":
    
    # 1. Seleção de Idioma
    select_language()
    
    # 2. Verificação de Admin (agora com strings traduzidas)
    if not check_admin():
        print(f"{YELLOW}[WARNING]{RESET} {T('admin_warning')}")
        print(f"{CYAN}[INFO]{RESET} {T('admin_info_restarting')}")
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        except Exception as e:
            print(f"{RED}[ERRO]{RESET} {T('admin_error_restart').format(e)}")
            print(f"{CYAN}[DETALHE]{RESET} {T('admin_detail')}")
            input(f"\n{CYAN}{T('admin_press_enter_exit')}{RESET}")
        sys.exit(0)

    # 3. Configuração do Webhook
    configure_webhook()

    # 4. Início do Menu Principal
    main_menu()