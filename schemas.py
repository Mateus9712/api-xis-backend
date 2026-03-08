from pydantic import BaseModel
from pydantic import BaseModel, EmailStr

# --- USUÁRIOS (SEGURANÇA E LGPD) ---
class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str
    perfil: str = "CLIENTE"

class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    perfil: str
    # Repare que NÃO colocamos a senha aqui! Essa é a essência da LGPD na API.
    class Config:
        from_attributes = True

# ... (Mantenha os esquemas de Produto, Pedido e Pagamento que já tínhamos) ...

# --- PRODUTOS ---
class ProdutoBase(BaseModel):
    nome: str
    descricao: str
    preco: float

class ProdutoCreate(ProdutoBase):
    pass

class Produto(ProdutoBase):
    id: int
    class Config:
        from_attributes = True

# --- ITENS DO PEDIDO ---
class ItemPedidoCreate(BaseModel):
    produto_id: int
    quantidade: int

class ItemPedidoResponse(BaseModel):
    produto_id: int
    quantidade: int
    preco_unitario: float
    class Config:
        from_attributes = True

# --- PEDIDOS ---
class PedidoCreate(BaseModel):
    canalPedido: str  # Ex: "APP", "TOTEM"
    itens: list[ItemPedidoCreate]

class PedidoResponse(BaseModel):
    id: int
    canalPedido: str
    status: str
    total: float
    itens: list[ItemPedidoResponse]
    class Config:
        from_attributes = True
# --- PAGAMENTO MOCK ---
class PagamentoMock(BaseModel):
    forma_pagamento: str # Ex: PIX, CARTAO
    sucesso: bool        # True para simular aprovação, False para simular recusa
# --- AUTENTICAÇÃO (LOGIN) ---
class UsuarioLogin(BaseModel):
    email: str
    senha: str

class Token(BaseModel):
    access_token: str
    token_type: str