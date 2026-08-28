pg:
	docker run -d --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=password pgvector/pgvector:pg17

bk:
	git add .
	git commit -m "backup"
	git push

lines:
	cloc .

freeze:
	pip freeze > requirements.txt