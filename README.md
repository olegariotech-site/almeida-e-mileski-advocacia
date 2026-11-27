# Almeida e Mileski Advocacia — V0.4 Signature Legal Experience

Prévia institucional estática desenvolvida pela OLEGARIO TECH. **Branch de desenvolvimento; sem autorização de merge, deploy ou indexação.**

## Visualizar localmente

Requer Python 3.10+. O site gerado não depende de JavaScript, internet ou Node para apresentar seu conteúdo.

```bash
python3 scripts/build.py
python3 scripts/check.py
python3 scripts/serve.py
```

Abrir `http://127.0.0.1:8765/`. O servidor também simula a prévia de projeto em `http://127.0.0.1:8765/almeida-e-mileski-advocacia/`.

Também é possível abrir `dist/index.html` diretamente. O servidor é recomendado para verificar 404 e navegação por diretórios. A propagação opcional de UTMs foi projetada para HTTP(S).

## Arquitetura

| Página | URL relativa |
| --- | --- |
| Home | `/` |
| O escritório | `/o-escritorio/` |
| As advogadas | `/as-advogadas/` |
| Imobiliário e Condominial | `/areas/direito-imobiliario-e-condominial/` |
| Família e Sucessões | `/areas/direito-de-familia-e-sucessoes/` |
| Bancário | `/areas/direito-bancario/` |
| Consumidor | `/areas/direito-do-consumidor/` |
| Previdenciário e Assistencial | `/areas/direito-previdenciario-e-assistencial/` |
| Conteúdos e orientações | `/conteudos/` |
| Contato | `/contato/` |
| Privacidade | `/politica-de-privacidade/` |
| Página de erro | `/404.html` |

`content/areas.json` contém as cinco áreas, 26 grupos e 123 atividades institucionais. `scripts/build.py` gera HTML completo com navegação e metadados individuais. `assets/css/site.css` e `assets/js/site.js` contêm estilos reutilizáveis e melhorias progressivas. JavaScript não é necessário para consultar áreas, expandir os controles nativos ou navegar.

## Superfície de publicação

O único diretório elegível para futura hospedagem é **`dist/`**, gerado por allowlist. Nunca publicar a raiz do repositório. Documentos de reunião da versão anterior foram retirados desta branch e continuam preservados no histórico e no snapshot. Relatórios de revisão e documentos fornecidos não entram em `dist/`.

Não há workflow de deploy, alteração em Pages, DNS ou domínio nesta entrega. Qualquer futura publicação deve enviar exclusivamente o conteúdo de `dist/` como artefato estático; a escolha ou alteração da hospedagem depende de autorização separada.

Todas as 12 páginas mantêm `noindex,nofollow`. A 404 é independente de CSS e caminhos relativos, funciona em profundidade arbitrária e detecta o prefixo padrão do repositório com JavaScript. Sem JavaScript, a 404 oferece os caminhos para o domínio próprio e para a prévia de apresentação. Não existe sitemap, canonical de produção, Organization/LegalService com dados não confirmados ou indexação antecipada.

## Conteúdo e decisões provisórias

- Cíntia: OAB/SP 541.172; cursos apresentados como **em andamento**; participação no IBDFAM conforme documento.
- Sócia Mileski: OAB/PR 59.635 e OAB/SP 452.260 (suplementar). O nome permanece neutro na interface até resolver Karine/Karime e nome completo. A denominação não confirmada do curso de Fundamentos do Direito foi reservada à revisão.
- Cinco áreas, sem criar página independente de Direito Civil.
- Marca e fotografias da V0.3 preservadas. A imagem conjunta tem enquadramento CSS que não exibe a faixa com nome divergente; a legenda informa que é composição digital para aprovação.
- A marca visual existente mantém Almeida e Mileski. A adoção de CK na denominação depende de validação.
- Endereço e WhatsApp herdados da V0.3; nenhuma nova indicação geográfica ou informação de contato foi inventada. Validar os dados finais antes da publicação.
- O trecho sobre saúde/seguros foi editado para retirar formulação de garantia, mantendo cobertura, tratamentos, reajustes e cancelamento como assuntos sujeitos à análise. Revisão jurídica final pendente.

## Movimento, acessibilidade e privacidade

Accordions nativos `details/summary`, foco visível, menu com Escape e devolução do foco, sumário contextual, controles para expandir/recolher e anúncio do resultado em região de status. Não se duplicam estados ARIA nativos dos controles. Conteúdo permanece visível sem observador ou sem JS. Movimento respeita `prefers-reduced-motion`; rolagem natural, sem preloader e sem parallax.

Fontes Bodoni Moda locais, sob SIL OFL, com licença em `assets/fonts/OFL.txt`. Fotografias WebP responsivas; prioridade alta na imagem principal e lazy loading nos retratos. Sem frameworks, coleta, cookies, storage, pixels ou analytics. UTMs permitidas são copiadas apenas entre URLs internas; não são persistidas nem enviadas nos links de WhatsApp.

## Verificação reproduzível

```bash
npm ci
npx playwright install chromium firefox webkit
npm test -- /caminho/para/evidencias
```

O verificador inicia e encerra seu próprio servidor local, testa as 12 páginas nas larguras 320, 390, 768, 1366 e 1920, registra auditorias axe, navegação sem JS, teclado, movimento reduzido, links, dois prefixos, contatos e ausência de rastreamento. Para usar um Chromium disponível no ambiente, informar `CHROMIUM_EXECUTABLE`. Para usar o binário empacotado para ambientes de teste, informar `SPARTICUZ_CHROMIUM=1`. A versão e as condições reais de cada navegador devem constar no relatório; metas Lighthouse e WCAG não constituem certificação automática.

```bash
npm run benchmark -- /caminho/para/evidencias-de-pesquisa
```

O benchmarking registra o que foi efetivamente observado e suas limitações. Referências internacionais orientam a organização das informações; textos, marcas, fotografias e código de terceiros não integram o site.

## Rollback

Baseline: `d734034b6a6b7a06d35d1bf0cfdbbdd37b25d690`. Referência remota preservada: `snapshot/v03-before-v04`. A `main` permanece nesse baseline durante o desenvolvimento.

Nesta etapa, rollback significa descartar ou fechar a branch/PR de desenvolvimento; não há implantação para reverter. Se uma futura publicação for autorizada, preservar o artefato implantado e o SHA antes da operação. Para recuperar os arquivos da V0.3 em um checkout separado:

```bash
git worktree add ../almeida-mileski-v03 snapshot/v03-before-v04
```

Não executar reset forçado da main ou comandos de publicação como parte desta entrega.
