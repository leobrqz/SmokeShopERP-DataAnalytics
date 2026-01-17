## Como usar o software
Passo a passo simples para executar o softwaree  configurar o banco de dados.

## Banco de dados

- Criar um banco de dados chamado TabacariaDB no PostgreSQL
- Criar um .env com DB_PASSWORD=sua_senha
- Rode o script mock_data.py para gerar dados de exemplo


### Executável Pyinstaller

- Execute o .exe
- Clique em "Conectar" para configurar o banco de dados

Para compilar manualmente, instale o Pyinstaller:
```bash
pip install pyinstaller
```
E execute o seguinte comando:
```bash
./build_exe.sh
```

### Python
Execute o seguinte comando para instalar as dependências:
```bash
pip install -r requirements.txt
```
- Configure o .env com a senha do banco de dados
```bash
python mock_data.py
```
- Execute o seguinte comando para executar o software:
```bash
python main.py
```