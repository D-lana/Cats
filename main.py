from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
# import json
import uuid
import psycopg2
import psycopg2.extras
from config import *

app = FastAPI()

class Cat(BaseModel):
	name: str
	breed: Optional[str] = None
	# cat_id: str

# Создаем БД для хранения информации о котах
#################################
connection = None
try:
	# connect to bd
	connection = psycopg2.connect(
		host=host,
		user=user,
		# password=password,
		database=db_name
	)
	connection.autocommit = True
	# удаляю и пересоздаю таблицу для удобства, чтобы не ругался
	with connection.cursor() as cursor:
		cursor.execute(
		"""
		DROP TABLE cats;
		"""
		)
	with connection.cursor() as cursor:
		cursor.execute(
		"""
		CREATE TABLE cats 
		(
			cat_id UUID PRIMARY KEY,
			cat_name TEXT NULL,
			cat_breed TEXT NULL
		);
		"""
		)
except Exception as e:
	print("Error!", e)
finally:
	if connection:
		connection.close()
		print("Connection was closed")

#################################

@app.post("/create_cat/", response_model=str)
def create_cat(cat: Cat):
	psycopg2.extras.register_uuid()
	cat_id = str(uuid.uuid4())
	connection = None
	try:
		# connect to bd
		connection = psycopg2.connect(
			host=host,
			user=user,
			# password=password, # у меня нет пароля в мою БД)))
			database=db_name
		)
		connection.autocommit = True
		with connection.cursor() as cursor:
			cursor.execute(
			"""
			INSERT INTO cats (cat_id, cat_name, cat_breed)
			VALUES (%s, %s, %s)
			""", (cat_id, cat.name, cat.breed)
			)
	except Exception as e:
		print("Error!", e)
		raise HTTPException(status_code=500, detail="Failed to create cat")
	finally:
		if connection:
			connection.close()
			print("Connection was closed")
	return cat_id

@app.get("/get_cat/{cat_id}", response_model=Cat)
def get_cat(cat_id: str):
	connection = None
	cat = None
	try:
		# connect to bd
		connection = psycopg2.connect(
			host=host,
			user=user,
			# password=password, # у меня нет пароля в мою БД)))
			database=db_name
		)
		connection.autocommit = True
		with connection.cursor() as cursor:
			cursor.execute(
			"""
			SELECT cat_name, cat_breed FROM cats WHERE cat_id = %s
			""", (cat_id,)
			)
			tup = cursor.fetchone()
			print(tup)
			cat = Cat(name=tup[0], breed=tup[1])
	except Exception as e:
		print("Error!", e)
		raise HTTPException(status_code=404, detail="Cat not found")
	finally:
		if connection:
			connection.close()
			print("Connection was closed")
	print(cat)
	return cat