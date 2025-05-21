import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, DateTime, Enum, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as PyEnum

db = SQLAlchemy()

class Climate(PyEnum):  
    SUNNY = "SUNNY"
    CLOUDY = "CLOUDY"
    RAINY = "RAINY"
    WINDY = "WINDY"
    STORMY = "STORMY"

class Gender(PyEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class VehicleType(PyEnum):
    CAR = "CAR"
    MOTORCYCLE = "MOTORCYCLE"
    TRUCK = "TRUCK"


favorite_planets = Table(
    "favorite_planets",
    db.Model.metadata,
    db.Column("user_id", db.Integer, ForeignKey("user.id"), primary_key=True),
    db.Column("planet_id", db.Integer, ForeignKey("planet.id"), primary_key=True)
)

favorite_characters = Table(
    "favorite_characters",
    db.Model.metadata,
    db.Column("user_id", db.Integer, ForeignKey("user.id"), primary_key=True),
    db.Column("character_id", db.Integer, ForeignKey("character.id"), primary_key=True)
)

favorite_vehicles = Table(
    "favorite_vehicles",
    db.Model.metadata,
    db.Column("user_id", db.Integer, ForeignKey("user.id"), primary_key=True),
    db.Column("vehicle_id", db.Integer, ForeignKey("vehicle.id"), primary_key=True)
)

class Planet(db.Model):
    __tablename__ = "planet"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[int] = mapped_column(nullable=False)
    climate: Mapped[Climate] = mapped_column(Enum(Climate), nullable=False)
    gravity: Mapped[bool] = mapped_column(Boolean())

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "size": self.size,
            "climate": self.climate.value,
            "gravity": self.gravity
        }

class Character(db.Model):
    __tablename__ = "character"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)
    gender: Mapped[Gender] = mapped_column(Enum(Gender), nullable=False)
    

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender.value
        }
    
class Vehicle(db.Model):
    __tablename__ = "vehicle"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    cargo_capacity: Mapped[int] = mapped_column(nullable=False)
    model: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[VehicleType] = mapped_column(Enum(VehicleType), nullable=False)

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "cargo_capacity": self.cargo_capacity,
            "model": self.model,
            "type": self.type.value
        }

class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    lastname: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    created_date: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    favorite_planets: Mapped[list["Planet"]] = relationship(
        "Planet",
        secondary=favorite_planets,
        backref="fans"
    )
    favorite_characters: Mapped[list["Character"]] = relationship(
        "Character",
        secondary=favorite_characters,
        backref="fans"
    )
    favorite_vehicles: Mapped[list["Vehicle"]] = relationship(
        "Vehicle",
        secondary=favorite_vehicles,
        backref="fans"
    )

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "lastname": self.lastname,
            "created_date": self.created_date.isoformat(),
            "email": self.email,
            "favorite_planets": [planet.name for planet in self.favorite_planets],
            "favorite_characters": [character.name for character in self.favorite_characters],
            "favorite_vehicles": [vehicle.name for vehicle in self.favorite_vehicles]
        }