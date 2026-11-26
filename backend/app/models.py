from datetime import date, datetime
from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class Usuario(Base):
    """Titular de los datos de recetas, retiros y tramites."""

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    telefono: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    canal_aviso: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="push"
    )
    tamano_letra: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="grande"
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    eliminado_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    medicos: Mapped[list["Medico"]] = relationship(back_populates="usuario")
    sedes_pami: Mapped[list["SedePami"]] = relationship(back_populates="usuario")
    medicamentos: Mapped[list["Medicamento"]] = relationship(back_populates="usuario")
    ordenes_receta: Mapped[list["OrdenReceta"]] = relationship(back_populates="usuario")
    eventos_tramite: Mapped[list["EventoTramite"]] = relationship(back_populates="usuario")
    alertas: Mapped[list["Alerta"]] = relationship(back_populates="usuario")


class Medico(Base):
    """Medicos de cabecera o especialistas asociados a un usuario."""

    __tablename__ = "medicos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(40), nullable=True)
    lugar: Mapped[str | None] = mapped_column(String(200), nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    eliminado_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="medicos")
    ordenes_receta: Mapped[list["OrdenReceta"]] = relationship(back_populates="medico")


class SedePami(Base):
    """Agencias o sedes de PAMI donde el usuario realiza sus tramites."""

    __tablename__ = "sedes_pami"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    direccion: Mapped[str] = mapped_column(String(200), nullable=False)
    horarios: Mapped[str | None] = mapped_column(String(150), nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(40), nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    eliminado_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="sedes_pami")


class Medicamento(Base):
    """Remedios del usuario con su dosis diaria e indicacion."""

    __tablename__ = "medicamentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    dosis_diaria: Mapped[str] = mapped_column(String(120), nullable=False)
    indicacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    eliminado_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="medicamentos")
    ordenes_receta: Mapped[list["OrdenReceta"]] = relationship(
        back_populates="medicamento"
    )
    eventos_tramite: Mapped[list["EventoTramite"]] = relationship(
        back_populates="medicamento"
    )


class OrdenReceta(Base):
    """Orden emitida por un medico para un medicamento (contiene 1 o 3 recetas)."""

    __tablename__ = "ordenes_receta"
    __table_args__ = (
        CheckConstraint(
            "cantidad_recetas IN (1, 3)",
            name="ck_ordenes_receta_cantidad_valida",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    medico_id: Mapped[int | None] = mapped_column(
        ForeignKey("medicos.id", ondelete="SET NULL"), nullable=True, index=True
    )
    medicamento_id: Mapped[int] = mapped_column(
        ForeignKey("medicamentos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    fecha_emision: Mapped[date] = mapped_column(Date, nullable=False)
    cantidad_recetas: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="1"
    )
    origen: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default="manual"
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    eliminado_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="ordenes_receta")
    medico: Mapped["Medico | None"] = relationship(back_populates="ordenes_receta")
    medicamento: Mapped["Medicamento"] = relationship(back_populates="ordenes_receta")
    recetas: Mapped[list["Receta"]] = relationship(
        back_populates="orden", cascade="all, delete-orphan"
    )


class Receta(Base):
    """Cada una de las recetas individuales (1 a 3) dentro de una orden."""

    __tablename__ = "recetas"
    __table_args__ = (
        CheckConstraint("numero BETWEEN 1 AND 3", name="ck_recetas_numero_valido"),
        CheckConstraint(
            "vigente_hasta >= vigente_desde",
            name="ck_recetas_rango_vigencia_valido",
        ),
        UniqueConstraint("orden_id", "numero", name="uq_recetas_orden_numero"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    orden_id: Mapped[int] = mapped_column(
        ForeignKey("ordenes_receta.id", ondelete="CASCADE"), nullable=False, index=True
    )
    numero: Mapped[int] = mapped_column(Integer, nullable=False)
    vigente_desde: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    vigente_hasta: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="disponible", index=True
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    eliminado_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    orden: Mapped["OrdenReceta"] = relationship(back_populates="recetas")
    retiros: Mapped[list["Retiro"]] = relationship(back_populates="receta")


class Retiro(Base):
    """Registro de retiro de un medicamento en farmacia asociado a una receta."""

    __tablename__ = "retiros"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    receta_id: Mapped[int] = mapped_column(
        ForeignKey("recetas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    fecha_retiro: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    farmacia: Mapped[str | None] = mapped_column(String(150), nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    eliminado_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    receta: Mapped["Receta"] = relationship(back_populates="retiros")


class EventoTramite(Base):
    """Registro de autorizaciones en PAMI (6 meses) y pedidos de receta al medico (3 meses)."""

    __tablename__ = "eventos_tramite"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('autorizacion_pami', 'pedido_receta')",
            name="ck_eventos_tramite_tipo_valido",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    medicamento_id: Mapped[int | None] = mapped_column(
        ForeignKey("medicamentos.id", ondelete="SET NULL"), nullable=True, index=True
    )
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    proximo_vencimiento: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    eliminado_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="eventos_tramite")
    medicamento: Mapped["Medicamento | None"] = relationship(
        back_populates="eventos_tramite"
    )


class Alerta(Base):
    """Avisos programados y generados por el motor de reglas."""

    __tablename__ = "alertas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    referencia: Mapped[str | None] = mapped_column(String(100), nullable=True)
    programada_para: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    canal: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="push"
    )
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="pendiente", index=True
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    eliminado_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="alertas")
