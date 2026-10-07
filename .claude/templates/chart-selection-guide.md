# Escolha de gráficos por objetivo

Avaliação em 07/10/2026 do Lighthouse e do projeto OneSpaWorld: templates Plotly, screens_definition.yaml e componentes das páginas. Referência visual: https://python-graph-gallery.com/best-python-chart-examples/ . A galeria reúne sobretudo exemplos editoriais em Matplotlib; adaptar a linguagem visual para Plotly/Dash, preservando hover, filtros e drill-down. As recomendações abaixo são julgamento aplicado ao projeto, não um ranking fornecido pelo site.

## Aplicação ao OneSpaWorld

| Objetivo | Melhor opção | Decisão e critérios |
|---|---|---|
| RevPATH semanal atual × baseline | Duas linhas na mesma escala | Manter. Distinguir baseline por tracejado e identificar séries diretamente. Ordenar datas e deixar lacunas quando faltar observação. Se houver muitas classes, usar pequenos múltiplos com escala comum. |
| Comparar RevPATH por classe | Barras agrupadas; dumbbell como evolução | Barras já disponíveis permitem comparar valores absolutos. Dumbbell reduz ruído quando houver exatamente duas medidas pareadas e várias classes; exige novo helper e integração ao schema. |
| Priorizar oportunidades/receita por categoria | Barras horizontais ordenadas | `bar_ranking`; mostrar unidade, período e universo do Top N. Lollipop é alternativa visual, sem necessidade funcional imediata. |
| Explicar uma recomendação por drivers SHAP | Barras horizontais divergentes | `diverging_bars`, ordenadas por magnitude absoluta quando a prioridade for relevância. Mostrar sinal, unidade da saída do modelo e referência. Direção positiva não significa necessariamente resultado comercial bom. Para explicação global, média de SHAP absoluto responde outra pergunta e perde o sinal. |
| Elasticidade média por categoria | Barras horizontais com referência em zero | Manter. Informar número de estudos e ponderação. Intervalos só podem ser mostrados se forem calculados; R² não é intervalo de confiança. |
| Elasticidade por categoria × tier | Heatmap retangular | Manter. Uma escala comum entre filtros; representar ausência como ausência, nunca zero. Escala divergente apenas quando existir referência relevante; valores todos negativos podem usar escala sequencial. |
| Desconto pré-cruzeiro × gasto onboard | Dispersão por classificação | `scatter_by_series`, transparência e legenda estável. Informar amostragem de 1.500 pontos. Se houver sobreposição severa, propor densidade/hexbin como nova implementação. Relação observada não prova expansão causal de carteira. |
| Simular preço × volume | Curva de elasticidade com pontos atual/simulado | Manter `elasticity_curve`. Identificar como estimativa do modelo, domínio válido, segmento e hipótese. Evitar agregar curvas de segmentos heterogêneos sem explicar a ponderação. |
| Distribuição de preços, descontos ou elasticidade | Histograma; boxplot por grupo como evolução | Histograma já existe. Boxplot requer novo helper e schema; útil quando médias escondem dispersão e outliers. Violin/ridgeline exigem amostras suficientes e explicação da densidade. |
| Aprovar recomendações | Grid + KPIs + detalhe SHAP | A tabela sustenta a decisão individual. Não acrescentar gráfico decorativo. Funil só serve para coortes que realmente passam pelas mesmas etapas; contagens atuais por status não representam conversão. |
| Configurar guardrails e usuários | Grid/formulário + KPIs | Manter. Gráfico só se houver pergunta analítica definida, como frequência de violações por regra. |

## Biblioteca e pipeline

Já existem helpers para ranking, barras, linhas, área, donut, dispersão, histograma, waterfall, curva de elasticidade, cenários, heatmap, treemap, combo, barras empilhadas/agrupadas, funil, gauge e sparkline. Promovidos nesta revisão: `diverging_bars`, `scatter_by_series` e `with_empty_state`.

Não usar mapas sem pergunta geográfica; gráficos circulares/radar não são prioridade para comparar preços ou impactos com precisão. Para realizado × meta, preferir KPI com referência ou propor bullet chart; gauge ocupa mais espaço. Combo de dois eixos exige unidades explícitas e escalas justificadas; dois painéis alinhados costumam facilitar a interpretação.

Referências específicas dentro da galeria: **Inline labels**, **Line chart with small multiple**, **Horizontal Barplot**, **Dumbell chart**, **Double heatmap for comparison**, **Scatterplot with grouping, highlighting and annotation**, **Histogram with clean color scale and annotation**, **Violin and Boxplot combination**. Usar composição e legibilidade como inspiração, sem copiar ornamentos.

Novos tipos como dumbbell, boxplot, bullet e pequenos múltiplos precisam ser implementados no template, mapeados em `skill07-dash-page.md`, aceitos nas listas canônicas e documentados na agregação de `skill-analytics.md` antes de entrar em roadmaps gerados. `diverging_bars` é helper de detalhes SHAP; não foi adicionado como novo tipo declarativo.

## Contrato para estados vazios

Componentes Dash vazios podem avaliar como falsos. Helpers não devem descartar `html.Div(id=...)` ou outro componente só porque não tem filhos: testar `is not None`. Isso vale para chips à direita de filtros/cards e ações opcionais.

Se grid/gráfico participa de Input, Output ou State, manter seu ID no layout mesmo sem dados: `with_empty_state(component, empty_state(...), df.empty)`. O helper alterna visibilidade dos dois blocos. Ele não popula dados nem resolve sozinho IDs duplicados ou erros de callbacks.

Validar a transição dados → vazio → dados, presença dos IDs, clique de drill-down e remoção dos chips. Verificação estrutural não substitui smoke de navegador para confirmar renderização e eventos.
