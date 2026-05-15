from typing import Optional
import datetime
import enum
from sqlalchemy import CheckConstraint, Column, Date, DateTime, Enum, ForeignKeyConstraint, Index, Integer, PrimaryKeyConstraint, String, Table, Text, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

class RolAdministradorParticipanteT(str, enum.Enum):
    ADMINISTRADOR = 'administrador'
    PARTICIPANTE = 'participante'


class Usuarios(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint('id_usuario', name='usuarios_pkey'),
        UniqueConstraint('email', name='usuarios_email_key'),
        UniqueConstraint('username', name='usuarios_username_key')
    )

    id_usuario: int = Field(sa_column=Column('id_usuario', Integer, primary_key=True))
    email: str = Field(sa_column=Column('email', String, nullable=False))
    username: str = Field(sa_column=Column('username', String, nullable=False))
    contraseña: str = Field(sa_column=Column('contraseña', String, nullable=False))
    fecha_de_nacimiento: datetime.date = Field(sa_column=Column('fecha_de_nacimiento', Date, nullable=False))
    fecha_de_alta: datetime.date = Field(sa_column=Column('fecha_de_alta', Date, nullable=False))

    amigos_id_usuario1: list['Amigos'] = Relationship(back_populates='usuarios', sa_relationship_kwargs={'foreign_keys': '[Amigos.id_usuario1]'})
    amigos_id_usuario2: list['Amigos'] = Relationship(back_populates='usuarios_', sa_relationship_kwargs={'foreign_keys': '[Amigos.id_usuario2]'})
    canales: list['Canales'] = Relationship(back_populates='usuarios')
    rol_usuario_canal: list['RolUsuarioCanal'] = Relationship(back_populates='usuarios')
    # salas: list['Salas'] = Relationship(back_populates='usuarios', sa_relationship_kwargs={'secondary': 'usuarios_activos_sala'})
    mensajes_id_usuario_emisor: list['Mensajes'] = Relationship(back_populates='usuarios', sa_relationship_kwargs={'foreign_keys': '[Mensajes.id_usuario_emisor]'})
    mensajes_id_usuario_receptor: list['Mensajes'] = Relationship(back_populates='usuarios_', sa_relationship_kwargs={'foreign_keys': '[Mensajes.id_usuario_receptor]'})


class Amigos(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(['id_usuario1'], ['usuarios.id_usuario'], name='amigos_id_usuario1_fkey'),
        ForeignKeyConstraint(['id_usuario2'], ['usuarios.id_usuario'], name='amigos_id_usuario2_fkey'),
        PrimaryKeyConstraint('id_usuario1', 'id_usuario2', name='amigos_pkey')
    )

    id_usuario1: int = Field(sa_column=Column('id_usuario1', Integer, primary_key=True))
    id_usuario2: int = Field(sa_column=Column('id_usuario2', Integer, primary_key=True))
    fecha_amistad: datetime.datetime = Field(sa_column=Column('fecha_amistad', DateTime, nullable=False))

    usuarios: 'Usuarios' = Relationship(back_populates='amigos_id_usuario1', sa_relationship_kwargs={'foreign_keys': '[Amigos.id_usuario1]'})
    usuarios_: 'Usuarios' = Relationship(back_populates='amigos_id_usuario2', sa_relationship_kwargs={'foreign_keys': '[Amigos.id_usuario2]'})


class Canales(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(['id_usuario_dueno'], ['usuarios.id_usuario'], name='canales_id_usuario_dueno_fkey'),
        PrimaryKeyConstraint('id_canal', name='canales_pkey'),
        UniqueConstraint('nombre', name='canales_nombre_key') 
    )

    id_canal: int = Field(sa_column=Column('id_canal', Integer, primary_key=True))
    id_usuario_dueno: int = Field(sa_column=Column('id_usuario_dueno', Integer, nullable=False))
    nombre: str = Field(sa_column=Column('nombre', String(100), nullable=False))
    contenido_principal: Optional[str] = Field(default=None, sa_column=Column('contenido_principal', Text))

    usuarios: 'Usuarios' = Relationship(back_populates='canales')
    rol_usuario_canal: list['RolUsuarioCanal'] = Relationship(back_populates='canales')
    salas: list['Salas'] = Relationship(back_populates='canales')


class RolUsuarioCanal(SQLModel, table=True):
    __tablename__ = 'rol_usuario_canal'
    __table_args__ = (
        ForeignKeyConstraint(['id_canal'], ['canales.id_canal'], name='rol_usuario_canal_id_canal_fkey'),
        ForeignKeyConstraint(['id_usuario'], ['usuarios.id_usuario'], name='rol_usuario_canal_id_usuario_fkey'),
        PrimaryKeyConstraint('id_usuario', 'id_canal', name='rol_usuario_canal_pkey')
    )

    id_usuario: int = Field(sa_column=Column('id_usuario', Integer, primary_key=True))
    id_canal: int = Field(sa_column=Column('id_canal', Integer, primary_key=True))
    rol: RolAdministradorParticipanteT = Field(sa_column=Column('rol', Enum(RolAdministradorParticipanteT, values_callable=lambda cls: [member.value for member in cls], name='rol_administrador_participante_t'), nullable=False))

    canales: 'Canales' = Relationship(back_populates='rol_usuario_canal')
    usuarios: 'Usuarios' = Relationship(back_populates='rol_usuario_canal')


class Salas(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint("tipo::text = ANY (ARRAY['texto'::character varying, 'voz'::character varying]::text[])", name='salas_tipo_check'),
        ForeignKeyConstraint(['id_canal'], ['canales.id_canal'], name='salas_id_canal_fkey'),
        PrimaryKeyConstraint('id_sala', name='salas_pkey')
    )

    id_sala: int = Field(sa_column=Column('id_sala', Integer, primary_key=True))
    tipo: str = Field(sa_column=Column('tipo', String, nullable=False))
    id_canal: int = Field(sa_column=Column('id_canal', Integer, nullable=False))
    nombre_sala: Optional[str] = Field(default=None, sa_column=Column('nombre_sala', String))

    canales: 'Canales' = Relationship(back_populates='salas')
    # usuarios: list['Usuarios'] = Relationship(back_populates='salas', sa_relationship_kwargs={'secondary': 'usuarios_activos_sala'})
    mensajes: list['Mensajes'] = Relationship(back_populates='salas')


class Mensajes(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(['id_sala'], ['salas.id_sala'], name='mensajes_id_sala_fkey'),
        ForeignKeyConstraint(['id_usuario_emisor'], ['usuarios.id_usuario'], name='mensajes_id_usuario_emisor_fkey'),
        ForeignKeyConstraint(['id_usuario_receptor'], ['usuarios.id_usuario'], name='mensajes_id_usuario_receptor_fkey'),
        PrimaryKeyConstraint('id_mensaje', name='mensajes_pkey'),
        Index('idx_mensajes_emisor', 'id_usuario_emisor'),
        Index('idx_mensajes_fecha', 'fecha'),
        Index('idx_mensajes_sala', 'id_sala')
    )

    id_mensaje: int = Field(sa_column=Column('id_mensaje', Integer, primary_key=True))
    contenido: str = Field(sa_column=Column('contenido', Text, nullable=False))
    id_usuario_emisor: int = Field(sa_column=Column('id_usuario_emisor', Integer, nullable=False))
    fecha: datetime.datetime = Field(sa_column=Column('fecha', DateTime, nullable=False))
    id_sala: Optional[int] = Field(default=None, sa_column=Column('id_sala', Integer))
    id_usuario_receptor: Optional[int] = Field(default=None, sa_column=Column('id_usuario_receptor', Integer))

    salas: Optional['Salas'] = Relationship(back_populates='mensajes')
    usuarios: 'Usuarios' = Relationship(back_populates='mensajes_id_usuario_emisor', sa_relationship_kwargs={'foreign_keys': '[Mensajes.id_usuario_emisor]'})
    usuarios_: Optional['Usuarios'] = Relationship(back_populates='mensajes_id_usuario_receptor', sa_relationship_kwargs={'foreign_keys': '[Mensajes.id_usuario_receptor]'})


# t_usuarios_activos_sala = Table(
#     'usuarios_activos_sala', SQLModel.metadata,
#     Column('id_usuario', Integer, primary_key=True),
#     Column('id_sala', Integer, primary_key=True),
#     ForeignKeyConstraint(['id_sala'], ['salas.id_sala'], name='usuarios_activos_sala_id_sala_fkey'),
#     ForeignKeyConstraint(['id_usuario'], ['usuarios.id_usuario'], name='usuarios_activos_sala_id_usuario_fkey'),
#     PrimaryKeyConstraint('id_usuario', 'id_sala', name='usuarios_activos_sala_pkey')
# )



# ACTUALIZACION + NOTIFICACIONES


# from typing import Optional
# import datetime
# import enum
# from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, Text, UniqueConstraint, ForeignKeyConstraint, PrimaryKeyConstraint, Index
# from sqlalchemy import Enum as SAEnum
# from sqlmodel import Field, Relationship, SQLModel


# # ── ENUMs ──────────────────────────────────────────────────────────────────────

# class EstadoUsuarioT(str, enum.Enum):
#     DESCONECTADO = 'desconectado'
#     CONECTADO    = 'conectado'

# class RolAdministradorParticipanteT(str, enum.Enum):
#     ADMINISTRADOR = 'administrador'
#     PARTICIPANTE  = 'participante'

# class TipoSalaT(str, enum.Enum):
#     TEXTO = 'texto'
#     VOZ   = 'voz'


# # ── TABLAS ─────────────────────────────────────────────────────────────────────

# class Usuarios(SQLModel, table=True):
#     __table_args__ = (
#         UniqueConstraint('email',    name='usuarios_email_key'),
#         UniqueConstraint('username', name='usuarios_username_key'),
#         PrimaryKeyConstraint('id_usuario', name='usuarios_pkey')
#     )

#     id_usuario          : int            = Field(sa_column=Column('id_usuario', Integer, primary_key=True))
#     email               : str            = Field(sa_column=Column('email', String, nullable=False))
#     username            : str            = Field(sa_column=Column('username', String, nullable=False))
#     contrasenha         : str            = Field(sa_column=Column('contrasenha', String, nullable=False))
#     estado              : EstadoUsuarioT = Field(sa_column=Column('estado', SAEnum(EstadoUsuarioT, values_callable=lambda cls: [m.value for m in cls], name='estado_usuario'), nullable=False))
#     fecha_de_nacimiento : datetime.date  = Field(sa_column=Column('fecha_de_nacimiento', Date, nullable=False))
#     fecha_de_alta       : datetime.date  = Field(sa_column=Column('fecha_de_alta', Date, nullable=False))
#     fecha_ultima_conex  : datetime.date  = Field(sa_column=Column('fecha_ultima_conex', Date, nullable=False))

#     amigos_id_usuario1      : list['Amigos']         = Relationship(back_populates='usuarios',  sa_relationship_kwargs={'foreign_keys': '[Amigos.id_usuario1]'})
#     amigos_id_usuario2      : list['Amigos']         = Relationship(back_populates='usuarios_', sa_relationship_kwargs={'foreign_keys': '[Amigos.id_usuario2]'})
#     canales                 : list['Canales']         = Relationship(back_populates='usuarios')
#     rol_usuario_canal       : list['RolUsuarioCanal'] = Relationship(back_populates='usuarios')
#     mensajes_id_usuario_emisor  : list['Mensajes']   = Relationship(back_populates='usuarios',  sa_relationship_kwargs={'foreign_keys': '[Mensajes.id_usuario_emisor]'})
#     mensajes_id_usuario_receptor: list['Mensajes']   = Relationship(back_populates='usuarios_', sa_relationship_kwargs={'foreign_keys': '[Mensajes.id_usuario_receptor]'})
#     usuario_notificacion    : list['UsuarioNotificacion'] = Relationship(back_populates='usuarios')


# class Amigos(SQLModel, table=True):
#     __table_args__ = (
#         ForeignKeyConstraint(['id_usuario1'], ['usuarios.id_usuario'], name='amigos_id_usuario1_fkey'),
#         ForeignKeyConstraint(['id_usuario2'], ['usuarios.id_usuario'], name='amigos_id_usuario2_fkey'),
#         PrimaryKeyConstraint('id_usuario1', 'id_usuario2', name='amigos_pkey')
#     )

#     id_usuario1   : int                = Field(sa_column=Column('id_usuario1', Integer, primary_key=True))
#     id_usuario2   : int                = Field(sa_column=Column('id_usuario2', Integer, primary_key=True))
#     fecha_amistad : datetime.datetime  = Field(sa_column=Column('fecha_amistad', DateTime, nullable=False))

#     usuarios  : 'Usuarios' = Relationship(back_populates='amigos_id_usuario1', sa_relationship_kwargs={'foreign_keys': '[Amigos.id_usuario1]'})
#     usuarios_ : 'Usuarios' = Relationship(back_populates='amigos_id_usuario2', sa_relationship_kwargs={'foreign_keys': '[Amigos.id_usuario2]'})


# class Canales(SQLModel, table=True):
#     __table_args__ = (
#         ForeignKeyConstraint(['id_usuario_dueno'], ['usuarios.id_usuario'], name='canales_id_usuario_dueno_fkey'),
#         UniqueConstraint('nombre', name='canales_nombre_key'),
#         PrimaryKeyConstraint('id_canal', name='canales_pkey')
#     )

#     id_canal            : int           = Field(sa_column=Column('id_canal', Integer, primary_key=True))
#     id_usuario_dueno    : int           = Field(sa_column=Column('id_usuario_dueno', Integer, nullable=False))
#     nombre              : str           = Field(sa_column=Column('nombre', String(100), nullable=False))
#     contenido_principal : Optional[str] = Field(default=None, sa_column=Column('contenido_principal', Text))

#     usuarios          : 'Usuarios'          = Relationship(back_populates='canales')
#     rol_usuario_canal : list['RolUsuarioCanal'] = Relationship(back_populates='canales')
#     salas             : list['Salas']        = Relationship(back_populates='canales')


# class RolUsuarioCanal(SQLModel, table=True):
#     __tablename__ = 'rol_usuario_canal'
#     __table_args__ = (
#         ForeignKeyConstraint(['id_canal'],  ['canales.id_canal'],   name='rol_usuario_canal_id_canal_fkey'),
#         ForeignKeyConstraint(['id_usuario'], ['usuarios.id_usuario'], name='rol_usuario_canal_id_usuario_fkey'),
#         PrimaryKeyConstraint('id_usuario', 'id_canal', name='rol_usuario_canal_pkey')
#     )

#     id_usuario : int                          = Field(sa_column=Column('id_usuario', Integer, primary_key=True))
#     id_canal   : int                          = Field(sa_column=Column('id_canal',   Integer, primary_key=True))
#     rol        : RolAdministradorParticipanteT = Field(sa_column=Column('rol', SAEnum(RolAdministradorParticipanteT, values_callable=lambda cls: [m.value for m in cls], name='rol_administrador_participante_t'), nullable=False))

#     canales  : 'Canales'  = Relationship(back_populates='rol_usuario_canal')
#     usuarios : 'Usuarios' = Relationship(back_populates='rol_usuario_canal')


# class Salas(SQLModel, table=True):
#     __table_args__ = (
#         ForeignKeyConstraint(['id_canal'], ['canales.id_canal'], name='salas_id_canal_fkey'),
#         PrimaryKeyConstraint('id_sala', name='salas_pkey')
#     )

#     id_sala     : int           = Field(sa_column=Column('id_sala', Integer, primary_key=True))
#     tipo        : TipoSalaT     = Field(sa_column=Column('tipo', SAEnum(TipoSalaT, values_callable=lambda cls: [m.value for m in cls], name='tipo_sala_t'), nullable=False))
#     id_canal    : int           = Field(sa_column=Column('id_canal', Integer, nullable=False))
#     nombre_sala : Optional[str] = Field(default=None, sa_column=Column('nombre_sala', String))

#     canales  : 'Canales'       = Relationship(back_populates='salas')
#     mensajes : list['Mensajes'] = Relationship(back_populates='salas')


# class Mensajes(SQLModel, table=True):
#     __table_args__ = (
#         ForeignKeyConstraint(['id_sala'],            ['salas.id_sala'],        name='mensajes_id_sala_fkey'),
#         ForeignKeyConstraint(['id_usuario_emisor'],  ['usuarios.id_usuario'],  name='mensajes_id_usuario_emisor_fkey'),
#         ForeignKeyConstraint(['id_usuario_receptor'],['usuarios.id_usuario'],  name='mensajes_id_usuario_receptor_fkey'),
#         PrimaryKeyConstraint('id_mensaje', name='mensajes_pkey'),
#         Index('idx_mensajes_emisor', 'id_usuario_emisor'),
#         Index('idx_mensajes_fecha',  'fecha'),
#         Index('idx_mensajes_sala',   'id_sala')
#     )

#     id_mensaje          : int                = Field(sa_column=Column('id_mensaje', Integer, primary_key=True))
#     contenido           : str                = Field(sa_column=Column('contenido', Text, nullable=False))
#     id_usuario_emisor   : int                = Field(sa_column=Column('id_usuario_emisor', Integer, nullable=False))
#     fecha               : datetime.datetime  = Field(sa_column=Column('fecha', DateTime, nullable=False))
#     id_sala             : Optional[int]      = Field(default=None, sa_column=Column('id_sala', Integer))
#     id_usuario_receptor : Optional[int]      = Field(default=None, sa_column=Column('id_usuario_receptor', Integer))

#     salas    : Optional['Salas']    = Relationship(back_populates='mensajes')
#     usuarios : 'Usuarios'           = Relationship(back_populates='mensajes_id_usuario_emisor',   sa_relationship_kwargs={'foreign_keys': '[Mensajes.id_usuario_emisor]'})
#     usuarios_: Optional['Usuarios'] = Relationship(back_populates='mensajes_id_usuario_receptor', sa_relationship_kwargs={'foreign_keys': '[Mensajes.id_usuario_receptor]'})
#     notificaciones: Optional['Notificaciones'] = Relationship(back_populates='mensajes')


# class Notificaciones(SQLModel, table=True):
#     __table_args__ = (
#         ForeignKeyConstraint(['id_mensaje'], ['mensajes.id_mensaje'], name='notificaciones_id_mensaje_fkey'),
#         PrimaryKeyConstraint('id_notificacion', name='notificaciones_pkey')
#     )

#     id_notificacion : int               = Field(sa_column=Column('id_notificacion', Integer, primary_key=True))
#     id_mensaje      : int               = Field(sa_column=Column('id_mensaje', Integer, nullable=False))
#     contenido_notif : str               = Field(sa_column=Column('contenido_notif', Text, nullable=False))
#     fecha_creacion  : datetime.datetime = Field(sa_column=Column('fecha_creacion', DateTime, nullable=False))

#     mensajes             : 'Mensajes'                  = Relationship(back_populates='notificaciones')
#     usuario_notificacion : list['UsuarioNotificacion'] = Relationship(back_populates='notificaciones')


# class UsuarioNotificacion(SQLModel, table=True):
#     __tablename__ = 'usuario_notificacion'
#     __table_args__ = (
#         ForeignKeyConstraint(['id_usuario'],      ['usuarios.id_usuario'],              name='usuario_notificacion_id_usuario_fkey'),
#         ForeignKeyConstraint(['id_notificacion'], ['notificaciones.id_notificacion'],   name='usuario_notificacion_id_notificacion_fkey'),
#         PrimaryKeyConstraint('id_usuario', 'id_notificacion', name='usuario_notificacion_pkey')
#     )

#     id_usuario      : int  = Field(sa_column=Column('id_usuario',      Integer, primary_key=True))
#     id_notificacion : int  = Field(sa_column=Column('id_notificacion', Integer, primary_key=True))
#     leida           : bool = Field(sa_column=Column('leida', Boolean, nullable=False, default=False))

#     usuarios       : 'Usuarios'       = Relationship(back_populates='usuario_notificacion')
#     notificaciones : 'Notificaciones' = Relationship(back_populates='usuario_notificacion')