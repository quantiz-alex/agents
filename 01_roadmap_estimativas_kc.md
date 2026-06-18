# KC Pricing System: Roadmap Técnico e Estimativas

**Visão Geral:** Sistema proprietário de formação de preços regulares (Sell In) e simulação de impactos em toda a cadeia de valor, parametrizado pelas novas regras da Reforma Tributária. Substitui o uso de Excel/Alteryx/KNIME por um motor auditável que permite decisões de preço ágeis em cenário de incerteza tributária, com base na metodologia do Projeto Harmonização.

**Insumo de origem:** `20260602_KC_Proposta_Sistema.pdf` (especificação funcional, arquitetura do MVP e exemplos de metodologia PTC Médio/High).

**Ponto de partida (acelerador):** já existe um protótipo funcional (`TaxReformSimulator`) que valida a espinha dorsal tributária: cronograma de transição 2026-2033, alíquotas efetivas por ano (ICMS, PIS/COFINS, IBS, CBS), Imposto Seletivo, cascata de cadeia (Indústria → Distribuidor → Varejo) e os cenários **"Mantém Margem"** vs **"Mantém PPC"** (via busca binária). A lógica de negócio core, portanto, **já está provada**. A v0 deixa de ser construção do zero e passa a ser **port para a stack padrão Python/Dash + extensão para a metodologia completa de Pricing (PTC → Margem Cadeia → Sell In)**.

**Decisão de stack:** v0 e v1 na stack que o time já domina (**Python + Dash/Plotly + pandas**, persistência PostgreSQL). Sem React. Isso elimina ramp-up e reduz risco de execução.

---

## 1. Fatiamento do Roadmap

Alinhado aos **dois Sprints do PDF**. O hardening mínimo (testes, reconciliação contábil, auditoria) é absorvido dentro de cada fase, não em uma fase separada.

### Versão v0 (MVP / Sprint 1: Formação de Preço + Simulação)
* **Objetivo:** Entregar o simulador que gera, em segundos, os novos preços Sell In e seus impactos na cadeia ao ajustar parâmetros tributários. Reaproveita a lógica já provada no protótipo.
* **Escopo Funcional:**
  * **Port do motor tributário para Python:** transição 2026-2033, alíquotas efetivas, IBS/CBS, Imposto Seletivo, legado vs reforma, cenários Mantém Margem / Mantém PPC (lógica existente no protótipo).
  * **Extensão para a metodologia de Pricing completa:** PTC (Sell Out) com Capitães e Main-Offenders por canal/região, Price Index e Relatividades, Arquitetura de Produtos, depois Margem da Cadeia por família/canal, depois Sell In com CAPs. (Este é o principal trabalho novo.)
  * **Ingestão manual de bases (offline/Excel) + modelo de dados de portfólio:** Nielsen (Retail e Scantrack), Preços Atuais (ERP), P&L (SAP Hana), Cadastros Gerais (Produtos, Clientes, De-Paras).
  * **Simulação de impactos no portfólio:** Volume, Receita (NIV) e Margem por elo da cadeia.
  * **UI Dash:** parametrização, cascata de formação de preço e visualização de impactos.
* **Renúncias (O que NÃO vamos fazer na v0):**
  * Sem integração automática com ERP/SAP/Nielsen (carga manual via Excel).
  * Sem módulo de Promoção (PTC Low) e sem suite de analytics de tracking.
  * Sem datalake; persistência PostgreSQL simples.
  * Versionamento de cenários e RBAC em forma básica apenas.

### Versão v1 (Sprint 2: Automação, Promoção e Analytics)
* **Objetivo:** Automação plena de dados, novos módulos de receita e preparação para uso recorrente.
* **Escopo Funcional:**
  * **Ingestão e Tratamento de Dados:** construção de datalake e integração plena com o sistema de preços (automatização completa, fim da carga manual).
  * **Módulo Promoção:** mecânica de recomendação de PTC Low (cobertura, profundidade e TP) e cálculo de ROI (Retorno vs TP).
  * **Suite de Análises de Preços:** NRR Tracking (Realizado vs Referência/Target), evolutivo de PTC e Sell In, aderência Sell Out, evolutivo de Market Share, evolutivo TA/TP e Pricing Index Tracking.
* **Melhorias Não-Funcionais:**
  * Orquestração de pipelines, governança, observabilidade e SLA definido.

---

## 2. Estimativa de Prazo por Versão

### v0 (MVP / Sprint 1)

| Entregável | Tamanho | Base (sem) |
|---|---|---|
| Port do motor tributário para Python (a partir do protótipo) | M | 2 |
| Extensão metodologia PTC → Margem Cadeia → Sell In + CAPs | G | 3 |
| Ingestão manual Excel + modelo de dados de portfólio | G | 3 |
| Simulação de impactos no portfólio (Volume/NIV/Margem por elo) | M | 2 |
| UI Dash (parametrização + cascata + impactos) | M | 2 |
| **Subtotal** | | **12 sem** |

* **Nível de Informação do Cliente:** 3 (Multiplicador: x1.0) — protótipo funcional + metodologia detalhada + stack já dominada.
* **Buffer Estrutural (15%):** ~1.8 sem
* **Estimativa Total da Versão (cronograma corrido, squad em paralelo; data science é o caminho crítico):** **8 a 10 semanas**

### v1 (Sprint 2)

| Entregável | Tamanho | Base (sem) |
|---|---|---|
| Datalake + ingestão automatizada plena (ERP/SAP/Nielsen) | GG | 4 |
| Módulo Promoção (PTC Low + ROI) | G | 3 |
| Suite de Analytics (NRR, evolutivos, market share, índices) | G | 3 |
| Governança, observabilidade e performance | M | 2 |
| **Subtotal** | | **12 sem** |

* **Nível de Informação do Cliente:** 2 (Multiplicador: x1.4)
* **Buffer Estrutural (15%):** ~2.5 sem
* **Estimativa Total da Versão:** **12 a 15 semanas**

### Resumo: Esforço x Cronograma

Premissa de squad: até 5 funções técnicas em paralelo + governança on top.

| Métrica | V0 | V1 |
|---|---|---|
| Esforço (sem-homem) — base do contrato | ~29 sem-homem | ~38 sem-homem |
| Cronograma corrido — relógio do cliente | 8–10 sem | 12–15 sem |

* **Esforço total do programa:** ~67 sem-homem (~2.670 horas).
* **Cronograma total do programa:** ~20 a 25 semanas (~5 a 6 meses), admitindo sobreposição parcial entre v0 e v1. Se o foco for somente o MVP (v0), o Go-Live ocorre em **8 a 10 semanas**.

---

## 3. Detalhamento de Requisitos (Foco na v0 / MVP)

### Funcionais
* **[RF01]** Importar bases via Excel/offline: Nielsen Retail e Scantrack, Preços ERP, P&L SAP Hana, Cadastros e De-Paras.
* **[RF02]** Parametrizar regras tributárias (alíquotas, créditos e débitos de PIS/COFINS e ICMS, regime de transição IBS/CBS) que reprecificam todos os passos subsequentes.
* **[RF03]** Definir Capitães e Main-Offenders por canal e região e parametrizar Price Index e Relatividades entre canais.
* **[RF04]** Configurar Arquitetura de Produtos (hierarquias de famílias, embalagens) e Margem da Cadeia por família e canal.
* **[RF05]** Gerar Lista de Preços Sell In na sequência PTC → Margem Cadeia → Sell In, respeitando CAPs e guardrails.
* **[RF06]** Simular impactos em Volume, Receita (NIV) e Margem em cada elo da cadeia de valor.
* **[RF07]** Reproduzir a metodologia de cadeia tributária dos exemplos (PTC Médio e PTC High), incluindo Sell In NF, Sell In NIV, custo de aquisição e markup.

### Não-Funcionais
* **Auditabilidade:** todo preço gerado deve ser rastreável até os parâmetros e bases que o originaram (requisito crítico para área fiscal e comercial).
* **Precisão e Reconciliação:** resultados conferem com a metodologia Harmonização dentro de tolerância contábil definida.
* **Performance:** recálculo completo de um cenário do portfólio em tempo interativo (alvo de segundos, não minutos).
* **Segurança:** dados de P&L e preços são sensíveis; acesso controlado e sem exposição de PII/dados comerciais.
* **Usabilidade:** parametrização sem necessidade de código, operável pelo time de Pricing.

## 4. Próximos Passos (Call to Action)
* **Decisão Arquitetural confirmada:** stack Python + Dash/Plotly + pandas, persistência PostgreSQL, reaproveitando a lógica do protótipo `TaxReformSimulator`. A ser formalizado via ADR (Passo 2 do workflow).
* **Ação Esperada do Cliente:** validar a premissa de squad e fornecer valores de investimento e prazo desejado (ou autorizar uso de placeholders) para a proposta comercial.
