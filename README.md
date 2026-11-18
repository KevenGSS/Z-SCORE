# 🛡️ Auditoria Inteligente de Faturamento (Z-Score Móvel)

> **Projeto de Portfólio & Prova de Conceito (PoC)** desenvolvido por **Keven Soares** (**K Consultoria em Tecnologia**) para demonstrar a aplicação prática de estatística e engenharia de dados na auditoria automatizada de séries temporais financeiras.

---

## 🎯 O Problema de Negócio

Na maioria das operações corporativas, a conferência de faturamento depende de revisões manuais ou de regras fixas (ex: *"alertar se o faturamento diário ficar abaixo de um teto estático"*). Em empresas reais com crescimento contínuo ou sazonalidade (picos de fim de semana), médias fixas geram dois gargalos graves:

* **Falsos Positivos:** Conforme a operação cresce, limites antigos disparam alarmes desnecessários o tempo todo.
* **Cegueira Operacional:** Uma falha de integração entre PDV e ERP ou ruptura de estoque pode derrubar as vendas de um dia em 60%, mas o valor ainda passa despercebido por ficar acima da média histórica antiga.

---

## 🧠 Como Funciona a Solução (Motor Estatístico)

Para resolver esse problema sem depender de modelos opacos de Machine Learning, implementei o método **Z-Score Móvel Deslocado (*Shifted Rolling Z-Score*)**:

$$Z_t = \frac{X_t - \mu_{t-1}}{\sigma_{t-1}}$$

### Diferenciais Técnicos da Implementação:
* **Janela Móvel Dinâmica (*Rolling Window*):** Recalcula continuamente a média ($\mu$) e o desvio-padrão ($\sigma$) com base apenas nos últimos $N$ dias (configurável de 7 a 30 dias), adaptando-se ao ritmo atual.
* **Prevenção de Contaminação (`shift(1)`):** O faturamento de hoje ($X_t$) é julgado estritamente contra o histórico fechado até ontem ($t - 1$). Isso impede que um erro grave de digitação ou lote duplicado distorça a própria régua estatística no dia em que ocorre.
* **Relatório Executivo em Excel (`.xlsx`):** Exportação nativa das anomalias isoladas com cálculo do impacto financeiro em reais (`R$`) e diagnóstico automatizado.

---

## 🔒 Privacidade e Segurança dos Dados

Esta aplicação foi desenvolvida com foco total na segurança da informação corporativa:
* **Processamento 100% em Memória (RAM):** Os dados enviados via upload de planilhas são processados estritamente na memória volátil da sessão. **Nenhum dado é salvo em banco de dados, gravado em disco ou compartilhado com terceiros.**
* **Auditoria Aberta:** Como o código-fonte é 100% aberto neste repositório, qualquer equipe técnica pode inspecionar o script e verificar essa blindagem. 
* *Boa Prática:* Para testes com dados reais de empresas, recomendamos a anonimização prévia dos registros.

---

## 🚀 Como Executar Localmente

### 1. Clone o repositório
```bash
git clone [https://github.com/KevenGSS/Z-SCORE.git](https://github.com/KevenGSS/Z-SCORE.git)
cd Z-SCORE
