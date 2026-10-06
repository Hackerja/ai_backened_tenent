from sqlalchemy import String, ForeignKey, Text, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from .core.database import Base

from datetime import datetime


class User(Base):
    __tablename__ = "User"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255))

    hash_password: Mapped[str] = mapped_column(String)

    documents: Mapped[list["Document"]] = relationship(back_populates="user")
    document_chunks: Mapped[list["DocumentChunk"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Document(Base):
    __tablename__ = 'Document'

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column()
    file_url: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user_id: Mapped[int] = mapped_column(
        ForeignKey("User.id")
    )

    user: Mapped["User"] = relationship(
        back_populates="documents"
    )
    chunks: Mapped[list["DocumentChunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("Document.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("User.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(384), nullable=False)
    chunk_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    document: Mapped["Document"] = relationship(back_populates="chunks")
    user: Mapped["User"] = relationship(back_populates="document_chunks")