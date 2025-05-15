from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, DateTime, func, Boolean, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

db = SQLAlchemy()
BaseModel = declarative_base()



class BaseModel(db.Model):
    __abstract__ = True  # Prevent this class from being created as a table

    # tbd implement uuid at some point
    created_at = db.Column(DateTime, nullable=False, default=func.current_timestamp())
    updated_at = db.Column(DateTime, nullable=False, default=func.current_timestamp(), onupdate=func.current_timestamp())

class Application(BaseModel):
    __tablename__ = 'Application'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    image = db.Column(db.Text, nullable=True)
    check_hash = db.Column(db.Boolean, default=False, nullable=False)
    multiple_processes = db.Column(db.Boolean, default=False, nullable=False)
    disabled = db.Column(db.Boolean, default=False, nullable=False)
    allow_request_access = db.Column(db.Boolean, default=False, nullable=False)
    # Relationships
    hashes = db.relationship('ApplicationHash', back_populates='application', cascade='all, delete-orphan')
    paths = db.relationship('ApplicationPath', back_populates='application', cascade='all, delete-orphan')
    requests = db.relationship('AccessRequest', back_populates='application', cascade='all, delete-orphan')
    option_groups = db.relationship('ApplicationOptionGroup', back_populates='application', cascade='all, delete-orphan')

class ApplicationHash(BaseModel):
    __tablename__ = 'ApplicationHash'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(240), nullable=True)
    disabled = db.Column(db.Boolean, default=False, nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey('Application.id', ondelete='CASCADE'), nullable=False)
    application = db.relationship('Application', back_populates='hashes')

class ApplicationPath(BaseModel):
    __tablename__ = 'ApplicationPath'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(240), nullable=True)
    disabled = db.Column(db.Boolean, default=False, nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey('Application.id', ondelete='CASCADE'), nullable=False)
    application = db.relationship('Application', back_populates='paths')

class ApplicationOptionGroup(BaseModel):
    __tablename__ = 'ApplicationOptionGroup'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    disabled = db.Column(db.Boolean, default=False, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    application_id = db.Column(db.Integer, db.ForeignKey('Application.id', ondelete='CASCADE'), nullable=False)
    # Relationships
    application = db.relationship('Application', back_populates='option_groups')
    items = db.relationship('ApplicationOptionGroupItem', back_populates='group', cascade='all, delete-orphan')
    access_rights = db.relationship('Access', back_populates='group_access_rights', cascade='all, delete-orphan')

class ApplicationOptionGroupItem(BaseModel):
    __tablename__ = 'ApplicationOptionGroupItem'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('ApplicationOptionGroup.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    value = db.Column(db.String(240), nullable=True)
    sensitive = db.Column(db.Boolean, nullable=False, default=False)
    sensitive_mask = db.Column(db.String(240), nullable=True)
    disabled = db.Column(db.Boolean, default=False, nullable=False)
    group = db.relationship('ApplicationOptionGroup', back_populates='items')

class ClientConfig(BaseModel):
    __tablename__ = 'ClientConfig'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(48), nullable=False, unique=True)
    device_identifier = db.Column(db.String(48), nullable=False, unique=True)
    kiosk = db.Column(db.Boolean, default=False, nullable=True)
    autologout = db.Column(db.Boolean, default=False, nullable=False)
    autologoff_timeout = db.Column(db.Integer, default=300, nullable=True)

class LocalUsers(BaseModel):
    __tablename__ = 'LocalUsers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(48), nullable=False, unique=False)
    username = db.Column(db.String(48), nullable=False, unique=True)
    disabled = db.Column(db.Boolean, default=False, nullable=False)
    info = db.Column(db.String(255), unique=False, nullable=True)
    # email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    password_salt = db.Column(db.String(255), nullable=False)

class AuthSource(BaseModel):
    __tablename__ = 'AuthSource'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(48), nullable=False, unique=True)
    server_type = db.Column(db.String(20), nullable=False) # ldap, radius, ad
    description = db.Column(db.String(255), nullable=True)
    disabled = db.Column(db.Boolean, default=False, nullable=False)
    ssl = db.Column(db.Boolean, default=False, nullable=False)
    port = db.Column(db.Integer, nullable=False)
    host = db.Column(db.String(120), nullable=False)
    bind_user_dn = db.Column(db.String(255), nullable=False)
    bind_password = db.Column(db.String(255), nullable=False)
    base_dn = db.Column(db.String(255), nullable=False)
    ldap_object = db.relationship('LdapObject', backref='auth_source', lazy=True, cascade='all, delete-orphan')

class Access(BaseModel):
    __tablename__ = 'Access'
    id = db.Column(db.Integer, primary_key=True)
    ldap_object_id = db.Column(db.Integer, db.ForeignKey('LdapObject.id', ondelete='CASCADE'), nullable=True)
    access_to = db.Column(db.Integer, db.ForeignKey('ApplicationOptionGroup.id', ondelete='CASCADE'), nullable=False)
    ldap_object = db.relationship('LdapObject', back_populates='accesses')
    group_access_rights = db.relationship('ApplicationOptionGroup', back_populates='access_rights')

class LdapObject(BaseModel):
    __tablename__ = 'LdapObject'
    id = db.Column(db.Integer, primary_key=True)
    auth_source_id = db.Column(db.Integer, db.ForeignKey('AuthSource.id', ondelete='CASCADE'), nullable=False)
    object_type = db.Column(db.String(20), nullable=False) # group, user
    object_uuid = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    ldap_uid = db.Column(db.String(80), nullable=False)
    data_fetched_at = db.Column(DateTime, nullable=False, default=func.current_timestamp())
    two_factor_data = db.Column(db.String(80), nullable=True, default=None)
    accesses = db.relationship('Access', back_populates='ldap_object', cascade='all, delete-orphan')
    access_requests = db.relationship('AccessRequest', back_populates='ldap_object', cascade='all, delete-orphan')

class AccessRequest(BaseModel):
    __tablename__ = 'AccessRequest'
    id = db.Column(db.Integer, primary_key=True)
    ldap_object_id = db.Column(db.Integer, db.ForeignKey('LdapObject.id', ondelete='CASCADE'), nullable=True)
    application_id = db.Column(db.Integer, db.ForeignKey('Application.id', ondelete='CASCADE'), nullable=False)
    ldap_object = db.relationship('LdapObject', back_populates='access_requests')
    application = db.relationship('Application', back_populates='requests')

class ServerConfig(BaseModel):
    __tablename__ = 'ServerConfig'
    id = db.Column(db.Integer, primary_key=True)
    initial = db.Column(db.Boolean, default=True, nullable=False)
    reset = db.Column(db.Boolean, default=False, nullable=False)
    license_key = db.Column(db.String(255), nullable=True)
    license_expirity = db.Column(db.DateTime, nullable=True)

class SyslogServer(BaseModel):
    __tablename__ = 'SyslogServer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    host = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    protocol = db.Column(db.String(10), nullable=False)  # e.g., "tcp", "udp"
    disabled = db.Column(db.Boolean, default=False)

class SmtpServer(BaseModel):
    __tablename__ = 'SmtpServer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    host = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, nullable=False, default=587)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    from_email = db.Column(db.String(255), nullable=False)
    security = db.Column(db.String(10), nullable=False, default="STARTTLS")  # Options: SSL, STARTTLS, NONE
    disabled = db.Column(db.Boolean, default=False, nullable=False)
    

class TwoFaSources(BaseModel):
    __tablename__ = 'TwoFaSources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    host = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, default=443, nullable=False)
    ssl = db.Column(db.Boolean, default=True, nullable=False)
    disabled = db.Column(db.Boolean, default=False, nullable=False)
    type = db.Column(db.String(20), default=False, nullable=False)
    realm = db.Column(db.String(255), nullable=True)
    
class Logs(BaseModel):
    __tablename__ = 'Logs'
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Log timestamp
    level = db.Column(db.String(50), nullable=False)  # Log level (e.g., INFO, ERROR, DEBUG)
    title = db.Column(db.String(50), nullable=True)
    message = db.Column(db.Text, nullable=False)  # Log message
    data = db.Column(db.JSON, nullable=True)  # Additional structured data
    
    def __repr__(self):
        """Representation for debugging purposes."""
        return f"<Logs(id={self.id}, level={self.level})>"

    def as_dict(self):
        """Helper method to serialize the object to a dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "level": self.level,
            "message": self.message,
            "data": self.data
        }
