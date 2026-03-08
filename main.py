import jwt
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
import models
import schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Xis do Mateus", version="1.0.0")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


import bcrypt  # Importe isso lá na primeira linha do main.py!


# ==========================================
# ENDPOINTS DE USUÁRIOS (AUTENTICAÇÃO)
# ==========================================
@app.post("/usuarios", response_model=schemas.UsuarioResponse, tags=["Usuários"])
def criar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    """Cadastra um novo usuário criptografando a senha (LGPD)."""

    # 1. Verifica se o e-mail já existe
    usuario_existente = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado!")

    # 2. Criptografa a senha (HASH)
    senha_criptografada = bcrypt.hashpw(usuario.senha.encode('utf-8'), bcrypt.gensalt())

    # 3. Salva no banco
    novo_usuario = models.Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=senha_criptografada.decode('utf-8'),
        perfil=usuario.perfil.upper()
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario


# --- CONFIGURAÇÕES DE SEGURANÇA ---
SECRET_KEY = "chave_super_secreta_do_xis"  # A senha mestra da API
ALGORITHM = "HS256"


@app.post("/auth/login", response_model=schemas.Token, tags=["Autenticação"])
def login(credenciais: schemas.UsuarioLogin, db: Session = Depends(get_db)):
    """Valida o usuário e gera um Token de acesso (JWT)."""

    # 1. Busca o usuário no banco pelo e-mail
    usuario = db.query(models.Usuario).filter(models.Usuario.email == credenciais.email).first()

    # Se não achar o usuário, retorna Erro 401 (Não Autorizado)
    if not usuario:
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos.")

    # 2. Confere se a senha digitada bate com a senha criptografada do banco
    senha_correta = bcrypt.checkpw(credenciais.senha.encode('utf-8'), usuario.senha_hash.encode('utf-8'))
    if not senha_correta:
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos.")

    # 3. Gera o "Crachá Virtual" (Token JWT) válido por 1 hora
    tempo_expiracao = datetime.now(timezone.utc) + timedelta(hours=1)
    dados_token = {
        "sub": usuario.email,
        "perfil": usuario.perfil,
        "exp": tempo_expiracao
    }

    token_jwt = jwt.encode(dados_token, SECRET_KEY, algorithm=ALGORITHM)

    # Devolve o token no formato que o professor pediu no Roteiro
    return {"access_token": token_jwt, "token_type": "Bearer"}
# --- ROTAS DE PRODUTO ---
@app.post("/produtos", response_model=schemas.Produto, tags=["Produtos"])
def criar_produto(produto: schemas.ProdutoCreate, db: Session = Depends(get_db)):
    novo_produto = models.Produto(**produto.model_dump())
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return novo_produto


@app.get("/produtos", response_model=list[schemas.Produto], tags=["Produtos"])
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(models.Produto).all()


# --- ROTAS DE PEDIDO (MULTICANALIDADE) ---
@app.post("/pedidos", response_model=schemas.PedidoResponse, tags=["Pedidos"])
def criar_pedido(pedido: schemas.PedidoCreate, db: Session = Depends(get_db)):
    # 1. Valida se o canal é permitido
    canais_permitidos = ["APP", "TOTEM", "BALCAO", "WEB"]
    if pedido.canalPedido.upper() not in canais_permitidos:
        raise HTTPException(status_code=400, detail="Canal inválido. Use APP, TOTEM, BALCAO ou WEB.")

    # 2. Cria o pedido vazio
    novo_pedido = models.Pedido(canalPedido=pedido.canalPedido.upper())
    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)

    # 3. Adiciona os itens e calcula o total
    total_pedido = 0.0
    for item in pedido.itens:
        produto_db = db.query(models.Produto).filter(models.Produto.id == item.produto_id).first()
        if not produto_db:
            raise HTTPException(status_code=404, detail=f"Produto ID {item.produto_id} não encontrado!")

        preco = produto_db.preco
        total_pedido += preco * item.quantidade

        novo_item = models.ItemPedido(
            pedido_id=novo_pedido.id,
            produto_id=produto_db.id,
            quantidade=item.quantidade,
            preco_unitario=preco
        )
        db.add(novo_item)

    # 4. Atualiza o total do pedido e salva
    novo_pedido.total = total_pedido
    db.commit()
    db.refresh(novo_pedido)

    return novo_pedido


@app.get("/pedidos", response_model=list[schemas.PedidoResponse], tags=["Pedidos"])
def listar_pedidos(canalPedido: str = None, db: Session = Depends(get_db)):
    """Lista pedidos. Permite filtrar por canal (Ex: ?canalPedido=APP)"""
    query = db.query(models.Pedido)
    if canalPedido:
        query = query.filter(models.Pedido.canalPedido == canalPedido.upper())
    return query.all()


# --- ROTA DE PAGAMENTO MOCK (FLUXO CRÍTICO) ---
@app.post("/pedidos/{pedido_id}/pagar", tags=["Pagamentos"])
def simular_pagamento(pedido_id: int, pagamento: schemas.PagamentoMock, db: Session = Depends(get_db)):
    """Simula um gateway de pagamento externo."""
    # 1. Busca o pedido no banco
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado!")

    if pedido.status != "CRIADO":
        raise HTTPException(status_code=400, detail=f"O pedido já está com status: {pedido.status}")

    # 2. Simula a resposta do banco/cartão
    if pagamento.sucesso:
        pedido.status = "PAGO"
        mensagem = f"Pagamento via {pagamento.forma_pagamento} aprovado!"
    else:
        pedido.status = "PAGAMENTO_RECUSADO"
        mensagem = f"Pagamento via {pagamento.forma_pagamento} recusado pelo banco."

    # 3. Salva o novo status no banco
    db.commit()
    db.refresh(pedido)

    return {
        "pedido_id": pedido.id,
        "status_atual": pedido.status,
        "mensagem_gateway": mensagem
    }