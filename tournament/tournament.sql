-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
create table players (
	name text,
	id serial primary key
);

create table matches(
	id serial references players, 
	round integer,
	win boolean,
	opponent integer
);

create table scores (
	id serial references players,
	wins integer
);

-- You can write comments in this file by starting them with two dashes, like
-- these lines here.


