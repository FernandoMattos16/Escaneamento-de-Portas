# Port Scanner - Interface Gráfica

## Descrição
Este é um **scanner de portas TCP e UDP** com interface gráfica em **Python e PyQt5**. Ele permite escanear um host ou rede, identificar serviços e exibir banners de resposta.

## Funcionalidades
- **Escaneia portas TCP e UDP**
- **Interface amigável** (GUI em PyQt5)
- **Filtragem de resultados** (Abertas, Fechadas, Filtradas)
- **Detecção de banners** para identificar sistemas operacionais
- **Exibe serviços conhecidos**
- **Barra de progresso** para acompanhamento do escaneamento

## Instalação
Antes de rodar o programa, instale as dependências executando:

```
pip install -r requirements.txt
```

## Como Usar
1. Execute o programa com o comando:

    ```
   python portscanner.py
    ```

2. Digite o IP ou domínio
3. Escolha a faixa de portas
4. Selecione TCP ou UDP
5. Clique em "Iniciar Escaneamento"
6. Analise os resultados na tabela

---