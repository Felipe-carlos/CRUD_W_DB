CREATE TABLE produtos(
	id serial PRIMARY KEY,
	nome VARCHAR(50) NOT NULL,
	preco DECIMAL(8,2) NOT NULL,
	estoque INT NOT NULL
);