# Fidelity — case de desenvolvimento

Landing page estática independente. Marca, clientes, compras e recompensa são fictícios. A prévia da primeira dobra é uma ilustração em HTML, não uma captura do sistema original. Os números ilustrativos (3 clientes, 8 compras, 0 resgates) correspondem aos dados iniciais da simulação, não a resultados de negócio.

## Visualizar

No PowerShell, de qualquer diretório:

```powershell
python -m http.server 8080 --bind 127.0.0.1 --directory "D:\GitHub\Client Fidelity System\portfolio"
```

Abra **http://127.0.0.1:8080**. Encerre com `Ctrl+C`. Se a porta estiver ocupada, use outra porta livre. A opção `--directory` é obrigatória: nunca sirva a raiz do repositório. Não é necessário iniciar Django, instalar dependências, fazer build ou configurar variáveis de ambiente.

## Demonstração

1. Ana começa com 3 compras; Lucas com 1; Beatriz com 4. A meta fictícia é de 5 compras.
2. Selecione um cliente: cartão, histórico, situação e contador mostram esse cliente.
3. Registre compras e acompanhe a atualização do cartão. Lucas começa em um cenário fictício de 32 dias sem comprar; uma nova compra atualiza sua sinalização.
4. Ao atingir a meta, o botão de resgate é habilitado. O foco vai para ele para facilitar o uso por teclado.
5. Resgate a recompensa: a contagem do ciclo volta a zero, o total de resgates aumenta e o histórico recente é preservado. O foco retorna a registrar compra.
6. Complete outro ciclo ou mude de cliente; os estados são independentes.
7. Reiniciar restaura **todos** os clientes, históricos, compras e resgates. Recarregar a página produz o mesmo efeito.

O histórico exibe até quatro registros recentes por cliente. A demonstração aceita compras além da meta, como o sistema original. Ao resgatar, todas as compras anteriores deixam a contagem do ciclo; não há transporte de excedentes. O progresso visual é limitado a 100%, com a quantidade real informada no painel e no texto acessível.

Somente a campanha por quantidade é simulada. O produto também possui ciclos mensais consecutivos; o prêmio desses ciclos só libera após o fechamento do último mês, desde que a meta de cada mês tenha sido cumprida. Não há simulação de calendário, cadastro, configuração de campanha ou alteração de tema nesta página.

## Funcionalidades verificadas por leitura de código

Nenhum comando Django foi executado e nenhuma base foi consultada.

| Funcionalidade | Evidência no código original |
| --- | --- |
| Cadastro de clientes | `customers/models.py`: `Customer`; `customers/views.py`: `CustomerCreateView`, `CustomerUpdateView` |
| Registro e histórico de compras | `customers/models.py`: `PurchaseRecord`; `customers/views.py`: `register_purchase`, `CustomerDetailView` |
| Quantidade e ciclos mensais | `loyalty/models.py`: `LoyaltyCampaign`; `loyalty/services.py`: `purchase_count_progress`, `monthly_consecutive_progress` |
| Elegibilidade e resgates | `loyalty/views.py`: `redeem_reward`; `loyalty/services.py`: `purchases_in_current_cycle` |
| Sinalização por recência | `customers/views.py`: `build_customer_month_status`, `CustomerListView` |
| Consulta pública | `customers/views.py`: `CustomerPublicLookupView`, `CustomerPublicProgressView` |
| Identidade por implantação | `company/models.py`: `CompanySettings`; `company/forms.py`: `CompanySettingsForm` |
| Organização modular | Apps `accounts`, `company`, `customers`, `loyalty`, `core`; regras em `loyalty/services.py` |

A configuração única de empresa por deploy corresponde ao modelo de uma instância por empresa. Este case não afirma suporte a múltiplas empresas na mesma instância.

## Contato profissional: pendência

O contato não foi informado. Em `app.js`, preencha `PORTFOLIO_CONFIG.contactUrl` com um endereço profissional confirmado (`mailto:` ou URL absoluta `https://`). O CTA de contratação aparece automaticamente ao configurar um destino válido; até lá, o encerramento informa que o canal está em configuração e mantém o acesso à demonstração. Não foram inventados e-mail, WhatsApp ou GitHub.

## Isolamento e publicação futura

- Arquivos entregues: `index.html`, `styles.css`, `app.js`, `favicon.svg` e este `README.md`.
- Não depende de rotas, autenticação, configurações, dependências ou deploy da aplicação original.
- Não lê banco, `.env`, mídia, credenciais ou dados de clientes. Não faz requisições à produção.
- Não há fontes externas, analytics, bibliotecas, persistência, cookies, formulários de envio ou serviços externos.
- A política CSP restringe recursos à origem local e bloqueia conexões e envios de formulários. Todo conteúdo dinâmico usa `textContent` e criação de elementos.
- Em uma eventual publicação, copie **somente os cinco arquivos desta pasta** para um projeto estático separado. Nunca publique a raiz do repositório nem conecte esta página à produção.
- Nenhum deploy faz parte desta tarefa.

## Acessibilidade e verificação

Idioma português, landmarks e títulos, link para pular conteúdo, foco visível, controles nativos com rótulos, avisos em região `aria-live`, progresso com valores acessíveis e identificação textual dos estados. Layouts adaptáveis para desktop, tablet e celular; suporte a movimento reduzido e cores forçadas. Sem JavaScript, o case permanece legível e os controles da simulação ficam desabilitados com aviso.

Roteiro de conferência: estado inicial → compra → meta → resgate → novo ciclo; independência dos três clientes; bloqueio de resgate antecipado e duplicado; compras acima da meta; reinício global; recarregamento; histórico; sinalização de recência; configuração válida e inválida do contato.

### Resultado da validação — 15/10/2026

- `node --check portfolio/app.js`: sintaxe válida.
- 15 cenários de integração aprovados executando o JavaScript real em um adaptador de DOM: estado inicial, resgate antecipado, compra e progresso, meta e foco, compras acima da meta, resgate e novo ciclo, resgate duplicado, segundo ciclo, seleção e independência dos clientes, recência, reinício global, reinício repetido e nova inicialização, contato ausente, contatos válidos e contatos inválidos.
- HTML com tags balanceadas, 34 IDs únicos, âncoras e referências ARIA/rótulos válidos; recursos exclusivamente locais; controles desabilitados sem JavaScript e aviso `noscript` presente.
- Cinco arquivos independentes em UTF-8, sem caracteres de substituição, controles corrompidos ou links simbólicos; favicon SVG válido.
- Paleta principal de texto conferida por cálculo: contraste mínimo de 4,77:1 entre os pares verificados. Isso não equivale a uma auditoria completa de acessibilidade.
- Nenhuma API de rede, armazenamento, cookies ou inserção de HTML na simulação. A execução dos cenários bloqueia essas APIs para detectar seu uso acidental.
- O manipulador estático padrão do Python, configurado com `portfolio` como raiz, respondeu corretamente aos quatro recursos públicos em teste **offline**, sem abrir sockets. Tentativas de sair da pasta e acessar código do projeto retornaram 404 nesse teste.
- `git diff --exit-code` confirmou que nenhum arquivo rastreado da aplicação original foi modificado. A única entrada nova em `git status` é `portfolio/`.

**Revisão visual pendente:** a ferramenta de navegador falhou antes de abrir a página, informando que não encontrou um diretório necessário da plataforma Windows. A abertura de prévia no aplicativo também falhou. O acesso HTTP local foi bloqueado por `WinError 10013`; o processo temporário do servidor foi encerrado. Não houve revisão visual, teste real de teclado/leitor de tela, aferição de layout em desktop/celular ou captura final. Os breakpoints, estados de foco e recursos acessíveis foram implementados e inspecionados no código, mas não se afirma validação em navegador. Os testes de DOM e do manipulador offline não substituem essa revisão.
