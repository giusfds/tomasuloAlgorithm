# Apresentação do Simulador de Tomasulo

Esta pasta contém a apresentação em LaTeX (Beamer) do projeto.

## Compilação

### Linux/macOS

```bash
cd docs
pdflatex presentation.tex
pdflatex presentation.tex  # Segunda vez para resolver referências
```

Ou use o Makefile na raiz do projeto:

```bash
make  # Compila a apresentação
make view  # Visualiza (Linux)
make view-mac  # Visualiza (macOS)
```

### Windows

Opção 1 - Script batch:
```bash
compile_presentation.bat
```

Opção 2 - Manual:
```bash
cd docs
pdflatex presentation.tex
pdflatex presentation.tex
```

## Requisitos

Você precisa ter uma distribuição LaTeX instalada:

- **Linux**: TeX Live
  ```bash
  sudo apt-get install texlive-full
  ```

- **macOS**: MacTeX
  ```bash
  brew install --cask mactex
  ```

- **Windows**: MiKTeX ou TeX Live
  - Download: https://miktex.org/download
  - Ou: https://www.tug.org/texlive/

## Estrutura da Apresentação

A apresentação tem aproximadamente 7 minutos e cobre:

1. **Introdução** (1 min)
   - O que é o Algoritmo de Tomasulo
   - Motivação e objetivos

2. **Arquitetura do Simulador** (1.5 min)
   - Componentes principais
   - Estruturas de dados

3. **Implementação** (1.5 min)
   - Modularização
   - Pipeline de execução

4. **Interface Gráfica** (1 min)
   - Funcionalidades
   - Execução passo a passo

5. **Métricas de Desempenho** (1 min)
   - IPC, ciclos, bolhas
   - Análise de performance

6. **Demonstração** (1 min)
   - Exemplo de código MIPS
   - Execução no simulador

7. **Conclusão** (1 min)
   - Resultados
   - Trabalhos futuros

## Personalização

Edite o arquivo `presentation.tex` para personalizar:

- **Linha 24**: Nome do autor
- **Linha 25**: Nome da universidade
- **Linha 109**: Seu e-mail
- Adicione capturas de tela da GUI se desejar

## Notas para o Apresentador

1. **Slide 1-2**: Introdução rápida, contextualizar o problema
2. **Slide 3-4**: Mostrar arquitetura visual (diagrama)
3. **Slide 5-6**: Explicar implementação técnica
4. **Slide 7-8**: Demonstrar funcionalidades da GUI
5. **Slide 9-10**: Destacar métricas de desempenho
6. **Slide 11-12**: Se possível, fazer demo ao vivo
7. **Slide 13-14**: Conclusão e perguntas

## Dicas

- Pratique a apresentação para manter em ~7 minutos
- Tenha o simulador aberto para demonstração rápida
- Prepare-se para perguntas sobre:
  - Diferenças entre Tomasulo e Scoreboarding
  - Como funciona o register renaming
  - Impacto do ROB na performance
  - Predição de desvios

## Exportar para PowerPoint

Se precisar converter para PowerPoint:

```bash
# Instalar pdf2pptx (requer Python)
pip install pdf2pptx

# Converter
pdf2pptx presentation.pdf presentation.pptx
```

Ou use ferramentas online como:
- https://www.ilovepdf.com/pdf_to_powerpoint
- https://smallpdf.com/pdf-to-ppt

## Licença

Esta apresentação está sob a mesma licença MIT do projeto principal.
