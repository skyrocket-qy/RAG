pg:
	docker run -d --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:17.2

bk:
	git add .
	git commit -m "backup"
	git push

lines:
	cloc .

freeze:
	pip freeze > requirements.txt