# 🍔 API Raízes do Nordeste

Projeto de Back-end para a rede de lanchonetes gaúcha, focado em multicanalidade e segurança.

## 🛠️ Como o professor deve testar:
1. Instalar as bibliotecas: `pip install fastapi uvicorn sqlalchemy bcrypt pyjwt`
2. Rodar o servidor: `uvicorn main:app --reload`
3. Acesssar o link http://127.0.0.1:8000/docs
4. Testar os 10 cenários no Postman usando o arquivo `testes_xis.json` que está nesta pasta.

## 🛡️ Destaques de Segurança e LGPD:
* Senhas protegidas com BCrypt.
* Login seguro com Token JWT.
