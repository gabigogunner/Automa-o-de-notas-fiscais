import datetime
from datetime import date
import subprocess
import time
import playwright
from playwright.sync_api import sync_playwright
class Pessoa:
    def __init__(self, cpf, senha, codigo, valor_nota, desc_servico, numero_nota, cnpj_tomador):
        self.cpf = cpf
        self.senha = senha
        self.codigo = codigo
        self.valor_nota = valor_nota
        self.numero_nota = numero_nota
        self.cnpj_tomador = cnpj_tomador
        self.desc_servico = desc_servico

    def automacao(self):
        print("Iniciando automação e abrindo o Chrome.")

        #1 CAMINHO DO CHROME
        caminho_chrome = rf"C:\Users\SeuCaminho\AppData\Local\Google\Chrome\Application\chrome.exe" #Copiar o caminho do seu Chrome (Conferir nas propriedades)

        # 2 ABRIR O CHROME DIRETO PELO PYTHON
        subprocess.Popen([
            caminho_chrome,
            "--remote-debugging-port=9222",
            rf"--user-data-dir=C:\TempChrome"
        ])

        time.sleep(1)

        #3 CONECTA O PLAYWRIGHT NO CHROME QUE ACABOU DE ABRIR
        with sync_playwright() as p:
            navegador = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            contexto = navegador.contexts[0]
            pagina = contexto.pages[0]

            #4 MANDA O NAVEGADOR PARA O SITE DA NOTA FISCAL
            pagina.goto("https://www.nfse.gov.br/EmissorNacional/Dashboard")

            #4.1 Espera a página carregar
            pagina.wait_for_load_state("networkidle")

            #5 COMEÇO DA AUTOMAÇÃO

            pagina.locator(".img-govbr").click()
            pagina.wait_for_load_state("networkidle")
            pagina.locator("#accountId").fill(self.cpf)
            pagina.locator(".button-continuar").click()
            pagina.wait_for_load_state("networkidle")
            pagina.locator("#password").fill(self.senha)
            pagina.locator("#submit-button").click()
            pagina.wait_for_load_state("networkidle")
            pagina.locator("#gdd-close-hint").click()
            pagina.locator("#otpInput").fill(self.codigo)
            pagina.locator("#enter-offline-2fa-code").click()
            pagina.wait_for_load_state("networkidle")
            botao_nova_nota = pagina.locator('a[data-original-title="Nova NFS-e"]')
            botao_nova_nota.click()
            pagina.wait_for_load_state("networkidle")
            pagina.locator("#DataCompetencia").fill(date.today().strftime("%d/%m/%Y"))
            pagina.locator("#DataCompetencia").blur() #Isso faz voltar o foco do evento, sem precisar apertar tab
            pagina.get_by_text("Prestador").click()
            # 5.1 Isolando a seção  (painel) do Tomador para o bot não se confundir
            painel_tomador = pagina.locator("#pnlTomador")
            painel_tomador.get_by_text("Brasil", exact=True).click()
            time.sleep(0.2)
            pagina.get_by_text("Prestador").click()
            pagina.locator("#Tomador_Inscricao").fill(self.cnpj_tomador)
            pagina.locator("#Tomador_Inscricao").blur()
            pagina.locator("#btnAvancar").click()
            pagina.wait_for_load_state("networkidle")
            pagina.locator('[aria-controls="select2-LocalPrestacao_CodigoMunicipioPrestacao-container"]').click()
            pagina.locator(".select2-search__field").fill("sao")
            time.sleep(0.5)
            pagina.get_by_role("option", name="São Paulo/SP", exact=True).click()
            pagina.locator('[aria-controls="select2-ServicoPrestado_CodigoTributacaoNacional-container"]').click()
            pagina.locator(".select2-search__field").fill("dati")
            time.sleep(0.5)
            pagina.get_by_role("option", name="17.02.01 - Datilografia, digitação, estenografia e congêneres.", exact=True).click()
            pagina.wait_for_load_state("networkidle")
            time.sleep(0.5)
            pagina.locator('input#ServicoPrestado_HaExportacaoImunidadeNaoIncidencia[value="0"]').evaluate("node => node.click()")
            time.sleep(0.5)
            pagina.locator("#ServicoPrestado_Descricao").fill(self.desc_servico)
            pagina.locator("#ServicoPrestado_Descricao").blur()
            time.sleep(0.5)
            pagina.get_by_role("button", name="Avançar").click()
            pagina.wait_for_load_state("networkidle")
            pagina.locator("#Valores_ValorServico").fill(self.valor_nota)
            pagina.locator("#Valores_ValorServico").blur()
            pagina.locator('input#ValorTributos_TipoValorTributos[value="3"]').evaluate("node => node.click()")
            pagina.get_by_role("button", name="Avançar").click()
            pagina.wait_for_load_state("networkidle")
            pagina.locator("#btnProsseguir").click()
            pagina.wait_for_load_state("networkidle")
            #6 DOWNLOAD DO ARQUIVO
            with pagina.expect_download() as info_download:
                pagina.locator("#btnDownloadDANFSE").click()
            download = info_download.value
            nome_arquivo = rf"C:\PastaQueDesejaSalvar\0{self.numero_nota}-NFS-e-{date.today().strftime("%d/%m/%Y").replace("/","-")}.pdf" #Colocar o caminho que deseja salvar a nota
            download.save_as(nome_arquivo)

            print(f"PDF salvo como: {nome_arquivo}")

            input("Pressione ENTER no terminal do PyCharm para encerrar...")

meu_usuario = Pessoa("000.000.000-00",
                     "Sua senha do GOV",
                     "000000",
                     "0000,00",
                     "Descrição do seu serviço prestado",
                     "1",
                     "00.000.000/0000-00")


meu_usuario.automacao()