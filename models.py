from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    email = Column(String, unique=True, index=True)
    senha_hash = Column(String) # Aqui guardaremos a senha criptografada!
    perfil = Column(String, default="CLIENTE") # Pode ser CLIENTE, GERENTE ou ADMIN

# ... (Mantenha as tabelas Produto, Pedido e ItemPedido exatamente como estavam) ...
class Produto(Base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    descricao = Column(String)
    preco = Column(Float)

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True, index=True)
    canalPedido = Column(String)
    status = Column(String, default="CRIADO")
    total = Column(Float, default=0.0)
    itens = relationship("ItemPedido", back_populates="pedido")

class ItemPedido(Base):
    __tablename__ = "itens_pedido"
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    quantidade = Column(Integer)
    preco_unitario = Column(Float)
    pedido = relationship("Pedido", back_populates="itens")
    produto = relationship("Produto")